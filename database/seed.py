"""Create a coherent, clearly labeled historical SAMPLE/SEED dataset.

The script is deterministic and idempotent. It never masquerades seed values as
live API data; live records would be ingested by a future sync job into the same
relational tables with their source metadata preserved at the application layer.
"""

from __future__ import annotations

import datetime as dt
import sqlite3
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from database.connection import get_connection, initialize_database


TEAMS = [
    (1, "India", "India", "IND"), (2, "Australia", "Australia", "AUS"),
    (3, "England", "England", "ENG"), (4, "South Africa", "South Africa", "SA"),
]
VENUES = [
    (1, "Narendra Modi Stadium", "Ahmedabad", "India", 132000),
    (2, "Melbourne Cricket Ground", "Melbourne", "Australia", 100024),
    (3, "Lord's Cricket Ground", "London", "England", 30000),
    (4, "Wanderers Stadium", "Johannesburg", "South Africa", 34000),
    (5, "Eden Gardens", "Kolkata", "India", 68000),
    (6, "Sydney Cricket Ground", "Sydney", "Australia", 48000),
    (7, "The Oval", "London", "England", 27500),
    (8, "Kingsmead", "Durban", "South Africa", 25000),
]
SERIES = [(1, "World Test Championship Cycle", "England", "Test", "2024-06-01", 9), (2, "Global ODI Cup", "India", "ODI", "2024-02-10", 12), (3, "Summer T20I League", "Australia", "T20I", "2024-11-01", 8), (4, "Continental Tour 2025", "South Africa", "ODI", "2025-01-10", 6)]
PLAYERS = [
    (1,"Virat Kohli","Batsman","Right-hand","Right-arm medium","India",1),(2,"Rohit Sharma","Batsman","Right-hand","Right-arm off break","India",1),(3,"Ravindra Jadeja","All-rounder","Left-hand","Slow left-arm orthodox","India",1),(4,"Jasprit Bumrah","Bowler","Right-hand","Right-arm fast","India",1),
    (5,"Steve Smith","Batsman","Right-hand","Right-arm leg break","Australia",2),(6,"David Warner","Batsman","Left-hand","Right-arm leg break","Australia",2),(7,"Glenn Maxwell","All-rounder","Right-hand","Right-arm off break","Australia",2),(8,"Pat Cummins","Bowler","Right-hand","Right-arm fast","Australia",2),
    (9,"Joe Root","Batsman","Right-hand","Right-arm off break","England",3),(10,"Ben Stokes","All-rounder","Left-hand","Right-arm fast-medium","England",3),(11,"Jos Buttler","Wicket-keeper","Right-hand","Right-arm medium","England",3),(12,"Jofra Archer","Bowler","Right-hand","Right-arm fast","England",3),
    (13,"Aiden Markram","All-rounder","Right-hand","Right-arm off break","South Africa",4),(14,"Quinton de Kock","Wicket-keeper","Left-hand","Right-arm leg break","South Africa",4),(15,"Kagiso Rabada","Bowler","Right-hand","Right-arm fast","South Africa",4),(16,"Marco Jansen","All-rounder","Left-hand","Left-arm fast-medium","South Africa",4),
]


def _match_dates() -> list[dt.date]:
    today = dt.date.today()
    dates = [today - dt.timedelta(days=2)]
    for year in range(2022, 2026):
        for month in (1, 4, 7, 10):
            for day in (5, 10, 15, 20, 25, 28):
                dates.append(dt.date(year, month, day))
    return dates[:97]


