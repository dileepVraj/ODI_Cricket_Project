"""Typed contracts for player and squad analysis payloads."""

from __future__ import annotations

from typing import Literal, Optional, Protocol, TypeAlias, TypedDict, Union

from core.interfaces.team_types import (
    ComparisonReportRow,
    ComparisonReportRows,
    DataAccessPort,
    MatrixReportRow,
)


class TacticalRecorderPort(Protocol):
    """Contract for recorders that capture tactical alerts from PlayerEngine.

    Distinct from RecorderPort (which declares record()).
    PlayerEngine calls log_tactical_alert() on the recorder.
    """

    def log_tactical_alert(
        self, alert_type: str, message: str
    ) -> None:
        ...


class MatchupRowExtended(TypedDict):
    Bowler: str
    Style: str
    Balls: int
    Runs: int
    Outs: int
    Avg: float
    SR: float
    ThreatRating: str
    Confidence: int
    DismissalStructural: int
    DismissalCaught: int
    DismissalOther: int
    PP_Balls: int
    PP_Runs: int
    PP_Outs: int
    PP_Avg: Optional[float]
    PP_SR: Optional[float]
    PP_ThreatRating: str
    Mid_Balls: int
    Mid_Runs: int
    Mid_Outs: int
    Mid_Avg: Optional[float]
    Mid_SR: Optional[float]
    Mid_ThreatRating: str
    Death_Balls: int
    Death_Runs: int
    Death_Outs: int
    Death_Avg: Optional[float]
    Death_SR: Optional[float]
    Death_ThreatRating: str
    IsBunny: bool


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
    team_a_name: list["MatrixReportRow"]
    team_b_name: list["MatrixReportRow"]


class MatchupsData(TypedDict):
    team_a_name: dict[str, list["ComparisonReportRow"]]
    team_b_name: dict[str, list["ComparisonReportRow"]]


class SquadComparisonPayload(TypedDict):
    SquadComparison: dict[str, list[str]]
    TacticalMatrix: dict[str, list["MatrixReportRow"]]
    Matchups: dict[str, dict[str, list["ComparisonReportRow"]]]
    PlayerStats: dict[str, PlayerStatsIndexed]


class GlobalCompareEnvelope(TypedDict):
    # Depending on dynamic key structure (like "TeamA_vs_TeamB"), payload gets wrapped strictly.
    SquadComparePayload: SquadComparisonPayload


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


FormatRulesMap: TypeAlias = dict[str, Union[
    str, int, float, bool,
    dict[str, Union[int, float, str, bool]],
    list[str],
    None,
]]


class SquadMetricsCompat(Protocol):
    caps: int
    runs: int
    wickets: int
    centuries: int
    fifties: int
    five_wkt_hauls: int
    avg_caps: int


SquadBulkMetricsResult: TypeAlias = dict[str, Union[
    "SquadMetricsCompat",
    list[dict[str, Union[str, int, float, bool, list[Union[str, None]], None]]],
]]


class PlayerAnalyzerPort(Protocol):
    """Port for analyzers that expose a DAL for player venue stats."""

    dal: DataAccessPort


__all__ = [
    "ComparisonReportRow",
    "ComparisonReportRows",
    "DataAccessPort",
    "FormatRulesMap",
    "GlobalCompareEnvelope",
    "MatchupRowExtended",
    "MatchupsData",
    "MatrixReportRow",
    "NormalizedTokenPayload",
    "PhaseRunsPayload",
    "PlayerAnalyzerPort",
    "PlayerStatRow",
    "PlayerStatsIndexed",
    "PlayerVenueStatsFallback",
    "PlayerVenueStatsFallbackPayload",
    "PlayerVenueStatsFallbackRequest",
    "SquadBulkMetricsResult",
    "SquadComparisonPayload",
    "SquadMetricsCompat",
    "TacticalMatrixData",
    "TacticalRecorderPort",
]
