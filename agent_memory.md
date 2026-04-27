# Agent Memory

This file is a shared working memory for planning, project context, decisions, and reflection. It should be updated as the project direction becomes clearer.

## Current Project Context

- Project: Music Recommender Simulation.
- Core goal: Recommend songs from a small catalog using content-based filtering.
- Main data source: `data/songs.csv`.
- Main logic: `src/recommender.py`.
- Main runner: `src/main.py`.
- Tests: `tests/test_recommender.py`.
- Documentation: `README.md`, `model_card.md`, `reflection.md`, and `docs/data-flow.md`.
- Assets directory: `assets/`, intended for system architecture images and screenshots.

## Current Status

- The recommender loads a catalog of songs, scores each song against a user profile, sorts results by score, and returns top recommendations.
- The project currently supports multiple scoring strategies:
  - Balanced
  - Genre-first
  - Mood-first
  - Energy-focused
- The README includes formatted screenshot/image sections.
- The selected next direction is RAG Study DJ: a study playlist assistant that retrieves song data and task-specific study rules before generating a playlist plan.

## Future Plan

Implement and refine the RAG Study DJ app.

Current implementation target:

- Use `data/songs.csv` and `data/study_rules.csv` as the retrieved knowledge sources.
- Use `src/study_dj.py` for the RAG pipeline, fallback planner, and optional OpenAI generation.
- Use `streamlit_app.py` as the main user-facing app.
- Keep `src/main.py` runnable for the original CLI demo.

Detailed next steps:

1. Verify tests after dependencies are installed.
2. Manually run the Streamlit app with `streamlit run streamlit_app.py`.
3. Confirm changing task type changes retrieved rules and playlist output.
4. Consider moving root screenshot files into `assets/` after the app work is stable.

Completion criteria:

- The app retrieves relevant songs and study rules.
- The generated playlist uses only retrieved songs.
- The app works without an API key using deterministic fallback planning.
- The app can use OpenAI generation when `OPENAI_API_KEY` is configured.

## Retained Decisions

- Keep project changes scoped and readable.
- Use `assets/` for architecture diagrams, screenshots, and other visual project files.
- Do not assume a new product direction until one is explicitly chosen.

## Observations And Possible Improvements

- `src/recommender.py` has duplicated scoring logic across the different strategy classes.
- The project uses both dictionary-based song data and dataclass-based song data, which could be unified later.
- `docs/data-flow.md` may need updates if scoring weights change.
- User energy values are expected to be between `0.0` and `1.0`, but the current examples include an out-of-range test profile.
- `pytest` is listed in `requirements.txt`, but it was not installed in the active shell environment during the last check.
- `openai` and `tabulate` are now listed in `requirements.txt` for the AI app and formatted CLI output.

## Reflection Notes

- Simple scoring weights have a large effect on recommendation behavior.
- Energy weighting currently has a strong influence on rankings.
- Future project direction should decide whether this stays a classroom simulation or becomes a more polished app/tool.

## Open Questions

- Should the next phase focus on code cleanup, documentation, UI, testing, or model behavior?
- Should screenshots currently in the project root be moved into `assets/`?
- Should the recommender use one consistent data model instead of both dictionaries and dataclasses?
- Should the scoring strategy system be simplified into configurable weights?
- Should the Streamlit app later support user-uploaded notes as an additional RAG source?
