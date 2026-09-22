"""Match-level analytics helpers."""

from __future__ import annotations

from database.connection import query_df


def recent_matches(limit: int = 20):
    return query_df("""SELECT m.description, ta.name || ' vs ' || tb.name AS teams, m.match_date,
        v.name || ', ' || v.city AS venue, COALESCE(w.name, 'No result') AS winner,
        m.victory_margin, m.victory_type FROM matches m JOIN teams ta ON ta.team_id=m.team_a_id
        JOIN teams tb ON tb.team_id=m.team_b_id JOIN venues v ON v.venue_id=m.venue_id
        LEFT JOIN teams w ON w.team_id=m.winner_team_id WHERE m.status='completed'
        ORDER BY m.match_date DESC LIMIT ?""", (limit,))


def toss_advantage():
    return query_df("""SELECT toss_decision, COUNT(*) AS matches,
        SUM(CASE WHEN toss_winner_id=winner_team_id THEN 1 ELSE 0 END) AS toss_winner_wins,
        ROUND(100.0*SUM(CASE WHEN toss_winner_id=winner_team_id THEN 1 ELSE 0 END)/COUNT(*),2) AS win_percentage
        FROM matches WHERE status='completed' GROUP BY toss_decision ORDER BY toss_decision""")