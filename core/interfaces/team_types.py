"""
Typed contracts for TeamEngine payloads and request context.
"""

from __future__ import annotations

from typing import Literal, Protocol, TypeAlias, TypedDict, Union, Sequence

import pandas as pd


class RecorderPort(Protocol):
    """Optional request recorder contract for shell-layer instrumentation."""

    def record(self, message: str) -> None:
        ...


class TacticalRecorderPort(Protocol):
    """Contract for recorders that capture tactical alerts from PlayerEngine.

    Distinct from RecorderPort (which declares record()).
    PlayerEngine calls log_tactical_alert() on the recorder.
    """

    def log_tactical_alert(
        self, alert_type: str, message: str
    ) -> None:
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


class TeamVenueBattingStats(TypedDict):
    avg: str | int | None
    high: int | str | None
    low: int | str | None
    avg_win: str | int | None
    low_def: int | str | None


class TeamVenueChaseStats(TypedDict):
    avg: str | int | None
    high: int | str | None
    succ: str | int | None
    fail: str | int | None


class TeamVenueStatsPayload(TypedDict):
    wins: int
    defended: int
    chased: int
    bat1: TeamVenueBattingStats
    chase: TeamVenueChaseStats
    team_color: str | None
    team_tone: str | None
    low_sample_warnings: list[str]
    highlight_flags: SectionHighlightFlags
    derived_badges: list[str]


class VenueMatchupSummary(TypedDict, total=False):
    matches: int
    win_pct: int
    tie_nr: int
    last_5_home: str | None
    last_5_away: str | None


class VenueMatchupTeamPayload(TypedDict):
    name: str
    stats: TeamVenueStatsPayload


class VenueAveragePayload(TypedDict):
    avg_1st: str | int | None
    avg_2nd: str | int | None
    avg_win_score: str | int | None


class VenueMatchupReport(TypedDict):
    summary: VenueMatchupSummary
    team_a: VenueMatchupTeamPayload
    team_b: VenueMatchupTeamPayload
    venue_avg: VenueAveragePayload
    MATCH_IDS: str | None
    low_sample_warnings: list[str]
    highlight_flags: SectionHighlightFlags
    derived_badges: list[str]


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


class ReportMetricPayload(TypedDict):
    """Typed context for single metric formatting."""
    metric_label: str
    value: Union[str, int, float, None]
    tone: str
    is_low_sample: bool


class MatchupVisualPayload(TypedDict):
    """UI metadata for matchup rows."""
    highlight_flags: dict[str, bool]
    cell_tones: dict[str, str]
    derived_badges: list[str]


class MatchupBadgePayload(TypedDict):
    """Payload for derived matchup status badges."""
    is_bunny: bool
    label: str


class FormSequencePayload(TypedDict):
    """Contract for visual form sequences."""
    results: list[str]
    missing_token: str


