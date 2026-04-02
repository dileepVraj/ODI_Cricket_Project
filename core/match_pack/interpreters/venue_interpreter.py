"""
core/match_pack/interpreters.venue_interpreter — venue interpretation domain.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from core.match_pack.interpreters._base import InterpreterBase


class VenueInterpreter(InterpreterBase):
    def interpret_fortress(self, data: Dict[str, Any], home_team: str) -> Dict[str, Any]:
        """
        Adds fortress status tags and narrative.

        Interpretation Rules:
            FORTRESS_CONFIRMED: Home win% > 60%
            NEUTRAL_GROUND: Home win% 45-55%
            VISITOR_FRIENDLY: Home win% < 45%
        """
        if "error" in data:
            return {"data": data, "context": {"status": "NO_DATA"}, "narrative": "Insufficient data for this analysis.", "section_description": "Home team's record at this specific venue."}

        win_pct = data.get("home_win_pct", 0)
        matches = data.get("matches_played", 0)
        home_wins = data.get("home_wins", 0)

        if win_pct > 60:
            fortress_status = "FORTRESS_CONFIRMED"
            fort_reasoning = f"{home_team} win {win_pct}% here ({home_wins}/{matches}) — exceeds 60% fortress threshold."
        elif 45 <= win_pct <= 55:
            fortress_status = "NEUTRAL_GROUND"
            fort_reasoning = f"{win_pct}% home win rate ({home_wins}/{matches}) — within the 45-55% neutral band."
        elif win_pct < 45:
            fortress_status = "VISITOR_FRIENDLY"
            fort_reasoning = f"Only {win_pct}% home win rate ({home_wins}/{matches}) — below 45%, visitors have historically done well."
        else:
            fortress_status = "SLIGHT_HOME_EDGE"
            fort_reasoning = f"{win_pct}% home win rate ({home_wins}/{matches}) — slight home advantage but not a fortress."

        # Extract defend/chase thresholds
        low_defended = data.get("batting_first", {}).get("home_lowest_defended", 0)
        highest_chase = data.get("chasing", {}).get("away_highest_chase", 0)
        avg_winning = data.get("batting_first", {}).get("home_avg_winning_score", data.get("avg_winning_score", 0))

        bat_first_bias = "STRONG" if data.get("batting_first", {}).get("home_won_batting_first", 0) > data.get("chasing", {}).get("home_won_chasing", 0) else "WEAK"

        narrative = (
            f"This venue is {'a confirmed fortress' if fortress_status == 'FORTRESS_CONFIRMED' else 'neutral ground' if fortress_status == 'NEUTRAL_GROUND' else 'visitor-friendly'} "
            f"for {home_team} ({win_pct}% win rate, {home_wins}/{matches} matches). "
        )

        if avg_winning > 0:
            narrative += f"Average winning score here is {avg_winning}. "
        if low_defended > 0:
            narrative += f"Lowest successfully defended score is {low_defended}. "
        if highest_chase > 0:
            narrative += f"Visitors have never chased above {highest_chase} here."

        context = {
            "fortress_status": fortress_status,
            "fortress_reasoning": fort_reasoning,
            "batting_first_bias": bat_first_bias,
            "defend_threshold": low_defended,
            "chase_ceiling": highest_chase,
        }

        return {
            "section_description": f"Evaluates whether this venue is a 'fortress' for {home_team} based on their historical win rate here. Includes key score thresholds (lowest defended, highest chased).",
            "data": data,
            "context": context,
            "narrative": narrative.strip(),
        }

    def interpret_toss_bias(self, data: Dict[str, Any], match_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Adds toss verdict and alignment tags.

        Combined with Match Context:
            TOSS_ALIGNED: Toss winner chose the side that matches venue bias.
            TOSS_MISALIGNED: Toss winner chose against venue bias.
            COUNTER_TOSS: Away team seized the toss advantage.
        """
        if "error" in data:
            return {"data": data, "context": {"status": "NO_DATA"}, "narrative": "Insufficient data for this analysis.", "section_description": "Historical toss impact at this venue."}

        verdict = data.get("verdict", "NEUTRAL")
        bat1_pct = data.get("bat_first_win_pct", 0)
        chase_pct = data.get("chase_win_pct", 0)
        avg_1st = data.get("avg_1st_innings", 0)
        avg_2nd = data.get("avg_2nd_innings", 0)
        score_drop = data.get("score_drop_2nd_innings", 0)
        matches = data.get("matches_analyzed", 0)
        period = data.get("period", "")

        # Determine strength
        pct_gap = abs(bat1_pct - chase_pct)
        if pct_gap > 20:
            strength = "STRONG"
            str_reasoning = f"{pct_gap}pp gap between bat-first ({bat1_pct}%) and chase ({chase_pct}%) win rates — strong bias."
        elif pct_gap > 10:
            strength = "MODERATE"
            str_reasoning = f"{pct_gap}pp gap — moderate toss impact."
        else:
            strength = "SLIGHT"
            str_reasoning = f"Only {pct_gap}pp gap — toss has minimal historical impact."

        # Toss alignment with match context
        toss_alignment = "UNKNOWN"
        toss_advantage = False
        toss_reasoning = "No toss information provided."
        if match_context:
            toss_str = str(match_context.get("toss", "")).lower()
            is_bat_first_venue = "BAT FIRST" in verdict.upper()

            if "batting" in toss_str and is_bat_first_venue:
                toss_alignment = "TOSS_ALIGNED"
                toss_advantage = True
                toss_reasoning = f"Toss winner chose to bat, which aligns with venue bias ({verdict})."
            elif "bowling" in toss_str and not is_bat_first_venue:
                toss_alignment = "TOSS_ALIGNED"
                toss_advantage = True
                toss_reasoning = f"Toss winner chose to bowl, which aligns with venue bias ({verdict})."
            elif "batting" in toss_str and not is_bat_first_venue:
                toss_alignment = "TOSS_MISALIGNED"
                toss_reasoning = f"Toss winner chose to bat but venue historically favours chasing ({verdict})."
            elif "bowling" in toss_str and is_bat_first_venue:
                toss_alignment = "TOSS_MISALIGNED"
                toss_reasoning = f"Toss winner chose to bowl but venue historically favours batting first ({verdict})."

            if "away" in toss_str and toss_advantage:
                toss_alignment = "COUNTER_TOSS"
                toss_reasoning = "Away team won toss and made the statistically optimal choice — counter-toss scenario."

        # Narrative
        bias_text = "batting first" if "BAT" in verdict.upper() else ("chasing" if "BOWL" in verdict.upper() else "neither side")
        narrative = (
            f"This venue favours {bias_text} ({bat1_pct}% bat-first win rate vs {chase_pct}% chasing, {matches} matches over {period}). "
        )
        if score_drop > 0:
            narrative += (
                f"Average 1st innings score is {avg_1st}, dropping to {avg_2nd} in the 2nd — "
                f"a {score_drop}-run depression suggesting the pitch deteriorates. "
            )
        if toss_alignment not in ("UNKNOWN", ""):
            narrative += f"Toss decision is {toss_alignment.replace('_', ' ').lower()}."

        context = {
            "verdict": verdict,
            "strength": strength,
            "strength_reasoning": str_reasoning,
            "toss_alignment": toss_alignment,
            "toss_reasoning": toss_reasoning,
            "toss_winner_advantage": toss_advantage,
        }

        return {
            "section_description": f"Analyses whether batting first or chasing has historically won more at this venue ({period}). Combined with live toss information to assess alignment.",
            "data": data,
            "context": context,
            "narrative": narrative.strip(),
        }
