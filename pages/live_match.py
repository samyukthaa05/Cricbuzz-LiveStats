"""Live match page with real-time Cricbuzz polling and detailed scorecards."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from api.cricbuzz_api import (
    api_configured,
    fetch_live_matches,
    fetch_match_scorecard,
    fetch_recent_matches,
    fetch_upcoming_matches,
    normalize_match_cards,
    parse_scorecard,
)
from utils.error_handler import friendly_error
from utils.helpers import render_header, render_metric_card


def _safe_str(mapping: dict, *keys: str, default: str = "N/A") -> str:
    """Retrieve the first non-empty value from a nested dict."""
    for key in keys:
        val = mapping.get(key)
        if val not in (None, ""):
            return str(val)
    return default


def render_live_match_page() -> None:
    render_header(
        "Live Match & Real-Time Scorecards",
        "Fetch live, recent, and upcoming cricket matches from Cricbuzz REST API.",
        "LIVE / CRICBUZZ API",
    )

    # API Source Status & Refresh Row
    col_status, col_btn = st.columns([3, 1])
    with col_status:
        if api_configured():
            st.success("🟢 Cricbuzz API Connected via .env (RapidAPI)")
        else:
            st.warning("⚠️ Cricbuzz API credentials not configured in .env. Showing offline fallback.")
    with col_btn:
        if st.button("🔄 Refresh Data", key="live-refresh-button", use_container_width=True):
            fetch_live_matches.clear()
            fetch_recent_matches.clear()
            fetch_upcoming_matches.clear()
            fetch_match_scorecard.clear()
            st.rerun()

    # Match Category Selector
    match_category = st.radio(
        "Select Match View",
        ["Live Matches", "Recent Matches", "Upcoming Matches"],
        horizontal=True,
        key="match-category-radio",
    )

    # Fetch corresponding match data
    with st.spinner("Fetching matches from Cricbuzz API..."):
        if match_category == "Live Matches":
            result = fetch_live_matches()
        elif match_category == "Recent Matches":
            result = fetch_recent_matches()
        else:
            result = fetch_upcoming_matches()

    if not result.ok:
        st.error(f"API Error: {result.error}")
        st.info("💡 You can still explore the historical database in Top Player Stats, SQL Queries, and CRUD pages.")
        return

    cards = normalize_match_cards(result)
    if not cards:
        st.info(f"No {match_category.lower()} currently available from Cricbuzz API.")
        return

    # Build dropdown options
    match_options: list[tuple[str, dict]] = []
    for idx, card in enumerate(cards):
        info = card.get("matchInfo", card) if isinstance(card, dict) else {}
        desc = _safe_str(info, "matchDesc", default=f"Match {idx+1}")
        t1 = _safe_str(info.get("team1", {}), "teamName", "teamSName", default="Team 1")
        t2 = _safe_str(info.get("team2", {}), "teamName", "teamSName", default="Team 2")
        series = _safe_str(info, "seriesName", default="")
        label = f"{t1} vs {t2} - {desc}" + (f" ({series})" if series else "")
        match_options.append((label, card))

    labels = [opt[0] for opt in match_options]
    selected_label = st.selectbox("Select a Match to view details", labels, key="match-dropdown-selector")
    selected_card = match_options[labels.index(selected_label)][1]

    info = selected_card.get("matchInfo", selected_card) if isinstance(selected_card, dict) else {}
    match_id = info.get("matchId")
    match_status = _safe_str(info, "status", default="In progress")
    match_desc = _safe_str(info, "matchDesc", default="Match")
    match_format = _safe_str(info, "matchFormat", default="Cricket")
    venue_info = info.get("venueInfo", {})
    venue_name = _safe_str(venue_info, "ground", "name", default="Venue TBA")
    city_name = _safe_str(venue_info, "city", default="")
    full_venue = f"{venue_name}, {city_name}" if city_name else venue_name

    # Header Card
    st.markdown(f"### {match_desc}: {_safe_str(info.get('team1', {}), 'teamName')} vs {_safe_str(info.get('team2', {}), 'teamName')}")
    st.markdown(f"**Status:** `{match_status}`")

    # Metric Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("MATCH FORMAT", match_format, "Format")
    with c2:
        render_metric_card("STATUS", match_status[:20], "Current State")
    with c3:
        render_metric_card("VENUE", venue_name[:18], city_name)
    with c4:
        render_metric_card("MATCH ID", str(match_id or "N/A"), "Cricbuzz ID")

    # Score summary from live card if available
    match_score = selected_card.get("matchScore") or {}
    team1_score = match_score.get("team1Score", {})
    team2_score = match_score.get("team2Score", {})

    if team1_score or team2_score:
        st.markdown("#### Live In-Game Score")
        sc_cols = st.columns(2)
        with sc_cols[0]:
            t1_name = _safe_str(info.get("team1", {}), "teamName", default="Team 1")
            inngs1 = team1_score.get("inngs1", {})
            r = inngs1.get("runs", "-")
            w = inngs1.get("wickets", "-")
            o = inngs1.get("overs", "-")
            st.metric(label=t1_name, value=f"{r}/{w}" if r != "-" else "Yet to bat", delta=f"{o} ov" if o != "-" else None)
        with sc_cols[1]:
            t2_name = _safe_str(info.get("team2", {}), "teamName", default="Team 2")
            inngs1 = team2_score.get("inngs1", {})
            r = inngs1.get("runs", "-")
            w = inngs1.get("wickets", "-")
            o = inngs1.get("overs", "-")
            st.metric(label=t2_name, value=f"{r}/{w}" if r != "-" else "Yet to bat", delta=f"{o} ov" if o != "-" else None)

    # Detailed Scorecard fetching from API
    st.markdown("---")
    st.markdown("#### Detailed Scorecard")

    if not match_id:
        st.info("Match ID is unavailable for detailed scorecard lookup.")
        return

    with st.spinner("Fetching detailed scorecard..."):
        sc_result = fetch_match_scorecard(match_id)

    if sc_result.ok and sc_result.data:
        parsed_innings = parse_scorecard(sc_result.data)
        if parsed_innings:
            for idx, inn in enumerate(parsed_innings, start=1):
                st.markdown(
                    f"##### 🏏 {inn['team_name']} Innings — **{inn['score']}/{inn['wickets']}** ({inn['overs']} Overs)"
                    + (f" · RR: `{inn['run_rate']}`" if inn.get("run_rate") else "")
                )

                # Batting Table
                if inn["batsmen"]:
                    st.markdown("**Batting**")
                    bat_df = pd.DataFrame(inn["batsmen"])
                    st.dataframe(bat_df, use_container_width=True, hide_index=True)
                else:
                    st.caption("Batting details pending.")

                # Bowling Table
                if inn["bowlers"]:
                    st.markdown("**Bowling**")
                    bowl_df = pd.DataFrame(inn["bowlers"])
                    st.dataframe(bowl_df, use_container_width=True, hide_index=True)
                else:
                    st.caption("Bowling details pending.")

                st.markdown("")
        else:
            st.info("Scorecard details are not yet available for this match.")
    else:
        st.info("Scorecard could not be loaded from API for this match.")

    # Raw API JSON viewer for viva/debugging
    with st.expander("🔍 View Raw Cricbuzz API JSON Response"):
        st.json(selected_card)