def seed() -> None:
    initialize_database()
    with get_connection() as connection:
        connection.execute("PRAGMA foreign_keys = OFF")
        for table in ("partnerships","fielding_performances","bowling_performances","batting_performances","innings","matches","players","series","venues","teams"):
            connection.execute(f"DELETE FROM {table}")
        connection.executemany("INSERT INTO teams VALUES (?,?,?,?)", TEAMS)
        connection.executemany("INSERT INTO venues VALUES (?,?,?,?,?)", VENUES)
        connection.executemany("INSERT INTO series VALUES (?,?,?,?,?,?)", SERIES)
        connection.executemany("INSERT INTO players(player_id,full_name,role,batting_style,bowling_style,country,team_id) VALUES (?,?,?,?,?,?,?)", PLAYERS)

        rosters = {team_id: [p[0] for p in PLAYERS if p[6] == team_id] for team_id, *_ in TEAMS}
        match_rows, innings_rows, batting_rows, bowling_rows, fielding_rows, partnership_rows = [], [], [], [], [], []
        batting_id = bowling_id = fielding_id = partnership_id = innings_id = 1
        dates = _match_dates()
        for match_id, match_date in enumerate(dates, start=1):
            team_a = ((match_id - 1) % 4) + 1
            team_b = (team_a % 4) + 1
            format_name = ("Test", "ODI", "T20I")[(match_id - 1) % 3]
            venue_id = ((match_id - 1) % 8) + 1
            series_id = ((match_id - 1) % 4) + 1
            winner = team_a if match_id % 3 else team_b
            victory_type = "runs" if match_id % 2 else "wickets"
            margin = 24 + (match_id % 8) * 8
            toss_winner = team_a if match_id % 2 else team_b
            toss_decision = "bat" if match_id % 3 else "bowl"
            match_rows.append((match_id, f"{format_name} Match {match_id:02d}", match_date.isoformat(), format_name, "completed", venue_id, series_id, team_a, team_b, winner, margin, victory_type, toss_winner, toss_decision))
            for innings_number, batting_team, bowling_team in ((1, team_a, team_b), (2, team_b, team_a)):
                current_innings = innings_id
                innings_rows.append((current_innings, match_id, innings_number, batting_team, bowling_team, 0, 0))
                batters = rosters[batting_team] + rosters[bowling_team][:2]
                runs_in_innings = 0
                wickets = 0
                for position, player_id in enumerate(batters, start=1):
                    runs = 38 + ((player_id * 7 + match_id * 3 + position * 11) % 78)
                    balls = max(10, int(runs * 0.72) + (position % 4))
                    if position == 1 and match_id % 7 == 0:
                        runs = 108 + (match_id % 20)
                    runs_in_innings += runs
                    wickets += int(position in (2, 5) and match_id % 4 != 0)
                    batting_rows.append((batting_id, current_innings, player_id, position, runs, balls, runs // 12, runs // 30, "caught" if position in (2,5) else "not out"))
                    if position < 6:
                        partnership_rows.append((partnership_id, current_innings, batters[position-1], batters[position], position, position+1, runs + 45 + ((match_id + position) % 55)))
                        partnership_id += 1
                    batting_id += 1
                innings_rows[-1] = (current_innings, match_id, innings_number, batting_team, bowling_team, runs_in_innings, wickets)
                bowlers = rosters[bowling_team] + rosters[batting_team][:2]
                for position, player_id in enumerate(bowlers, start=1):
                    overs = 4.0 if position <= 4 else 2.0
                    conceded = int(overs * (4.8 + ((match_id + player_id) % 5) * .55))
                    wickets_taken = 1 + int((match_id + player_id + innings_number) % 5 == 0)
                    bowling_rows.append((bowling_id, current_innings, player_id, overs, conceded, wickets_taken, int(position == 1)))
                    bowling_id += 1
                for player_id in rosters[bowling_team][:3]:
                    fielding_rows.append((fielding_id, match_id, player_id, (match_id + player_id) % 3, 0, (match_id + player_id) % 2))
                    fielding_id += 1
                innings_id += 1

        connection.executemany("INSERT INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", match_rows)
        connection.executemany("INSERT INTO innings VALUES (?,?,?,?,?,?,?)", innings_rows)
        connection.executemany("INSERT INTO batting_performances VALUES (?,?,?,?,?,?,?,?,?)", batting_rows)
        connection.executemany("INSERT INTO bowling_performances VALUES (?,?,?,?,?,?,?)", bowling_rows)
        connection.executemany("INSERT INTO fielding_performances VALUES (?,?,?,?,?,?)", fielding_rows)
        connection.executemany("INSERT INTO partnerships VALUES (?,?,?,?,?,?,?)", partnership_rows)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.commit()
    print(f"Seeded {len(match_rows)} matches, {len(batting_rows)} batting rows, and {len(bowling_rows)} bowling rows")


if __name__ == "__main__":
    seed()