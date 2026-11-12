
from src.recommender import recommend_songs


def retrieve_songs(user_prefs, songs, k=5):
    """
    Retrieve and rank songs based on user preferences.
    Returns structured evidence for the LLM.
    """
    results = recommend_songs(user_prefs, songs, k=k)

    retrieved = []

    for song, score, reasons in results:
        retrieved.append({
            "id": str(song["id"]),
            "title": song["title"],
            "artist": song["artist"],
            "genre": song["genre"],
            "mood": song["mood"],
            "energy": song["energy"],
            "valence": song["valence"],
            "tempo_bpm": song["tempo_bpm"],
            "score": score,
            "reasons": reasons
        })

    return retrieved


def build_context(retrieved_songs):
    """
    Convert retrieved songs into grounded LLM context.
    """
    if not retrieved_songs:
        return "No matching songs were found."

    lines = []

    for index, song in enumerate(retrieved_songs, start=1):
        lines.append(
            f"Song {index}:\n"
            f"ID: {song['id']}\n"
            f"Title: {song['title']}\n"
            f"Artist: {song['artist']}\n"
            f"Genre: {song['genre']}\n"
            f"Mood: {song['mood']}\n"
            f"Energy: {song['energy']}\n"
            f"Valence: {song['valence']}\n"
            f"Tempo: {song['tempo_bpm']} BPM\n"
            f"Match Score: {song['score']}\n"
            f"Reasons: {song['reasons']}\n"
        )

    return "\n".join(lines)
