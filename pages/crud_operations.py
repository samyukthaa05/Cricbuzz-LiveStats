"""Full validated CRUD interface for Players and Matches."""

from __future__ import annotations

import datetime as dt
import streamlit as st

from database.crud import (
    create_match,
    create_player,
    delete_match,
    delete_player,
    list_matches,
    list_players,
    list_series,
    list_teams,
    list_venues,
    update_match,
    update_player,
    update_player_active,
)
from utils.error_handler import friendly_error
from utils.helpers import render_header
from utils.validation import FORMATS, MATCH_STATUSES, ROLES, TOSS_DECISIONS, VICTORY_TYPES


def render_player_crud_tabs() -> None:
    """Render Player CRUD operations."""
    tabs = st.tabs(["Browse & Search", "Add Player", "Update Player", "Delete Player"])
    teams_df = list_teams()
    team_options = {f"{row['name']} ({row['country']})": int(row["team_id"]) for _, row in teams_df.iterrows()}

    # Browse & Search
    with tabs[0]:
        search = st.text_input("Search players by name, country, or role", key="crud-player-search")
        try:
            records = list_players(search)
            st.dataframe(records, use_container_width=True, hide_index=True)
            st.caption(f"{len(records)} player records found.")
        except Exception as exc:
            friendly_error("Read players", exc)

    # Add Player
    with tabs[1]:
        with st.form("create-player-form", clear_on_submit=True):
            full_name = st.text_input("Full Name", placeholder="e.g. Shubman Gill")
            role = st.selectbox("Playing Role", ROLES)
            batting_style = st.text_input("Batting Style", value="Right-hand")
            bowling_style = st.text_input("Bowling Style", value="Right-arm off break")
            country = st.text_input("Country", value="India")
            team_label = st.selectbox("Team", list(team_options.keys()))
            submitted = st.form_submit_button("➕ Create Player")

        if submitted:
            try:
                player_id = create_player({
                    "full_name": full_name,
                    "role": role,
                    "batting_style": batting_style,
                    "bowling_style": bowling_style,
                    "country": country,
                    "team_id": team_options[team_label],
                })
                st.success(f"Player '{full_name}' created successfully with Player ID {player_id}.")
            except Exception as exc:
                friendly_error("Create player", exc)

    # Update Player
    with tabs[2]:
        records = list_players()
        if records.empty:
            st.info("No player records available to update.")
        else:
            player_map = {f"{row['full_name']} (ID: {row['player_id']}, {row['country']})": row for _, row in records.iterrows()}
            selected = st.selectbox("Select Player to Edit", list(player_map.keys()), key="crud-player-update-selector")
            row = player_map[selected]

            with st.form("update-player-form"):
                full_name = st.text_input("Full Name", str(row["full_name"]))
                role_idx = ROLES.index(row["role"]) if row["role"] in ROLES else 0
                role = st.selectbox("Playing Role", ROLES, index=role_idx)
                batting_style = st.text_input("Batting Style", str(row["batting_style"]))
                bowling_style = st.text_input("Bowling Style", str(row["bowling_style"]))
                country = st.text_input("Country", str(row["country"]))

                current_team_id = int(row["team_id"])
                team_labels = list(team_options.keys())
                team_vals = list(team_options.values())
                team_idx = team_vals.index(current_team_id) if current_team_id in team_vals else 0
                team_label = st.selectbox("Team", team_labels, index=team_idx)
                active = st.checkbox("Active Roster", value=bool(row["active"]))

                saved = st.form_submit_button("💾 Save Player Changes")

            if saved:
                try:
                    update_player(int(row["player_id"]), {
                        "full_name": full_name,
                        "role": role,
                        "batting_style": batting_style,
                        "bowling_style": bowling_style,
                        "country": country,
                        "team_id": team_options[team_label],
                    })
                    update_player_active(int(row["player_id"]), active)
                    st.success("Player record updated successfully.")
                except Exception as exc:
                    friendly_error("Update player", exc)

    # Delete Player
    with tabs[3]:
        records = list_players()
        if records.empty:
            st.info("No player records available.")
        else:
            player_map = {f"{row['full_name']} (ID: {row['player_id']})": row for _, row in records.iterrows()}
            selected = st.selectbox("Select Player to Delete", list(player_map.keys()), key="crud-player-delete-selector")
            row = player_map[selected]
            st.warning("⚠️ Deleting a player with recorded match performances is blocked by referential integrity. You can mark them inactive in the Update tab instead.")
            confirm = st.checkbox("I confirm I want to permanently delete this player", key="crud-player-delete-confirm")
            if st.button("🗑 Delete Player", disabled=not confirm, key="crud-player-delete-btn"):
                try:
                    delete_player(int(row["player_id"]))
                    st.success("Player record deleted successfully.")
                    st.rerun()
                except Exception as exc:
                    friendly_error("Delete player", exc)


