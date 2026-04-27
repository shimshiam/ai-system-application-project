import json
import os
from typing import Any, Dict, Iterable, List, Optional


SPOTIFY_SCOPES = "user-top-read user-read-recently-played"
DEFAULT_REDIRECT_URI = "http://localhost:8501"

GENRE_MOOD_HINTS = {
    "ambient": ("ambient", "chill", 0.30, 0.88),
    "classical": ("classical", "peaceful", 0.24, 0.92),
    "country": ("country", "nostalgic", 0.46, 0.72),
    "dance": ("edm", "energetic", 0.86, 0.12),
    "edm": ("edm", "energetic", 0.88, 0.08),
    "electronic": ("electronic", "focused", 0.72, 0.14),
    "folk": ("folk", "peaceful", 0.40, 0.90),
    "hip hop": ("hip-hop", "confident", 0.78, 0.16),
    "indie": ("indie pop", "focused", 0.58, 0.45),
    "jazz": ("jazz", "relaxed", 0.42, 0.84),
    "lo-fi": ("lofi", "focused", 0.36, 0.78),
    "lofi": ("lofi", "focused", 0.36, 0.78),
    "metal": ("metal", "aggressive", 0.92, 0.08),
    "pop": ("pop", "happy", 0.74, 0.24),
    "r&b": ("r&b", "romantic", 0.55, 0.46),
    "rap": ("hip-hop", "confident", 0.80, 0.14),
    "rock": ("rock", "intense", 0.78, 0.22),
    "soul": ("blues", "soulful", 0.50, 0.72),
}

TITLE_MOOD_HINTS = {
    "calm": "peaceful",
    "chill": "chill",
    "coding": "focused",
    "dance": "happy",
    "dream": "dreamy",
    "focus": "focused",
    "happy": "happy",
    "love": "romantic",
    "night": "moody",
    "party": "hype",
    "rain": "chill",
    "study": "focused",
}


def spotify_is_configured() -> bool:
    return all(
        os.getenv(name)
        for name in ("SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET")
    )


def get_spotify_auth():
    from spotipy.oauth2 import SpotifyOAuth

    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI", DEFAULT_REDIRECT_URI),
        scope=SPOTIFY_SCOPES,
        cache_path=".spotify_cache",
        open_browser=False,
    )


def get_spotify_auth_url() -> str:
    return get_spotify_auth().get_authorize_url()


def get_spotify_client(auth_code: Optional[str] = None):
    if not spotify_is_configured():
        raise RuntimeError("Spotify credentials are not configured.")

    import spotipy

    auth = get_spotify_auth()
    token_info = auth.get_cached_token()
    if not token_info and auth_code:
        token_info = auth.get_access_token(auth_code, as_dict=True)
    if not token_info:
        raise RuntimeError("Spotify login is required before importing tracks.")
    return spotipy.Spotify(auth=token_info["access_token"])


def import_spotify_tracks(
    limit_top: int = 50,
    limit_recent: int = 50,
    auth_code: Optional[str] = None,
) -> List[Dict[str, Any]]:
    client = get_spotify_client(auth_code=auth_code)
    imported: List[Dict[str, Any]] = []
    seen_ids = set()

    top_items = client.current_user_top_tracks(limit=limit_top, time_range="medium_term").get("items", [])
    recent_items = client.current_user_recently_played(limit=limit_recent).get("items", [])
    artist_genres = _fetch_artist_genres(client, [*top_items, *recent_items])

    for item in top_items:
        spotify_id = item.get("id")
        if spotify_id and spotify_id not in seen_ids:
            seen_ids.add(spotify_id)
            imported.append(normalize_spotify_track(item, "top_track", artist_genres, len(imported) + 1))

    for item in recent_items:
        track = item.get("track", item)
        spotify_id = track.get("id")
        if spotify_id and spotify_id not in seen_ids:
            seen_ids.add(spotify_id)
            imported.append(normalize_spotify_track(item, "recently_played", artist_genres, len(imported) + 1))

    return classify_spotify_tracks(imported)


