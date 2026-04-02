"""
Typed contracts for TeamEngine payloads and request context.
"""

from __future__ import annotations

from typing import Protocol, TypeAlias, TypedDict

import pandas as pd

from core.interfaces.shared_types import (
    ComparisonReportRow,
    ComparisonReportRows,
    DataAccessPort,
    MatrixReportRow,
    SectionHighlightFlags,
    TeamFormRow,
)


class RecorderPort(Protocol):
    """Optional request recorder contract for shell-layer instrumentation."""

    def record(self, message: str) -> None:
        ...


class PhaseWindow(TypedDict):
    start: int
    end: int


class PhaseRules(TypedDict, total=False):
    pp: PhaseWindow
    mid: PhaseWindow
    dth: PhaseWindow
    powerplay: PhaseWindow
    middle: PhaseWindow
    death: PhaseWindow


class TacticalThresholds(TypedDict, total=False):
    form_window_matches: int
    competitive_chase_threshold: int
    low_sample_min_matches: int
    bias_win_pct_min: int
    strong_bias_gap_min: int
    phase_start_year_default: int


class SportConstants(TypedDict, total=False):
    percent_scale: int
    all_out_wickets: int
    balls_per_over: int


class FormatConfig(TypedDict):
    min_balls_for_completed_innings: int
    default_years_window: int
    phases: PhaseRules
    tactical_thresholds: TacticalThresholds
    SPORT_CONSTANTS: SportConstants


class TeamMatchContext(TypedDict, total=False):
    match_df: pd.DataFrame
    phase_df: pd.DataFrame
    reference_date: pd.Timestamp
    tactical_thresholds: TacticalThresholds
    format_config: FormatConfig


class TeamMetricsPayload(TypedDict):
    avg_1st: str
    high_1st: int | str
    low_1st: int | str
    avg_1st_win: str
    low_defended: int | str
    avg_2nd: str
    high_chased: int | str
    avg_succ: str
    avg_fail: str


class TeamBatFirstStats(TypedDict):
    avg: str
    high: int | str
    low: int | str
    avg_win: str
    low_def: int | str


class TeamChaseStats(TypedDict):
    avg: str
    high: int | str
    succ: str
    fail: str


# ---------------------------------------------------------------------------
# Form-guide contracts — MUST be defined before MatrixReportRow/TeamFormRow
# because the functional TypedDict() syntax evaluates values eagerly.
# ---------------------------------------------------------------------------


class FormGuidePayload(TypedDict):
    """Semantic form-guide data passed from builder to formatter."""

    wins: int
    losses: int
    no_results: int
    total: int
    raw_results: list[str]


class FormSequencePayload(TypedDict):
    """Contract for visual form sequences."""

    results: list[str]
    missing_token: str


MATRIX_ROW_HOME_TEAM_COLOR = "home_team_color"
MATRIX_ROW_HOME_TEAM_NAME = "home_team_name"


MatrixReportRows: TypeAlias = list[MatrixReportRow]


TeamFormRows: TypeAlias = list[TeamFormRow]


class TeamEngineProtocol(Protocol):
    def apply_smart_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        ...


class AnalyzerEngineProtocol(Protocol):
    team_engine: TeamEngineProtocol



__all__ = [
    "AnalyzerEngineProtocol",
    "ComparisonReportRow",
    "ComparisonReportRows",
    "DataAccessPort",
    "FormatConfig",
    "FormGuidePayload",
    "FormSequencePayload",
    "MATRIX_ROW_HOME_TEAM_COLOR",
    "MATRIX_ROW_HOME_TEAM_NAME",
    "MatrixReportRow",
    "MatrixReportRows",
    "PhaseRules",
    "PhaseWindow",
    "RecorderPort",
    "SectionHighlightFlags",
    "SportConstants",
    "TacticalThresholds",
    "TeamBatFirstStats",
    "TeamChaseStats",
    "TeamEngineProtocol",
    "TeamFormRow",
    "TeamFormRows",
    "TeamMatchContext",
    "TeamMetricsPayload",
]

