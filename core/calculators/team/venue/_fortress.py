"""Home fortress venue calculator domain."""

from __future__ import annotations

from typing import cast

import pandas as pd

from config.shared.team_colors import TEAM_COLORS
from core.calculators.team.venue._base import (
    ComparisonRowsPayload,
    HomeFortressContext,
    HomeFortressReport,
    HomeFortressStructuredPayload,
    _apply_filters,
    _comparison_rows,
    _summary_payload,
    _team_intel,
    _venue_avg_payload,
    _venue_window,
)
from core.services.match_filter_service import MatchFilterService


def calculate_home_fortress_payload(match_df: pd.DataFrame, context: HomeFortressContext) -> ComparisonRowsPayload:
    venue_df, _ = _venue_window(match_df, context["stadium_id"], context["years_back"], context["reference_date"])
    if venue_df.empty:
        return {"rows": []}
    rivalry_df = venue_df[(venue_df["team_bat_1"] == context["home_team"]) | (venue_df["team_bat_2"] == context["home_team"])].copy()
    if context["opp_team"] != "All":
        rivalry_df = rivalry_df[(rivalry_df["team_bat_1"] == context["opp_team"]) | (rivalry_df["team_bat_2"] == context["opp_team"])].copy()
    clean_df = _apply_filters(rivalry_df, context["min_balls_for_completed_innings"])
    if clean_df.empty:
        return {"rows": []}
    visitor_label = context["opp_team"] if context["opp_team"] != "All" else "VISITOR_TEAM"
    return {"rows": _comparison_rows(clean_df, context["home_team"], visitor_label, "FORTRESS_REPORT", context["competitive_chase_threshold"], True)}


def _home_fortress_summary_payload(
    summary_df: pd.DataFrame,
    home_team: str,
    percent_scale: int,
) -> dict[str, int]:
    matchup_summary = _summary_payload(summary_df, home_team, percent_scale)
    return {
        "matches": matchup_summary["matches"],
        "home_win_pct": matchup_summary["win_pct"],
        "tie_nr": matchup_summary["tie_nr"],
    }


def _home_fortress_team_colors(clean_df: pd.DataFrame) -> dict[str, str]:
    team_columns = [
        column_name
        for column_name in ("team_bat_1", "team_bat_2")
        if column_name in clean_df.columns
    ]
    if not team_columns:
        return {}
    team_names = pd.concat(
        [
            clean_df[column_name].dropna().astype(str).str.strip()
            for column_name in team_columns
        ],
        ignore_index=True,
    )
    if team_names.empty:
        return {}
    unique_team_names = set(team_names[team_names != ""].unique().tolist())
    return {
        team_name: color
        for team_name in unique_team_names
        if (color := TEAM_COLORS.get(team_name))
    }


def calculate_home_fortress_structured_payload(
    match_df: pd.DataFrame,
    context: HomeFortressContext,
) -> HomeFortressStructuredPayload:
    venue_df, _ = _venue_window(
        match_df,
        context["stadium_id"],
        context["years_back"],
        context["reference_date"],
    )
    if venue_df.empty:
        return cast(HomeFortressStructuredPayload, {"payload": {}})
    rivalry_df = venue_df[
        (venue_df["team_bat_1"] == context["home_team"])
        | (venue_df["team_bat_2"] == context["home_team"])
    ].copy()
    if context["opp_team"] != "All":
        rivalry_df = rivalry_df[
            (rivalry_df["team_bat_1"] == context["opp_team"])
            | (rivalry_df["team_bat_2"] == context["opp_team"])
        ].copy()
    clean_df = _apply_filters(rivalry_df, context["min_balls_for_completed_innings"])
    if clean_df.empty:
        return cast(HomeFortressStructuredPayload, {"payload": {}})
    summary_df = clean_df[
        ~MatchFilterService.get_excluded_no_result_mask(clean_df)
    ].copy()
    if summary_df.empty:
        return cast(HomeFortressStructuredPayload, {"payload": {}})
    low_sample_min_matches = cast(int, context.get("low_sample_min_matches", 0))
    percent_scale = cast(int, context.get("percent_scale", 0))
    home_stats = _team_intel(
        summary_df,
        context["home_team"],
        context["competitive_chase_threshold"],
        low_sample_min_matches,
    )
    if context["opp_team"] == "All":
        visitor_display_name = "Visitors".upper()
        visitor_df = summary_df.copy()
        visitor_df["home_team_ref"] = context["home_team"]
        visitor_stats = _team_intel(
            visitor_df,
            "Visitors",
            context["competitive_chase_threshold"],
            low_sample_min_matches,
        )
        visitor_wins_df = summary_df[summary_df["winner"] != context["home_team"]]
        valid_winners = visitor_wins_df[
            ~visitor_wins_df["winner"].str.lower().isin(
                ["tie", "no result", "nan", "none", ""]
            )
        ]
        visitor_stats["wins"] = len(valid_winners)
        visitor_stats["defended"] = int(
            (valid_winners["team_bat_1"] != context["home_team"]).sum()
        )
        visitor_stats["chased"] = int(
            (valid_winners["team_bat_2"] != context["home_team"]).sum()
        )
    else:
        visitor_display_name = context["opp_team"]
        visitor_stats = _team_intel(
            summary_df,
            visitor_display_name,
            context["competitive_chase_threshold"],
            low_sample_min_matches,
        )
    low_sample_warnings = [
        *home_stats["low_sample_warnings"],
        *visitor_stats["low_sample_warnings"],
    ]
    report_values = [
        _home_fortress_summary_payload(
            summary_df,
            context["home_team"],
            percent_scale,
        ),
        {"name": context["home_team"], "stats": home_stats},
        {"name": visitor_display_name, "stats": visitor_stats},
        _venue_avg_payload(
            summary_df,
            context["competitive_chase_threshold"],
        ),
        _home_fortress_team_colors(clean_df),
        ",".join(clean_df["match_id"].astype(str).unique().tolist()) or None,
        low_sample_warnings,
    ]
    report = cast(
        HomeFortressReport,
        dict(zip(HomeFortressReport.__annotations__, report_values)),
    )
    return {"payload": report}
