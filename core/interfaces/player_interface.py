from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import pandas as pd

@dataclass
class BattingStats:
    innings: int
    runs: int
    average: float
    strike_rate: float
    centuries: int
    fifties: int
    highest_score: int
    form_last_10: List[str]  # ["12", "55*", "0", "DNB"]

@dataclass
class BowlingStats:
    innings: int
    wickets: int
    average: float
    economy: float
    best_figures: str  # "5/24"
    form_last_10: List[str]  # ["2/30", "0/45", "-"]

@dataclass
class ContextStats:
    batting: BattingStats
    bowling: Optional[BowlingStats]

@dataclass
class PlayerProfile:
    name: str
    role: str
    batting: BattingStats
    bowling: Optional[BowlingStats]
    venue_stats: Optional[ContextStats]
    vs_opponent_stats: Optional[ContextStats]

@dataclass
class MatchupStats:
    batter: str
    bowler: str
    balls: int
    runs: int
    outs: int
    avg: float
    sr: float
    is_bunny: bool  # True if Outs >= 3

@dataclass
class SquadMetrics:
    caps: int
    runs: int
    wickets: int
    centuries: int
    fifties: int
    five_wkt_hauls: int
    avg_caps: int

@dataclass
class TacticalMatrixRow:
    player: str
    role: str
    stats_per_style: Dict[str, Dict[str, Any]] # {Style: {avg, sr, raw_avg}}

@dataclass
class SquadComparisonData:
    team_a_name: str
    team_b_name: str
    metrics_a: SquadMetrics
    metrics_b: SquadMetrics
    player_stats_a: List[Dict[str, Any]]
    player_stats_b: List[Dict[str, Any]]
    tactical_matrix_a: List[Dict[str, Any]]
    tactical_matrix_b: List[Dict[str, Any]]
    matchups_a: Dict[str, List[Dict[str, Any]]]
    matchups_b: Dict[str, List[Dict[str, Any]]]
    venue_id: str
    years: int

class IPlayerEngine(ABC):
    """
    The Strict Contract for Player Analytics.
    RULES:
    1. STRICT RETURN TYPES: No 'dict' chaos. Use Dataclasses.
    2. NO HTML: Logic only.
    """

    @abstractmethod
    def get_active_squad(self, team_name: str) -> List[str]:
        """Returns active squad members for a team."""
        raise NotImplementedError

    @abstractmethod
    def get_last_match_xi(self, team_name: str) -> List[str]:
        """Returns the XI from the most recent match."""
        raise NotImplementedError

    @abstractmethod
    def get_squad_comparison_data(
        self,
        team_a_name: str,
        team_a_players: List[str],
        team_b_name: str,
        team_b_players: List[str],
        venue_id: str,
        years: Optional[int] = None,
    ) -> SquadComparisonData:
        """Builds structured squad-comparison payload."""
        raise NotImplementedError

    @abstractmethod
    def compare_squads(
        self,
        team_a_name: str,
        team_a_players: List[str],
        team_b_name: str,
        team_b_players: List[str],
        venue_id: str,
        years: Optional[int] = None,
        recorder: Any = None,
    ) -> SquadComparisonData:
        """Compares two squads in a match context."""
        raise NotImplementedError

    @abstractmethod
    def analyze_squad_types(
        self,
        team_name: str,
        players: List[str],
        opposition_bowlers: List[str],
        years: Optional[int] = None,
        recorder: Any = None,
        context_df: Optional[pd.DataFrame] = None,
    ) -> List[Dict[str, Any]]:
        """Analyzes batting archetypes against bowler styles."""
        raise NotImplementedError

    @abstractmethod
    def get_player_profile(
        self,
        player_name: str,
        opposition: Optional[str] = None,
        venue_id: Optional[str] = None,
        years: int = 10,
    ) -> Optional[PlayerProfile]:
        """
        Fetches the complete 360-degree profile of a player.
        """
        raise NotImplementedError

    @abstractmethod
    def get_matchups(
        self,
        batter: str,
        bowlers: List[str],
        context_df: Optional[pd.DataFrame] = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns Head-to-Head stats for a batter against a specific list of bowlers.
        """
        raise NotImplementedError

    @abstractmethod
    def analyze_player_profile(
        self,
        player_name: str,
        opposition: Optional[str] = None,
        venue_id: Optional[str] = None,
        active_bowlers: Optional[List[str]] = None,
        years: int = 10,
    ) -> Optional[PlayerProfile]:
        """
        Context-aware player profile retrieval.
        """
        raise NotImplementedError
