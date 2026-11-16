# VibeMatch AI — Model Card

## 1. System Overview

**System Name:** VibeMatch AI  
**Application:** Explainable Music Recommendation  
**Language Model:** Qwen3 4B (via Ollama)  
**Primary AI Feature:** Natural-Language Preference Extraction  
**Reliability Approach:** Hybrid LLM and Deterministic Validation

VibeMatch AI uses a locally hosted language model to interpret users' music preferences and convert them into structured attributes. A separate content-based recommendation algorithm retrieves and ranks songs from a cleaned Spotify dataset.

The language model does not directly generate the final song recommendations.

## 2. Intended Use

VibeMatch AI is intended for users who want music recommendations using natural-language descriptions instead of manually selecting numerical audio features.

Supported requests include genre preferences, mood descriptions, energy levels, tempo preferences, and explicit genre exclusions.

The system is designed as an educational AI engineering project rather than a production-grade music recommendation service.

## 3. Limitations and Potential Biases

### Language Understanding

Qwen3 4B can interpret many direct and indirect music requests, but its performance is not always consistent.

The model may omit preferences, infer unnecessary attributes, or misunderstand complex sentences.

For example, requests involving indirect emotional goals sometimes failed under Non-Thinking mode.

### Dataset Bias

The cleaned Spotify dataset contains 89,583 unique track IDs across 113 genre labels.

However, Spotify genre labels may not accurately represent the musical characteristics of every recording.

Popularity-based ranking can also favor already popular artists and reduce the visibility of less-known music.

### Limited Personalization

VibeMatch primarily uses preferences expressed in the current request. It does not learn long-term musical tastes from listening histories.

The system also has limited support for multiple simultaneous positive genre preferences.

### Evaluation Limitations

Our LLM evaluation used a small set of manually defined test cases.

Consequently, the observed accuracy should not be interpreted as a general measure of model performance across all music requests.

## 4. Potential Misuse and Mitigation

VibeMatch is a relatively low-risk recommendation application, but several risks remain.

**Misleading Recommendations:** Users may interpret a high matching score as proof of musical quality. To address this, the system provides explanations based on the attributes actually used in ranking.

**Unreliable Genre Classification:** Incorrect dataset labels may produce recommendations that do not match users' expectations. This limitation is documented rather than concealed.

**Unintended Preference Inference:** The language model may assume preferences that users never expressed. Deterministic validation, null-valued unspecified fields, and clarification behavior help limit this issue.

**Privacy:** The language model runs locally through Ollama, avoiding the need to transmit preference requests to a paid external LLM API. However, publicly shared Gradio interfaces still require appropriate access controls and network security.

The system does not claim to provide psychological or medical treatment through music recommendations.

## 5. Reliability Testing and Unexpected Findings

Reliability was evaluated using automated tests, LLM experiments, and manual review.

### Automated Testing

The latest completed full test suite reported:

**39 tests passed.**

Tests covered recommendation ranking, data validation, genre normalization, negation handling, exclusion filtering, and pipeline integration.

### Thinking Mode Comparison

| Configuration | Exact Match Accuracy | Average Latency |
|---|---:|---:|
| Thinking OFF | 37.5% (3/8) | 2.71 s |
| Thinking ON | 62.5% (5/8) | 13.41 s |
| Thinking OFF + Validator | 50.0% (4/8) | Approximately 2.71 s |
| Thinking ON + Validator | 62.5% (5/8) | Approximately 13.41 s |

These figures describe one exploratory eight-request evaluation, not a statistically representative benchmark.

### What Surprised Me

One surprising finding was that enabling Thinking improved the interpretation of indirect music preferences but increased inference time considerably.

Another unexpected finding was that deterministic validation rules could introduce errors of their own.

For instance, the phrase "I want music without acoustic instruments" initially caused the validator to incorrectly add `genre=acoustic`, even though the LLM had correctly identified the negative acoustic preference.

This demonstrated that reliability mechanisms themselves require independent testing.

We also discovered that genre aliases and overlapping string matches could cause incorrect results. For example, the system initially interpreted `J-pop` as `pop` because the shorter genre name overlapped with the longer one.

These failures motivated additional regression tests and improved normalization logic.

## 6. Collaboration with AI

AI assistance was used during implementation, debugging, testing, and documentation.

However, AI-generated suggestions were evaluated rather than accepted automatically.

### AI Suggestion Accepted

One useful suggestion was to develop automated reliability tests and compare the language model's Thinking and Non-Thinking configurations.

I adopted this approach because it made system behavior measurable rather than relying only on a few successful demonstrations.

The resulting experiments identified important trade-offs between semantic interpretation accuracy and inference latency.

### AI Suggestion Revised

During development, we considered using an LLM more directly for music recommendations.

I chose to retain a separate deterministic recommendation algorithm instead of making the language model responsible for selecting songs.

This decision preserved transparent scoring, reproducible ranking, and clearer separation between understanding user intent and evaluating songs.

I also revised several AI-suggested validation rules after tests revealed that they could introduce false-positive genre matches.

### Human Oversight

I reviewed test failures, evaluated actual recommendation outputs, questioned architectural decisions, and used regression tests to verify changes.

This process reinforced the importance of treating AI-generated code and explanations as proposals requiring validation.

## 7. Responsible AI Reflection

The most important lesson from this project was that producing a working AI application is not the same as producing a reliable one.

A system may appear successful during demonstrations while still failing on small changes in wording, punctuation, negation, or musical context.

Combining a language model with conventional software improved transparency, but the additional validation layer also created new sources of error.

I learned to measure system behavior, preserve reproducible evidence, and examine individual failures before making architectural changes.

In future work, I would prioritize larger human-labeled evaluation datasets, better genre metadata, more expressive preference representations, and systematic testing of semantic ambiguity.

VibeMatch AI demonstrates how language models and deterministic algorithms can complement each other while retaining clear boundaries and acknowledging uncertainty.