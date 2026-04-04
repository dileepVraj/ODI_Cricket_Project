"""Venue matchup calculator domain."""

from __future__ import annotations

import pandas as pd

from config.shared.team_colors import TEAM_COLORS
from core.calculators.team.venue._base import (
    TeamVenueStatsPayload,
    VenueMatchupContext,
    VenueMatchupPayload,
    VenueMatchupReport,
    _apply_filters,
    _summary_payload,
    _team_intel,
    _venue_avg_payload,
    _venue_window,
)
from core.services.match_filter_service import MatchFilterService
from core.services.report_builder import ReportBuilder
from core.services.report_formatter import ReportFormatter


def _empty_team_stats(team_name: str) -> TeamVenueStatsPayload:
    team_color = TEAM_COLORS.get(team_name) or TEAM_COLORS.get("VISITOR_TEAM") or TEAM_COLORS.get("Visitors", "gray")
    return {
        "wins": 0,
        "defended": 0,
        "chased": 0,
        "bat1": {"avg": None, "high": None, "low": None, "avg_win": None, "low_def": None},
        "chase": {"avg": None, "high": None, "succ": None, "fail": None},
        "team_color": team_color,
        "team_tone": None,
        "low_sample_warnings": [],
        "highlight_flags": {"has_low_sample_warnings": False},
        "derived_badges": [],
    }


def _empty_match_intel(home_team: str, opp_team: str) -> VenueMatchupReport:
    return {
        "summary": {"matches": 0, "win_pct": 0, "tie_nr": 0},
        "team_a": {"name": home_team, "stats": _empty_team_stats(home_team)},
        "team_b": {"name": opp_team, "stats": _empty_team_stats(opp_team)},
        "venue_avg": {"avg_1st": None, "avg_2nd": None, "avg_win_score": None},
        "MATCH_IDS": None,
        "low_sample_warnings": [],
        "highlight_flags": {"has_low_sample_warnings": False, "has_form_guide": False},
        "derived_badges": [],
    }


def calculate_venue_matchup_payload(match_df: pd.DataFrame, context: VenueMatchupContext) -> VenueMatchupPayload:
    venue_df, _ = _venue_window(match_df, context["stadium_id"], context["years_back"], context["reference_date"])
    if venue_df.empty:
        return {"payload": _empty_match_intel(context["home_team"], context["opp_team"])}
    clean_df = _apply_filters(venue_df, context["min_balls_for_completed_innings"])
    matchup_mask = ((clean_df["team_bat_1"] == context["home_team"]) & (clean_df["team_bat_2"] == context["opp_team"])) | ((clean_df["team_bat_1"] == context["opp_team"]) & (clean_df["team_bat_2"] == context["home_team"]))
    matchup_df = clean_df[matchup_mask].copy()
    summary_df = matchup_df[~MatchFilterService.get_excluded_no_result_mask(matchup_df)].copy()
    if summary_df.empty:
        return {"payload": _empty_match_intel(context["home_team"], context["opp_team"])}
    return {"payload": _build_match_intel(summary_df, context)}


def _build_match_intel(summary_df: pd.DataFrame, context: VenueMatchupContext) -> VenueMatchupReport:
    summary = _summary_payload(summary_df, context["home_team"], context["percent_scale"])
    team_a_stats = _team_intel(summary_df, context["home_team"], context["competitive_chase_threshold"], context["low_sample_min_matches"])
    team_b_stats = _team_intel(summary_df, context["opp_team"], context["competitive_chase_threshold"], context["low_sample_min_matches"])
    last_5_home = ReportFormatter._none_if_placeholder(ReportFormatter.format_form_guide(ReportBuilder._build_form_data_payload(summary_df, context["home_team"])))
    last_5_away = ReportFormatter._none_if_placeholder(ReportFormatter.format_form_guide(ReportBuilder._build_form_data_payload(summary_df, context["opp_team"])))
    low_sample_warnings = [*team_a_stats["low_sample_warnings"], *team_b_stats["low_sample_warnings"]]
    summary["last_5_home"] = last_5_home
    summary["last_5_away"] = last_5_away
    return {
        "summary": summary,
        "team_a": {"name": context["home_team"], "stats": team_a_stats},
        "team_b": {"name": context["opp_team"], "stats": team_b_stats},
        "venue_avg": _venue_avg_payload(summary_df, context["competitive_chase_threshold"]),
        "MATCH_IDS": ",".join(summary_df["match_id"].astype(str).unique().tolist()) or None,
        "low_sample_warnings": low_sample_warnings,
        "highlight_flags": {"has_low_sample_warnings": bool(low_sample_warnings), "has_form_guide": bool(last_5_home or last_5_away)},
        "derived_badges": [],
    }
