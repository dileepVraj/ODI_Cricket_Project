from typing import List, Optional, Union

import numpy as np
import pandas as pd
import re

from core.services.match_filter_service import MatchStatus
from core.interfaces.team_types import (
    DisplayRecord, 
    MatchupVisualPayload, 
    FormSequencePayload, 
    FormGuidePayload
)
from core.interfaces.team_types import (
    ScenarioDiff,
    ScenarioDiffRows,
    ScenarioRow,
    ScenarioRows,
)


class ReportFormatter:
    """Pure stateless formatter for UI metadata and visual tokens."""

    LOW_SAMPLE_LABELS = (
        "Batting 1st Avg",
        "Avg Winning Score",
        "Chasing Avg",
    )

    MATCH_STATUS_LABELS = {
        int(MatchStatus.STATUS_OK): "Included",
        int(MatchStatus.STATUS_NR_DROP): "Excluded (No Result)",
        int(MatchStatus.STATUS_SHORT_FIRST_DROP): "Excluded (Short 1st)",
        int(MatchStatus.STATUS_SHORT_SECOND_DROP): "Excluded (Short 2nd)",
        int(MatchStatus.STATUS_DROP): "Excluded",
    }

    MATCH_STATUS_ICONS = {
        int(MatchStatus.STATUS_OK): "✅",
        int(MatchStatus.STATUS_NR_DROP): "☔",
        int(MatchStatus.STATUS_SHORT_FIRST_DROP): "☔",
        int(MatchStatus.STATUS_SHORT_SECOND_DROP): "☔",
        int(MatchStatus.STATUS_DROP): "☔",
    }

    MATCH_STATUS_TONES = {
        int(MatchStatus.STATUS_OK): "elite",
        int(MatchStatus.STATUS_NR_DROP): "caution",
        int(MatchStatus.STATUS_SHORT_FIRST_DROP): "caution",
        int(MatchStatus.STATUS_SHORT_SECOND_DROP): "caution",
        int(MatchStatus.STATUS_DROP): "caution",
    }

    @staticmethod
    def normalize_match_status_code(value: int | float | str | None) -> int:
        if value is None:
            return int(MatchStatus.STATUS_OK)
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return int(MatchStatus.STATUS_OK)

    @staticmethod
    def format_match_status(status_code: int | float | str | None) -> str:
        code = ReportFormatter.normalize_match_status_code(status_code)
        label = ReportFormatter.MATCH_STATUS_LABELS.get(code, ReportFormatter.MATCH_STATUS_LABELS[int(MatchStatus.STATUS_OK)])
        icon = ReportFormatter.MATCH_STATUS_ICONS.get(code, ReportFormatter.MATCH_STATUS_ICONS[int(MatchStatus.STATUS_OK)])
        return f"{icon} {label}"

    @staticmethod
    def match_status_tone(status_code: int | float | str | None) -> str:
        code = ReportFormatter.normalize_match_status_code(status_code)
        return ReportFormatter.MATCH_STATUS_TONES.get(code, "muted")

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
    def _none_if_placeholder(value: str | int | float | None) -> str | int | float | None:
        if value is None:
            return None
        return None if str(value).strip() == "-" else value

    @staticmethod
    def _format_low_sample_warnings(team_name: str, sample_sizes: list[Optional[int]], min_matches: int) -> list[str]:
        warnings: list[str] = []
        for label, sample_size in zip(ReportFormatter.LOW_SAMPLE_LABELS, sample_sizes):
            if sample_size is not None and sample_size < min_matches:
                warnings.append(f"{team_name} {label} (n={sample_size})")
        return warnings

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
            "derived_badges": ReportFormatter._badges_from_matchup_flags(bool(is_bunny)),
        }

    @staticmethod
    def _value_or_placeholder(value: str | int | float | None, placeholder: str = "-") -> str | int | float:
        if value is None:
            return placeholder
        try:
            if pd.isna(value):  # type: ignore
                return placeholder
        except (TypeError, ValueError):
            pass
        return value

    @staticmethod
    def _format_form_sequence(payload: FormSequencePayload) -> str:
        raw_entries = payload["results"]
        missing_token = payload["missing_token"]
        if not raw_entries:
            return "-"
        normalized = [missing_token if entry in (None, "") else str(entry) for entry in raw_entries]
        if all(token == missing_token for token in normalized):
            return "-"
        return ", ".join(normalized)

    @staticmethod
    def format_form_guide(payload: FormGuidePayload) -> str:
        """
        Translates semantic form data into UI visuals (emoji sequence).
        """
        if not payload.get("raw_results"):
            return "-"
        
        mapping = {
            "W": "✅",
            "L": "❌",
            "T": "🤝",
            "NR": "🌧️",
        }
        return " ".join(mapping.get(res, "❓") for res in payload["raw_results"])

    @staticmethod
    def format_squad_player_stats(records: list[DisplayRecord]) -> list[DisplayRecord]:
        """Convert semantic squad-service payload into UI table labels/placeholders."""
        formatted: list[DisplayRecord] = []
        for record in records:
            player_name = str(record.get("player_name") or "")
            player_role = str(record.get("player_role") or "All-Rounder")
            innings = int(record.get("innings") or 0)

            bat_form_payload: FormSequencePayload = {
                "results": record.get("batting_form") or [], # type: ignore
                "missing_token": "DNB"
            }
            bat_form = ReportFormatter._format_form_sequence(bat_form_payload)

            bowl_form_payload: FormSequencePayload = {
                "results": record.get("bowling_form") or [], # type: ignore
                "missing_token": "-"
            }
            bowl_form = ReportFormatter._format_form_sequence(bowl_form_payload)

            bat_avg_raw = record.get("batting_average")
            bat_avg = bat_avg_raw if innings > 0 and bat_avg_raw is not None else "-"

            venue_runs_raw = record.get("venue_runs")
            venue_activity = bool(record.get("venue_batting_activity"))
            if venue_runs_raw is None and venue_activity:
                venue_runs: str | int | float = "DNB"
            else:
                venue_runs = ReportFormatter._value_or_placeholder(venue_runs_raw, "-")

            formatted.append(
                {
                    "Player": player_name,
                    "Role": player_role,
                    "Inns": innings,
                    "Bat Form": bat_form,
                    "Bat Avg": bat_avg if bat_avg is not None else "-",
                    "vs Opp": ReportFormatter._value_or_placeholder(record.get("vs_opposition_average"), "-"),
                    "Ven Inns": ReportFormatter._value_or_placeholder(record.get("venue_innings"), "-"),
                    "Ven Runs": venue_runs,
                    "Ven Avg": ReportFormatter._value_or_placeholder(record.get("venue_average"), "-"),
                    "Ven HS": ReportFormatter._value_or_placeholder(record.get("venue_high_score"), "-"),
                    "Bowl Form": bowl_form,
                    "Bowl Econ": ReportFormatter._value_or_placeholder(record.get("bowling_economy"), "-"),
                    "Ven Econ": ReportFormatter._value_or_placeholder(record.get("venue_economy"), "-"),
                    "Ven Wkts": ReportFormatter._value_or_placeholder(record.get("venue_wickets"), "-"),
                    "Ven Matches": ReportFormatter._value_or_placeholder(record.get("venue_matches"), "-"),
                }
            )
        return formatted

    @staticmethod
    def format_tactical_matrix(records: list[DisplayRecord]) -> list[DisplayRecord]:
        """Convert semantic matchup-engine payload into UI matrix shape."""
        formatted: list[DisplayRecord] = []
        for record in records:
            row: DisplayRecord = {
                "Player": str(record.get("player_name") or ""),
                "Role": str(record.get("player_role") or "All-Rounder"),
            }
            style_metrics = record.get("style_metrics", {})
            if not isinstance(style_metrics, dict):
                formatted.append(row)
                continue

            for style_key, metric in style_metrics.items():
                style_name = str(style_key)
                metric_dict = metric if isinstance(metric, dict) else {}
                avg_raw = metric_dict.get("average_raw", metric_dict.get("average"))
                sr_raw = metric_dict.get("strike_rate")

                if avg_raw is None:
                    row[style_name] = "-"
                    continue

                if isinstance(avg_raw, (int, np.integer)) and not isinstance(avg_raw, bool):
                    display_avg: int | float = int(avg_raw)
                else:
                    try:
                        avg_value = float(avg_raw)
                    except (TypeError, ValueError):
                        row[style_name] = "-"
                        continue
                    display_avg = round(avg_value, 1)

                sr_value = 0
                if sr_raw is not None:
                    try:
                        sr_value = int(float(sr_raw))
                    except (TypeError, ValueError):
                        sr_value = 0

                row[style_name] = [display_avg, sr_value]
                if not (style_name == "Unmapped" and avg_value in (0.0,)):
                    row[f"{style_name}_raw"] = display_avg

            formatted.append(row)
        return formatted

    @staticmethod
    def format_scenario_rows(
        diff_rows: ScenarioDiffRows,
    ) -> ScenarioRows:
        """Convert raw ScenarioDiff rows into display-ready ScenarioRow structures.

        Applies tone ("success", "danger", "muted")
        and direction text ("UP x.x", "DOWN x.x")
        from raw numeric diff and advantage fields.
        This is the only place in the codebase
        permitted to produce these presentation tokens.
        """

        def _format_one(row: ScenarioDiff) -> ScenarioRow:
            diff = row["diff"]
            advantage = row["advantage"]

            if advantage == "neutral" and diff == 0.0:
                diff_text = "-" if (
                    row["home_value"] is None
                    or row["away_value"] is None
                ) else "0.0"
                return {
                    "label": row["label"],
                    "home_value": row["home_value"],
                    "away_value": row["away_value"],
                    "higher_better": row["higher_better"],
                    "diff_text": diff_text,
                    "diff_tone": "muted",
                }

            sign = "UP" if advantage == "home" else "DOWN"
            tone = "success" if advantage == "home" else "danger"
            return {
                "label": row["label"],
                "home_value": row["home_value"],
                "away_value": row["away_value"],
                "higher_better": row["higher_better"],
                "diff_text": f"{sign} {diff:.1f}",
                "diff_tone": tone,
            }

        return {
            "bat_first": [
                _format_one(r)
                for r in diff_rows["bat_first"]
            ],
            "chasing": [
                _format_one(r)
                for r in diff_rows["chasing"]
            ],
        }
