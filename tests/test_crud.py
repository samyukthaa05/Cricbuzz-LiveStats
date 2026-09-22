import pytest

from database.connection import initialize_database
from database.crud import (
    create_match,
    create_player,
    delete_match,
    delete_player,
    list_matches,
    list_players,
    list_teams,
    list_venues,
    update_match,
    update_player,
)


@pytest.fixture(autouse=True)
def database():
    initialize_database()


def test_player_validation_rejects_blank_name():
    with pytest.raises(ValueError):
        create_player({
            "full_name": "",
            "role": "Batsman",
            "batting_style": "Right-hand",
            "bowling_style": "None",
            "country": "India",
            "team_id": 1,
        })


def test_create_and_update_player():
    player_id = create_player({
        "full_name": "Test Batter",
        "role": "Batsman",
        "batting_style": "Right-hand",
        "bowling_style": "None",
        "country": "India",
        "team_id": 1,
    })
    assert any(row["player_id"] == player_id for _, row in list_players("Test Batter").iterrows())

    update_player(player_id, {
        "full_name": "Updated Batter",
        "role": "Batsman",
        "batting_style": "Left-hand",
        "bowling_style": "None",
        "country": "India",
        "team_id": 1,
    })
    assert not list_players("Updated Batter").empty


def test_create_and_update_and_delete_match():
    # Validation check: same team rejected
    with pytest.raises(ValueError):
        create_match({
            "description": "Invalid Derby",
            "match_date": "2026-09-21",
            "format": "T20I",
            "status": "scheduled",
            "venue_id": 1,
            "series_id": None,
            "team_a_id": 1,
            "team_b_id": 1,
        })

    match_id = create_match({
        "description": "Pytest Final Match",
        "match_date": "2026-09-21",
        "format": "ODI",
        "status": "scheduled",
        "venue_id": 1,
        "series_id": 1,
        "team_a_id": 1,
        "team_b_id": 2,
    })
    assert match_id > 0

    # Read
    matches_df = list_matches("Pytest Final Match")
    assert not matches_df.empty

    # Update
    update_match(match_id, {
        "description": "Pytest Final Match Completed",
        "match_date": "2026-09-21",
        "format": "ODI",
        "status": "completed",
        "venue_id": 1,
        "series_id": 1,
        "team_a_id": 1,
        "team_b_id": 2,
        "winner_team_id": 1,
        "victory_margin": 50,
        "victory_type": "runs",
        "toss_winner_id": 1,
        "toss_decision": "bat",
    })
    updated_df = list_matches("Pytest Final Match Completed")
    assert not updated_df.empty
    assert updated_df.iloc[0]["status"] == "completed"

    # Delete
    delete_match(match_id)
    assert list_matches("Pytest Final Match Completed").empty