# Data Flow: From User Preferences to Top Recommendations

## Written Map

### INPUT

Two data sources enter the system:

1. **songs.csv** (20 songs) -- loaded by `load_songs()` into a list of dictionaries.
   Each song carries: genre, mood, energy, acousticness (scored) + title, artist, id, tempo, valence, danceability (stored but not scored).

2. **User Preferences** (a dictionary) -- defined in `main.py`.
   Contains: genre, mood, energy (float target), likes_acoustic (bool).

### PROCESS (The Loop)

`recommend_songs()` iterates through every song in the list.
For each song, it calls `score_song(user_prefs, song)` which runs four checks:

```
For song #1 (Sunrise City):
  Check 1: Does song.genre == user.genre?       pop == pop  --> YES --> +2.0 pts
  Check 2: Does song.mood == user.mood?          happy == happy --> YES --> +1.0 pt
  Check 3: Energy closeness                      1.0 - |0.80 - 0.82| = 0.98 --> +0.98 pts
  Check 4: Acoustic fit (user likes electronic)  0.5 * (1.0 - 0.18) = 0.41 --> +0.41 pts
  TOTAL = 4.39 pts

For song #2 (Midnight Coding):
  Check 1: Does song.genre == user.genre?        lofi == pop --> NO  --> +0.0 pts
  Check 2: Does song.mood == user.mood?           chill == happy --> NO --> +0.0 pts
  Check 3: Energy closeness                       1.0 - |0.80 - 0.42| = 0.62 --> +0.62 pts
  Check 4: Acoustic fit (user likes electronic)   0.5 * (1.0 - 0.71) = 0.15 --> +0.15 pts
  TOTAL = 0.77 pts

...repeat for all 20 songs...
```

Each song exits the loop as a tuple: (song_dict, score, explanation_string).

### OUTPUT (The Ranking)

After all 20 songs are scored:

1. **Sort** the full list by score, highest first.
2. **Slice** the top k results (default k=5).
3. **Return** the final list of (song, score, explanation) tuples.

```
Unsorted scores:                    Sorted + cut to k=5:
  Sunrise City      4.39              1. Sunrise City      4.39
  Midnight Coding   0.77              2. Gym Hero           3.35
  Storm Runner      1.34              3. Rooftop Lights     2.29
  Library Rain      0.70              4. Concrete Jungle    1.41
  Gym Hero          3.35      -->     5. Bass Cathedral     1.39
  Spacewalk         0.55              --- cut here (k=5) ---
  Coffee Shop       0.74              6-20: not returned
  Night Drive       1.34
  ...16 more...
```

---

## Mermaid.js Flowchart

```mermaid
flowchart TD
    subgraph INPUT ["INPUT"]
        CSV["songs.csv\n20 songs with:\ngenre, mood, energy,\nacousticness, title, ..."]
        UP["User Preferences\ngenre: pop\nmood: happy\nenergy: 0.80\nlikes_acoustic: false"]
    end

    LOAD["load_songs()\nParse CSV into\nlist of 20 song dicts"]
    CSV --> LOAD

    subgraph PROCESS ["PROCESS: The Scoring Loop"]
        direction TB
        LOOP["For each song in catalog...\n(repeats 20 times)"]

        subgraph SCORE ["score_song() — One Song at a Time"]
            direction TB
            G{"Genre match?\nsong.genre == user.genre"}
            G -- "YES" --> GP["+2.0 pts"]
            G -- "NO" --> GN["+0.0 pts"]

            M{"Mood match?\nsong.mood == user.mood"}
            M -- "YES" --> MP["+1.0 pt"]
            M -- "NO" --> MN["+0.0 pts"]

            E["Energy closeness\n1.0 - |user.energy - song.energy|"]
            EP["+0.00 to +1.00 pts"]
            E --> EP

            A{"Acoustic fit\nuser likes acoustic?"}
            A -- "YES" --> AY["+0.5 x song.acousticness"]
            A -- "NO" --> AN["+0.5 x (1 - song.acousticness)"]
        end

        SUM["Sum all points\nTotal = genre + mood + energy + acoustic\nMax possible: 4.5"]
        TUPLE["Create tuple:\n(song_dict, score, explanation)"]

        LOOP --> SCORE
        GP & GN & MP & MN & EP & AY & AN --> SUM
        SUM --> TUPLE
        TUPLE -- "next song" --> LOOP
    end

    LOAD --> LOOP
    UP --> LOOP

    subgraph OUTPUT ["OUTPUT: The Ranking"]
        direction TB
        SORT["Sort all 20 tuples\nby score descending"]
        SLICE["Slice top k\n(default k = 5)"]
        RESULT["Return final list:\n1. Sunrise City  4.39\n2. Gym Hero  3.35\n3. Rooftop Lights  2.29\n4. Concrete Jungle  1.41\n5. Bass Cathedral  1.39"]

        SORT --> SLICE --> RESULT
    end

    TUPLE --> SORT

    style INPUT fill:#e8f4f8,stroke:#2196F3,stroke-width:2px
    style PROCESS fill:#fff3e0,stroke:#FF9800,stroke-width:2px
    style SCORE fill:#fff8e1,stroke:#FFC107,stroke-width:1px
    style OUTPUT fill:#e8f5e9,stroke:#4CAF50,stroke-width:2px
```
