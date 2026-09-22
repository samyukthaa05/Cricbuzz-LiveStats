from database.connection import get_connection, initialize_database
from utils.db_connection import query_df


def test_schema_initializes_with_foreign_keys():
    path = initialize_database()
    assert path.endswith("cricbuzz_livestats.db")
    with get_connection() as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {
        "teams", "venues", "series", "players", "matches",
        "innings", "batting_performances", "bowling_performances",
        "fielding_performances", "partnerships"
    }.issubset(tables)


def test_utils_db_connection_query():
    df = query_df("SELECT COUNT(*) AS cnt FROM teams")
    assert not df.empty
    assert df.iloc[0]["cnt"] >= 4