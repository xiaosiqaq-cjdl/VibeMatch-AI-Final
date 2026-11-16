import csv
import time
from pathlib import Path

from src.preference_parser import parse_user_preferences
from src.preference_validator import validate_and_correct

TEST_CASES = [
    {
        "input": "I need something to get me through a tough workout.",
        "expected": {
            "energy": 0.8,
        },
    },
    {
        "input": "I'd like mellow tunes while I read before bed.",
        "expected": {
            "energy": 0.2,
        },
    },
    {
        "input": "Today was exhausting, but I need music to stay alert.",
        "expected": {
            "energy": 0.8,
        },
    },
    {
        "input": "I'm feeling down today.",
        "expected": {},
    },
    {
        "input": "Play some blues around 95 BPM.",
        "expected": {
            "genre": "blues",
            "tempo_bpm": 95,
        },
    },
    {
        "input": "I could really use something cheerful right now.",
        "expected": {
            "mood": "happy",
        },
    },
    {
        "input": "I want music without acoustic instruments.",
        "expected": {
            "likes_acoustic": False,
        },
    },
    {
        "input": "Something peaceful to help me settle down.",
        "expected": {
            "mood": "calm",
        },
    },
]


def evaluate_case(case, think):
    """
    Evaluate one request using the selected thinking mode.
    Measure accuracy and inference latency.
    """
    start = time.perf_counter()

    try:
        actual = parse_user_preferences(
        case["input"],
        think=think
        )

        corrected, corrections = validate_and_correct(
            case["input"],
            actual
        )       

        elapsed = time.perf_counter() - start

        # Expand expected values: unspecified fields must be None
        expected = {
            "genre": None,
            "mood": None,
            "energy": None,
            "tempo_bpm": None,
            "valence": None,
            "likes_acoustic": None,
        }
        expected.update(case["expected"])

        # Exact match across all six fields
        correct = actual == expected
        hybrid_correct = corrected == expected

        # Count unsupported non-null fields
        unsupported = sum(
            1
            for field, value in actual.items()
            if value is not None
            and expected.get(field) is None
        )

        return {
            "input": case["input"],
            "thinking": think,
            "correct": correct,
            "unsupported_fields": unsupported,
            "latency_seconds": round(elapsed, 3),
            "expected": str(expected),
            "actual": str(actual),
            "hybrid_correct": hybrid_correct,
            "corrected": str(corrected),
            "corrections": str(corrections),
        }

    except Exception as exc:
        return {
            "input": case["input"],
            "thinking": think,
            "correct": False,
            "unsupported_fields": 0,
            "latency_seconds": round(
                time.perf_counter() - start, 3
            ),
            "expected": str(case["expected"]),
            "actual": f"ERROR: {exc}",
            "hybrid_correct": False,
            "corrected": "",
            "corrections": "",
        }



def main():
    results = []

    # Test each request with both thinking modes
    for index, case in enumerate(TEST_CASES, start=1):
        print(f"\nTesting {index}/{len(TEST_CASES)}")

        for think in (False, True):
            print(f"  Thinking={think}...")

            result = evaluate_case(case, think)
            results.append(result)

            print(
                f"  Correct: {result['correct']} | "
                f"Time: {result['latency_seconds']:.2f}s"
            )

    # Save detailed results
    output_file = Path("evaluation_thinking.csv")

    with output_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    # Summarize the results
    
    print("\n=== Thinking Evaluation Summary ===")

    for think in (False, True):
        subset = [
            result for result in results
            if result["thinking"] == think
        ]

        total = len(subset)

        raw_passed = sum(
            result["correct"] for result in subset
        )

        hybrid_passed = sum(
            result["hybrid_correct"] for result in subset
        )

        avg_latency = sum(
            result["latency_seconds"] for result in subset
        ) / total

        unsupported = sum(
            result["unsupported_fields"] for result in subset
        )

        print(f"\nThinking={think}")
        print(f"  Raw: {raw_passed}/{total} ({raw_passed / total:.2%})")
        print(f"  Hybrid: {hybrid_passed}/{total} ({hybrid_passed / total:.2%})")
        print(f"  Average latency: {avg_latency:.2f}s")
        print(f"  Unsupported fields: {unsupported}")

    print(f"\nResults saved to: {output_file}")



if __name__ == "__main__":
    main()
