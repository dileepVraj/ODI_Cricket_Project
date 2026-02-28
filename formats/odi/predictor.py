import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional, Any, Union
from config.shared.venues import get_venue_aliases
from config.settings import (
    VENUE_BASELINE_DEFAULT, STANDARD_BATTING_POTENTIAL, 
    PREDICTION_MARGIN, MIN_BAT_AVG_CAP, MAX_BAT_AVG_CAP, MIN_BOWLS_FILTER
)
from config.shared.team_colors import TEAM_COLORS
from core.interfaces.predictor_interface import IPredictorEngine

# 🔧 INTERNAL CALIBRATION (Modern ODI Standards)
MODERN_BOWLING_ECONOMY = 5.85
MODERN_BOWLING_SR = 34.0
CRITICAL_BAT_DEPTH = 7

logger = logging.getLogger("CricketAnalyzer")


class PredictorEngine(IPredictorEngine):
    """
    🔮 The Sniper (v5.1 - Hardened & Config-Driven).
    - HEADLESS: Returns pure Dicts, no UI.
    - CONFIG-DRIVEN: No hardcoded constants.
    - ROBUST: Zero-hallucination floor on predictions.
    """
    def __init__(
        self,
        player_df: pd.DataFrame,
        dal: Any,
        format_config: Optional[Dict[str, Any]] = None,
        format_rules: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.player_df = player_df
        self.dal = dal
        self.format_config = format_config or {}
        self.rules = format_rules or {}
        
        # Injected Constants (with ODI defaults if config is missing)
        self.VENUE_BASELINE_DEFAULT = self.format_config.get("venue_baseline_default", 280)
        self.STANDARD_BATTING_POTENTIAL = self.format_config.get("standard_batting_potential", 300)
        self.MIN_BAT_AVG_CAP = self.format_config.get("min_bat_avg_cap", 5.0)
        self.MAX_BAT_AVG_CAP = self.format_config.get("max_bat_avg_cap", 60.0)
        self.MODERN_BOWLING_ECONOMY = self.format_config.get("modern_bowling_economy", 5.85)
        self.CRITICAL_BAT_DEPTH = self.format_config.get("critical_bat_depth", 7)
        self.PREDICTION_MARGIN = self.format_config.get("prediction_margin", 15)

    def calculate_smart_projection(self, player: str, role: str, venue_pattern: str) -> Tuple[float, str]:
        """
        Calculates a player's projected performance based on career and venue history.
        """
        # 1. Career Baseline (Static Context)
        bat = self.player_df[(self.player_df['player'] == player) & (self.player_df['role'] == role)]
        
        if bat.empty: 
            return 0.0, "-"
        
        if role == 'batting':
            runs = bat[bat['context']=='vs_team']['runs'].sum()
            outs = bat[bat['context']=='vs_team']['dismissals'].sum()
            car_val = runs / max(1, outs)
        else:
            wkts = bat[bat['context']=='vs_team']['dismissals'].sum()
            inns = bat[bat['context']=='vs_team']['innings'].sum()
            car_val = wkts / max(1, inns)

        # 2. Venue Specifics (Dynamic DAL Query)
        ven_val = car_val
        try:
            if self.dal is not None:
                # OPTIMIZATION: Request only balls for this player and venue
                base_df = self.dal.get_balls(
                    striker=player if role == 'batting' else None,
                    bowler=player if role == 'bowling' else None,
                    venue_id=venue_pattern
                )
                
                if base_df.empty:
                    return car_val, "OK"

                if role == 'batting':
                    v_runs = base_df['runs_off_bat'].sum()
                    v_outs = base_df['wicket_type'].notna().sum()
                    ven_val = v_runs / max(1, v_outs)
                else:
                    wkt_types = ['bowled','caught','lbw','stumped','caught and bowled','hit wicket']
                    v_wkts = base_df['wicket_type'].isin(wkt_types).sum()
                    v_matches = len(base_df['match_id'].unique())
                    ven_val = v_wkts / max(1, v_matches)
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            logger.warning(
                "Non-fatal smart projection venue context issue for player '%s': %s",
                player,
                exc,
            )

        proj = (0.3 * ven_val) + (0.7 * car_val)
        return round(proj, 1), "OK"

    # -------------------------------------------------------------------------
    # predict_score() — REMOVED (Phase 12 Rebuild Pending)
    #
    # Reason: The previous implementation loaded the entire balls table
    # (~181MB on disk, 300-600MB in RAM) with no player or team filter.
    # This was identified as a critical memory risk for Phase 12's
    # 10-second scrape cycle which would have caused repeated RAM spikes
    # eventually exceeding the 4GB hardware ceiling.
    #
    # Rebuild Requirements (for when this is reimplemented):
    # - MUST filter by players=all_players before loading any ball data
    # - MUST filter by team and venue at the SQL level, not in Pandas
    # - MUST comply with the Memory Ceiling Law in engineering_standards.md
    # - MUST comply with the I/O Air-Gap Law — no DAL calls inside the
    #   execute path. Data must be pre-loaded and injected.
    # - MUST use pre-allocated NumPy arrays for simulation results
    # - MUST be registered in manifest.py before any API or UI work begins
    # -------------------------------------------------------------------------
