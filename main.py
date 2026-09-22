"""Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics.

Streamlit application entry point providing single unified sidebar navigation.
"""

from __future__ import annotations

import streamlit as st

from analytics.player_analytics import get_player_summary
from api.cricbuzz_api import api_configured
from database.connection import initialize_database
from pages.crud_operations import render_crud_page
from pages.live_match import render_live_match_page
from pages.player_stats import render_player_stats_page
from pages.sql_analytics import render_sql_analytics_page
from utils.error_handler import friendly_error
from utils.helpers import inject_css, render_header, render_metric_card


st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def boot_database() -> str:
    """Initialize the local SQLite database once per Streamlit process."""
    return initialize_database()


def render_home() -> None:
    """Render a clean, student-friendly Home overview page."""
    render_header(
        "🏏 Cricbuzz LiveStats",
        "Real-Time Cricket Insights & SQL-Based Analytics Dashboard",
        "GUVI & HCL PROJECT",
    )

    # 1. System Status Cards
    try:
        boot_database()
        summary = get_player_summary()
        api_status = "Online" if api_configured() else "Offline (.env needed)"
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_metric_card("CRICBUZZ API", api_status, "RapidAPI REST")
        with c2:
            render_metric_card("DATABASE", "Connected", "SQLite Relational")
        with c3:
            render_metric_card("PLAYERS IN DB", f"{summary['players']}", "Roster count")
        with c4:
            render_metric_card("MATCHES IN DB", f"{summary['matches']}", "Sample matches")
    except Exception as exc:
        friendly_error("System status", exc)

    st.markdown("---")

    col_left, col_right = st.columns([1.1, 0.9])

    with col_left:
        # 2. Overview / Problem Statement
        st.markdown("### 🎯 Project Overview & Problem Statement")
        st.markdown(
            """
            This project provides a comprehensive cricket analytics workbench that integrates real-time live data
            from the **Cricbuzz REST API** with a local **relational SQL database (SQLite)**. 

            **Core Deliverables:**
            - **⚡ Real-Time Match Updates:** Live scores, ball-by-ball scorecards, and venue details.
            - **📊 Player Statistics:** Live top performers from Cricbuzz API and format-wise historical database leaderboards.
            - **🔍 SQL Analytics:** A complete 25-query practice catalogue (Beginner to Advanced) and custom SQL editor.
            - **⚙️ CRUD Operations:** Form-based management for player rosters and match schedules.
            """
        )

        # 3. Technologies Used
        st.markdown("### 🛠 Technologies Used")
        st.markdown(
            """
            | Component | Technology | Purpose |
            | :--- | :--- | :--- |
            | **Programming Language** | Python 3.10+ | Core application logic and data pipelines |
            | **Web Interface** | Streamlit | Clean, responsive multi-page dashboard |
            | **Database** | SQLite | Relational database with foreign keys & indexes |
            | **Cricket Data API** | Cricbuzz via RapidAPI | Live scores, scorecards, and ICC rankings |
            | **Data Analytics** | pandas | Data manipulation and tabular representations |
            | **Visualizations** | Plotly Express | Interactive bar charts and metrics |
            | **Configuration** | python-dotenv | Secure API credential management via `.env` |
            | **Testing** | pytest | Automated test coverage across all modules |
            """
        )

    with col_right:
        # 4. Brief Module Descriptions
        st.markdown("### 🧭 Dashboard Modules")
        st.markdown(
            """
            - **🏏 Live Match:** View live ongoing, recent completed, and upcoming matches from Cricbuzz API with full innings scorecards.
            - **📊 Top Player Stats:** Explore live API top stats (runs, wickets, averages) and historical database leaderboards.
            - **🔍 SQL Queries & Analytics:** Execute the 25 required SQL questions and run custom queries with the interactive runner.
            - **⚙️ CRUD Operations:** Add, update, and manage players and matches with form validation and referential integrity.
            """
        )

        # 5. Navigation & Documentation
        st.markdown("### 📖 Documentation & Setup")
        st.markdown(
            """
            - **Sidebar Navigation:** Use the left sidebar to switch between any of the 5 modules.
            - **Database Schema:** Defined in `database/schema.sql` (10 relational tables).
            - **SQL Queries:** Complete reference list of queries in `sql/queries.sql`.
            - **API Testing Notebook:** Explore `notebooks/data_fetching.ipynb` for step-by-step pipeline demonstrations.
            - **Setup & Execution:** Refer to `README.md` for virtual environment setup and pytest execution.
            """
        )


def main() -> None:
    inject_css()
    try:
        boot_database()
    except Exception as exc:
        friendly_error("Database initialization", exc)

    # Clean, single sidebar navigation
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand"><b>🏏 Cricbuzz LiveStats</b><small>Cricket Analytics Dashboard</small></div>',
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Navigation Menu",
            ["Home", "Live Match", "Top Player Stats", "SQL Queries & Analytics", "CRUD Operations"],
            label_visibility="collapsed",
        )
        st.markdown(
            '<div class="sidebar-footer"><span class="status-dot"></span> <b>Database:</b> SQLite Ready<br><span class="status-dot"></span> <b>API Key:</b> Protected in .env</div>',
            unsafe_allow_html=True,
        )

    if page == "Home":
        render_home()
    elif page == "Live Match":
        render_live_match_page()
    elif page == "Top Player Stats":
        render_player_stats_page()
    elif page == "SQL Queries & Analytics":
        render_sql_analytics_page()
    else:
        render_crud_page()


if __name__ == "__main__":
    main()