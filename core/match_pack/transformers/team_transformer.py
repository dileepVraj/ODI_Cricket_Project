"""Team form and dominance matrix transforms."""
from __future__ import annotations

from typing import Any, Dict, List

from core.match_pack.transformers.string_utils import (
    _safe_int,
    _strip_emojis,
    _strip_html,
)


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
