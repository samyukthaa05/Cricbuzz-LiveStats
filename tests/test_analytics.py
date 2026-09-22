from analytics.form_analysis import recent_form
from analytics.match_analytics import recent_matches, toss_advantage
from analytics.player_analytics import batting_leaderboard, bowling_leaderboard, get_player_summary
from database.connection import initialize_database, query_df
from database.seed import seed
from sql.query_metadata import QUERIES


def setup_module():
    initialize_database()
    seed()


def test_queries_catalogue_has_25_questions():
    assert len(QUERIES) == 25
    beginner = [q for q in QUERIES if q.difficulty == "Beginner"]
    intermediate = [q for q in QUERIES if q.difficulty == "Intermediate"]
    advanced = [q for q in QUERIES if q.difficulty == "Advanced"]
    assert len(beginner) == 8
    assert len(intermediate) == 8
    assert len(advanced) == 9


def test_all_25_queries_execute_with_results():
    for item in QUERIES:
        result = query_df(item.sql)
        assert list(result.columns), f"Q{item.number} returned no columns"
        assert len(result) > 0, f"Q{item.number} returned 0 rows"


def test_analytics_helpers():
    summary = get_player_summary()
    assert summary["players"] > 0
    assert summary["matches"] > 0

    batting = batting_leaderboard("All")
    assert not batting.empty
    assert "player" in batting.columns
    assert "runs" in batting.columns

    bowling = bowling_leaderboard("All")
    assert not bowling.empty
    assert "player" in bowling.columns
    assert "wickets" in bowling.columns

    recent = recent_matches(5)
    assert len(recent) <= 5

    toss = toss_advantage()
    assert not toss.empty

    form = recent_form()
    assert not form.empty