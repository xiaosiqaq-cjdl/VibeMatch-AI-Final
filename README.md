# VibeMatch AI

**An Explainable Music Recommendation System Powered by a Local Large Language Model**

## 1. Project Overview

VibeMatch AI is a music recommendation application that translates natural-language requests into personalized song recommendations.

Instead of requiring users to manually select genres, moods, or audio features, VibeMatch allows users to describe the music they want in everyday language.

For example:

- "I want relaxing acoustic music for studying."
- "Give me something energetic for my workout."
- "Play some J-pop music."
- "I want upbeat music, but no jazz."

The system combines a locally running Qwen3 4B language model with deterministic preference validation and a custom feature-based recommendation algorithm.

### Original Project

VibeMatch AI extends the **Module 3 Music Recommendation Simulation** developed during AI110.

The original project demonstrated a basic content-based recommendation system that matched structured user preferences against a small collection of songs using audio characteristics such as genre, mood, energy, and tempo.

The final project transforms that prototype into an end-to-end AI application with natural-language understanding, a significantly expanded real-world music dataset, reliability safeguards, automated evaluation, and an interactive web interface.

### Key Features

- **Natural Language Understanding:** Uses Qwen3 4B through Ollama to extract structured music preferences.
- **Hybrid Preference Validation:** Combines LLM outputs with deterministic rules to improve reliability.
- **Explainable Recommendations:** Scores songs using genre, mood, energy, tempo, valence, and acoustic preferences.
- **Large Music Dataset:** Uses 89,583 unique Spotify track IDs across 113 genre labels after data cleaning.
- **Negative Preference Handling:** Supports excluding unwanted music genres.
- **Popularity-Based Ranking:** Uses song popularity as a secondary ranking criterion and as a fallback when only exclusions are specified.
- **Web Interface:** Provides an interactive Gradio application for entering music requests and viewing recommendations.
- **Automated Testing:** Includes unit and integration tests for preference extraction, recommendation logic, and reliability.

### Project Objective

The goal of VibeMatch AI is not to let an LLM directly choose songs.

Instead, the LLM is responsible for interpreting the user's language, while a separate, transparent recommendation algorithm calculates song rankings.

This separation makes the system easier to test, explain, and improve.

---

## 2. System Architecture

See [System Architecture](diagrams/architecture.md) for the complete Mermaid diagram and component descriptions.

VibeMatch AI uses a modular pipeline connecting language understanding, deterministic validation, retrieval, ranking, and user-facing recommendations.

The architecture consists of the following stages:

1. **User Input:** The user describes their music preferences through the Gradio interface.
2. **LLM Parsing:** Qwen3 4B interprets the request and returns structured preferences.
3. **Deterministic Validation:** Python rules recover explicit preferences, normalize genre names, and handle negation.
4. **Candidate Retrieval and Filtering:** The system retrieves songs from the cleaned Spotify dataset and removes excluded genres.
5. **Ranking:** A custom scoring algorithm ranks songs using the user's expressed preferences.
6. **Explanation:** The application provides song titles, artists, matching scores where applicable, and human-readable recommendation reasons.
7. **Evaluation:** Automated tests and experimental scripts verify individual components and system behavior.

The Mermaid architecture diagram is stored at:

`diagrams/architecture.md`

### Main Components

| File | Responsibility |
|---|---|
| `src/llm_client.py` | Connects to the local Ollama model |
| `src/preference_parser.py` | Extracts structured preferences using Qwen |
| `src/preference_validator.py` | Validates preferences, resolves genre aliases, and handles negation |
| `src/pipeline.py` | Coordinates preference processing and recommendation |
| `src/ai_recommender.py` | Connects structured preferences to song retrieval |
| `src/recommender.py` | Loads song data and calculates recommendation scores |
| `src/web_app.py` | Provides the Gradio web interface |
| `scripts/prepare_dataset.py` | Cleans the original Spotify dataset |
| `scripts/evaluate_thinking.py` | Compares LLM Thinking and Non-Thinking modes |
| `tests/` | Contains unit, reliability, and integration tests |

