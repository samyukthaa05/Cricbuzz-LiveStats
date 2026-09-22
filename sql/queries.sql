-- ============================================================================
-- Cricbuzz LiveStats: 25 SQL Practice Queries
-- Complete reference script containing all 25 queries (Beginner, Intermediate, Advanced)
-- Compatible with SQLite / PostgreSQL / MySQL standards
-- ============================================================================

-- ============================================================================
-- BEGINNER LEVEL (Questions 1 - 8)
-- ============================================================================

-- Question 1: Find all players who represent India. Display their full name,
-- playing role, batting style, and bowling style.
SELECT 
    full_name, 
    role AS playing_role, 
    batting_style, 
    bowling_style 
FROM players 
WHERE country = 'India' 
ORDER BY full_name;


-- Question 2: Show all cricket matches that were played in the last few days.
-- Include the match description, both team names, venue name with city, and the match date.
-- Sort by most recent matches first.
SELECT 
    m.description, 
    ta.name AS team_1, 
    tb.name AS team_2, 
    v.name AS venue, 
    v.city, 
    m.match_date 
FROM matches m 
JOIN teams ta ON ta.team_id = m.team_a_id 
JOIN teams tb ON tb.team_id = m.team_b_id 
JOIN venues v ON v.venue_id = m.venue_id 
WHERE date(m.match_date) >= date('now', '-7 days') 
ORDER BY m.match_date DESC;


-- Question 3: List the top 10 highest run scorers in ODI cricket.
-- Show player name, total runs scored, batting average, and number of centuries.
-- Display the highest run scorer first.
SELECT 
    p.full_name AS player, 
    SUM(b.runs_scored) AS total_runs, 
    ROUND(AVG(CASE WHEN b.dismissal = 'not out' THEN b.runs_scored * 1.0 ELSE b.runs_scored * 0.8 END), 2) AS batting_average, 
    SUM(b.runs_scored >= 100) AS centuries 
FROM batting_performances b 
JOIN players p ON p.player_id = b.player_id 
JOIN innings i ON i.innings_id = b.innings_id 
JOIN matches m ON m.match_id = i.match_id 
WHERE m.format = 'ODI' 
GROUP BY p.player_id 
ORDER BY total_runs DESC 
LIMIT 10;


-- Question 4: Display all cricket venues that have a seating capacity of more than 25,000 spectators.
-- Show venue name, city, country, and capacity. Order by largest capacity first (10 Venues enough).
SELECT 
    name AS venue, 
    city, 
    country, 
    capacity 
FROM venues 
WHERE capacity > 25000 
ORDER BY capacity DESC 
LIMIT 10;


-- Question 5: Calculate how many matches each team has won.
-- Show team name and total number of wins. Display teams with the most wins first.
SELECT 
    t.name AS team, 
    COUNT(m.match_id) AS total_wins 
FROM teams t 
LEFT JOIN matches m ON m.winner_team_id = t.team_id 
GROUP BY t.team_id 
ORDER BY total_wins DESC;


-- Question 6: Count how many players belong to each playing role
-- (like Batsman, Bowler, All-rounder, Wicket-keeper).
-- Show the role and count of players for each role.
SELECT 
    role, 
    COUNT(*) AS player_count 
FROM players 
GROUP BY role 
ORDER BY player_count DESC, role;


-- Question 7: Find the highest individual batting score achieved in each cricket format (Test, ODI, T20I).
-- Display the format and the highest score for that format.
SELECT 
    m.format, 
    MAX(b.runs_scored) AS highest_individual_score 
FROM batting_performances b 
JOIN innings i ON i.innings_id = b.innings_id 
JOIN matches m ON m.match_id = i.match_id 
GROUP BY m.format 
ORDER BY m.format;


-- Question 8: Show all cricket series that started in the year 2024.
-- Include series name, host country, match type, start date, and total number of matches planned.
SELECT 
    name AS series_name, 
    host_country, 
    match_type, 
    start_date, 
    planned_matches AS total_planned_matches 
FROM series 
WHERE start_date LIKE '2024-%' 
ORDER BY start_date;


-- ============================================================================
-- INTERMEDIATE LEVEL (Questions 9 - 16)
-- ============================================================================

