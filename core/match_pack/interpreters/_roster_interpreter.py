"""
core/match_pack/interpreters._roster_interpreter -- bowling roster analysis domain.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.match_pack.interpreters._base import InterpreterBase
from core.match_pack.interpreters._condition_interpreter import (
    _classify_experience,
    _strip_style_emojis,
)


def _build_bowling_roster(
    players: List[str],
    bowler_styles: Dict[str, Any],
    player_roles: Dict[str, Any],
    team_stats: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Module-level helper -- builds one team's bowling roster from config dicts."""
    roster = []
    for p in players:
        style = bowler_styles.get(p)
        if style and style != "\U0001F6AB Part-Timer":
            role_raw = player_roles.get(p, "All-Rounder")
            wickets = 0
            if team_stats and p in team_stats:
                stats = team_stats[p]
                wickets = stats.get("career", {}).get("bowling", {}).get("wickets", 0)
            exp_rank = _classify_experience(wickets)
            clean_style = _strip_style_emojis(style)
            roster.append(
                {
                    "bowler": p,
                    "type": clean_style,
                    "role": role_raw,
                    "experience": exp_rank,
                }
            )
    return roster


class RosterInterpreter(InterpreterBase):
    def analyze_bowling_roster(
        self,
        home_xi: List[str],
        away_xi: List[str],
        pitch_conditions: str = "",
        player_stats: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Builds the bowling roster for both teams and determines pitch suitability.
        v3.3: Added awareness of bowler experience and career venue metrics.
        """
        home_stats = player_stats.get("home", {}) if player_stats else {}
        away_stats = player_stats.get("away", {}) if player_stats else {}

        home_roster = _build_bowling_roster(home_xi, self.bowler_styles, self.player_roles, home_stats)
        away_roster = _build_bowling_roster(away_xi, self.bowler_styles, self.player_roles, away_stats)

        home_spin = sum(1 for b in home_roster if "Spin" in b["type"] or "Orth" in b["type"] or "Unorth" in b["type"])
        away_spin = sum(1 for b in away_roster if "Spin" in b["type"] or "Orth" in b["type"] or "Unorth" in b["type"])
        home_pace = sum(1 for b in home_roster if "Fast" in b["type"] or "Med" in b["type"])
        away_pace = sum(1 for b in away_roster if "Fast" in b["type"] or "Med" in b["type"])

        pitch_lower = str(pitch_conditions).lower()
        is_spin_pitch = any(
            kw in pitch_lower for kw in ["dry", "turn", "dust", "spin", "cracks"]
        )
        is_pace_pitch = any(
            kw in pitch_lower for kw in ["green", "seam", "pace", "moisture", "grass"]
        )

        if is_spin_pitch:
            verdict = (
                "HOME_SPIN_ADVANTAGE"
                if home_spin > away_spin
                else ("AWAY_SPIN_ADVANTAGE" if away_spin > home_spin else "EVEN_SPIN")
            )
        elif is_pace_pitch:
            verdict = (
                "HOME_PACE_ADVANTAGE"
                if home_pace > away_pace
                else ("AWAY_PACE_ADVANTAGE" if away_pace > home_pace else "EVEN_PACE")
            )
        else:
            verdict = "BALANCED"

        narrative = ""
        if is_spin_pitch:
            more_spin_team = "Home" if home_spin > away_spin else "Away"
            narrative = (
                f"{more_spin_team} team has {max(home_spin, away_spin)} spinner(s) vs "
                f"{min(home_spin, away_spin)}. On this spin-friendly surface, "
                f"the {'home' if home_spin > away_spin else 'away'} bowling attack is better suited."
            )
        elif is_pace_pitch:
            more_pace_team = "Home" if home_pace > away_pace else "Away"
            narrative = (
                f"{more_pace_team} team has {max(home_pace, away_pace)} pacer(s) vs "
                f"{min(home_pace, away_pace)}. On this seam-friendly surface, "
                f"the {'home' if home_pace > away_pace else 'away'} bowling attack is better suited."
            )
        else:
            narrative = f"Balanced conditions - Home has {home_spin}S/{home_pace}P, Away has {away_spin}S/{away_pace}P."

        return {
            "home": home_roster,
            "away": away_roster,
            "pitch_suitability": {
                "home_spin_bowlers": home_spin,
                "away_spin_bowlers": away_spin,
                "home_pace_bowlers": home_pace,
                "away_pace_bowlers": away_pace,
                "verdict": verdict,
                "narrative": narrative,
            },
        }
