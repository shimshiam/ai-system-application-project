import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int
    release_year: int
    detailed_mood_tags: List[str]
    artist_popularity: int
    song_length_seconds: int
    language: str
    explicit: int

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Scorer(ABC):
    """Abstract base class for scoring strategies."""
    
    @abstractmethod
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Score one song against user prefs and return (points, reasons)."""
        pass


class BalancedScorer(Scorer):
    """Default balanced scoring strategy."""
    
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        return score_song(user_prefs, song)


class GenreFirstScorer(Scorer):
    """Prioritizes genre matches with higher weights."""
    
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []

        # Genre match: +2.0 points (high importance)
        if song["genre"] == user_prefs.get("genre"):
            score += 2.0
            reasons.append(f"+2.0 genre match ({song['genre']})")

        # Mood match: +0.5 point (reduced)
        if song["mood"] == user_prefs.get("mood"):
            score += 0.5
            reasons.append(f"+0.5 mood match ({song['mood']})")

        # Energy closeness: up to +1.0 point (reduced)
        if "energy" in user_prefs:
            energy_pts = max(0.0, 1.0 * (1.0 - abs(user_prefs["energy"] - song["energy"])))
            score += energy_pts
            reasons.append(f"+{energy_pts:.2f} energy closeness")

        # Acoustic fit: up to +0.5 points
        if "likes_acoustic" in user_prefs:
            if user_prefs["likes_acoustic"]:
                acoustic_pts = 0.5 * song.get("acousticness", 0.5)
                score += acoustic_pts
                if acoustic_pts > 0.3:
                    reasons.append(f"+{acoustic_pts:.2f} acoustic sound")
            else:
                acoustic_pts = 0.5 * (1.0 - song.get("acousticness", 0.5))
                score += acoustic_pts
                if acoustic_pts > 0.3:
                    reasons.append(f"+{acoustic_pts:.2f} electronic/produced sound")

        # Add new bonuses with reduced weights
        popularity_pts = (song.get("popularity", 50) / 100) * 0.3
        score += popularity_pts
        reasons.append(f"+{popularity_pts:.2f} popularity bonus")

        artist_pop_pts = (song.get("artist_popularity", 50) / 100) * 0.15
        score += artist_pop_pts
        reasons.append(f"+{artist_pop_pts:.2f} artist popularity bonus")

        if user_prefs.get("mood") in song.get("detailed_mood_tags", []):
            score += 0.3
            reasons.append("+0.3 detailed mood tag match")

        if song.get("release_year", 2000) >= 2020:
            score += 0.2
            reasons.append("+0.2 modern release bonus")

        length = song.get("song_length_seconds", 200)
        if 180 <= length <= 240:
            score += 0.1
            reasons.append("+0.1 ideal length bonus")

        if song.get("language") == "English":
            score += 0.05
            reasons.append("+0.05 English language bonus")

        if song.get("explicit", 0) == 1:
            score -= 0.3
            reasons.append("-0.3 explicit content penalty")

        if not reasons:
            reasons.append("weak overall match")

        return (score, reasons)


class MoodFirstScorer(Scorer):
    """Prioritizes mood matches with higher weights."""
    
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []

        # Genre match: +0.5 point (reduced)
        if song["genre"] == user_prefs.get("genre"):
            score += 0.5
            reasons.append(f"+0.5 genre match ({song['genre']})")

        # Mood match: +2.0 points (high importance)
        if song["mood"] == user_prefs.get("mood"):
            score += 2.0
            reasons.append(f"+2.0 mood match ({song['mood']})")

        # Energy closeness: up to +1.0 point
        if "energy" in user_prefs:
            energy_pts = max(0.0, 1.0 * (1.0 - abs(user_prefs["energy"] - song["energy"])))
            score += energy_pts
            reasons.append(f"+{energy_pts:.2f} energy closeness")

        # Acoustic fit: up to +0.5 points
        if "likes_acoustic" in user_prefs:
            if user_prefs["likes_acoustic"]:
                acoustic_pts = 0.5 * song.get("acousticness", 0.5)
                score += acoustic_pts
                if acoustic_pts > 0.3:
                    reasons.append(f"+{acoustic_pts:.2f} acoustic sound")
            else:
                acoustic_pts = 0.5 * (1.0 - song.get("acousticness", 0.5))
                score += acoustic_pts
                if acoustic_pts > 0.3:
                    reasons.append(f"+{acoustic_pts:.2f} electronic/produced sound")

        # Add new bonuses
        popularity_pts = (song.get("popularity", 50) / 100) * 0.3
        score += popularity_pts
        reasons.append(f"+{popularity_pts:.2f} popularity bonus")

        artist_pop_pts = (song.get("artist_popularity", 50) / 100) * 0.15
        score += artist_pop_pts
        reasons.append(f"+{artist_pop_pts:.2f} artist popularity bonus")

        if user_prefs.get("mood") in song.get("detailed_mood_tags", []):
            score += 0.8  # Higher for mood-first
            reasons.append("+0.8 detailed mood tag match")

        if song.get("release_year", 2000) >= 2020:
            score += 0.2
            reasons.append("+0.2 modern release bonus")

        length = song.get("song_length_seconds", 200)
        if 180 <= length <= 240:
            score += 0.1
            reasons.append("+0.1 ideal length bonus")

        if song.get("language") == "English":
            score += 0.05
            reasons.append("+0.05 English language bonus")

        if song.get("explicit", 0) == 1:
            score -= 0.3
            reasons.append("-0.3 explicit content penalty")

        if not reasons:
            reasons.append("weak overall match")

        return (score, reasons)


class EnergyFocusedScorer(Scorer):
    """Prioritizes energy closeness with higher weights."""
    
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []

        # Genre match: +0.5 point (reduced)
        if song["genre"] == user_prefs.get("genre"):
            score += 0.5
            reasons.append(f"+0.5 genre match ({song['genre']})")

        # Mood match: +0.5 point (reduced)
        if song["mood"] == user_prefs.get("mood"):
            score += 0.5
            reasons.append(f"+0.5 mood match ({song['mood']})")

        # Energy closeness: up to +3.0 points (very high importance)
        if "energy" in user_prefs:
            energy_pts = max(0.0, 3.0 * (1.0 - abs(user_prefs["energy"] - song["energy"])))
            score += energy_pts
            reasons.append(f"+{energy_pts:.2f} energy closeness")

        # Acoustic fit: up to +0.5 points
        if "likes_acoustic" in user_prefs:
            if user_prefs["likes_acoustic"]:
                acoustic_pts = 0.5 * song.get("acousticness", 0.5)
                score += acoustic_pts
                if acoustic_pts > 0.3:
                    reasons.append(f"+{acoustic_pts:.2f} acoustic sound")
            else:
                acoustic_pts = 0.5 * (1.0 - song.get("acousticness", 0.5))
                score += acoustic_pts
                if acoustic_pts > 0.3:
                    reasons.append(f"+{acoustic_pts:.2f} electronic/produced sound")

        # Add new bonuses with energy focus
        popularity_pts = (song.get("popularity", 50) / 100) * 0.3
        score += popularity_pts
        reasons.append(f"+{popularity_pts:.2f} popularity bonus")

        artist_pop_pts = (song.get("artist_popularity", 50) / 100) * 0.15
        score += artist_pop_pts
        reasons.append(f"+{artist_pop_pts:.2f} artist popularity bonus")

        if user_prefs.get("mood") in song.get("detailed_mood_tags", []):
            score += 0.3
            reasons.append("+0.3 detailed mood tag match")

        if song.get("release_year", 2000) >= 2020:
            score += 0.2
            reasons.append("+0.2 modern release bonus")

        length = song.get("song_length_seconds", 200)
        if 180 <= length <= 240:
            score += 0.1
            reasons.append("+0.1 ideal length bonus")

        if song.get("language") == "English":
            score += 0.05
            reasons.append("+0.05 English language bonus")

        if song.get("explicit", 0) == 1:
            score -= 0.3
            reasons.append("-0.3 explicit content penalty")

        if not reasons:
            reasons.append("weak overall match")

        return (score, reasons)

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song], scorer: Optional[Scorer] = None):
        self.songs = songs
        self.scorer = scorer or BalancedScorer()

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score all songs against a user profile and return the top k sorted by score."""
        scored = []
        for song in self.songs:
            song_dict = {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "tempo_bpm": song.tempo_bpm,
                "valence": song.valence,
                "danceability": song.danceability,
                "acousticness": song.acousticness,
                "popularity": song.popularity,
                "release_year": song.release_year,
                "detailed_mood_tags": song.detailed_mood_tags,
                "artist_popularity": song.artist_popularity,
                "song_length_seconds": song.song_length_seconds,
                "language": song.language,
                "explicit": song.explicit,
            }
            user_dict = {
                "genre": user.favorite_genre,
                "mood": user.favorite_mood,
                "energy": user.target_energy,
                "likes_acoustic": user.likes_acoustic,
            }
            score, _ = self.scorer.score_song(user_dict, song_dict)
            scored.append((song, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a semicolon-joined string of reasons why a song matches a user."""
        song_dict = {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "tempo_bpm": song.tempo_bpm,
            "valence": song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
            "popularity": song.popularity,
            "release_year": song.release_year,
            "detailed_mood_tags": song.detailed_mood_tags,
            "artist_popularity": song.artist_popularity,
            "song_length_seconds": song.song_length_seconds,
            "language": song.language,
            "explicit": song.explicit,
        }
        user_dict = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        _, reasons = self.scorer.score_song(user_dict, song_dict)
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Parse a CSV file and return a list of song dicts with typed values."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "popularity": int(row["popularity"]),
                "release_year": int(row["release_year"]),
                "detailed_mood_tags": row["detailed_mood_tags"].split(",") if row["detailed_mood_tags"] else [],
                "artist_popularity": int(row["artist_popularity"]),
                "song_length_seconds": int(row["song_length_seconds"]),
                "language": row["language"],
                "explicit": int(row["explicit"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user prefs and return (points, reasons). Max ~6.0."""
    score = 0.0
    reasons = []

    # Genre match: +1.0 points (reduced importance)
    if song["genre"] == user_prefs.get("genre"):
        score += 1.0
        reasons.append(f"+1.0 genre match ({song['genre']})")

    # Mood match: +1.0 point
    if song["mood"] == user_prefs.get("mood"):
        score += 1.0
        reasons.append(f"+1.0 mood match ({song['mood']})")

    # Energy closeness: up to +2.0 points (increased importance)
    if "energy" in user_prefs:
        energy_pts = max(0.0, 2.0 * (1.0 - abs(user_prefs["energy"] - song["energy"])))
        score += energy_pts
        reasons.append(f"+{energy_pts:.2f} energy closeness")

    # Acoustic fit: up to +0.5 points
    if "likes_acoustic" in user_prefs:
        if user_prefs["likes_acoustic"]:
            acoustic_pts = 0.5 * song.get("acousticness", 0.5)
            score += acoustic_pts
            if acoustic_pts > 0.3:
                reasons.append(f"+{acoustic_pts:.2f} acoustic sound")
        else:
            acoustic_pts = 0.5 * (1.0 - song.get("acousticness", 0.5))
            score += acoustic_pts
            if acoustic_pts > 0.3:
                reasons.append(f"+{acoustic_pts:.2f} electronic/produced sound")

    # Popularity bonus: up to +0.5 points
    popularity_pts = (song.get("popularity", 50) / 100) * 0.5
    score += popularity_pts
    reasons.append(f"+{popularity_pts:.2f} popularity bonus")

    # Artist popularity bonus: up to +0.25 points
    artist_pop_pts = (song.get("artist_popularity", 50) / 100) * 0.25
    score += artist_pop_pts
    reasons.append(f"+{artist_pop_pts:.2f} artist popularity bonus")

    # Detailed mood tags match: +0.5 if user's mood is in tags
    if user_prefs.get("mood") in song.get("detailed_mood_tags", []):
        score += 0.5
        reasons.append("+0.5 detailed mood tag match")

    # Release year bonus: +0.3 for modern music (2020+)
    if song.get("release_year", 2000) >= 2020:
        score += 0.3
        reasons.append("+0.3 modern release bonus")

    # Song length bonus: +0.2 for ideal length (180-240 seconds)
    length = song.get("song_length_seconds", 200)
    if 180 <= length <= 240:
        score += 0.2
        reasons.append("+0.2 ideal length bonus")

    # Language bonus: +0.1 for English
    if song.get("language") == "English":
        score += 0.1
        reasons.append("+0.1 English language bonus")

    # Explicit penalty: -0.5 if explicit
    if song.get("explicit", 0) == 1:
        score -= 0.5
        reasons.append("-0.5 explicit content penalty")

    if not reasons:
        reasons.append("weak overall match")

    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, scorer: Optional[Scorer] = None) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort by score descending, and return the top k with explanations."""
    if scorer is None:
        scorer = BalancedScorer()
    scored = []
    for song in songs:
        score, reasons = scorer.score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored.append((song, score, explanation))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
