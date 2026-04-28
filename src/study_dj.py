import csv
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.recommender import (
    BalancedScorer,
    EnergyFocusedScorer,
    GenreFirstScorer,
    MoodFirstScorer,
    ResonanceScorer,
    recommend_songs,
)


SCORERS = {
    "balanced": BalancedScorer,
    "genre_first": GenreFirstScorer,
    "mood_first": MoodFirstScorer,
    "energy_focused": EnergyFocusedScorer,
    "resonance": ResonanceScorer,
}


PLAYLIST_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"},
        "ordered_tracks": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "rank": {"type": "integer"},
                    "title": {"type": "string"},
                    "artist": {"type": "string"},
                    "reason": {"type": "string"},
                    "pacing_note": {"type": "string"},
                },
                "required": ["rank", "title", "artist", "reason", "pacing_note"],
            },
        },
        "study_strategy": {"type": "string"},
        "source_context_used": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["summary", "ordered_tracks", "study_strategy", "source_context_used"],
}


@dataclass
class StudyDJRequest:
    task_type: str
    session_minutes: int
    focus_goal: str
    preferred_genre: str
    preferred_mood: str
    target_energy: float
    likes_acoustic: bool
    allows_lyrics: bool
    allows_explicit: bool
    synthesis_mode: Optional[str] = None
    synthesis_params: Optional[Dict[str, Any]] = None


