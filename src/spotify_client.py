import json
import os
from typing import Any, Dict, Iterable, List, Optional


SPOTIFY_SCOPES = "user-top-read user-read-recently-played"
DEFAULT_REDIRECT_URI = "http://127.0.0.1:8501"

GENRE_MOOD_HINTS = {
    # Electronic / EDM family
    "ambient": ("ambient", "chill", 0.30, 0.88),
    "chillwave": ("electronic", "chill", 0.35, 0.70),
    "downtempo": ("electronic", "chill", 0.32, 0.72),
    "trip hop": ("electronic", "moody", 0.40, 0.55),
    "trip-hop": ("electronic", "moody", 0.40, 0.55),
    "synthwave": ("electronic", "energetic", 0.75, 0.10),
    "retrowave": ("electronic", "energetic", 0.73, 0.10),
    "vapor": ("electronic", "dreamy", 0.38, 0.30),
    "house": ("edm", "energetic", 0.85, 0.08),
    "techno": ("edm", "intense", 0.88, 0.06),
    "trance": ("edm", "energetic", 0.84, 0.06),
    "dubstep": ("edm", "intense", 0.90, 0.05),
    "drum and bass": ("edm", "intense", 0.92, 0.05),
    "dnb": ("edm", "intense", 0.92, 0.05),
    "dance": ("edm", "energetic", 0.86, 0.12),
    "edm": ("edm", "energetic", 0.88, 0.08),
    "electro": ("electronic", "energetic", 0.78, 0.10),
    "electronic": ("electronic", "focused", 0.72, 0.14),
    # Lo-fi / Study
    "lo-fi": ("lofi", "focused", 0.36, 0.78),
    "lofi": ("lofi", "focused", 0.36, 0.78),
    "chillhop": ("lofi", "chill", 0.38, 0.72),
    "study": ("lofi", "focused", 0.34, 0.75),
    # Hip-hop / Rap family
    "hip hop": ("hip-hop", "confident", 0.78, 0.16),
    "hip-hop": ("hip-hop", "confident", 0.78, 0.16),
    "rap": ("hip-hop", "confident", 0.80, 0.14),
    "trap": ("hip-hop", "intense", 0.82, 0.10),
    "drill": ("hip-hop", "aggressive", 0.85, 0.08),
    "boom bap": ("hip-hop", "confident", 0.68, 0.20),
    "conscious": ("hip-hop", "focused", 0.62, 0.25),
    # R&B / Soul family
    "r&b": ("r&b", "romantic", 0.55, 0.46),
    "rnb": ("r&b", "romantic", 0.55, 0.46),
    "alternative r&b": ("r&b", "moody", 0.50, 0.40),
    "soul": ("blues", "soulful", 0.50, 0.72),
    "neo soul": ("r&b", "soulful", 0.48, 0.60),
    "vapor soul": ("r&b", "soulful", 0.45, 0.55),
    "funk": ("funk", "energetic", 0.75, 0.35),
    "gospel": ("gospel", "uplifting", 0.60, 0.65),
    # Rock family
    "rock": ("rock", "intense", 0.78, 0.22),
    "alt": ("alt rock", "moody", 0.65, 0.30),
    "alternative": ("alt rock", "moody", 0.65, 0.30),
    "grunge": ("rock", "intense", 0.80, 0.18),
    "punk": ("punk", "aggressive", 0.88, 0.15),
    "emo": ("rock", "moody", 0.70, 0.25),
    "shoegaze": ("rock", "dreamy", 0.55, 0.35),
    "post-rock": ("rock", "moody", 0.50, 0.40),
    "prog": ("rock", "focused", 0.65, 0.30),
    # Metal family
    "metal": ("metal", "aggressive", 0.92, 0.08),
    "hardcore": ("metal", "aggressive", 0.94, 0.06),
    "screamo": ("metal", "aggressive", 0.90, 0.08),
    # Pop family
    "pop": ("pop", "happy", 0.74, 0.24),
    "k-pop": ("pop", "energetic", 0.80, 0.15),
    "kpop": ("pop", "energetic", 0.80, 0.15),
    "j-pop": ("pop", "happy", 0.72, 0.20),
    "synth pop": ("pop", "energetic", 0.72, 0.12),
    "dream pop": ("pop", "dreamy", 0.45, 0.40),
    "art pop": ("pop", "focused", 0.60, 0.30),
    "hyperpop": ("pop", "intense", 0.88, 0.08),
    "bubblegum": ("pop", "happy", 0.78, 0.20),
    # Indie family
    "indie": ("indie pop", "focused", 0.58, 0.45),
    "bedroom": ("indie pop", "chill", 0.42, 0.55),
    # Folk / Acoustic / Country family
    "folk": ("folk", "peaceful", 0.40, 0.90),
    "acoustic": ("folk", "peaceful", 0.38, 0.92),
    "singer-songwriter": ("folk", "peaceful", 0.42, 0.88),
    "country": ("country", "nostalgic", 0.46, 0.72),
    "bluegrass": ("country", "energetic", 0.55, 0.90),
    "americana": ("country", "nostalgic", 0.44, 0.80),
    # Classical / Jazz family
    "classical": ("classical", "peaceful", 0.24, 0.92),
    "orchestral": ("classical", "peaceful", 0.30, 0.90),
    "piano": ("classical", "peaceful", 0.28, 0.95),
    "jazz": ("jazz", "relaxed", 0.42, 0.84),
    "bossa": ("jazz", "relaxed", 0.38, 0.82),
    "swing": ("jazz", "happy", 0.55, 0.70),
    # Latin family
    "latin": ("latin", "energetic", 0.78, 0.35),
    "reggaeton": ("latin", "energetic", 0.84, 0.12),
    "salsa": ("latin", "happy", 0.80, 0.40),
    "bachata": ("latin", "romantic", 0.65, 0.45),
    # Other
    "blues": ("blues", "soulful", 0.45, 0.75),
    "reggae": ("reggae", "chill", 0.55, 0.50),
    "ska": ("reggae", "happy", 0.72, 0.35),
    "afrobeat": ("afrobeat", "energetic", 0.78, 0.35),
    "world": ("world", "peaceful", 0.50, 0.60),
    "new age": ("ambient", "peaceful", 0.25, 0.88),
    "meditation": ("ambient", "peaceful", 0.20, 0.90),
    "soundtrack": ("classical", "focused", 0.40, 0.70),
    "video game": ("electronic", "focused", 0.55, 0.40),
    "anime": ("pop", "energetic", 0.72, 0.20),
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

TITLE_GENRE_HINTS = {
    "acoustic": "folk",
    "ambient": "ambient",
    "anime": "pop",
    "bachata": "latin",
    "beat": "hip-hop",
    "blues": "blues",
    "bossa": "jazz",
    "chill": "lofi",
    "classical": "classical",
    "club": "edm",
    "coding": "lofi",
    "country": "country",
    "dance": "edm",
    "drill": "hip-hop",
    "edm": "edm",
    "electro": "electronic",
    "folk": "folk",
    "funk": "funk",
    "gospel": "gospel",
    "grunge": "rock",
    "guitar": "rock",
    "hip hop": "hip-hop",
    "hip-hop": "hip-hop",
    "house": "edm",
    "indie": "indie pop",
    "jazz": "jazz",
    "latin": "latin",
    "lofi": "lofi",
    "lo-fi": "lofi",
    "metal": "metal",
    "orchestra": "classical",
    "piano": "classical",
    "punk": "punk",
    "r&b": "r&b",
    "rap": "hip-hop",
    "reggae": "reggae",
    "reggaeton": "latin",
    "rock": "rock",
    "salsa": "latin",
    "soul": "blues",
    "soundtrack": "classical",
    "study": "lofi",
    "symphony": "classical",
    "synth": "electronic",
    "techno": "edm",
    "trap": "hip-hop",
    "trance": "edm",
}


def spotify_is_configured() -> bool:
    return bool(os.getenv("SPOTIPY_CLIENT_ID"))


def get_spotify_auth(cache_handler=None):
    from spotipy.oauth2 import SpotifyPKCE

    kwargs = {
        "client_id": os.getenv("SPOTIPY_CLIENT_ID"),
        "redirect_uri": os.getenv("SPOTIPY_REDIRECT_URI", DEFAULT_REDIRECT_URI),
        "scope": SPOTIFY_SCOPES,
        "open_browser": False,
    }
    if cache_handler:
        kwargs["cache_handler"] = cache_handler
    else:
        kwargs["cache_path"] = ".spotify_cache"

    return SpotifyPKCE(**kwargs)


def get_spotify_auth_url(cache_handler=None) -> str:
    auth = get_spotify_auth(cache_handler=cache_handler)
    url = auth.get_authorize_url()
    return url

def get_spotify_client(
    auth_code: Optional[str] = None,
    cache_handler=None
):
    if not spotify_is_configured():
        raise RuntimeError("Spotify is not configured on the server.")

    import spotipy

    auth = get_spotify_auth(cache_handler=cache_handler)

    token_info = auth.validate_token(auth.cache_handler.get_cached_token())
    if not token_info and auth_code:
        auth.get_access_token(auth_code)
        token_info = auth.validate_token(auth.cache_handler.get_cached_token())
    if not token_info:
        raise RuntimeError("Spotify login is required before importing tracks.")
    return spotipy.Spotify(auth=token_info["access_token"])


def import_spotify_tracks(
    limit_top: int = 50,
    limit_recent: int = 50,
    auth_code: Optional[str] = None,
    cache_handler=None,
) -> List[Dict[str, Any]]:
    client = get_spotify_client(auth_code=auth_code, cache_handler=cache_handler)
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
    album_name = raw_track.get("album", {}).get("name", "")

    popularity = int(raw_track.get("popularity") or 50)
    duration_seconds = int((raw_track.get("duration_ms") or 210000) / 1000)
    inferred = _infer_features(
        title=raw_track.get("name", "Untitled Track"),
        artist_genres=genres,
        popularity=popularity,
        explicit=1 if raw_track.get("explicit") else 0,
        duration_seconds=duration_seconds,
        album_name=album_name,
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
        "album_name": album_name,
    }


def classify_spotify_tracks(
    tracks: List[Dict[str, Any]],
    use_llm: bool = True,
) -> List[Dict[str, Any]]:
    from src.llm_client import llm_is_available

    if use_llm and llm_is_available() and tracks:
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
        try:
            response = client.artists(chunk)
            for artist in response.get("artists", []):
                genres[artist["id"]] = artist.get("genres", [])
        except Exception as e:
            print(f"Warning: Failed to fetch artist genres: {e}")
    return genres


def _infer_features(
    title: str,
    artist_genres: List[str],
    popularity: int,
    explicit: int,
    duration_seconds: int,
    album_name: str = "",
) -> Dict[str, Any]:
    genre, mood, base_energy, acousticness = _genre_defaults(artist_genres)

    # If artist_genres produced no useful match (fell back to "pop" with no
    # actual genre data), try to infer genre from the title and album name.
    if not artist_genres or genre == "pop":
        title_genre = _title_genre(title, album_name)
        if title_genre:
            # Re-derive defaults from the title-inferred genre
            g, m, e, a = _genre_defaults([title_genre])
            if g != "pop" or title_genre.lower() == "pop":
                genre, mood, base_energy, acousticness = g, m, e, a

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
        album_name=track.get("album_name", ""),
    )
    updated = {**track, **inferred}
    return updated


