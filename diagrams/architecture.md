
# VibeMatch AI — System Architecture

The following diagram illustrates the end-to-end recommendation pipeline, from natural-language input to explainable music recommendations.

```mermaid
flowchart TD
    A["User Music Request"] --> B["Gradio Web Interface"]
    B --> C["Pipeline Orchestration"]

    C --> D["Qwen3 4B via Ollama"]
    D --> E["Structured Preference Extraction"]

    C --> F["Deterministic Genre Detection"]
    E --> G["Hybrid Preference Validator"]
    F --> G

    G --> H["Validated Positive Preferences"]
    F --> I["Excluded Genres"]

    J["Spotify Dataset: 89,583 Tracks"] --> K["Candidate Filtering"]
    I --> K

    H --> L{"Positive Preferences Available?"}
    K --> L

    L -->|Yes| M["Feature-Based Scoring"]
    L -->|Exclusions Only| N["Popularity Fallback"]
    L -->|No Preferences| O["Request Clarification"]

    M --> P["Deterministic Ranking"]
    N --> Q["Top 5 Popular Picks"]
    P --> R["Top 5 Matches + Explanations"]

    Q --> S["Gradio Results"]
    R --> S
    O --> S

    T["Pytest Unit and Integration Tests"] -.-> G
    T -.-> K
    T -.-> M

    U["LLM Thinking A/B Evaluation"] -.-> D
    V["Human Review and Feedback"] -.-> S
```

## Component Responsibilities

| Component | Purpose |
|---|---|
| Gradio Web Interface | Collects user requests and displays results |
| Qwen3 4B / Ollama | Interprets natural-language music preferences |
| Hybrid Preference Validator | Normalizes explicit preferences and corrects certain LLM errors |
| Genre Detection | Recognizes standard names, spelling variants, and exclusions |
| Candidate Filtering | Removes tracks matching excluded genres |
| Feature-Based Scoring | Calculates preference-matching scores |
| Deterministic Ranking | Sorts by match score, popularity, and track ID |
| Popularity Fallback | Handles exclusion-only requests without inventing preference scores |
| Reliability Tests | Verify individual functions and pipeline behavior |
| Human Review | Evaluates recommendation relevance and known limitations |
