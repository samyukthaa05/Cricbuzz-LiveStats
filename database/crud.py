"""Validated CRUD operations used by the admin page and tests."""

from __future__ import annotations

from typing import Any
import pandas as pd

from database.connection import execute, get_connection, query_df
from utils.validation import validate_match, validate_player


# ---------------------------------------------------------------------------
# Players CRUD
# ---------------------------------------------------------------------------

def list_players(search: str = "") -> pd.DataFrame:
    pattern = f"%{search.strip()}%"
    return query_df(
        """SELECT p.player_id, p.full_name, p.role, p.batting_style, p.bowling_style,
        p.country, p.team_id, t.name AS team, p.active FROM players p JOIN teams t ON t.team_id=p.team_id
        WHERE p.full_name LIKE ? OR p.country LIKE ? OR p.role LIKE ? ORDER BY p.full_name""",
        (pattern, pattern, pattern),
    )


def list_teams() -> pd.DataFrame:
    return query_df("SELECT team_id, name, country, short_code FROM teams ORDER BY name")


def create_player(payload: dict[str, Any]) -> int:
    validate_player(payload)
    return execute(
        """INSERT INTO players(full_name, role, batting_style, bowling_style, country, team_id)
        VALUES (?,?,?,?,?,?)""",
        (
            payload["full_name"].strip(),
            payload["role"],
            payload["batting_style"].strip(),
            payload["bowling_style"].strip(),
            payload["country"].strip(),
            int(payload["team_id"]),
        ),
    )


def update_player(player_id: int, payload: dict[str, Any]) -> int:
    validate_player(payload)
    return execute(
        """UPDATE players SET full_name=?, role=?, batting_style=?, bowling_style=?, country=?, team_id=?
        WHERE player_id=?""",
        (
            payload["full_name"].strip(),
            payload["role"],
            payload["batting_style"].strip(),
            payload["bowling_style"].strip(),
            payload["country"].strip(),
            int(payload["team_id"]),
            player_id,
        ),
    )


def delete_player(player_id: int) -> None:
    with get_connection() as connection:
        references = connection.execute(
            "SELECT COUNT(*) FROM batting_performances WHERE player_id=?", (player_id,)
        ).fetchone()[0]
        references += connection.execute(
            "SELECT COUNT(*) FROM bowling_performances WHERE player_id=?", (player_id,)
        ).fetchone()[0]
        if references:
            raise ValueError(
                "This player has performance history and cannot be deleted. Mark them inactive instead."
            )
        connection.execute("DELETE FROM players WHERE player_id=?", (player_id,))
        connection.commit()


def update_player_active(player_id: int, active: bool) -> None:
    execute("UPDATE players SET active=? WHERE player_id=?", (1 if active else 0, player_id))


# ---------------------------------------------------------------------------
# Matches CRUD
# ---------------------------------------------------------------------------

def list_venues() -> pd.DataFrame:
    return query_df("SELECT venue_id, name, city, country, capacity FROM venues ORDER BY name")


def list_series() -> pd.DataFrame:
    return query_df("SELECT series_id, name, host_country, match_type, start_date FROM series ORDER BY start_date DESC")


def list_matches(search: str = "", limit: int = 50) -> pd.DataFrame:
    pattern = f"%{search.strip()}%"
    return query_df(
        """SELECT m.match_id, m.description, m.match_date, m.format, m.status,
        ta.name AS team_a, tb.name AS team_b, COALESCE(w.name, 'No Result') AS winner,
        m.victory_margin, m.victory_type, v.name AS venue, v.city
        FROM matches m
        JOIN teams ta ON ta.team_id = m.team_a_id
        JOIN teams tb ON tb.team_id = m.team_b_id
        JOIN venues v ON v.venue_id = m.venue_id
        LEFT JOIN teams w ON w.team_id = m.winner_team_id
        WHERE m.description LIKE ? OR ta.name LIKE ? OR tb.name LIKE ? OR v.name LIKE ?
        ORDER BY m.match_date DESC
        LIMIT ?""",
        (pattern, pattern, pattern, pattern, limit),
    )


def create_match(payload: dict[str, Any]) -> int:
    validate_match(payload)
    return execute(
        """INSERT INTO matches (
            description, match_date, format, status, venue_id, series_id,
            team_a_id, team_b_id, winner_team_id, victory_margin, victory_type,
            toss_winner_id, toss_decision
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            payload["description"].strip(),
            str(payload["match_date"]),
            payload["format"],
            payload["status"],
            int(payload["venue_id"]),
            int(payload["series_id"]) if payload.get("series_id") else None,
            int(payload["team_a_id"]),
            int(payload["team_b_id"]),
            int(payload["winner_team_id"]) if payload.get("winner_team_id") else None,
            int(payload.get("victory_margin") or 0),
            payload.get("victory_type") or None,
            int(payload["toss_winner_id"]) if payload.get("toss_winner_id") else None,
            payload.get("toss_decision") or None,
        ),
    )


def update_match(match_id: int, payload: dict[str, Any]) -> int:
    validate_match(payload)
    return execute(
        """UPDATE matches SET
            description = ?, match_date = ?, format = ?, status = ?,
            venue_id = ?, series_id = ?, team_a_id = ?, team_b_id = ?,
            winner_team_id = ?, victory_margin = ?, victory_type = ?,
            toss_winner_id = ?, toss_decision = ?
        WHERE match_id = ?""",
        (
            payload["description"].strip(),
            str(payload["match_date"]),
            payload["format"],
            payload["status"],
            int(payload["venue_id"]),
            int(payload["series_id"]) if payload.get("series_id") else None,
            int(payload["team_a_id"]),
            int(payload["team_b_id"]),
            int(payload["winner_team_id"]) if payload.get("winner_team_id") else None,
            int(payload.get("victory_margin") or 0),
            payload.get("victory_type") or None,
            int(payload["toss_winner_id"]) if payload.get("toss_winner_id") else None,
            payload.get("toss_decision") or None,
            match_id,
        ),
    )


def delete_match(match_id: int) -> None:
    with get_connection() as connection:
        # Cascades to innings, batting, bowling, fielding, partnerships
        connection.execute("DELETE FROM matches WHERE match_id = ?", (match_id,))
        connection.commit()