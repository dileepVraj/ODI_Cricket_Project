"""
core/match_pack/interpreters.team_interpreter - team interpretation domain.
"""
from __future__ import annotations

from typing import Any, Dict

from core.match_pack.interpreters._base import InterpreterBase


def _calculate_momentum(
    seq: list[str],
    rankings: dict[str, int],
) -> tuple[float, int]:
    """Compute the quality-weighted momentum score for the last 5 matches."""
    momentum_points: float = 0.0
    w5 = 0

    for item in seq[:5]:
        code = item.split(":")[0].strip() if ":" in item else item
        opp = item.split(":")[1].strip() if ":" in item else ""
        rank = rankings.get(opp, 15)

        if code == "W":
            w5 += 1
            if rank <= 3:
                weight = 2.5
            elif rank <= 7:
                weight = 1.5
            elif rank <= 10:
                weight = 1.0
            else:
                weight = 0.5
            momentum_points += weight
        elif code == "L":
            if rank <= 3:
                weight = -0.2
            elif rank <= 7:
                weight = -0.8
            elif rank <= 10:
                weight = -1.5
            else:
                weight = -2.5
            momentum_points += weight

    return momentum_points, w5


def _classify_momentum(momentum_points: float, w5: int) -> tuple[str, str]:
    """Map a momentum score to a tag and one-line reasoning string."""
    if momentum_points >= 6.0:
        tag = "HOT"
        reasoning = (
            f"Momentum score: {momentum_points:.1f} (Won {w5} of 5). "
            "Excellent rhythm with quality wins against top-tier opposition."
        )
    elif momentum_points >= 2.0:
        tag = "STABLE"
        reasoning = (
            f"Momentum score: {momentum_points:.1f}. "
            "Form is steady; competitive against the current strength of schedule."
        )
    else:
        tag = "COLD"
        reasoning = (
            f"Momentum score: {momentum_points:.1f}. "
            "Significant momentum loss - struggling to defend rankings or secure quality wins."
        )
    return tag, reasoning


def _calculate_trend(seq: list[str], total: int) -> tuple[str, str]:
    """Detect whether recent form is improving or declining vs the earlier window."""
    if total < 6:
        return "FLAT", "Not enough data to determine trend."

    mid = total // 2
    first_half = seq[mid:]
    second_half = seq[:mid]

    first_half_wr = (
        first_half.count("W") / len(first_half) * 100 if len(first_half) > 0 else 0
    )
    second_half_wr = (
        second_half.count("W") / len(second_half) * 100 if len(second_half) > 0 else 0
    )
    wr_diff = second_half_wr - first_half_wr

    if wr_diff >= 25:
        tag = "TRENDING_UP"
        reasoning = (
            f"Recent {len(second_half)} matches: "
            f"{second_half.count('W')}W/{second_half.count('L')}L "
            f"({second_half_wr:.0f}% WR) vs "
            f"earlier {len(first_half)} matches: "
            f"{first_half.count('W')}W/{first_half.count('L')}L "
            f"({first_half_wr:.0f}% WR). "
            f"Improvement of {wr_diff:.0f} percentage points."
        )
    elif wr_diff <= -25:
        tag = "TRENDING_DOWN"
        reasoning = (
            f"Recent {len(second_half)} matches: "
            f"{second_half.count('W')}W/{second_half.count('L')}L "
            f"({second_half_wr:.0f}% WR) vs "
            f"earlier {len(first_half)} matches: "
            f"{first_half.count('W')}W/{first_half.count('L')}L "
            f"({first_half_wr:.0f}% WR). "
            f"Decline of {abs(wr_diff):.0f} percentage points."
        )
    else:
        tag = "FLAT"
        reasoning = (
            f"Recent {len(second_half)} matches: {second_half_wr:.0f}% WR vs "
            f"earlier {len(first_half)}: {first_half_wr:.0f}% WR. "
            f"Difference of {abs(wr_diff):.0f}pp - no significant trend."
        )

    return tag, reasoning


def _detect_streak(seq: list[str]) -> tuple[str, str]:
    """Scan the result sequence for a current consecutive streak."""
    if len(seq) < 2:
        return "", ""

    streak_type = seq[0]
    streak_count = 0
    for r in seq:
        if r == streak_type:
            streak_count += 1
        else:
            break

    if streak_count < 2:
        return "", ""

    label = {"W": "wins", "L": "losses", "T": "ties", "NR": "no results"}.get(
        streak_type, streak_type
    )
    streak_label = f"{streak_count} consecutive {label}"
    streak_reasoning = f"The last {streak_count} results are all '{streak_type}'."
    return streak_label, streak_reasoning


