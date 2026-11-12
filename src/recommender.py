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
    Score a song using only specified user preferences.
    Normalize active weights to keep scores between 0 and 100.
    """

    weights = {
        "genre": 0.35,
        "mood": 0.21,
        "valence": 0.09,
        "energy": 0.175,
        "tempo_bpm": 0.075,
        "likes_acoustic": 0.10,
    }

    weighted_score = 0.0
    active_weight = 0.0
    reasons = []

    # 1. Genre matching
    genre = user_prefs.get("genre")
    if genre is not None:
        match = float(genre.casefold() == song["genre"].casefold())
        weighted_score += weights["genre"] * match
        active_weight += weights["genre"]

        if match:
            reasons.append("Genre matches")

    # 2. Mood matching
    mood = user_prefs.get("mood")
    if mood is not None:
        match = float(mood.casefold() == song["mood"].casefold())
        weighted_score += weights["mood"] * match
        active_weight += weights["mood"]

        if match:
            reasons.append("Mood matches")

    # 3. Valence similarity
    valence = user_prefs.get("valence")
    if valence is not None:
        similarity = max(0.0, 1 - abs(song["valence"] - valence))
        weighted_score += weights["valence"] * similarity
        active_weight += weights["valence"]
        reasons.append(f"Valence similarity: {similarity:.2f}")

    # 4. Energy similarity
    energy = user_prefs.get("energy")
    if energy is not None:
        similarity = max(0.0, 1 - abs(song["energy"] - energy))
        weighted_score += weights["energy"] * similarity
        active_weight += weights["energy"]
        reasons.append(f"Energy similarity: {similarity:.2f}")

    # 5. Tempo similarity
    tempo = user_prefs.get("tempo_bpm")
    if tempo is not None:
        similarity = max(
            0.0,
            1 - abs(song["tempo_bpm"] - tempo) / 160
        )
        weighted_score += weights["tempo_bpm"] * similarity
        active_weight += weights["tempo_bpm"]
        reasons.append(f"Tempo similarity: {similarity:.2f}")

    # 6. Acoustic preference
    acoustic = user_prefs.get("likes_acoustic")
    if acoustic is not None:
        similarity = (
            song["acousticness"]
            if acoustic
            else 1 - song["acousticness"]
        )

        weighted_score += weights["likes_acoustic"] * similarity
        active_weight += weights["likes_acoustic"]
        reasons.append(
            f"Acoustic preference match: {similarity:.2f}"
        )

    # 7. Normalize the score
    if active_weight == 0:
        raise ValueError("At least one music preference is required.")

    score = 100 * weighted_score / active_weight

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

    
    recommendations.sort(
        key=lambda item: (
            -item[1],
            -int(item[0].get("popularity", 0)),
            str(item[0]["id"])
        )
    )

    return recommendations[:k]
