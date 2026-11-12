from src.preference_validator import validate_and_correct
import json
from pathlib import Path

from src.preference_parser import parse_user_preferences


TEST_CASES = [
    {
        "input": "I want relaxing acoustic music.",
        "expected": {
            "genre": None,
            "mood": "calm",
            "energy": None,
            "tempo_bpm": None,
            "valence": None,
            "likes_acoustic": True,
        },
    },
    {
        "input": "Play some happy pop music.",
        "expected": {
            "genre": "pop",
            "mood": "happy",
            "energy": None,
            "tempo_bpm": None,
            "valence": None,
            "likes_acoustic": None,
        },
    },
    {
        "input": "I want energetic rock music.",
        "expected": {
            "genre": "rock",
            "mood": None,
            "energy": 0.8,
            "tempo_bpm": None,
            "valence": None,
            "likes_acoustic": None,
        },
    },
    {
        "input": "Give me calm jazz.",
        "expected": {
            "genre": "jazz",
            "mood": "calm",
            "energy": None,
            "tempo_bpm": None,
            "valence": None,
            "likes_acoustic": None,
        },
    },
    {
        "input": "I want something sad.",
        "expected": {
            "genre": None,
            "mood": "sad",
            "energy": None,
            "tempo_bpm": None,
            "valence": None,
            "likes_acoustic": None,
        },
    },
    {
        "input": "Play music around 120 BPM.",
        "expected": {
            "genre": None,
            "mood": None,
            "energy": None,
            "tempo_bpm": 120,
            "valence": None,
            "likes_acoustic": None,
        },
    },
    {
        "input": "I prefer electronic music with high energy.",
        "expected": {
            "genre": "electronic",
            "mood": None,
            "energy": 0.8,
            "tempo_bpm": None,
            "valence": None,
            "likes_acoustic": None,
        },
    },
    {
        "input": "Surprise me.",
        "expected": {
            "genre": None,
            "mood": None,
            "energy": None,
            "tempo_bpm": None,
            "valence": None,
            "likes_acoustic": None,
        },
    },
]


def main():
    results = []

    for index, case in enumerate(TEST_CASES, start=1):
        print(f"Testing {index}/{len(TEST_CASES)}...")

        
        try:
            raw = parse_user_preferences(case["input"])

            corrected, corrections = validate_and_correct(
                case["input"],
                raw
            )

            raw_passed = raw == case["expected"]
            hybrid_passed = corrected == case["expected"]

            results.append({
                "input": case["input"],
                "expected": case["expected"],
                "raw": raw,
                "corrected": corrected,
                "corrections": corrections,
                "raw_passed": raw_passed,
                "hybrid_passed": hybrid_passed,
            })

        except Exception as exc:
            results.append({
                "input": case["input"],
                "expected": case["expected"],
                "raw": None,
                "corrected": None,
                "corrections": [],
                "raw_passed": False,
                "hybrid_passed": False,
                "error": str(exc),
            })


    output_path = Path("evaluation_results.json")

    output_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    
    total = len(TEST_CASES)

    raw_passed = sum(
        item["raw_passed"] for item in results
    )

    hybrid_passed = sum(
        item["hybrid_passed"] for item in results
    )

    correction_count = sum(
        len(item["corrections"]) for item in results
    )

    print("\n=== Hybrid Evaluation Summary ===")
    print(
        f"Raw LLM: {raw_passed}/{total} "
        f"({raw_passed / total:.2%})"
    )
    print(
        f"Hybrid: {hybrid_passed}/{total} "
        f"({hybrid_passed / total:.2%})"
    )
    print(f"Total field corrections: {correction_count}")
    print(f"Results saved to: {output_path}")



if __name__ == "__main__":
    main()
