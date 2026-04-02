"""Typed contracts for venue analysis payloads."""

from __future__ import annotations

from typing import Dict, Tuple, TypeAlias, TypedDict

import pandas as pd

from core.interfaces.shared_types import ComparisonReportRows, SectionHighlightFlags


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


class HomeFortressSummary(TypedDict, total=False):
    matches: int
    home_win_pct: int
    tie_nr: int


class HomeFortressTeamPayload(TypedDict):
    name: str
    stats: TeamVenueStatsPayload


class HomeFortressReport(TypedDict):
    summary: HomeFortressSummary
    home: HomeFortressTeamPayload
    visitor: HomeFortressTeamPayload
    venue_avg: VenueAveragePayload
    team_colors: dict[str, str]
    MATCH_IDS: str | None
    low_sample_warnings: list[str]


class VenuePercentBreakdown(TypedDict):
    bat_first: int
    chase: int
    tie_nr: int


class VenueBiasCI(TypedDict):
    lower: int
    upper: int


class VenueScoreStats(TypedDict):
    min: int
    max: int
    median: int
    std: int


class VenueScoreBand(TypedDict):
    label: str
    count: int
    pct: int


class VenueScoreBanding(TypedDict):
    inn1_bands: list[VenueScoreBand]
    total: int


class VenueTossLossRecovery(TypedDict):
    forced_bat_win_pct: int | None
    forced_bowl_win_pct: int | None
    forced_bat_count: int
    forced_bowl_count: int
    data_available: bool


class VenueScoreDistribution(TypedDict):
    inn1: VenueScoreStats
    inn2: VenueScoreStats


class VenueScoreExtremes(TypedDict):
    lowest_defended: int | None
    highest_chased: int | None


class VenueBiasTrend(TypedDict):
    direction: str
    recent_pct: int | None
    historical_pct: int | None


class VenueTossIntelligence(TypedDict):
    chose_bat_win_pct: int | None
    chose_bowl_win_pct: int | None
    toss_match_count: int
    data_available: bool


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
    confidence_interval: VenueBiasCI
    sample_reliability: str
    score_distribution: VenueScoreDistribution | None
    score_extremes: VenueScoreExtremes
    bias_trend: VenueBiasTrend
    toss_intelligence: VenueTossIntelligence
    MATCH_IDS: str | None
    raw_matches: str


class PhaseSummaryCell(TypedDict):
    avg: float
    n: int
    wkts: float


class PhasePayload(TypedDict):
    phase_df: pd.DataFrame
    phase_bounds: Dict[str, Tuple[int, int]]
    phase_overs: Dict[str, float]


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


class ScenarioDiff(TypedDict):
    label: str
    home_value: float | None
    away_value: float | None
    higher_better: bool
    diff: float
    advantage: str


class ScenarioRows(TypedDict):
    bat_first: list[ScenarioRow]
    chasing: list[ScenarioRow]


class ScenarioDiffRows(TypedDict):
    bat_first: list[ScenarioDiff]
    chasing: list[ScenarioDiff]


ScenarioDiffs: TypeAlias = list[ScenarioDiff]


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


__all__ = [
    "BatFirstGlobalHabits",
    "ChasingGlobalHabits",
    "ComparisonReportRows",
    "HomeFortressReport",
    "HomeFortressSummary",
    "HomeFortressTeamPayload",
    "InningsPhaseSummary",
    "PhasePayload",
    "PhaseSummaryByInnings",
    "PhaseSummaryCell",
    "RunRateHabits",
    "ScenarioDiff",
    "ScenarioDiffRows",
    "ScenarioDiffs",
    "ScenarioRow",
    "ScenarioRows",
    "SectionHighlightFlags",
    "TeamVenueBattingStats",
    "TeamVenueChaseStats",
    "TeamVenuePhaseSnapshot",
    "TeamVenueStatsPayload",
    "VenueAveragePayload",
    "VenueBiasCI",
    "VenueBiasReport",
    "VenueBiasTrend",
    "VenueGlobalHabits",
    "VenueMatchupReport",
    "VenueMatchupSummary",
    "VenueMatchupTeamPayload",
    "VenuePercentBreakdown",
    "VenuePhaseFilterCriteria",
    "VenuePhasesReport",
    "VenueScoreBand",
    "VenueScoreBanding",
    "VenueScoreDistribution",
    "VenueScoreExtremes",
    "VenueScoreStats",
    "VenueTossIntelligence",
    "VenueTossLossRecovery",
]
