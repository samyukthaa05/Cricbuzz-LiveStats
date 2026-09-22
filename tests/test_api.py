from api.cricbuzz_api import (
    ApiResult,
    api_configured,
    normalize_match_cards,
    parse_scorecard,
)


def test_api_configured_returns_bool():
    assert isinstance(api_configured(), bool)


def test_api_empty_state_does_not_crash():
    assert normalize_match_cards(ApiResult(False, error="offline")) == []


def test_normalize_common_match_shape():
    result = ApiResult(True, {"matches": [{"matchInfo": {"matchDesc": "Demo"}}]})
    cards = normalize_match_cards(result)
    assert len(cards) == 1
    assert cards[0]["matchInfo"]["matchDesc"] == "Demo"


def test_parse_scorecard():
    sample_payload = {
        "scoreCard": [
            {
                "batteamname": "India",
                "score": 180,
                "wickets": 4,
                "overs": 20.0,
                "runrate": "9.0",
                "batsman": [
                    {
                        "name": "Virat Kohli",
                        "runs": 82,
                        "balls": 53,
                        "fours": 6,
                        "sixes": 4,
                        "strkrate": "154.7",
                        "outdec": "not out",
                    }
                ],
                "bowler": [
                    {
                        "name": "Mitchell Starc",
                        "overs": 4.0,
                        "maidens": 0,
                        "runs": 32,
                        "wickets": 2,
                        "economy": 8.0,
                    }
                ],
            }
        ]
    }
    parsed = parse_scorecard(sample_payload)
    assert len(parsed) == 1
    assert parsed[0]["team_name"] == "India"
    assert parsed[0]["score"] == 180
    assert len(parsed[0]["batsmen"]) == 1
    assert parsed[0]["batsmen"][0]["Batter"] == "Virat Kohli"
    assert len(parsed[0]["bowlers"]) == 1
    assert parsed[0]["bowlers"][0]["Bowler"] == "Mitchell Starc"