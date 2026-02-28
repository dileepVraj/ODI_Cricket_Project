"""
core/interfaces/team_interface.py
Structural contracts for Team Analytics engines.

These dataclasses are used as type hints and return types.
The ITeamEngine ABC defines the minimum API any format's
TeamEngine must implement.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass, field
import pandas as pd


@dataclass
class VenueStats:
    """Stats for a specific venue."""
    venue_id: str
    matches_played: int
    home_win_pct: float
    bat_first_win_pct: float
    avg_first_inns_score: int
    avg_wickets_lost: float


@dataclass
class TeamMatchup:
    """Head-to-head record between two teams."""
    team: str
    opponent: str
    matches: int
    wins: int
    losses: int
    win_pct: float
    last_5_results: List[str]  # ["W", "L", "W", "NR", "W"]


@dataclass
class FormGuide:
    """Recent form summary for a team."""
    team: str
    total: int
    wins: int
    losses: int
    win_pct: float
    sequence: List[str]
    form_string: str  # "W W L W L"


@dataclass
class TeamVenueStats:
    """Detailed batting/chasing stats for a team at a specific venue."""
    wins: int
    defended: int
    chased: int
    bat1: Dict[str, Any]      # {avg, high, low, avg_win, low_def}
    chase: Dict[str, Any]     # {avg, high, succ, fail}
    team_color: Optional[str] = None
    team_tone: Optional[str] = None
    low_sample_warnings: List[str] = field(default_factory=list)
    highlight_flags: Dict[str, bool] = field(default_factory=dict)
    derived_badges: List[str] = field(default_factory=list)


@dataclass
class MatchIntelligenceData:
    """Structured data for the dual-card Match Intelligence UI."""
    summary: Dict[str, Any]   # {matches, win_pct, tie_nr}
    team_a: Dict[str, Any]    # {name, stats: TeamVenueStats}
    team_b: Dict[str, Any]    # {name, stats: TeamVenueStats}
    venue_avg: Dict[str, Any] # {avg_1st, avg_2nd, avg_win_score}
    MATCH_IDS: Optional[str] = None
    low_sample_warnings: List[str] = field(default_factory=list)
    highlight_flags: Dict[str, bool] = field(default_factory=dict)
    derived_badges: List[str] = field(default_factory=list)


class MatchContext(TypedDict, total=False):
    """Request-scoped context for stateless TeamEngine execution."""
    match_df: pd.DataFrame
    phase_df: pd.DataFrame
    reference_date: pd.Timestamp
    tactical_thresholds: Dict[str, int]


class ITeamEngine(ABC):
    """
    The Strict Contract for Team Analytics.

    Rules:
    1. Returns Data Classes or Typed Dicts.
    2. NO HTML Generation (Violation of Headless Principle).
    3. NO Direct Database Access (Must use DataAccess Layer).

    Any format's TeamEngine MUST implement at minimum these methods.
    Additional format-specific methods are allowed.
    """

    @abstractmethod
    def analyze_home_fortress(
        self,
        stadium_name: str,
        home_team: str,
        opp_team: str = 'All',
        years_back: int = 10,
        recorder: Any = None,
        match_context: Optional[MatchContext] = None,
    ) -> List[Dict[str, Any]]:
        """Analyzes a team's performance at a specific stadium."""
        raise NotImplementedError

    @abstractmethod
    def analyze_venue_matchup_structured(
        self,
        stadium_name: str,
        home_team: str,
        opp_team: str,
        years_back: int = 5,
        match_context: Optional[MatchContext] = None,
    ) -> MatchIntelligenceData:
        """Returns structured venue matchup intelligence payload."""
        raise NotImplementedError

    @abstractmethod
    def analyze_venue_phases(
        self,
        stadium_id: str,
        home_team: Optional[str] = None,
        away_team: Optional[str] = None,
        years: int = 5,
        recorder: Any = None,
        match_context: Optional[MatchContext] = None,
    ) -> Dict[str, Any]:
        """Analyzes phase-level venue behavior."""
        raise NotImplementedError

    @abstractmethod
    def analyze_venue_bias(
        self,
        stadium_name: str,
        years_back: int = 10,
        recorder: Any = None,
        match_context: Optional[MatchContext] = None,
    ) -> Optional[Dict[str, Any]]:
        """Determines bat-first vs chase bias at a venue."""
        raise NotImplementedError

    @abstractmethod
    def analyze_global_h2h(
        self,
        home_team: str,
        opp_team: str,
        years_back: int = 5,
        match_context: Optional[MatchContext] = None,
    ) -> Dict[str, Any]:
        """Analyzes Head-to-Head performance between two teams globally."""
        raise NotImplementedError

    @abstractmethod
    def analyze_country_h2h(
        self,
        home_team: str,
        opp_team: str = "All",
        country_name: Optional[str] = None,
        years_back: int = 10,
        recorder: Optional[Any] = None,
        match_context: Optional[MatchContext] = None,
    ) -> List[Dict[str, Any]]:
        """Analyzes team performance by host country."""
        raise NotImplementedError

    @abstractmethod
    def analyze_home_dominance(
        self,
        home_team: str,
        years_back: int = 10,
        recorder: Optional[Any] = None,
        match_context: Optional[MatchContext] = None,
    ) -> List[Dict[str, Any]]:
        """Analyzes home dominance matrix."""
        raise NotImplementedError

    @abstractmethod
    def analyze_away_performance(
        self,
        team_name: str,
        years_back: int = 5,
        recorder: Optional[Any] = None,
        match_context: Optional[MatchContext] = None,
    ) -> List[Dict[str, Any]]:
        """Analyzes away performance matrix."""
        raise NotImplementedError

    @abstractmethod
    def analyze_global_performance(
        self,
        team_name: str,
        years_back: int = 5,
        match_context: Optional[MatchContext] = None,
    ) -> List[Dict[str, Any]]:
        """Analyzes global performance matrix."""
        raise NotImplementedError

    @abstractmethod
    def analyze_continent_performance(
        self,
        team_name: str,
        continent: str,
        opp_team: str = "All",
        years_back: int = 5,
        match_context: Optional[MatchContext] = None,
    ) -> List[Dict[str, Any]]:
        """Analyzes regional/continent performance."""
        raise NotImplementedError

    @abstractmethod
    def analyze_team_form(
        self,
        team_name: str,
        opp_team: str = 'All',
        continent: str = 'All',
        limit: int = 5,
        recorder: Any = None,
        match_context: Optional[MatchContext] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieves recent team form."""
        raise NotImplementedError
