from typing import cast

import numpy as np
import pandas as pd

from core.interfaces.serialization_types import DisplayRecord
from core.interfaces.team_types import FormGuidePayload, FormSequencePayload
from core.interfaces.venue_types import ScenarioDiff, ScenarioDiffRows, ScenarioRow, ScenarioRows
from core.services.report_formatter import ReportFormatter


class DisplayFormatter:
    LOW_SAMPLE_LABELS = (
        "Batting 1st Avg",
        "Avg Winning Score",
        "Chasing Avg",
    )

    @staticmethod
    def _none_if_placeholder(value: str | int | float | None) -> str | int | float | None:
        if value is None:
            return None
        return None if str(value).strip() == "-" else value

    @staticmethod
    def _format_low_sample_warnings(team_name: str, sample_sizes: list[int | None], min_matches: int) -> list[str]:
        warnings: list[str] = []
        for label, sample_size in zip(DisplayFormatter.LOW_SAMPLE_LABELS, sample_sizes):
            if sample_size is not None and sample_size < min_matches:
                warnings.append(f"{team_name} {label} (n={sample_size})")
        return warnings

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
            "W": "\u2705",
            "L": "\u274C",
            "T": "\U0001F91D",
            "NR": "\U0001F327\ufe0f",
        }
        return " ".join(mapping.get(res, "\u2753") for res in payload["raw_results"])

    @staticmethod
    def format_squad_player_stats(records: list[DisplayRecord]) -> list[DisplayRecord]:
        """Convert semantic squad-service payload into UI table labels/placeholders."""
        formatted: list[DisplayRecord] = []
        for record in records:
            player_name = str(record.get("player_name") or "")
            player_role = str(record.get("player_role") or "All-Rounder")
            innings_raw = cast(str | int | float | None, record.get("innings"))
            innings = int(innings_raw or 0)

            bat_form_payload: FormSequencePayload = {
                "results": record.get("batting_form") or [],  # type: ignore
                "missing_token": "DNB",
            }
            bat_form = ReportFormatter._format_form_sequence(bat_form_payload)

            bowl_form_payload: FormSequencePayload = {
                "results": record.get("bowling_form") or [],  # type: ignore
                "missing_token": "-",
            }
            bowl_form = ReportFormatter._format_form_sequence(bowl_form_payload)

            bat_avg_raw = cast(str | int | float | None, record.get("batting_average"))
            bat_avg = bat_avg_raw if innings > 0 and bat_avg_raw is not None else "-"

            venue_runs_raw = cast(str | int | float | None, record.get("venue_runs"))
            venue_activity = bool(record.get("venue_batting_activity"))
            if venue_runs_raw is None and venue_activity:
                venue_runs: str | int | float = "DNB"
            else:
                venue_runs = ReportFormatter._value_or_placeholder(venue_runs_raw, "-")

            vs_opp_average = cast(str | int | float | None, record.get("vs_opposition_average"))
            venue_innings = cast(str | int | float | None, record.get("venue_innings"))
            venue_average = cast(str | int | float | None, record.get("venue_average"))
            venue_high_score = cast(str | int | float | None, record.get("venue_high_score"))
            bowling_economy = cast(str | int | float | None, record.get("bowling_economy"))
            venue_economy = cast(str | int | float | None, record.get("venue_economy"))
            venue_wickets = cast(str | int | float | None, record.get("venue_wickets"))
            venue_matches = cast(str | int | float | None, record.get("venue_matches"))

            formatted.append(
                {
                    "Player": player_name,
                    "Role": player_role,
                    "Inns": innings,
                    "Bat Form": bat_form,
                    "Bat Avg": bat_avg if bat_avg is not None else "-",
                    "vs Opp": ReportFormatter._value_or_placeholder(vs_opp_average, "-"),
                    "Ven Inns": ReportFormatter._value_or_placeholder(venue_innings, "-"),
                    "Ven Runs": venue_runs,
                    "Ven Avg": ReportFormatter._value_or_placeholder(venue_average, "-"),
                    "Ven HS": ReportFormatter._value_or_placeholder(venue_high_score, "-"),
                    "Bowl Form": bowl_form,
                    "Bowl Econ": ReportFormatter._value_or_placeholder(bowling_economy, "-"),
                    "Ven Econ": ReportFormatter._value_or_placeholder(venue_economy, "-"),
                    "Ven Wkts": ReportFormatter._value_or_placeholder(venue_wickets, "-"),
                    "Ven Matches": ReportFormatter._value_or_placeholder(venue_matches, "-"),
                }
            )
        return formatted

    @staticmethod
    def format_tactical_matrix(records: list[DisplayRecord]) -> list[DisplayRecord]:
        """Convert semantic matchup-engine payload into UI matrix shape."""
        formatted: list[DisplayRecord] = []
        for record in records:
            row: dict[str, object] = {
                "Player": str(record.get("player_name") or ""),
                "Role": str(record.get("player_role") or "All-Rounder"),
            }
            style_metrics = cast(dict[str, object], record.get("style_metrics", {}))
            if not isinstance(style_metrics, dict):
                formatted.append(cast(DisplayRecord, row))
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

            formatted.append(cast(DisplayRecord, row))
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