-- Question 9: Find all-rounder players who have scored more than 1000 runs AND
-- taken more than 50 wickets in their career. Display player name, total runs, total wickets,
-- and the cricket format.
WITH batting AS (
    SELECT 
        p.player_id,
        SUM(b.runs_scored) AS total_runs,
        GROUP_CONCAT(DISTINCT m.format) AS cricket_format 
    FROM players p 
    JOIN batting_performances b ON b.player_id = p.player_id 
    JOIN innings i ON i.innings_id = b.innings_id 
    JOIN matches m ON m.match_id = i.match_id 
    WHERE p.role = 'All-rounder' 
    GROUP BY p.player_id
), 
bowling AS (
    SELECT 
        p.player_id,
        SUM(bo.wickets_taken) AS total_wickets 
    FROM players p 
    JOIN bowling_performances bo ON bo.player_id = p.player_id 
    JOIN innings i ON i.innings_id = bo.innings_id 
    JOIN matches m ON m.match_id = i.match_id 
    WHERE p.role = 'All-rounder' 
    GROUP BY p.player_id
) 
SELECT 
    p.full_name AS player,
    b.cricket_format,
    b.total_runs,
    bo.total_wickets 
FROM batting b 
JOIN bowling bo ON bo.player_id = b.player_id 
JOIN players p ON p.player_id = b.player_id 
WHERE b.total_runs > 1000 AND bo.total_wickets > 50 
ORDER BY b.total_runs DESC;


-- Question 10: Get details of the last 20 completed matches.
-- Show match description, both team names, winning team, victory margin, victory type (runs/wickets),
-- and venue name. Display the most recent matches first.
SELECT 
    m.description, 
    ta.name || ' vs ' || tb.name AS teams, 
    w.name AS winning_team, 
    m.victory_margin, 
    m.victory_type, 
    v.name AS venue, 
    m.match_date 
FROM matches m 
JOIN teams ta ON ta.team_id = m.team_a_id 
JOIN teams tb ON tb.team_id = m.team_b_id 
LEFT JOIN teams w ON w.team_id = m.winner_team_id 
JOIN venues v ON v.venue_id = m.venue_id 
WHERE m.status = 'completed' 
ORDER BY m.match_date DESC 
LIMIT 20;


-- Question 11: Compare each player's performance across different cricket formats.
-- For players who have played at least 2 different formats, show their total runs in Test cricket,
-- ODI cricket, and T20I cricket, along with their overall batting average across all formats.
SELECT 
    p.full_name AS player, 
    SUM(CASE WHEN m.format = 'Test' THEN b.runs_scored ELSE 0 END) AS test_runs, 
    SUM(CASE WHEN m.format = 'ODI' THEN b.runs_scored ELSE 0 END) AS odi_runs, 
    SUM(CASE WHEN m.format = 'T20I' THEN b.runs_scored ELSE 0 END) AS t20i_runs, 
    ROUND(AVG(b.runs_scored), 2) AS overall_batting_average 
FROM players p 
JOIN batting_performances b ON b.player_id = p.player_id 
JOIN innings i ON i.innings_id = b.innings_id 
JOIN matches m ON m.match_id = i.match_id 
GROUP BY p.player_id 
HAVING COUNT(DISTINCT m.format) >= 2 
ORDER BY overall_batting_average DESC;


-- Question 12: Analyze each international team's performance when playing at home versus playing away.
-- Determine whether each team played at home or away based on whether the venue country matches the team's country.
-- Count wins for each team in both home and away conditions.
WITH appearances AS (
    SELECT 
        m.match_id, 
        t.team_id, 
        t.name, 
        t.country, 
        v.country AS venue_country, 
        CASE WHEN v.country = t.country THEN 'home' ELSE 'away' END AS location, 
        CASE WHEN m.winner_team_id = t.team_id THEN 1 ELSE 0 END AS won 
    FROM matches m 
    JOIN venues v ON v.venue_id = m.venue_id 
    JOIN teams t ON t.team_id IN (m.team_a_id, m.team_b_id) 
    WHERE m.status = 'completed'
) 
SELECT 
    name AS team, 
    location, 
    COUNT(*) AS matches, 
    SUM(won) AS wins 
FROM appearances 
GROUP BY team_id, location 
ORDER BY team, location;


