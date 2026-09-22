"""Player form and trajectory calculations used by SQL Q23/Q25 documentation."""

from __future__ import annotations

import pandas as pd

from database.connection import query_df


def recent_form() -> pd.DataFrame:
    return query_df("""WITH ranked AS (SELECT p.full_name AS player, m.match_date, b.runs_scored,
        ROUND(100.0*b.runs_scored/NULLIF(b.balls_faced,0),2) AS strike_rate,
        ROW_NUMBER() OVER (PARTITION BY p.player_id ORDER BY m.match_date DESC) AS rn
        FROM batting_performances b JOIN players p ON p.player_id=b.player_id
        JOIN innings i ON i.innings_id=b.innings_id JOIN matches m ON m.match_id=i.match_id)
        SELECT player, ROUND(AVG(CASE WHEN rn<=5 THEN runs_scored END),2) AS average_last_5,
        ROUND(AVG(runs_scored),2) AS average_last_10, SUM(runs_scored>50) AS scores_above_50,
        ROUND(AVG(strike_rate),2) AS recent_strike_rate, ROUND(sqrt(AVG(runs_scored*runs_scored)-AVG(runs_scored)*AVG(runs_scored)),2) AS consistency_sd
        FROM ranked WHERE rn<=10 GROUP BY player ORDER BY average_last_5 DESC""")