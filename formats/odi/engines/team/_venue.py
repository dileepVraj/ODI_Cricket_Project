from __future__ import annotations

import pandas as pd
from typing import Optional, cast

from core.calculators.team.venue import (
    calculate_home_fortress_payload,
    calculate_home_fortress_structured_payload,
    calculate_venue_bias_payload,
    calculate_venue_matchup_payload,
    calculate_venue_phases_payload,
)
from core.interfaces.team_types import ComparisonReportRows, RecorderPort, TeamMatchContext
from core.interfaces.venue_types import HomeFortressReport, VenueBiasReport, VenueMatchupReport, VenuePhasesReport
from core.services.serialization_service import SerializationService
from core.services.venue_service import VenueService

from ._base import TeamEngineBase


class TeamVenueAnalyzer(TeamEngineBase):
    def _resolve_stadium_id(self, stadium_name: str) -> str:
        """Resolve a stadium name to its canonical ID via the venue service."""
        return VenueService.resolve_stadium_id(stadium_name)

    def _home_fortress_payload(
        self,
        stadium_name: str,
        home_team: str,
        opp_team: str,
        years_back: int,
        match_context: Optional[TeamMatchContext],
    ) -> dict[str, object]:
        ctx = self._require_match_context(match_context)
        resolved_years = self._resolved_years(years_back)
        stadium_id = self._resolve_stadium_id(stadium_name)
        return calculate_home_fortress_payload(
            self._context_df(ctx, "match_df"),
            {
                "stadium_id": stadium_id,
                "home_team": home_team,
                "opp_team": opp_team,
                "years_back": resolved_years,
                "reference_date": self._context_reference_date(ctx),
                "min_balls_for_completed_innings": self._min_balls_for_completed_innings(),
                "competitive_chase_threshold": self._threshold(ctx, "competitive_chase_threshold"),
            },
        )

    def _venue_phases_payload(
        self,
        stadium_id: str,
        home_team: Optional[str],
        away_team: Optional[str],
        years: int,
        match_context: Optional[TeamMatchContext],
    ) -> dict[str, object]:
        ctx = self._require_match_context(match_context)
        resolved_years = self._resolved_years(years)
        return calculate_venue_phases_payload(
            self._context_df(ctx, "phase_df"),
            {
                "stadium_id": stadium_id,
                "years": resolved_years,
                "reference_date": self._context_reference_date(ctx),
                "match_df": self._context_df(ctx, "match_df"),
                "home_team": home_team,
                "away_team": away_team,
                "min_balls_for_completed_innings": self._min_balls_for_completed_innings(),
                "all_out_wickets": self._sport_constant("all_out_wickets"),
                "balls_per_over": self._sport_constant("balls_per_over"),
                "phases": self._phase_rules(),
                "phase_start_year_default": self._threshold(ctx, "phase_start_year_default"),
            },
        )

    def _venue_bias_payload(
        self,
        stadium_name: str,
        years_back: int,
        match_context: Optional[TeamMatchContext],
    ) -> dict[str, object]:
        ctx = self._require_match_context(match_context)
        resolved_years = self._resolved_years(years_back)
        stadium_id = self._resolve_stadium_id(stadium_name)
        return calculate_venue_bias_payload(
            self._context_df(ctx, "match_df"),
            {
                "stadium_id": stadium_id,
                "years_back": resolved_years,
                "reference_date": self._context_reference_date(ctx),
                "min_balls_for_completed_innings": self._min_balls_for_completed_innings(),
                "percent_scale": self._sport_constant("percent_scale"),
                "bias_win_pct_min": self._threshold(ctx, "bias_win_pct_min"),
                "strong_bias_gap_min": self._threshold(ctx, "strong_bias_gap_min"),
            },
        )

    def analyze_home_fortress(
        self,
        stadium_name: str,
        home_team: str,
        opp_team: str = "All",
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> ComparisonReportRows:
        _ = recorder
        _ = self._require_match_context(match_context)
        _ = self._resolved_years(years_back)
        payload = self._home_fortress_payload(stadium_name, home_team, opp_team, years_back, match_context)
        return cast(ComparisonReportRows, payload.get("rows", []))

    def analyze_home_fortress_structured(
        self,
        stadium_name: str,
        home_team: str,
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> HomeFortressReport:
        ctx = self._require_match_context(match_context)
        resolved_years = self._resolved_years(years_back)
        stadium_id = self._resolve_stadium_id(stadium_name)
        opp_team: str = "All"
        payload = calculate_home_fortress_structured_payload(
            self._context_df(ctx, "match_df"),
            {
                "stadium_id": stadium_id,
                "home_team": home_team,
                "opp_team": opp_team,
                "years_back": resolved_years,
                "reference_date": self._context_reference_date(ctx),
                "min_balls_for_completed_innings": self._min_balls_for_completed_innings(),
                "competitive_chase_threshold": self._threshold(ctx, "competitive_chase_threshold"),
            },
        )
        return cast(HomeFortressReport, payload.get("payload", {}))

    def analyze_venue_matchup_structured(
        self,
        stadium_name: str,
        home_team: str,
        opp_team: str,
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> VenueMatchupReport:
        ctx = self._require_match_context(match_context)
        resolved_years = self._resolved_years(years_back)
        stadium_id = self._resolve_stadium_id(stadium_name)
        payload = calculate_venue_matchup_payload(
            self._context_df(ctx, "match_df"),
            {
                "stadium_id": stadium_id,
                "home_team": home_team,
                "opp_team": opp_team,
                "years_back": resolved_years,
                "reference_date": self._context_reference_date(ctx),
                "min_balls_for_completed_innings": self._min_balls_for_completed_innings(),
                "competitive_chase_threshold": self._threshold(ctx, "competitive_chase_threshold"),
                "low_sample_min_matches": self._threshold(ctx, "low_sample_min_matches"),
                "percent_scale": self._sport_constant("percent_scale"),
            },
        )
        return cast(VenueMatchupReport, payload.get("payload", {}))

    def analyze_venue_phases(
        self,
        stadium_id: str,
        home_team: Optional[str] = None,
        away_team: Optional[str] = None,
        years: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> VenuePhasesReport:
        _ = recorder
        _ = self._require_match_context(match_context)
        _ = self._resolved_years(years)
        payload = self._venue_phases_payload(stadium_id, home_team, away_team, years, match_context)
        return cast(VenuePhasesReport, payload.get("report", {}))

    def analyze_venue_bias(
        self,
        stadium_name: str,
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> Optional[VenueBiasReport]:
        _ = recorder
        _ = self._require_match_context(match_context)
        _ = self._resolved_years(years_back)
        payload = self._venue_bias_payload(stadium_name, years_back, match_context)
        report = payload.get("report")
        if report is not None:
            raw_matches = report.get("raw_matches")
            if isinstance(raw_matches, pd.DataFrame):
                report["raw_matches"] = SerializationService.serialize_raw_matches(raw_matches)
        return cast(Optional[VenueBiasReport], report)