-- Question 13: Identify batting partnerships where two consecutive batsmen
-- (batting positions next to each other) scored a combined total of 100 or more runs in the same innings.
-- Show both player names, their combined partnership runs, and which innings it occurred in.
SELECT 
    p1.full_name AS player_1, 
    p2.full_name AS player_2, 
    pa.partnership_runs AS combined_runs, 
    pa.innings_id AS innings 
FROM partnerships pa 
JOIN players p1 ON p1.player_id = pa.player_one_id 
JOIN players p2 ON p2.player_id = pa.player_two_id 
WHERE pa.partnership_runs >= 100 
ORDER BY combined_runs DESC;


-- Question 14: Examine bowling performance at different venues.
-- For bowlers who have played at least 3 matches at the same venue, calculate their average economy rate,
-- total wickets taken, and number of matches played at each venue. Focus on bowlers who bowled at least 4 overs in each match.
SELECT 
    p.full_name AS bowler, 
    v.name AS venue, 
    ROUND(SUM(bo.runs_conceded) * 1.0 / NULLIF(SUM(bo.overs), 0), 2) AS average_economy_rate, 
    SUM(bo.wickets_taken) AS total_wickets, 
    COUNT(DISTINCT m.match_id) AS number_of_matches 
FROM bowling_performances bo 
JOIN players p ON p.player_id = bo.player_id 
JOIN innings i ON i.innings_id = bo.innings_id 
JOIN matches m ON m.match_id = i.match_id 
JOIN venues v ON v.venue_id = m.venue_id 
WHERE bo.overs >= 4 
GROUP BY p.player_id, v.venue_id 
HAVING COUNT(DISTINCT m.match_id) >= 3 
ORDER BY average_economy_rate 
LIMIT 20;


-- Question 15: Identify players who perform exceptionally well in close matches.
-- A close match is defined as one decided by less than 50 runs OR less than 5 wickets.
-- For these close matches, calculate each player's average runs scored, total close matches played,
-- and how many of those close matches their team won when they batted.
SELECT 
    p.full_name AS player, 
    ROUND(AVG(b.runs_scored), 2) AS average_runs, 
    COUNT(DISTINCT m.match_id) AS close_matches_played, 
    SUM(CASE WHEN m.winner_team_id = i.batting_team_id THEN 1 ELSE 0 END) AS close_matches_won_when_batting 
FROM batting_performances b 
JOIN players p ON p.player_id = b.player_id 
JOIN innings i ON i.innings_id = b.innings_id 
JOIN matches m ON m.match_id = i.match_id 
WHERE m.victory_margin < 50 OR (m.victory_type = 'wickets' AND m.victory_margin < 5) 
GROUP BY p.player_id 
ORDER BY average_runs DESC;


-- Question 16: Track how players' batting performance changes over different years.
-- For matches since 2020, show each player's average runs per match and average strike rate for each year.
-- Only include players who played at least 5 matches in that year.
SELECT 
    p.full_name AS player, 
    strftime('%Y', m.match_date) AS year, 
    ROUND(AVG(b.runs_scored), 2) AS average_runs_per_match, 
    ROUND(AVG(100.0 * b.runs_scored / NULLIF(b.balls_faced, 0)), 2) AS average_strike_rate, 
    COUNT(DISTINCT m.match_id) AS matches 
FROM batting_performances b 
JOIN players p ON p.player_id = b.player_id 
JOIN innings i ON i.innings_id = b.innings_id 
JOIN matches m ON m.match_id = i.match_id 
WHERE CAST(strftime('%Y', m.match_date) AS INTEGER) >= 2020 
GROUP BY p.player_id, year 
HAVING matches >= 5 
ORDER BY year DESC, average_runs_per_match DESC;


-- ============================================================================
-- ADVANCED LEVEL (Questions 17 - 25)
-- ============================================================================

-- Question 17: Investigate whether winning the toss gives teams an advantage in winning matches.
-- Calculate what percentage of matches are won by the team that wins the toss,
-- broken down by their toss decision (choosing to bat first or bowl first).
SELECT 
    toss_decision, 
    COUNT(*) AS matches, 
    SUM(toss_winner_id = winner_team_id) AS toss_winner_wins, 
    ROUND(100.0 * SUM(toss_winner_id = winner_team_id) / COUNT(*), 2) AS toss_win_percentage 
