from __future__ import annotations

from typing import Optional, cast

from core.calculators.team.matchup_calculator import calculate_team_form_payload
from core.interfaces.team_types import RecorderPort, TeamFormRows, TeamMatchContext

from ._base import TeamEngineBase


class TeamFormAnalyzer(TeamEngineBase):
    def analyze_team_form(
        self,
        team_name: str,
        opp_team: str = "All",
        continent: str = "All",
        limit: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> TeamFormRows:
        _ = recorder
        ctx = self._require_match_context(match_context)
        resolved_limit = self._resolved_team_form_limit(ctx, limit)
        payload = calculate_team_form_payload(
            self._context_df(ctx, "match_df"),
            {
                "team_name": team_name,
                "opp_team": opp_team,
                "continent": continent,
                "limit": resolved_limit,
                "min_balls_for_completed_innings": self._min_balls_for_completed_innings(),
            },
        )
        return cast(TeamFormRows, payload.get("rows", []))
