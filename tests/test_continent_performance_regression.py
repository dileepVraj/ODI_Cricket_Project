import pandas as pd

from formats.odi.engines.team import TeamEngine


def _make_engine_with_df(df: pd.DataFrame) -> TeamEngine:
    engine = TeamEngine.__new__(TeamEngine)
    engine.dal = None
    engine.match_df = df
    engine._reference_date = pd.Timestamp("2026-01-01")
    return engine


def test_continent_mask_uses_venue_fallback_when_venue_id_missing() -> None:
    engine = TeamEngine.__new__(TeamEngine)
    df = pd.DataFrame(
        [
            {"venue": "IND_BANGALORE", "venue_id": None},
            {"venue": "ENG_LORDS", "venue_id": "ENG_LORDS"},
        ]
    )

    mask = engine._build_continent_mask(df, "Asia")

    assert bool(mask.iloc[0]) is True
    assert bool(mask.iloc[1]) is False


def test_continent_perf_home_vs_away_in_asia_includes_bangalore_and_returns_match_card_rows() -> None:
    df = pd.DataFrame(
        [
            {
                "match_id": "1384416",
                "start_date": "2023-10-26",
                "team_bat_1": "England",
                "team_bat_2": "Sri Lanka",
                "winner": "Sri Lanka",
                "venue": "IND_BANGALORE",
                "venue_id": None,
                "score_inn1": 156,
                "score_inn2": 160,
            },
            {
                "match_id": "2000001",
                "start_date": "2023-07-01",
                "team_bat_1": "England",
                "team_bat_2": "Sri Lanka",
                "winner": "England",
                "venue": "ENG_LORDS",
                "venue_id": "ENG_LORDS",
                "score_inn1": 300,
                "score_inn2": 250,
            },
        ]
    )

    engine = _make_engine_with_df(df)
    rows = engine.analyze_continent_performance(
        team_name="Sri Lanka",
        continent="Asia",
        opp_team="England",
        years_back=10,
    )

    match_count = next(r["Value"] for r in rows if r.get("Metric") == "Matches Played")
    assert match_count == 1
    assert any(r.get("Metric") == "Sri Lanka Last 5" for r in rows)
    assert any(r.get("Metric") == "England Last 5" for r in rows)


def test_continent_perf_home_vs_all_still_returns_matrix_rows() -> None:
    df = pd.DataFrame(
        [
            {
                "match_id": "1384416",
                "start_date": "2023-10-26",
                "team_bat_1": "England",
                "team_bat_2": "Sri Lanka",
                "winner": "Sri Lanka",
                "venue": "IND_BANGALORE",
                "venue_id": None,
                "score_inn1": 156,
                "score_inn2": 160,
            },
            {
                "match_id": "2000002",
                "start_date": "2022-07-01",
                "team_bat_1": "India",
                "team_bat_2": "Sri Lanka",
                "winner": "India",
                "venue": "IND_MUMBAI_WANKHEDE",
                "venue_id": "IND_MUMBAI_WANKHEDE",
                "score_inn1": 300,
                "score_inn2": 270,
            },
        ]
    )

    engine = _make_engine_with_df(df)
    rows = engine.analyze_continent_performance(
        team_name="Sri Lanka",
        continent="Asia",
        opp_team="All",
        years_back=10,
    )

    assert isinstance(rows, list)
    assert len(rows) > 0
    assert "Opponent" in rows[0]
