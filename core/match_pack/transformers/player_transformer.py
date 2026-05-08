"""Player and squad transform functions."""
from __future__ import annotations

from typing import Any, Dict

from core.match_pack.transformers.string_utils import (
    _safe_float,
    _safe_int,
    _strip_emojis,
    _strip_html,
)


def transform_squad_comparison(comparison_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts the nested dict from _generate_comparison_payload into the
    Chapter 4 schema for the Match Pack.

    Args:
        comparison_payload: The dict returned by PlayerEngine._generate_comparison_payload.

    Returns:
        dict: Clean structured data for squad comparison, tactical matrix, and matchups.
    """
    if not comparison_payload or not isinstance(comparison_payload, dict):
        return {"error": "No data returned from engine"}

    result: dict[str, Any] = {
        "squad_comparison": {},
        "tactical_matrix": {},
        "matchups": {},
    }

    # --- Squad Comparison (clean pass-through, keys are already good) ---
    squad_raw = comparison_payload.get("SquadComparison", {})
    for team_name, metrics in squad_raw.items():
        if isinstance(metrics, dict):
            result["squad_comparison"][team_name] = {
                k: _safe_int(v) for k, v in metrics.items()
            }

    # --- Tactical Matrix (strip HTML from all values) ---
    matrix_raw = comparison_payload.get("TacticalMatrix", {})
    for team_name, matrix_data in matrix_raw.items():
        if isinstance(matrix_data, list):
            clean_rows = []
            for row in matrix_data:
                if isinstance(row, dict):
                    clean_row = {}
                    for k, v in row.items():
                        if isinstance(v, str):
                            # Strip HTML and extract raw values
                            cleaned = _strip_html(v)
                            cleaned = _strip_emojis(cleaned)
                            # Try to extract number if it looks like one
                            if k != "Player":
                                try:
                                    cleaned = round(float(cleaned), 1)
                                except (ValueError, TypeError):
                                    pass
                            clean_row[k] = cleaned
                        else:
                            clean_row[k] = v
                    clean_rows.append(clean_row)
            result["tactical_matrix"][team_name] = clean_rows

    # --- Matchups (clean pass-through, strip HTML) ---
    matchups_raw = comparison_payload.get("Matchups", {})
    for team_name, player_matchups in matchups_raw.items():
        if isinstance(player_matchups, dict):
            clean_player_matchups = {}
            for player, matchup_list in player_matchups.items():
                if isinstance(matchup_list, list):
                    clean_matchups = []
                    for m in matchup_list:
                        if isinstance(m, dict):
                            clean_m = {}
                            for k, v in m.items():
                                if isinstance(v, str):
                                    clean_m[k] = _strip_html(_strip_emojis(v))
                                else:
                                    clean_m[k] = v
                            clean_matchups.append(clean_m)
                    if clean_matchups:
                        clean_player_matchups[player] = clean_matchups
            result["matchups"][team_name] = clean_player_matchups

    return result


def transform_player_stats(stats_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts the flat dict from PlayerEngine._get_stats into structured
    batting_form and bowling_form objects for the per-player schema.

    Args:
        stats_dict: The dict returned by _get_stats for a single player.

    Returns:
        dict: Restructured player data.
    """
    if not stats_dict or not isinstance(stats_dict, dict):
        return {"error": "No data"}

    player = stats_dict.get("Player", "Unknown")

    # Parse batting form string "45, 12*, DNB, 0, 89" into list
    bat_form_raw = stats_dict.get("Bat Form", "-")
    if isinstance(bat_form_raw, str) and bat_form_raw != "-":
        bat_scores = [s.strip() for s in bat_form_raw.split(",")]
    else:
        bat_scores = []

    return {
        "player": player,
        "batting": {
            "innings": _safe_int(stats_dict.get("Inns", 0)),
            "form_scores": bat_scores,
            "average": _safe_float(stats_dict.get("Bat Avg", 0)),
            "vs_opponent_avg": _safe_float(stats_dict.get("vs Opp", 0)) if stats_dict.get("vs Opp") != "-" else None,
            "venue": {
                "innings": _safe_int(stats_dict.get("Ven Inns", 0)),
                "runs": _safe_int(stats_dict.get("Ven Runs", 0)),
                "average": _safe_float(stats_dict.get("Ven Avg", 0)),
                "highest": _safe_int(stats_dict.get("Ven HS", 0)),
            },
        },
        "bowling": {
            "form_display": _strip_html(str(stats_dict.get("Bowl Form", "-"))),
            "economy": _safe_float(stats_dict.get("Bowl Econ", 0)),
            "venue_economy": _safe_float(stats_dict.get("Ven Econ", 0)),
            "venue_wickets": _safe_int(stats_dict.get("Ven Wkts", 0)),
            "venue_matches": _safe_int(stats_dict.get("Ven Matches", 0)),
        },
    }
