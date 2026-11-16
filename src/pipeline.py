from src.preference_validator import (
    validate_and_correct,
    detect_negated_genres,
)
from src.preference_parser import parse_user_preferences
from src.ai_recommender import retrieve_songs




def build_ranking_preferences(parsed, defaults=None):
    """
    Preserve explicitly extracted preferences.

    Missing preferences remain None so they can be
    excluded from the ranking calculation.
    """
    fields = (
        "genre",
        "mood",
        "energy",
        "tempo_bpm",
        "valence",
        "likes_acoustic",
    )

    ranking_prefs = {
        field: parsed.get(field)
        for field in fields
    }

    unspecified_fields = [
        field
        for field, value in ranking_prefs.items()
        if value is None
    ]

    return ranking_prefs, unspecified_fields



def run_ai_recommender(user_request, songs, defaults, client=None):
    """
    Natural language -> LLM parser -> ranking -> results.
    """

    # Step 1: Extract preferences using Qwen
    parsed = parse_user_preferences(
        user_request,
        client=client
    )
    corrected, corrections = validate_and_correct(
    user_request,
    parsed
)

    # Step 2: Prepare preferences for the existing algorithm
    ranking_prefs, defaulted_fields = build_ranking_preferences(
        corrected,
        defaults
    )


    
    # Detect genres the user wants to exclude
    excluded_genres = detect_negated_genres(user_request)

    # Filter candidate songs before ranking
    filtered_songs = [
        song
        for song in songs
        if song["genre"].lower() not in excluded_genres
    ]

    has_positive_preferences = any(
        value is not None
        for value in ranking_prefs.values()
    )

    if has_positive_preferences:
        recommendations = retrieve_songs(
            ranking_prefs,
            filtered_songs,
            k=5
        )
    elif excluded_genres:
        # Exclusion-only fallback:
        # prioritize popularity without inventing preferences
        ranked = sorted(
            filtered_songs,
            key=lambda song: (
                -int(song.get("popularity", 0)),
                str(song["id"])
            )
        )

        recommendations = [
            {
                **song,
                "score": None,
                "reasons": "Popular song outside excluded genres"
            }
            for song in ranked[:5]
        ]
    else:
        # No usable musical preference
        recommendations = []


    
    return {
        "user_request": user_request,
        "parsed_preferences": parsed,
        "corrected_preferences": corrected,
        "corrections": corrections,
        "ranking_preferences": ranking_prefs,
        "defaulted_fields": defaulted_fields,
        "recommendations": recommendations,
        "excluded_genres": sorted(excluded_genres),
        "candidate_count": len(filtered_songs),
        "needs_clarification": (
            not has_positive_preferences
            and not excluded_genres
        ),
        "ranking_strategy": (
            "preference_score"
            if has_positive_preferences
            else "popularity_fallback"
            if excluded_genres
            else "clarification"
        ),
    }

