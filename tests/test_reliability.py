import random

import pytest

from src.recommender import load_songs, score_song, recommend_songs


@pytest.fixture
def songs():
    """Load the real Spotify dataset."""
    return load_songs("data/songs_real.csv")


def test_order_invariance(songs):
    """Shuffling input should not change recommendation ranking."""

    prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "tempo_bpm": 120,
        "valence": 0.8,
        "likes_acoustic": False,
    }

    original = recommend_songs(prefs, songs, k=10)

    shuffled = songs.copy()
    random.Random(42).shuffle(shuffled)

    reordered = recommend_songs(prefs, shuffled, k=10)

    original_ids = [song["id"] for song, _, _ in original]
    reordered_ids = [song["id"] for song, _, _ in reordered]

    assert original_ids == reordered_ids


def test_preference_sensitivity(songs):
    """A song should score higher when the energy preference matches."""

    song = songs[0]

    matching = {
        "energy": song["energy"]
    }

    mismatching = {
        "energy": 1.0 if song["energy"] < 0.5 else 0.0
    }

    matching_score, _ = score_song(matching, song)
    mismatching_score, _ = score_song(mismatching, song)

    assert matching_score > mismatching_score


def test_unspecified_preferences(songs):
    """Unspecified attributes should not affect ranking."""

    song = songs[0]

    first = {
        "mood": "calm",
        "genre": None,
        "energy": None
    }

    second = {
        "mood": "calm"
    }

    score1, _ = score_song(first, song)
    score2, _ = score_song(second, song)

    assert score1 == pytest.approx(score2)


def test_empty_preferences(songs):
    """The system should reject completely empty preferences."""

    with pytest.raises(ValueError, match="At least one"):
        score_song({}, songs[0])



from src.preference_validator import detect_explicit_preferences


def test_negated_mood_not_extracted():
    result = detect_explicit_preferences(
        "I don't want relaxing music."
    )

    assert result.get("mood") is None


def test_positive_mood_still_extracted():
    result = detect_explicit_preferences(
        "I want relaxing music."
    )

    assert result["mood"] == "calm"


def test_avoid_sad_music():
    result = detect_explicit_preferences(
        "Avoid sad music."
    )

    assert result.get("mood") is None



def test_popularity_tiebreaker():
    """Higher popularity should win when match scores are equal."""

    songs = [
        {
            "id": "song_low",
            "genre": "blues",
            "popularity": 20,
        },
        {
            "id": "song_high",
            "genre": "blues",
            "popularity": 90,
        },
    ]

    results = recommend_songs(
        {"genre": "blues"},
        songs,
        k=2,
    )

    assert results[0][0]["id"] == "song_high"
    assert results[1][0]["id"] == "song_low"
