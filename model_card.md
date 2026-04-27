# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**EnergyMatch Recommender 1.0**

---

## 2. Intended Use

This recommender suggests songs from a small catalog based on a user's favorite genre, mood, energy level, and acoustic preference. It is meant for classroom exploration and testing ideas, not for a real music service. The system assumes the user has a single genre and mood they want right now.

---

## 3. How the Model Works

The model compares each song to the user's tastes and gives points for matching features. It gives points for exact genre and mood matches, and extra points when song energy is close to the user's target. Acoustic songs get a small bonus if the user likes acoustic sound. The final score is the sum of these bonuses, and songs are ranked by that score.

---

## 4. Data

The dataset is a small catalog of 20 songs in `data/songs.csv`. It includes genres like pop, lofi, rock, metal, jazz, hip-hop, electronic, and more. Each song also has mood labels, energy, tempo, valence, danceability, and acousticness. The dataset is limited because it only has one mood and one genre per song, and it does not represent every possible listening style.

---

## 5. Strengths

The system works well when the user wants a clear genre and mood, such as happy pop or chill lofi. It can also surface good matches when a song is very close in energy to the user's target. The scoring is easy to understand, so it is useful for learning how recommendation logic works.

---

## 6. Limitations and Bias

The current scoring system can create a strong filter bubble by over-prioritizing songs with energy close to the user target. This means users with niche or extreme energy preferences may still see recommendations dominated by a small set of songs, even if the genre or mood is not a great fit. The model also treats genre and mood as exact matches only, so similar genres like pop and indie pop or related moods like chill and relaxed get no partial credit. That causes the system to ignore a lot of reasonable alternatives in the catalog and can leave some user profiles with weaker results.

---

## 7. Evaluation

I tested profiles like Party Mode, Study Session, Gym Grinder, Conflicted Pop Fan, Evening Wind-Down, Road Trip, Impossible Energy, and No Good Match. I compared the top songs for each profile and checked whether they matched the desired genre, mood, energy, and acoustic feeling. It was surprising how often energy closeness could push a song into the top list even if the mood was not a perfect match. The Gym Hero example showed that a song can still rank high for happy pop listeners because it is pop and close to the requested high energy.

---

## 8. Future Work

- Add partial credit for similar genres and moods so related songs can count.
- Use a softer energy gap so extreme or unusual targets do not drop all songs to zero.
- Add a diversity penalty so the top list does not repeat the same style too much.

---

## 9. Personal Reflection

I learned that simple recommendation logic can still be useful but it can also be biased by how points are weighted. It was interesting to see how energy became more important when I changed the score rules. This made me realize real music recommenders need to balance many factors.