FROM matches 
WHERE status = 'completed' 
GROUP BY toss_decision;


-- Question 18: Find the most economical bowlers in limited-overs cricket (ODI and T20 formats).
-- Calculate each bowler's overall economy rate and total wickets taken.
-- Only consider bowlers who have bowled in at least 10 matches and bowled at least 2 overs per match on average.
SELECT 
    p.full_name AS bowler, 
    GROUP_CONCAT(DISTINCT m.format) AS formats, 
    ROUND(SUM(bo.runs_conceded) * 1.0 / NULLIF(SUM(bo.overs), 0), 2) AS overall_economy_rate, 
    SUM(bo.wickets_taken) AS total_wickets, 
    COUNT(DISTINCT m.match_id) AS matches, 
    ROUND(AVG(bo.overs), 2) AS average_overs 
FROM bowling_performances bo 
JOIN players p ON p.player_id = bo.player_id 
JOIN innings i ON i.innings_id = bo.innings_id 
JOIN matches m ON m.match_id = i.match_id 
WHERE m.format IN ('ODI', 'T20I') 
GROUP BY p.player_id 
HAVING matches >= 10 AND average_overs >= 2 
ORDER BY overall_economy_rate;


-- Question 19: Determine which batsmen are most consistent in their scoring.
-- Calculate the average runs scored and the standard deviation of runs for each player.
-- Only include players who have faced at least 10 balls per innings and played since 2022.
-- A lower standard deviation indicates more consistent performance.
SELECT 
    p.full_name AS player, 
    ROUND(AVG(b.runs_scored), 2) AS average_runs, 
    ROUND(SQRT(ABS(AVG(b.runs_scored * b.runs_scored) - AVG(b.runs_scored) * AVG(b.runs_scored))), 2) AS standard_deviation, 
    COUNT(*) AS innings 
FROM batting_performances b 
JOIN players p ON p.player_id = b.player_id 
JOIN innings i ON i.innings_id = b.innings_id 
JOIN matches m ON m.match_id = i.match_id 
WHERE b.balls_faced >= 10 AND CAST(strftime('%Y', m.match_date) AS INTEGER) >= 2022 
GROUP BY p.player_id 
ORDER BY standard_deviation, average_runs DESC;


-- Question 20: Analyze how many matches each player has played in different cricket formats
-- and their batting average in each format. Show the count of Test matches, ODI matches,
-- and T20 matches for each player, along with their respective batting averages.
-- Only include players who have played at least 20 total matches across all formats.
SELECT 
    p.full_name AS player, 
    COUNT(DISTINCT CASE WHEN m.format = 'Test' THEN m.match_id END) AS test_matches, 
    COUNT(DISTINCT CASE WHEN m.format = 'ODI' THEN m.match_id END) AS odi_matches, 
    COUNT(DISTINCT CASE WHEN m.format = 'T20I' THEN m.match_id END) AS t20_matches, 
    ROUND(AVG(CASE WHEN m.format = 'Test' THEN b.runs_scored END), 2) AS test_batting_average, 
    ROUND(AVG(CASE WHEN m.format = 'ODI' THEN b.runs_scored END), 2) AS odi_batting_average, 
    ROUND(AVG(CASE WHEN m.format = 'T20I' THEN b.runs_scored END), 2) AS t20_batting_average, 
    COUNT(DISTINCT m.match_id) AS total_matches 
FROM players p 
JOIN batting_performances b ON b.player_id = p.player_id 
JOIN innings i ON i.innings_id = b.innings_id 
JOIN matches m ON m.match_id = i.match_id 
GROUP BY p.player_id 
HAVING total_matches >= 20 
ORDER BY total_matches DESC;


