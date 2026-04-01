"""
core/transformer.py
The Data Cleaner — converts raw engine output into clean structured dicts.

Purpose:
    Engine methods return Jupyter-formatted data (list[dict], flat dicts, HTML strings).
    This module strips all display artifacts and restructures into the Match Pack JSON schema.

Rules:
    - ZERO HTML tags in output
    - ZERO emoji decorators in output
    - All numbers are actual numbers (int/float), not strings
    - Every output is a plain dict ready for the Interpreter
    - NO _match_ids in output (internal diagnostic only)
"""
import re
from typing import Any, Dict, List


# =============================================================================
# PRIVATE HELPERS
# =============================================================================

def _parse_avg_string(val: Any) -> Dict[str, int]:
    """
    Parses engine's "230 (15)" format into {avg: 230, count: 15}.
    Also handles plain numbers like 230 or "-".
    """
    if val is None or val == "-" or val == "" or val == 0:
        return {"avg": 0, "count": 0}

    val_str = str(val).strip()

    # Pattern: "230 (15)"
    match = re.match(r'^([\d.]+)\s*\((\d+)\)$', val_str)
    if match:
        return {"avg": round(float(match.group(1))), "count": int(match.group(2))}

    # Pattern: plain number "230" or "230.5"
    try:
        return {"avg": round(float(val_str)), "count": 0}
    except (ValueError, TypeError):
        return {"avg": 0, "count": 0}


def _parse_pct_string(val: Any) -> Dict[str, int]:
    """
    Parses engine's "57% (16)" format into {pct: 57, count: 16}.
    Also handles "57%" or plain "57".
    """
    if val is None or val == "-" or val == "":
        return {"pct": 0, "count": 0}

    val_str = str(val).strip()

    # Pattern: "57% (16)"
    match = re.match(r'^(\d+)%?\s*\((\d+)\)$', val_str)
    if match:
        return {"pct": int(match.group(1)), "count": int(match.group(2))}

    # Pattern: "57%" or plain "57"
    match = re.match(r'^(\d+)%?$', val_str)
    if match:
        return {"pct": int(match.group(1)), "count": 0}

    return {"pct": 0, "count": 0}


def _strip_emojis(text: Any) -> Any:
    """Removes all emoji characters and common decorators from a string."""
    if not isinstance(text, str):
        return text
    # Remove common emoji patterns used in the engine
    cleaned = re.sub(r'[🏏🥎⚖️🦁✈️🪙🌍🏰📉📅🏟️📊🔎❌\U00002705⚠️🚀💾🔧🧠⚙️🔄🚨💡🤝🌧️⚡]', '', text)
    return cleaned.strip()


def _safe_int(val: Any) -> int:
    """Converts a value to int safely, returns 0 for failures."""
    if val is None or val == "-" or val == "":
        return 0
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0


def _safe_float(val: Any, decimals: int = 1) -> float:
    """Converts a value to float safely, returns 0.0 for failures."""
    if val is None or val == "-" or val == "":
        return 0.0
    try:
        return round(float(val), decimals)
    except (ValueError, TypeError):
        return 0.0


def _strip_html(text: Any) -> Any:
    """Removes all HTML tags from a string."""
    if not isinstance(text, str):
        return text
    return re.sub(r'<[^>]+>', '', text).strip()


def _extract_value(data_list: List[Dict[str, Any]], index: int) -> Any:
    """Safely extracts Value from a [{Metric, Value}] list by index."""
    if data_list is None or index >= len(data_list):
        return "-"
    return data_list[index].get("Value", "-")


# =============================================================================
# 1. TRANSFORM H2H REPORT (SLIM — wins/losses only, no averages)
# =============================================================================

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


# =============================================================================
# 2. TRANSFORM H2H REPORT (FULL — with batting averages, for Fortress/Venue)
# =============================================================================

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


# =============================================================================
# 3. TRANSFORM VENUE BIAS
# =============================================================================

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


