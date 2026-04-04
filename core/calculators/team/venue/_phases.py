"""Venue phase calculator domain."""

from __future__ import annotations

from typing import cast

import pandas as pd

from core.calculators.phase_engine import (
    build_phase_scenario_rows,
    calculate_phase_breakdown,
    calculate_team_phase_habits,
    summarize_phase_by_innings,
)
from core.calculators.team.venue._base import (
    VenuePhasesContext,
    VenuePhasesPayload,
    VenuePhasesReport,
    _empty_like,
)
from core.interfaces.venue_types import TeamVenuePhaseSnapshot, VenueGlobalHabits
from core.services.report_formatter import ReportFormatter
from core.services.venue_service import VenueService


def _coerce_match_meta(match_df: pd.DataFrame) -> pd.DataFrame:
    required = ["match_id", "balls_inn1", "wickets_inn1", "balls_inn2", "wickets_inn2", "winner", "team_bat_2"]
    if match_df.empty or not all(col in match_df.columns for col in required):
        return _empty_like(match_df)
    meta_df = match_df.copy()
    meta_df["match_id"] = meta_df["match_id"].astype(str).str.split(".").str[0].str.strip()
    meta_df = meta_df.drop_duplicates(subset=["match_id"])
    for col in ["balls_inn1", "balls_inn2", "wickets_inn1", "wickets_inn2"]:
        meta_df[col] = pd.to_numeric(meta_df[col], errors="coerce")
    return meta_df


def _valid_phase_match_ids(meta_df: pd.DataFrame, min_balls: int, all_out_wickets: int) -> tuple[set[str], set[str]]:
    if meta_df.empty:
        return set(), set()
    winner_norm = meta_df["winner"].astype(str).str.lower().str.strip()
    team2_norm = meta_df["team_bat_2"].astype(str).str.lower().str.strip()
    is_no_result = winner_norm.isin(["nan", "none", "no result", "abandoned", ""])
    is_chase_win = (~is_no_result) & (winner_norm == team2_norm)
    valid_1 = (meta_df["balls_inn1"] >= min_balls) | (meta_df["wickets_inn1"] >= all_out_wickets)
    valid_2 = (meta_df["balls_inn2"] >= min_balls) | (meta_df["wickets_inn2"] >= all_out_wickets) | is_chase_win
    short_1 = (meta_df["balls_inn1"] < min_balls) & (meta_df["wickets_inn1"] < all_out_wickets)
    short_2 = (meta_df["balls_inn2"] < min_balls) & (meta_df["wickets_inn2"] < all_out_wickets) & (~is_chase_win)
    eligible = (~(is_no_result & (short_1 | short_2))) & valid_1
    ids_1 = set(meta_df.loc[eligible & valid_1, "match_id"].astype(str))
    ids_2 = set(meta_df.loc[eligible & valid_2, "match_id"].astype(str))
    return ids_1, ids_2


def _filter_phase_rows(phase_df: pd.DataFrame, ids_1: set[str], ids_2: set[str]) -> pd.DataFrame:
    valid_ids = ids_1 | ids_2
    filtered_df = phase_df[phase_df["match_id"].isin(valid_ids)].copy()
    if "innings" not in filtered_df.columns:
        return filtered_df
    inn1 = (filtered_df["innings"] == 1) & filtered_df["match_id"].isin(ids_1)
    inn2 = (filtered_df["innings"] == 2) & filtered_df["match_id"].isin(ids_2)
    return filtered_df[inn1 | inn2].copy()


def _ensure_phase_dates(phase_df: pd.DataFrame, match_df: pd.DataFrame) -> pd.DataFrame:
    if phase_df.empty or "start_date" in phase_df.columns or "match_id" not in phase_df.columns:
        return phase_df.copy()
    if match_df.empty or "match_id" not in match_df.columns or "start_date" not in match_df.columns:
        return phase_df.copy()
    date_lookup_df = match_df.copy()
    date_lookup_df["match_id"] = date_lookup_df["match_id"].astype(str).str.split(".").str[0].str.strip()
    date_map = date_lookup_df.set_index("match_id")["start_date"].to_dict()
    merged_df = phase_df.copy()
    merged_df["start_date"] = merged_df["match_id"].map(date_map)
    return merged_df


def _phase_report_base(
    venue_stats: pd.DataFrame,
    stadium_id: str,
    years: int,
    min_balls: int,
    balls_per_over: int,
) -> VenuePhasesReport:
    match_count = int(venue_stats["match_id"].nunique()) if "match_id" in venue_stats.columns else int(len(venue_stats))
    return {
        "stadium_id": stadium_id, "match_count": match_count, "years": years,
        "filter_criteria": {
            "min_first_innings_balls": min_balls, "min_first_innings_overs": round(min_balls / balls_per_over, 1),
            "keep_all_outs": True, "keep_successful_chases": True, "drop_short_no_result_only": True,
        },
        "baseline": summarize_phase_by_innings(venue_stats), "home_at_venue": None, "away_at_venue": None, "global_habits": None,
        "MATCH_IDS": ",".join(venue_stats["match_id"].astype(str).unique().tolist()) if "match_id" in venue_stats.columns else None,
    }


