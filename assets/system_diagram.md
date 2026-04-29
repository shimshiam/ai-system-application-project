# Study DJ — System Architecture Diagram

```mermaid
flowchart TB
    subgraph INPUT["🎤 Input Sources"]
        direction LR
        DEMO["Demo Catalog<br/><i>data/songs.csv</i>"]
        SPOTIFY["Spotify API<br/><i>PKCE Auth Flow</i>"]
        RULES["Study Rules<br/><i>data/study_rules.csv</i>"]
    end

    subgraph SPOTIFY_PIPELINE["🔌 Spotify Ingestion Pipeline <i>(spotify_client.py)</i>"]
        direction TB
        FETCH["Fetch Artist Genres<br/><i>_fetch_artist_genres()</i>"]
        NORM["Normalize Tracks<br/><i>normalize_spotify_track()</i>"]
        CLASSIFY{"Classify Genres<br/><i>classify_spotify_tracks()</i>"}
        LLM_CLASS["OpenAI Classification<br/><i>_classify_with_openai()</i>"]
        FALLBACK_CLASS["Heuristic Fallback<br/><i>_fallback_classify()</i><br/>Genre/Mood/Energy from<br/>artist tags, title, album"]
        FETCH --> NORM --> CLASSIFY
        CLASSIFY -->|"API key available"| LLM_CLASS
        CLASSIFY -->|"No API key / error"| FALLBACK_CLASS
    end

    subgraph UI["🖥️ Streamlit Dashboard <i>(streamlit_app.py)</i>"]
        direction TB
        MOD1["Module 1: Source Input<br/><i>Catalog selection, Spotify import</i>"]
        MOD2["Module 2: Context Modulators<br/><i>Task type, focus goal, session length</i>"]
        MOD3["Module 3: Vibe Synthesis Engine<br/><i>Synthesis mode, genre, mood, energy</i>"]
        MOD4["Module 4: Signal Filters<br/><i>Acoustic, lyrics, explicit, LLM toggle</i>"]
    end

    subgraph RAG["⚙️ RAG Pipeline <i>(study_dj.py)</i>"]
        direction TB
        RETRIEVE_RULES["Retrieve Study Rules<br/><i>retrieve_study_rules()</i><br/>Score rules by task + focus match"]
        RETRIEVE_SONGS["Retrieve Candidate Songs<br/><i>retrieve_candidate_songs()</i><br/>Filter → Score → Rank top-k"]
        CONTEXT["Build Context Package<br/><i>retrieve_context()</i>"]
        RETRIEVE_RULES --> CONTEXT
        RETRIEVE_SONGS --> CONTEXT
    end

    subgraph SCORING["📊 Recommender Engine <i>(recommender.py)</i>"]
        direction TB
        SCORER{"Scorer Strategy<br/><i>Selected by synthesis mode</i>"}
        BAL["BalancedScorer"]
        GENRE["GenreFirstScorer"]
        MOOD["MoodFirstScorer"]
        ENERGY["EnergyFocusedScorer"]
        RESON["ResonanceScorer"]
        SCORER --> BAL
        SCORER --> GENRE
        SCORER --> MOOD
        SCORER --> ENERGY
        SCORER --> RESON
    end

    subgraph GENERATION["🤖 Playlist Generation <i>(study_dj.py)</i>"]
        direction TB
        GEN{"generate_playlist_plan()"}
        LLM_GEN["AI Generator<br/><i>OpenAI / Mistral / Groq / Gemini</i><br/><i>Structured JSON output</i><br/><i>Grounded on retrieved context</i>"]
        FALLBACK_GEN["Deterministic Fallback<br/><i>generate_fallback_playlist_plan()</i><br/><i>Rank-ordered with pacing notes</i>"]
        VALIDATE["Validate & Ground<br/><i>_ensure_plan_uses_retrieved_songs()</i><br/>Reject hallucinated tracks"]
        GEN -->|"API key available"| LLM_GEN --> VALIDATE
        GEN -->|"No API key / error"| FALLBACK_GEN
    end

    subgraph OUTPUT["📋 Output"]
        direction LR
        PLAYLIST["Ordered Playlist<br/><i>Tracks, reasons, pacing</i>"]
        STRATEGY["Study Strategy<br/><i>Focus guidance</i>"]
        METRICS["Retrieval Metrics<br/><i>Songs retrieved, source, AI mode</i>"]
    end

    subgraph TESTING["🧪 Testing & Human Oversight"]
        direction TB
        T1["test_recommender.py<br/><i>Score sorting, explanations</i>"]
        T2["test_spotify_client.py<br/><i>Schema compliance, dedup,<br/>classification, PKCE auth</i>"]
        T3["test_study_dj.py<br/><i>Rule retrieval, filtering,<br/>plan validation, grounding</i>"]
        HUMAN["👤 Human-in-the-Loop<br/><i>• Dashboard controls tune all params<br/>• Visual review of playlist + reasons<br/>• Source context shown for transparency<br/>• Toggle LLM on/off for comparison</i>"]
    end

    %% Data flow connections
    DEMO --> MOD1
    SPOTIFY --> SPOTIFY_PIPELINE --> MOD1
    RULES --> RAG

    MOD1 -->|"active_songs"| RAG
    MOD2 -->|"StudyDJRequest"| RAG
    MOD3 -->|"synthesis_mode + prefs"| RAG
    MOD4 -->|"filter flags"| RAG

    RAG -->|"user_prefs"| SCORING
    SCORING -->|"scored candidates"| RAG
    CONTEXT -->|"retrieved context"| GENERATION

    VALIDATE --> OUTPUT
    FALLBACK_GEN --> OUTPUT
    OUTPUT --> UI

    %% Testing connections
    T1 -.->|"validates"| SCORING
    T2 -.->|"validates"| SPOTIFY_PIPELINE
    T3 -.->|"validates"| RAG
    T3 -.->|"validates"| GENERATION
    HUMAN -.->|"reviews"| OUTPUT

    %% Styling
    classDef input fill:#1a3a2a,stroke:#b5ff7a,color:#b5ff7a
    classDef pipeline fill:#1a2a3a,stroke:#7ab5ff,color:#7ab5ff
    classDef ui fill:#2a1a3a,stroke:#c49bff,color:#c49bff
    classDef rag fill:#3a2a1a,stroke:#ffb57a,color:#ffb57a
    classDef scoring fill:#1a3a3a,stroke:#7affdb,color:#7affdb
    classDef gen fill:#3a1a2a,stroke:#ff7ab5,color:#ff7ab5
    classDef output fill:#2a3a1a,stroke:#dbff7a,color:#dbff7a
    classDef testing fill:#2a2a2a,stroke:#aaa,color:#ccc

    class DEMO,SPOTIFY,RULES input
    class FETCH,NORM,CLASSIFY,LLM_CLASS,FALLBACK_CLASS pipeline
    class MOD1,MOD2,MOD3,MOD4 ui
    class RETRIEVE_RULES,RETRIEVE_SONGS,CONTEXT rag
    class SCORER,BAL,GENRE,MOOD,ENERGY,RESON scoring
    class GEN,LLM_GEN,FALLBACK_GEN,VALIDATE gen
    class PLAYLIST,STRATEGY,METRICS output
    class T1,T2,T3,HUMAN testing
```

