# 🎧 Vibe Synthesizer (RAG Study DJ)

Vibe Synthesizer is a Streamlit-based music recommender application that generates highly personalized study playlists. It utilizes traditional content-based song filtering combined with Retrieval-Augmented Generation (RAG) principles and live Spotify account integration to curate well-paced study blocks tailored to your specific task, focus goals, and musical preferences.

The application features a unique, custom 2000s metallic hardware aesthetic for its UI, providing an engaging and nostalgic user experience.

## ✨ Features

- **Spotify PKCE Integration**: Securely connect to your Spotify account using the PKCE authorization flow to import your top and recently played tracks. The app uses a server-configured Spotify Client ID and never asks end users for a Client Secret.
- **Retrieval-Augmented Generation (RAG)**: Combines user preferences with retrieved study rules to ensure the generated playlist matches the desired pacing and target energy levels.
- **Hybrid AI Pipeline**: Leverages OpenAI models (if an API key is provided) to intelligently classify unknown Spotify tracks, synthesize the final tracklist with justifications, and provide a holistic study strategy.
- **Smart Fallback Mechanism**: Gracefully falls back to deterministic planning and title-based genre/mood assignments if API restrictions occur (e.g., `403 Forbidden` from Spotify) or if strict user constraints filter out too many tracks.
- **Custom UI Aesthetic**: A highly-styled 2000s metallic mixer interface built entirely with custom CSS in Streamlit.

## 📂 Project Structure

```text
.
├── assets/                 # Architecture diagrams, screenshots, and visual assets
├── data/                   # Default catalog data
│   ├── songs.csv           # Baseline curated tracks
│   └── study_rules.csv     # Task-specific study rules and pacing guidance
├── docs/                   # Additional documentation
├── src/                    # Source code
│   ├── main.py             # CLI runner
│   ├── recommender.py      # Core recommendation engine and scoring logic
│   ├── spotify_client.py   # Spotify API integration (PKCE flow, track importing)
│   └── study_dj.py         # RAG pipeline and playlist generation logic
├── tests/                  # Unit tests
├── streamlit_app.py        # Streamlit web application (UI and entry point)
├── agent_memory.md         # Developer notes and shared memory
├── model_card.md           # Model architecture and details
└── requirements.txt        # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- [Spotify Developer Account](https://developer.spotify.com/dashboard/) (to get a Client ID and set up Redirect URIs)
- (Optional) [OpenAI API Key](https://platform.openai.com/) for the AI-powered generative planning and feature inference.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shimshiam/ai-system-application-project.git
   cd ai-system-application-project
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Configure Spotify and optional OpenAI access on the server before starting the app.

If setting environment variables:
```bash
export SPOTIPY_CLIENT_ID="your_spotify_client_id"
export SPOTIPY_REDIRECT_URI="http://127.0.0.1:8501" # Default Streamlit port
export OPENAI_API_KEY="your_openai_api_key" # Optional
```

*Note: You must add `http://127.0.0.1:8501` as a Redirect URI in your Spotify Developer Dashboard for the integration to work.*

### Running the App

Start the Streamlit development server:

```bash
streamlit run streamlit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

## 🎮 Usage

1. **Connect Spotify (Optional)**: If the server is configured with `SPOTIPY_CLIENT_ID`, use the "Connect Spotify" button in the "Mix Console" section to authorize your account and import your tracks. You can also proceed using the built-in demo catalog.
2. **Set Study Session**: Choose your task type (e.g., coding, reading), focus goal, and desired session length.
3. **Configure Preferences**: Set your preferred genre, mood, target energy, and toggle advanced filters (Acoustic, Lyrics, Explicit).
4. **Generate**: The Vibe Synthesizer will immediately compute and display your retrieved context, the generated playlist plan, and a custom study strategy.

## 🧪 Testing

Run the test suite using:

```bash
PYTHONPATH=. pytest -q
```

## 📝 License

This project is open-source. Feel free to use, modify, and distribute it as needed.