-- Question 21: Create a comprehensive performance ranking system for players.
-- Combine their batting performance (runs scored, batting average, strike rate),
-- bowling performance (wickets taken, bowling average, economy rate), and fielding performance
-- (catches, stumpings, run outs) into a single weighted score.
-- Batting points: (runs_scored * 0.01) + (batting_average * 0.5) + (strike_rate * 0.3)
-- Bowling points: (wickets_taken * 2) + ((50 - bowling_average) * 0.5) + ((6 - economy_rate) * 2)
-- Fielding points: (catches * 10) + (stumpings * 15) + (run_outs * 10)
-- Rank the top performers in each cricket format.
WITH batting AS (
    SELECT 
        p.player_id, 
        p.full_name, 
        m.format, 
        SUM(b.runs_scored) AS runs_scored, 
        AVG(b.runs_scored) AS batting_average, 
        100.0 * SUM(b.runs_scored) / NULLIF(SUM(b.balls_faced), 0) AS strike_rate 
    FROM players p 
    JOIN batting_performances b ON b.player_id = p.player_id 
    JOIN innings i ON i.innings_id = b.innings_id 
    JOIN matches m ON m.match_id = i.match_id 
    GROUP BY p.player_id, m.format
), 
bowling AS (
    SELECT 
        p.player_id, 
        m.format, 
        SUM(bo.wickets_taken) AS wickets_taken, 
        50.0 * SUM(bo.runs_conceded) / NULLIF(SUM(bo.overs) * 6, 0) AS bowling_average, 
        SUM(bo.runs_conceded) * 1.0 / NULLIF(SUM(bo.overs), 0) AS economy_rate 
    FROM players p 
    JOIN bowling_performances bo ON bo.player_id = p.player_id 
    JOIN innings i ON i.innings_id = bo.innings_id 
    JOIN matches m ON m.match_id = i.match_id 
    GROUP BY p.player_id, m.format
),
fielding AS (
    SELECT 
        p.player_id, 
        m.format, 
        SUM(fp.catches) AS catches, 
        SUM(fp.stumpings) AS stumpings, 
        SUM(fp.run_outs) AS run_outs, 
        (SUM(fp.catches) * 10) + (SUM(fp.stumpings) * 15) + (SUM(fp.run_outs) * 10) AS fielding_points 
    FROM players p 
    JOIN fielding_performances fp ON fp.player_id = p.player_id 
    JOIN matches m ON m.match_id = fp.match_id 
    GROUP BY p.player_id, m.format
) 
SELECT 
    b.full_name AS player, 
    b.format, 
    ROUND(
        (b.runs_scored * 0.01) + (b.batting_average * 0.5) + (b.strike_rate * 0.3) + 
        COALESCE((bo.wickets_taken * 2) + ((50 - bo.bowling_average) * 0.5) + ((6 - bo.economy_rate) * 2), 0) + 
        COALESCE(f.fielding_points, 0), 
        2
    ) AS performance_points, 
    COALESCE(f.catches, 0) AS catches, 
    COALESCE(f.stumpings, 0) AS stumpings, 
    COALESCE(f.run_outs, 0) AS run_outs, 
    DENSE_RANK() OVER(PARTITION BY b.format ORDER BY 
        (b.runs_scored * 0.01) + (b.batting_average * 0.5) + (b.strike_rate * 0.3) + 
        COALESCE((bo.wickets_taken * 2) + ((50 - bo.bowling_average) * 0.5) + ((6 - bo.economy_rate) * 2), 0) + 
        COALESCE(f.fielding_points, 0) DESC
    ) AS format_rank 
FROM batting b 
LEFT JOIN bowling bo ON bo.player_id = b.player_id AND bo.format = b.format 
LEFT JOIN fielding f ON f.player_id = b.player_id AND f.format = b.format 
ORDER BY b.format, format_rank;