class TeamInterpreter(InterpreterBase):
    def interpret_form(self, data: Dict[str, Any], filter_label: str = "Global") -> Dict[str, Any]:
        """
        Adds momentum tags and narrative to form data.

        Interpretation Rules:
            HOT: 4+ wins out of 5
            STABLE: 2-3 wins out of 5
            COLD: 0-1 wins out of 5
            TRENDING_UP: 2nd half win rate > 1st half win rate by 25%+
            TRENDING_DOWN: 2nd half win rate < 1st half win rate by 25%+
        """
        if "error" in data:
            return {
                "data": data,
                "context": {"status": "NO_DATA"},
                "narrative": "Insufficient data for this analysis.",
                "section_description": "Recent match results and form.",
            }

        team = data.get("team", "Unknown")
        seq = data.get("sequence", [])
        wins = data.get("wins", 0)
        losses = data.get("losses", 0)
        total = data.get("total", 0)

        momentum_points, w5 = _calculate_momentum(seq, self.rankings)
        momentum, mom_reasoning = _classify_momentum(momentum_points, w5)
        trend, trend_reasoning = _calculate_trend(seq, total)
        streak, streak_reasoning = _detect_streak(seq)

        win_pct = data.get("win_pct", round((wins / total) * 100) if total > 0 else 0)
        narrative = (
            f"{team} have won {wins} and lost {losses} of their last {total} matches ({filter_label}), "
            f"a {win_pct}% win rate. "
        )
        if momentum == "HOT":
            narrative += f"They are in excellent form with {w5} wins from their recent matches."
        elif momentum == "COLD":
            narrative += f"They are struggling with only {w5} win(s) from their recent matches."
        else:
            narrative += f"Form is steady with {w5} wins from their recent matches."

        if streak:
            narrative += f" Currently on a streak of {streak}."

        context = {
            "filter": filter_label,
            "momentum": momentum,
            "momentum_reasoning": mom_reasoning,
            "trend": trend,
            "trend_reasoning": trend_reasoning,
            "streak": streak,
            "streak_reasoning": streak_reasoning,
        }

        return {
            "section_description": (
                f"Recent form analysis for {team} ({filter_label}). Shows momentum direction, "
                "current streaks, and whether form is improving or declining."
            ),
            "data": data,
            "context": context,
            "narrative": narrative.strip(),
        }

    def interpret_dominance(self, data: Dict[str, Any], team_name: str, mode: str = "HOME") -> Dict[str, Any]:
        """
        Adds strength tags to home dominance or away performance data.
        """
        if "error" in data:
            return {
                "data": data,
                "context": {"status": "NO_DATA"},
                "narrative": "Insufficient data for this analysis.",
                "section_description": f"{team_name}'s {mode.lower()} performance matrix.",
            }

        overall = data.get("overall", {})
        win_pct = overall.get("win_pct", 0)
        matches = overall.get("matches", 0)
        wins = overall.get("wins", 0)

        if mode == "HOME":
            if win_pct > 65:
                strength = "STRONG"
                str_reasoning = f"{win_pct}% win rate at home ({wins}/{matches}) - above 65% threshold."
            elif win_pct >= 50:
                strength = "MODERATE"
                str_reasoning = f"{win_pct}% win rate at home ({wins}/{matches}) - positive but not dominant."
            else:
                strength = "WEAK"
                str_reasoning = f"Only {win_pct}% win rate at home ({wins}/{matches}) - below 50%."
            label = "home"
        else:
            if win_pct > 50:
                strength = "STRONG_TRAVELLER"
                str_reasoning = f"{win_pct}% win rate away ({wins}/{matches}) - winning more than losing on the road."
            elif win_pct >= 35:
                strength = "COMPETITIVE_AWAY"
                str_reasoning = f"{win_pct}% win rate away ({wins}/{matches}) - competitive but below par."
            else:
                strength = "STRUGGLES_AWAY"
                str_reasoning = f"Only {win_pct}% win rate away ({wins}/{matches}) - significantly below par."
            label = "away"

        narrative = f"{team_name} win {win_pct}% of {label} matches ({wins}/{matches}). "

        opponents = data.get("vs_opponents", [])
        if opponents:
            meaningful = [o for o in opponents if o.get("played", 0) >= 3]
            if meaningful:
                best = max(meaningful, key=lambda x: x.get("win_pct", 0))
                worst = min(meaningful, key=lambda x: x.get("win_pct", 0))
                narrative += f"Best record vs {best['opponent']} ({best['win_pct']}%, {best['won']}/{best['played']}). "
                if worst["opponent"] != best["opponent"]:
                    narrative += (
                        f"Worst record vs {worst['opponent']} "
                        f"({worst['win_pct']}%, {worst['won']}/{worst['played']})."
                    )

        context = {
            "strength": strength,
            "strength_reasoning": str_reasoning,
            "mode": mode,
        }

        return {
            "section_description": (
                f"Overall {label} performance matrix for {team_name} against all major opponents. "
                f"Identifies which teams they dominate and struggle against {label}."
            ),
            "data": data,
            "context": context,
            "narrative": narrative.strip(),
        }