def render_match_crud_tabs() -> None:
    """Render Match CRUD operations."""
    tabs = st.tabs(["Browse & Search Matches", "Schedule/Add Match", "Update Match", "Delete Match"])
    teams_df = list_teams()
    team_opts = {row["name"]: int(row["team_id"]) for _, row in teams_df.iterrows()}
    venues_df = list_venues()
    venue_opts = {f"{row['name']} ({row['city']})": int(row["venue_id"]) for _, row in venues_df.iterrows()}
    series_df = list_series()
    series_opts = {"None / Bilateral": None}
    series_opts.update({f"{row['name']}": int(row["series_id"]) for _, row in series_df.iterrows()})

    # Browse Matches
    with tabs[0]:
        search_m = st.text_input("Search matches by team, description, or venue", key="crud-match-search")
        try:
            matches = list_matches(search_m)
            st.dataframe(matches, use_container_width=True, hide_index=True)
            st.caption(f"{len(matches)} match records displayed.")
        except Exception as exc:
            friendly_error("Read matches", exc)

    # Add Match
    with tabs[1]:
        with st.form("create-match-form", clear_on_submit=True):
            description = st.text_input("Match Description", placeholder="e.g. 1st ODI - IND vs AUS")
            match_date = st.date_input("Match Date", value=dt.date.today())
            match_format = st.selectbox("Format", FORMATS)
            status = st.selectbox("Status", MATCH_STATUSES)
            venue_label = st.selectbox("Venue", list(venue_opts.keys()))
            series_label = st.selectbox("Series", list(series_opts.keys()))

            c1, c2 = st.columns(2)
            with c1:
                team_a_label = st.selectbox("Team A", list(team_opts.keys()), index=0)
            with c2:
                team_b_label = st.selectbox("Team B", list(team_opts.keys()), index=min(1, len(team_opts) - 1))

            st.markdown("##### Toss & Results (Optional)")
            c3, c4 = st.columns(2)
            with c3:
                toss_opts = ["None"] + list(team_opts.keys())
                toss_winner_label = st.selectbox("Toss Winner", toss_opts)
                toss_decision = st.selectbox("Toss Decision", ["None"] + list(TOSS_DECISIONS))
            with c4:
                winner_opts = ["None"] + list(team_opts.keys())
                winner_label = st.selectbox("Match Winner", winner_opts)
                victory_type = st.selectbox("Victory Type", ["None"] + list(VICTORY_TYPES))
                victory_margin = st.number_input("Victory Margin", min_value=0, value=0, step=1)

            submitted_match = st.form_submit_button("➕ Create Match")

        if submitted_match:
            try:
                m_payload = {
                    "description": description,
                    "match_date": match_date.isoformat(),
                    "format": match_format,
                    "status": status,
                    "venue_id": venue_opts[venue_label],
                    "series_id": series_opts[series_label],
                    "team_a_id": team_opts[team_a_label],
                    "team_b_id": team_opts[team_b_label],
                    "winner_team_id": team_opts[winner_label] if winner_label != "None" else None,
                    "victory_margin": victory_margin,
                    "victory_type": victory_type if victory_type != "None" else None,
                    "toss_winner_id": team_opts[toss_winner_label] if toss_winner_label != "None" else None,
                    "toss_decision": toss_decision if toss_decision != "None" else None,
                }
                new_id = create_match(m_payload)
                st.success(f"Match created successfully with ID {new_id}.")
            except Exception as exc:
                friendly_error("Create match", exc)

    # Update Match
    with tabs[2]:
        all_matches = list_matches(limit=100)
        if all_matches.empty:
            st.info("No matches available.")
        else:
            match_map = {f"#{row['match_id']}: {row['description']} ({row['match_date']})": row for _, row in all_matches.iterrows()}
            chosen_m = st.selectbox("Select Match to Edit", list(match_map.keys()), key="crud-match-update-sel")
            m_row = match_map[chosen_m]
            m_id = int(m_row["match_id"])

            with st.form("update-match-form"):
                u_desc = st.text_input("Description", str(m_row["description"]))
                try:
                    parsed_d = dt.date.fromisoformat(str(m_row["match_date"])[:10])
                except Exception:
                    parsed_d = dt.date.today()
                u_date = st.date_input("Match Date", value=parsed_d)
                u_fmt_idx = FORMATS.index(m_row["format"]) if m_row["format"] in FORMATS else 0
                u_format = st.selectbox("Format", FORMATS, index=u_fmt_idx)

                u_stat_idx = MATCH_STATUSES.index(m_row["status"]) if m_row["status"] in MATCH_STATUSES else 0
                u_status = st.selectbox("Status", MATCH_STATUSES, index=u_stat_idx)

                u_winner = st.selectbox("Winner Team", ["None"] + list(team_opts.keys()))
                u_margin = st.number_input("Victory Margin", min_value=0, value=int(m_row["victory_margin"] or 0))
                u_vtype = st.selectbox("Victory Type", ["None"] + list(VICTORY_TYPES))

                updated_btn = st.form_submit_button("💾 Save Match Changes")

            if updated_btn:
                try:
                    # Update fields
                    team_a_id = team_opts.get(m_row["team_a"]) or 1
                    team_b_id = team_opts.get(m_row["team_b"]) or 2
                    update_match(m_id, {
                        "description": u_desc,
                        "match_date": u_date.isoformat(),
                        "format": u_format,
                        "status": u_status,
                        "venue_id": 1,
                        "series_id": None,
                        "team_a_id": team_a_id,
                        "team_b_id": team_b_id,
                        "winner_team_id": team_opts.get(u_winner) if u_winner != "None" else None,
                        "victory_margin": u_margin,
                        "victory_type": u_vtype if u_vtype != "None" else None,
                        "toss_winner_id": None,
                        "toss_decision": None,
                    })
                    st.success(f"Match #{m_id} updated successfully.")
                except Exception as exc:
                    friendly_error("Update match", exc)

    # Delete Match
    with tabs[3]:
        all_matches = list_matches(limit=100)
        if all_matches.empty:
            st.info("No matches available.")
        else:
            match_map = {f"#{row['match_id']}: {row['description']}": row for _, row in all_matches.iterrows()}
            chosen_del = st.selectbox("Select Match to Delete", list(match_map.keys()), key="crud-match-del-sel")
            m_del_row = match_map[chosen_del]
            m_del_id = int(m_del_row["match_id"])
            st.warning(f"⚠️ Deleting Match #{m_del_id} will also cascade delete associated innings and ball performance records.")
            confirm_del = st.checkbox("I confirm I want to permanently delete this match", key="del-m-confirm")
            if st.button("🗑 Delete Match", disabled=not confirm_del, key="del-m-btn"):
                try:
                    delete_match(m_del_id)
                    st.success(f"Match #{m_del_id} deleted successfully.")
                    st.rerun()
                except Exception as exc:
                    friendly_error("Delete match", exc)


def render_crud_page() -> None:
    render_header(
        "CRUD Operations",
        "Perform full Create, Read, Update, and Delete operations on players and matches.",
        "DATA OPS / CRUD",
    )

    main_tabs = st.tabs(["👤 Player Management", "🏏 Match Management"])
    with main_tabs[0]:
        render_player_crud_tabs()
    with main_tabs[1]:
        render_match_crud_tabs()