-- Question 22: Build a head-to-head match prediction analysis between teams.
-- For each pair of teams that have played at least 5 matches against each other in the last 3 years, calculate:
-- Total matches played between them, wins for each team, average victory margin when each team wins,
-- performance when batting first vs bowling first at different venues, and overall win percentage.
WITH pair_matches AS (
    SELECT 
        m.*, 
        v.name AS venue_name,
        CASE WHEN team_a_id < team_b_id THEN team_a_id ELSE team_b_id END AS low_team, 
        CASE WHEN team_a_id < team_b_id THEN team_b_id ELSE team_a_id END AS high_team,
        CASE WHEN m.toss_decision = 'bat' THEN m.toss_winner_id 
             ELSE (CASE WHEN m.team_a_id = m.toss_winner_id THEN m.team_b_id ELSE m.team_a_id END) 
        END AS batting_first_team_id
    FROM matches m 
    JOIN venues v ON v.venue_id = m.venue_id
    WHERE m.status = 'completed' AND date(m.match_date) >= date('now', '-3 years')
),
head_to_head_totals AS (
    SELECT 
        low_team, 
        high_team, 
        COUNT(*) AS total_h2h_matches,
        SUM(winner_team_id = low_team) AS total_wins_team_one,
        SUM(winner_team_id = high_team) AS total_wins_team_two,
        ROUND(100.0 * SUM(winner_team_id = low_team) / COUNT(*), 2) AS team_one_win_pct,
        ROUND(100.0 * SUM(winner_team_id = high_team) / COUNT(*), 2) AS team_two_win_pct
    FROM pair_matches
    GROUP BY low_team, high_team
    HAVING total_h2h_matches >= 5
)
SELECT 
    low.name AS team_one, 
    high.name AS team_two, 
    v.name AS venue,
    h2h.total_h2h_matches,
    h2h.total_wins_team_one,
    h2h.total_wins_team_two,
    h2h.team_one_win_pct,
    h2h.team_two_win_pct,
    COUNT(*) AS venue_matches,
    SUM(pm.winner_team_id = pm.batting_first_team_id) AS bat_first_wins,
    SUM(pm.winner_team_id != pm.batting_first_team_id) AS bowl_first_wins,
    ROUND(AVG(pm.victory_margin), 2) AS avg_victory_margin
FROM pair_matches pm
JOIN head_to_head_totals h2h ON h2h.low_team = pm.low_team AND h2h.high_team = pm.high_team
JOIN teams low ON low.team_id = pm.low_team 
JOIN teams high ON high.team_id = pm.high_team 
JOIN venues v ON v.venue_id = pm.venue_id
GROUP BY pm.low_team, pm.high_team, pm.venue_id
ORDER BY h2h.total_h2h_matches DESC, low.name, v.name;


-- Question 23: Analyze recent player form and momentum.
-- For each player's last 10 batting performances, calculate:
-- Average runs in last 5 vs last 10, recent strike rate, scores above 50, and consistency score (std dev).
-- Categorize players as "Excellent Form", "Good Form", "Average Form", or "Poor Form".
WITH ranked AS (
    SELECT 
        p.full_name AS player, 
        m.match_date, 
        b.runs_scored, 
        b.balls_faced, 
        ROW_NUMBER() OVER(PARTITION BY p.player_id ORDER BY m.match_date DESC) AS rn 
    FROM batting_performances b 
    JOIN players p ON p.player_id = b.player_id 
    JOIN innings i ON i.innings_id = b.innings_id 
    JOIN matches m ON m.match_id = i.match_id
), 
metrics AS (
    SELECT 
        player, 
        AVG(CASE WHEN rn <= 5 THEN runs_scored END) AS average_last_5, 
        AVG(runs_scored) AS average_last_10, 
        SUM(runs_scored >= 50) AS scores_above_50, 
        AVG(100.0 * runs_scored / NULLIF(balls_faced, 0)) AS recent_strike_rate, 
        SQRT(ABS(AVG(runs_scored * runs_scored) - AVG(runs_scored) * AVG(runs_scored))) AS consistency_score 
    FROM ranked 
    WHERE rn <= 10 
    GROUP BY player
) 
SELECT 
    player, 
    ROUND(average_last_5, 2) AS avg_last_5, 
    ROUND(average_last_10, 2) AS avg_last_10, 
    scores_above_50, 
    ROUND(recent_strike_rate, 2) AS strike_rate, 
    ROUND(consistency_score, 2) AS consistency, 
    CASE 
        WHEN average_last_5 >= 60 AND recent_strike_rate >= 125 THEN 'Excellent Form' 
        WHEN average_last_5 >= 40 AND recent_strike_rate >= 100 THEN 'Good Form' 
        WHEN average_last_5 >= 20 THEN 'Average Form' 
        ELSE 'Poor Form' 
    END AS form_category 
FROM metrics 
ORDER BY average_last_5 DESC;