def _attach_phase_team_snapshots(
    report: VenuePhasesReport,
    venue_stats: pd.DataFrame,
    home_team: str | None,
    away_team: str | None,
) -> None:
    if home_team and home_team != "All" and "team" in venue_stats.columns:
        home_df = venue_stats[venue_stats["team"] == home_team]
        if not home_df.empty:
            report["home_at_venue"] = cast(TeamVenuePhaseSnapshot, {"team": home_team, "stats": summarize_phase_by_innings(home_df)})
    if away_team and away_team != "All" and "team" in venue_stats.columns:
        away_df = venue_stats[venue_stats["team"] == away_team]
        if not away_df.empty:
            report["away_at_venue"] = cast(TeamVenuePhaseSnapshot, {"team": away_team, "stats": summarize_phase_by_innings(away_df)})


def _global_habits(phase_df: pd.DataFrame, home_team: str | None, away_team: str | None, cutoff: pd.Timestamp | None, start_year: int | str, phase_overs: dict[str, float]) -> VenueGlobalHabits | None:
    if not home_team or not away_team or away_team == "All" or "team" not in phase_df.columns:
        return None
    phase_window = phase_df[phase_df["start_date"] >= cutoff].copy() if cutoff is not None and "start_date" in phase_df.columns else phase_df.copy()
    home_df = phase_window[phase_window["team"] == home_team]
    away_df = phase_window[phase_window["team"] == away_team]
    if home_df.empty or away_df.empty:
        return None
    home_habits = calculate_team_phase_habits(home_df, phase_overs)
    away_habits = calculate_team_phase_habits(away_df, phase_overs)
    return cast(VenueGlobalHabits, {
        "start_year": start_year, "bat_first": {
            "home_team_pp_runs": home_habits["bat_first"]["pp_runs"], "away_team_pp_runs": away_habits["bat_first"]["pp_runs"],
            "home_team_pp_wkts": home_habits["bat_first"]["pp_wkts"], "away_team_pp_wkts": away_habits["bat_first"]["pp_wkts"],
            "home_team_mid_runs": home_habits["bat_first"]["mid_runs"], "away_team_mid_runs": away_habits["bat_first"]["mid_runs"],
            "home_team_mid_wkts": home_habits["bat_first"]["mid_wkts"], "away_team_mid_wkts": away_habits["bat_first"]["mid_wkts"],
            "home_team_dth_runs": home_habits["bat_first"]["dth_runs"], "away_team_dth_runs": away_habits["bat_first"]["dth_runs"],
            "home_team_dth_wkts": home_habits["bat_first"]["dth_wkts"], "away_team_dth_wkts": away_habits["bat_first"]["dth_wkts"]},
        "chasing": {
            "home_team_pp_runs": home_habits["chasing"]["pp_runs"], "away_team_pp_runs": away_habits["chasing"]["pp_runs"],
            "home_team_mid_wkts": home_habits["chasing"]["mid_wkts"], "away_team_mid_wkts": away_habits["chasing"]["mid_wkts"],
            "home_team_dth_wkts": home_habits["chasing"]["dth_wkts"], "away_team_dth_wkts": away_habits["chasing"]["dth_wkts"]},
        "home": home_habits["rr"], "away": away_habits["rr"], "scenario_rows": ReportFormatter.format_scenario_rows(build_phase_scenario_rows(home_habits, away_habits))
    })


def calculate_venue_phases_payload(phase_df: pd.DataFrame, context: VenuePhasesContext) -> VenuePhasesPayload:
    if phase_df.empty:
        return {"report": {}}
    phase_payload = calculate_phase_breakdown(phase_df, context["phases"])
    scoped_phase_df = phase_payload.get("phase_df", pd.DataFrame())
    phase_overs = cast(dict[str, float], phase_payload.get("phase_overs", {"pp": 0.0, "mid": 0.0, "dth": 0.0}))
    if scoped_phase_df.empty:
        return {"report": {}}
    meta_df = _coerce_match_meta(context["match_df"])
    ids_1, ids_2 = _valid_phase_match_ids(meta_df, context["min_balls_for_completed_innings"], context["all_out_wickets"])
    phase_window = _filter_phase_rows(scoped_phase_df, ids_1, ids_2) if ids_1 or ids_2 else scoped_phase_df.copy()
    phase_window = _ensure_phase_dates(phase_window, context["match_df"])
    venue_stats = phase_window[VenueService._build_venue_mask(phase_window, context["stadium_id"])].copy()
    report, cutoff, start_year = _phase_report_with_window(venue_stats, context)
    if not report:
        return {"report": {}}
    _attach_phase_team_snapshots(report, venue_stats, context["home_team"], context["away_team"])
    report["global_habits"] = _global_habits(phase_window, context["home_team"], context["away_team"], cutoff, start_year, phase_overs)
    return {"report": report}


def _phase_report_with_window(
    venue_stats: pd.DataFrame,
    context: VenuePhasesContext,
) -> tuple[VenuePhasesReport, pd.Timestamp | None, int | str]:
    if venue_stats.empty:
        return {}, None, context["phase_start_year_default"]
    if "start_date" not in venue_stats.columns:
        report = _phase_report_base(venue_stats, context["stadium_id"], context["years"], context["min_balls_for_completed_innings"], context["balls_per_over"])
        return report, None, context["phase_start_year_default"]
    cutoff = context["reference_date"] - pd.DateOffset(years=context["years"])
    scoped_stats = venue_stats[venue_stats["start_date"] >= cutoff].copy()
    if scoped_stats.empty:
        return {}, cutoff, cutoff.year
    report = _phase_report_base(scoped_stats, context["stadium_id"], context["years"], context["min_balls_for_completed_innings"], context["balls_per_over"])
    return report, cutoff, cutoff.year
