import os
from pathlib import Path
from html import escape

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

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
    page_title="Vibe Synthesizer",
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

try:
    from spotipy.cache_handler import CacheHandler
    class StreamlitSessionCacheHandler(CacheHandler):
        def get_cached_token(self):
            return st.session_state.get("spotify_token_info")
        def save_token_to_cache(self, token_info):
            st.session_state["spotify_token_info"] = token_info
except ImportError:
    StreamlitSessionCacheHandler = None

def load_spotify_songs(auth_code, cache_handler):
    return import_spotify_tracks(
        limit_top=25,
        limit_recent=25,
        auth_code=auth_code,
        cache_handler=cache_handler,
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

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) {
            background:
                radial-gradient(circle at top left, rgba(255,255,255,0.08), transparent 16rem),
                linear-gradient(180deg, #252d37 0%, #161c23 100%) !important;
            border: 1px solid #0b0f13 !important;
            border-radius: 14px !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.08),
                inset 0 -18px 28px rgba(0,0,0,0.34),
                0 18px 34px rgba(21,27,34,0.18) !important;
            padding: 1rem 1rem 0.95rem !important;
            position: relative;
            overflow: hidden;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor)::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, rgba(120,81,45,0.95) 0, rgba(52,33,20,0.98) 18px, transparent 18px calc(100% - 18px), rgba(52,33,20,0.98) calc(100% - 18px), rgba(120,81,45,0.95) 100%);
            opacity: 0.9;
            pointer-events: none;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor)::after {
            content: "";
            position: absolute;
            inset: 14px;
            border: 1px solid rgba(243,187,96,0.16);
            border-radius: 10px;
            pointer-events: none;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04);
        }

        .module-anchor {
            display: none;
        }

        .module-intro {
            position: relative;
            z-index: 1;
            margin: -0.2rem -0.08rem 0.95rem;
            padding: 0.95rem 1rem 0.9rem;
            background:
                linear-gradient(180deg, rgba(18,23,29,0.98) 0%, rgba(30,38,48,0.98) 100%);
            border: 1px solid rgba(92,111,128,0.4);
            border-radius: 10px;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.06),
                inset 0 -16px 26px rgba(0,0,0,0.34);
        }

        .module-head {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 0.9rem;
            align-items: start;
        }

        .module-legend {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.55rem;
            margin-bottom: 0.55rem;
        }

        .module-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.38rem;
            padding: 0.18rem 0.48rem;
            border-radius: 999px;
            background: rgba(120,198,220,0.1);
            border: 1px solid rgba(120,198,220,0.24);
            color: #cfefff;
            font-family: "Courier New", monospace;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .module-chip::before {
            content: "";
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, #fdffd3 0%, #a6ff78 48%, #256c39 100%);
            box-shadow: 0 0 7px rgba(146,255,112,0.72);
        }

        .module-title {
            color: #f6f1de;
            font-family: "Trebuchet MS", Verdana, sans-serif;
            font-size: 1.22rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            margin: 0;
            text-transform: uppercase;
        }

        .module-code {
            align-self: start;
            background:
                linear-gradient(180deg, #12171d 0%, #05080b 100%);
            border: 1px solid rgba(120,198,220,0.34);
            border-radius: 999px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
            color: #dbffaf;
            font-family: "Courier New", monospace;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            padding: 0.34rem 0.64rem;
            text-shadow: 0 0 7px rgba(154,242,109,0.25);
        }

        .module-subtitle {
            color: #cad4df;
            font-size: 0.95rem;
            font-weight: 500;
            line-height: 1.52;
            margin: 0;
            max-width: 56ch;
        }

        .module-hardware {
            display: grid;
            grid-template-columns: 118px minmax(0, 1fr);
            gap: 1rem;
            align-items: center;
            margin-top: 0.9rem;
            padding: 0.8rem 0.85rem;
            background:
                linear-gradient(180deg, rgba(4,7,11,0.46) 0%, rgba(26,34,44,0.28) 100%);
            border: 1px solid rgba(142,162,181,0.18);
            border-radius: 10px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
        }

        .module-knob-cluster {
            display: flex;
            gap: 0.75rem;
            justify-content: space-between;
        }

        .module-knob {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.34rem;
        }

        .module-knob-face {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            background:
                radial-gradient(circle at 35% 30%, #f9fbff 0 10%, #aebbc8 20%, #5b6470 58%, #1a2027 100%);
            border: 1px solid rgba(212,220,229,0.16);
            box-shadow: inset 0 2px 4px rgba(255,255,255,0.7), 0 3px 7px rgba(0,0,0,0.35);
            position: relative;
        }

        .module-knob-face::after {
            content: "";
            position: absolute;
            top: 4px;
            left: 15px;
            width: 4px;
            height: 12px;
            border-radius: 3px;
            background: linear-gradient(180deg, #fff8c1 0%, #f0bc61 100%);
            box-shadow: 0 0 5px rgba(244,188,97,0.65);
        }

        .module-knob span {
            color: #d5dee7;
            font-family: "Courier New", monospace;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .module-patch-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem 1rem;
            align-items: center;
        }

        .module-jack {
            display: inline-flex;
            align-items: center;
            gap: 0.42rem;
            min-width: 74px;
        }

        .module-jack-hole {
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background:
                radial-gradient(circle at 50% 50%, #010204 0 34%, #4f5a68 35% 58%, #151a22 59% 100%);
            border: 1px solid rgba(200,208,218,0.16);
            box-shadow: inset 0 0 4px rgba(0,0,0,0.9);
            flex-shrink: 0;
        }

        .module-jack span {
            color: #b9c5d2;
            font-family: "Courier New", monospace;
            font-size: 0.73rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .module-footer {
            position: relative;
            z-index: 1;
            margin-top: -0.15rem;
            padding-top: 0.3rem;
            border-top: 1px solid rgba(173,143,87,0.18);
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.8rem;
        }

        .module-led-bank {
            display: flex;
            gap: 0.42rem;
        }

        .module-led {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #10161d;
            border: 1px solid rgba(201,208,216,0.12);
            box-shadow: inset 0 0 3px rgba(0,0,0,0.9);
        }

        .module-led.live {
            background: radial-gradient(circle at 30% 30%, #fdffd3 0%, #a6ff78 46%, #246c3a 100%);
            box-shadow: 0 0 8px rgba(152,255,116,0.72);
        }

        .module-bus {
            color: #d7fbaf;
            background: linear-gradient(180deg, rgba(10,15,20,0.96), rgba(28,35,44,0.96));
            border: 1px solid rgba(120,198,220,0.22);
            border-radius: 999px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
            font-family: "Courier New", monospace;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            padding: 0.18rem 0.56rem;
            text-transform: uppercase;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) {
            background:
                radial-gradient(circle at top left, rgba(255,255,255,0.62), transparent 14rem),
                linear-gradient(180deg, #edf2f5 0%, #c9d2da 46%, #a0adb9 100%) !important;
            border: 1px solid #6a7784 !important;
            border-radius: 12px !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.94),
                inset 0 -12px 18px rgba(58,70,82,0.12),
                0 8px 18px rgba(34,45,56,0.08) !important;
            padding: 0.9rem 0.95rem 0.85rem !important;
            position: relative;
            overflow: hidden;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor)::before {
            content: "";
            position: absolute;
            inset: 12px;
            border: 1px solid rgba(71,84,96,0.18);
            border-radius: 9px;
            pointer-events: none;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
        }

        .control-bay-anchor {
            display: none;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) div[data-testid="stWidgetLabel"] {
            display: inline-flex;
            align-items: center;
            margin-bottom: 0.34rem;
            padding: 0.14rem 0.36rem;
            background: linear-gradient(180deg, rgba(250,252,253,0.96), rgba(212,220,227,0.9));
            border: 1px solid rgba(103,118,130,0.28);
            border-radius: 4px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.92);
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) div[data-testid="stWidgetLabel"] *,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) label * {
            color: #16222f !important;
            font-family: "Trebuchet MS", Verdana, sans-serif !important;
            font-size: 0.88rem !important;
            font-weight: 700 !important;
            letter-spacing: 0 !important;
            text-transform: none !important;
            text-shadow: 0 1px 0 rgba(255,255,255,0.78) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="select"] > div,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="input"] > div {
            background:
                linear-gradient(180deg, #1f2630 0%, #2c3440 100%) !important;
            border: 1px solid rgba(87,100,113,0.58) !important;
            border-radius: 8px !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.08),
                inset 0 -9px 14px rgba(0,0,0,0.34),
                0 1px 3px rgba(30,39,48,0.18) !important;
            min-height: 48px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="select"] *,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="input"] input,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="select"] [class*="singleValue"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="select"] [class*="placeholder"] {
            color: #f3f7fb !important;
            font-family: "Trebuchet MS", Verdana, sans-serif !important;
            font-weight: 700 !important;
            text-shadow: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="select"] svg {
            color: #d4dde6 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stSlider"] {
            background:
                linear-gradient(180deg, rgba(246,249,251,0.94), rgba(214,223,230,0.9)) !important;
            border: 1px solid rgba(91,104,116,0.3) !important;
            border-radius: 8px !important;
            padding: 0.7rem 0.78rem 0.44rem !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.86), inset 0 -8px 12px rgba(68,80,92,0.08) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="slider"] > div > div {
            height: 10px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="slider"] > div > div > div {
            border-radius: 999px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="slider"] > div > div > div:first-child {
            background: linear-gradient(90deg, #808a93 0%, #dbe2e8 100%) !important;
            box-shadow: inset 0 1px 1px rgba(0,0,0,0.18) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="slider"] > div > div > div:nth-child(2) {
            background: linear-gradient(90deg, #9fe0ff 0%, #53bcf1 48%, #74d97a 100%) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.25), 0 0 8px rgba(83,188,241,0.16) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [role="slider"] {
            background: linear-gradient(180deg, #fbfdff 0%, #c7d0d8 40%, #7b8792 100%) !important;
            border: 1px solid #55616c !important;
            border-radius: 6px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.94), 0 2px 4px rgba(43,53,63,0.2) !important;
            width: 22px !important;
            height: 26px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stRadio"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            box-shadow: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stRadio"] label {
            background: none !important;
            border: none !important;
            padding: 0.12rem 0 !important;
            box-shadow: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stRadio"] p {
            color: #101922 !important;
            font-family: "Trebuchet MS", Verdana, sans-serif !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            text-shadow: 0 1px 0 rgba(255,255,255,0.78) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stMarkdownContainer"] p {
            color: #d2dbe3;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) label *,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stWidgetLabel"] * {
            color: #d9f5ff !important;
            font-family: "Courier New", monospace !important;
            font-size: 0.76rem !important;
            font-weight: 700 !important;
            text-shadow: none !important;
            letter-spacing: 0.1em !important;
            text-transform: uppercase !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stWidgetLabel"] {
            display: inline-flex;
            align-items: center;
            margin-bottom: 0.34rem;
            padding: 0.18rem 0.54rem;
            background: linear-gradient(180deg, #161d24 0%, #0d1218 100%);
            border: 1px solid rgba(120,198,220,0.24);
            border-radius: 999px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="select"] > div,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="input"] > div {
            background:
                linear-gradient(180deg, #323c47 0%, #1a222a 100%) !important;
            border: 1px solid rgba(118,135,150,0.46) !important;
            border-radius: 9px !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.08),
                inset 0 -12px 18px rgba(0,0,0,0.38),
                0 2px 4px rgba(0,0,0,0.22) !important;
            min-height: 52px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="select"] *,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="input"] input {
            color: #f4f7fb !important;
            font-family: "Trebuchet MS", Verdana, sans-serif !important;
            font-weight: 700 !important;
            text-shadow: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="select"] svg {
            color: #bdefff !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="select"] [class*="singleValue"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="select"] [class*="placeholder"] {
            color: #f4f7fb !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="select"] > div:hover,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="input"] > div:hover {
            border-color: rgba(120,198,220,0.46) !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.08),
                inset 0 -12px 18px rgba(0,0,0,0.42),
                0 0 0 1px rgba(120,198,220,0.08) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-testid="stSlider"] {
            background:
                linear-gradient(180deg, rgba(18,23,29,0.88), rgba(28,37,47,0.88)) !important;
            border: 1px solid rgba(96,113,128,0.32) !important;
            border-radius: 10px !important;
            padding: 0.8rem 0.85rem 0.5rem !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), inset 0 -10px 16px rgba(0,0,0,0.28) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="slider"] {
            padding: 0.12rem 0 0.28rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="slider"] > div > div {
            height: 12px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="slider"] > div > div > div {
            border-radius: 999px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="slider"] > div > div > div:first-child {
            background: linear-gradient(90deg, #0b0f14 0%, #39444e 100%) !important;
            box-shadow: inset 0 1px 2px rgba(255,255,255,0.04), inset 0 -1px 3px rgba(0,0,0,0.62) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-baseweb="slider"] > div > div > div:nth-child(2) {
            background: linear-gradient(90deg, #bdefff 0%, #72d7ff 42%, #9af26d 100%) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.28), 0 0 9px rgba(114,215,255,0.18) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [role="slider"] {
            background:
                linear-gradient(180deg, #f6f8fb 0%, #b8c1cb 34%, #5e6873 100%) !important;
            border: 1px solid #3f4a55 !important;
            border-radius: 7px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.92), 0 3px 5px rgba(0,0,0,0.34) !important;
            width: 24px !important;
            height: 28px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-testid="stRadio"] {
            background: rgba(6,10,15,0.34);
            border: 1px solid rgba(96,113,128,0.24);
            border-radius: 10px;
            padding: 0.6rem 0.72rem 0.48rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-testid="stRadio"] label {
            background:
                linear-gradient(180deg, #2f3944 0%, #161d24 100%);
            border: 1px solid rgba(108,124,138,0.46);
            border-radius: 999px;
            padding: 0.34rem 0.76rem 0.28rem !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 1px 3px rgba(0,0,0,0.24);
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-testid="stRadio"] p {
            color: #f3f6fb !important;
            font-family: "Trebuchet MS", Verdana, sans-serif !important;
            font-size: 0.88rem !important;
            font-weight: 700 !important;
            text-shadow: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-testid="stRadio"] > div {
            gap: 0.6rem !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-testid="stRadio"] label[data-checked="true"] {
            border-color: rgba(154,242,109,0.55) !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.08),
                0 0 0 1px rgba(154,242,109,0.14),
                0 0 10px rgba(154,242,109,0.08) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-testid="stCheckbox"] {
            background:
                linear-gradient(180deg, rgba(18,24,31,0.86), rgba(31,39,49,0.9)) !important;
            border: 1px solid rgba(101,119,134,0.3) !important;
            border-radius: 10px !important;
            padding: 0.46rem 0.68rem !important;
            margin-bottom: 0.5rem !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 1px 3px rgba(0,0,0,0.18) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-testid="stCheckbox"] p {
            color: #f1f5fa !important;
            font-family: "Trebuchet MS", Verdana, sans-serif !important;
            font-size: 0.96rem !important;
            font-weight: 700 !important;
            text-shadow: none !important;
            background: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-testid="stCheckbox"] label {
            gap: 0.5rem !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:first-child {
            background: linear-gradient(180deg, #202730 0%, #0d1116 100%) !important;
            border: 1px solid rgba(120,198,220,0.36) !important;
            border-radius: 4px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 1px 2px rgba(0,0,0,0.28) !important;
            width: 20px !important;
            height: 20px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) [data-testid="stCheckbox"] [data-baseweb="checkbox"] input:checked + div::after {
            width: 11px !important;
            height: 11px !important;
            background: radial-gradient(circle at 30% 30%, #fdffd3 0%, #9af26d 52%, #226c39 100%) !important;
            border-radius: 50% !important;
            box-shadow: 0 0 8px rgba(154,242,109,0.72) !important;
        }

        /* --- Nested control bay inside module: comprehensive dark-text overrides --- */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) {
            background:
                repeating-linear-gradient(
                    90deg,
                    rgba(255,255,255,0.06) 0 1px, transparent 1px 4px
                ),
                radial-gradient(circle at top left, rgba(255,255,255,0.72), transparent 14rem),
                linear-gradient(180deg, #e2e9ee 0%, #c4cdd5 38%, #9daab6 100%) !important;
            border: 1px solid #5e6d7a !important;
            border-radius: 10px !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.96),
                inset 0 -14px 22px rgba(58,70,82,0.14),
                0 6px 16px rgba(34,45,56,0.10) !important;
            padding: 1rem 1rem 0.9rem !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor)::before {
            content: "";
            position: absolute;
            inset: 8px;
            border: 1px solid rgba(71,84,96,0.14);
            border-radius: 8px;
            pointer-events: none;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.8);
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) div[data-testid="stWidgetLabel"] {
            background: linear-gradient(180deg, rgba(250,252,253,0.98), rgba(208,216,223,0.94)) !important;
            border: 1px solid rgba(88,102,114,0.32) !important;
            border-radius: 4px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.96) !important;
            padding: 0.16rem 0.42rem !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) div[data-testid="stWidgetLabel"] *,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) label *,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stRadio"] p,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stCheckbox"] p,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stSlider"] *,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stMarkdownContainer"] p,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) small,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) span {
            color: #0e1820 !important;
            font-family: "Trebuchet MS", Verdana, sans-serif !important;
            font-size: 0.88rem !important;
            font-weight: 700 !important;
            letter-spacing: 0 !important;
            text-transform: none !important;
            text-shadow: 0 1px 0 rgba(255,255,255,0.82) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stRadio"] label {
            background: linear-gradient(180deg, rgba(252,253,254,0.96), rgba(219,227,234,0.94)) !important;
            border: 1px solid rgba(102,116,128,0.34) !important;
            border-radius: 999px !important;
            padding: 0.28rem 0.74rem 0.24rem !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.94),
                inset 0 -4px 8px rgba(77,89,101,0.08),
                0 1px 2px rgba(34,45,56,0.08) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stRadio"] label[data-checked="true"] {
            border-color: rgba(60,110,148,0.52) !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.96),
                inset 0 -4px 8px rgba(77,89,101,0.08),
                0 0 0 1px rgba(60,110,148,0.18) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stCheckbox"] {
            background:
                linear-gradient(180deg, rgba(248,251,253,0.96), rgba(218,226,233,0.94)) !important;
            border: 1px solid rgba(102,116,128,0.32) !important;
            border-radius: 8px !important;
            padding: 0.42rem 0.62rem !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.94),
                inset 0 -6px 10px rgba(77,89,101,0.08),
                0 1px 2px rgba(34,45,56,0.08) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:first-child {
            background: linear-gradient(180deg, #f9fbfd 0%, #cfd8df 100%) !important;
            border: 1px solid rgba(91,104,116,0.42) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.96), 0 1px 2px rgba(34,45,56,0.1) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-testid="stSlider"] {
            background:
                linear-gradient(180deg, rgba(244,248,250,0.96), rgba(210,219,226,0.92)) !important;
            border: 1px solid rgba(88,102,114,0.32) !important;
            border-radius: 8px !important;
            padding: 0.7rem 0.78rem 0.44rem !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.9), inset 0 -8px 12px rgba(68,80,92,0.06) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="slider"] > div > div > div:first-child {
            background: linear-gradient(90deg, #808a93 0%, #dbe2e8 100%) !important;
            box-shadow: inset 0 1px 1px rgba(0,0,0,0.18) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="slider"] > div > div > div:nth-child(2) {
            background: linear-gradient(90deg, #9fe0ff 0%, #53bcf1 48%, #74d97a 100%) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [role="slider"] {
            background: linear-gradient(180deg, #fbfdff 0%, #c7d0d8 40%, #7b8792 100%) !important;
            border: 1px solid #55616c !important;
            border-radius: 6px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.94), 0 2px 4px rgba(43,53,63,0.2) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="select"] > div {
            background:
                linear-gradient(180deg, #1f2630 0%, #2c3440 100%) !important;
            border: 1px solid rgba(87,100,113,0.58) !important;
            border-radius: 8px !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.08),
                inset 0 -9px 14px rgba(0,0,0,0.34),
                0 1px 3px rgba(30,39,48,0.18) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="select"] [class*="singleValue"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="select"] [class*="placeholder"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="select"] *,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="input"] input {
            color: #f3f7fb !important;
            font-family: "Trebuchet MS", Verdana, sans-serif !important;
            font-weight: 700 !important;
            text-shadow: none !important;
            letter-spacing: 0 !important;
            text-transform: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.module-anchor) div[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bay-anchor) [data-baseweb="select"] svg {
            color: #d4dde6 !important;
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
            background: #888 !important;
            background-image: linear-gradient(180deg, #ccc 0%, #888 100%) !important;
            border: 2px outset #ccc !important;
            border-radius: 2px !important;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.8) !important;
            padding: 0.36rem 0.75rem !important;
        }
        
        [data-testid="baseButton-secondary"] *,
        [data-testid="baseButton-primary"] * {
            color: #000 !important;
            font-family: Tahoma, "MS Sans Serif", Verdana, sans-serif !important;
            font-weight: bold !important;
            text-transform: none !important;
        }

        [data-testid="baseButton-secondary"]:active,
        [data-testid="baseButton-primary"]:active {
            border: 2px inset #ccc !important;
            box-shadow: inset 2px 2px 5px rgba(0,0,0,0.8) !important;
            background-image: linear-gradient(180deg, #777 0%, #aaa 100%) !important;
        }

        h3#mix-console {
            color: #24323e !important;
            font-family: "Trebuchet MS", Verdana, sans-serif !important;
            font-size: 1.9rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            text-shadow: 0 1px 0 rgba(255,255,255,0.85) !important;
            margin-top: 1.55rem !important;
            margin-bottom: 1.05rem !important;
            padding: 0.75rem 1rem 0.72rem 1.1rem !important;
            border-left: 8px solid #8b5a2b !important;
            background: linear-gradient(180deg, rgba(255,255,255,0.56), rgba(204,213,220,0.36)) !important;
            border-radius: 12px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.8), 0 8px 18px rgba(45,57,69,0.08) !important;
        }
        /* --- ACCENT COLOR OVERRIDES (replaces default Streamlit orange) --- */
        :root {
            --accent: #3ba5b6;
            --accent-glow: rgba(59,165,182,0.35);
        }

        /* Primary / secondary buttons */
        [data-testid="baseButton-secondary"],
        [data-testid="baseButton-primary"] {
            background: #888 !important;
            background-image: linear-gradient(180deg, #d0d5da 0%, #8e959c 48%, #6a737b 100%) !important;
            border: 2px outset #b8bec4 !important;
            border-radius: 3px !important;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.55) !important;
            padding: 0.36rem 0.75rem !important;
        }

        [data-testid="baseButton-secondary"] *,
        [data-testid="baseButton-primary"] * {
            color: #0a0e13 !important;
            font-family: Tahoma, "MS Sans Serif", Verdana, sans-serif !important;
            font-weight: bold !important;
            text-transform: none !important;
            text-shadow: 0 1px 0 rgba(255,255,255,0.5) !important;
        }

        [data-testid="baseButton-secondary"]:hover,
        [data-testid="baseButton-primary"]:hover {
            background-image: linear-gradient(180deg, #dce1e5 0%, #9da5ad 48%, #78828b 100%) !important;
        }

        [data-testid="baseButton-secondary"]:active,
        [data-testid="baseButton-primary"]:active {
            border: 2px inset #b8bec4 !important;
            box-shadow: inset 1px 1px 3px rgba(0,0,0,0.55) !important;
            background-image: linear-gradient(180deg, #6a737b 0%, #8e959c 100%) !important;
        }

        /* Slider accent track */
        [data-baseweb="slider"] > div > div > div:nth-child(2) {
            background: linear-gradient(90deg, #9fe0ff 0%, var(--accent) 48%, #74d97a 100%) !important;
        }

        /* Slider thumb */
        [role="slider"] {
            background: linear-gradient(180deg, #fbfdff 0%, #c7d0d8 40%, #7b8792 100%) !important;
            border: 1px solid #55616c !important;
            border-color: #55616c !important;
        }

        /* Slider value text */
        [data-baseweb="slider"] [data-testid="stThumbValue"] {
            color: var(--accent) !important;
        }

        /* Radio button indicators */
        [data-testid="stRadio"] input[type="radio"]:checked + div {
            border-color: var(--accent) !important;
        }

        [data-testid="stRadio"] input[type="radio"]:checked + div::after {
            background-color: var(--accent) !important;
        }

        /* Checkbox checked state */
        [data-testid="stCheckbox"] [data-baseweb="checkbox"] input:checked + div {
            background-color: var(--accent) !important;
            border-color: var(--accent) !important;
        }

        /* Toggle switch */
        [data-testid="stToggle"] [data-baseweb="toggle"] > div {
            background-color: var(--accent) !important;
        }

        /* Link buttons (like Connect Spotify) */
        a[data-testid="baseLinkButton-secondary"] {
            background-image: linear-gradient(180deg, #d0d5da 0%, #8e959c 48%, #6a737b 100%) !important;
            border: 2px outset #b8bec4 !important;
            border-radius: 3px !important;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.55) !important;
        }

        a[data-testid="baseLinkButton-secondary"] * {
            color: #0a0e13 !important;
            font-family: Tahoma, "MS Sans Serif", Verdana, sans-serif !important;
            font-weight: bold !important;
            text-shadow: 0 1px 0 rgba(255,255,255,0.5) !important;
        }

        /* Select-slider option labels (remove orange highlight) */
        [data-baseweb="slider"] [role="slider"]::after {
            background-color: var(--accent) !important;
        }

        /* Focus rings */
        *:focus-visible {
            outline-color: var(--accent) !important;
        }
        /* --- ACCENT OVERRIDES END --- */

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
                <h1>Vibe Synthesizer</h1>
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


def render_module_intro(title: str, code: str, subtitle: str, knob_labels: list[str], jack_labels: list[str]):
    knob_markup = "".join(
        f'<div class="module-knob"><div class="module-knob-face"></div><span>{escape(label)}</span></div>'
        for label in knob_labels
    )
    jack_markup = "".join(
        f'<div class="module-jack"><div class="module-jack-hole"></div><span>{escape(label)}</span></div>'
        for label in jack_labels
    )
    st.markdown(
        (
            f'<div class="module-anchor"></div>'
            f'<div class="module-intro">'
            f'<div class="module-head">'
            f'<div>'
            f'<div class="module-legend"><span class="module-chip">voice active</span><span class="module-chip">analog path</span></div>'
            f'<div class="module-title">{escape(title)}</div>'
            f'<p class="module-subtitle">{escape(subtitle)}</p></div>'
            f'<div class="module-code">{escape(code)}</div>'
            f'</div>'
            f'<div class="module-hardware">'
            f'<div class="module-knob-cluster">{knob_markup}</div>'
            f'<div class="module-patch-row">{jack_markup}</div>'
            f'</div>'
            f'</div>'
        ),
        unsafe_allow_html=True,
    )


def render_module_footer(bus_label: str, live_leds: int = 2):
    leds = "".join(
        f'<div class="module-led{" live" if idx < live_leds else ""}"></div>'
        for idx in range(4)
    )
    st.markdown(
        (
            f'<div class="module-footer">'
            f'<div class="module-led-bank">{leds}</div>'
            f'<div class="module-bus">{escape(bus_label)}</div>'
            f'</div>'
        ),
        unsafe_allow_html=True,
    )


def render_control_bay_anchor():
    st.markdown('<div class="control-bay-anchor"></div>', unsafe_allow_html=True)


def main():
    demo_songs, study_rules = load_catalog()
    task_types = sorted({rule["task_type"] for rule in study_rules})
    focus_goals = sorted({rule["focus_goal"] for rule in study_rules})

    render_styles()
    render_player_header()

    active_songs = demo_songs
    source_label = "Demo catalog"
    source_notice = ""

    st.markdown("<h3 id='mix-console'>Mix Console // Vibe Synthesizer Rack</h3>", unsafe_allow_html=True)
    
    # Row 1: Source and Context
    row1_col1, row1_col2 = st.columns(2, gap="large")
    
    with row1_col1:
        with st.container(border=True):
            render_module_intro(
                "Module 1: Source Input",
                "SRC-01",
                "Import, route, and latch the active catalog before the chain starts.",
                ["Gain", "Cue", "Sync"],
                ["IN", "USB", "CLK", "ARM"],
            )
            with st.container(border=True):
                render_control_bay_anchor()
                if not spotify_is_configured():
                    st.warning(
                        "Spotify import is unavailable until the server is configured with "
                        "`SPOTIPY_CLIENT_ID` and an allowed redirect URI."
                    )
                else:
                    cache_handler = StreamlitSessionCacheHandler() if StreamlitSessionCacheHandler else None
                    auth_code = get_query_code()

                    # --- PKCE verifier persistence ---
                    # SpotifyPKCE generates a random code_verifier on every
                    # __init__.  Streamlit reruns (and hot-reloads) create new
                    # instances, losing the verifier that was used to build the
                    # auth URL.  We persist it to disk so it survives everything.
                    import json as _json
                    _PKCE_FILE = Path(__file__).parent / ".pkce_verifier.json"

                    from src.spotify_client import get_spotify_auth
                    auth_mgr = get_spotify_auth(cache_handler=cache_handler)

                    # Restore a previously-saved verifier, or save the new one
                    if _PKCE_FILE.exists():
                        try:
                            stored = _json.loads(_PKCE_FILE.read_text())
                            auth_mgr.code_verifier = stored["verifier"]
                            auth_mgr.code_challenge = stored["challenge"]
                        except Exception:
                            pass  # will regenerate below

                    def _save_pkce():
                        _PKCE_FILE.write_text(_json.dumps({
                            "verifier": auth_mgr.code_verifier,
                            "challenge": auth_mgr.code_challenge,
                        }))

                    if not st.session_state.get("spotify_songs"):
                        st.markdown('''<style>a[href^="https://accounts.spotify.com"] { background-color: #1DB954 !important; color: white !important; border: none !important; font-weight: bold !important; }</style>''', unsafe_allow_html=True)
                        if "spotify_auth_url" not in st.session_state:
                            st.session_state["spotify_auth_url"] = auth_mgr.get_authorize_url()
                            _save_pkce()  # save verifier that matches this URL
                        st.link_button("Connect Spotify", st.session_state["spotify_auth_url"])
                    if auth_code:
                        st.caption("Spotify authorization code detected.")
                    if st.button("Import Spotify tracks", use_container_width=True):
                        try:
                            import spotipy
                            auth_mgr.get_access_token(auth_code)
                            token_info = auth_mgr.validate_token(auth_mgr.cache_handler.get_cached_token())
                            if not token_info:
                                raise RuntimeError("Spotify login failed — please reconnect.")
                            sp = spotipy.Spotify(auth=token_info["access_token"])

                            from src.spotify_client import (
                                normalize_spotify_track,
                                _fetch_artist_genres,
                                classify_spotify_tracks,
                            )
                            imported = []
                            seen_ids = set()
                            top_items = sp.current_user_top_tracks(limit=25, time_range="medium_term").get("items", [])
                            recent_items = sp.current_user_recently_played(limit=25).get("items", [])
                            artist_genres = _fetch_artist_genres(sp, [*top_items, *recent_items])

                            for item in top_items:
                                sid = item.get("id")
                                if sid and sid not in seen_ids:
                                    seen_ids.add(sid)
                                    imported.append(normalize_spotify_track(item, "top_track", artist_genres, len(imported) + 1))
                            for item in recent_items:
                                track = item.get("track", item)
                                sid = track.get("id")
                                if sid and sid not in seen_ids:
                                    seen_ids.add(sid)
                                    imported.append(normalize_spotify_track(item, "recently_played", artist_genres, len(imported) + 1))

                            st.session_state["spotify_songs"] = classify_spotify_tracks(imported)
                            st.session_state["spotify_error"] = ""
                            st.query_params.clear()
                            # Clean up verifier file after successful exchange
                            _PKCE_FILE.unlink(missing_ok=True)
                        except Exception as exc:
                            st.session_state["spotify_songs"] = []
                            st.session_state["spotify_error"] = str(exc)

                    spotify_songs = st.session_state.get("spotify_songs", [])
                    spotify_error = st.session_state.get("spotify_error", "")
                    if spotify_songs:
                        st.success(f"Imported {len(spotify_songs)} Spotify tracks.")
                    elif spotify_error:
                        st.warning(f"Spotify import failed: {spotify_error}")

                source_options = ["Demo catalog"]
                if st.session_state.get("spotify_songs"):
                    source_options.append("Spotify import")
                    
                source_mode = st.radio(
                    "Signal Source",
                    source_options,
                    horizontal=True,
                    index=1 if st.session_state.get("spotify_songs") else 0,
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
            render_module_footer("Source Bus A", live_leds=1 if source_mode == "Demo catalog" else 3)

    with row1_col2:
        with st.container(border=True):
            genres = unique_values(active_songs, "genre")
            moods = unique_values(active_songs, "mood")

            render_module_intro(
                "Module 2: Context Modulators",
                "CTX-02",
                "Clock the session, target the task lane, and bias the retrieval envelope.",
                ["Task", "Focus", "Clock"],
                ["TASK", "GOAL", "BPM", "CV"],
            )
            with st.container(border=True):
                render_control_bay_anchor()
                task_type = st.selectbox("Task type", task_types, index=option_index(task_types, "coding"))
                focus_goal = st.selectbox("Focus goal", focus_goals, index=option_index(focus_goals, "deep focus"))
                session_minutes = st.slider("Session length", 15, 120, 45, step=5)
            render_module_footer("Context Bus B", live_leds=3)

    # Row 2: Vibe Synthesis and Filters
    row2_col1, row2_col2 = st.columns(2, gap="large")
    
    with row2_col1:
        with st.container(border=True):
            render_module_intro(
                "Module 3: Vibe Synthesis Engine",
                "SYN-03",
                "Blend oscillator mood, genre color, and energy drive into the scoring path.",
                ["A Tone", "B Tone", "Drive"],
                ["OSC A", "OSC B", "ENV", "MIX"],
            )
            with st.container(border=True):
                render_control_bay_anchor()
                synthesis_mode_options = {
                    "Auto (Driven by Context)": "auto",
                    "Balanced Mix": "balanced",
                    "Genre Priority": "genre_first",
                    "Mood Priority": "mood_first",
                    "Energy Override": "energy_focused",
                    "Resonance Tuning": "resonance",
                }
                synthesis_mode_label = st.selectbox("Synthesis Mode (Scorer algorithm)", list(synthesis_mode_options.keys()))
                synthesis_mode = synthesis_mode_options[synthesis_mode_label]
                
                preferred_genre = st.selectbox("Oscillator A: Genre", genres, index=option_index(genres, "lofi"))
                preferred_mood = st.selectbox("Oscillator B: Mood", moods, index=option_index(moods, "focused"))
                energy_mapping = {
                    "Sleepy": 0.1,
                    "Chill": 0.3,
                    "Balanced": 0.5,
                    "Upbeat": 0.7,
                    "Intense": 0.9
                }
                energy_feeling = st.select_slider("Main Energy Gain", options=list(energy_mapping.keys()), value="Chill")
                target_energy = energy_mapping[energy_feeling]
                # Resonance tuning parameter (used by ResonanceScorer)
                tuning_shift = 0.0
                if synthesis_mode == "resonance":
                    tuning_shift = st.slider(
                        "Resonance Tuning (energy shift)",
                        -0.3,
                        0.3,
                        0.0,
                        step=0.01,
                        help="Subtly shift the target energy to tune resonance behavior.",
                    )
                    st.caption(f"Tuning shift: {tuning_shift:+.2f}")
            render_module_footer("Synthesis Mix", live_leds=4)

    with row2_col2:
        with st.container(border=True):
            render_module_intro(
                "Module 4: Signal Filters & Outboard",
                "FLT-04",
                "Gate the final signal path with vocal, acoustic, explicit, and AI outboard switches.",
                ["Cutoff", "Bias", "Send"],
                ["AUX", "VOC", "AI", "OUT"],
            )
            with st.container(border=True):
                render_control_bay_anchor()
                col_a, col_b = st.columns(2)
                with col_a:
                    likes_acoustic = st.checkbox("Acoustic Pass", value=True)
                    allows_lyrics = st.checkbox("Vocal Pass (Lyrics)", value=False)
                with col_b:
                    allows_explicit = st.checkbox("Explicit Pass", value=False)
                    from src.llm_client import llm_is_available
                    use_llm = st.checkbox("Enable LLM Brain", value=llm_is_available())
            render_module_footer("Output Matrix", live_leds=2 + int(bool(use_llm and llm_is_available())))

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
        synthesis_mode=synthesis_mode,
        synthesis_params={"tuning_shift": tuning_shift} if 'tuning_shift' in locals() else None,
    )

    # Scale playlist size to fill the session using actual catalog durations
    total_seconds = sum(s.get("song_length_seconds", 210) for s in active_songs)
    avg_song_minutes = (total_seconds / len(active_songs) / 60) if active_songs else 3.5
    k = max(3, min(len(active_songs), round(session_minutes / avg_song_minutes)))

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Synthesize Playlist", type="primary", use_container_width=True):
        with st.spinner("Synthesizing vibe..."):
            st.session_state["playlist_result"] = build_study_playlist(
                request,
                active_songs,
                study_rules,
                k=k,
                use_llm=use_llm,
                model=os.getenv("AI_MODEL"),
            )

    if "playlist_result" not in st.session_state:
        st.info("Configure your modules above and click **Synthesize Playlist** to generate your mix.")
        return

    result = st.session_state["playlist_result"]
    retrieval = result["retrieval"]
    playlist = result["playlist"]
    metric_cols = st.columns(3)
    metric_cols[0].metric("Retrieved Songs", len(retrieval["retrieved_songs"]))
    metric_cols[1].metric("Catalog Source", source_label)
    metric_cols[2].metric("AI Mode", "LLM" if use_llm and llm_is_available() else "Fallback")

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
