"""
core/match_pack/interpreters._condition_interpreter -- pitch/time/toss condition domain.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.match_pack.interpreters._base import InterpreterBase


def _strip_style_emojis(style: str) -> str:
    """Remove display emoji prefixes from a bowling style label."""
    return style.replace("\u26A1 ", "").replace("\U0001F300 ", "")


def _classify_experience(wickets: int) -> str:
    """Classify a bowler's experience tier from career wicket count."""
    if wickets > 100:
        return "VETERAN"
    if wickets < 20:
        return "PROSPECT"
    return "INTERMEDIATE"


def _detect_pitch_conditions(pitch: str) -> List[str]:
    """Return a list of condition tokens for the given pitch description."""
    pitch_lower = str(pitch).lower() if pitch else ""
    tokens: List[str] = []
    if any(kw in pitch_lower for kw in ["dry", "cracks", "turn", "dust", "spin"]):
        tokens.append("SPIN")
    if any(kw in pitch_lower for kw in ["green", "grass", "seam", "moisture", "pace"]):
        tokens.append("SEAM")
    return tokens


def _detect_time_conditions(time: str) -> List[str]:
    """Return a list of condition tokens for the given match start time."""
    time_lower = str(time).lower() if time else ""
    if any(kw in time_lower for kw in ["night", "evening", "sunset", "dew"]):
        return ["DEW"]
    if any(t in time_lower for t in ["14:30", "15:00", "15:30", "16:00", "14:", "15:", "16:"]):
        return ["DEW"]
    return []


class ConditionInterpreter(InterpreterBase):
    def interpret_conditions(
        self,
        pitch: str,
        time: str,
        toss: str,
        bias_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generates condition adjustments from pitch/time/toss context inputs.

        Keywords detected:
            Pitch: dry/cracks/turn/dust -> SPIN_BOOST
            Pitch: green/grass/seam/moisture -> SEAM_BOOST
            Time: night/14:30+/sunset -> DEW_FACTOR
            Toss alignment with venue bias
        """
        adjustments: List[str] = []
        weights: Dict[str, float] = {}

        for pitch_token in _detect_pitch_conditions(pitch):
            if pitch_token == "SPIN":
                adjustments.append("SPIN_BOOST")
                weights["spin_weight"] = 1.2
            elif pitch_token == "SEAM":
                adjustments.append("SEAM_BOOST")
                weights["pace_weight"] = 1.15

        for time_token in _detect_time_conditions(time):
            if time_token == "DEW":
                if "DEW_FACTOR" not in adjustments:
                    adjustments.append("DEW_FACTOR")
                weights["chase_boost"] = 1.1

        toss_lower = str(toss).lower() if toss else ""
        if bias_data and isinstance(bias_data, dict):
            verdict = bias_data.get("verdict", "NEUTRAL").upper()
            is_bat_first_venue = "BAT" in verdict

            if "home" in toss_lower and "batting" in toss_lower and is_bat_first_venue:
                adjustments.append("TOSS_ALIGNED")
            elif "away" in toss_lower and "batting" in toss_lower and is_bat_first_venue:
                adjustments.append("COUNTER_TOSS")
            elif "home" in toss_lower and "bowling" in toss_lower and not is_bat_first_venue:
                adjustments.append("TOSS_ALIGNED")
            elif "away" in toss_lower and "bowling" in toss_lower and not is_bat_first_venue:
                adjustments.append("COUNTER_TOSS")

        return {
            "adjustments": adjustments,
            "weights": weights,
            "pitch_report": str(pitch) if pitch else "",
            "match_time": str(time) if time else "",
            "toss_decision": str(toss) if toss else "",
        }
