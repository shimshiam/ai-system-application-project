import os

import streamlit as st

from src.recommender import load_songs
from src.study_dj import (
    StudyDJRequest,
    build_study_playlist,
    default_data_paths,
    load_study_rules,
)


st.set_page_config(
    page_title="RAG Study DJ",
    page_icon="SD",
    layout="wide",
)


@st.cache_data
def load_catalog():
    paths = default_data_paths()
    return load_songs(str(paths["songs"])), load_study_rules(str(paths["study_rules"]))


def unique_values(songs, field):
    return sorted({song[field] for song in songs})


def main():
    songs, study_rules = load_catalog()
    genres = unique_values(songs, "genre")
    moods = unique_values(songs, "mood")
    task_types = sorted({rule["task_type"] for rule in study_rules})
    focus_goals = sorted({rule["focus_goal"] for rule in study_rules})

    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #f4f0e8 0%, #e8f1ee 52%, #f7f5ee 100%);
        }
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.68);
            border: 1px solid rgba(47, 79, 79, 0.14);
            padding: 0.7rem 0.9rem;
            border-radius: 8px;
        }
        .playlist-track {
            background: rgba(255, 255, 255, 0.74);
            border: 1px solid rgba(34, 68, 64, 0.16);
            border-left: 5px solid #2f6f73;
            border-radius: 8px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.75rem;
        }
        .small-label {
            color: #49615f;
            font-size: 0.86rem;
            text-transform: uppercase;
            letter-spacing: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("RAG Study DJ")
    st.caption("A study playlist assistant that retrieves songs and task guidance before generating a plan.")

    with st.sidebar:
        st.header("Study Session")
        task_type = st.selectbox("Task type", task_types, index=task_types.index("coding"))
        focus_goal = st.selectbox("Focus goal", focus_goals, index=focus_goals.index("deep focus"))
        session_minutes = st.slider("Session length", 15, 120, 45, step=5)

        st.header("Music Preferences")
        preferred_genre = st.selectbox("Preferred genre", genres, index=genres.index("lofi"))
        preferred_mood = st.selectbox("Preferred mood", moods, index=moods.index("focused"))
        target_energy = st.slider("Target energy", 0.0, 1.0, 0.4, step=0.05)
        likes_acoustic = st.toggle("Prefer acoustic sound", value=True)
        allows_lyrics = st.toggle("Allow lyrics", value=False)
        allows_explicit = st.toggle("Allow explicit tracks", value=False)
        use_llm = st.toggle(
            "Use OpenAI when configured",
            value=bool(os.getenv("OPENAI_API_KEY")),
            help="If no API key exists, the app uses a deterministic fallback planner.",
        )

    request = StudyDJRequest(
        task_type=task_type,
        session_minutes=session_minutes,
        focus_goal=focus_goal,
        preferred_genre=preferred_genre,
        preferred_mood=preferred_mood,
        target_energy=target_energy,
        likes_acoustic=likes_acoustic,
        allows_lyrics=allows_lyrics,
        allows_explicit=allows_explicit,
    )

    result = build_study_playlist(
        request,
        songs,
        study_rules,
        k=5,
        use_llm=use_llm,
        model=os.getenv("AI_MODEL"),
    )
    retrieval = result["retrieval"]
    playlist = result["playlist"]

    metric_cols = st.columns(3)
    metric_cols[0].metric("Retrieved Songs", len(retrieval["retrieved_songs"]))
    metric_cols[1].metric("Study Rules", len(retrieval["retrieved_study_rules"]))
    metric_cols[2].metric("AI Mode", "OpenAI" if use_llm and os.getenv("OPENAI_API_KEY") else "Fallback")

    left, right = st.columns([1.25, 0.85], gap="large")
    with left:
        st.subheader("Generated Playlist Plan")
        st.write(playlist["summary"])
        for track in playlist["ordered_tracks"]:
            st.markdown(
                f"""
                <div class="playlist-track">
                    <div class="small-label">Track {track['rank']}</div>
                    <h4>{track['title']} - {track['artist']}</h4>
                    <p>{track['reason']}</p>
                    <p><strong>Pacing:</strong> {track['pacing_note']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.subheader("Study Strategy")
        st.write(playlist["study_strategy"])
        st.subheader("Retrieved Context")
        st.caption(retrieval["retrieval_explanation"])
        with st.expander("Songs used as context", expanded=True):
            for item in retrieval["retrieved_songs"]:
                song = item["song"]
                st.write(
                    f"**{song['title']}** by {song['artist']} "
                    f"({song['genre']}, {song['mood']}) - score {item['score']}"
                )
                st.caption(item["explanation"])
        with st.expander("Study rules used as context"):
            for rule in retrieval["retrieved_study_rules"]:
                st.write(f"**{rule['task_type']} / {rule['focus_goal']}**")
                st.caption(rule["guidance"])


if __name__ == "__main__":
    main()
