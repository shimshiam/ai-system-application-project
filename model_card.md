# 🎧 Model Card: Vibe Synthesizer

## 1. Model Name

**Vibe Synthesizer (with Spotify Integration)**

---

## 2. Intended Use

This recommender system is designed to generate highly personalized study playlists by combining traditional content-based song filtering with Retrieval-Augmented Generation (RAG) and live Spotify account integration. It uses the listener's task type (e.g., coding, reading) and focus goals alongside musical preferences (genre, mood, acousticness, explicitness) to curate a well-paced study block.

---

## 3. How the Model Works

The pipeline follows a multi-stage approach:
1. **Data Ingestion:** Loads a default catalog of songs or seamlessly ingests up to 50 of the user's top/recently played tracks directly from the Spotify API.
2. **Metadata Augmentation:** Automatically infers unlisted track features. The system is fortified against Spotify API restrictions (e.g., `403 Forbidden` limits on catalog endpoints) by gracefully falling back to LLM-inferred or title-based genre/mood assignments, recalculating necessary fields like track language based on these updates.
3. **Retrieval & Filtering:** Candidate tracks are filtered according to the user's UI rules (e.g., excluding explicit tracks or filtering out vocal tracks). A smart fallback system guarantees a playlist by relaxing rules if strict constraints inadvertently filter out all available tracks.
4. **Scoring:** Retained tracks are scored against retrieved study guidance rules (incorporating pacing and target energy levels).
5. **Generative Planning:** The final tracklist, complete with justifications and a holistic study strategy, is synthesized via an LLM.

---

## 4. Data

The system operates on two data sources:
- **Local Catalog:** A baseline collection of curated tracks (`data/songs.csv`) and task-specific rules (`data/study_rules.csv`).
- **Live Spotify Imports:** The user's actual Spotify listening history (Top and Recent tracks). Features such as popularity, acousticness, energy, and genre are dynamically aggregated and normalized, effectively tailoring the data pool to individual listening habits.

---

## 5. Strengths

- **Resilience:** The application features robust error handling when interacting with the restrictive Spotify Web API. If catalog data like artist genres are inaccessible, or if strict user constraints filter out too many songs, the system gracefully adapts its logic and filters to ensure a curated playlist is always returned.
- **Dynamic Pacing:** Beyond just matching songs to genres, it utilizes explicit study rules to dictate energy flow, ensuring the start and end of a playlist support the intended focus task.
- **Hybrid AI Pipeline:** Leverages an LLM not just to generate descriptions, but to actively classify unknown Spotify tracks and structure the final output.

---

## 6. Limitations and Bias

- **Catalog Dependency:** For users who import a small or highly homogeneous Spotify history (e.g., entirely high-energy rap), the recommender's fallback logic may be forced to ignore the user's "No Lyrics" constraints in order to populate the list. 
- **LLM Hallucination Risks:** While mitigated by strict JSON schemas and validation loops, the generative step occasionally needs to fall back to a deterministic planner if the LLM struggles to parse the retrieved context.

---

## 7. Evaluation

The system was evaluated against rigid edge cases, such as users requesting strictly instrumental study tracks from a Spotify library entirely composed of vocal pop music. The smart fallback mechanisms successfully prevented empty retrievals by loosening constraints. API testing confirmed the application no longer crashes when facing newly-enforced `403 Forbidden` catalog restrictions in Development Mode apps.

---

## 8. Future Work

- **Advanced Token Management:** Implement robust token refresh flows and API backoffs for the Spotify integration to support long-lived sessions.
- **Enhanced Feature Extraction:** Support fetching and caching audio features from more lenient secondary APIs or local audio analysis when Spotify restricts access.
- **Expanded Rule Engine:** Allow users to upload their own study notes or pacing guidelines as additional RAG context.
