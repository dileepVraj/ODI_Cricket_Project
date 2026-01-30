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
MODERN_BOWLING_ECONOMY = 5.85
MODERN_BOWLING_SR = 34.0
CRITICAL_BAT_DEPTH = 7

class PredictorEngine:
    """
    🔮 The Sniper (v4.0 - Fully Dynamic Timeframe).
    - FEATURE: Batting & Bowling factors now respect the 'years' slider.
    - FIX: '1.00x' is now labeled 'AVERAGE ATTACK', not 'WEAK'.
    - LOGIC: Calculates player form on-the-fly from the specific time window.
    """
    def __init__(self, raw_df, player_df):
        self.raw_df = raw_df
        self.player_df = player_df

    def calculate_smart_projection(self, player, role, venue_pattern):
        # (Helper for simple tables - keeps static context for speed)
        bat = self.player_df[(self.player_df['player'] == player) & (self.player_df['role'] == role)]
        if bat.empty: return 0, "-"
        
        if role == 'batting':
            car_val = bat[bat['context']=='vs_team']['runs'].sum() / max(1, bat[bat['context']=='vs_team']['dismissals'].sum())
        else:
            car_val = bat[bat['context']=='vs_team']['dismissals'].sum() / max(1, bat[bat['context']=='vs_team']['innings'].sum())

        ven_val = car_val
        try:
            mask = (self.raw_df['venue'].str.contains(venue_pattern, case=False, na=False))
            if role == 'batting':
                raw_ven = self.raw_df[(self.raw_df['striker'] == player) & mask]
                if not raw_ven.empty:
                    ven_val = raw_ven['runs_off_bat'].sum() / max(1, raw_ven['wicket_type'].notna().sum())
            else:
                raw_ven = self.raw_df[(self.raw_df['bowler'] == player) & mask]
                if not raw_ven.empty:
                    wkts = raw_ven['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']).sum()
                    ven_val = wkts / max(1, len(raw_ven['match_id'].unique()))
        except: pass

        proj = (0.3 * ven_val) + (0.7 * car_val)
        return round(proj, 1), "OK"

    def predict_score(self, batting_team, batting_players, bowling_team, bowling_players, venue_id, years=5):
        # 1. SETUP DYNAMIC WINDOW
        # We slice the Raw DB once to improve performance
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years)
        window_df = self.raw_df[self.raw_df['start_date'] >= cutoff_date].copy()
        
        # 2. VENUE INTELLIGENCE (From Window)
        target_venues = get_venue_aliases(venue_id)
        if "_" in venue_id: 
            parts = venue_id.split("_")
            if len(parts) > 1: target_venues.append(parts[1]) 
            
        venue_pattern = '|'.join([re.escape(v) for v in target_venues if v])
        
        venue_matches = window_df[
            (window_df['venue'].str.contains(venue_pattern, case=False, na=False)) & 
            (window_df['innings'] == 1)
        ]
        
        venue_avg = VENUE_BASELINE_DEFAULT
        venue_msg = "Global Avg (Data Missing)"
        
        if not venue_matches.empty:
            match_sums = venue_matches.groupby('match_id')[['runs_off_bat', 'extras']].sum()
            match_totals = match_sums['runs_off_bat'] + match_sums['extras']
            clean_totals = match_totals[match_totals > 180] 
            
            if not clean_totals.empty:
                venue_avg = int(clean_totals.mean())
                venue_msg = f"Venue Par (Last {years} Yrs, {len(clean_totals)} Mat)"
            else:
                venue_avg = int(match_totals.mean())
                venue_msg = f"Venue Avg (Low Sample: {len(match_totals)})"
        
        # 3. BATTING POWER (From Window)
        total_bat_potential = 0
        capable_batters = 0 
        
        for p in batting_players:
            # Filter specifically for this player in the time window
            p_data = window_df[window_df['striker'] == p]
            
            if not p_data.empty:
                runs = p_data['runs_off_bat'].sum()
                outs = p_data['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']).sum()
                avg = (runs / outs) if outs > 0 else runs
                
                # Apply Caps (Standardizing form)
                if avg > MAX_BAT_AVG_CAP: avg = MAX_BAT_AVG_CAP
                if avg < MIN_BAT_AVG_CAP: avg = MIN_BAT_AVG_CAP
                
                total_bat_potential += avg
                if avg > 22: capable_batters += 1
            else:
                # Fallback: If no data in window, use a conservative baseline
                total_bat_potential += 15 
        
        # 4. BOWLING THREAT (From Window)
        total_econ = 0
        active_bowlers = 0
        
        for p in bowling_players:
            p_data = window_df[window_df['bowler'] == p]
            
            if not p_data.empty:
                runs = p_data['runs_off_bat'].sum() + p_data['extras'].sum()
                balls = len(p_data)
                
                if balls > 60: # Minimum 10 overs in timeframe to count
                    econ = (runs / balls) * 6
                    total_econ += econ
                    active_bowlers += 1
        
        # If no active bowlers found in window, assume average
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
            bf_color = 'green'; bf_text = "STRONG ATTACK"
        elif bowl_factor > 1.05:
            bf_color = 'red'; bf_text = "WEAK ATTACK"
        else:
            bf_color = '#d35400'; bf_text = "AVERAGE ATTACK"

        # 7. RENDER
        lower = int(final_prediction - PREDICTION_MARGIN)
        upper = int(final_prediction + PREDICTION_MARGIN)
        c1 = TEAM_COLORS.get(batting_team, "#333")
        
        display(HTML(f"""
        <div style="background:#fff; border:1px solid #ddd; border-top: 4px solid {c1}; border-radius:6px; margin-bottom:20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <div style="padding:10px; background:#f8f9fa; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;">
                <div style="font-weight:bold; color:#333;">🔮 PROJECTED SCORE: {batting_team.upper()}</div>
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