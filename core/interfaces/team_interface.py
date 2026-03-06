"""
core/interfaces/team_interface.py
Structural contracts for Team Analytics engines.

These dataclasses are used as type hints and return types.
The ITeamEngine ABC defines the minimum API any format's
TeamEngine must implement.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass, field
import pandas as pd

from core.interfaces.team_types import (
    ComparisonReportRows,
    MatrixReportRows,
    RecorderPort,
    TeamFormRows,
    TeamMatchContext,
    VenueBiasReport,
    VenueMatchupReport,
    VenuePhasesReport,
)

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
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> ComparisonReportRows:
        """Analyzes a team's performance at a specific stadium."""
        raise NotImplementedError

    @abstractmethod
    def analyze_venue_matchup_structured(
        self,
        stadium_name: str,
        home_team: str,
        opp_team: str,
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> VenueMatchupReport:
        """Returns structured venue matchup intelligence payload."""
        raise NotImplementedError

    @abstractmethod
    def analyze_venue_phases(
        self,
        stadium_id: str,
        home_team: Optional[str] = None,
        away_team: Optional[str] = None,
        years: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> VenuePhasesReport:
        """Analyzes phase-level venue behavior."""
        raise NotImplementedError

    @abstractmethod
    def analyze_venue_bias(
        self,
        stadium_name: str,
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> Optional[VenueBiasReport]:
        """Determines bat-first vs chase bias at a venue."""
        raise NotImplementedError

    @abstractmethod
    def analyze_global_h2h(
        self,
        home_team: str,
        opp_team: str,
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> ComparisonReportRows:
        """Analyzes Head-to-Head performance between two teams globally."""
        raise NotImplementedError

    @abstractmethod
    def analyze_country_h2h(
        self,
        home_team: str,
        opp_team: str = "All",
        country_name: Optional[str] = None,
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> ComparisonReportRows:
        """Analyzes team performance by host country."""
        raise NotImplementedError

    @abstractmethod
    def analyze_home_dominance(
        self,
        home_team: str,
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> MatrixReportRows:
        """Analyzes home dominance matrix."""
        raise NotImplementedError

    @abstractmethod
    def analyze_away_performance(
        self,
        team_name: str,
        years_back: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> MatrixReportRows:
        """Analyzes away performance matrix."""
        raise NotImplementedError

    @abstractmethod
    def analyze_global_performance(
        self,
        team_name: str,
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> MatrixReportRows:
        """Analyzes global performance matrix."""
        raise NotImplementedError

    @abstractmethod
    def analyze_continent_performance(
        self,
        team_name: str,
        continent: str,
        opp_team: str = "All",
        years_back: int = 0,
        match_context: Optional[TeamMatchContext] = None,
    ) -> MatrixReportRows | ComparisonReportRows:
        """Analyzes regional/continent performance."""
        raise NotImplementedError

    @abstractmethod
    def analyze_team_form(
        self,
        team_name: str,
        opp_team: str = 'All',
        continent: str = 'All',
        limit: int = 0,
        recorder: Optional[RecorderPort] = None,
        match_context: Optional[TeamMatchContext] = None,
    ) -> TeamFormRows:
        """Retrieves recent team form."""
        raise NotImplementedError