---

## 3. Music Dataset

### Data Source

The project uses a publicly available Spotify tracks dataset containing approximately 114,000 original records.

The dataset contains track metadata and audio-related features, including:

- Track ID
- Track name
- Artist
- Genre
- Popularity
- Energy
- Valence
- Tempo
- Danceability
- Acousticness

### Data Cleaning

The preprocessing pipeline performs the following operations:

1. Removes records with missing essential information.
2. Validates numerical audio features.
3. Removes duplicate track IDs.
4. Preserves Spotify genre labels.
5. Derives a simplified mood category from numerical audio characteristics.
6. Exports a cleaned dataset for recommendation.

### Cleaning Results

| Metric | Result |
|---|---:|
| Original records | 114,000 |
| Invalid records | 158 |
| Duplicate track IDs | 24,259 |
| Cleaned unique track IDs | 89,583 |
| Genre categories | 113 |

The resulting dataset is saved as:

`data/songs_full.csv`

The recommendation engine operates on this local dataset without requiring a paid music API.

**Dataset limitation:** Unique Spotify track IDs do not necessarily correspond to unique compositions. Multiple recordings, releases, and remastered versions may remain. Genre labels may also be broad or imperfect.

---

## 4. Installation and Usage

### Requirements

- Python and pip
- Ollama
- Qwen3 4B
- Dependencies listed in `requirements.txt`

The project was developed and tested primarily on Windows using VS Code and PowerShell.

### Step 1: Clone the Repository

```bash
git clone https://github.com/xiaosiqaq-cjdl/VibeMatch-AI-Final.git
cd VibeMatch-AI-Final
```

### Step 2: Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 4: Install Ollama and Download the Model

Install Ollama from its official website:

https://ollama.com/

Then download the required local model:

```powershell
ollama pull qwen3:4b
```

Verify that the model is available:

```powershell
ollama list
```

### Step 5: Prepare the Dataset

Download the source Spotify dataset and place its CSV file in the location expected by `scripts/prepare_dataset.py`.

Run:

```powershell
python scripts/prepare_dataset.py
```

The script generates `data/songs_full.csv`.

**Important:** The complete raw dataset may not be included in the GitHub repository. Users must obtain the original dataset separately, following its distribution terms.

### Step 6: Configure Web Authentication

For the current Windows PowerShell session:

```powershell
$env:VIBEMATCH_USER = "your_username"
$env:VIBEMATCH_PASSWORD = "your_password"
```

Do not commit credentials or API keys to GitHub.

### Step 7: Launch VibeMatch

```powershell
python -m src.web_app
```

Open the local Gradio URL displayed in the terminal.

The application requires the local Ollama service to be available.

### Step 8: Run Automated Tests

```powershell
python -m pytest -q
```

Tests cover recommendation behavior, preference validation, negative preferences, genre normalization, and pipeline integration.

Some tests or evaluation routines may require a running local LLM.

---

## 5. Recommendation Algorithm

VibeMatch uses a content-based recommendation algorithm rather than relying on an LLM to generate song selections.

### Preference Extraction

The LLM extracts six structured preference fields:

```python
{
    "genre": None,
    "mood": None,
    "energy": 0.8,
    "tempo_bpm": None,
    "valence": None,
    "likes_acoustic": None
}
```

Unspecified preferences remain `None`.

The system distinguishes a user's current condition from the desired musical experience.

For example:

- "I'm tired" does not necessarily imply a particular music preference.
- "I want music to keep me awake" implies a high-energy preference.

### Dynamic Weighted Scoring

Songs receive scores based on the relevant musical attributes requested by the user.

The system normalizes the weighted score over active preference dimensions so that unspecified preferences do not automatically influence the result.

This approach allows the algorithm to prioritize explicit user preferences without inventing additional requirements.