## Component Summary

| Component | File(s) | Role |
|-----------|---------|------|
| **Streamlit Dashboard** | `streamlit_app.py` | UI layer — 4 hardware-themed modules let the user configure every parameter |
| **Spotify Ingestion** | `src/spotify_client.py` | Authenticates via PKCE, imports tracks, classifies genre/mood/energy |
| **RAG Retriever** | `src/study_dj.py` | Retrieves matching study rules + candidate songs using scored ranking |
| **Recommender Engine** | `src/recommender.py` | 5 pluggable scorer strategies that rank songs against user preferences |
| **Playlist Generator** | `src/study_dj.py` | AI-grounded (OpenAI/Mistral) or deterministic fallback plan with hallucination guard |
| **Reliability Suite** | `scripts/reliability_test.py` | Automated fidelity and grounding checks across predefined scenarios |
| **Test Suite** | `tests/test_*.py` | 18 automated tests covering scoring, Spotify integration, and RAG grounding |
| **Human Oversight** | Dashboard UI | All retrieval context is visible; users tune params and toggle AI on/off |

## Data Flow Summary

```
User Preferences (UI)
        │
        ▼
┌─────────────────────┐     ┌──────────────────┐
│  Song Catalog        │     │  Study Rules      │
│  (Demo or Spotify)   │     │  (CSV knowledge)  │
└────────┬────────────┘     └────────┬─────────┘
         │                           │
         ▼                           ▼
┌─────────────────────────────────────────────┐
│         RETRIEVAL (RAG)                      │
│  1. Score rules by task/focus match          │
│  2. Filter songs (explicit, lyrics)          │
│  3. Score songs with selected Scorer         │
│  4. Return top-k candidates + rules          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│         GENERATION                           │
│  • AI (OpenAI/Mistral): structured JSON      │
│  • Fallback: deterministic rank + pacing     │
│  • Grounding: reject hallucinated tracks     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│         OUTPUT                               │
│  • Ordered playlist with reasons             │
│  • Study strategy guidance                   │
│  • Full retrieval context (transparent)      │
└─────────────────────────────────────────────┘
```
