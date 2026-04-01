"""
Typed contracts for TeamEngine payloads and request context.
"""

from __future__ import annotations

from typing import Dict, Literal, Optional, Protocol, Sequence, Tuple, TypeAlias, TypedDict, Union

import pandas as pd


class RecorderPort(Protocol):
    """Optional request recorder contract for shell-layer instrumentation."""

    def record(self, message: str) -> None:
        ...


class DataAccessPort(Protocol):
    """Opaque DAL port placeholder for constructor compatibility."""

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


class SectionHighlightFlags(TypedDict, total=False):
    has_low_sample_warnings: bool
    has_form_guide: bool
    has_strong_bias: bool
    is_overall: bool
    is_win: bool


class ComparisonReportRow(TypedDict, total=False):
    Metric: str
    Value: str | int
    row_kind: str
    display_metric: str
    section_label: str
    section_tone: str
    value_tone: str
    is_zero_or_empty: bool


ComparisonReportRows: TypeAlias = list[ComparisonReportRow]


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


MatrixReportRow = TypedDict(
    "MatrixReportRow",
    {
        "Opponent": str,
        "Mat": int,
        "Won": int,
        "Lost": int,
        "Tie/NR": int,
        "Win %": str,
        "team_color": Optional[str],
        MATRIX_ROW_HOME_TEAM_COLOR: Optional[str],
        MATRIX_ROW_HOME_TEAM_NAME: Optional[str],
        "form_data": FormGuidePayload,
        "Opp Avg (1st)": str,
        "MATCH_IDS": str,
        "cell_tones": dict[str, str],
        "highlight_flags": SectionHighlightFlags,
        "derived_badges": list[str],
    },
    total=False,
)


MatrixReportRows: TypeAlias = list[MatrixReportRow]


TeamFormRow = TypedDict(
    "TeamFormRow",
    {
        "Date": str,
        "Opponent": str,
        "Venue": str,
        "Result": str,
        "TeamScore": str,
        "OppScore": str,
        "RawResult": str,
        "ResultTone": str,
        "ResultSymbol": str,
        "form_data": FormGuidePayload,
        "highlight_flags": SectionHighlightFlags,
        "derived_badges": list[str],
    },
    total=False,
)


TeamFormRows: TypeAlias = list[TeamFormRow]


class TeamEngineProtocol(Protocol):
    def apply_smart_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        ...


class AnalyzerEngineProtocol(Protocol):
    team_engine: TeamEngineProtocol


# ---------------------------------------------------------------------------
# re-exports: backward compat — all 16 import sites use team_types directly.
# Remove once all import sites are migrated to the specific domain module.
# ---------------------------------------------------------------------------

from core.interfaces.venue_types import (
    TeamVenueBattingStats,
    TeamVenueChaseStats,
    TeamVenueStatsPayload,
    VenueMatchupSummary,
    VenueMatchupTeamPayload,
    VenueAveragePayload,
    VenueMatchupReport,
    HomeFortressSummary,
    HomeFortressTeamPayload,
    HomeFortressReport,
    VenuePercentBreakdown,
    VenueBiasCI,
    VenueScoreStats,
    VenueScoreBand,
    VenueScoreBanding,
    VenueTossLossRecovery,
    VenueScoreDistribution,
    VenueScoreExtremes,
    VenueBiasTrend,
    VenueTossIntelligence,
    VenueBiasReport,
    PhaseSummaryCell,
    PhasePayload,
    InningsPhaseSummary,
    PhaseSummaryByInnings,
    VenuePhaseFilterCriteria,
    TeamVenuePhaseSnapshot,
    ScenarioRow,
    ScenarioDiff,
    ScenarioRows,
    ScenarioDiffRows,
    ScenarioDiffs,
    BatFirstGlobalHabits,
    ChasingGlobalHabits,
    RunRateHabits,
    VenueGlobalHabits,
    VenuePhasesReport,
)
from core.interfaces.player_types import (
    TacticalRecorderPort,
    MatchupRowExtended,
    PlayerStatRow,
    PlayerStatsIndexed,
    TacticalMatrixData,
    MatchupsData,
    SquadComparisonPayload,
    GlobalCompareEnvelope,
    PlayerVenueStatsFallback,
    PlayerVenueStatsFallbackRequest,
    PlayerVenueStatsFallbackPayload,
    NormalizedTokenPayload,
    PhaseRunsPayload,
    FormatRulesMap,
    SquadBulkMetricsResult,
    SquadMetricsCompat,
    PlayerAnalyzerPort,
)
from core.interfaces.serialization_types import (
    MatchAuditRecord,
    ReportMetricPayload,
    MatchupVisualPayload,
    MatchupBadgePayload,
    DataclassProtocol,
    PydanticProtocol,
    SerializedEnvelope,
    CellValue,
    DisplayRecord,
    ManifestValue,
    ManifestFunctionDef,
    RawContextParams,
    MappedEngineParams,
    EnrichablePayload,
    EnrichedListPayload,
)
