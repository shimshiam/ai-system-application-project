# Reflection: Building the Vibe Synthesizer

### Limitations and Biases
One big limitation is that the system is only as good as the metadata it gets from Spotify. If an artist's genre is tagged incorrectly or if a track has a weird energy rating, the engine might throw it into a playlist where it doesn't belong. There's also a bit of a bias in the study rules—they reflect my own idea of what "focus" sounds like. Someone who studies better with high-energy metal might find the system too restrictive.

### Misuse and Prevention
The main way this could be misused is by someone trying to use it as a generic "playlist generator" to bypass the intended focus-based goal. Even if the LLM wants to get creative, the "Hallucination Guard" and the deterministic fallback ensure that the tracks actually match the study strategy. Also, using the PKCE flow means I'm not storing any user secrets, which keeps the integration secure.

### Testing Surprises
During testing, I noticed that the high-energy tracks almost always won. It made the playlists feel too intense too fast. I had to build the "Resonance Scorer" to basically say, "if the vibe is supposed to be chill, don't just pick the loudest track".

### AI Collaboration
Working with different AI models was a big part of the process. A mix of a massive speed boost and some occasional debugging.

*   **The Good**: **Claude** was a lifesaver when it came to security. It was the one that pushed me to use the Spotify PKCE flow and fix a major key leak. **Codex** was also a huge help with the complex skeuomorphic CSS for the "Mix Console."
*   **The Bad**: Earlier in the project, **Gemini Pro** helped me get the initial Spotify integration running, but it suggested hardcoding the Client Secret directly in the source code. It was super easy to set up, but it was a massive security hole that I had to go back and patch later. 
*   **The Lesson**: The recent `KeyError` I hit in the pacing note logic was another reminder that even if an AI refactor looks clean and elegant, you still have to verify the data plumbing before you ship.
