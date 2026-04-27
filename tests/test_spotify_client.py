from src.recommender import load_songs
import src.spotify_client as spotify_client
from src.spotify_client import (
    classify_spotify_tracks,
    normalize_spotify_track,
    spotify_is_configured,
)
from src.study_dj import StudyDJRequest, build_study_playlist, default_data_paths, load_study_rules


def spotify_track(track_id="track-1", name="Focus Coding Loop"):
    return {
        "id": track_id,
        "name": name,
        "artists": [{"id": "artist-1", "name": "Test Artist"}],
        "album": {"release_date": "2023-03-01"},
        "duration_ms": 212000,
        "popularity": 72,
        "explicit": False,
        "external_urls": {"spotify": "https://open.spotify.com/track/track-1"},
    }


def test_normalize_spotify_track_matches_recommender_schema():
    song = normalize_spotify_track(
        spotify_track(),
        "top_track",
        {"artist-1": ["lo-fi beats", "study"]},
        index=7,
    )

    required_fields = {
        "id",
        "title",
        "artist",
        "genre",
        "mood",
        "energy",
        "acousticness",
        "popularity",
        "release_year",
        "detailed_mood_tags",
        "language",
        "explicit",
        "spotify_id",
        "spotify_url",
        "source",
    }
    assert required_fields <= set(song)
    assert song["id"] == 7
    assert song["spotify_id"] == "track-1"
    assert song["genre"] == "lofi"
    assert song["mood"] == "focused"
    assert song["language"] == "Instrumental"


def test_import_spotify_tracks_dedupes_top_and_recent(monkeypatch):
    class FakeSpotify:
        def current_user_top_tracks(self, limit, time_range):
            return {"items": [spotify_track("same-id", "Top Version")]}

        def currently_unused(self):
            return None

        def current_user_recently_played(self, limit):
            return {"items": [{"track": spotify_track("same-id", "Recent Version")}]}

        def artists(self, artist_ids):
            return {"artists": [{"id": "artist-1", "genres": ["lo-fi beats"]}]}

    monkeypatch.setattr(spotify_client, "get_spotify_client", lambda auth_code=None: FakeSpotify())
    songs = spotify_client.import_spotify_tracks(limit_top=50, limit_recent=50)

    assert len(songs) == 1
    assert songs[0]["spotify_id"] == "same-id"
    assert songs[0]["source"] == "top_track"
    assert songs[0]["title"] == "Top Version"


def test_fallback_classification_returns_complete_recommender_fields():
    track = normalize_spotify_track(
        spotify_track(name="Night Study Rain"),
        "recently_played",
        {"artist-1": ["ambient"]},
    )

    [classified] = classify_spotify_tracks([track], use_llm=False)

    assert classified["mood"] in classified["detailed_mood_tags"]
    assert 0.0 <= classified["energy"] <= 1.0
    assert 0.0 <= classified["acousticness"] <= 1.0
    assert classified["tempo_bpm"] > 0


def test_spotify_tracks_work_with_study_playlist_pipeline():
    paths = default_data_paths()
    rules = load_study_rules(str(paths["study_rules"]))
    spotify_songs = classify_spotify_tracks([
        normalize_spotify_track(
            spotify_track("spotify-focus", "Focus Coding Loop"),
            "top_track",
            {"artist-1": ["lo-fi beats"]},
        ),
        normalize_spotify_track(
            spotify_track("spotify-party", "Party Jump"),
            "recently_played",
            {"artist-1": ["dance pop"]},
            index=2,
        ),
    ], use_llm=False)
    request = StudyDJRequest(
        task_type="coding",
        session_minutes=45,
        focus_goal="deep focus",
        preferred_genre="lofi",
        preferred_mood="focused",
        target_energy=0.4,
        likes_acoustic=True,
        allows_lyrics=True,
        allows_explicit=False,
    )

    result = build_study_playlist(request, spotify_songs, rules, k=2, use_llm=False)

    assert result["retrieval"]["retrieved_songs"]
    assert result["playlist"]["ordered_tracks"]
    assert {
        track["title"] for track in result["playlist"]["ordered_tracks"]
    } <= {song["title"] for song in spotify_songs}


def test_missing_spotify_credentials_is_false_without_env(monkeypatch):
    monkeypatch.delenv("SPOTIPY_CLIENT_ID", raising=False)
    monkeypatch.delenv("SPOTIPY_CLIENT_SECRET", raising=False)

    assert spotify_is_configured() is False
