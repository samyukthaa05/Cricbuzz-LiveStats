"""Presentation helpers that keep normal errors out of the UI tracebacks."""

from __future__ import annotations

import sqlite3

import streamlit as st


def friendly_error(area: str, exc: Exception) -> None:
    """Show a concise user-safe message while preserving useful category context."""
    if isinstance(exc, sqlite3.IntegrityError):
        message = "The record conflicts with existing data. Check duplicate values and relationships."
    elif isinstance(exc, sqlite3.Error):
        message = "The local database could not complete that operation."
    else:
        message = str(exc) or "An unexpected error occurred."
    st.error(f"{area}: {message}")