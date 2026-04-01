from __future__ import annotations

"""Typed contracts for serialisation, display, and output pipelines."""

from typing import Protocol, TypeAlias, TypedDict, Union

from core.interfaces.team_types import ComparisonReportRow, MatrixReportRow, TeamFormRow
from core.interfaces.venue_types import (
    HomeFortressReport,
    VenueBiasReport,
    VenueMatchupReport,
    VenuePhasesReport,
)
from core.interfaces.player_types import GlobalCompareEnvelope, SquadComparisonPayload


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


CellValue: TypeAlias = Union[str, int, float, bool, list[str | None], None]
DisplayRecord: TypeAlias = dict[str, CellValue]
ManifestValue: TypeAlias = Union[str, int, float, bool, list[str], dict[str, str], None]
ManifestFunctionDef: TypeAlias = dict[str, ManifestValue]
RawContextParams: TypeAlias = dict[str, Union[str, int, float, list[str], None]]
MappedEngineParams: TypeAlias = dict[str, Union[str, int, float, bool, list[str], dict[str, str], None]]

EnrichablePayload: TypeAlias = Union[
    list["ComparisonReportRow"],
    list["MatrixReportRow"],
    list["TeamFormRow"],
    "VenueBiasReport",
    "VenuePhasesReport",
    "VenueMatchupReport",
    "HomeFortressReport",
    SquadComparisonPayload,
    GlobalCompareEnvelope,
]


class SerializedEnvelope(TypedDict, total=False):
    """Finalized serialization return contract."""

    data: EnrichablePayload


class EnrichedListPayload(TypedDict):
    stats: Union[list["ComparisonReportRow"], list["MatrixReportRow"], list["TeamFormRow"]]
    match_audit: list[MatchAuditRecord]


class DataclassProtocol(Protocol):
    __dataclass_fields__: dict[str, type]


class PydanticProtocol(Protocol):
    def model_dump(self) -> SerializedEnvelope:
        ...


__all__ = [
    "CellValue",
    "ComparisonReportRow",
    "DataclassProtocol",
    "DisplayRecord",
    "EnrichablePayload",
    "EnrichedListPayload",
    "GlobalCompareEnvelope",
    "HomeFortressReport",
    "ManifestFunctionDef",
    "ManifestValue",
    "MappedEngineParams",
    "MatchAuditRecord",
    "MatchupBadgePayload",
    "MatchupVisualPayload",
    "MatrixReportRow",
    "PydanticProtocol",
    "RawContextParams",
    "ReportMetricPayload",
    "SerializedEnvelope",
    "SquadComparisonPayload",
    "TeamFormRow",
    "VenueBiasReport",
    "VenueMatchupReport",
    "VenuePhasesReport",
]
