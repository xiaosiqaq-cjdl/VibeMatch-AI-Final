import re


SUPPORTED_GENRES = (
    "pop", "rock", "jazz", "classical", "electronic",
    "hip-hop", "r-n-b", "country", "metal", "ambient"
)

MOOD_KEYWORDS = {
    "calm": ("calm", "relaxing", "peaceful", "soothing"),
    "happy": ("happy", "joyful", "cheerful", "upbeat"),
    "sad": ("sad", "melancholic", "depressing"),
    "intense": ("intense", "aggressive", "angry"),
}


def detect_explicit_preferences(user_request):
    """Extract preferences using deterministic rules."""
    text = user_request.lower()
    detected = {}

    # Explicit genre detection
    for genre in SUPPORTED_GENRES:
        pattern = rf"(?<!\w){re.escape(genre)}(?!\w)"
        if re.search(pattern, text):
            detected["genre"] = genre
            break

    # Explicit mood detection
    
    # Explicit mood detection with simple negation handling
    for mood, keywords in MOOD_KEYWORDS.items():
        for keyword in keywords:
            pattern = rf"\b{re.escape(keyword)}\b"

            for match in re.finditer(pattern, text):
                before = text[max(0, match.start() - 35):match.start()]

                # Detect negation close to the keyword
                negated = re.search(
                    r"\b(?:not|no|avoid|without|don't want|do not want)"
                    r"(?:\s+\w+){0,3}\s*$",
                    before
                )

                if not negated:
                    detected["mood"] = mood
                    break

            if "mood" in detected:
                break

        if "mood" in detected:
            break


    # Explicit numerical tempo
    tempo_match = re.search(
        r"\b(\d{2,3})\s*bpm\b",
        text
    )

    if tempo_match:
        detected["tempo_bpm"] = int(tempo_match.group(1))

    # Acoustic preference, including simple negation
    if re.search(r"\b(no|avoid|without|don't want)\s+acoustic\b", text):
        detected["likes_acoustic"] = False
    elif re.search(r"\bacoustic\b", text):
        detected["likes_acoustic"] = True

    # Explicit energy phrases
    if re.search(r"\b(high energy|energetic)\b", text):
        detected["energy"] = 0.8
    elif re.search(r"\b(low energy|gentle)\b", text):
        detected["energy"] = 0.2

    return detected


def validate_and_correct(user_request, llm_preferences):
    """Correct explicit preferences while preserving other LLM fields."""

    corrected = llm_preferences.copy()
    detected = detect_explicit_preferences(user_request)

    corrections = []

    for field, value in detected.items():
        if corrected.get(field) != value:
            corrections.append({
                "field": field,
                "before": corrected.get(field),
                "after": value
            })

            corrected[field] = value

    return corrected, corrections