MatrixReportRow = TypedDict(
    "MatrixReportRow",
    {
        "Opponent": str,
        "Mat": int,
        "Won": int,
        "Lost": int,
        "Tie/NR": int,
        "Win %": str,
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


# TeamFormSummary consolidated into FormGuidePayload


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


class VenuePercentBreakdown(TypedDict):
    bat_first: int
    chase: int
    tie_nr: int


class VenueBiasReport(TypedDict):
    venue_id: str
    period: int
    total_matches: int
    bat1_wins: int
    chase_wins: int
    bat1_win_pct: int
    chase_win_pct: int
    bias_verdict: str
    avg_1st_inn: str | int | None
    avg_2nd_inn: str | int | None
    percent_breakdown: VenuePercentBreakdown
    highlight_flags: SectionHighlightFlags
    derived_badges: list[str]
    MATCH_IDS: str | None
    raw_matches: str


class PhaseSummaryCell(TypedDict):
    avg: float
    n: int
    wkts: float


class InningsPhaseSummary(TypedDict):
    pp: PhaseSummaryCell
    mid: PhaseSummaryCell
    dth: PhaseSummaryCell
    total: PhaseSummaryCell


PhaseSummaryByInnings = TypedDict(
    "PhaseSummaryByInnings",
    {"1": InningsPhaseSummary, "2": InningsPhaseSummary},
)


class VenuePhaseFilterCriteria(TypedDict):
    min_first_innings_balls: int
    min_first_innings_overs: float
    keep_all_outs: bool
    keep_successful_chases: bool
    drop_short_no_result_only: bool


class TeamVenuePhaseSnapshot(TypedDict):
    team: str
    stats: PhaseSummaryByInnings


class ScenarioRow(TypedDict):
    label: str
    home_value: float | None
    away_value: float | None
    higher_better: bool
    diff_text: str
    diff_tone: str


class ScenarioRows(TypedDict):
    bat_first: list[ScenarioRow]
    chasing: list[ScenarioRow]


class BatFirstGlobalHabits(TypedDict):
    home_team_pp_runs: float
    away_team_pp_runs: float
    home_team_pp_wkts: float
    away_team_pp_wkts: float
    home_team_mid_runs: float
    away_team_mid_runs: float
    home_team_mid_wkts: float
    away_team_mid_wkts: float
    home_team_dth_runs: float
    away_team_dth_runs: float
    home_team_dth_wkts: float
    away_team_dth_wkts: float


class ChasingGlobalHabits(TypedDict):
    home_team_pp_runs: float
    away_team_pp_runs: float
    home_team_mid_wkts: float
    away_team_mid_wkts: float
    home_team_dth_wkts: float
    away_team_dth_wkts: float


class RunRateHabits(TypedDict):
    pp_rr: float
    mid_rr: float
    dth_rr: float
    avg_score: float


class VenueGlobalHabits(TypedDict):
    start_year: int | str
    bat_first: BatFirstGlobalHabits
    chasing: ChasingGlobalHabits
    home: RunRateHabits
    away: RunRateHabits
    scenario_rows: ScenarioRows


class VenuePhasesReport(TypedDict, total=False):
    stadium_id: str
    match_count: int
    years: int
    filter_criteria: VenuePhaseFilterCriteria
    baseline: PhaseSummaryByInnings
    home_at_venue: TeamVenuePhaseSnapshot | None
    away_at_venue: TeamVenuePhaseSnapshot | None
    global_habits: VenueGlobalHabits | None
    MATCH_IDS: str | None


# Data Extract & Audit Definition
class MatchAuditRecord(TypedDict):
    start_date: str
    venue: str
    winner: str
    team_bat_1: str
    score_inn1: str
    team_bat_2: str
    score_inn2: str
    status: str
    status_tone: str

# Player Stat TypedDict explicitly declared without primitive aliases
class PlayerStatRow(TypedDict, total=False):
    Player: str
    Mat: int
    Inns: int
    Runs: int
    Avg: str
    SR: str
    Wkts: int
    Econ: str

PlayerStatsIndexed: TypeAlias = dict[str, PlayerStatRow]

class TacticalMatrixData(TypedDict):
    team_a_name: list['MatrixReportRow']
    team_b_name: list['MatrixReportRow']

class MatchupsData(TypedDict):
    team_a_name: dict[str, list['ComparisonReportRow']]
    team_b_name: dict[str, list['ComparisonReportRow']]

class SquadComparisonPayload(TypedDict):
    SquadComparison: dict[str, list[str]]
    TacticalMatrix: dict[str, list['MatrixReportRow']]
    Matchups: dict[str, dict[str, list['ComparisonReportRow']]]
    PlayerStats: dict[str, PlayerStatsIndexed]

class GlobalCompareEnvelope(TypedDict):
    # Depending on dynamic key structure (like "TeamA_vs_TeamB"), payload gets wrapped strictly.
    SquadComparePayload: SquadComparisonPayload

# ---------------------------------------------------------------------------
# Strike-1 Recovery Contracts (Mandatory 17)
# ---------------------------------------------------------------------------


class PlayerVenueStatsFallback(TypedDict):
    """Contract for player venue stats fallback request context."""
    analyzer_id: str
    player_name: str
    venue_id: str
    years: int
    fallback_stats: dict[str, float]


class PlayerVenueStatsFallbackRequest(TypedDict):
    """Input contract for player venue stats requests."""
    player_name: str
    venue_id: str
    years: int


class PlayerVenueStatsFallbackPayload(TypedDict):
    """Return contract for player venue stats requests."""
    batting: dict[str, Union[str, int, float, None]] | None
    bowling: dict[str, Union[str, int, float, None]] | None


class NormalizedTokenPayload(TypedDict):
    """Contract for venue token normalization inputs."""
    raw_value: str | int | None
    token_type: Literal["venue", "label", "code"]
    metadata: dict[str, str]


class PhaseRunsPayload(TypedDict):
    """Contract for phase-level run totals in team service."""
    phase_id: str
    total_runs: int
    baseline_runs: int
    coverage_pct: float


# FormGuidePayload, ReportMetricPayload, MatchupVisualPayload,
# MatchupBadgePayload, and FormSequencePayload are defined above
# (before MatrixReportRow) to avoid NameError in functional TypedDict syntax.


class PlayerAnalyzerPort(Protocol):
    """Port for analyzers that expose a DAL for player venue stats."""
    dal: DataAccessPort


class SerializedEnvelope(TypedDict, total=False):
    """Finalized serialization return contract."""
    data: EnrichablePayload


# Flexible display cell type — covers all UI table values
CellValue: TypeAlias = Union[str, int, float, bool, list[str | None], None]
DisplayRecord: TypeAlias = dict[str, CellValue]

# Param-mapper contracts (replaces Dict[str, object])
ManifestValue: TypeAlias = Union[str, int, float, bool, list[str], dict[str, str], None]
ManifestFunctionDef: TypeAlias = dict[str, ManifestValue]
RawContextParams: TypeAlias = dict[str, Union[str, int, float, list[str], None]]
MappedEngineParams: TypeAlias = dict[str, Union[str, int, float, bool, list[str], dict[str, str], None]]

# SquadService contracts
# FormatRulesMap replaces Dict[str, object] for format-rules injection into SquadService.__init__
FormatRulesMap: TypeAlias = dict[str, Union[
    str, int, float, bool,
    dict[str, Union[int, float, str, bool]],
    list[str],
    None,
]]

# SquadBulkMetricsResult replaces Dict[str, object] for SquadService.get_bulk_metrics return
# Note: squad_metrics is a SquadMetrics dataclass (from player_interface); player_stats is the
# raw list of per-player metric records built by _build_bulk_player_stats.
SquadBulkMetricsResult: TypeAlias = dict[str, Union[
    "SquadMetricsCompat",
    list[dict[str, Union[str, int, float, bool, list[Union[str, None]], None]]],
]]

# Protocol-compatible alias for SquadMetrics dataclass (avoids cross-module import cycle)
class SquadMetricsCompat(Protocol):
    caps: int
    runs: int
    wickets: int
    centuries: int
    fifties: int
    five_wkt_hauls: int
    avg_caps: int

# ---------------------------------------------------------------------------
# Structural Protocols & Output Unions
# ---------------------------------------------------------------------------

EnrichablePayload: TypeAlias = Union[
    list['ComparisonReportRow'], 
    list['MatrixReportRow'], 
    'VenueBiasReport', 
    'VenuePhasesReport', 
    'VenueMatchupReport',
    SquadComparisonPayload,
    GlobalCompareEnvelope,
]

class EnrichedListPayload(TypedDict):
    stats: Union[list['ComparisonReportRow'], list['MatrixReportRow']]
    match_audit: list[MatchAuditRecord]

class TeamEngineProtocol(Protocol):
    def apply_smart_filters(self, df: pd.DataFrame) -> pd.DataFrame: ...

class AnalyzerEngineProtocol(Protocol):
    team_engine: TeamEngineProtocol

class DataclassProtocol(Protocol):
    __dataclass_fields__: dict[str, type]

class PydanticProtocol(Protocol):
    def model_dump(self) -> SerializedEnvelope: ...