# =============================================================================
# 4. TRANSFORM TEAM FORM (SLIM — summary only, no match details)
# =============================================================================

def transform_team_form(raw_dict: Dict[str, Any], team_name: str) -> Dict[str, Any]:
    """
    Converts the dict from analyze_team_form into a clean SLIM dict.
    Outputs only summary stats and sequence — no individual match details.

    Args:
        raw_dict: The dict returned by TeamEngine.analyze_team_form.
        team_name: Name of the team for labeling.

    Returns:
        dict: Clean structured summary dict.
    """
    if not raw_dict or not isinstance(raw_dict, dict):
        return {"error": "No data returned from engine"}

    summary_raw = raw_dict.get("summary_code", [])
    summary = []
    
    # Extract just the code (W, L, T, NR) from "W: against India"
    for item in summary_raw:
        if ":" in item:
            summary.append(item.split(":")[0].strip())
        else:
            summary.append(item)

    wins = summary.count("W")
    losses = summary.count("L")
    ties = summary.count("T")
    no_results = summary.count("NR")

    return {
        "team": team_name,
        "sequence": summary,
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "no_results": no_results,
        "total": len(summary),
        "win_pct": round((wins / (len(summary) - no_results - ties)) * 100) if (len(summary) - no_results - ties) > 0 else 0,
    }


# =============================================================================
# 5. TRANSFORM DOMINANCE / AWAY MATRIX
# =============================================================================

def transform_dominance_matrix(raw_list: List[Dict[str, Any]], team_name: str) -> Dict[str, Any]:
    """
    Converts the matrix report from analyze_home_dominance / analyze_away_performance
    into aggregated stats.

    Engine returns keys: 'Opponent', 'Mat', 'Won', 'Lost', 'Tie/NR', 'Win %', 'form_window'

    Args:
        raw_list: The list returned by _generate_matrix_report.
        team_name: Focus team name.

    Returns:
        dict: Aggregated stats from the matrix.
    """
    if not raw_list or not isinstance(raw_list, list):
        return {"error": "No data returned from engine"}

    total_matches = 0
    total_wins = 0
    total_losses = 0
    opponent_records = []

    for row in raw_list:
        if not isinstance(row, dict):
            continue

        opp = row.get("Opponent", "")
        if not opp:
            continue

        opp_clean = _strip_emojis(_strip_html(str(opp))).strip()

        # Skip the OVERALL summary row — we calculate our own totals
        if "OVERALL" in opp_clean.upper():
            continue

        # Engine uses 'Mat', 'Won', 'Lost' as keys
        played = _safe_int(row.get("Mat", row.get("Played", row.get("P", 0))))
        won = _safe_int(row.get("Won", row.get("W", 0)))
        lost = _safe_int(row.get("Lost", row.get("L", 0)))
        form_guide = _strip_emojis(str(row.get("form_guide", "-")))

        # Professional Win %: exclude Ties/NR from denominator
        decisions = played - _safe_int(row.get("Tie/NR", row.get("T", 0)))
        
        total_matches += played
        total_wins += won
        total_losses += lost
        
        if played > 0:
            opponent_records.append({
                "opponent": opp_clean,
                "played": played,
                "won": won,
                "lost": lost,
                "win_pct": round((won / decisions) * 100) if decisions > 0 else 0,
                "form": form_guide,
            })

    # Overall Win %: Exclude NR/Ties from sum total
    total_nr_ties = sum([_safe_int(row.get("Tie/NR", 0)) for row in raw_list if "OVERALL" not in str(row.get("Opponent", "")).upper()])
    total_decisions = total_matches - total_nr_ties
    win_pct = round((total_wins / total_decisions) * 100) if total_decisions > 0 else 0

    return {
        "team": team_name,
        "overall": {
            "matches": total_matches,
            "wins": total_wins,
            "losses": total_losses,
            "win_pct": win_pct,
        },
        "vs_opponents": opponent_records,
    }


# =============================================================================
# 6. TRANSFORM PLAYER DATA
# =============================================================================

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

    result = {
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
