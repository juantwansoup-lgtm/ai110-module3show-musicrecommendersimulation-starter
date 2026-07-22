"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender against a set of
user taste profiles.

Two groups of profiles are defined below:

- NORMAL_PROFILES: coherent, everyday listeners.
- ADVERSARIAL_PROFILES: edge cases designed during "System Evaluation" to
  probe whether the scoring logic can be tricked or produce surprising
  results (conflicting signals, out-of-range values, unknown categories,
  and a completely empty profile).

The recommender functions live in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from typing import Dict

from src.recommender import load_songs, recommend_songs


# ---------------------------------------------------------------------------
# Normal profiles — coherent tastes a real listener might have.
# ---------------------------------------------------------------------------
NORMAL_PROFILES: Dict[str, Dict] = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9},
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9},
}


# ---------------------------------------------------------------------------
# Adversarial / edge-case profiles — built to stress-test the scoring rule.
# Each one targets a specific weakness in score_song().
# ---------------------------------------------------------------------------
ADVERSARIAL_PROFILES: Dict[str, Dict] = {
    # Conflicting signals: asks for maximum energy but a low-energy, downbeat
    # mood. No catalog song can satisfy both pulls at once, so the ranking
    # should reveal that the two preferences fight each other.
    "Conflicting: hyped but sad": {
        "genre": "classical",
        "mood": "melancholy",
        "energy": 0.95,
    },
    # Out-of-range energy: 2.0 is outside the valid 0-1 feature range. The
    # energy term 2.0 * (1 - |song - target|) goes NEGATIVE, turning the
    # bonus into a penalty. Nothing clamps the input, so watch for negative
    # scores.
    "Out-of-range energy": {"genre": "metal", "mood": "angry", "energy": 2.0},
    # Unknown categories: a genre and mood that appear nowhere in the catalog.
    # Both categorical bonuses die, and ranking collapses to pure energy
    # proximity around 0.5.
    "Unknown genre & mood": {"genre": "polka", "mood": "ecstatic", "energy": 0.5},
    # Empty profile: no preferences at all. get() returns None everywhere, the
    # energy term is skipped entirely, and every song scores 0.0 — so the
    # "top 5" is just whatever order ties resolve to.
    "Empty profile": {},
}


def describe_profile(prefs: Dict) -> str:
    """Render a preference dict as a short, readable one-liner."""
    if not prefs:
        return "(empty - no preferences)"
    return ", ".join(f"{key}={value}" for key, value in prefs.items())


def run_profile(name: str, prefs: Dict, songs, k: int = 5) -> None:
    """Score the catalog for one profile and print its top-k recommendations."""
    recommendations = recommend_songs(prefs, songs, k=k)

    print("\n" + "=" * 60)
    print(f"  {name}")
    print(f"  Profile: {describe_profile(prefs)}")
    print("=" * 60 + "\n")

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} - {song['artist']}   (score: {score:.2f})")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    print("\n" + "#" * 60)
    print("#  NORMAL PROFILES")
    print("#" * 60)
    for name, prefs in NORMAL_PROFILES.items():
        run_profile(name, prefs, songs)

    print("\n" + "#" * 60)
    print("#  ADVERSARIAL / EDGE-CASE PROFILES")
    print("#" * 60)
    for name, prefs in ADVERSARIAL_PROFILES.items():
        run_profile(name, prefs, songs)


if __name__ == "__main__":
    main()
