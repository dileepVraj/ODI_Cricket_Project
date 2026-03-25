"""Unit tests for enriched venue bias calculator helpers."""
import pytest
import pandas as pd
from core.calculators.team.venue_calculator import (
    _wilson_confidence_interval,
    _sample_reliability,
    _score_stats,
    _score_distribution,
    _score_extremes,
    _bias_trend,
    _toss_intelligence,
)


# -- Wilson CI ---------------------------------------------------------------

def test_wilson_ci_zero_denominator():
    result = _wilson_confidence_interval(0, 0)
    assert result == {"lower": 0, "upper": 0}


def test_wilson_ci_fifty_percent():
    result = _wilson_confidence_interval(5, 10)
    assert result["lower"] < 50 < result["upper"]


def test_wilson_ci_high_confidence():
    result = _wilson_confidence_interval(20, 20)
    assert result["lower"] > 70
    assert result["upper"] == 100


def test_wilson_ci_low_confidence():
    result = _wilson_confidence_interval(1, 2)
    assert result["upper"] - result["lower"] > 50


# -- Sample reliability ------------------------------------------------------

def test_sample_reliability_low():
    assert _sample_reliability(8) == "LOW_SAMPLE"


def test_sample_reliability_boundary_low():
    assert _sample_reliability(9) == "LOW_SAMPLE"


def test_sample_reliability_moderate():
    assert _sample_reliability(10) == "MODERATE"
    assert _sample_reliability(24) == "MODERATE"


def test_sample_reliability_reliable():
    assert _sample_reliability(25) == "RELIABLE"
    assert _sample_reliability(100) == "RELIABLE"


# -- Score stats -------------------------------------------------------------

def test_score_stats_empty_series():
    result = _score_stats(pd.Series([], dtype=float))
    assert result == {"min": 0, "max": 0, "median": 0, "std": 0}


def test_score_stats_basic():
    result = _score_stats(pd.Series([200, 250, 300]))
    assert result["min"] == 200
    assert result["max"] == 300
    assert result["median"] == 250


# -- Score extremes ----------------------------------------------------------

