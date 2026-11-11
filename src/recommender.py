from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv
import logging
logger = logging.getLogger(__name__)

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs


    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "tempo_bpm": 100,
            "valence": 0.5,
            "likes_acoustic": user.likes_acoustic,
        }

        song_dicts = [vars(song) for song in self.songs]

        results = recommend_songs(user_prefs, song_dicts, k=k)

        return [
            Song(**song_data)
            for song_data, score, explanation in results
        ]



    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "tempo_bpm": 100,
            "valence": 0.5,
            "likes_acoustic": user.likes_acoustic,
        }

        score, reasons = score_song(user_prefs, vars(song))

        return f"Match score: {score:.2f}/100. " + "; ".join(reasons)



def load_songs(csv_path: str) -> List[Dict]:
    """Load and validate song data from a CSV file."""

    required_fields = {
        "id", "title", "artist", "genre", "mood",
        "energy", "tempo_bpm", "valence",
        "danceability", "acousticness"
    }

    numeric_fields = {
    "energy": float,
    "tempo_bpm": float,
    "valence": float,
    "danceability": float,
    "acousticness": float
    }

    songs = []

    try:
        with open(csv_path, mode="r", encoding="utf-8-sig", newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            if not reader.fieldnames:
                raise ValueError("CSV is empty or has no header.")

            missing = required_fields - set(reader.fieldnames)
            if missing:
                raise ValueError(
                    f"Missing required columns: {sorted(missing)}"
                )

            for line_number, row in enumerate(reader, start=2):
                for field in required_fields:
                    if row.get(field) is None or not str(row[field]).strip():
                        raise ValueError(
                            f"Row {line_number}: missing value in '{field}'"
                        )

                for field, converter in numeric_fields.items():
                    try:
                        row[field] = converter(row[field])
                    except ValueError as exc:
                        raise ValueError(
                            f"Row {line_number}: invalid value for '{field}'"
                        ) from exc

                for field in ("energy", "valence", "danceability", "acousticness"):
                    if not 0 <= row[field] <= 1:
                        raise ValueError(
                            f"Row {line_number}: '{field}' must be between 0 and 1"
                        )

                if row["tempo_bpm"] <= 0:
                    raise ValueError(
                        f"Row {line_number}: tempo_bpm must be positive"
                    )

                songs.append(row)

    except FileNotFoundError as exc:
        logger.error("Song dataset not found: %s", csv_path)
        raise FileNotFoundError(
            f"Song dataset not found: {csv_path}"
        ) from exc

    logger.info("Loaded %d songs from %s", len(songs), csv_path)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    genre_match = user_prefs["genre"].casefold() == song["genre"].casefold()
    mood_match = user_prefs["mood"].casefold() == song["mood"].casefold()

    G = 1.0 if genre_match else 0.0
    M = 1.0 if mood_match else 0.0

    reasons = []


    if genre_match:
        reasons.append("Genre matches")
    if mood_match:
        reasons.append("Mood matches")

    V = 1 - abs(song["valence"] - user_prefs["valence"])
    En = 1 - abs(song["energy"] - user_prefs["energy"])
    T = max(0, 1 - abs(song["tempo_bpm"] - user_prefs["tempo_bpm"]) / 160)

    if user_prefs["likes_acoustic"]:
        C = song["acousticness"]
    else:
        C = 1 - song["acousticness"]

    reasons.append(f"Valence similarity: {V:.2f}")
    reasons.append(f"Energy similarity: {En:.2f}")
    reasons.append(f"Tempo similarity: {T:.2f}")
    reasons.append(f"Acoustic preference match: {C:.2f}")

    emotion_score = 0.70 * M + 0.30 * V
    activity_score = 0.70 * En + 0.30 * T

    score = 100 * (
        0.35 * G
        + 0.30 * emotion_score
        + 0.25 * activity_score
        + 0.10 * C
    )

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    recommendations = []

    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        recommendations.append((song, score, explanation))

    recommendations.sort(key=lambda item: item[1], reverse=True)
    return recommendations[:k]
