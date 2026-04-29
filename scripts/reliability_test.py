import sys
import os
from pathlib import Path
from dataclasses import asdict

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.recommender import load_songs
from src.study_dj import (
    StudyDJRequest,
    build_study_playlist,
    default_data_paths,
    load_study_rules
)

def run_reliability_suite():
    print("====================================================")
    print(" VIBE SYNTHESIZER: RELIABILITY & FIDELITY REPORT")
    print("====================================================\n")

    paths = default_data_paths()
    songs = load_songs(str(paths["songs"]))
    rules = load_study_rules(str(paths["study_rules"]))

    test_cases = [
        {
            "name": "Deep Focus (Coding)",
            "params": {
                "task_type": "coding",
                "focus_goal": "deep focus",
                "preferred_genre": "ambient",
                "target_energy": 0.4
            }
        },
        {
            "name": "Light Review (Reading)",
            "params": {
                "task_type": "reading",
                "focus_goal": "light focus",
                "preferred_genre": "classical",
                "target_energy": 0.2
            }
        },
        {
            "name": "Creative Writing (Jazz)",
            "params": {
                "task_type": "writing",
                "focus_goal": "creative flow",
                "preferred_genre": "jazz",
                "target_energy": 0.5
            }
        }
    ]

    total_passed = 0
    
    for case in test_cases:
        print(f"Testing: {case['name']}...")
        request = StudyDJRequest(
            session_minutes=45,
            preferred_mood="focused",
            likes_acoustic=True,
            allows_lyrics=False,
            allows_explicit=False,
            **case["params"]
        )

        try:
            # Run without LLM for deterministic reliability check
            result = build_study_playlist(request, songs, rules, k=5, use_llm=False)
            
            playlist = result["playlist"]
            retrieved = result["retrieval"]["retrieved_songs"]
            
            # 1. Check for playlist generation
            gen_ok = len(playlist["ordered_tracks"]) > 0
            
            # 2. Check for Hallucination Guard (all tracks must be in retrieval)
            retrieved_ids = {item["song"]["spotify_id"] for item in retrieved if "spotify_id" in item["song"]}
            retrieved_titles = {item["song"]["title"] for item in retrieved}
            
            hallucination_free = True
            for track in playlist["ordered_tracks"]:
                if "spotify_id" in track and track["spotify_id"]:
                    if track["spotify_id"] not in retrieved_ids:
                        hallucination_free = False
                elif track["title"] not in retrieved_titles:
                    hallucination_free = False

            # 3. Calculate average score of selected tracks
            # In non-LLM mode, they should be the top-k scored tracks
            avg_score = sum(item["score"] for item in retrieved[:len(playlist["ordered_tracks"])]) / len(playlist["ordered_tracks"])

            if gen_ok and hallucination_free:
                status = "PASS"
                total_passed += 1
            else:
                status = "FAIL"

            print(f"  Status:       {status}")
            print(f"  Fidelity:     {'100% Grounded' if hallucination_free else 'Hallucinations detected'}")
            print(f"  Vibe Match:   {avg_score:.2f} (avg score)")
            print(f"  Pacing Notes: {len(playlist['ordered_tracks'])} generated\n")

        except Exception as e:
            print(f"  Status:       CRITICAL FAIL")
            print(f"  Error:        {str(e)}\n")

    print("====================================================")
    print(f" FINAL SUMMARY: {total_passed}/{len(test_cases)} Test Cases Passed")
    print("====================================================")

if __name__ == "__main__":
    run_reliability_suite()
