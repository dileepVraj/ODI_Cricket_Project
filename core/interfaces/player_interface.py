from typing import Dict, List, Optional, Protocol, Union, Any
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

class IPlayerEngine(Protocol):
    """
    The Strict Contract for Player Analytics.
    RULES:
    1. STRICT RETURN TYPES: No 'dict' chaos. Use Dataclasses.
    2. NO HTML: Logic only.
    """

    def get_player_profile(self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None) -> PlayerProfile:
        """
        Fetches the complete 360-degree profile of a player.
        """
        ...

    def get_matchups(self, batter: str, bowlers: List[str]) -> List[MatchupStats]:
        """
        Returns Head-to-Head stats for a batter against a specific list of bowlers.
        """
        ...

    def get_squad_metrics(self, players: List[str], years: int = 5) -> Dict[str, Any]:
        """
        Aggregated stats for a list of players (Total Runs, Wickets, Caps).
        """
        ...
