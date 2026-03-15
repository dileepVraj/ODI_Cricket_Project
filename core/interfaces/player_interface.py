from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import pandas as pd
from core.interfaces.team_types import TacticalRecorderPort, DisplayRecord

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
    last_10_runs: List[Optional[int]] = field(default_factory=list)

@dataclass
class BowlingStats:
    innings: int
    wickets: int
    average: float
    economy: float
    best_figures: Optional[str]  # "5/24"
    form_last_10: List[str]  # ["2/30", "0/45", "-"]


@dataclass
class PhaseRunsRow:
    phase: str
    total_runs: int
    balls_faced: int
    dismissals: int
    avg_runs: float
    strike_rate: float


@dataclass
class VsBowlingStyleRow:
    style: str
    total_runs: int
    balls_faced: int
    dismissals: int
    avg_runs: float
    strike_rate: float


@dataclass
class PhaseBowlingRow:
    phase: str
    wickets: int
    economy: float
    average: float
    strike_rate: float
    dot_pct: float
    boundary_pct: float


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
    venue_stats: Optional[ContextStats] = None
    vs_opponent_stats: Optional[ContextStats] = None
    phase_runs: List[PhaseRunsRow] = field(default_factory=list)
    vs_bowling_style: List[VsBowlingStyleRow] = field(default_factory=list)
    phase_bowling: List[PhaseBowlingRow] = field(default_factory=list)
    last_10_bowling: List[Optional[int]] = field(default_factory=list)

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
class SquadComparisonData:
    team_a_name: str
    team_b_name: str
    metrics_a: SquadMetrics
    metrics_b: SquadMetrics
    player_stats_a: List[DisplayRecord]
    player_stats_b: List[DisplayRecord]
    tactical_matrix_a: List[DisplayRecord]
    tactical_matrix_b: List[DisplayRecord]
    matchups_a: Dict[str, List[DisplayRecord]]
    matchups_b: Dict[str, List[DisplayRecord]]
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
    def get_last_match_xi(
        self,
        team_name: str,
        team_matches: Optional[pd.DataFrame] = None,
        match_balls_df: Optional[pd.DataFrame] = None,
    ) -> List[str]:
        """
        Returns the XI from the most recent match.

        Dual-path contract (ARCH-DEC-01):
        - Primary path: uses self.squads_df if populated (constructor data)
        - Fallback path: uses team_matches + match_balls_df if provided (injection enrichment)
        Returns [] if neither source yields results.
        """
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
        *,
        context_df: pd.DataFrame,
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
        recorder: Optional[TacticalRecorderPort] = None,
        *,
        context_df: pd.DataFrame,
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
        recorder: Optional[TacticalRecorderPort] = None,
        *,
        context_df: pd.DataFrame,
    ) -> List[DisplayRecord]:
        """Analyzes batting archetypes against bowler styles."""
        raise NotImplementedError

    @abstractmethod
    def get_player_profile(
        self,
        player_name: str,
        opposition: Optional[str] = None,
        venue_id: Optional[str] = None,
        years: Optional[int] = None,
        raw_balls_df: Optional[pd.DataFrame] = None,
    ) -> Optional[PlayerProfile]:
        """
        Fetches the complete 360-degree profile of a player.

        Dual-path contract (ARCH-DEC-01):
        - Primary path: uses self.player_df (constructor data) for career stats
        - Enrichment path: uses raw_balls_df if provided for milestone calculation
        Returns None if player_name is not found.
        """
        raise NotImplementedError

    @abstractmethod
    def get_matchups(
        self,
        batter: str,
        bowlers: Optional[List[str]] = None,
        *,
        home_team: Optional[str] = None,
        opp_team: Optional[str] = None,
        home_xi: Optional[List[str]] = None,
        away_xi: Optional[List[str]] = None,
        context_df: pd.DataFrame,
    ) -> List[DisplayRecord]:
        """
        Returns Head-to-Head stats for a batter against a specific list of bowlers.
        Bowlers may be inferred from home_xi/away_xi if not provided directly.
        context_df is required (ARCH-DEC-02).
        """
        raise NotImplementedError

    @abstractmethod
    def analyze_player_profile(
        self,
        player_name: str,
        opposition: Optional[str] = None,
        venue_id: Optional[str] = None,
        active_bowlers: Optional[List[str]] = None,
        years: Optional[int] = None,
        raw_balls_df: Optional[pd.DataFrame] = None,
        country: Optional[str] = None,
        ground: Optional[str] = None,
    ) -> Optional[PlayerProfile]:
        """
        Context-aware player profile retrieval.
        """
        raise NotImplementedError
