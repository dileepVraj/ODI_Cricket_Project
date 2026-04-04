"""formats/odi/engines/player_engine — backward-compat shim. Import from player/ directly."""
from typing import List, Optional, Union

import pandas as pd

from core.interfaces.player_interface import PlayerProfile, SquadComparisonData
from core.interfaces.player_types import TacticalRecorderPort
from .player import PlayerEngine as _PlayerEngine


class PlayerEngine(_PlayerEngine):
    def analyze_player_profile(self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, active_bowlers: Optional[List[str]] = None, years: Optional[int] = None, raw_balls_df: Optional[pd.DataFrame] = None, country: Optional[str] = None, ground: Optional[str] = None) -> Optional[PlayerProfile]:
        return super().analyze_player_profile(player_name, opposition=opposition, venue_id=venue_id, active_bowlers=active_bowlers, years=years, raw_balls_df=raw_balls_df, country=country, ground=ground)

    def compare_squads(self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None, recorder: Optional[TacticalRecorderPort] = None, *, context_df: pd.DataFrame) -> SquadComparisonData:
        return super().compare_squads(team_a_name, team_a_players, team_b_name, team_b_players, venue_id, years=years, recorder=recorder, context_df=context_df)

    def analyze_dual_squad_matrix(self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], years: Optional[int] = None, *, context_df: pd.DataFrame) -> List[dict[str, Union[str, int, float, bool, list[Optional[str]], None]]]:
        return super().analyze_dual_squad_matrix(team_a_name, team_a_players, team_b_name, team_b_players, years=years, context_df=context_df)

    def get_matchups(self, batter: Optional[str] = None, bowlers: Optional[List[str]] = None, *, home_team: Optional[str] = None, opp_team: Optional[str] = None, home_xi: Optional[List[str]] = None, away_xi: Optional[List[str]] = None, context_df: pd.DataFrame, venue_filtered: bool = False) -> List[dict[str, Union[str, int, float, bool, list[Optional[str]], None]]]:
        return super().get_matchups(batter=batter, bowlers=bowlers, home_team=home_team, opp_team=opp_team, home_xi=home_xi, away_xi=away_xi, context_df=context_df, venue_filtered=venue_filtered)

__all__ = ["PlayerEngine"]
