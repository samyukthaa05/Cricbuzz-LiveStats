"""User-input validation shared by Streamlit forms and tests."""

from __future__ import annotations

from typing import Any


ROLES = ("Batsman", "Bowler", "All-rounder", "Wicket-keeper")
FORMATS = ("Test", "ODI", "T20I")
MATCH_STATUSES = ("completed", "live", "scheduled")
VICTORY_TYPES = ("runs", "wickets", "draw", "tie")
TOSS_DECISIONS = ("bat", "bowl")


def validate_player(payload: dict[str, Any]) -> None:
    required = ("full_name", "role", "batting_style", "bowling_style", "country", "team_id")
    missing = [field for field in required if payload.get(field) in (None, "")]
    if missing:
        raise ValueError(f"Complete these fields: {', '.join(missing)}")
    if payload["role"] not in ROLES:
        raise ValueError("Select a valid playing role.")
    if len(str(payload["full_name"]).strip()) < 2:
        raise ValueError("Player name must contain at least two characters.")
    try:
        if int(payload["team_id"]) <= 0:
            raise ValueError
    except (TypeError, ValueError) as exc:
        raise ValueError("Select a valid team.") from exc


def validate_match(payload: dict[str, Any]) -> None:
    required = ("description", "match_date", "format", "status", "venue_id", "team_a_id", "team_b_id")
    missing = [field for field in required if payload.get(field) in (None, "")]
    if missing:
        raise ValueError(f"Complete these match fields: {', '.join(missing)}")
    if payload["format"] not in FORMATS:
        raise ValueError(f"Format must be one of {FORMATS}")
    if payload["status"] not in MATCH_STATUSES:
        raise ValueError(f"Status must be one of {MATCH_STATUSES}")
    if int(payload["team_a_id"]) == int(payload["team_b_id"]):
        raise ValueError("Team A and Team B cannot be the same team.")