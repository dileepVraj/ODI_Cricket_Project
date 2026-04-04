from __future__ import annotations

# mypy: ignore-errors

import pandas as pd

from core.services.venue_service import VenueService

from ._base import (
    AwayPerformanceContext,
    ContinentPerformanceContext,
    GlobalPerformanceContext,
    HomeDominanceContext,
    MatrixRowsPayload,
    _filter_year_window,
    _matrix_rows,
    _normalize_opp_scope,
)

def calculate_home_dominance_payload(match_df: pd.DataFrame, context: HomeDominanceContext) -> MatrixRowsPayload:
    prefix = context["region"].get(context["home_team"])
    if not prefix:
        return {"rows": []}
    window_df = _filter_year_window(match_df, context["reference_date"], context["years_back"])
    if window_df.empty:
        return {"rows": []}
    venue_col = "venue_id" if "venue_id" in window_df.columns else "venue"
    team_mask = (window_df["team_bat_1"] == context["home_team"]) | (window_df["team_bat_2"] == context["home_team"])
    match_df_home = window_df[team_mask & window_df[venue_col].astype(str).str.startswith(prefix)].copy()
    return {"rows": _matrix_rows(match_df_home, context["home_team"], "DOMINANCE_MATRIX", False, context["min_balls_for_completed_innings"])} if not match_df_home.empty else {"rows": []}


def calculate_away_performance_payload(match_df: pd.DataFrame, context: AwayPerformanceContext) -> MatrixRowsPayload:
    prefix = context["region"].get(context["team_name"])
    if not prefix:
        return {"rows": []}
    window_df = _filter_year_window(match_df, context["reference_date"], context["years_back"])
    if window_df.empty:
        return {"rows": []}
    venue_col = "venue_id" if "venue_id" in window_df.columns else "venue"
    team_mask = (window_df["team_bat_1"] == context["team_name"]) | (window_df["team_bat_2"] == context["team_name"])
    away_df = window_df[team_mask & (~window_df[venue_col].astype(str).str.startswith(prefix))].copy()
    return {"rows": _matrix_rows(away_df, context["team_name"], "AWAY_PERFORMANCE_MATRIX", True, context["min_balls_for_completed_innings"])} if not away_df.empty else {"rows": []}


def calculate_global_performance_payload(match_df: pd.DataFrame, context: GlobalPerformanceContext) -> MatrixRowsPayload:
    window_df = _filter_year_window(match_df, context["reference_date"], context["years_back"])
    if window_df.empty:
        return {"rows": []}
    team_mask = (window_df["team_bat_1"] == context["team_name"]) | (window_df["team_bat_2"] == context["team_name"])
    global_df = window_df[team_mask].copy()
    return {"rows": _matrix_rows(global_df, context["team_name"], "GLOBAL_PERFORMANCE_MATRIX", False, context["min_balls_for_completed_innings"])} if not global_df.empty else {"rows": []}


def calculate_continent_performance_payload(
    match_df: pd.DataFrame,
    context: ContinentPerformanceContext,
) -> MatrixRowsPayload:
    window_df = _filter_year_window(match_df, context["reference_date"], context["years_back"])
    if window_df.empty:
        return {"rows": []}
    opp_scope = _normalize_opp_scope(context["opp_team"])
    mask = (window_df["team_bat_1"] == context["team_name"]) | (window_df["team_bat_2"] == context["team_name"])
    if context["continent"] != "All":
        mask = mask & VenueService._build_continent_mask(window_df, context["continent"])
    if opp_scope != "All":
        mask = mask & ((window_df["team_bat_1"] == opp_scope) | (window_df["team_bat_2"] == opp_scope))
    scoped_df = window_df[mask].copy()
    if scoped_df.empty:
        return {"rows": []}
    return {"rows": _matrix_rows(scoped_df, context["team_name"], "REGIONAL_PERFORMANCE_MATRIX", False, context["min_balls_for_completed_innings"])}
