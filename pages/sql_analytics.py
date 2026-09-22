"""Interactive SQL Analytics page for 25 required practice questions and custom query runner."""

from __future__ import annotations

import time
import plotly.express as px
import streamlit as st

from database.connection import get_connection, query_df
from sql.query_metadata import QUERIES
from utils.error_handler import friendly_error
from utils.helpers import render_header, render_metric_card


SCHEMA_HINTS = {
    "teams": ["team_id", "name", "country", "short_code"],
    "venues": ["venue_id", "name", "city", "country", "capacity"],
    "series": ["series_id", "name", "host_country", "match_type", "start_date", "planned_matches"],
    "players": ["player_id", "full_name", "role", "batting_style", "bowling_style", "country", "team_id", "active"],
    "matches": ["match_id", "description", "match_date", "format", "status", "venue_id", "series_id", "team_a_id", "team_b_id", "winner_team_id", "victory_margin", "victory_type", "toss_winner_id", "toss_decision"],
    "innings": ["innings_id", "match_id", "innings_number", "batting_team_id", "bowling_team_id", "total_runs", "wickets_lost"],
    "batting_performances": ["batting_id", "innings_id", "player_id", "batting_position", "runs_scored", "balls_faced", "fours", "sixes", "dismissal"],
    "bowling_performances": ["bowling_id", "innings_id", "player_id", "overs", "runs_conceded", "wickets_taken", "maidens"],
    "fielding_performances": ["fielding_id", "match_id", "player_id", "catches", "stumpings", "run_outs"],
    "partnerships": ["partnership_id", "innings_id", "player_one_id", "player_two_id", "player_one_position", "player_two_position", "partnership_runs"],
}


def render_practice_queries_tab() -> None:
    """Render the 25 required practice SQL questions."""
    diff_filter = st.radio(
        "Filter by Level",
        ["All Levels (25)", "Beginner (1-8)", "Intermediate (9-16)", "Advanced (17-25)"],
        horizontal=True,
        key="sql-diff-filter",
    )

    if diff_filter.startswith("Beginner"):
        filtered_queries = [q for q in QUERIES if q.difficulty == "Beginner"]
    elif diff_filter.startswith("Intermediate"):
        filtered_queries = [q for q in QUERIES if q.difficulty == "Intermediate"]
    elif diff_filter.startswith("Advanced"):
        filtered_queries = [q for q in QUERIES if q.difficulty == "Advanced"]
    else:
        filtered_queries = QUERIES

    labels = [f"Q{item.number:02d} · {item.title} · [{item.difficulty}]" for item in filtered_queries]
    selected_label = st.selectbox("Choose a Question", labels, key="sql-question-selector")
    item = filtered_queries[labels.index(selected_label)]

    st.markdown(f"### Q{item.number:02d}: {item.title}")
    st.info(f"**Question:** {item.question}")
    st.caption(f"**Difficulty:** {item.difficulty} | **Demonstrates:** {item.demonstrates}")

    with st.expander("📄 View SQL Query", expanded=True):
        st.code(item.sql, language="sql")

    if st.button(f"▶ Run Q{item.number:02d} Query", key="sql-execute-button"):
        try:
            start_t = time.perf_counter()
            result = query_df(item.sql)
            elapsed_ms = (time.perf_counter() - start_t) * 1000

            st.success(f"Query executed in {elapsed_ms:.2f} ms · {len(result):,} rows returned")

            if result.empty:
                st.info("The query executed successfully, but returned 0 rows for the current filter.")
            else:
                st.dataframe(result, use_container_width=True, hide_index=True)

                # Optional automatic chart
                numeric_cols = result.select_dtypes(include="number").columns.tolist()
                if numeric_cols and 1 < len(result) <= 30:
                    x_col = result.columns[0]
                    y_col = numeric_cols[-1]
                    fig = px.bar(
                        result.head(15),
                        x=x_col,
                        y=y_col,
                        title=f"Visualization: {item.title}",
                        color=y_col,
                        color_continuous_scale="Tealgrn",
                    )
                    fig.update_layout(height=350, margin=dict(l=10, r=10, t=45, b=10))
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as exc:
            friendly_error(f"Q{item.number:02d} Execution", exc)


def render_custom_query_tab() -> None:
    """Render custom SQL runner with schema browser."""
    st.markdown("### Custom SQL Query Interface")
    st.markdown("Write and execute any custom `SELECT` or `WITH` queries against the SQLite database.")

    with st.expander("📚 Database Schema & Available Tables", expanded=False):
        for table, cols in SCHEMA_HINTS.items():
            st.markdown(f"- **`{table}`**: `{', '.join(cols)}`")

    default_query = """SELECT 
    p.full_name, 
    p.country, 
    p.role, 
    SUM(b.runs_scored) AS total_runs
FROM players p
JOIN batting_performances b ON b.player_id = p.player_id
GROUP BY p.player_id
ORDER BY total_runs DESC
LIMIT 10;"""

    user_sql = st.text_area(
        "Enter SQL Query (Read-only SELECT / WITH)",
        value=default_query,
        height=180,
        key="custom-sql-input",
    )

    if st.button("▶ Execute Custom SQL", key="custom-sql-run-btn"):
        trimmed = user_sql.strip().lower()
        if not (trimmed.startswith("select") or trimmed.startswith("with")):
            st.error("For database safety, only read-only SELECT and WITH statements are permitted in this runner.")
            return

        try:
            start_t = time.perf_counter()
            df = query_df(user_sql)
            elapsed_ms = (time.perf_counter() - start_t) * 1000

            st.success(f"Executed successfully in {elapsed_ms:.2f} ms · {len(df):,} rows returned")
            st.dataframe(df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Result as CSV",
                data=csv,
                file_name="query_result.csv",
                mime="text/csv",
            )
        except Exception as exc:
            friendly_error("Custom SQL Execution", exc)


def render_sql_analytics_page() -> None:
    render_header(
        "SQL Queries & Analytics",
        "Run the complete 25 SQL practice questions and execute custom queries on the relational cricket database.",
        "QUERY LAB / SQL",
    )

    # Metrics row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("BEGINNER", "08", "Q1 – Q8")
    with c2:
        render_metric_card("INTERMEDIATE", "08", "Q9 – Q16")
    with c3:
        render_metric_card("ADVANCED", "09", "Q17 – Q25")
    with c4:
        render_metric_card("TOTAL QUERIES", "25", "100% Tested")

    tabs = st.tabs(["📋 25 Required Practice Queries", "💻 Custom SQL Query Runner"])
    with tabs[0]:
        render_practice_queries_tab()
    with tabs[1]:
        render_custom_query_tab()