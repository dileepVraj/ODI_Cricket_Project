"""
core/interfaces/team_interface.py
Structural contracts for Team Analytics engines.

These dataclasses are used as type hints and return types.
The ITeamEngine Protocol defines the minimum API any format's
TeamEngine must implement.
"""
from typing import Dict, List, Optional, Protocol, Any
from dataclasses import dataclass


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


class ITeamEngine(Protocol):
    """
    The Strict Contract for Team Analytics.

    Rules:
    1. Returns Data Classes or Typed Dicts.
    2. NO HTML Generation (Violation of Headless Principle).
    3. NO Direct Database Access (Must use DataAccess Layer).

    Any format's TeamEngine MUST implement at minimum these methods.
    Additional format-specific methods are allowed.
    """

    def analyze_home_fortress(
        self,
        stadium_name: str,
        home_team: str,
        opp_team: str = 'All',
        years_back: int = 10,
        recorder: Any = None
    ) -> Dict[str, Any]:
        """Analyzes a team's performance at a specific stadium."""
        ...

    def analyze_venue_bias(
        self,
        stadium_name: str,
        years_back: int = 10,
        recorder: Any = None
    ) -> Dict[str, Any]:
        """Determines bat-first vs chase bias at a venue."""
        ...

    def analyze_global_h2h(
        self,
        home_team: str,
        opp_team: str,
        years_back: int = 5
    ) -> Dict[str, Any]:
        """Analyzes Head-to-Head performance between two teams globally."""
        ...

    def analyze_team_form(
        self,
        team_name: str,
        opp_team: str = 'All',
        continent: str = 'All',
        limit: int = 5,
        recorder: Any = None
    ) -> Dict[str, Any]:
        """Retrieves recent team form."""
        ...
