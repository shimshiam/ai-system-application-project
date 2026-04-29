# 🎚️ Vibe Synthesizer (RAG Study DJ)

**Vibe Synthesizer** is an advanced, RAG-powered music recommendation system designed to curate perfectly paced study playlists. By bridging the gap between your personal Spotify library and task-specific cognitive focus strategies, it ensures your audio environment matches the intensity of your work.

---

## 🕒 Original Project: Music Recommender Simulation (Module 3)
This project originated as **Music Recommender Simulation**, a simple command-line interface tool. 
*   **Original Goals**: To demonstrate basic content-based filtering by matching user-inputted genre and mood preferences against a static catalog of 20 songs.
*   **Original Capabilities**: Basic scoring logic based on energy closeness and string-match genre detection, producing a ranked list of top 5 recommendations in the terminal.

---

## 🏗️ Architecture Overview

The Vibe Synthesizer evolved into a multi-layered Retrieval-Augmented Generation (RAG) system:

1.  **Ingestion Layer**: Securely imports user data (Top Tracks, Recently Played) via the **Spotify PKCE Flow**.
2.  **Retrieval Layer (The Vibe Engine)**: 
    *   Queries `study_rules.csv` for task-specific guidance (e.g., "Coding" requires "Instrumental" and "High Energy").
    *   Scores candidate tracks using weighted algorithms (**Balanced**, **Resonance**, **Energy-Focused**) to find the best match for the current focus block.
3.  **Synthesis Layer (RAG)**: An LLM (OpenAI) synthesizes the retrieved tracks and study rules into a cohesive **Playlist Plan**, providing a "Pacing Note" for every track to explain its role in the study arc.
4.  **Presentation Layer (Mix Console)**: A custom-themed Streamlit dashboard utilizing a **2000s skeuomorphic hardware aesthetic** for a tactile, immersive user experience.

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- [Spotify Developer Account](https://developer.spotify.com/dashboard/) (to obtain a Client ID)
- (Optional) [OpenAI API Key](https://platform.openai.com/) for AI-powered planning.

### Installation
1. **Clone and Enter**:
   ```bash
   git clone https://github.com/shimshiam/ai-system-application-project.git
   cd ai-system-application-project
   ```
2. **Environment Setup**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Configuration**: Create a `.env` file or export the following:
   ```bash
   export SPOTIPY_CLIENT_ID="your_client_id"
   export SPOTIPY_REDIRECT_URI="http://127.0.0.1:8501"
   export OPENAI_API_KEY="your_openai_key" # Optional
   ```

### Running the App
```bash
streamlit run streamlit_app.py
```

---

## 🎮 Sample Interactions

| Input (Task/Goal) | Preferred Vibe | Resulting AI Output (Strategy) |
| :--- | :--- | :--- |
| **Coding / Deep Work** | Lo-Fi, Chill, 0.4 Energy | "Warm-up with 'Midnight City' (0.35 energy). Build to 'Data Stream' (0.6 energy) during core logic hours. Strategy: Use steady rhythms to mask ambient noise." |
| **Reading / Calm** | Jazz, Relaxed, 0.2 Energy | "A 30-minute block of low-intensity acoustic jazz. Strategy: Maintain a consistent background hum without linguistic distraction to maximize comprehension." |
| **Workout / Power** | Metal, Aggressive, 0.9 Energy | "High-intensity metal and electronic tracks. Strategy: Maximum BPM and aggressive mood weighting to drive physical performance during interval peaks." |

---

## 🛠️ Design Decisions & Trade-offs

*   **Skeuomorphic Hardware UI**: I chose a "Mix Console" aesthetic to make the "Synthesis" of vibes feel physical and tactile, moving away from flat modern design to create a more focused, nostalgic environment.
*   **Spotify PKCE Authorization**: I implemented the PKCE flow specifically to improve security. This allows the application to run in client-side contexts without requiring a `Client Secret`, making it safer for users to connect their accounts.
*   **RAG vs. Pure Generative**: Instead of letting the AI "hallucinate" songs, I use RAG to ground every recommendation in the user's actual Spotify library or a curated catalog.

---

## 🧪 Testing Summary

*   **What Worked**: The hybrid scoring system successfully distinguishes between "Background" tasks (low energy, acoustic) and "Active" tasks (high energy, electronic).
*   **The Energy Drift Problem**: During testing, I found that high-energy tracks often dominated rankings. I solved this by implementing the **Resonance Scorer**, which penalizes tracks that deviate too far from the median library energy.
*   **Automation**: Unit tests (`pytest`) ensure that Spotify data parsing remains robust even when metadata is missing or restricted.

---

## 🧠 Reflection: AI and Problem Solving

Building the **Vibe Synthesizer** taught me that the "Vibe" of an AI application is as much about the **deterministic constraints** as it is about the **generative model**. By using RAG, I ensure the AI acts as a "curator" rather than a "creator," which is essential for tools meant to aid human productivity. I learned that the most difficult part of AI development isn't the prompt engineering—it's the **data plumbing** and ensuring the UI provides enough feedback for the user to trust the algorithm's decisions.
