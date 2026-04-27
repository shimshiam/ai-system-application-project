# Agent Memory

This file is a shared working memory for planning, project context, decisions, and reflection. It should be updated as the project direction becomes clearer.

## Current Project Context

- Project: Music Recommender Simulation (RAG Study DJ).
- Core goal: Recommend songs from a catalog and study rules using content-based filtering and RAG principles.
- Main data sources: `data/songs.csv`, `data/study_rules.csv`, and user-imported Spotify tracks.
- Main logic: `src/study_dj.py` (RAG pipeline) and `src/spotify_client.py` (Spotify PKCE Integration).
- Main runner: `streamlit_app.py` for the web UI, `src/main.py` for the CLI.
- Tests: `tests/test_recommender.py`.
- Documentation: `README.md`, `model_card.md`, `reflection.md`, and `docs/data-flow.md`.
- Assets directory: `assets/`, intended for system architecture images and screenshots.

## Current Status

- The Streamlit app (`streamlit_app.py`) has been fully styled with a custom 2000s metallic hardware aesthetic. Recent CSS fixes ensure that all text (including buttons, alerts, and labels) is readable regardless of the user's Streamlit dark/light theme setting.
- The Spotify Integration is active and uses the PKCE flow (`spotipy.oauth2.SpotifyPKCE`), which requires only a `SPOTIPY_CLIENT_ID` and a `SPOTIPY_REDIRECT_URI` (no client secret is needed). The `as_dict` error has been patched for compatibility with newer `spotipy` versions.
- The app supports fallback deterministic planning or OpenAI generation if `OPENAI_API_KEY` is provided.

## Future Plan

Refine and stabilize the RAG Study DJ app based on user feedback.

Detailed next steps:

1. Move root screenshot files (`image-1.png`, etc.) into `assets/` to clean up the root directory.
2. Expand the `SpotifyPKCE` integration if more features (like saving playlists back to Spotify) are requested.
3. Enhance the OpenAI prompt for generating better playlist plans.

Completion criteria:

- The app reliably builds a focused study playlist using local demo tracks or user-imported Spotify tracks.
- The user interface maintains a cohesive, highly-styled metallic theme without visual bugs.

## Agent Code Review Protocol

All future agents must strictly follow these protocols when reviewing or modifying the codebase:

1. **Spotify API Guidelines**:
   - **OpenAPI Schema**: Always refer to the Spotify OpenAPI spec for schema and endpoints. Do not guess endpoints or field names.
   - **Authorization**: Strictly use the Authorization Code with PKCE flow for user data (never use Implicit Grant). Client Credentials are only for public data.
   - **Redirect URIs**: Always use HTTPS redirect URIs (except `http://127.0.0.1` for local development).
   - **Scopes**: Request only the minimum scopes needed. No broad preemptive scopes.
   - **Tokens**: Manage securely. Never expose the Client Secret. Ensure token refresh logic is robust.
   - **Rate Limits**: Implement exponential backoff for HTTP 429 rate limit responses.
   - **Deprecated Endpoints**: Prefer modern endpoints (e.g., `/playlists/{id}/items` over `/playlists/{id}/tracks`).
   - **Error Handling**: Handle all HTTP error codes and relay meaningful feedback to the user.
2. **UI & CSS Theme Integrity**:
   - The application relies heavily on specific structural CSS overrides to mimic a physical 2000s mixer. When modifying `streamlit_app.py`, ensure new widgets are properly wrapped or targeted (e.g. using `nth-of-type` or `:has()`) so they match the metallic style and remain readable.
3. **Dependency Compatibility**:
   - Verify library updates (like `spotipy` or `streamlit`) do not break existing method signatures or standard DOM test IDs.
4. **General Practices**:
   - Preserve existing documentation and docstrings unless explicitly told otherwise.
   - Do not assume new product directions unless explicitly guided by the user.

## Retained Decisions

- Keep project changes scoped and readable.
- Use `assets/` for architecture diagrams, screenshots, and other visual project files.
- The Spotify integration will exclusively use the PKCE flow to avoid exposing client secrets in a client-side Streamlit application context.

## Observations And Possible Improvements

- `src/recommender.py` has duplicated scoring logic across the different strategy classes.
- The project uses both dictionary-based song data and dataclass-based song data, which could be unified later.
- `docs/data-flow.md` may need updates if scoring weights change.

## Reflection Notes

- Simple scoring weights have a large effect on recommendation behavior.
- Energy weighting currently has a strong influence on rankings.
- The custom CSS required a highly specific structural targeting approach due to changes in Streamlit's container DOM generation.

## Open Questions

- Should the recommender use one consistent data model instead of both dictionaries and dataclasses?
- Should the Streamlit app later support user-uploaded notes as an additional RAG source?
- Are we ready to implement token refresh logic or rate limit backoffs for the Spotify API?
