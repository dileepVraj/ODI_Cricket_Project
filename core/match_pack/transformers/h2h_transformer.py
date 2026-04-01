"""Head-to-head transform functions — converts raw engine H2H output to clean dicts."""
from __future__ import annotations

from typing import Any, Dict, List

from core.match_pack.transformers.string_utils import (
    _extract_value,
    _parse_avg_string,
    _safe_int,
)


def transform_h2h_slim(raw_list: List[Dict[str, Any]], home_team: str, away_team: str) -> Dict[str, Any]:
    """
    Converts the [{Metric, Value}] list from _build_and_display_report
    into a SLIM dict with only win/loss record and key facts.
    Used for Global H2H and Country H2H (averages are in Fortress/Venue).

    Args:
        raw_list: The list returned by analyze_global_h2h / analyze_home_fortress / etc.
        home_team: Home team name.
        away_team: Away team name.

    Returns:
        dict: Slim structured data dict (no batting averages).
    """
    if not raw_list or not isinstance(raw_list, list):
        return {"error": "No data returned from engine"}

    matches_played = _safe_int(_extract_value(raw_list, 0))
    tie_nr = _safe_int(_extract_value(raw_list, 1))

    # Parse win %: "64%" -> 64
    win_pct_str = str(_extract_value(raw_list, 2)).replace('%', '').strip()
    home_win_pct = _safe_int(win_pct_str)

    home_wins = _safe_int(_extract_value(raw_list, 4))
    home_won_bat1 = _safe_int(_extract_value(raw_list, 5))
    home_won_bat2 = _safe_int(_extract_value(raw_list, 6))

    away_wins = _safe_int(_extract_value(raw_list, 8))
    away_won_bat1 = _safe_int(_extract_value(raw_list, 9))
    away_won_bat2 = _safe_int(_extract_value(raw_list, 10))

    return {
        "matches_played": matches_played,
        "home_wins": home_wins,
        "away_wins": away_wins,
        "no_result": tie_nr,
        "home_win_pct": home_win_pct,
        "home_won_batting_first": home_won_bat1,
        "home_won_chasing": home_won_bat2,
        "away_won_batting_first": away_won_bat1,
        "away_won_chasing": away_won_bat2,
    }


def transform_h2h_report(raw_list: List[Dict[str, Any]], home_team: str, away_team: str) -> Dict[str, Any]:
    """
    Converts the 37-item [{Metric, Value}] list from _build_and_display_report
    into a clean structured dict WITH batting/chasing averages.
    Used for Fortress and Venue-specific H2H only.

    Args:
        raw_list: The list returned by analyze_global_h2h / analyze_home_fortress / etc.
        home_team: Home team name (for labeling).
        away_team: Away team name (for labeling).

    Returns:
        dict: Clean structured data dict with full batting context.
    """
    if not raw_list or not isinstance(raw_list, list):
        return {"error": "No data returned from engine"}

    matches_played = _safe_int(_extract_value(raw_list, 0))
    tie_nr = _safe_int(_extract_value(raw_list, 1))

    # Parse win %: "64%" -> 64
    win_pct_str = str(_extract_value(raw_list, 2)).replace('%', '').strip()
    home_win_pct = _safe_int(win_pct_str)

    home_wins = _safe_int(_extract_value(raw_list, 4))
    home_won_bat1 = _safe_int(_extract_value(raw_list, 5))
    home_won_bat2 = _safe_int(_extract_value(raw_list, 6))

    away_wins = _safe_int(_extract_value(raw_list, 8))
    away_won_bat1 = _safe_int(_extract_value(raw_list, 9))
    away_won_bat2 = _safe_int(_extract_value(raw_list, 10))

    # Venue/Overall averages
    avg_winning_score = _parse_avg_string(_extract_value(raw_list, 14))

    # Home batting 1st stats
    h_avg_1st = _parse_avg_string(_extract_value(raw_list, 16))
    h_avg_win = _parse_avg_string(_extract_value(raw_list, 19))
    h_low_defended = _safe_int(_extract_value(raw_list, 20))

    # Away batting 1st stats
    a_avg_1st = _parse_avg_string(_extract_value(raw_list, 22))
    a_avg_win = _parse_avg_string(_extract_value(raw_list, 25))
    a_low_defended = _safe_int(_extract_value(raw_list, 26))

    # Home chasing stats
    h_high_chased = _safe_int(_extract_value(raw_list, 29))
    h_avg_succ = _parse_avg_string(_extract_value(raw_list, 30))

    # Away chasing stats
    a_high_chased = _safe_int(_extract_value(raw_list, 34))
    a_avg_succ = _parse_avg_string(_extract_value(raw_list, 35))

    return {
        "matches_played": matches_played,
        "home_wins": home_wins,
        "away_wins": away_wins,
        "no_result": tie_nr,
        "home_win_pct": home_win_pct,
        "batting_first": {
            "home_avg_score": h_avg_1st["avg"],
            "home_avg_winning_score": h_avg_win["avg"],
            "home_lowest_defended": h_low_defended,
            "home_won_batting_first": home_won_bat1,
            "away_avg_score": a_avg_1st["avg"],
            "away_avg_winning_score": a_avg_win["avg"],
            "away_lowest_defended": a_low_defended,
            "away_won_batting_first": away_won_bat1,
        },
        "chasing": {
            "home_highest_chase": h_high_chased,
            "home_avg_successful_chase": h_avg_succ["avg"],
            "home_won_chasing": home_won_bat2,
            "away_highest_chase": a_high_chased,
            "away_avg_successful_chase": a_avg_succ["avg"],
            "away_won_chasing": away_won_bat2,
        },
        "avg_winning_score": avg_winning_score["avg"],
    }
