
from src import pipeline


def test_excluded_genres_filtering(monkeypatch):
    """Excluded genres must not enter the ranking stage."""

    # Simulate the output from Qwen
    fake_preferences = {
        "genre": None,
        "mood": None,
        "energy": 0.8,
        "tempo_bpm": None,
        "valence": None,
        "likes_acoustic": None,
    }

    # Simulate a small music dataset
    songs = [
        {"id": "1", "genre": "jazz", "title": "Jazz Song"},
        {"id": "2", "genre": "rock", "title": "Rock Song"},
        {"id": "3", "genre": "pop", "title": "Pop Song"},
    ]

    # Replace the LLM call with a predictable result
    monkeypatch.setattr(
        pipeline,
        "parse_user_preferences",
        lambda *args, **kwargs: fake_preferences.copy()
    )

    captured = {}

    # Capture songs passed to the ranking function
    def fake_retrieve(preferences, candidates, k=5):
        captured["preferences"] = preferences
        captured["candidates"] = candidates
        return []

    monkeypatch.setattr(
        pipeline,
        "retrieve_songs",
        fake_retrieve
    )

    # Run the complete pipeline up to the ranking stage
    result = pipeline.run_ai_recommender(
        user_request="I want energetic music, but no jazz.",
        songs=songs,
        defaults={},
    )

    # Verify that jazz songs were excluded
    candidate_genres = {
        song["genre"]
        for song in captured["candidates"]
    }

    assert "jazz" not in candidate_genres
    assert candidate_genres == {"rock", "pop"}

    # Verify the positive preference is preserved
    assert captured["preferences"]["energy"] == 0.8

    # Verify filtering metadata
    assert result["excluded_genres"] == ["jazz"]
    assert result["candidate_count"] == 2



def test_exclusion_only_popularity_fallback(monkeypatch):
    """Exclusion-only requests should use popularity ranking."""

    fake_preferences = {
        "genre": None,
        "mood": None,
        "energy": None,
        "tempo_bpm": None,
        "valence": None,
        "likes_acoustic": None,
    }

    songs = [
        {
            "id": "1",
            "title": "Jazz Song",
            "genre": "jazz",
            "popularity": 99,
        },
        {
            "id": "2",
            "title": "Popular Rock",
            "genre": "rock",
            "popularity": 80,
        },
        {
            "id": "3",
            "title": "Popular Pop",
            "genre": "pop",
            "popularity": 90,
        },
        {
            "id": "4",
            "title": "Less Popular Rock",
            "genre": "rock",
            "popularity": 30,
        },
    ]

    monkeypatch.setattr(
        pipeline,
        "parse_user_preferences",
        lambda *args, **kwargs: fake_preferences.copy(),
    )

    result = pipeline.run_ai_recommender(
        user_request="No jazz music, please.",
        songs=songs,
        defaults={},
    )

    recommendations = result["recommendations"]

    assert result["needs_clarification"] is False
    assert result["ranking_strategy"] == "popularity_fallback"
    assert result["excluded_genres"] == ["jazz"]
    assert result["candidate_count"] == 3

    assert [song["id"] for song in recommendations] == [
        "3", "2", "4"
    ]

    assert all(
        song["genre"] != "jazz"
        for song in recommendations
    )

    assert all(
        song["score"] is None
        for song in recommendations
    )
