from __future__ import annotations

from typing import Optional, cast

from core.calculators.team.matchup_calculator import (
    calculate_away_performance_payload,
    calculate_continent_performance_payload,
    calculate_country_h2h_payload,
    calculate_global_h2h_payload,
    calculate_global_h2h_structured_payload,
    calculate_global_performance_payload,
    calculate_home_dominance_payload,
)
from core.interfaces.team_types import ComparisonReportRows, MatrixReportRows, RecorderPort, TeamMatchContext
from core.interfaces.venue_types import VenueMatchupReport
from formats.odi.config.settings import ODI_COUNTRY_PREFIX_MAP

from ._base import TeamEngineBase


class TeamH2HAnalyzer(TeamEngineBase):
    def analyze_global_h2h(
        self,
        home_team: str,
        opp_team: str,
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> ComparisonReportRows:
        ctx = self._require_match_context(match_context)
        resolved_years = self._resolved_years(years_back)
        payload = calculate_global_h2h_payload(
            self._context_df(ctx, "match_df"),
            {
                "home_team": home_team,
                "opp_team": opp_team,
                "years_back": resolved_years,
                "reference_date": self._context_reference_date(ctx),
                "min_balls_for_completed_innings": self._min_balls_for_completed_innings(),
                "competitive_chase_threshold": self._threshold(ctx, "competitive_chase_threshold"),
            },
        )
        return cast(ComparisonReportRows, payload.get("rows", []))

    def analyze_global_h2h_structured(
        self,
        home_team: str,
        opp_team: str,
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> VenueMatchupReport:
        ctx = self._require_match_context(match_context)
        resolved_years = self._resolved_years(years_back)
        payload = calculate_global_h2h_structured_payload(
            self._context_df(ctx, "match_df"),
            {
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

    def analyze_country_h2h(
        self,
        home_team: str,
        opp_team: str,
        country_name: Optional[str] = None,
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> VenueMatchupReport:
        _ = recorder
        ctx = self._require_match_context(match_context)
        resolved_years = self._resolved_years(years_back)
        payload = calculate_country_h2h_payload(
            self._context_df(ctx, "match_df"),
            {
                "home_team": home_team,
                "opp_team": opp_team,
                "country_name": country_name,
                "years_back": resolved_years,
                "reference_date": self._context_reference_date(ctx),
                "min_balls_for_completed_innings": self._min_balls_for_completed_innings(),
                "competitive_chase_threshold": self._threshold(ctx, "competitive_chase_threshold"),
            },
        )
        return cast(VenueMatchupReport, payload.get("payload", {}))

    def analyze_home_dominance(
        self,
        home_team: str,
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> MatrixReportRows:
        _ = recorder
        ctx = self._require_match_context(match_context)
        resolved_years = self._resolved_years(years_back)
        payload = calculate_home_dominance_payload(
            self._context_df(ctx, "match_df"),
            {
                "home_team": home_team,
                "years_back": resolved_years,
                "reference_date": self._context_reference_date(ctx),
                "min_balls_for_completed_innings": self._min_balls_for_completed_innings(),
                "region": ODI_COUNTRY_PREFIX_MAP,
            },
        )
        return cast(MatrixReportRows, payload.get("rows", []))

    def analyze_away_performance(
        self,
        team_name: str,
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> MatrixReportRows:
        _ = recorder
        ctx = self._require_match_context(match_context)
        resolved_years = self._resolved_years(years_back)
        payload = calculate_away_performance_payload(
            self._context_df(ctx, "match_df"),
            {
                "team_name": team_name,
                "years_back": resolved_years,
                "reference_date": self._context_reference_date(ctx),
                "min_balls_for_completed_innings": self._min_balls_for_completed_innings(),
                "region": ODI_COUNTRY_PREFIX_MAP,
            },
        )
        return cast(MatrixReportRows, payload.get("rows", []))

    def analyze_global_performance(
        self,
        team_name: str,
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> MatrixReportRows:
        ctx = self._require_match_context(match_context)
        resolved_years = self._resolved_years(years_back)
        payload = calculate_global_performance_payload(
            self._context_df(ctx, "match_df"),
            {
                "team_name": team_name,
                "years_back": resolved_years,
                "reference_date": self._context_reference_date(ctx),
                "min_balls_for_completed_innings": self._min_balls_for_completed_innings(),
            },
        )
        return cast(MatrixReportRows, payload.get("rows", []))

    def analyze_continent_performance(
        self,
        team_name: str,
        continent: str,
        opp_team: str = "All",
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> MatrixReportRows | ComparisonReportRows:
        ctx = self._require_match_context(match_context)
        resolved_years = self._resolved_years(years_back)
        payload = calculate_continent_performance_payload(
            self._context_df(ctx, "match_df"),
            {
                "team_name": team_name,
                "continent": continent,
                "opp_team": opp_team,
                "years_back": resolved_years,
                "reference_date": self._context_reference_date(ctx),
                "min_balls_for_completed_innings": self._min_balls_for_completed_innings(),
                "competitive_chase_threshold": self._threshold(ctx, "competitive_chase_threshold"),
            },
        )
        return cast(MatrixReportRows | ComparisonReportRows, payload.get("rows", []))
