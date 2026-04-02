"""Shared interface types used across multiple domain modules.
Extracted from team_types to break circular import dependencies."""

from __future__ import annotations

from typing import Optional, Protocol, TypeAlias, TypedDict


class SectionHighlightFlags(TypedDict, total=False):
    has_low_sample_warnings: bool
    has_form_guide: bool
    has_strong_bias: bool
    is_overall: bool
    is_win: bool


class DataAccessPort(Protocol):
    """Opaque DAL port placeholder for constructor compatibility."""

    ...


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
        "home_team_color": Optional[str],
        "home_team_name": Optional[str],
        "form_data": dict[str, int | list[str]],
        "Opp Avg (1st)": str,
        "MATCH_IDS": str,
        "cell_tones": dict[str, str],
        "highlight_flags": SectionHighlightFlags,
        "derived_badges": list[str],
    },
    total=False,
)


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
        "form_data": dict[str, int | list[str]],
        "highlight_flags": SectionHighlightFlags,
        "derived_badges": list[str],
    },
    total=False,
)