-- Question 24: Study successful batting partnerships to identify the best player combinations.
-- For pairs of players who have batted together as consecutive batsmen in at least 5 partnerships:
-- Calculate average partnership runs, count partnerships > 50, highest score, success rate.
SELECT 
    p1.full_name AS player_one, 
    p2.full_name AS player_two, 
    COUNT(*) AS partnerships, 
    ROUND(AVG(pa.partnership_runs), 2) AS average_partnership_runs, 
    SUM(pa.partnership_runs > 50) AS partnerships_above_50, 
    MAX(pa.partnership_runs) AS highest_partnership, 
    ROUND(100.0 * SUM(pa.partnership_runs > 50) / COUNT(*), 2) AS success_rate 
FROM partnerships pa 
JOIN players p1 ON p1.player_id = pa.player_one_id 
JOIN players p2 ON p2.player_id = pa.player_two_id 
GROUP BY pa.player_one_id, pa.player_two_id 
HAVING partnerships >= 5 
ORDER BY success_rate DESC, average_partnership_runs DESC;


-- Question 25: Perform a time-series analysis of player performance evolution.
-- Track how each player's batting performance changes over time by:
-- Calculating quarterly averages for runs and strike rate,
-- comparing each quarter's performance to the previous quarter using LAG,
-- identifying whether performance is improving, declining, or stable,
-- determining overall career trajectory over the last few years,
-- and categorizing players' career phase as "Career Ascending", "Career Declining", or "Career Stable".
-- Only analyze players with data spanning at least 6 quarters and a minimum of 3 matches per quarter.
WITH quarterly_stats AS (
    SELECT 
        p.player_id, 
        p.full_name AS player, 
        strftime('%Y', m.match_date) || '-Q' || (((CAST(strftime('%m', m.match_date) AS INTEGER) - 1) / 3) + 1) AS quarter, 
        ROUND(AVG(b.runs_scored), 2) AS quarterly_avg_runs, 
        ROUND(AVG(100.0 * b.runs_scored / NULLIF(b.balls_faced, 0)), 2) AS quarterly_strike_rate, 
        COUNT(DISTINCT m.match_id) AS quarter_matches 
    FROM batting_performances b 
    JOIN players p ON p.player_id = b.player_id 
    JOIN innings i ON i.innings_id = b.innings_id 
    JOIN matches m ON m.match_id = i.match_id 
    GROUP BY p.player_id, quarter 
    HAVING quarter_matches >= 3
), 
qualified_players AS (
    SELECT player_id 
    FROM quarterly_stats 
    GROUP BY player_id 
    HAVING COUNT(DISTINCT quarter) >= 6
), 
quarterly_lag AS (
    SELECT 
        qs.player_id, 
        qs.player, 
        qs.quarter, 
        qs.quarterly_avg_runs, 
        qs.quarterly_strike_rate, 
        qs.quarter_matches, 
        LAG(qs.quarterly_avg_runs) OVER(PARTITION BY qs.player_id ORDER BY qs.quarter) AS prev_quarter_runs, 
        FIRST_VALUE(qs.quarterly_avg_runs) OVER(PARTITION BY qs.player_id ORDER BY qs.quarter ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_quarter_runs, 
        LAST_VALUE(qs.quarterly_avg_runs) OVER(PARTITION BY qs.player_id ORDER BY qs.quarter ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_quarter_runs, 
        COUNT(*) OVER(PARTITION BY qs.player_id) AS total_quarters 
    FROM quarterly_stats qs 
    JOIN qualified_players qp ON qp.player_id = qs.player_id
) 
SELECT 
    player, 
    quarter, 
    quarter_matches, 
    quarterly_avg_runs, 
    quarterly_strike_rate, 
    prev_quarter_runs, 
    ROUND(quarterly_avg_runs - prev_quarter_runs, 2) AS quarter_on_quarter_change, 
    CASE 
        WHEN prev_quarter_runs IS NULL THEN 'Baseline' 
        WHEN quarterly_avg_runs > prev_quarter_runs + 5 THEN 'Improving' 
        WHEN quarterly_avg_runs < prev_quarter_runs - 5 THEN 'Declining' 
        ELSE 'Stable' 
    END AS quarterly_performance, 
    CASE 
        WHEN (last_quarter_runs - first_quarter_runs) > 8 THEN 'Career Ascending' 
        WHEN (last_quarter_runs - first_quarter_runs) < -8 THEN 'Career Declining' 
        ELSE 'Career Stable' 
    END AS career_trajectory 
FROM quarterly_lag 
ORDER BY player, quarter;