### Deterministic Ranking

Songs are ranked by:

1. Primary preference match score, descending.
2. Spotify popularity, descending, when match scores are equal.
3. Track ID, ascending, as a deterministic final tie-breaker.

This ensures reproducible ordering when multiple tracks receive identical scores.

### Negative Preferences

The system also supports requests such as:

```text
I want energetic music, but no jazz.
```

Explicitly excluded genres are removed from the candidate pool before ranking.

If the user specifies only an exclusion, such as "No jazz music, please," the system uses popularity-based ranking among the remaining songs rather than inventing positive preferences.

---

## 6. Sample Interactions and Reproducible Evidence

The following examples demonstrate observed application behavior. Recommendation results depend on the cleaned dataset and model configuration.

### Example 1: Genre-Based Recommendation

**Input:**

```text
I want some blues music.
```

**Extracted preference:**

```text
genre: blues
```

**Observed recommendations included:**

```text
1. Sweet Home Alabama — Lynyrd Skynyrd
   Match Score: 100.00/100

2. Cigarette Daydreams — Cage The Elephant
   Match Score: 100.00/100

3. For What It's Worth — Buffalo Springfield
   Match Score: 100.00/100

4. All Along the Watchtower — Jimi Hendrix
   Match Score: 100.00/100

5. Free Bird — Lynyrd Skynyrd
   Match Score: 100.00/100
```

These results illustrate both genre-based ranking and a limitation of dataset labels. A perfect genre-only score indicates a match against the stored genre label, not an objective judgment of musical quality.

### Example 2: Exclusion-Only Recommendation

**Input:**

```text
No jazz music, please.
```

**Observed recommendation behavior:**

```text
Recommendation Type: Popular pick
Why: Popular song outside excluded genres
```

Example returned tracks included:

```text
1. Unholy (feat. Kim Petras) — Sam Smith;Kim Petras
2. Quevedo: Bzrp Music Sessions, Vol. 52 — Bizarrap;Quevedo
3. I'm Good (Blue) — David Guetta;Bebe Rexha
4. La Bachata — Manuel Turizo
5. Tití Me Preguntó — Bad Bunny
```

No numerical preference score was displayed because the user had not supplied positive ranking preferences.

### Example 3: Natural-Language Preference Extraction

**Input:**

```text
I need something to get me through a tough workout.
```

**Observed parser results:**

```text
Thinking OFF:
energy = None

Thinking ON:
energy = 0.8
```

This case demonstrates how additional LLM reasoning can improve interpretation of indirect preferences.

---

## 7. Reliability and Evaluation

Reliability testing is an integrated component of VibeMatch AI.

The project uses automated unit tests, integration tests, deterministic validation, and experimental evaluation of LLM behavior.

### Automated Tests

The most recent completed test suite reported:

```text
39 passed in 65.86s
```

Testing includes:

- Recommendation ranking consistency.
- Missing and malformed dataset handling.
- Preference extraction and validation.
- Genre negation.
- Genre alias normalization.
- Overlapping genre matches.
- Excluded-genre filtering.
- Popularity fallback behavior.
- Pipeline integration.

### Qwen Thinking Mode Evaluation

Eight music preference prompts were evaluated under Thinking OFF and Thinking ON configurations.

Results from the recorded experiment:

| Configuration | Exact Match | Accuracy | Average Latency |
|---|---:|---:|---:|
| Thinking OFF | 3/8 | 37.5% | 2.71 seconds |
| Thinking ON | 5/8 | 62.5% | 13.41 seconds |
| Thinking OFF + Hybrid Validator | 4/8 | 50.0% | Approximately 2.71 seconds |
| Thinking ON + Hybrid Validator | 5/8 | 62.5% | Approximately 13.41 seconds |

The Hybrid Validator results use the same model calls as their corresponding raw configurations. The latency figures represent the combined evaluation calls, not separately benchmarked validator latency.

### Key Findings

