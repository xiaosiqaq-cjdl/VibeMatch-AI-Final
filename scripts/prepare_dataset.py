
import csv
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to the original Spotify dataset
INPUT_FILE = BASE_DIR / "data" / "raw" / "spotify-tracks-dataset-detailed.csv"


import random
from collections import defaultdict

OUTPUT_FILE = BASE_DIR / "data" / "songs_real.csv"
# Use all availavle genres
GENRES = None

SONGS_PER_GENRE = None
RANDOM_SEED = 42


def infer_mood(energy, valence):
    """Estimate mood from audio features."""
    if energy >= 0.5 and valence >= 0.5:
        return "happy"
    elif energy < 0.5 and valence >= 0.5:
        return "calm"
    elif energy >= 0.5 and valence < 0.5:
        return "intense"
    else:
        return "sad"



def prepare_dataset():
    """Clean the full Spotify dataset without sampling."""
    cleaned = {}
    total_rows = 0
    invalid_rows = 0
    duplicate_rows = 0

    with INPUT_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            total_rows += 1
            track_id = (row.get("track_id") or "").strip()

            if not track_id:
                invalid_rows += 1
                continue

            if track_id in cleaned:
                duplicate_rows += 1
                continue

            try:
                energy = float(row["energy"])
                valence = float(row["valence"])
                danceability = float(row["danceability"])
                acousticness = float(row["acousticness"])
                tempo = float(row["tempo"])
                popularity = int(row["popularity"])

                if not 0 <= popularity <= 100:
                    invalid_rows += 1
                    continue

                if not all(
                    0 <= value <= 1
                    for value in (
                        energy, valence,
                        danceability, acousticness
                    )
                ):
                    invalid_rows += 1
                    continue

                if not 0 < tempo <= 300:
                    invalid_rows += 1
                    continue

                title = (row.get("track_name") or "").strip()
                artist = (row.get("artists") or "").strip()
                genre = (row.get("track_genre") or "").strip().lower()

                if not title or not artist or not genre:
                    invalid_rows += 1
                    continue

                cleaned[track_id] = {
                    "id": track_id,
                    "title": title,
                    "artist": artist,
                    "genre": genre,
                    "popularity": popularity,
                    "mood": infer_mood(energy, valence),
                    "energy": energy,
                    "tempo_bpm": tempo,
                    "valence": valence,
                    "danceability": danceability,
                    "acousticness": acousticness,
                }

            except (ValueError, TypeError, KeyError):
                invalid_rows += 1
                continue

    output_file = BASE_DIR / "data" / "songs_full.csv"

    fieldnames = [
        "id", "title", "artist", "genre", "mood",
        "energy", "tempo_bpm", "valence",
        "danceability", "acousticness", "popularity"
    ]

    with output_file.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned.values())

    genres = {song["genre"] for song in cleaned.values()}

    print(f"Original rows: {total_rows}")
    print(f"Invalid rows: {invalid_rows}")
    print(f"Duplicate track IDs: {duplicate_rows}")
    print(f"Cleaned unique songs: {len(cleaned)}")
    print(f"Genres: {len(genres)}")
    print(f"Saved to: {output_file}")

if __name__ == "__main__":
    prepare_dataset()


def inspect_dataset():
    """Inspect the structure of the raw Spotify dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Spotify dataset not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        print("Dataset columns:")
        print(reader.fieldnames)

        print("\nFirst 3 songs:")
        for index, row in enumerate(reader):
            if index >= 3:
                break

            print(f"\nSong {index + 1}")
            print(row)


