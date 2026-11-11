from pathlib import Path

import pytest

from src.recommender import Song, UserProfile, Recommender
from src.recommender import load_songs, recommend_songs


SONGS_CSV = Path(__file__).resolve().parents[1] / "data" / "songs.csv"

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(list(reversed(songs)))


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


@pytest.mark.parametrize(
    ("profile", "expected_top_song"),
    [
        (
            {
                "genre": "pop",
                "mood": "happy",
                "energy": 0.9,
                "tempo_bpm": 130,
                "valence": 0.85,
                "likes_acoustic": False,
            },
            "Sunrise City",
        ),
        (
            {
                "genre": "lofi",
                "mood": "chill",
                "energy": 0.4,
                "tempo_bpm": 78,
                "valence": 0.6,
                "likes_acoustic": True,
            },
            "Library Rain",
        ),
        (
            {
                "genre": "rock",
                "mood": "intense",
                "energy": 0.9,
                "tempo_bpm": 150,
                "valence": 0.5,
                "likes_acoustic": False,
            },
            "Storm Runner",
        ),
    ],
    ids=["high-energy-pop", "chill-lofi", "deep-intense-rock"],
)
def test_recommendations_match_diverse_profiles(profile, expected_top_song):
    songs = load_songs(str(SONGS_CSV))

    results = recommend_songs(profile, songs, k=3)

    assert len(results) == 3
    assert results[0][0]["title"] == expected_top_song
    assert [score for _, score, _ in results] == sorted(
        (score for _, score, _ in results), reverse=True
    )


def test_missing_csv_file():
    with pytest.raises(FileNotFoundError, match="Song dataset not found"):
        load_songs("nonexistent_songs.csv")


def test_missing_required_column(tmp_path):
    bad_csv = tmp_path / "bad_songs.csv"
    bad_csv.write_text(
        "id,title,artist\n1,Test Song,Test Artist\n",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        load_songs(str(bad_csv))


def test_invalid_numeric_value(tmp_path):
    bad_csv = tmp_path / "invalid_songs.csv"
    bad_csv.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness\n"
        "1,Test Song,Test Artist,pop,happy,high,120,0.8,0.7,0.2\n",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="invalid value for 'energy'"):
        load_songs(str(bad_csv))
