"""
core/match_pack/interpreters.h2h_interpreter — H2H interpretation domain.
"""
from __future__ import annotations

from typing import Any, Dict

from core.match_pack.interpreters._base import InterpreterBase


class H2HInterpreter(InterpreterBase):
    def interpret_h2h(self, data: Dict[str, Any], home_team: str, away_team: str, timeline_label: str) -> Dict[str, Any]:
        """
        Adds dominance tags and narrative to H2H data.

        Interpretation Rules:
            DOMINANT: Win% > 65%
            COMPETITIVE: Win% 45-55%
            ONE_SIDED: Win% gap > 20 points
            EVENLY_MATCHED: Win% == 50%
        """
        if "error" in data:
            return {"data": data, "context": {"status": "NO_DATA"}, "narrative": "Insufficient data for this analysis.", "section_description": "Head-to-head record between the two teams."}

        win_pct = data.get("home_win_pct", 0)
        matches = data.get("matches_played", 0)
        home_wins = data.get("home_wins", 0)
        away_wins = data.get("away_wins", 0)

        # Determine dominance — FIX: handle exactly 50%
        if win_pct > 65:
            dominance = "HOME_DOMINANT"
            dom_reasoning = f"{home_team} win {win_pct}% which exceeds the 65% dominance threshold."
        elif win_pct < 35:
            dominance = "AWAY_DOMINANT"
            dom_reasoning = f"{away_team} win {100 - win_pct}% which exceeds the 65% dominance threshold."
        elif 45 <= win_pct <= 55:
            dominance = "COMPETITIVE"
            dom_reasoning = f"Win rate of {win_pct}% falls within the 45-55% competitive band."
        elif win_pct == 50:
            dominance = "EVENLY_MATCHED"
            dom_reasoning = "Exactly 50-50 — neither team has an edge."
        else:
            dominance = "SLIGHT_EDGE"
            edge_team = home_team if win_pct > 50 else away_team
            dom_reasoning = f"{edge_team} have a slight edge at {max(win_pct, 100 - win_pct)}%, outside the competitive band but below dominance."

        # Determine intensity
        win_gap = abs(win_pct - 50) * 2
        if win_gap > 20:
            intensity = "ONE_SIDED"
            int_reasoning = f"Gap of {round(win_gap)} points from neutral indicates a one-sided record."
        elif win_gap < 10:
            intensity = "TIGHT"
            int_reasoning = f"Gap of {round(win_gap)} points — very tight contest historically."
        else:
            intensity = "MODERATE"
            int_reasoning = f"Gap of {round(win_gap)} points — moderate separation."

        # Build narrative — FIX: handle exactly 50%
        if win_pct == 50:
            narrative = (
                f"This rivalry is evenly split over {timeline_label} — "
                f"both teams have won {home_wins} of {matches} decided matches. "
            )
        elif win_pct > 50:
            narrative = (
                f"{home_team} lead this rivalry with a {win_pct}% win rate "
                f"over {timeline_label} ({home_wins} wins from {matches} matches). "
            )
        else:
            narrative = (
                f"{away_team} lead this rivalry with a {100 - win_pct}% win rate "
                f"over {timeline_label} ({away_wins} wins from {matches} matches). "
            )

        # Add batting first vs chasing split insight
        h_bat1 = data.get("home_won_batting_first", data.get("batting_first", {}).get("home_won_batting_first", 0))
        h_chase = data.get("home_won_chasing", data.get("chasing", {}).get("home_won_chasing", 0))
        a_bat1 = data.get("away_won_batting_first", data.get("batting_first", {}).get("away_won_batting_first", 0))
        a_chase = data.get("away_won_chasing", data.get("chasing", {}).get("away_won_chasing", 0))

        total_bat1_wins = h_bat1 + a_bat1
        total_chase_wins = h_chase + a_chase
        if total_bat1_wins + total_chase_wins > 0:
            if total_bat1_wins > total_chase_wins:
                narrative += f"In this matchup, batting first has produced {total_bat1_wins} wins vs {total_chase_wins} chasing."
            elif total_chase_wins > total_bat1_wins:
                narrative += f"In this matchup, chasing has produced {total_chase_wins} wins vs {total_bat1_wins} batting first."

        context = {
            "timeline": timeline_label,
            "dominance": dominance,
            "dominance_reasoning": dom_reasoning,
            "intensity": intensity,
            "intensity_reasoning": int_reasoning,
        }

        return {
            "section_description": f"Head-to-head record between {home_team} and {away_team} over {timeline_label}. Shows who holds the historical advantage and how matches are typically won.",
            "data": data,
            "context": context,
            "narrative": narrative.strip(),
        }
