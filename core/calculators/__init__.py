"""Pure calculator functions used by engines and services."""

from .player_math import calculate_batting_metrics, calculate_squad_batting_metrics
from .matchup_engine import MatchupEngine
from .performance import calculate_team_metrics
from .phase_engine import (
    build_phase_scenario_rows,
    calculate_phase_breakdown,
    calculate_team_phase_habits,
    summarize_phase_by_innings,
)
from .team import (
    calculate_away_performance_payload,
    calculate_continent_performance_payload,
    calculate_country_h2h_payload,
    calculate_global_h2h_payload,
    calculate_global_performance_payload,
    calculate_home_dominance_payload,
    calculate_home_fortress_payload,
    calculate_team_form_payload,
    calculate_venue_bias_payload,
    calculate_venue_matchup_payload,
    calculate_venue_phases_payload,
)

__all__ = [
    "calculate_batting_metrics",
    "calculate_squad_batting_metrics",
    "MatchupEngine",
    "calculate_team_metrics",
    "calculate_phase_breakdown",
    "summarize_phase_by_innings",
    "calculate_team_phase_habits",
    "build_phase_scenario_rows",
    "calculate_global_h2h_payload",
    "calculate_country_h2h_payload",
    "calculate_home_fortress_payload",
    "calculate_venue_bias_payload",
    "calculate_venue_matchup_payload",
    "calculate_venue_phases_payload",
    "calculate_home_dominance_payload",
    "calculate_away_performance_payload",
    "calculate_global_performance_payload",
    "calculate_continent_performance_payload",
    "calculate_team_form_payload",
]
