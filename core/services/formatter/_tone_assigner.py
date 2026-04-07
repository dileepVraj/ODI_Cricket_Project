from typing import Optional

import re

from core.interfaces.serialization_types import MatchupVisualPayload


class ToneAssigner:
    @staticmethod
    def _extract_sample_size(value: str | int | float | None) -> Optional[int]:
        """Extract sample-size tokens from strings like '278 [7]'."""
        if value is None:
            return None
        match = re.search(r"\[(\d+)\]", str(value))
        if not match:
            return None
        try:
            return int(match.group(1))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _tone_from_win_pct(value: str | int | float | None) -> str:
        """Shared threshold classifier for win-percentage highlights."""
        try:
            text = str(value).replace("%", "").strip()
            pct = float(text)
        except (TypeError, ValueError):
            return "default"

        if pct >= 60:
            return "elite"
        if pct >= 45:
            return "strong"
        if pct >= 30:
            return "caution"
        if pct > 0:
            return "danger"
        return "muted"

    @staticmethod
    def _verdict_tone(verdict: str) -> str:
        verdict_upper = str(verdict).upper()
        if "BAT" in verdict_upper:
            return "primary"
        if "BOWL" in verdict_upper or "CHASE" in verdict_upper:
            return "secondary"
        return "muted"

    @staticmethod
    def _team_tone_from_color(team_color: Optional[str]) -> str:
        """Convert a hex team color into a stable semantic tone token."""
        if not team_color:
            return "slate"

        clean = str(team_color).replace("#", "").strip()
        if not re.fullmatch(r"[0-9a-fA-F]{6}", clean):
            return "slate"

        r = int(clean[0:2], 16) / 255.0
        g = int(clean[2:4], 16) / 255.0
        b = int(clean[4:6], 16) / 255.0

        max_v = max(r, g, b)
        min_v = min(r, g, b)
        delta = max_v - min_v
        hue = 0.0
        if delta != 0:
            if max_v == r:
                hue = ((g - b) / delta) % 6
            elif max_v == g:
                hue = (b - r) / delta + 2
            else:
                hue = (r - g) / delta + 4
        hue_deg = int(round(hue * 60)) % 360

        if 200 <= hue_deg < 255:
            return "blue"
        if 85 <= hue_deg < 160:
            return "emerald"
        if 35 <= hue_deg < 65:
            return "amber"
        if hue_deg >= 330 or hue_deg < 15:
            return "rose"
        if 255 <= hue_deg < 330:
            return "violet"
        return "slate"

    @staticmethod
    def _comparison_section_tone(section_label: str) -> str:
        label = str(section_label).lower()
        if "home" in label or "batting 1st" in label:
            return "primary"
        if "visitor" in label or "chasing" in label:
            return "secondary"
        if "venue" in label or "overall" in label:
            return "tertiary"
        return "muted"

    @staticmethod
    def _tone_from_matchup_outs(outs: str | int | float | None, hard_threshold: int, soft_threshold: int) -> str:
        """Return tone token for batter-vs-bowler dismissal pressure."""
        try:
            dismissals = float(outs if outs is not None else 0)
        except (TypeError, ValueError):
            return "default"

        if dismissals >= float(hard_threshold):
            return "danger"
        if dismissals >= float(soft_threshold):
            return "caution"
        return "default"

    @staticmethod
    def _badges_from_matchup_flags(is_bunny: bool) -> list[str]:
        """Generate human-facing matchup badges from semantic flags."""
        return ["Bunny Alert"] if bool(is_bunny) else []

    @staticmethod
    def _format_matchup_row_visuals(is_bunny: bool, dismissal_tone: str) -> MatchupVisualPayload:
        """Assemble UI-ready visual metadata for matchup rows."""
        tone_token = str(dismissal_tone).strip() if dismissal_tone is not None else "default"
        return {
            "highlight_flags": {"bunny_alert": bool(is_bunny)},
            "cell_tones": {"Outs": tone_token},
            "derived_badges": ToneAssigner._badges_from_matchup_flags(bool(is_bunny)),
        }
