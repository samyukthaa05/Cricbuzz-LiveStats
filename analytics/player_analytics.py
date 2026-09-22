"""Reusable player analytics queries."""

from __future__ import annotations

import pandas as pd

from database.connection import query_df


def get_player_summary() -> dict[str, int]:
    counts = query_df("SELECT (SELECT COUNT(*) FROM players) players, (SELECT COUNT(*) FROM matches) matches")
    return {key: int(counts.iloc[0][key]) for key in ("players", "matches")}


def batting_leaderboard(format_name: str = "All") -> pd.DataFrame:
    where = "" if format_name == "All" else "WHERE m.format = ?"
    params = () if not where else (format_name,)
    return query_df(f"""SELECT p.full_name AS player, p.country, SUM(b.runs_scored) AS runs,
        ROUND(CAST(SUM(b.runs_scored) AS REAL)/NULLIF(COUNT(DISTINCT m.match_id),0),2) AS average_runs,
        ROUND(CAST(SUM(b.runs_scored) AS REAL)*100/NULLIF(SUM(b.balls_faced),0),2) AS strike_rate
        FROM batting_performances b JOIN players p ON p.player_id=b.player_id
        JOIN innings i ON i.innings_id=b.innings_id JOIN matches m ON m.match_id=i.match_id
        {where} GROUP BY p.player_id ORDER BY runs DESC LIMIT 10""", params)


def bowling_leaderboard(format_name: str = "All") -> pd.DataFrame:
    where = "" if format_name == "All" else "WHERE m.format = ?"
    params = () if not where else (format_name,)
    return query_df(f"""SELECT p.full_name AS player, p.country, SUM(b.wickets_taken) AS wickets,
        ROUND(CAST(SUM(b.runs_conceded) AS REAL)/NULLIF(SUM(b.overs),0),2) AS economy_rate
        FROM bowling_performances b JOIN players p ON p.player_id=b.player_id
        JOIN innings i ON i.innings_id=b.innings_id JOIN matches m ON m.match_id=i.match_id
        {where} GROUP BY p.player_id ORDER BY wickets DESC LIMIT 10""", params)