def _classify_with_openai(tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    from src.llm_client import chat_json
    import os

    # Use a faster, higher-limit model for classification if on Groq or Mistral
    model = None
    if os.getenv("GROQ_API_KEY"):
        model = "llama-3.1-8b-instant"
    elif os.getenv("MISTRAL_API_KEY"):
        model = "mistral-small-latest"

    results = []
    batch_size = 30
    
    system_prompt = (
        "Classify each Spotify track for a study playlist recommender.\n\n"
        "For each track, return:\n"
        "- genre: Use one of these broad genres: "
        "pop, rock, alt rock, metal, punk, hip-hop, r&b, blues, jazz, "
        "classical, folk, country, lofi, ambient, electronic, edm, "
        "latin, indie pop, funk, reggae, afrobeat, world.\n"
        "- mood: Use one of these moods: happy, chill, focused, relaxed, "
        "energetic, intense, confident, peaceful, moody, dreamy, romantic, "
        "soulful, aggressive, nostalgic.\n"
        "- energy: Float 0.0 to 1.0 (0=very calm, 0.3=chill, 0.5=moderate, "
        "0.7=upbeat, 1.0=max intensity).\n"
        "- acousticness: Float 0.0 to 1.0 (0=electronic, 1.0=acoustic).\n"
        "- detailed_mood_tags: 2-4 descriptive mood tags.\n\n"
        "Use your knowledge of these artists and songs to classify accurately.\n\n"
        "Return JSON in this exact format:\n"
        '{"tracks": [{"spotify_id": "...", "genre": "...", "mood": "...", '
        '"energy": 0.5, "acousticness": 0.5, "detailed_mood_tags": ["..."]}, ...]}\n'
        "Return ONLY valid JSON, no other text."
    )

    for i in range(0, len(tracks), batch_size):
        batch = tracks[i:i + batch_size]
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
            for track in batch
        ]

        try:
            batch_result = chat_json(system_prompt, json.dumps(payload, indent=2), model=model)
            results.extend(batch_result.get("tracks", []))
        except Exception as e:
            print(f"Warning: Classification batch {i} failed: {e}")

    return results


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
        updated["language"] = _language_from_features(updated)
        merged.append(updated)
    return merged


