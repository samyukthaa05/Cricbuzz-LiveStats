"""Centralized database connection logic as specified in project requirements.

Provides database-agnostic interface and handles connection pooling,
pragmas, foreign keys, custom SQLite functions, and query helpers.
"""

from __future__ import annotations

import sqlite3
from typing import Any
import pandas as pd

from database.connection import (
    SCHEMA_PATH,
    execute,
    execute_script,
    get_connection,
    initialize_database,
    query_df,
)

__all__ = [
    "SCHEMA_PATH",
    "get_connection",
    "initialize_database",
    "query_df",
    "execute",
    "execute_script",
]
