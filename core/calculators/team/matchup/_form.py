from __future__ import annotations

# mypy: ignore-errors

import pandas as pd

from typing import cast

from core.interfaces.team_types import TeamFormRows
from core.services.report_builder import ReportBuilder
from core.services.venue_service import VenueService

from ._base import (
    TeamFormContext,
    TeamFormRowsPayload,
    _apply_filters,
)

def calculate_team_form_payload(match_df: pd.DataFrame, context: TeamFormContext) -> TeamFormRowsPayload:
    if match_df.empty:
        return {"rows": []}
    mask = (match_df["team_bat_1"] == context["team_name"]) | (match_df["team_bat_2"] == context["team_name"])
    if context["opp_team"] != "All":
        mask = mask & ((match_df["team_bat_1"] == context["opp_team"]) | (match_df["team_bat_2"] == context["opp_team"]))
    if context["continent"] != "All":
        mask = mask & VenueService._build_continent_mask(match_df, context["continent"])
    scoped_df = match_df[mask].copy()
    clean_df = _apply_filters(scoped_df, context["min_balls_for_completed_innings"])
    if clean_df.empty:
        return {"rows": []}
    recent_df = clean_df.sort_values("start_date", ascending=False).head(context["limit"])
    return {"rows": cast(TeamFormRows, ReportBuilder._build_team_form_records(recent_df, context["team_name"]))}
