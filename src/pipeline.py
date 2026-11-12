from src.preference_validator import validate_and_correct
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

    if all(value is None for value in ranking_prefs.values()):
        return {
            "user_request": user_request,
            "parsed_preferences": parsed,
            "corrected_preferences": corrected,
            "corrections": corrections,
            "ranking_preferences": ranking_prefs,
            "defaulted_fields": defaulted_fields,
            "recommendations": [],
            "needs_clarification": True,
        }

    # Step 3: Use our own ranking algorithm
    recommendations = retrieve_songs(
        ranking_prefs,
        songs,
        k=5
    )

    return {
        "user_request": user_request,
        "parsed_preferences": parsed,
        "corrected_preferences": corrected,
        "corrections": corrections,
        "ranking_preferences": ranking_prefs,
        "defaulted_fields": defaulted_fields,
        "recommendations": recommendations,
        "needs_clarification": False,
    }
