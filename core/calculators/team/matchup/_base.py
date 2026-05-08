"""Pure vectorized rivalry and team-performance calculators."""

# mypy: ignore-errors

from __future__ import annotations

from typing import Mapping, TypedDict, cast

import pandas as pd

from config.shared.venues import VENUE_MAP, get_country_prefixes
from core.calculators.performance import calculate_team_metrics
from core.interfaces.team_types import ComparisonReportRows, MatrixReportRows, TeamFormRows
from core.interfaces.venue_types import VenueMatchupReport
from core.services.match_filter_service import apply_smart_filters as apply_match_filters
from core.services.report_builder import ReportBuilder
from core.services.serialization_service import SerializationService


class GlobalH2HContext(TypedDict):
    home_team: str
    opp_team: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    competitive_chase_threshold: int
    low_sample_min_matches: int
    percent_scale: int


class CountryH2HContext(TypedDict):
    home_team: str
    opp_team: str
    country_name: str | None
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    competitive_chase_threshold: int


class HomeDominanceContext(TypedDict):
    home_team: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    region: Mapping[str, str]


class AwayPerformanceContext(TypedDict):
    team_name: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    region: Mapping[str, str]


class GlobalPerformanceContext(TypedDict):
    team_name: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int


class ContinentPerformanceContext(TypedDict):
    team_name: str
    continent: str
    opp_team: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    competitive_chase_threshold: int


class TeamFormContext(TypedDict):
    team_name: str
    opp_team: str
    continent: str
    limit: int
    min_balls_for_completed_innings: int


class ComparisonRowsPayload(TypedDict):
    rows: ComparisonReportRows


class VenueMatchupPayload(TypedDict):
    payload: VenueMatchupReport


class GlobalH2HStructuredPayload(TypedDict):
    payload: VenueMatchupReport


class MatrixRowsPayload(TypedDict):
    rows: MatrixReportRows


class TeamFormRowsPayload(TypedDict):
    rows: TeamFormRows


class ContinentRowsPayload(TypedDict):
    rows: MatrixReportRows | ComparisonReportRows


def _empty_like(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.iloc[0:0].copy() if isinstance(frame, pd.DataFrame) else pd.DataFrame()


def _filter_year_window(match_df: pd.DataFrame, reference_date: pd.Timestamp, years_back: int) -> pd.DataFrame:
    if match_df.empty:
        return _empty_like(match_df)
    if "start_date" not in match_df.columns:
        return match_df.copy()
    cutoff = reference_date - pd.DateOffset(years=years_back)
    return match_df[match_df["start_date"] >= cutoff].copy()


def _apply_filters(match_df: pd.DataFrame, min_balls: int) -> pd.DataFrame:
    if match_df.empty:
        return _empty_like(match_df)
    return apply_match_filters(match_df, min_balls=min_balls)


# ── Service/config facades ────────────────────────────────────────────────────
# Calculator functions must not call service/config domains directly.
# These module-level wrappers absorb the cross-domain calls so that internal
# calculator functions stay within a single domain boundary.

def _call_build_report_data(
    match_df: pd.DataFrame,
    home_team: str,
    visitor_label: str,
    title: str,
    is_venue_mode: bool,
    calculate_team_stats: object,
) -> object:
    return ReportBuilder._build_report_data(
        match_df, home_team, visitor_label, title,
        is_venue_mode=is_venue_mode,
        calculate_team_stats=calculate_team_stats,
    )


def _comparison_rows(
    match_df: pd.DataFrame,
    home_team: str,
    visitor_label: str,
    title: str,
    competitive_threshold: int,
) -> ComparisonReportRows:
    return cast(ComparisonReportRows, _call_build_report_data(
        match_df,
        home_team,
        visitor_label,
        title,
        is_venue_mode=False,
        calculate_team_stats=lambda df, team_name, _is_home: calculate_team_metrics(
            df=df,
            team_name=team_name,
            competitive_threshold=competitive_threshold,
        ),
    ))


def _matrix_rows(
    match_df: pd.DataFrame,
    team_name: str,
    title: str,
    is_away: bool,
    min_balls: int,
) -> MatrixReportRows:
    return cast(MatrixReportRows, ReportBuilder._generate_matrix_report(
        matches=match_df,
        team_name=team_name,
        title=title,
        is_away=is_away,
        apply_smart_filters=lambda frame: _apply_filters(frame, min_balls),
        serialize_ui_records=SerializationService.serialize_ui_records,
    ))


def _normalize_opp_scope(opp_team: str) -> str:
    return opp_team if opp_team and str(opp_team).strip() and opp_team != "All" else "All"


def _country_scope(home_team: str, country_name: str | None) -> tuple[str, bool]:
    raw_country = str(country_name).strip() if country_name is not None else ""
    default_home_country = raw_country in ("", "All")
    return (home_team if default_home_country else raw_country, default_home_country)


def _country_matchup_mask(match_df: pd.DataFrame, home_team: str, opp_scope: str) -> pd.Series:
    if opp_scope == "All":
        return (match_df["team_bat_1"] == home_team) | (match_df["team_bat_2"] == home_team)
    return (
        ((match_df["team_bat_1"] == home_team) & (match_df["team_bat_2"] == opp_scope))
        | ((match_df["team_bat_1"] == opp_scope) & (match_df["team_bat_2"] == home_team))
    )


def _country_prefix_mask(match_df: pd.DataFrame, prefixes: list[str]) -> pd.Series:
    prefix_tuple = tuple(prefixes)
    mask = pd.Series(False, index=match_df.index)
    if "venue_id" in match_df.columns:
        mask = mask | match_df["venue_id"].fillna("").astype(str).str.upper().str.startswith(prefix_tuple)
    if "venue" in match_df.columns:
        venue_series = match_df["venue"].fillna("").astype(str).str.strip()
        mapped_ids = venue_series.map(VENUE_MAP)
        canonical_ids = venue_series.where(venue_series.isin(set(VENUE_MAP.values())), "")
        resolved_ids = mapped_ids.where(mapped_ids.notna(), canonical_ids).fillna("").astype(str).str.upper()
        mask = mask | resolved_ids.str.startswith(prefix_tuple)
    return mask


def _explicit_country_mask(match_df: pd.DataFrame, country_scope: str) -> pd.Series:
    venue_text = match_df["venue"].astype(str) if "venue" in match_df.columns else pd.Series("", index=match_df.index)
    venue_id_text = (
        match_df["venue_id"].astype(str) if "venue_id" in match_df.columns else pd.Series("", index=match_df.index)
    )
    return venue_text.str.contains(country_scope, case=False, na=False) | venue_id_text.str.contains(
        country_scope, case=False, na=False
    )


def _apply_country_scope(match_df: pd.DataFrame, country_scope: str, default_home_country: bool) -> pd.DataFrame:
    if not country_scope:
        return match_df.copy()
    prefixes = get_country_prefixes(country_scope)
    if prefixes:
        return match_df[_country_prefix_mask(match_df, prefixes)].copy()
    if default_home_country:
        return match_df.copy()
    return match_df[_explicit_country_mask(match_df, country_scope)].copy()

