PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL,
    short_code TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS venues (
    venue_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity >= 0),
    UNIQUE(name, city)
);

CREATE TABLE IF NOT EXISTS series (
    series_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    host_country TEXT NOT NULL,
    match_type TEXT NOT NULL,
    start_date TEXT NOT NULL,
    planned_matches INTEGER NOT NULL CHECK (planned_matches > 0)
);

CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('Batsman','Bowler','All-rounder','Wicket-keeper')),
    batting_style TEXT NOT NULL,
    bowling_style TEXT NOT NULL,
    country TEXT NOT NULL,
    team_id INTEGER NOT NULL REFERENCES teams(team_id) ON UPDATE CASCADE,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1)),
    UNIQUE(full_name, country)
);

CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    match_date TEXT NOT NULL,
    format TEXT NOT NULL CHECK (format IN ('Test','ODI','T20I')),
    status TEXT NOT NULL CHECK (status IN ('completed','live','scheduled')),
    venue_id INTEGER NOT NULL REFERENCES venues(venue_id),
    series_id INTEGER REFERENCES series(series_id),
    team_a_id INTEGER NOT NULL REFERENCES teams(team_id),
    team_b_id INTEGER NOT NULL REFERENCES teams(team_id),
    winner_team_id INTEGER REFERENCES teams(team_id),
    victory_margin INTEGER DEFAULT 0 CHECK (victory_margin >= 0),
    victory_type TEXT CHECK (victory_type IN ('runs','wickets','draw','tie')),
    toss_winner_id INTEGER REFERENCES teams(team_id),
    toss_decision TEXT CHECK (toss_decision IN ('bat','bowl')),
    CHECK (team_a_id <> team_b_id)
);

CREATE TABLE IF NOT EXISTS innings (
    innings_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    innings_number INTEGER NOT NULL CHECK (innings_number > 0),
    batting_team_id INTEGER NOT NULL REFERENCES teams(team_id),
    bowling_team_id INTEGER NOT NULL REFERENCES teams(team_id),
    total_runs INTEGER NOT NULL CHECK (total_runs >= 0),
    wickets_lost INTEGER NOT NULL CHECK (wickets_lost >= 0),
    UNIQUE(match_id, innings_number)
);

CREATE TABLE IF NOT EXISTS batting_performances (
    batting_id INTEGER PRIMARY KEY,
    innings_id INTEGER NOT NULL REFERENCES innings(innings_id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    batting_position INTEGER NOT NULL CHECK (batting_position > 0),
    runs_scored INTEGER NOT NULL CHECK (runs_scored >= 0),
    balls_faced INTEGER NOT NULL CHECK (balls_faced >= 0),
    fours INTEGER NOT NULL DEFAULT 0 CHECK (fours >= 0),
    sixes INTEGER NOT NULL DEFAULT 0 CHECK (sixes >= 0),
    dismissal TEXT NOT NULL DEFAULT 'not out',
    UNIQUE(innings_id, batting_position)
);

CREATE TABLE IF NOT EXISTS bowling_performances (
    bowling_id INTEGER PRIMARY KEY,
    innings_id INTEGER NOT NULL REFERENCES innings(innings_id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    overs REAL NOT NULL CHECK (overs >= 0),
    runs_conceded INTEGER NOT NULL CHECK (runs_conceded >= 0),
    wickets_taken INTEGER NOT NULL CHECK (wickets_taken >= 0),
    maidens INTEGER NOT NULL DEFAULT 0 CHECK (maidens >= 0),
    UNIQUE(innings_id, player_id)
);

CREATE TABLE IF NOT EXISTS fielding_performances (
    fielding_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    catches INTEGER NOT NULL DEFAULT 0,
    stumpings INTEGER NOT NULL DEFAULT 0,
    run_outs INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS partnerships (
    partnership_id INTEGER PRIMARY KEY,
    innings_id INTEGER NOT NULL REFERENCES innings(innings_id) ON DELETE CASCADE,
    player_one_id INTEGER NOT NULL REFERENCES players(player_id),
    player_two_id INTEGER NOT NULL REFERENCES players(player_id),
    player_one_position INTEGER NOT NULL,
    player_two_position INTEGER NOT NULL,
    partnership_runs INTEGER NOT NULL CHECK (partnership_runs >= 0),
    CHECK (ABS(player_one_position - player_two_position) = 1)
);

CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date DESC);
CREATE INDEX IF NOT EXISTS idx_matches_format ON matches(format);
CREATE INDEX IF NOT EXISTS idx_batting_player ON batting_performances(player_id);
CREATE INDEX IF NOT EXISTS idx_batting_innings ON batting_performances(innings_id);
CREATE INDEX IF NOT EXISTS idx_bowling_player ON bowling_performances(player_id);
CREATE INDEX IF NOT EXISTS idx_players_country ON players(country);