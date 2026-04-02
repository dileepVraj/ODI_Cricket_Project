"""
core/match_pack/interpreters.player_interpreter — player interpretation domain.
"""
from __future__ import annotations

from core.match_pack.interpreters._base import InterpreterBase


class PlayerInterpreter(InterpreterBase):
    def rate_batting_form(self, average: float, innings: int) -> str:
        """
        Applies batting form rating rules from match_pack_plan.md.
        """
        if innings == 0:
            return "DNB"
        if innings < 5:
            return "SMALL_SAMPLE"
        if average > 45:
            return "ELITE_FORM"
        if average >= 30:
            return "IN_FORM"
        if average >= 18:
            return "STEADY"
        return "OUT_OF_FORM"

    def rate_batting_venue(self, average: float, innings: int) -> str:
        """
        Applies batting venue rating rules from match_pack_plan.md.
        """
        if innings == 0:
            return "NO_VENUE_DATA"
        if average > 40 and innings >= 5:
            return "VENUE_SPECIALIST"
        if 25 <= average <= 40:
            return "COMFORTABLE"
        if average < 18 and innings >= 4:
            return "STRUGGLES_HERE"
        return "MODERATE"

    def rate_bowling_form(self, economy: float, wickets_per_match: float, matches: int) -> str:
        """
        Applies bowling form rating rules from match_pack_plan.md.
        """
        if matches == 0:
            return "DNB"
        if matches < 5:
            return "SMALL_SAMPLE"
        if economy > 7.0 or (wickets_per_match == 0 and matches >= 5):
            return "OUT_OF_FORM"
        if economy > 6.5:
            return "EXPENSIVE"
        if economy < 4.5 and wickets_per_match >= 2.0:
            return "ELITE_FORM"
        if economy < 5.5 and wickets_per_match >= 1.5:
            return "IN_FORM"
        return "STEADY"

    def rate_bowling_venue(self, average: float, economy: float, matches: int) -> str:
        """
        Applies bowling venue rating rules from match_pack_plan.md.
        """
        if matches == 0:
            return "NO_VENUE_DATA"
        if average < 25 and economy < 5.0 and matches >= 3:
            return "VENUE_SPECIALIST"
        if 25 <= average <= 35 and economy < 5.5:
            return "EFFECTIVE"
        if (average > 45 or economy > 6.5) and matches >= 3:
            return "STRUGGLES_HERE"
        return "MODERATE"

    def rate_matchup(self, average: float, strike_rate: float, dismissals: int, balls: int) -> str:
        """
        Applies H2H matchup rating rules from match_pack_plan.md.
        """
        if balls < 12:
            return "SMALL_SAMPLE"
        if dismissals >= 3 and average < 20:
            return "BUNNY_ALERT"
        if dismissals >= 2 and average < 25:
            return "HIGH_RISK"
        if average > 50 and strike_rate > 100:
            return "PLAYER_DOMINANCE"
        if dismissals == 0 and balls > 12:
            return "SAFE_MATCHUP"
        return "NEUTRAL"