def normalize_spotify_track(
    track: Dict[str, Any],
    source: str,
    artist_genres: Optional[Dict[str, List[str]]] = None,
    index: int = 1,
) -> Dict[str, Any]:
    raw_track = track.get("track", track)
    artist_genres = artist_genres or {}
    artists = raw_track.get("artists", [])
    primary_artist = artists[0] if artists else {}
    artist_name = primary_artist.get("name", "Unknown Artist")
    genres = artist_genres.get(primary_artist.get("id"), [])

    popularity = int(raw_track.get("popularity") or 50)
    duration_seconds = int((raw_track.get("duration_ms") or 210000) / 1000)
    inferred = _infer_features(
        title=raw_track.get("name", "Untitled Track"),
        artist_genres=genres,
        popularity=popularity,
        explicit=1 if raw_track.get("explicit") else 0,
        duration_seconds=duration_seconds,
    )

    return {
        "id": index,
        "title": raw_track.get("name", "Untitled Track"),
        "artist": artist_name,
        "genre": inferred["genre"],
        "mood": inferred["mood"],
        "energy": inferred["energy"],
        "tempo_bpm": inferred["tempo_bpm"],
        "valence": inferred["valence"],
        "danceability": inferred["danceability"],
        "acousticness": inferred["acousticness"],
        "popularity": popularity,
        "release_year": _release_year(raw_track),
        "detailed_mood_tags": inferred["detailed_mood_tags"],
        "artist_popularity": popularity,
        "song_length_seconds": duration_seconds,
        "language": _language_from_features(inferred),
        "explicit": 1 if raw_track.get("explicit") else 0,
        "spotify_id": raw_track.get("id", ""),
        "spotify_url": raw_track.get("external_urls", {}).get("spotify", ""),
        "source": source,
        "artist_genres": genres,
    }


def classify_spotify_tracks(
    tracks: List[Dict[str, Any]],
    use_llm: bool = True,
) -> List[Dict[str, Any]]:
    if use_llm and os.getenv("OPENAI_API_KEY") and tracks:
        try:
            classifications = _classify_with_openai(tracks)
            return _merge_classifications(tracks, classifications)
        except Exception:
            return [_fallback_classify(track) for track in tracks]
    return [_fallback_classify(track) for track in tracks]


def _fetch_artist_genres(client: Any, raw_tracks: Iterable[Dict[str, Any]]) -> Dict[str, List[str]]:
    artist_ids = []
    for item in raw_tracks:
        track = item.get("track", item)
        for artist in track.get("artists", []):
            artist_id = artist.get("id")
            if artist_id and artist_id not in artist_ids:
                artist_ids.append(artist_id)

    genres: Dict[str, List[str]] = {}
    for start in range(0, len(artist_ids), 50):
        chunk = artist_ids[start:start + 50]
        response = client.artists(chunk)
        for artist in response.get("artists", []):
            genres[artist["id"]] = artist.get("genres", [])
    return genres


def _infer_features(
    title: str,
    artist_genres: List[str],
    popularity: int,
    explicit: int,
    duration_seconds: int,
) -> Dict[str, Any]:
    genre, mood, base_energy, acousticness = _genre_defaults(artist_genres)
    title_mood = _title_mood(title)
    if title_mood:
        mood = title_mood

    popularity_energy = min(1.0, max(0.0, popularity / 100))
    energy = round((base_energy * 0.7) + (popularity_energy * 0.3), 2)
    if explicit:
        energy = min(1.0, round(energy + 0.06, 2))
    if duration_seconds > 270:
        energy = max(0.0, round(energy - 0.05, 2))

    return {
        "genre": genre,
        "mood": mood,
        "energy": energy,
        "tempo_bpm": round(70 + (energy * 85), 1),
        "valence": round(0.35 + (energy * 0.45), 2),
        "danceability": round(0.30 + (energy * 0.55), 2),
        "acousticness": round(acousticness, 2),
        "detailed_mood_tags": _mood_tags(mood, artist_genres),
    }


