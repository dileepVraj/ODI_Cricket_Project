from __future__ import annotations

from typing import Optional

from core.interfaces.team_types import (
    ComparisonReportRows,
    MatrixReportRows,
    RecorderPort,
    TeamFormRows,
    TeamMatchContext,
)
from core.interfaces.venue_types import (
    HomeFortressReport,
    VenueBiasReport,
    VenueMatchupReport,
    VenuePhasesReport,
)
import formats.odi.engines.team as _team_module

_TeamEngine = _team_module.TeamEngine


class TeamEngine(_TeamEngine):
    def analyze_home_fortress_structured(
        self,
        stadium_name: str,
        home_team: str,
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> HomeFortressReport:
        return super().analyze_home_fortress_structured(
            stadium_name, home_team, years_back=years_back, match_context=match_context
        )

    def analyze_venue_matchup_structured(
        self,
        stadium_name: str,
        home_team: str,
        opp_team: str,
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> VenueMatchupReport:
        return super().analyze_venue_matchup_structured(
            stadium_name, home_team, opp_team, years_back=years_back, match_context=match_context
        )

    def analyze_venue_phases(
        self,
        stadium_id: str,
        home_team: Optional[str] = None,
        away_team: Optional[str] = None,
        years: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> VenuePhasesReport:
        return super().analyze_venue_phases(
            stadium_id,
            home_team=home_team,
            away_team=away_team,
            years=years,
            recorder=recorder,
            match_context=match_context,
        )

    def analyze_venue_bias(
        self,
        stadium_name: str,
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> Optional[VenueBiasReport]:
        return super().analyze_venue_bias(
            stadium_name,
            years_back=years_back,
            recorder=recorder,
            match_context=match_context,
        )

    def analyze_global_h2h_structured(
        self,
        home_team: str,
        opp_team: str,
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> VenueMatchupReport:
        return super().analyze_global_h2h_structured(
            home_team, opp_team, years_back=years_back, match_context=match_context
        )

    def analyze_country_h2h(
        self,
        home_team: str,
        opp_team: str,
        country_name: Optional[str] = None,
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> VenueMatchupReport:
        return super().analyze_country_h2h(
            home_team,
            opp_team,
            country_name=country_name,
            years_back=years_back,
            recorder=recorder,
            match_context=match_context,
        )

    def analyze_home_dominance(
        self,
        home_team: str,
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> MatrixReportRows:
        return super().analyze_home_dominance(
            home_team,
            years_back=years_back,
            recorder=recorder,
            match_context=match_context,
        )

    def analyze_away_performance(
        self,
        team_name: str,
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> MatrixReportRows:
        return super().analyze_away_performance(
            team_name,
            years_back=years_back,
            recorder=recorder,
            match_context=match_context,
        )

    def analyze_global_performance(
        self,
        team_name: str,
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> MatrixReportRows:
        return super().analyze_global_performance(
            team_name, years_back=years_back, match_context=match_context
        )

    def analyze_continent_performance(
        self,
        team_name: str,
        continent: str,
        opp_team: str = "All",
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> MatrixReportRows | ComparisonReportRows:
        return super().analyze_continent_performance(
            team_name,
            continent,
            opp_team=opp_team,
            years_back=years_back,
            match_context=match_context,
        )

    def analyze_team_form(
        self,
        team_name: str,
        opp_team: str = "All",
        continent: str = "All",
        limit: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> TeamFormRows:
        return super().analyze_team_form(
            team_name,
            opp_team=opp_team,
            continent=continent,
            limit=limit,
            recorder=recorder,
            match_context=match_context,
        )


__all__ = ["TeamEngine"]
