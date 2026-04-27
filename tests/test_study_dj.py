from src.recommender import load_songs
from src.study_dj import (
    StudyDJRequest,
    build_study_playlist,
    default_data_paths,
    generate_fallback_playlist_plan,
    load_study_rules,
    retrieve_candidate_songs,
    retrieve_context,
    retrieve_study_rules,
)


def make_request(**overrides):
    data = {
        "task_type": "coding",
        "session_minutes": 45,
        "focus_goal": "deep focus",
        "preferred_genre": "lofi",
        "preferred_mood": "focused",
        "target_energy": 0.4,
        "likes_acoustic": True,
        "allows_lyrics": False,
        "allows_explicit": False,
    }
    data.update(overrides)
    return StudyDJRequest(**data)


def load_fixture_data():
    paths = default_data_paths()
    return load_songs(str(paths["songs"])), load_study_rules(str(paths["study_rules"]))


def test_retrieve_study_rules_selects_task_and_focus_goal():
    _, rules = load_fixture_data()
    request = make_request(task_type="coding", focus_goal="deep focus")

    matches = retrieve_study_rules(request, rules)

    assert matches[0]["task_type"] == "coding"
    assert matches[0]["focus_goal"] == "deep focus"


def test_song_retrieval_uses_scores_and_returns_best_matching_study_track():
    songs, rules = load_fixture_data()
    request = make_request()
    retrieved_rules = retrieve_study_rules(request, rules)

    matches = retrieve_candidate_songs(request, songs, retrieved_rules, k=3)

    assert matches
    assert matches[0]["song"]["title"] == "Focus Flow"
    assert matches[0]["score"] >= matches[-1]["score"]


def test_explicit_tracks_are_excluded_when_not_allowed():
    songs, rules = load_fixture_data()
    request = make_request(
        task_type="review",
        focus_goal="light focus",
        preferred_genre="hip-hop",
        preferred_mood="confident",
        allows_lyrics=True,
        allows_explicit=False,
        target_energy=0.8,
        likes_acoustic=False,
    )
    context = retrieve_context(request, songs, rules, k=10)

    assert all(item["song"]["explicit"] == 0 for item in context["retrieved_songs"])
    assert "Concrete Jungle" not in {
        item["song"]["title"] for item in context["retrieved_songs"]
    }


def test_fallback_plan_is_complete_and_uses_only_retrieved_songs():
    songs, rules = load_fixture_data()
    request = make_request()
    context = retrieve_context(request, songs, rules, k=4)

    plan = generate_fallback_playlist_plan(request, context)

    retrieved_titles = {item["song"]["title"] for item in context["retrieved_songs"]}
    planned_titles = {track["title"] for track in plan["ordered_tracks"]}
    assert plan["summary"]
    assert plan["study_strategy"]
    assert planned_titles <= retrieved_titles
    assert all(source.startswith(("song:", "rule:")) for source in plan["source_context_used"])


def test_main_pipeline_integrates_retrieval_and_generation_without_api():
    songs, rules = load_fixture_data()
    request = make_request()

    result = build_study_playlist(request, songs, rules, k=3, use_llm=False)

    assert result["retrieval"]["retrieved_songs"]
    assert result["playlist"]["ordered_tracks"]
    retrieved_titles = {
        item["song"]["title"] for item in result["retrieval"]["retrieved_songs"]
    }
    assert {
        track["title"] for track in result["playlist"]["ordered_tracks"]
    } <= retrieved_titles
