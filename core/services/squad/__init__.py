from typing import Dict, List, Optional, Union

import pandas as pd

from core.interfaces.team_types import SquadBulkMetricsResult
from core.services.squad._base import SquadServiceBase  # noqa: F401
from core.services.squad._player_stats import PlayerStatsBuilder  # noqa: F401
from core.services.squad._squad_metrics import SquadMetricsCalculator  # noqa: F401


class SquadService(SquadMetricsCalculator, PlayerStatsBuilder):
    def get_bulk_metrics(
        self,
        base_df: pd.DataFrame,
        player_ids: List[str],
        opposition: str,
        venue_pattern: str,
        player_roles: Optional[Dict[str, str]] = None,
        squad_batting_metrics: Optional[Dict[str, Dict[str, Union[int, float]]]] = None,
    ) -> SquadBulkMetricsResult:
        """
        Compute squad metrics and player stats for a full XI in a single vectorized pass.
        """
        players = self._normalize_players(player_ids)
        normalized_df = self._normalize_base_df(base_df)
        form_window_matches = self._get_tactical_threshold("form_window_matches", 1)

        squad_metrics = self._calculate_squad_metrics(
            normalized_df,
            players,
            squad_batting_metrics=squad_batting_metrics,
        )
        player_stats = self._build_bulk_player_stats(
            normalized_df,
            players,
            opposition=opposition,
            venue_pattern=venue_pattern,
            player_roles=player_roles,
            squad_batting_metrics=squad_batting_metrics,
            form_window_matches=form_window_matches,
        )
        return {
            "squad_metrics": squad_metrics,
            "player_stats": player_stats,
        }


__all__ = ["SquadService", "SquadMetricsCalculator", "PlayerStatsBuilder", "SquadServiceBase"]