def _fallback_classify(track: Dict[str, Any]) -> Dict[str, Any]:
    inferred = _infer_features(
        title=track.get("title", ""),
        artist_genres=track.get("artist_genres", []),
        popularity=int(track.get("popularity", 50)),
        explicit=int(track.get("explicit", 0)),
        duration_seconds=int(track.get("song_length_seconds", 210)),
    )
    updated = {**track, **inferred}
    return updated


def _classify_with_openai(tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    from openai import OpenAI

    client = OpenAI()
    payload = [
        {
            "spotify_id": track.get("spotify_id"),
            "title": track.get("title"),
            "artist": track.get("artist"),
            "artist_genres": track.get("artist_genres", []),
            "popularity": track.get("popularity"),
            "explicit": track.get("explicit"),
            "duration_seconds": track.get("song_length_seconds"),
        }
        for track in tracks
    ]
    response = client.responses.create(
        model=os.getenv("AI_MODEL", "gpt-5"),
        instructions=(
            "Classify Spotify tracks for a study playlist recommender. Return only JSON. "
            "Use broad genres and moods compatible with the existing app."
        ),
        input=json.dumps(payload, indent=2),
        text={
            "format": {
                "type": "json_schema",
                "name": "spotify_track_classifications",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "tracks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "spotify_id": {"type": "string"},
                                    "genre": {"type": "string"},
                                    "mood": {"type": "string"},
                                    "energy": {"type": "number"},
                                    "acousticness": {"type": "number"},
                                    "detailed_mood_tags": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                                "required": [
                                    "spotify_id",
                                    "genre",
                                    "mood",
                                    "energy",
                                    "acousticness",
                                    "detailed_mood_tags",
                                ],
                            },
                        }
                    },
                    "required": ["tracks"],
                },
                "strict": True,
            }
        },
    )
    return json.loads(response.output_text)["tracks"]


def _merge_classifications(
    tracks: List[Dict[str, Any]],
    classifications: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    by_id = {item["spotify_id"]: item for item in classifications}
    merged = []
    for track in tracks:
        classification = by_id.get(track.get("spotify_id"))
        if not classification:
            merged.append(_fallback_classify(track))
            continue
        updated = {**track}
        updated["genre"] = classification["genre"]
        updated["mood"] = classification["mood"]
        updated["energy"] = _clamp_float(classification["energy"])
        updated["acousticness"] = _clamp_float(classification["acousticness"])
        updated["detailed_mood_tags"] = classification["detailed_mood_tags"]
        updated["tempo_bpm"] = round(70 + (updated["energy"] * 85), 1)
        updated["valence"] = round(0.35 + (updated["energy"] * 0.45), 2)
        updated["danceability"] = round(0.30 + (updated["energy"] * 0.55), 2)
        merged.append(updated)
    return merged


def _genre_defaults(artist_genres: List[str]) -> tuple[str, str, float, float]:
    lowered = " ".join(artist_genres).lower()
    for key, defaults in GENRE_MOOD_HINTS.items():
        if key in lowered:
            return defaults
    return ("pop", "focused", 0.55, 0.45)


def _title_mood(title: str) -> Optional[str]:
    lowered = title.lower()
    for keyword, mood in TITLE_MOOD_HINTS.items():
        if keyword in lowered:
            return mood
    return None


def _mood_tags(mood: str, artist_genres: List[str]) -> List[str]:
    tags = [mood]
    for genre in artist_genres[:2]:
        clean = genre.strip().lower()
        if clean and clean not in tags:
            tags.append(clean)
    return tags


def _release_year(track: Dict[str, Any]) -> int:
    release_date = track.get("album", {}).get("release_date", "")
    try:
        return int(release_date[:4])
    except ValueError:
        return 2020


def _language_from_features(features: Dict[str, Any]) -> str:
    instrumental_friendly = {"ambient", "classical", "jazz", "lofi"}
    return "Instrumental" if features.get("genre") in instrumental_friendly else "English"


def _clamp_float(value: Any) -> float:
    try:
        return min(1.0, max(0.0, round(float(value), 2)))
    except (TypeError, ValueError):
        return 0.5
