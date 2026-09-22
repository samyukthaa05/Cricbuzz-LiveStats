# Project documentation

## Architecture

`main.py` owns navigation and bootstrapping. `pages/` contains presentation-only Streamlit renderers. `api/` owns external requests. `database/` owns SQLite connection, schema, seed, and parameterized CRUD. `analytics/` contains reusable leaderboard/form helpers. `sql/` is the reviewed question catalogue. `utils/` owns validation, styling, and safe error presentation.

## Analytics assumptions

- Batting average in the demo dataset is a match-performance average because career dismissal counts are not supplied by the source API.
- Economy rate is runs conceded divided by overs.
- Q19 uses population standard deviation over qualifying innings.
- Q23 uses the last ten records ordered by match date. Excellent, Good, Average, and Poor thresholds are documented in README and encoded in the SQL.
- Q25 requires three matches per quarter and six qualifying quarters. Career trajectory compares first versus last qualifying quarter; ±10 runs is the stable band.

## Data provenance

The seed generator supplies structured historical SAMPLE / SEED DATA for reproducible SQL demonstrations where a live provider cannot supply a complete multi-year data warehouse. It is not presented as live Cricbuzz information. Live responses are polled only on the Live Match page and are not silently mixed into the seeded aggregates.

## CRUD behavior

Player create/update writes use bound parameters and validation. Reads support search across name, country, and role. Delete requires confirmation and is protected when dependent batting/bowling history exists. The active flag supports safe retirement of historical players.