def _genre_defaults(artist_genres: List[str]) -> tuple[str, str, float, float]:
    # Pass 1: check each Spotify genre tag individually (more precise)
    for genre_tag in artist_genres:
        tag = genre_tag.strip().lower()
        if tag in GENRE_MOOD_HINTS:
            return GENRE_MOOD_HINTS[tag]
    # Pass 2: substring scan across all tags joined
    lowered = " ".join(artist_genres).lower()
    # Sort keys longest-first so "dream pop" matches before "pop"
    for key in sorted(GENRE_MOOD_HINTS, key=len, reverse=True):
        if key in lowered:
            return GENRE_MOOD_HINTS[key]
    # Pass 3: use the first raw Spotify genre name instead of always "pop"
    if artist_genres:
        raw = artist_genres[0].strip().lower().replace(" ", "-")
        return (raw, "focused", 0.55, 0.45)
    return ("pop", "focused", 0.55, 0.45)


def _title_mood(title: str) -> Optional[str]:
    lowered = title.lower()
    for keyword, mood in TITLE_MOOD_HINTS.items():
        if keyword in lowered:
            return mood
    return None


def _title_genre(title: str, album_name: str = "") -> Optional[str]:
    """Infer genre from the track title or album name when artist genres are unavailable."""
    combined = f"{title} {album_name}".lower()
    # Sort longest-first to prefer specific matches ("hip-hop" before "hop")
    for keyword in sorted(TITLE_GENRE_HINTS, key=len, reverse=True):
        if keyword in combined:
            return TITLE_GENRE_HINTS[keyword]
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
    instrumental_friendly = {
        "ambient", "classical", "jazz", "lofi",
        "edm", "electronic", "funk", "world", "afrobeat",
    }
    return "Instrumental" if features.get("genre") in instrumental_friendly else "English"


def _clamp_float(value: Any) -> float:
    try:
        return min(1.0, max(0.0, round(float(value), 2)))
    except (TypeError, ValueError):
        return 0.5
