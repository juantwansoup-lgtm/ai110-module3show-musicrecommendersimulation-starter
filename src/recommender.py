import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    @staticmethod
    def _prefs(user: UserProfile) -> Dict:
        """Adapt a UserProfile into the dict shape score_song() expects."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Scores every song against the user profile and returns the top `k`
        Song objects, highest score first. Reuses the same score_song() recipe
        as the functional API so both paths rank identically.
        """
        prefs = self._prefs(user)
        ranked = sorted(
            self.songs,
            key=lambda song: score_song(prefs, asdict(song))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a plain-English explanation of why `song` fits the user."""
        _, reasons = score_song(self._prefs(user), asdict(song))
        if not reasons:
            return "No strong matches, but included to fill out the list."
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file into a list of dictionaries.

    Numeric fields are converted from strings to numbers so they can be used
    in scoring math later: `id` and `tempo_bpm` become ints, and the 0-1
    feature columns (energy, valence, danceability, acousticness) become floats.
    Text fields (title, artist, genre, mood) are left as strings.

    Required by src/main.py
    """
    int_fields = {"id", "tempo_bpm"}
    float_fields = {"energy", "valence", "danceability", "acousticness"}

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song: Dict = dict(row)
            for field in int_fields:
                song[field] = int(song[field])
            for field in float_fields:
                song[field] = float(song[field])
            songs.append(song)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences using the finalized
    Algorithm Recipe (see README "How The System Works"):

      +2.0                          for an exact genre match
      +1.5                          for an exact mood match
      +2.0 * (1 - |energy diff|)    energy proximity (continuous, 0-2.0)
      +0.5                          acoustic bonus when the user likes acoustic
                                    and the song is acoustic (acousticness >= 0.7)

    Returns a tuple of (score, reasons), where `reasons` is a list of
    plain-English strings explaining each point contribution.

    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons: List[str] = []

    # Genre match (+2.0)
    if user_prefs.get("genre") == song.get("genre"):
        score += 2.0
        reasons.append(f"genre match: {song['genre']} (+2.0)")

    # Mood match (+1.5)
    if user_prefs.get("mood") == song.get("mood"):
        score += 1.5
        reasons.append(f"mood match: {song['mood']} (+1.5)")

    # Energy similarity (+2.0 * closeness)
    target_energy = user_prefs.get("energy")
    if target_energy is not None:
        closeness = 1 - abs(song["energy"] - target_energy)
        energy_points = 2.0 * closeness
        score += energy_points
        reasons.append(
            f"energy {song['energy']:.2f} vs target {target_energy:.2f} "
            f"(+{energy_points:.2f})"
        )

    # Acoustic bonus (+0.5)
    if user_prefs.get("likes_acoustic") and song.get("acousticness", 0) >= 0.7:
        score += 0.5
        reasons.append(f"acoustic pick: acousticness {song['acousticness']:.2f} (+0.5)")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Ranks the whole catalog and returns the top `k` recommendations.

    Every song is judged by score_song(), then the catalog is sorted by score
    (highest first) and the best `k` are returned as (song, score, explanation)
    tuples. The explanation joins the scoring reasons into a readable sentence.

    Required by src/main.py
    """
    # Score every song, building (song, score, explanation) tuples.
    scored = [
        (song, score, "; ".join(reasons) if reasons else "no matching features")
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    # Sort highest score first, then keep the top k.
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
