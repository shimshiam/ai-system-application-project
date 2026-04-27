# Reflection on Recommendation Profiles

- Party Mode vs Study Session
  - Party Mode wants happy pop with high energy and electronic sound, so its top results are bright pop songs with strong energy. Study Session wants chill lofi and low energy acoustic sound, so its top results shift to mellow lofi tracks. This makes sense because the model is rewarding both the genre/mood match and the closeness of song energy to the target.

- Gym Grinder vs Conflicted Pop Fan
  - Gym Grinder is clearly looking for metal/aggressive and very high energy, so the top results are hard-driving metal and electronic tracks. Conflicted Pop Fan wants pop and sad mood, but the output still includes Gym Hero because it is pop and also very close to the requested high energy. That shows the model is still letting energy push songs into the top results even when the mood is not a perfect match.

- Evening Wind-Down vs Road Trip
  - Evening Wind-Down prefers blues, soulful, mid-low energy, and acoustic sound, so its recommendations move toward warm, relaxed songs. Road Trip prefers hip-hop, confident mood, high energy, and electronic production, so its top results are more upbeat and punchy. The difference is exactly what these two profiles are testing: one is about calm, acoustic relaxation and the other is about driving energy.

- No Good Match vs Impossible Energy
  - No Good Match asks for a genre/mood combo that is not well represented, so the system picks songs that are close in mood or energy rather than exact. Impossible Energy asks for energy outside the normal range, so it ends up ranking songs mostly by available energy closeness and genre match, demonstrating that the model struggles when the target is extreme. This comparison shows the limitation of the scoring formula for rare or out-of-range preferences.
