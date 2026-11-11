
import csv
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to the original Spotify dataset
INPUT_FILE = BASE_DIR / "data" / "raw" / "spotify-tracks-dataset-detailed.csv"


import random
from collections import defaultdict

OUTPUT_FILE = BASE_DIR / "data" / "songs_real.csv"

GENRES = [
    "pop", "rock", "jazz", "classical", "electronic",
    "hip-hop", "r-n-b", "country", "metal", "ambient"
]

SONGS_PER_GENRE = 50
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
    """Clean and sample real Spotify song data."""
    genre_groups = defaultdict(list)
    seen_ids = set()

    with INPUT_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            genre = row["track_genre"].lower().strip()
            track_id = row["track_id"]

            if genre not in GENRES:
                continue

            if not track_id or track_id in seen_ids:
                continue

            try:
                energy = float(row["energy"])
                valence = float(row["valence"])
                danceability = float(row["danceability"])
                acousticness = float(row["acousticness"])
                tempo = float(row["tempo"])

                if not all(
                    0 <= value <= 1
                    for value in [
                        energy, valence, danceability, acousticness
                    ]
                ):
                    continue

                if tempo <= 0:
                    continue

                song = {
                    "id": track_id,
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "genre": genre,
                    "mood": infer_mood(energy, valence),
                    "energy": energy,
                    "tempo_bpm": tempo,
                    "valence": valence,
                    "danceability": danceability,
                    "acousticness": acousticness,
                }

                if not song["title"] or not song["artist"]:
                    continue

                genre_groups[genre].append(song)
                seen_ids.add(track_id)

            except (ValueError, TypeError, KeyError):
                continue

    random.seed(RANDOM_SEED)
    selected_songs = []

    for genre in GENRES:
        songs = genre_groups[genre]
        sample_size = min(SONGS_PER_GENRE, len(songs))

        selected_songs.extend(
            random.sample(songs, sample_size)
        )

        print(f"{genre}: {sample_size} songs selected")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "id", "title", "artist", "genre", "mood",
        "energy", "tempo_bpm", "valence",
        "danceability", "acousticness"
    ]

    with OUTPUT_FILE.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(selected_songs)

    print(f"\nTotal songs: {len(selected_songs)}")
    print(f"Saved to: {OUTPUT_FILE}")


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


