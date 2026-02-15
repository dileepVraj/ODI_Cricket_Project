import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple, Optional, Any, Union
from config.shared.venues import get_venue_aliases
from config.settings import (
    VENUE_BASELINE_DEFAULT, STANDARD_BATTING_POTENTIAL, 
    PREDICTION_MARGIN, MIN_BAT_AVG_CAP, MAX_BAT_AVG_CAP, MIN_BOWLS_FILTER
)
from config.shared.team_colors import TEAM_COLORS

# 🔧 INTERNAL CALIBRATION (Modern ODI Standards)
MODERN_BOWLING_ECONOMY = 5.85
MODERN_BOWLING_SR = 34.0
CRITICAL_BAT_DEPTH = 7

class PredictorEngine:
    """
    🔮 The Sniper (v5.0 - Headless & Vectorized).
    - HEADLESS: Returns pure Dicts, no UI.
    - VECTORIZED: Uses groupby aggregation instead of loops.
    - TYPED: Full Type Hints.
    """
    def __init__(self, raw_df: pd.DataFrame, player_df: pd.DataFrame, dal: Optional[Any] = None) -> None:
        self.raw_df = raw_df
        self.player_df = player_df
        self.dal = dal

    def calculate_smart_projection(self, player: str, role: str, venue_pattern: str) -> Tuple[float, str]:
        """
        Calculates a player's projected performance based on career and venue history.
        """
        # 1. Career Baseline (Static Context for Speed)
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

        # 2. Venue Specifics (Dynamic)
        ven_val = car_val
        try:
            if self.dal is not None:
                base_df = self.dal.get_balls(striker=player) if role == 'batting' else self.dal.get_balls(bowler=player)
            else:
                base_df = self.raw_df

            mask = (base_df['venue'].str.contains(venue_pattern, case=False, na=False))
            
            if role == 'batting':
                raw_ven = base_df[(base_df['striker'] == player) & mask]
                if not raw_ven.empty:
                    v_runs = raw_ven['runs_off_bat'].sum()
                    v_outs = raw_ven['wicket_type'].notna().sum()
                    ven_val = v_runs / max(1, v_outs)
            else:
                raw_ven = base_df[(base_df['bowler'] == player) & mask]
                if not raw_ven.empty:
                    # Explicit list for wickets to match standards
                    wkt_types = ['bowled','caught','lbw','stumped','caught and bowled','hit wicket']
                    v_wkts = raw_ven['wicket_type'].isin(wkt_types).sum()
                    v_matches = len(raw_ven['match_id'].unique())
                    ven_val = v_wkts / max(1, v_matches)
        except Exception: 
            # Fallback to career stats if venue calculation fails (e.g. Regex error)
            pass

        proj = (0.3 * ven_val) + (0.7 * car_val)
        return round(proj, 1), "OK"

    def predict_score(self, 
                      batting_team: str, 
                      batting_players: List[str], 
                      bowling_team: str, 
                      bowling_players: List[str], 
                      venue_id: str, 
                      years: int = 5) -> Dict[str, Any]:
        """
        Generates a score prediction based on recent form and venue history.
        Vectorized for performance.
        """
        # 1. SETUP DYNAMIC WINDOW
        cutoff_date = pd.Timestamp.now().floor('D') - pd.DateOffset(years=years)
        
        if self.dal is not None:
            # If DAL exists, we might want to use it, but for now we follow the pattern
            # assuming DAL returns a DF or we fallback to raw_df
            window_df = self.dal.get_balls(years_back=years)
        else:
            window_df = self.raw_df

        if 'start_date' in window_df.columns:
            window_df['start_date'] = pd.to_datetime(window_df['start_date'], errors='coerce')
        
        # Filter by date
        window_df = window_df[window_df['start_date'] >= cutoff_date].copy()
        
        if window_df.empty:
            raise ValueError(f"No match data found for the last {years} years.")

        # 2. VENUE INTELLIGENCE
        target_venues = get_venue_aliases(venue_id)
        if "_" in venue_id: 
            parts = venue_id.split("_")
            if len(parts) > 1: target_venues.append(parts[1]) 
            
        # Escape for regex safely
        venue_pattern = '|'.join([re.escape(str(v)) for v in target_venues if v])
        
        venue_matches = window_df[
            (window_df['venue'].str.contains(venue_pattern, case=False, na=False)) & 
            (window_df['innings'] == 1)
        ]
        
        venue_avg = VENUE_BASELINE_DEFAULT
        venue_msg = "Global Avg (Data Missing)"
        
        if not venue_matches.empty:
            match_sums = venue_matches.groupby('match_id')[['runs_off_bat', 'extras']].sum()
            match_totals = match_sums['runs_off_bat'] + match_sums['extras']
            
            # Filter low scores (rain/collapses) to find 'Par'
            clean_totals = match_totals[match_totals > 180] 
            
            if not clean_totals.empty:
                venue_avg = int(clean_totals.mean())
                venue_msg = f"Venue Par (Last {years} Yrs, {len(clean_totals)} Mat)"
            else:
                venue_avg = int(match_totals.mean())
                venue_msg = f"Venue Avg (Low Sample: {len(match_totals)})"
        
        # 3. BATTING POWER (Vectorized)
        # Filter for all batting players at once
        bat_df = window_df[window_df['striker'].isin(batting_players)]
        
        # Calculate stats per player
        if not bat_df.empty:
             # Identify outs
            bat_df = bat_df.copy() # Avoid SettingWithCopy
            wkt_types = ['bowled','caught','lbw','stumped','caught and bowled','hit wicket']
            bat_df['is_out'] = bat_df['wicket_type'].isin(wkt_types).astype(int)
            
            player_stats = bat_df.groupby('striker').agg({
                'runs_off_bat': 'sum',
                'is_out': 'sum'
            })
            
            # Map back to ordered list
            stats_map = player_stats.to_dict('index')
        else:
            stats_map = {}

        total_bat_potential = 0.0
        capable_batters = 0 
        
        for p in batting_players:
            if p in stats_map:
                runs = stats_map[p]['runs_off_bat']
                outs = stats_map[p]['is_out']
                
                avg = (runs / outs) if outs > 0 else runs
                
                # Apply Caps
                avg = max(MIN_BAT_AVG_CAP, min(MAX_BAT_AVG_CAP, avg))
                
                total_bat_potential += avg
                if avg > 22: capable_batters += 1
            else:
                # Fallback for players with no recent data
                total_bat_potential += 15.0
        
        # 4. BOWLING THREAT (Vectorized)
        bowl_df = window_df[window_df['bowler'].isin(bowling_players)]
        
        total_econ = 0.0
        active_bowlers = 0
        
        if not bowl_df.empty:
            bowl_df = bowl_df.copy()
            # Calculate runs conceded (runs_off_bat + extras) per ball
            # Simplified: Sum runs and count rows
            bowl_agg = bowl_df.groupby('bowler').agg({
                'runs_off_bat': 'sum',
                'extras': 'sum',
                'match_id': 'count' # acts as ball count
            })
            
            for p in bowling_players:
                if p in bowl_agg.index:
                    runs = bowl_agg.loc[p, 'runs_off_bat'] + bowl_agg.loc[p, 'extras']
                    balls = bowl_agg.loc[p, 'match_id']
                    
                    if balls > 60: # Minimum 10 overs
                        econ = (runs / balls) * 6
                        total_econ += econ
                        active_bowlers += 1
        
        avg_bowling_econ = (total_econ / active_bowlers) if active_bowlers > 0 else MODERN_BOWLING_ECONOMY
        
        # 5. ALGORITHM
        bat_factor = total_bat_potential / STANDARD_BATTING_POTENTIAL
        bowl_factor = avg_bowling_econ / MODERN_BOWLING_ECONOMY 
        
        raw_prediction = venue_avg * bat_factor * bowl_factor
        
        # 6. RISK ADJUSTMENTS & LABELS
        adjustment_msg = []
        final_prediction = raw_prediction
        
        # A. Collapse Penalty
        if capable_batters < CRITICAL_BAT_DEPTH:
            base_penalty = (CRITICAL_BAT_DEPTH - capable_batters) * 20
            if bowl_factor < 0.96:
                base_penalty = int(base_penalty * 1.5)
                adjustment_msg.append(f"📉 High Collapse Risk (-{base_penalty})")
            else:
                adjustment_msg.append(f"📉 Tail-Ender Risk (-{base_penalty})")
            final_prediction -= base_penalty

        # B. Smart Labels
        if bowl_factor < 0.95:
            bf_text = "STRONG ATTACK"
        elif bowl_factor > 1.05:
            bf_text = "WEAK ATTACK"
        else:
            bf_text = "AVERAGE ATTACK"

        # 7. ASSEMBLE PACKET
        lower = int(final_prediction - PREDICTION_MARGIN)
        upper = int(final_prediction + PREDICTION_MARGIN)
        
        return {
            'batting_team': batting_team,
            'bowling_team': bowling_team,
            'venue_id': venue_id,
            'venue_msg': venue_msg,
            'venue_avg': venue_avg,
            'bat_factor': round(bat_factor, 2),
            'bowl_factor': round(bowl_factor, 2),
            'bf_text': bf_text,
            'lower': lower,
            'upper': upper,
            'adjustment_msg': adjustment_msg,
            'years': years
        }
