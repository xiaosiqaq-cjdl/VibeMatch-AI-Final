# 🎧 Model Card: VibeMatch Music Recommender

## 1. Model Name

**VibeMatch Music Recommender**

---

## 2. Intended Use  

VibeMatch is a classroom simulation that ranks songs from a small catalog according to a supplied user preference profile. It assumes the profile's genre, mood, energy, tempo, valence, and acoustic preference are meaningful targets for the user. The current command-line app uses one example profile defined in `src/main.py`; it is not an interactive or production recommendation service.

---

## 3. How the Model Works  

The recommender compares each song with the user's profile. It rewards exact genre and mood matches and gives similarity scores for valence, energy, and tempo. Mood and valence are grouped as emotional fit; energy and tempo are grouped as activity fit, so related signals do not each receive a full independent weight. Acousticness is scored according to whether the user prefers acoustic or less-acoustic music. These parts are combined into a 0-to-100 score, and songs are sorted from highest to lowest. The system also returns brief reasons for each recommendation.

The implementation adds CSV loading with numeric type conversion, the weighted scoring rule, score explanations, and ranked top-k results. The current app uses a fixed example profile; it does not yet ask for a user's current mood or accept arbitrary user-defined soft preferences beyond the acoustic preference.

---

## 4. Data  

The model uses the 10 rows in `data/songs.csv`. The catalog includes pop, lofi, rock, ambient, jazz, synthwave, and indie pop; moods include happy, chill, intense, relaxed, moody, and focused. Each row has title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. No songs were added or removed. The sample does not represent the breadth of music or listener preferences, and danceability is currently loaded but not used in scoring.

---

## 5. Strengths  

The system behaves predictably for profiles that closely match attributes represented in the catalog. In the tested profiles, pop/happy preferences ranked Sunrise City first, chill/acoustic lofi ranked Library Rain first, and intense rock ranked Storm Runner first. Its separate score components also make it possible to explain why one song outranks another.

---

## 6. Limitations and Bias 

The 10-song catalog is small and imbalanced: some genres and moods have only one example, so users with less represented tastes have fewer good matches. Exact genre and mood checks may miss related labels (for example, `pop` and `indie pop`). The model does not use listening history, lyrics, language, artist familiarity, or context, and danceability does not currently affect results. Hand-selected weights and tempo scaling may favor some profiles or songs; the system also does not enforce variety, so similar tracks can appear together. Scores are relative matches to the supplied profile, not probabilities that a person will enjoy a song.

---

## 7. Evaluation  

I tested the recommender with three different user profiles and checked whether the highest-ranked songs matched each profile's genre, mood, energy, tempo, valence, and acoustic preferences:

- **High-Energy Pop:** Sunrise City ranked first (96.15), followed by Gym Hero (77.16) and Rooftop Lights (58.41).
- **Chill Lofi:** Library Rain ranked first (97.44), followed by Midnight Coding (96.39) and Focus Flow (76.62).
- **Deep Intense Rock:** Storm Runner ranked first (98.55), followed by Gym Hero (60.70) and Night Drive Loop (37.21).

The top recommendations matched the intended profiles: upbeat pop ranked highly for the high-energy pop listener, calm and acoustic lofi ranked highly for the chill listener, and intense rock ranked first for the rock listener. The two leading Chill Lofi songs scored very closely, showing how several similar tracks can both be strong matches.

I also added automated tests for these three profiles. The tests check that each expected song ranks first, that three results are returned, and that the results are ordered from highest to lowest score. Running `python -m pytest tests\test_recommender.py -q` completed with **5 passed**. This evaluation is limited by the small catalog of 10 songs and checks only a few hand-built profiles; it does not measure real user satisfaction.

I also tried a weight-shift experiment, halving the genre weight and doubling the effective energy weight while keeping the other feature weights fixed. The top result stayed the same for all four evaluated profiles, but some lower-ranked songs moved substantially, especially for the sample pop profile and the deep rock profile. The comparison is documented in the README; it shows ranking sensitivity, not that the adjusted weights are objectively better.

---

## 8. Future Work

- Ask users for their current mood and desired listening experience, then map that choice to explicit target mood, valence, energy, and tempo values.
- Expand and balance the catalog so more genres and moods have multiple examples.
- Explore danceability and user-specified soft preferences, while avoiding double-counting features already in the core score.
- Test alternative weights across more diverse profiles and record how rankings change.
- Add a diversity step so the top recommendations are not all very similar.

---

## 9. Personal Reflection  

Building this project showed me how song features and scoring weights turn a user's preferences into a ranked list. I found that grouping related features such as energy and tempo makes the logic easier to explain, while the weight-shift experiment showed that changing one preference can noticeably reorder recommendations. Testing several profiles helped me see why a recommender should be evaluated with different users rather than only one example.

The small catalog also made the limitations clear: a scoring formula cannot recommend music that is missing from its data, and a high score is not proof that someone will like a song. I would want to test with more songs and more listener profiles before drawing stronger conclusions.
