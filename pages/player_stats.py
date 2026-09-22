"""Top player statistics page combining live Cricbuzz API stats and relational database analytics."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.player_analytics import batting_leaderboard, bowling_leaderboard
from api.cricbuzz_api import api_configured, fetch_rankings, fetch_top_stats
from database.connection import query_df
from utils.error_handler import friendly_error
from utils.helpers import render_header, render_metric_card


TOP_STATS_MAP = {
    "Most Runs": ("mostRuns", "R", "Runs"),
    "Highest Individual Score": ("highestScore", "HS", "Highest Score"),
    "Best Batting Average": ("highestAvg", "Avg", "Average"),
    "Best Batting Strike Rate": ("highestSr", "SR", "Strike Rate"),
    "Most Hundreds": ("mostHundreds", "100", "Hundreds"),
    "Most Fifties": ("mostFifties", "50", "Fifties"),
    "Most Wickets": ("mostWickets", "W", "Wickets"),
    "Best Bowling Economy": ("lowestEcon", "Eco", "Economy"),
    "Best Bowling Average": ("lowestAvg", "Avg", "Average"),
    "Best Bowling Strike Rate": ("lowestSr", "SR", "Strike Rate"),
    "Most 5-Wicket Hauls": ("mostFiveWickets", "5W", "5-Wickets"),
}


def render_cricbuzz_api_stats_tab() -> None:
    """Render top player stats directly fetched via Cricbuzz REST API."""
    if not api_configured():
        st.warning("Cricbuzz API is not configured. Add CRICBUZZ_API_KEY to .env to view live top stats.")
        return

    sub_tabs = st.tabs(["Top Leaders Categories", "ICC Rankings"])

    with sub_tabs[0]:
        st.markdown("##### Select Statistics Category (from Cricbuzz API)")
        selected_category = st.selectbox(
            "Category",
            list(TOP_STATS_MAP.keys()),
            key="api-top-stats-category",
        )
        endpoint_key, metric_col_short, metric_label = TOP_STATS_MAP[selected_category]

        with st.spinner("Fetching stats from Cricbuzz API..."):
            res = fetch_top_stats(endpoint_key)

        if not res.ok or not isinstance(res.data, dict):
            st.error(f"Failed to fetch {selected_category}: {res.error}")
            return

        headers = res.data.get("headers", [])
        values = [v.get("values", []) for v in res.data.get("values", []) if isinstance(v, dict)]

        if not headers or not values:
            st.info("No statistics returned for this category.")
            return

        # Align headers with values (often first value is player ID)
        if len(values[0]) == len(headers) + 1:
            cols = ["Player ID"] + headers
            df = pd.DataFrame(values, columns=cols)
            display_df = df.drop(columns=["Player ID"])
        else:
            display_df = pd.DataFrame(values, columns=headers[:len(values[0])])

        st.markdown(f"**Top Performers: {selected_category}** ({len(display_df)} players)")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Plot top 10 chart if a numeric metric column exists
        chart_col = None
        for candidate in [metric_col_short, "R", "W", "HS", "Eco", "Avg", "SR"]:
            if candidate in display_df.columns:
                chart_col = candidate
                break

        name_col = "Batter" if "Batter" in display_df.columns else "Bowler" if "Bowler" in display_df.columns else display_df.columns[0]

        if chart_col and name_col in display_df.columns:
            try:
                plot_df = display_df.head(10).copy()
                plot_df[chart_col] = pd.to_numeric(plot_df[chart_col].astype(str).str.replace("*", "", regex=False), errors="coerce")
                fig = px.bar(
                    plot_df,
                    x=name_col,
                    y=chart_col,
                    title=f"Top 10 - {selected_category} ({chart_col})",
                    color=chart_col,
                    color_continuous_scale="Viridis",
                )
                fig.update_layout(xaxis_tickangle=-30, height=380, margin=dict(l=10, r=10, t=45, b=10))
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                pass

    with sub_tabs[1]:
        st.markdown("##### ICC Player Rankings")
        c1, c2 = st.columns(2)
        with c1:
            rank_category = st.selectbox("Rank Category", ["batsmen", "bowlers", "allrounders", "teams"], key="icc-category")
        with c2:
            rank_format = st.selectbox("Format", ["test", "odi", "t20"], key="icc-format")

        with st.spinner("Fetching ICC rankings..."):
            rank_res = fetch_rankings(rank_category, rank_format)

        if rank_res.ok and isinstance(rank_res.data, dict):
            ranks = rank_res.data.get("rank", [])
            if ranks:
                rank_rows = []
                for r in ranks:
                    if isinstance(r, dict):
                        rank_rows.append({
                            "Rank": r.get("rank"),
                            "Name": r.get("name"),
                            "Country": r.get("country"),
                            "Rating": r.get("rating"),
                            "Trend": r.get("trend"),
                        })
                rank_df = pd.DataFrame(rank_rows)
                st.dataframe(rank_df, use_container_width=True, hide_index=True)
            else:
                st.info("No rankings data available for selected category.")
        else:
            st.info("Rankings endpoint currently unavailable or quota reached.")


def render_database_stats_tab() -> None:
    """Render historical player statistics from local SQLite database."""
    formats = ["All", "Test", "ODI", "T20I"]
    selected_format = st.selectbox("Filter Format", formats, key="db-player-format-filter")

    try:
        batting = batting_leaderboard(selected_format)
        bowling = bowling_leaderboard(selected_format)
        total_runs = int(batting["runs"].sum()) if not batting.empty else 0
        total_wickets = int(bowling["wickets"].sum()) if not bowling.empty else 0
        player_count = int(query_df("SELECT COUNT(*) count FROM players WHERE active=1").iloc[0]["count"])

        a, b, c = st.columns(3)
        with a:
            render_metric_card("ACTIVE PLAYERS", f"{player_count}", "Roster count")
        with b:
            render_metric_card("LEADING RUNS", f"{total_runs:,}", "Top 10 combined")
        with c:
            render_metric_card("LEADING WICKETS", f"{total_wickets:,}", "Top 10 combined")

        left, right = st.columns(2)
        with left:
            st.markdown("### Batting Leaders (Runs)")
            st.dataframe(batting, use_container_width=True, hide_index=True)
            if not batting.empty:
                figure = px.bar(
                    batting.head(8),
                    x="runs",
                    y="player",
                    orientation="h",
                    title="Runs Scored",
                    color="runs",
                    color_continuous_scale="Reds",
                )
                figure.update_layout(height=350, margin=dict(l=10, r=10, t=45, b=10))
                st.plotly_chart(figure, use_container_width=True)

        with right:
            st.markdown("### Bowling Leaders (Wickets)")
            st.dataframe(bowling, use_container_width=True, hide_index=True)
            if not bowling.empty:
                figure = px.bar(
                    bowling.head(8),
                    x="wickets",
                    y="player",
                    orientation="h",
                    title="Wickets Taken",
                    color="wickets",
                    color_continuous_scale="Blues",
                )
                figure.update_layout(height=350, margin=dict(l=10, r=10, t=45, b=10))
                st.plotly_chart(figure, use_container_width=True)

        st.caption("Source: Local relational database (SQLite).")
    except Exception as exc:
        friendly_error("Player analytics", exc)


def render_player_stats_page() -> None:
    render_header(
        "Top Player Stats",
        "View top batting and bowling leaders from Cricbuzz API and local database analytics.",
        "ANALYTICS / PLAYERS",
    )

    tabs = st.tabs(["⚡ Cricbuzz API Top Stats", "📊 Database Historical Stats"])
    with tabs[0]:
        render_cricbuzz_api_stats_tab()
    with tabs[1]:
        render_database_stats_tab()