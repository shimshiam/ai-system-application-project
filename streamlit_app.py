import os
from html import escape

import streamlit as st

from src.recommender import load_songs
from src.spotify_client import (
    get_spotify_auth_url,
    import_spotify_tracks,
    spotify_is_configured,
)
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


def option_index(options, preferred, fallback=0):
    try:
        return options.index(preferred)
    except ValueError:
        return fallback


def get_query_code():
    value = st.query_params.get("code")
    if isinstance(value, list):
        return value[0] if value else None
    return value


def load_spotify_songs(auth_code):
    return import_spotify_tracks(
        limit_top=5,
        limit_recent=5,
        auth_code=auth_code,
    )


def render_styles():
    st.markdown(
        """
        <style>
        :root {
            --ink: #10131c;
            --panel: #e8edf0;
            --chrome: #c7d1d7;
            --chrome-dark: #6f7a84;
            --screen: #162922;
            --screen-glow: #b5ff7a;
            --red: #f05a46;
            --aqua: #2a8f91;
            --gold: #e1b84d;
        }

        .stApp {
            background:
                radial-gradient(circle at 15% 0%, rgba(255,255,255,0.9), transparent 24rem),
                linear-gradient(135deg, #d9e7e9 0%, #f1efe8 43%, #bcc9d1 100%);
            color: var(--ink);
        }

        header[data-testid="stHeader"] {
            display: none;
        }

        .block-container {
            max-width: 1480px;
            padding-top: 2rem;
            padding-bottom: 1rem;
        }

        /* Mix Console Container Styling - 2000s Metallic Mixer Aesthetic */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background:
                linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(221,229,234,0.96) 42%, rgba(158,171,183,0.98) 100%);
            border: 1px solid rgba(53, 66, 76, 0.42);
            border-radius: 8px;
            box-shadow:
                0 10px 20px rgba(22,32,44,0.15),
                inset 0 1px 0 #ffffff,
                inset 0 -1px 0 rgba(44,54,67,0.42);
            padding: 1.25rem 1rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] * {
            color: #111722 !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"] h3 {
            color: #111722 !important;
            font-family: "Trebuchet MS", Verdana, sans-serif;
            font-size: 1.25rem;
            margin-top: 0;
            padding: 0 0 0.5rem 0;
            background: transparent;
            border: none;
            border-bottom: 2px solid rgba(0,0,0,0.1);
            border-radius: 0;
            box-shadow: 0 1px 0 rgba(255,255,255,0.5);
            text-shadow: 0 1px 0 #fff;
        }

        [data-testid="stVerticalBlockBorderWrapper"] label,
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] p,
        [data-testid="stVerticalBlockBorderWrapper"] .stMarkdown p {
            color: #4a5a6a !important;
            font-family: "Trebuchet MS", sans-serif;
            font-size: 0.82rem;
            font-weight: 800;
            text-transform: uppercase;
            text-shadow: 0 1px 0 #fff;
            letter-spacing: 0.5px;
        }

        /* Recessed Dark LCD Inputs */
        [data-testid="stVerticalBlockBorderWrapper"] [data-baseweb="select"] > div,
        [data-testid="stVerticalBlockBorderWrapper"] [data-baseweb="input"] > div {
            background:
                linear-gradient(180deg, #13231e 0%, #0b1411 100%);
            border: 2px solid #000;
            border-radius: 6px;
            box-shadow: inset 0 0 12px rgba(0,0,0,0.8), 0 1px 0 rgba(255,255,255,0.4);
            min-height: 48px;
        }

        [data-testid="stVerticalBlockBorderWrapper"] [data-baseweb="select"] span {
            color: #b5ff7a !important; /* LCD Green */
            font-family: "Courier New", monospace;
            font-weight: 800;
            text-shadow: 0 0 5px rgba(181,255,122,0.4);
        }

        [data-testid="stVerticalBlockBorderWrapper"] [data-baseweb="input"] input {
            color: #b5ff7a !important;
            font-family: "Courier New", monospace;
            font-weight: 800;
        }

        /* Slider and Toggles embedded in the plastic chassis */
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSlider"] {
            background: rgba(0,0,0,0.03);
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 8px;
            padding: 0.65rem 0.65rem 0.25rem;
            box-shadow: inset 0 1px 2px rgba(0,0,0,0.05), 0 1px 0 #fff;
        }

        [data-testid="stVerticalBlockBorderWrapper"] [role="slider"] {
            background-color: var(--red) !important;
            border-color: #ffafa3 !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }

        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSlider"] [data-testid="stTickBar"] {
            background: rgba(0,0,0,0.1);
        }

        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stToggle"] {
            background: rgba(0,0,0,0.03);
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 999px;
            padding: 0.32rem 0.6rem;
            margin-bottom: 0.35rem;
            box-shadow: inset 0 1px 2px rgba(0,0,0,0.05), 0 1px 0 #fff;
        }

        .player-shell {
            background:
                linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(221,229,234,0.96) 42%, rgba(158,171,183,0.98) 100%);
            border: 1px solid rgba(53, 66, 76, 0.42);
            border-radius: 8px;
            box-shadow:
                0 24px 60px rgba(22,32,44,0.28),
                inset 0 1px 0 #ffffff,
                inset 0 -1px 0 rgba(44,54,67,0.42);
            padding: 1rem;
            margin-bottom: 1.25rem;
        }

        .player-face {
            background:
                linear-gradient(180deg, #eff4f6 0%, #c5d0d7 52%, #8d9aa5 100%);
            border: 1px solid #78848f;
            border-radius: 8px;
            box-shadow: inset 0 1px 0 #fff, inset 0 -12px 30px rgba(28,39,49,0.22);
            padding: 1.1rem;
        }

        .player-top {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 220px;
            gap: 1rem;
            align-items: stretch;
        }

        .lcd {
            background:
                linear-gradient(180deg, rgba(214,255,165,0.09), rgba(100,179,103,0.05)),
                repeating-linear-gradient(0deg, rgba(181,255,122,0.07) 0 1px, transparent 1px 4px),
                #13231e;
            border: 2px solid #0b1411;
            border-radius: 6px;
            box-shadow: inset 0 0 22px rgba(18,0,0,0.65), 0 1px 0 #fff;
            color: var(--screen-glow);
            min-height: 150px;
            padding: 1rem 1.15rem;
            text-shadow: 0 0 6px rgba(181,255,122,0.5);
        }

        .lcd .kicker {
            color: #8ce06d;
            font-family: "Courier New", monospace;
            font-size: 0.8rem;
            letter-spacing: 0;
            text-transform: uppercase;
        }

        .lcd h1 {
            color: #d8ff9e;
            font-family: "Trebuchet MS", Verdana, sans-serif;
            font-size: 2.55rem;
            line-height: 1;
            margin: 0.35rem 0 0.65rem;
            text-shadow: 0 0 10px rgba(181,255,122,0.5);
        }

        .lcd p {
            color: #bde98f;
            margin: 0;
            max-width: 820px;
        }

        .disc {
            background:
                radial-gradient(circle at 50% 50%, #f3f5f7 0 12%, #7f8994 13% 18%, #dbe2e5 19% 32%, #65707a 33% 35%, #e9eef1 36% 100%);
            border: 1px solid #69737e;
            border-radius: 50%;
            min-height: 210px;
            box-shadow: inset 0 2px 4px #fff, inset 0 -10px 18px rgba(19,26,36,0.35), 0 8px 18px rgba(16,22,30,0.25);
        }

        .control-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 1rem;
            align-items: center;
        }

        .control-button {
            background: linear-gradient(180deg, #fbfcfd 0%, #c1cad1 48%, #7f8a95 100%);
            border: 1px solid #5f6b76;
            border-radius: 999px;
            box-shadow: inset 0 1px 0 #fff, 0 2px 4px rgba(17,24,31,0.24);
            color: #121822;
            font-weight: 800;
            min-width: 54px;
            padding: 0.36rem 0.75rem;
            text-align: center;
        }

        .control-button.red {
            background: linear-gradient(180deg, #ffb4aa 0%, #f05a46 48%, #a82620 100%);
            color: #fff;
        }

        .eq {
            display: flex;
            gap: 4px;
            align-items: end;
            height: 42px;
            margin-left: auto;
            min-width: 126px;
        }

        .eq span {
            display: block;
            width: 10px;
            background: linear-gradient(180deg, #fff79c, #49ca79 62%, #1a766f);
            border: 1px solid rgba(0,0,0,0.22);
        }

        .eq span:nth-child(1) { height: 18px; }
        .eq span:nth-child(2) { height: 31px; }
        .eq span:nth-child(3) { height: 24px; }
        .eq span:nth-child(4) { height: 40px; }
        .eq span:nth-child(5) { height: 27px; }
        .eq span:nth-child(6) { height: 35px; }
        .eq span:nth-child(7) { height: 21px; }

        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, #22352e 0%, #101915 100%);
            border: 2px solid #080d0b;
            border-radius: 6px;
            box-shadow: inset 0 0 14px rgba(0,0,0,0.75), 0 1px 0 #fff;
            padding: 0.8rem 1rem;
        }

        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--screen-glow) !important;
            font-family: "Courier New", monospace;
            text-shadow: 0 0 6px rgba(181,255,122,0.4);
        }

        h2, h3 {
            color: #111722 !important;
            font-family: "Trebuchet MS", Verdana, sans-serif;
            text-shadow: 0 1px 0 #fff;
        }

        .section-panel {
            background: rgba(245,248,249,0.82);
            border: 1px solid rgba(68,82,93,0.36);
            border-radius: 8px;
            box-shadow: inset 0 1px 0 #fff, 0 8px 22px rgba(35,48,61,0.12);
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
            color: var(--ink);
        }

        .section-panel p {
            color: #24313d;
            margin-bottom: 0;
        }

        .playlist-track {
            display: grid;
            grid-template-columns: 70px minmax(0, 1fr);
            gap: 1rem;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.96), rgba(229,235,239,0.96));
            border: 1px solid rgba(74,88,100,0.42);
            border-left: 6px solid var(--aqua);
            border-radius: 8px;
            box-shadow: inset 0 1px 0 #fff, 0 5px 13px rgba(28,40,54,0.11);
            color: var(--ink);
            padding: 0.9rem;
            margin-bottom: 0.72rem;
        }

        .track-rank {
            background:
                linear-gradient(180deg, #262d39 0%, #0e1219 100%);
            border: 1px solid #000;
            border-radius: 6px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.2);
            color: #d8ff9e;
            font-family: "Courier New", monospace;
            font-weight: 800;
            min-height: 66px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-shadow: 0 0 6px rgba(181,255,122,0.42);
        }

        .playlist-track h4 {
            color: #111722;
            font-family: "Trebuchet MS", Verdana, sans-serif;
            font-size: 1.1rem;
            margin: 0 0 0.35rem;
        }

        .playlist-track p {
            color: #33414c;
            margin: 0.2rem 0;
        }

        .track-meta {
            color: #60707c;
            font-family: "Courier New", monospace;
            font-size: 0.82rem;
            text-transform: uppercase;
        }

        [data-testid="stExpander"] {
            background: rgba(244,248,249,0.88);
            border: 1px solid rgba(63,76,88,0.38);
            border-radius: 8px;
            box-shadow: inset 0 1px 0 #fff;
        }

        [data-testid="stExpander"] p,
        [data-testid="stExpander"] span {
            color: #1d2730 !important;
        }

        /* --- UI FIXES START --- */
        [data-testid="stAlert"] {
            background: linear-gradient(180deg, #13231e 0%, #0b1411 100%) !important;
            border: 2px solid #000 !important;
            box-shadow: inset 0 0 12px rgba(0,0,0,0.8), 0 1px 0 rgba(255,255,255,0.4) !important;
            border-radius: 6px !important;
        }
        
        [data-testid="stAlert"] * {
            color: #b5ff7a !important;
            font-family: "Courier New", monospace !important;
            text-shadow: 0 0 5px rgba(181,255,122,0.4) !important;
        }

        [data-testid="baseButton-secondary"],
        [data-testid="baseButton-primary"] {
            background: linear-gradient(180deg, #fbfcfd 0%, #c1cad1 48%, #7f8a95 100%) !important;
            border: 1px solid #5f6b76 !important;
            border-radius: 999px !important;
            box-shadow: inset 0 1px 0 #fff, 0 2px 4px rgba(17,24,31,0.24) !important;
            color: #121822 !important;
            font-family: "Trebuchet MS", sans-serif !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            padding: 0.36rem 0.75rem !important;
        }

        [data-testid="baseButton-secondary"]:hover,
        [data-testid="baseButton-primary"]:hover {
            background: linear-gradient(180deg, #ffffff 0%, #d8dfe4 48%, #93a0ac 100%) !important;
            color: #000 !important;
            border-color: #78848f !important;
        }

        [data-testid="stToggle"] p,
        [data-testid="stRadio"] label p {
            color: #4a5a6a !important;
            font-family: "Trebuchet MS", sans-serif !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            text-shadow: 0 1px 0 #fff !important;
            letter-spacing: 0.5px !important;
        }

        h3#mix-console {
            color: #2c3e50 !important;
            font-family: "Trebuchet MS", Verdana, sans-serif !important;
            font-size: 1.8rem !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            text-shadow: 1px 1px 0px rgba(255,255,255,0.7), -1px -1px 0px rgba(0,0,0,0.2) !important;
            margin-top: 1.5rem !important;
            margin-bottom: 1rem !important;
            padding-left: 1rem !important;
            border-left: 6px solid var(--aqua) !important;
        }
        /* --- UI FIXES END --- */

        @media (max-width: 900px) {
            .player-top {
                grid-template-columns: 1fr;
            }

            .disc {
                min-height: 150px;
                max-width: 150px;
                margin: 0 auto;
            }

            .playlist-track {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_player_header():
    st.markdown(
        """
        <div class="player-shell">
          <div class="player-face">
            <div class="player-top">
              <div class="lcd">
                <div class="kicker">Now Playing // Retrieved Study Mix</div>
                <h1>RAG Study DJ</h1>
                <p>Builds a focused playlist by retrieving matching songs and study rules before generating the plan.</p>
              </div>
              <div class="disc"></div>
            </div>
            <div class="control-strip">
              <div class="control-button red">REC</div>
              <div class="control-button">PLAY</div>
              <div class="control-button">STOP</div>
              <div class="control-button">SKIP</div>
              <div class="eq">
                <span></span><span></span><span></span><span></span><span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    demo_songs, study_rules = load_catalog()
    task_types = sorted({rule["task_type"] for rule in study_rules})
    focus_goals = sorted({rule["focus_goal"] for rule in study_rules})

    render_styles()
    render_player_header()

    active_songs = demo_songs
    source_label = "Demo catalog"
    source_notice = ""

    st.markdown("### Mix Console")
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        with st.container(border=True):
            st.subheader("Spotify Integration")
            if not spotify_is_configured():
                st.warning("Spotify credentials are missing. Please provide your Client ID below to connect.")
                client_id = st.text_input("Spotify Client ID", type="password")
                if st.button("Save Credentials", use_container_width=True):
                    if client_id:
                        os.environ["SPOTIPY_CLIENT_ID"] = client_id
                        os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:8501"
                        st.rerun()
                    else:
                        st.error("Please provide your Client ID.")
            else:
                auth_code = get_query_code()
                if not st.session_state.get("spotify_songs"):
                    st.markdown('''<style>a[href^="https://accounts.spotify.com"] { background-color: #1DB954 !important; color: white !important; border: none !important; font-weight: bold !important; }</style>''', unsafe_allow_html=True)
                    st.link_button("Connect Spotify", get_spotify_auth_url())
                if auth_code:
                    st.caption("Spotify authorization code detected.")
                if st.button("Import Spotify tracks", use_container_width=True):
                    try:
                        st.session_state["spotify_songs"] = load_spotify_songs(auth_code)
                        st.session_state["spotify_error"] = ""
                    except Exception as exc:
                        st.session_state["spotify_songs"] = []
                        st.session_state["spotify_error"] = str(exc)

                spotify_songs = st.session_state.get("spotify_songs", [])
                spotify_error = st.session_state.get("spotify_error", "")
                if spotify_songs:
                    st.success(f"Imported {len(spotify_songs)} Spotify tracks.")
                elif spotify_error:
                    st.warning(f"Spotify import failed: {spotify_error}")

            st.subheader("Music Source")
            source_options = ["Demo catalog"]
            if st.session_state.get("spotify_songs"):
                source_options.append("Spotify import")
                
            source_mode = st.radio(
                "Catalog source",
                source_options,
                horizontal=True,
                index=1 if st.session_state.get("spotify_songs") else 0,
                label_visibility="collapsed"
            )
            
            if source_mode == "Spotify import" and st.session_state.get("spotify_songs"):
                active_songs = st.session_state["spotify_songs"]
                source_label = "Spotify import"
                source_notice = ""
            else:
                active_songs = demo_songs
                source_label = "Demo catalog"
                if spotify_is_configured() and not st.session_state.get("spotify_songs"):
                    source_notice = "Connect Spotify and import tracks, or keep using the demo catalog."

    with col2:
        with st.container(border=True):
            genres = unique_values(active_songs, "genre")
            moods = unique_values(active_songs, "mood")

            st.subheader("Study Session")
            task_type = st.selectbox("Task type", task_types, index=option_index(task_types, "coding"))
            focus_goal = st.selectbox("Focus goal", focus_goals, index=option_index(focus_goals, "deep focus"))
            session_minutes = st.slider("Session length", 15, 120, 45, step=5)

    with col3:
        with st.container(border=True):
            st.subheader("Music Preferences")
            preferred_genre = st.selectbox("Preferred genre", genres, index=option_index(genres, "lofi"))
            preferred_mood = st.selectbox("Preferred mood", moods, index=option_index(moods, "focused"))
            target_energy = st.slider("Target energy", 0.0, 1.0, 0.4, step=0.05)
            
            st.markdown("**Filters & Advanced**")
            col_a, col_b = st.columns(2)
            with col_a:
                likes_acoustic = st.toggle("Acoustic", value=True)
                allows_lyrics = st.toggle("Lyrics", value=False)
            with col_b:
                allows_explicit = st.toggle("Explicit", value=False)
                use_llm = st.toggle("Use LLM", value=bool(os.getenv("OPENAI_API_KEY")))

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
        active_songs,
        study_rules,
        k=5,
        use_llm=use_llm,
        model=os.getenv("AI_MODEL"),
    )
    retrieval = result["retrieval"]
    playlist = result["playlist"]

    metric_cols = st.columns(3)
    metric_cols[0].metric("Retrieved Songs", len(retrieval["retrieved_songs"]))
    metric_cols[1].metric("Catalog Source", source_label)
    metric_cols[2].metric("AI Mode", "OpenAI" if use_llm and os.getenv("OPENAI_API_KEY") else "Fallback")

    if source_notice:
        st.info(source_notice)

    left, right = st.columns([1.25, 0.85], gap="large")
    with left:
        st.subheader("Generated Playlist Plan")
        st.markdown(
            f"<div class='section-panel'><p>{escape(playlist['summary'])}</p></div>",
            unsafe_allow_html=True,
        )
        if playlist.get("ai_notice"):
            st.info(playlist["ai_notice"])
        for track in playlist["ordered_tracks"]:
            st.markdown(
                f"""
                <div class="playlist-track">
                    <div class="track-rank">{escape(str(track['rank'])).zfill(2)}</div>
                    <div>
                        <div class="track-meta">Track {escape(str(track['rank']))}</div>
                        <h4>{escape(track['title'])} - {escape(track['artist'])}</h4>
                        <p>{escape(track['reason'])}</p>
                        <p><strong>Pacing:</strong> {escape(track['pacing_note'])}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.subheader("Study Strategy")
        st.markdown(
            f"<div class='section-panel'><p>{escape(playlist['study_strategy'])}</p></div>",
            unsafe_allow_html=True,
        )
        st.subheader("Retrieved Context")
        st.markdown(
            f"<div class='section-panel'><p>{escape(retrieval['retrieval_explanation'])}</p></div>",
            unsafe_allow_html=True,
        )
        with st.expander("Songs used as context", expanded=True):
            for item in retrieval["retrieved_songs"]:
                song = item["song"]
                st.write(
                    f"**{song['title']}** by {song['artist']} "
                    f"({song['genre']}, {song['mood']}) - score {item['score']}"
                )
                if song.get("spotify_url"):
                    st.caption(f"Spotify source: {song['source']} - {song['spotify_url']}")
                st.caption(item["explanation"])
        with st.expander("Study rules used as context"):
            for rule in retrieval["retrieved_study_rules"]:
                st.write(f"**{rule['task_type']} / {rule['focus_goal']}**")
                st.caption(rule["guidance"])


if __name__ == "__main__":
    main()
