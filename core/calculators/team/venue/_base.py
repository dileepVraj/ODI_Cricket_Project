"""Shared venue calculator contracts and helpers."""

from __future__ import annotations

from typing import TypedDict, cast

import pandas as pd

from config.shared.team_colors import TEAM_COLORS
from core.calculators.performance import calculate_team_metrics
from core.interfaces.team_types import ComparisonReportRows
from core.interfaces.venue_types import (
    HomeFortressReport,
    VenueAveragePayload,
    TeamVenueStatsPayload,
    VenueBiasReport,
    VenueMatchupReport,
    VenueMatchupSummary,
    VenuePhasesReport,
)
from core.services.match_filter_service import MatchFilterService, apply_smart_filters as apply_match_filters
from core.services.report_builder import ReportBuilder
from core.services.report_formatter import ReportFormatter
from core.services.venue_service import VenueService
from core.utils.display_math import avg_with_count


class HomeFortressContext(TypedDict):
    stadium_id: str
    home_team: str
    opp_team: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    competitive_chase_threshold: int


class VenueBiasContext(TypedDict):
    stadium_id: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    percent_scale: int
    bias_win_pct_min: int
    strong_bias_gap_min: int


class VenueMatchupContext(TypedDict):
    stadium_id: str
    home_team: str
    opp_team: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    competitive_chase_threshold: int
    low_sample_min_matches: int
    percent_scale: int


class VenuePhasesContext(TypedDict):
    stadium_id: str
    years: int
    reference_date: pd.Timestamp
    match_df: pd.DataFrame
    home_team: str | None
    away_team: str | None
    min_balls_for_completed_innings: int
    all_out_wickets: int
    balls_per_over: int
    phases: dict[str, list[int]]
    phase_start_year_default: int


class ComparisonRowsPayload(TypedDict):
    rows: ComparisonReportRows


class HomeFortressStructuredPayload(TypedDict):
    payload: HomeFortressReport


class VenueBiasPayload(TypedDict):
    report: VenueBiasReport | None


class VenueMatchupPayload(TypedDict):
    payload: VenueMatchupReport


class VenuePhasesPayload(TypedDict):
    report: VenuePhasesReport


def _safe_percent(numerator: int, denominator: int, scale: int) -> int:
    return int((numerator / denominator) * scale) if denominator > 0 else 0


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


def _venue_window(
    match_df: pd.DataFrame,
    stadium_id: str,
    years_back: int,
    reference_date: pd.Timestamp,
) -> tuple[pd.DataFrame, str]:
    if match_df.empty:
        return _empty_like(match_df), stadium_id
    venue_mask = VenueService._build_venue_mask(match_df, stadium_id)
    venue_df = match_df[venue_mask].copy() if bool(venue_mask.any()) else _empty_like(match_df)
    return _filter_year_window(venue_df, reference_date, years_back), stadium_id


def _normalize_none_marker(value: str | int | None) -> str | int | None:
    return cast(str | int | None, ReportFormatter._none_if_placeholder(value))


def _normalize_text_metric(value: str | int | None) -> str | None:
    normalized = ReportFormatter._none_if_placeholder(value)
    if normalized is None:
        return None
    return str(normalized)


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


def _resolve_team_color(team_name: str) -> str:
    return (
        TEAM_COLORS.get(team_name)
        or TEAM_COLORS.get("VISITOR_TEAM")
        or TEAM_COLORS.get("Visitors", "gray")
    )


def _comparison_rows(
    match_df: pd.DataFrame,
    home_team: str,
    visitor_label: str,
    title: str,
    competitive_threshold: int,
    is_venue_mode: bool,
) -> ComparisonReportRows:
    return cast(ComparisonReportRows, _call_build_report_data(
        match_df,
        home_team,
        visitor_label,
        title,
        is_venue_mode=is_venue_mode,
        calculate_team_stats=lambda df, team_name, _is_home: calculate_team_metrics(
            df=df,
            team_name=team_name,
            competitive_threshold=competitive_threshold,
        ),
    ))


