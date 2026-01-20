import pandas as pd
import numpy as np
import re
from IPython.display import display, HTML
from venues import get_venue_aliases
from config.settings import (
    VENUE_BASELINE_DEFAULT, STANDARD_BATTING_POTENTIAL, 
    PREDICTION_MARGIN, MIN_BAT_AVG_CAP, MAX_BAT_AVG_CAP, MIN_BOWLS_FILTER
)
from config.teams import TEAM_COLORS

# 🔧 INTERNAL CALIBRATION (Modern ODI Standards)
# We moved these here to ensure they override any old settings
MODERN_BOWLING_ECONOMY = 5.85  # Raised from 5.0 -> Makes 5.4 look ELITE
MODERN_BOWLING_SR = 34.0       # Standard balls per wicket
CRITICAL_BAT_DEPTH = 7         # Minimum real batters needed

class PredictorEngine:
    """
    🔮 The Sniper (v3.2 - Calibrated).
    - Fix: 'Bowl Weakness' now correctly identifies Elite Attacks as 'Strength' (<1.0x).
    - Logic: Aggressive Collapse Penalty when weak batting meets strong bowling.
    """
    def __init__(self, raw_df, player_df):
        self.raw_df = raw_df
        self.player_df = player_df

    def calculate_smart_projection(self, player, role, venue_pattern):
        # (Lightweight helper for tables)
        bat = self.player_df[(self.player_df['player'] == player) & (self.player_df['role'] == role)]
        if bat.empty: return 0, "-"
        
        if role == 'batting':
            car_val = bat[bat['context']=='vs_team']['runs'].sum() / max(1, bat[bat['context']=='vs_team']['dismissals'].sum())
        else:
            car_val = bat[bat['context']=='vs_team']['dismissals'].sum() / max(1, bat[bat['context']=='vs_team']['innings'].sum())

        ven_val = car_val
        try:
            # Simple Regex search for table display
            mask = (self.raw_df['venue'].str.contains(venue_pattern, case=False, na=False))
            if role == 'batting':
                raw_ven = self.raw_df[(self.raw_df['striker'] == player) & mask]
                if not raw_ven.empty:
                    runs = raw_ven['runs_off_bat'].sum()
                    outs = raw_ven['wicket_type'].notna().sum()
                    ven_val = runs / max(1, outs)
            else:
                raw_ven = self.raw_df[(self.raw_df['bowler'] == player) & mask]
                if not raw_ven.empty:
                    wkts = raw_ven['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']).sum()
                    matches = len(raw_ven['match_id'].unique())
                    ven_val = wkts / max(1, matches)
        except: pass

        proj = (0.3 * ven_val) + (0.7 * car_val)
        return round(proj, 1), "OK"

    def predict_score(self, batting_team, batting_players, bowling_team, bowling_players, venue_id):
        # 1. VENUE INTELLIGENCE (Modern Par)
        target_venues = get_venue_aliases(venue_id)
        if "_" in venue_id: 
            parts = venue_id.split("_")
            if len(parts) > 1: target_venues.append(parts[1]) 
            
        venue_pattern = '|'.join([re.escape(v) for v in target_venues if v])
        
        # Date Filter: Last 5 Years
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=5)
        
        venue_matches = self.raw_df[
            (self.raw_df['venue'].str.contains(venue_pattern, case=False, na=False)) & 
            (self.raw_df['innings'] == 1) &
            (self.raw_df['start_date'] >= cutoff_date)
        ]
        
        venue_avg = VENUE_BASELINE_DEFAULT
        venue_msg = "Global Avg (Data Missing)"
        
        if not venue_matches.empty:
            match_sums = venue_matches.groupby('match_id')[['runs_off_bat', 'extras']].sum()
            match_totals = match_sums['runs_off_bat'] + match_sums['extras']
            clean_totals = match_totals[match_totals > 180] 
            
            if not clean_totals.empty:
                venue_avg = int(clean_totals.mean())
                venue_msg = f"Venue Par (Last 5 Yrs, {len(clean_totals)} Mat)"
            else:
                venue_avg = int(match_totals.mean())
                venue_msg = f"Venue Avg (Low Sample: {len(match_totals)})"
        
        # 2. BATTING POWER & DEPTH
        total_bat_potential = 0
        capable_batters = 0 
        
        for p in batting_players:
            p_stats = self.player_df[(self.player_df['player'] == p) & (self.player_df['role'] == 'batting')]
            if not p_stats.empty:
                runs = p_stats[p_stats['context'] == 'vs_team']['runs'].sum()
                outs = p_stats[p_stats['context'] == 'vs_team']['dismissals'].sum()
                avg = (runs / outs) if outs > 0 else runs
                
                # Apply Caps
                if avg > MAX_BAT_AVG_CAP: avg = MAX_BAT_AVG_CAP
                if avg < MIN_BAT_AVG_CAP: avg = MIN_BAT_AVG_CAP
                
                total_bat_potential += avg
                if avg > 22: capable_batters += 1 # Raised threshold slightly
        
        # 3. BOWLING THREAT (Economy + Strike Rate)
        total_econ = 0
        total_sr = 0
        active_bowlers = 0
        
        for p in bowling_players:
            p_stats = self.player_df[(self.player_df['player'] == p) & (self.player_df['role'] == 'bowling')]
            if not p_stats.empty:
                runs = p_stats[p_stats['context'] == 'vs_team']['runs'].sum()
                balls = p_stats[p_stats['context'] == 'vs_team']['balls'].sum()
                wkts = p_stats[p_stats['context'] == 'vs_team']['dismissals'].sum()
                
                if balls > MIN_BOWLS_FILTER:
                    econ = (runs / balls) * 6
                    sr = (balls / wkts) if wkts > 0 else 60
                    
                    total_econ += econ
                    total_sr += sr
                    active_bowlers += 1
        
        avg_bowling_econ = (total_econ / active_bowlers) if active_bowlers > 0 else MODERN_BOWLING_ECONOMY
        
        # 4. ALGORITHM (Calibrated)
        bat_factor = total_bat_potential / STANDARD_BATTING_POTENTIAL
        
        # Bowl Factor: If Economy is 5.4 vs Standard 5.85, Factor is 0.92 (Strength)
        bowl_factor = avg_bowling_econ / MODERN_BOWLING_ECONOMY 
        
        raw_prediction = venue_avg * bat_factor * bowl_factor
        
        # 5. RISK ADJUSTMENTS
        adjustment_msg = []
        final_prediction = raw_prediction
        
        # A. Collapse Penalty
        if capable_batters < CRITICAL_BAT_DEPTH:
            base_penalty = (CRITICAL_BAT_DEPTH - capable_batters) * 20 # -20 runs per missing batter
            
            # Multiplier: If bowling is STRONG (factor < 0.96), double the penalty
            if bowl_factor < 0.96:
                base_penalty = int(base_penalty * 1.5)
                adjustment_msg.append(f"📉 High Collapse Risk (-{base_penalty})")
            else:
                adjustment_msg.append(f"📉 Tail-Ender Risk (-{base_penalty})")
                
            final_prediction -= base_penalty

        # 6. RENDER
        lower = int(final_prediction - PREDICTION_MARGIN)
        upper = int(final_prediction + PREDICTION_MARGIN)
        
        c1 = TEAM_COLORS.get(batting_team, "#333")
        
        # Color logic for Bowl Factor (Green if < 1 because low score is good for bowling team)
        bf_color = 'green' if bowl_factor < 1.0 else 'red'
        bf_text = "STRONG ATTACK" if bowl_factor < 1.0 else "WEAK ATTACK"
        
        display(HTML(f"""
        <div style="background:#fff; border:1px solid #ddd; border-top: 4px solid {c1}; border-radius:6px; margin-bottom:20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <div style="padding:10px; background:#f8f9fa; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;">
                <div style="font-weight:bold; color:#333;">🔮 SCORE PREDICTOR</div>
                <div style="font-size:11px; color:#777;">{venue_msg}</div>
            </div>
            
            <div style="padding:15px; display:flex; justify-content:space-between; align-items:center;">
                <div style="text-align:center;">
                    <div style="font-size:12px; color:#555;">VENUE PAR</div>
                    <div style="font-size:20px; font-weight:bold; color:#333;">{venue_avg}</div>
                </div>
                <div style="text-align:center; color:#ccc;">✖️</div>
                <div style="text-align:center;">
                    <div style="font-size:12px; color:#555;">BAT STRENGTH</div>
                    <div style="font-size:18px; font-weight:bold; color:{'green' if bat_factor>=1 else 'red'}">{bat_factor:.2f}x</div>
                </div>
                <div style="text-align:center; color:#ccc;">✖️</div>
                <div style="text-align:center;">
                    <div style="font-size:12px; color:#555;">BOWL IMPACT</div>
                    <div style="font-size:18px; font-weight:bold; color:{bf_color}">{bowl_factor:.2f}x</div>
                    <div style="font-size:9px; color:{bf_color}">{bf_text}</div>
                </div>
                <div style="text-align:center; color:#ccc;">=</div>
                <div style="text-align:center; background:{c1}; color:white; padding:10px 20px; border-radius:6px;">
                    <div style="font-size:12px; opacity:0.9;">PREDICTED RANGE</div>
                    <div style="font-size:24px; font-weight:bold;">{lower} - {upper}</div>
                </div>
            </div>
            
            <div style="padding:10px; background:#fffbe6; font-size:11px; color:#856404; border-top:1px solid #ffeeba;">
                <b>🤖 Model Notes:</b> {', '.join(adjustment_msg) if adjustment_msg else 'Standard conditions detected.'}
            </div>
        </div>
        """))