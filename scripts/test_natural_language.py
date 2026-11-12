from src.preference_parser import parse_user_preferences

test_requests = [
    "I want music that lights me up and gives me more energy.",
    "I am tired.",
    "Give me something that gets my blood pumping.",
    "I need a soundtrack to help me unwind after a stressful day.",
    "I feel exhausted, but I want music that keeps me awake.",
]

for request in test_requests:
    print(f"\nInput: {request}")

    result = parse_user_preferences(request)

    print(f"Parsed: {result}")
