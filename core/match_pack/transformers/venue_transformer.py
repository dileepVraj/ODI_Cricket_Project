"""Venue bias transform — converts raw venue engine output to clean dicts."""
from __future__ import annotations

from typing import Any, Dict

from core.match_pack.transformers.string_utils import (
    _parse_avg_string,
    _parse_pct_string,
    _safe_int,
    _strip_emojis,
)


def transform_venue_bias(raw_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts the flat dict from analyze_venue_bias into a clean structured dict.

    Args:
        raw_dict: The dict returned by TeamEngine.analyze_venue_bias.

    Returns:
        dict: Clean structured data dict.
    """
    if not raw_dict or not isinstance(raw_dict, dict):
        return {"error": "No data returned from engine"}

    bat1 = _parse_pct_string(raw_dict.get("Win % Batting First", ""))
    chase = _parse_pct_string(raw_dict.get("Win % Chasing", ""))
    avg_1st = _parse_avg_string(raw_dict.get("Avg 1st innings score", ""))
    avg_2nd = _parse_avg_string(raw_dict.get("Avg 2nd innings score", ""))

    verdict_raw = raw_dict.get("Bias Verdict", "NEUTRAL")
    verdict = _strip_emojis(verdict_raw).strip()

    return {
        "period": raw_dict.get("Period", ""),
        "matches_analyzed": _safe_int(raw_dict.get("Matches analyzed", 0)),
        "bat_first_wins": bat1["count"],
        "bat_first_win_pct": bat1["pct"],
        "chase_wins": chase["count"],
        "chase_win_pct": chase["pct"],
        "avg_1st_innings": avg_1st["avg"],
        "avg_2nd_innings": avg_2nd["avg"],
        "score_drop_2nd_innings": avg_1st["avg"] - avg_2nd["avg"],
        "verdict": verdict,
    }