- Thinking improved recognition of some indirect music preferences.
- Thinking introduced substantially longer response times.
- Deterministic validation recovered some explicitly stated preferences omitted by the LLM.
- Validation rules could also introduce errors when negation or genre aliases were mishandled.
- Strict JSON exact-match evaluation sometimes penalized semantically reasonable additional preferences.

### Reliability Improvements

During development, several issues were discovered through testing:

**Order invariance:** Equal-scoring songs initially changed order when dataset records were shuffled. A deterministic Track ID tie-breaker resolved the instability.

**Negation handling:** Requests such as "I don't want jazz" were initially interpreted as positive genre preferences. The validator was extended to detect negative constraints.

**Genre normalization:** Alternative spellings such as Jpop, J-pop, and J Pop initially caused inconsistent matching. Canonicalization and overlapping-match resolution improved recognition.

**Unsupported preferences:** The system distinguishes explicit preferences from missing information and avoids automatically assigning defaults to every absent field.

### Evaluation Limitations

The eight-prompt Thinking experiment is an exploratory comparison rather than a statistically representative benchmark.

Its results are sensitive to prompt selection, model configuration, and labeling decisions. Additional evaluation with independent prompts and human judgments would be necessary to estimate real-world reliability.

---

## 8. Design Decisions and Trade-Offs

### Why Use a Local LLM?

Using Ollama allows the project to run without requiring a paid cloud LLM API.

It also provides local control over model selection and inference behavior.

The primary trade-off is inference latency, especially when Thinking mode is enabled.

### Why Not Let the LLM Recommend Songs Directly?

Direct LLM-generated recommendations would make it harder to guarantee that suggested songs exist in the dataset or satisfy user constraints.

VibeMatch instead uses the LLM for interpretation and a separate algorithm for retrieval and ranking.

This provides more transparent behavior and enables deterministic testing.

### Why Combine LLMs with Rules?

LLMs can interpret flexible language but may miss explicit details or infer unsupported preferences.

Deterministic rules are useful for well-defined tasks such as genre normalization, BPM recognition, and simple negation handling.

The hybrid approach combines the strengths of both methods while acknowledging their limitations.

### Why Not Use RAG?

The current architecture uses structured retrieval and ranking over a local music dataset rather than a full retrieval-augmented generation pipeline.

RAG could be a future extension for retrieving richer song descriptions and grounding natural-language explanations.

However, adding RAG was not necessary for the core project objective of explainable feature-based music recommendation.

---

## 9. Limitations and Future Work

Current limitations include:

- Inconsistent interpretation of some indirect music preferences.
- Increased latency when Thinking mode is enabled.
- Imperfect or overly broad genre labels in the source dataset.
- Potential duplicate compositions across different Spotify track IDs.
- Limited support for multiple simultaneously requested positive genres.
- Limited understanding of complex negation and conversational corrections.
- Dependence on a locally running Ollama service.

Future improvements could include multi-genre support, semantic retrieval, more robust preference extraction, diversification of recommended artists, and larger-scale human evaluation.

---

## 10. Reflection

VibeMatch AI demonstrated that building an AI application involves more than connecting a language model to a user interface.

One of the most important lessons was that an LLM can be useful for interpreting flexible language while still requiring deterministic validation and independent testing.

The project also showed the importance of evaluating errors rather than focusing only on aggregate accuracy. Several failures were introduced by validation rules intended to improve reliability, illustrating that safeguards themselves must be tested.

Finally, the distinction between language understanding and recommendation ranking helped produce a system that is more transparent and easier to maintain than an approach that delegates every decision to an LLM.

---

## 11. Repository and Portfolio

**GitHub Repository:**

https://github.com/xiaosiqaq-cjdl/VibeMatch-AI-Final

VibeMatch AI represents an applied AI engineering project combining natural-language processing, structured data processing, recommendation algorithms, and reliability evaluation.

It demonstrates how model-driven components and deterministic software can be integrated into a practical, explainable system.