def load_study_rules(csv_path: str) -> List[Dict[str, Any]]:
    """Load task guidance rules used as the RAG knowledge source."""
    rules: List[Dict[str, Any]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rules.append({
                "task_type": row["task_type"],
                "focus_goal": row["focus_goal"],
                "recommended_genre": row["recommended_genre"],
                "recommended_mood": row["recommended_mood"],
                "recommended_energy_min": float(row["recommended_energy_min"]),
                "recommended_energy_max": float(row["recommended_energy_max"]),
                "likes_acoustic": row["likes_acoustic"].strip().lower() == "true",
                "strategy": row["strategy"],
                "lyric_policy": row["lyric_policy"],
                "guidance": row["guidance"],
                "pacing": row["pacing"],
            })
    return rules


def retrieve_study_rules(
    request: StudyDJRequest,
    rules: List[Dict[str, Any]],
    k: int = 2,
) -> List[Dict[str, Any]]:
    """Retrieve the most relevant study rules for the requested task and focus goal."""
    scored_rules = []
    for rule in rules:
        score = 0
        if rule["task_type"] == request.task_type:
            score += 3
        if rule["focus_goal"] == request.focus_goal:
            score += 2
        if rule["recommended_mood"] == request.preferred_mood:
            score += 1
        if rule["recommended_genre"] == request.preferred_genre:
            score += 1
        scored_rules.append((score, rule))

    scored_rules.sort(key=lambda item: item[0], reverse=True)
    return [rule for score, rule in scored_rules[:k] if score > 0] or rules[:k]


def retrieve_candidate_songs(
    request: StudyDJRequest,
    songs: List[Dict[str, Any]],
    study_rules: List[Dict[str, Any]],
    k: int = 5,
) -> List[Dict[str, Any]]:
    """Retrieve candidate tracks using recommender scores plus study constraints."""
    primary_rule = study_rules[0] if study_rules else {}
    target_energy = _energy_for_study_rule(request.target_energy, primary_rule)
    
    if request.synthesis_mode and request.synthesis_mode != "auto":
        strategy = request.synthesis_mode
    else:
        strategy = primary_rule.get("strategy", "balanced")
        
    scorer = SCORERS.get(strategy, BalancedScorer)()

    filtered_songs = []
    for song in songs:
        if not request.allows_explicit and song.get("explicit", 0) == 1:
            continue
        if not request.allows_lyrics and song.get("language") != "Instrumental":
            continue
        filtered_songs.append(song)
        
    if len(filtered_songs) < k and songs:
        # Not enough songs survived the lyrics filter — pad with songs that
        # pass the explicit filter (but may have lyrics) to fill the playlist.
        existing_ids = {id(s) for s in filtered_songs}
        extras = [s for s in songs
                  if id(s) not in existing_ids
                  and (request.allows_explicit or s.get("explicit", 0) != 1)]
        filtered_songs.extend(extras)
        if len(filtered_songs) < k:
            # Fallback 2: Ignore all filters to prevent empty retrieval
            remaining = [s for s in songs if id(s) not in {id(s2) for s2 in filtered_songs}]
            filtered_songs.extend(remaining)

    user_prefs = {
        "genre": request.preferred_genre or primary_rule.get("recommended_genre"),
        "mood": request.preferred_mood or primary_rule.get("recommended_mood"),
        "energy": target_energy,
        "likes_acoustic": request.likes_acoustic,
        # pass through optional synthesis parameters (e.g. tuning shifts for resonance)
        "tuning_shift": float((request.synthesis_params or {}).get("tuning_shift", 0.0)),
    }
    recommendations = recommend_songs(user_prefs, filtered_songs, k=k, scorer=scorer)
    return [
        {
            "song": song,
            "score": round(score, 2),
            "explanation": explanation,
        }
        for song, score, explanation in recommendations
    ]


def retrieve_context(
    request: StudyDJRequest,
    songs: List[Dict[str, Any]],
    study_rules: List[Dict[str, Any]],
    k: int = 5,
) -> Dict[str, Any]:
    """Run the retrieval step before generation."""
    retrieved_rules = retrieve_study_rules(request, study_rules)
    retrieved_songs = retrieve_candidate_songs(request, songs, retrieved_rules, k=k)
    rule_names = ", ".join(
        f"{rule['task_type']} / {rule['focus_goal']}" for rule in retrieved_rules
    )
    return {
        "retrieved_songs": retrieved_songs,
        "retrieved_study_rules": retrieved_rules,
        "retrieval_explanation": (
            f"Retrieved {len(retrieved_songs)} songs after applying lyric and explicit filters. "
            f"Study guidance came from: {rule_names}."
        ),
    }


def generate_playlist_plan(
    request: StudyDJRequest,
    retrieval: Dict[str, Any],
    use_llm: bool = True,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a RAG-grounded playlist plan with an LLM or deterministic fallback."""
    if use_llm and os.getenv("OPENAI_API_KEY"):
        try:
            plan = _generate_with_openai(request, retrieval, model=model)
            return _ensure_plan_uses_retrieved_songs(plan, retrieval, request)
        except Exception as exc:
            fallback = generate_fallback_playlist_plan(request, retrieval)
            fallback["ai_notice"] = (
                "OpenAI generation was unavailable, so the deterministic fallback planner was used."
            )
            return fallback
    return generate_fallback_playlist_plan(request, retrieval)


def generate_fallback_playlist_plan(
    request: StudyDJRequest,
    retrieval: Dict[str, Any],
) -> Dict[str, Any]:
    """Create a deterministic plan that still uses the retrieved RAG context."""
    tracks = retrieval.get("retrieved_songs", [])
    rules = retrieval.get("retrieved_study_rules", [])
    primary_rule = rules[0] if rules else {}
    ordered_tracks = []

    for rank, item in enumerate(tracks, 1):
        song = item["song"]
        ordered_tracks.append({
            "rank": rank,
            "title": song["title"],
            "artist": song["artist"],
            "reason": (
                f"Score {item['score']} for {request.task_type}: "
                f"{item['explanation'].split('; ')[0]}"
            ),
            "pacing_note": _pacing_note(rank, len(tracks), song, primary_rule),
        })

    task_label = request.task_type.replace("_", " ")
    summary = (
        f"This {request.session_minutes}-minute {task_label} playlist uses retrieved song matches "
        f"and study guidance for {request.focus_goal}."
    )
    study_strategy = primary_rule.get(
        "guidance",
        "Use steady tracks that match the requested energy and focus goal.",
    )

    return {
        "summary": summary,
        "ordered_tracks": ordered_tracks,
        "track_reasons": _build_track_reasons(ordered_tracks),
        "study_strategy": f"{study_strategy} {primary_rule.get('pacing', '')}".strip(),
        "source_context_used": _source_context_used(retrieval),
    }


def build_study_playlist(
    request: StudyDJRequest,
    songs: List[Dict[str, Any]],
    study_rules: List[Dict[str, Any]],
    k: int = 5,
    use_llm: bool = True,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Main app pipeline: retrieve context, then generate the final playlist plan."""
    retrieval = retrieve_context(request, songs, study_rules, k=k)
    plan = generate_playlist_plan(request, retrieval, use_llm=use_llm, model=model)
    return {
        "request": asdict(request),
        "retrieval": retrieval,
        "playlist": plan,
    }


def _generate_with_openai(
    request: StudyDJRequest,
    retrieval: Dict[str, Any],
    model: Optional[str] = None,
) -> Dict[str, Any]:
    from openai import OpenAI

    client = OpenAI()
    selected_model = model or os.getenv("AI_MODEL", "gpt-5")
    context = {
        "request": asdict(request),
        "retrieved_study_rules": retrieval["retrieved_study_rules"],
        "retrieved_songs": [
            {
                "title": item["song"]["title"],
                "artist": item["song"]["artist"],
                "genre": item["song"]["genre"],
                "mood": item["song"]["mood"],
                "energy": item["song"]["energy"],
                "language": item["song"]["language"],
                "score": item["score"],
                "explanation": item["explanation"],
            }
            for item in retrieval["retrieved_songs"]
        ],
    }
    response = client.responses.create(
        model=selected_model,
        instructions=(
            "You are Study DJ, an AI playlist planner. Use only the retrieved songs and "
            "study rules in the provided JSON. Return a concise JSON object that matches "
            "the schema. Do not invent songs."
        ),
        input=json.dumps(context, indent=2),
        text={
            "format": {
                "type": "json_schema",
                "name": "study_playlist_plan",
                "schema": PLAYLIST_SCHEMA,
                "strict": True,
            }
        },
    )
    return json.loads(response.output_text)


def _ensure_plan_uses_retrieved_songs(
    plan: Dict[str, Any],
    retrieval: Dict[str, Any],
    request: StudyDJRequest,
) -> Dict[str, Any]:
    retrieved_by_key = {
        _track_identity_key(item["song"]): item for item in retrieval.get("retrieved_songs", [])
    }
    validated_tracks = []
    for track in plan.get("ordered_tracks", []):
        track_key = _track_identity_key(track)
        if track_key in retrieved_by_key:
            item = retrieved_by_key[track_key]
            song = item["song"]
            validated_tracks.append({
                "rank": len(validated_tracks) + 1,
                "title": song["title"],
                "artist": song["artist"],
                "reason": track.get("reason") or item["explanation"],
                "pacing_note": track.get("pacing_note") or "Use this track where its energy best fits.",
            })

    if len(validated_tracks) < len(retrieved_by_key):
        fallback = generate_fallback_playlist_plan(request, retrieval)
        existing_keys = {_track_identity_key(track) for track in validated_tracks}
        for track in fallback["ordered_tracks"]:
            if _track_identity_key(track) not in existing_keys:
                track["rank"] = len(validated_tracks) + 1
                validated_tracks.append(track)

    plan["ordered_tracks"] = validated_tracks
    plan["track_reasons"] = _build_track_reasons(validated_tracks)
    plan["source_context_used"] = _source_context_used(retrieval)
    return plan


def _energy_for_study_rule(target_energy: float, rule: Dict[str, Any]) -> float:
    if not rule:
        return min(1.0, max(0.0, target_energy))
    low = rule.get("recommended_energy_min", 0.0)
    high = rule.get("recommended_energy_max", 1.0)
    return min(high, max(low, min(1.0, max(0.0, target_energy))))


def _pacing_note(rank: int, total: int, song: Dict[str, Any], rule: Dict[str, Any]) -> str:
    if total <= 1 or rank == 1:
        return f"Start with {song['mood']} energy at {song['energy']:.2f}."
    if rank == total:
        return f"Close with a {song['genre']} track to reset before the next block."
    # Provide contextual pacing for mid-playlist positions
    position = rank / total
    if position <= 0.25:
        return f"Early warm-up — ease in with energy {song['energy']:.2f}."
    if 0.45 <= position <= 0.55:
        return f"Mid-session anchor — {song['mood']} energy at {song['energy']:.2f} to sustain focus."
    if position >= 0.75:
        return f"Final stretch — begin winding down with energy {song['energy']:.2f}."
    return f"Keep momentum steady with energy {song['energy']:.2f}."


def _source_context_used(retrieval: Dict[str, Any]) -> List[str]:
    sources = []
    for item in retrieval.get("retrieved_songs", []):
        song = item["song"]
        sources.append(f"song:{song['title']} by {song['artist']}")
    for rule in retrieval.get("retrieved_study_rules", []):
        sources.append(f"rule:{rule['task_type']} / {rule['focus_goal']}")
    return sources


def _track_identity_key(track: Dict[str, Any]) -> str:
    spotify_id = (track.get("spotify_id") or "").strip()
    if spotify_id:
        return f"spotify:{spotify_id}"

    title = (track.get("title") or "").strip().casefold()
    artist = (track.get("artist") or "").strip().casefold()
    return f"catalog:{title}|{artist}"


def _build_track_reasons(ordered_tracks: List[Dict[str, Any]]) -> Dict[str, str]:
    title_counts: Dict[str, int] = {}
    for track in ordered_tracks:
        title = track["title"]
        title_counts[title] = title_counts.get(title, 0) + 1

    used_labels: Dict[str, int] = {}
    track_reasons: Dict[str, str] = {}
    for track in ordered_tracks:
        label = track["title"]
        if title_counts[label] > 1:
            label = f"{track['title']} - {track['artist']}"

        suffix = used_labels.get(label, 0)
        used_labels[label] = suffix + 1
        if suffix:
            label = f"{label} ({suffix + 1})"

        track_reasons[label] = track["reason"]

    return track_reasons


def default_data_paths() -> Dict[str, Path]:
    root = Path(__file__).resolve().parents[1]
    return {
        "songs": root / "data" / "songs.csv",
        "study_rules": root / "data" / "study_rules.csv",
    }
