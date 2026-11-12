
from src.recommender import load_songs
from src.pipeline import run_ai_recommender


DEFAULT_PREFERENCES = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.7,
    "tempo_bpm": 120,
    "valence": 0.7,
    "likes_acoustic": False,
}


def main():
    songs = load_songs("data/songs_real.csv")

    print("=== VibeMatch AI ===")
    print(f"Loaded {len(songs)} songs.")

    user_request = input(
        "\nDescribe the music you want: "
    ).strip()

    if not user_request:
        print("Please enter a music preference.")
        return

    try:
        result = run_ai_recommender(
            user_request,
            songs,
            DEFAULT_PREFERENCES
        )

    except Exception as exc:
        print(f"Recommendation failed: {exc}")
        return

    
    print("\n--- Raw LLM Preferences ---")
    for key, value in result["parsed_preferences"].items():
        print(f"{key}: {value}")

    print("\n--- Validated Preferences ---")
    for key, value in result["corrected_preferences"].items():
        print(f"{key}: {value}")

    print("\n--- Deterministic Corrections ---")

    if result["corrections"]:
        for correction in result["corrections"]:
            print(
                f"{correction['field']}: "
                f"{correction['before']} -> {correction['after']}"
            )
    else:
        print("No corrections needed.")


    if result["defaulted_fields"]:
        print("\n--- Unspecified Preferences (Excluded from Ranking) ---")
        print(", ".join(result["defaulted_fields"]))

    print("\n--- Top 5 Recommendations ---")

    for index, song in enumerate(result["recommendations"], start=1):
        print(
            f"\n{index}. {song['title']} "
            f"- {song['artist']}"
        )
        print(f"Score: {song['score']:.2f}/100")
        print(f"Reason: {song['reasons']}")


if __name__ == "__main__":
    main()
