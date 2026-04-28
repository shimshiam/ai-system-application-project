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


class WeightedScorer(Scorer):
    """Base scorer with configurable primary weights and shared bonus logic.

    Subclasses set weight constants to control emphasis without
    duplicating the bonus pipeline.
    """

    # --- override in subclasses ---
    GENRE_WEIGHT: float = 1.0
    MOOD_WEIGHT: float = 1.0
    ENERGY_WEIGHT: float = 2.0
    MOOD_TAG_BONUS: float = 0.5
    POPULARITY_WEIGHT: float = 0.5
    ARTIST_POP_WEIGHT: float = 0.25
    RELEASE_BONUS: float = 0.3
    LENGTH_BONUS: float = 0.2
    LANGUAGE_BONUS: float = 0.1
    EXPLICIT_PENALTY: float = 0.5

    def _score_primary(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Score the three primary features (genre, mood, energy)."""
        score = 0.0
        reasons: List[str] = []

        if song["genre"] == user_prefs.get("genre"):
            score += self.GENRE_WEIGHT
            reasons.append(f"+{self.GENRE_WEIGHT:.1f} genre match ({song['genre']})")

        if song["mood"] == user_prefs.get("mood"):
            score += self.MOOD_WEIGHT
            reasons.append(f"+{self.MOOD_WEIGHT:.1f} mood match ({song['mood']})")

        if "energy" in user_prefs:
            energy_pts = max(0.0, self.ENERGY_WEIGHT * (1.0 - abs(user_prefs["energy"] - song["energy"])))
            score += energy_pts
            reasons.append(f"+{energy_pts:.2f} energy closeness")

        return score, reasons

    def _score_acoustic(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Score acoustic fit: up to +0.5 points."""
        score = 0.0
        reasons: List[str] = []

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

        return score, reasons

    def _common_bonuses(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Shared bonus/penalty logic used by all weighted scorers."""
        score = 0.0
        reasons: List[str] = []

        # Popularity bonus
        popularity_pts = (song.get("popularity", 50) / 100) * self.POPULARITY_WEIGHT
        score += popularity_pts
        reasons.append(f"+{popularity_pts:.2f} popularity bonus")

        # Artist popularity bonus
        artist_pop_pts = (song.get("artist_popularity", 50) / 100) * self.ARTIST_POP_WEIGHT
        score += artist_pop_pts
        reasons.append(f"+{artist_pop_pts:.2f} artist popularity bonus")

        # Detailed mood tag match
        if user_prefs.get("mood") in song.get("detailed_mood_tags", []):
            score += self.MOOD_TAG_BONUS
            reasons.append(f"+{self.MOOD_TAG_BONUS} detailed mood tag match")

        # Modern release bonus
        if song.get("release_year", 2000) >= 2020:
            score += self.RELEASE_BONUS
            reasons.append(f"+{self.RELEASE_BONUS} modern release bonus")

        # Ideal song length bonus
        length = song.get("song_length_seconds", 200)
        if 180 <= length <= 240:
            score += self.LENGTH_BONUS
            reasons.append(f"+{self.LENGTH_BONUS} ideal length bonus")

        # English language bonus
        if song.get("language") == "English":
            score += self.LANGUAGE_BONUS
            reasons.append(f"+{self.LANGUAGE_BONUS} English language bonus")

        # Explicit content penalty
        if song.get("explicit", 0) == 1:
            score -= self.EXPLICIT_PENALTY
            reasons.append(f"-{self.EXPLICIT_PENALTY} explicit content penalty")

        return score, reasons

    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Assemble the full score from primary features, acoustic fit, and bonuses."""
        p_score, p_reasons = self._score_primary(user_prefs, song)
        a_score, a_reasons = self._score_acoustic(user_prefs, song)
        b_score, b_reasons = self._common_bonuses(user_prefs, song)

        total = p_score + a_score + b_score
        reasons = p_reasons + a_reasons + b_reasons

        if not reasons:
            reasons.append("weak overall match")

        return (total, reasons)


class BalancedScorer(WeightedScorer):
    """Default balanced scoring strategy (matches standalone score_song weights)."""
    GENRE_WEIGHT = 1.0
    MOOD_WEIGHT = 1.0
    ENERGY_WEIGHT = 2.0
    MOOD_TAG_BONUS = 0.5
    POPULARITY_WEIGHT = 0.5
    ARTIST_POP_WEIGHT = 0.25
    RELEASE_BONUS = 0.3
    LENGTH_BONUS = 0.2
    LANGUAGE_BONUS = 0.1
    EXPLICIT_PENALTY = 0.5


class GenreFirstScorer(WeightedScorer):
    """Prioritizes genre matches with higher weights."""
    GENRE_WEIGHT = 2.0
    MOOD_WEIGHT = 0.5
    ENERGY_WEIGHT = 1.0
    MOOD_TAG_BONUS = 0.3
    POPULARITY_WEIGHT = 0.3
    ARTIST_POP_WEIGHT = 0.15
    RELEASE_BONUS = 0.2
    LENGTH_BONUS = 0.1
    LANGUAGE_BONUS = 0.05
    EXPLICIT_PENALTY = 0.3


class MoodFirstScorer(WeightedScorer):
    """Prioritizes mood matches with higher weights."""
    GENRE_WEIGHT = 0.5
    MOOD_WEIGHT = 2.0
    ENERGY_WEIGHT = 1.0
    MOOD_TAG_BONUS = 0.8
    POPULARITY_WEIGHT = 0.3
    ARTIST_POP_WEIGHT = 0.15
    RELEASE_BONUS = 0.2
    LENGTH_BONUS = 0.1
    LANGUAGE_BONUS = 0.05
    EXPLICIT_PENALTY = 0.3


class EnergyFocusedScorer(WeightedScorer):
    """Prioritizes energy closeness with higher weights."""
    GENRE_WEIGHT = 0.5
    MOOD_WEIGHT = 0.5
    ENERGY_WEIGHT = 3.0
    MOOD_TAG_BONUS = 0.3
    POPULARITY_WEIGHT = 0.3
    ARTIST_POP_WEIGHT = 0.15
    RELEASE_BONUS = 0.2
    LENGTH_BONUS = 0.1
    LANGUAGE_BONUS = 0.05
    EXPLICIT_PENALTY = 0.3


class ResonanceScorer(Scorer):
    """Resonance-based scorer that measures harmonic fit to a user's target vibe."""

    MOOD_TO_VALENCE = {
        "happy": 0.8,
        "upbeat": 0.75,
        "chill": 0.4,
        "focused": 0.35,
        "relaxed": 0.3,
        "intense": 0.85,
        "confident": 0.65,
    }

    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        # Extract preferences with sensible defaults
        target_energy = float(user_prefs.get("energy", 0.5))
        tuning_shift = float(user_prefs.get("tuning_shift", 0.0))
        target_energy = max(0.0, min(1.0, target_energy + tuning_shift))

        target_mood = user_prefs.get("mood", "")
        target_valence = float(self.MOOD_TO_VALENCE.get(target_mood, 0.5))

        reasons: List[str] = []

        # Energy match (0..1)
        song_energy = float(song.get("energy", 0.5))
        energy_match = max(0.0, 1.0 - abs(target_energy - song_energy))
        reasons.append(f"energy_match={energy_match:.2f}")

        # Valence proximity (0..1)
        song_valence = float(song.get("valence", 0.5))
        valence_match = max(0.0, 1.0 - abs(target_valence - song_valence))
        reasons.append(f"valence_match={valence_match:.2f}")

        # Mood tag resonance (1.0 if user's mood in song tags)
        mood_resonance = 1.0 if target_mood in song.get("detailed_mood_tags", []) else 0.0
        if mood_resonance:
            reasons.append("mood_tag_resonance")

        # Acoustic alignment (0..1)
        likes_acoustic = bool(user_prefs.get("likes_acoustic", False))
        acousticness = float(song.get("acousticness", 0.5))
        acoustic_match = acousticness if likes_acoustic else (1.0 - acousticness)
        reasons.append(f"acoustic_match={acoustic_match:.2f}")

        # Combine into a resonance score (0..1)
        resonance_raw = (
            0.5 * energy_match
            + 0.2 * valence_match
            + 0.2 * mood_resonance
            + 0.1 * acoustic_match
        )

        # Scale to be roughly comparable with other scorers
        score = resonance_raw * 3.0
        if resonance_raw > 0.85:
            reasons.append("strong resonance")
        elif resonance_raw > 0.6:
            reasons.append("good resonance")
        else:
            reasons.append("weak resonance")

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
