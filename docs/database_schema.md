# Database schema

SQLite is the default local database. `schema.sql` enables foreign keys and creates indexes on match dates, formats, player countries, innings, and player performance references.

## Relationship map

```text
teams ──< players
teams ──< matches (team_a, team_b, winner, toss_winner)
venues ──< matches
series ──< matches
matches ──< innings ──< batting_performances >── players
matches ──< innings ──< bowling_performances >── players
matches ──< fielding_performances >── players
innings ──< partnerships >── players (player_one/player_two)
```

`matches` stores format, status, date, result, margin, toss decision, and team relationships. `innings` stores batting/bowling sides and totals. Fact tables store match-level player performance so the 25 SQL questions are backed by real joins and aggregations.

## Integrity rules

- IDs are integer primary keys with foreign-key references.
- Player role, match format/status, victory type, and toss decision use checks.
- A match cannot use the same team twice.
- Batting positions are unique inside an innings.
- Partnership pairs must be consecutive positions.
- Seed records are internally consistent and labeled SAMPLE / SEED DATA in the UI.