import pandas as pd
from IPython.display import display, HTML
from venues import get_venue_aliases
from config.settings import (
    VENUE_BASELINE_DEFAULT, STANDARD_BATTING_POTENTIAL, 
    STANDARD_BOWLING_ECONOMY, PREDICTION_MARGIN,
    MIN_BAT_AVG_CAP, MAX_BAT_AVG_CAP, MIN_BOWLS_FILTER,
    WEIGHT_FORM, WEIGHT_VENUE, WEIGHT_CAREER
)

class PredictorEngine:
    """
    🔮 The Oracle.
    Handles Score Predictions and Smart Projections using the Law of Averages.
    """
    def __init__(self, raw_df, player_df):
        self.raw_df = raw_df
        self.player_df = player_df

    def calculate_smart_projection(self, player, role, venue_name):
        """
        🔮 LAW OF AVERAGES ENGINE
        Formula: (Form * W1) + (Venue * W2) + (Career * W3)
        """
        # 1. Career Stats
        p_stats = self.player_df[(self.player_df['player'] == player) & (self.player_df['role'] == role)]
        if p_stats.empty: return 0, "New Player"

        car_runs = p_stats[p_stats['context'] == 'vs_team']['runs'].sum()
        car_outs = p_stats[p_stats['context'] == 'vs_team']['dismissals'].sum()
        car_avg = (car_runs / car_outs) if car_outs > 0 else car_runs
        
        # 2. Venue Stats
        ven_stats = p_stats[(p_stats['context'] == 'at_venue') & (p_stats['opponent'] == venue_name)]
        if not ven_stats.empty:
            ven_runs = ven_stats['runs'].sum()
            ven_outs = ven_stats['dismissals'].sum()
            ven_avg = (ven_runs / ven_outs) if ven_outs > 0 else ven_runs
        else:
            ven_avg = car_avg

        # 3. Recent Form
        recent_avg = car_avg
        try:
            if role == 'batting':
                p_raw = self.raw_df[self.raw_df['striker'] == player].drop_duplicates(subset=['match_id'])
                last_5 = p_raw.tail(5)
                if not last_5.empty:
                    runs_5 = 0; outs_5 = 0
                    for m_id in last_5['match_id'].unique():
                        m_data = self.raw_df[(self.raw_df['match_id'] == m_id) & (self.raw_df['striker'] == player)]
                        runs_5 += m_data['runs_off_bat'].sum()
                        if m_data['wicket_type'].notna().any(): outs_5 += 1
                    recent_avg = (runs_5 / outs_5) if outs_5 > 0 else runs_5
            
            elif role == 'bowling':
                p_raw = self.raw_df[self.raw_df['bowler'] == player].drop_duplicates(subset=['match_id'])
                last_5 = p_raw.tail(5)
                if not last_5.empty:
                    wkts_5 = 0; matches_5 = len(last_5)
                    wicket_types = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
                    for m_id in last_5['match_id'].unique():
                        m_data = self.raw_df[(self.raw_df['match_id'] == m_id) & (self.raw_df['bowler'] == player)]
                        wkts_5 += m_data['wicket_type'].isin(wicket_types).sum()
                    
                    recent_avg = wkts_5 / matches_5 # Wkts per match
                    
                    # Normalize Historical Avgs to Wkts/Match for weighting
                    c_inns = p_stats[p_stats['context'] == 'vs_team']['innings'].sum()
                    c_wkts = p_stats[p_stats['context'] == 'vs_team']['dismissals'].sum()
                    car_avg = c_wkts / c_inns if c_inns > 0 else 0
                    
                    if not ven_stats.empty:
                         v_inns = ven_stats['innings'].sum()
                         v_wkts = ven_stats['dismissals'].sum()
                         ven_avg = v_wkts / v_inns if v_inns > 0 else 0
                    else:
                        ven_avg = car_avg
        except: pass

        weighted = (WEIGHT_FORM * recent_avg) + (WEIGHT_VENUE * ven_avg) + (WEIGHT_CAREER * car_avg)
        return round(weighted, 1), "OK"

    def predict_score(self, batting_team, batting_players, bowling_team, bowling_players, venue_id):
        print(f"\n🔮 SCORE PREDICTOR: {batting_team} Batting First at {venue_id}")
        print("="*80)
        
        target_venues = get_venue_aliases(venue_id)
        
        # 1. VENUE BASELINE
        venue_mask = self.raw_df['venue'].isin(target_venues) & (self.raw_df['innings'] == 1)
        venue_matches = self.raw_df[venue_mask]
        
        venue_avg = VENUE_BASELINE_DEFAULT
        sample_size = 0
        
        if venue_matches.empty:
            print(f"⚠️ Not enough data for venue '{venue_id}'. Using Global Avg ({VENUE_BASELINE_DEFAULT}).")
        else:
            match_sums = venue_matches.groupby('match_id')[['runs_off_bat', 'extras']].sum()
            match_totals = match_sums['runs_off_bat'] + match_sums['extras']
            venue_avg = int(match_totals.mean())
            sample_size = len(match_totals)
            print(f"🏟️ Venue Avg (1st Inn): {venue_avg} runs (Sample: {sample_size} matches)")

        # 2. BATTING POWER
        total_bat = 0
        for p in batting_players:
            p_stats = self.player_df[(self.player_df['player'] == p) & (self.player_df['role'] == 'batting')]
            if not p_stats.empty:
                runs = p_stats[p_stats['context'] == 'vs_team']['runs'].sum()
                outs = p_stats[p_stats['context'] == 'vs_team']['dismissals'].sum()
                avg = (runs / outs) if outs > 0 else runs
                if avg > MAX_BAT_AVG_CAP: avg = MAX_BAT_AVG_CAP
                if avg < MIN_BAT_AVG_CAP: avg = MIN_BAT_AVG_CAP
                total_bat += avg
        
        bat_factor = total_bat / STANDARD_BATTING_POTENTIAL if STANDARD_BATTING_POTENTIAL > 0 else 1.0
        
        # 3. BOWLING RESISTANCE
        total_econ = 0; active_bowlers = 0
        for p in bowling_players:
            p_stats = self.player_df[(self.player_df['player'] == p) & (self.player_df['role'] == 'bowling')]
            if not p_stats.empty:
                runs = p_stats[p_stats['context'] == 'vs_team']['runs'].sum()
                balls = p_stats[p_stats['context'] == 'vs_team']['balls'].sum()
                if balls > MIN_BOWLS_FILTER:
                    econ = (runs / balls) * 6
                    total_econ += econ
                    active_bowlers += 1
        
        avg_econ = (total_econ / active_bowlers) if active_bowlers > 0 else STANDARD_BOWLING_ECONOMY
        bowl_factor = avg_econ / STANDARD_BOWLING_ECONOMY
        
        # 4. RESULT
        predicted_score = venue_avg * bat_factor * bowl_factor
        low = int(predicted_score - PREDICTION_MARGIN)
        high = int(predicted_score + PREDICTION_MARGIN)
        
        bat_c = 'green' if bat_factor >= 1 else 'red'
        bowl_c = 'green' if bowl_factor >= 1 else 'red'
        
        html = f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
            <h2 style="color: #333; margin:0;">🔮 Prediction: {batting_team} to score</h2>
            <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                <div style="text-align: center;"><h3>🏟️ Venue</h3><span style="font-size:18px">{venue_avg}</span></div>
                <div style="text-align: center;"><h3>🏏 Bat</h3><span style="font-size:18px; color:{bat_c}">{round(bat_factor, 2)}x</span></div>
                <div style="text-align: center;"><h3>⚡ Bowl</h3><span style="font-size:18px; color:{bowl_c}">{round(bowl_factor, 2)}x</span></div>
            </div>
            <div style="text-align: center; margin-top: 20px; border-top: 1px solid #ccc; padding-top: 10px;">
                <h1 style="color: #2c3e50; margin:0;">{low} - {high}</h1>
                <small>(Confidence: {sample_size} matches)</small>
            </div>
        </div>
        """
        display(HTML(html))