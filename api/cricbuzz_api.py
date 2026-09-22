"""Configuration-driven Cricbuzz REST client with safe failure states.

The client connects to Cricbuzz via RapidAPI using credentials in .env.
If credentials or network are offline, it returns honest, safe error states
without crashing the application.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
import urllib3
import requests
import streamlit as st

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class ApiResult:
    ok: bool
    data: dict[str, Any] | list[Any] | None = None
    error: str | None = None
    source: str = "LIVE API DATA"


def api_configured() -> bool:
    """Check if API key and host are configured."""
    return bool(settings.api_key and settings.api_host)


def _get_headers() -> dict[str, str]:
    return {
        "x-rapidapi-key": settings.api_key,
        "x-rapidapi-host": settings.api_host,
    }


def safe_api_get(endpoint: str, params: dict[str, Any] | None = None) -> ApiResult:
    """Execute a safe GET request to the Cricbuzz RapidAPI with SSL resilience."""
    if not api_configured():
        return ApiResult(
            False,
            error="Live API credentials are not configured. Add CRICBUZZ_API_KEY and CRICBUZZ_API_HOST to .env.",
        )

    url = f"{settings.api_base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = _get_headers()

    try:
        # First attempt with configured SSL verification
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=settings.timeout_seconds,
            verify=settings.verify_ssl,
        )
        response.raise_for_status()
        payload = response.json()
        return ApiResult(True, payload)
    except requests.exceptions.SSLError:
        # Windows CA fallback: retry with verify=False if local certificates are unlinked
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=settings.timeout_seconds,
                verify=False,
            )
            response.raise_for_status()
            payload = response.json()
            return ApiResult(True, payload)
        except Exception as exc:
            return ApiResult(False, error=f"SSL/TLS connection error: {exc}")
    except requests.Timeout:
        return ApiResult(
            False,
            error=f"API request timed out after {settings.timeout_seconds}s. Database analytics remain available.",
        )
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "Unknown"
        return ApiResult(
            False,
            error=f"API returned HTTP {status_code}. Check RapidAPI subscription and endpoint quota.",
        )
    except (requests.RequestException, ValueError) as exc:
        return ApiResult(
            False,
            error=f"Live API data is currently unavailable ({type(exc).__name__}: {exc}).",
        )


@st.cache_data(ttl=30, show_spinner=False)
def fetch_live_matches() -> ApiResult:
    """Poll live matches from /matches/v1/live."""
    return safe_api_get("matches/v1/live")


@st.cache_data(ttl=60, show_spinner=False)
def fetch_recent_matches() -> ApiResult:
    """Fetch completed and recent matches from /matches/v1/recent."""
    return safe_api_get("matches/v1/recent")


@st.cache_data(ttl=120, show_spinner=False)
def fetch_upcoming_matches() -> ApiResult:
    """Fetch upcoming scheduled matches from /matches/v1/upcoming."""
    return safe_api_get("matches/v1/upcoming")


@st.cache_data(ttl=30, show_spinner=False)
def fetch_match_scorecard(match_id: int | str) -> ApiResult:
    """Fetch full detailed match scorecard from /mcenter/v1/{match_id}/scard."""
    return safe_api_get(f"mcenter/v1/{match_id}/scard")


@st.cache_data(ttl=30, show_spinner=False)
def fetch_match_miniscorecard(match_id: int | str) -> ApiResult:
    """Fetch mini scorecard from /mcenter/v1/{match_id}/hscard."""
    return safe_api_get(f"mcenter/v1/{match_id}/hscard")


@st.cache_data(ttl=300, show_spinner=False)
def fetch_top_stats(stats_type: str = "mostRuns") -> ApiResult:
    """Fetch top batting or bowling statistics from /stats/v1/topstats/0?statsType=..."""
    return safe_api_get("stats/v1/topstats/0", params={"statsType": stats_type})


@st.cache_data(ttl=300, show_spinner=False)
def fetch_rankings(category: str = "batsmen", format_type: str = "test") -> ApiResult:
    """Fetch ICC rankings from /stats/v1/rankings/{category}?formatType={format_type}."""
    return safe_api_get(f"stats/v1/rankings/{category}", params={"formatType": format_type})


def normalize_match_cards(result: ApiResult) -> list[dict[str, Any]]:
    """Normalize Cricbuzz match response shapes into a standard list of match dicts."""
    if not result.ok or not isinstance(result.data, dict):
        return []

    type_matches = result.data.get("typeMatches") or result.data.get("matches") or result.data.get("matchInfo") or []
    normalized: list[dict[str, Any]] = []

    for group in type_matches if isinstance(type_matches, list) else []:
        if isinstance(group, dict) and "seriesMatches" in group:
            for series_match in group.get("seriesMatches", []):
                if isinstance(series_match, dict):
                    item = series_match.get("seriesAdWrapper", series_match)
                    matches = item.get("matches", []) if isinstance(item, dict) else []
                    for m in matches:
                        if isinstance(m, dict):
                            # Ensure series name is available
                            if "seriesName" not in m.get("matchInfo", {}) and "seriesName" in item:
                                m.setdefault("matchInfo", {})["seriesName"] = item.get("seriesName")
                            normalized.append(m)
        elif isinstance(group, dict):
            normalized.append(group)

    return normalized


def parse_scorecard(scorecard_data: dict[str, Any] | list[Any] | None) -> list[dict[str, Any]]:
    """Extract innings, batsmen tables, and bowling tables from scorecard payload."""
    if not scorecard_data:
        return []

    raw_innings = []
    if isinstance(scorecard_data, dict):
        raw_innings = scorecard_data.get("scoreCard") or scorecard_data.get("scorecard") or []
    elif isinstance(scorecard_data, list):
        raw_innings = scorecard_data

    parsed_innings: list[dict[str, Any]] = []
    for inn in raw_innings:
        if not isinstance(inn, dict):
            continue

        team_name = inn.get("batteamname") or inn.get("batTeamDetails", {}).get("batTeamName") or "Team"
        score = inn.get("score", 0)
        wickets = inn.get("wickets", 0)
        overs = inn.get("overs", 0)
        run_rate = inn.get("runrate") or inn.get("runRate", "")

        # Extract batsmen
        batsmen_list: list[dict[str, Any]] = []
        raw_batsmen = inn.get("batsman") or inn.get("batTeamDetails", {}).get("batsmenData", {})
        iterable_batsmen = raw_batsmen.values() if isinstance(raw_batsmen, dict) else raw_batsmen
        for b in iterable_batsmen if isinstance(iterable_batsmen, (list, tuple)) else []:
            if isinstance(b, dict):
                name = b.get("name") or b.get("batName") or "Unknown"
                runs = b.get("runs", 0)
                balls = b.get("balls", 0)
                fours = b.get("fours", 0)
                sixes = b.get("sixes", 0)
                sr = b.get("strkrate") or b.get("strikeRate", 0.0)
                dismissal = b.get("outdec") or b.get("outDesc") or "not out"
                batsmen_list.append({
                    "Batter": name,
                    "Runs": runs,
                    "Balls": balls,
                    "4s": fours,
                    "6s": sixes,
                    "SR": sr,
                    "Dismissal": dismissal,
                })

        # Extract bowlers
        bowlers_list: list[dict[str, Any]] = []
        raw_bowlers = inn.get("bowler") or inn.get("bowlTeamDetails", {}).get("bowlersData", {})
        iterable_bowlers = raw_bowlers.values() if isinstance(raw_bowlers, dict) else raw_bowlers
        for bo in iterable_bowlers if isinstance(iterable_bowlers, (list, tuple)) else []:
            if isinstance(bo, dict):
                name = bo.get("name") or bo.get("bowlName") or "Unknown"
                overs_bowled = bo.get("overs", 0)
                maidens = bo.get("maidens", 0)
                runs_conceded = bo.get("runs", 0)
                wickets_taken = bo.get("wickets", 0)
                economy = bo.get("economy", 0.0)
                bowlers_list.append({
                    "Bowler": name,
                    "Overs": overs_bowled,
                    "Maidens": maidens,
                    "Runs": runs_conceded,
                    "Wickets": wickets_taken,
                    "Economy": economy,
                })

        parsed_innings.append({
            "team_name": team_name,
            "score": score,
            "wickets": wickets,
            "overs": overs,
            "run_rate": run_rate,
            "batsmen": batsmen_list,
            "bowlers": bowlers_list,
        })

    return parsed_innings