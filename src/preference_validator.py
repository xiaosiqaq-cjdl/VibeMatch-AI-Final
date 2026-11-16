import re



import csv
from pathlib import Path


def load_supported_genres():
    """Load available genres from the cleaned song dataset."""

    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "songs_full.csv"

    genres = set()

    with csv_path.open(
        "r", encoding="utf-8", newline=""
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            genre = row["genre"].strip().lower()

            if genre:
                genres.add(genre)

    return tuple(sorted(genres, key=len, reverse=True))


SUPPORTED_GENRES = load_supported_genres()

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
    # Avoid interpreting "acoustic" as a genre when
    # the user is referring to instruments or sound texture.
    
    # Explicit genre detection with negation handling
    for genre in SUPPORTED_GENRES:
        if genre == "acoustic":
            continue

        pattern = rf"(?<!\w){re.escape(genre)}(?!\w)"

        for match in re.finditer(pattern, text):
            before = text[max(0, match.start() - 40):match.start()]

            negated = re.search(
                r"\b(?:no|not|avoid|without|don't want|do not want)"
                r"(?:\s+\w+){0,3}\s*$",
                before
            )

            if negated:
                continue

            detected["genre"] = genre
            break

        if "genre" in detected:
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



def detect_negated_genres(user_request):
    """Detect explicitly rejected music genres."""
    text = user_request.lower()
    rejected = set()

    for genre in SUPPORTED_GENRES:
        pattern = rf"(?<!\w){re.escape(genre)}(?!\w)"

        for match in re.finditer(pattern, text):
            before = text[max(0, match.start() - 40):match.start()]

            negated = re.search(
                r"\b(?:no|not|avoid|without|don't want|do not want)"
                r"(?:\s+\w+){0,3}\s*$",
                before
            )

            if negated:
                rejected.add(genre)

    return rejected


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

    rejected_genres = detect_negated_genres(user_request)

    if corrected.get("genre") in rejected_genres:
        corrections.append({
            "field": "genre",
            "before": corrected["genre"],
            "after": None,
        })
        corrected["genre"] = None

    return corrected, corrections
