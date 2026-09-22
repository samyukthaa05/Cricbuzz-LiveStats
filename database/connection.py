"""SQLite connection and schema bootstrap helpers."""

from __future__ import annotations

import sqlite3
import math
from pathlib import Path
from typing import Any, Iterator

from config.settings import ROOT_DIR, settings


SCHEMA_PATH = ROOT_DIR / "database" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Open a foreign-key-enforced SQLite connection with row access by name."""
    path = settings.resolved_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.create_function("SQRT", 1, lambda value: math.sqrt(max(float(value), 0.0)))
    return connection


def initialize_database() -> str:
    """Apply the schema and return the resolved database path."""
    with get_connection() as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return str(settings.resolved_database_path())


def query_df(sql: str, params: tuple[Any, ...] = ()):
    """Return a pandas DataFrame from a parameterized SELECT."""
    import pandas as pd

    with get_connection() as connection:
        return pd.read_sql_query(sql, connection, params=params)


def execute(sql: str, params: tuple[Any, ...] = ()) -> int:
    """Execute one write statement and return its row id."""
    with get_connection() as connection:
        cursor = connection.execute(sql, params)
        connection.commit()
        return int(cursor.lastrowid or 0)


def execute_script(sql: str) -> None:
    """Execute a trusted schema/seed script."""
    with get_connection() as connection:
        connection.executescript(sql)
        connection.commit()