def _make_results_df(rows: list[dict[str, str | int | pd.Timestamp]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def test_score_extremes_lowest_defended():
    df = _make_results_df([
        {"match_id": 1, "winner": "TeamA", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 220, "start_date": "2023-01-01"},
        {"match_id": 2, "winner": "TeamA", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 180, "start_date": "2023-01-02"},
        {"match_id": 3, "winner": "TeamB", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 310, "start_date": "2023-01-03"},
    ])
    result = _score_extremes(df)
    assert result["lowest_defended"] == 180


def test_score_extremes_highest_chased():
    df = _make_results_df([
        {"match_id": 1, "winner": "TeamB", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 310, "start_date": "2023-01-01"},
        {"match_id": 2, "winner": "TeamB", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 275, "start_date": "2023-01-02"},
        {"match_id": 3, "winner": "TeamA", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 220, "start_date": "2023-01-03"},
    ])
    result = _score_extremes(df)
    assert result["highest_chased"] == 310


def test_score_extremes_no_defended():
    df = _make_results_df([
        {"match_id": 1, "winner": "TeamB", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 300, "start_date": "2023-01-01"},
    ])
    result = _score_extremes(df)
    assert result["lowest_defended"] is None


# -- Bias trend --------------------------------------------------------------

def _make_trend_df(bat1_wins_per_half: tuple[int, int], total_per_half: int) -> pd.DataFrame:
    rows: list[dict[str, str | int | pd.Timestamp]] = []
    mid = pd.Timestamp("2021-01-01")
    for i in range(total_per_half):
        winner = "TeamA" if i < bat1_wins_per_half[0] else "TeamB"
        rows.append({
            "match_id": i,
            "winner": winner,
            "team_bat_1": "TeamA",
            "team_bat_2": "TeamB",
            "score_inn1": 250,
            "start_date": pd.Timestamp("2019-01-01") + pd.Timedelta(days=i * 30),
        })
    for i in range(total_per_half):
        winner = "TeamA" if i < bat1_wins_per_half[1] else "TeamB"
        rows.append({
            "match_id": total_per_half + i,
            "winner": winner,
            "team_bat_1": "TeamA",
            "team_bat_2": "TeamB",
            "score_inn1": 250,
            "start_date": mid + pd.Timedelta(days=i * 30),
        })
    return pd.DataFrame(rows)


def test_bias_trend_strengthening():
    df = _make_trend_df((6, 9), 10)
    result = _bias_trend(df, 100)
    assert result["direction"] == "STRENGTHENING"
    assert result["recent_pct"] > result["historical_pct"]


def test_bias_trend_weakening():
    df = _make_trend_df((9, 4), 10)
    result = _bias_trend(df, 100)
    assert result["direction"] == "WEAKENING"


def test_bias_trend_stable():
    df = _make_trend_df((6, 6), 10)
    result = _bias_trend(df, 100)
    assert result["direction"] == "STABLE"


def test_bias_trend_insufficient_data():
    df = _make_trend_df((2, 2), 2)
    result = _bias_trend(df, 100)
    assert result["direction"] == "INSUFFICIENT_DATA"
    assert result["recent_pct"] is None


# -- Toss intelligence -------------------------------------------------------

def test_toss_intelligence_no_columns():
    df = pd.DataFrame([{"match_id": 1, "winner": "A", "team_bat_1": "A", "team_bat_2": "B"}])
    result = _toss_intelligence(df, 100)
    assert result["data_available"] is False
    assert result["chose_bat_win_pct"] is None


def test_toss_intelligence_chose_bat_wins():
    df = pd.DataFrame([
        {
            "match_id": i,
            "winner": "TeamA",
            "team_bat_1": "TeamA",
            "team_bat_2": "TeamB",
            "toss_winner": "TeamA",
            "toss_decision": "bat",
            "start_date": "2023-01-01",
        }
        for i in range(4)
    ] + [
        {
            "match_id": 10 + i,
            "winner": "TeamB",
            "team_bat_1": "TeamA",
            "team_bat_2": "TeamB",
            "toss_winner": "TeamA",
            "toss_decision": "bat",
            "start_date": "2023-01-01",
        }
        for i in range(1)
    ])
    result = _toss_intelligence(df, 100)
    assert result["data_available"] is True
    assert result["chose_bat_win_pct"] == 80


def test_toss_intelligence_mixed_decisions():
    df = pd.DataFrame([
        {
            "match_id": 1,
            "winner": "TeamA",
            "team_bat_1": "TeamA",
            "team_bat_2": "TeamB",
            "toss_winner": "TeamA",
            "toss_decision": "bat",
            "start_date": "2023-01-01",
        },
        {
            "match_id": 2,
            "winner": "TeamA",
            "team_bat_1": "TeamB",
            "team_bat_2": "TeamA",
            "toss_winner": "TeamA",
            "toss_decision": "field",
            "start_date": "2023-01-02",
        },
    ])
    result = _toss_intelligence(df, 100)
    assert result["data_available"] is True
    assert result["chose_bat_win_pct"] == 100
    assert result["chose_bowl_win_pct"] == 100


# -- Full payload integration ------------------------------------------------

def _make_full_df() -> pd.DataFrame:
    """12-match dataset with toss data, scores, and dates spanning 3 years."""
    rows = []
    for i in range(12):
        bat_first_wins = i % 3 != 0  # 8 bat-first wins, 4 chase wins
        rows.append({
            "match_id": i,
            "winner": "TeamA" if bat_first_wins else "TeamB",
            "team_bat_1": "TeamA",
            "team_bat_2": "TeamB",
            "score_inn1": 240 + i * 5,
            "score_inn2": 220 + i * 4,
            "balls_inn1": 300,
            "balls_inn2": 280,
            "toss_winner": "TeamA",
            "toss_decision": "bat" if i % 2 == 0 else "field",
            "start_date": pd.Timestamp("2021-01-01") + pd.Timedelta(days=i * 60),
            "venue": "Test Ground",
            "venue_id": "test_ground",
        })
    return pd.DataFrame(rows)


def test_full_bias_report_has_enriched_fields():
    from core.calculators.team.venue_calculator import calculate_venue_bias_payload

    df = _make_full_df()
    ctx = {
        "stadium_id": "test_ground",
        "years_back": 5,
        "reference_date": pd.Timestamp("2024-01-01"),
        "min_balls_for_completed_innings": 200,
        "percent_scale": 100,
        "bias_win_pct_min": 55,
        "strong_bias_gap_min": 15,
    }
    result = calculate_venue_bias_payload(df, ctx)
    report = result["report"]
    assert report is not None
    assert "confidence_interval" in report
    assert "lower" in report["confidence_interval"]
    assert "upper" in report["confidence_interval"]
    assert "sample_reliability" in report
    assert report["sample_reliability"] == "MODERATE"  # 12 matches
    assert "score_distribution" in report
    assert report["score_distribution"] is not None
    assert "inn1" in report["score_distribution"]
    assert "score_extremes" in report
    assert "lowest_defended" in report["score_extremes"]
    assert "highest_chased" in report["score_extremes"]
    assert "bias_trend" in report
    assert report["bias_trend"]["direction"] in ("STRENGTHENING", "WEAKENING", "STABLE", "INSUFFICIENT_DATA")
    assert "toss_intelligence" in report
    assert report["toss_intelligence"]["data_available"] is True