def _summary_payload(summary_df: pd.DataFrame, home_team: str, percent_scale: int) -> VenueMatchupSummary:
    unique_df = summary_df.groupby("match_id").first() if "match_id" in summary_df.columns else summary_df
    matches = len(unique_df)
    winner_series = unique_df["winner"].astype(str).str.lower().str.strip()
    home_wins = int((winner_series == home_team.lower().strip()).sum())
    tie_nr = int(winner_series.isin(["tie", "no result", "nan", "none"]).sum())
    decisions = matches - tie_nr
    return {"matches": matches, "win_pct": _safe_percent(home_wins, decisions, percent_scale), "tie_nr": tie_nr}


def _low_sample_warnings(team_name: str, payload: TeamVenueStatsPayload, min_matches: int) -> list[str]:
    sample_sizes = [
        ReportFormatter._extract_sample_size(payload["bat1"].get("avg")),
        ReportFormatter._extract_sample_size(payload["bat1"].get("avg_win")),
        ReportFormatter._extract_sample_size(payload["chase"].get("avg")),
    ]
    return ReportFormatter._format_low_sample_warnings(team_name, sample_sizes, min_matches)


def _team_intel(
    summary_df: pd.DataFrame,
    team_name: str,
    competitive_threshold: int,
    low_sample_min_matches: int,
) -> TeamVenueStatsPayload:
    stats = calculate_team_metrics(df=summary_df, team_name=team_name, competitive_threshold=competitive_threshold)
    team_wins = summary_df[summary_df["winner"] == team_name]
    team_wins_first = (
        team_wins.groupby("match_id").first()
        if "match_id" in team_wins.columns and not team_wins.empty
        else team_wins
    )
    payload: TeamVenueStatsPayload = {
        "wins": len(team_wins_first),
        "defended": int((team_wins_first["team_bat_1"] == team_name).sum()),
        "chased": int((team_wins_first["team_bat_2"] == team_name).sum()),
        "bat1": {
            "avg": stats["avg_1st"],
            "high": stats["high_1st"],
            "low": stats["low_1st"],
            "avg_win": stats["avg_1st_win"],
            "low_def": _normalize_text_metric(stats["low_defended"]),
        },
        "chase": {
            "avg": stats["avg_2nd"],
            "high": stats["high_chased"],
            "succ": stats["avg_succ"],
            "fail": stats["avg_fail"],
        },
        "team_color": _resolve_team_color(team_name),
        "team_tone": None,
        "low_sample_warnings": [],
        "highlight_flags": {},
        "derived_badges": [],
    }
    payload["low_sample_warnings"] = _low_sample_warnings(team_name, payload, low_sample_min_matches)
    payload["highlight_flags"] = {"has_low_sample_warnings": bool(payload["low_sample_warnings"])}
    return payload


def _venue_avg_payload(summary_df: pd.DataFrame, competitive_threshold: int) -> VenueAveragePayload:
    included_mask = MatchFilterService.get_valid_matches_mask(summary_df)
    short_second_mask = MatchFilterService.get_excluded_short_second_mask(summary_df)
    valid_1st = summary_df[included_mask | short_second_mask]
    valid_2nd = summary_df[included_mask]
    is_chase_win = valid_2nd["winner"] == valid_2nd["team_bat_2"]
    comp_mask = (~is_chase_win) | (valid_2nd["score_inn2"] >= competitive_threshold)
    comp_2nd = valid_2nd[comp_mask]
    return {
        "avg_1st": _normalize_none_marker(avg_with_count(valid_1st, "score_inn1")),
        "avg_2nd": _normalize_none_marker(avg_with_count(comp_2nd, "score_inn2")),
        "avg_win_score": _normalize_none_marker(avg_with_count(valid_1st[valid_1st["winner"] == valid_1st["team_bat_1"]], "score_inn1")),
    }
