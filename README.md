# 🎵 Music Recommender Simulation

## Project Summary

This is a small content-based music recommender. It loads a 10-song catalog from a CSV file, compares each song's attributes with a sample user's preferences, calculates an explainable match score, and prints the five highest-scoring songs. The project also evaluates the ranking with several sample profiles and a weight-shift experiment.

---

## How The System Works

Each song is described by its genre, mood, energy, tempo, valence, danceability, and acousticness. The current example user profile specifies a favorite genre and mood, target energy, tempo and valence, and whether they prefer acoustic songs.

Current mood gives context; the listening experience they want determines the recommendation targets. For example, a user who feels down but wants to feel energized can be matched with upbeat, higher-energy songs. If they feel down and want to relax, the system can target calmer songs with a moderate or positive valence instead of matching sadness directly.

The recommender compares each song with those targets and calculates a core score. Related features are grouped to reduce double-counting:

- **Genre (`G`):** 1 if the song's genre matches a favorite genre, otherwise 0.
- **Emotion (`E`):** mood match is the main signal, with valence similarity as support.
- **Activity (`A`):** energy similarity is the main signal, with tempo similarity as support.
- **Acoustic preference (`C`):** how well the song's acousticness matches the user's preference.

The core score weights genre at 35%, emotion at 30%, activity at 25%, and acoustic preference at 10%. Within emotion, mood contributes 70% and valence 30%; within activity, energy contributes 70% and tempo 30%:

```text
core_score = 100 × (0.35 × G + 0.30 × E + 0.25 × A + 0.10 × C)

E = 0.70 × M + 0.30 × V
A = 0.70 × En + 0.30 × T
```

`M` is 1 when the song mood matches the target mood, otherwise 0. The numeric similarities range from 0 (least similar) to 1 (exact match):

```text
V  = 1 - abs(song_valence - target_valence)
En = 1 - abs(song_energy - target_energy)
T  = max(0, 1 - abs(song_tempo_bpm - target_tempo_bpm) / 160)

C = song_acousticness       if the user prefers acoustic songs
C = 1 - song_acousticness  otherwise
```

The tempo divisor is an initial scaling choice that can be adjusted after testing. The current command-line version uses a sample preference dictionary in `src/main.py`; it does not interactively ask about the user's current mood or desired listening experience. Those could be added later to choose the target mood, valence, energy, and tempo. The implemented score uses the genre, mood, valence, energy, tempo, and acousticness preferences described above. `danceability` is loaded from the CSV but is not currently part of the score. Songs are ranked by score and the highest-scoring ones are recommended. This is a simple content-based approach: it uses song attributes and stated preferences rather than listening history.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python -m src.main
   ```

### Running Tests

Run the tests with:

```bash
python -m pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

The sample profile in `src/main.py` is pop, happy, energy 0.8, tempo 125 BPM, valence 0.9, and no acoustic preference. Running `python -m src.main` produces:

```
Top recommendations:

Sunrise City - Score: 96.98
Because: Genre matches; Mood matches; Valence similarity: 0.94; Energy similarity: 0.98; Tempo similarity: 0.96; Acoustic preference match: 0.82

Gym Hero - Score: 74.73
Because: Genre matches; Valence similarity: 0.87; Energy similarity: 0.87; Tempo similarity: 0.96; Acoustic preference match: 0.95

Rooftop Lights - Score: 59.94
Because: Mood matches; Valence similarity: 0.91; Energy similarity: 0.96; Tempo similarity: 0.99; Acoustic preference match: 0.65

Night Drive Loop - Score: 36.53
Because: Valence similarity: 0.59; Energy similarity: 0.95; Tempo similarity: 0.91; Acoustic preference match: 0.78

Storm Runner - Score: 36.03
Because: Valence similarity: 0.58; Energy similarity: 0.89; Tempo similarity: 0.83; Acoustic preference match: 0.90
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

I compared the original scoring weights with an experimental weight shift. In the original formula, genre has 35% of the total weight and energy's effective weight is 25% × 70% = 17.5%. For the experiment, I halved genre to 17.5% and doubled energy to 35%, keeping mood (21%), valence (9%), tempo (7.5%), and acousticness (10%) unchanged. The weights still sum to 100%. I calculated the experimental scores separately without changing the recommender implementation.

| Profile | Original top 3 | After weight shift |
|---|---|---|
| Sample Pop/Happy | Sunrise City (96.98), Gym Hero (74.73), Rooftop Lights (59.94) | Sunrise City (96.63), Rooftop Lights (76.74), Gym Hero (72.45) |
| High-Energy Pop | Sunrise City (96.15), Gym Hero (77.16), Rooftop Lights (58.41) | Sunrise City (94.75), Gym Hero (76.64), Rooftop Lights (73.46) |
| Chill Lofi | Library Rain (97.44), Midnight Coding (96.39), Focus Flow (76.62) | Library Rain (96.57), Midnight Coding (96.04), Focus Flow (76.62) |
| Deep Intense Rock | Storm Runner (98.55), Gym Hero (60.70), Night Drive Loop (37.21) | Storm Runner (98.38), Gym Hero (77.68), Sunrise City (52.34) |

The high-energy profile still ranked energetic songs near the top, but the lower genre weight helped Rooftop Lights rise above Gym Hero for the sample profile. The Chill Lofi ranking did not change, while the Deep Intense Rock profile gave a much larger boost to other high-energy songs. This shows that changing weights can affect the balance between a user's genre match and numeric energy similarity; the experiment is illustrative, not proof of better recommendations.

---

## Limitations and Risks

The catalog contains only 10 songs, so genres and moods are unevenly represented and recommendations have little variety. Mood and genre matches are exact text comparisons, the weights and tempo scaling value are hand-chosen, and the system does not use listening history, lyrics, language, or context. Although danceability is present in the data, it does not affect the score. A small or imbalanced catalog can cause some songs and genres to be recommended more often than others.

---

## Reflection

The project showed me that a recommender's output depends on both the features available and the weights chosen for them. A song can rank highly for different reasons, so returning an explanation helps make the score easier to inspect. Comparing three different preference profiles also showed that the same catalog can produce different rankings when user targets change.

The results are only as representative as the small catalog and hand-built profiles allow. If a genre is missing or underrepresented, users who like it may receive poor or repetitive recommendations. The weight experiment also showed that adjusting one feature can change rankings for users whose preferences differ, so weights should be tested across diverse profiles rather than chosen from one example. See the [model card](model_card.md) for details about intended use, evaluation, limitations, and future work.
