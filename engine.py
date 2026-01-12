import pandas as pd
import numpy as np
import difflib  # <--- 🧠 THE BRAIN IMPLANT (Fuzzy Logic)
import re
from IPython.display import display
from venues import VENUE_MAP  # <--- Imports our 'Source of Truth'
from venues import get_venue_aliases

class CricketAnalyzer:
    """
    The Brain of the Operation. 🧠
    Now equipped with Fuzzy Logic to auto-correct messy venue names.
    """

    # =================================================================================
    # 1. INITIALIZATION & DATA LOADING
    # =================================================================================
    def __init__(self, filepath):
            # 🧠 UNDERSTANDING & CONTEXT:
            # The Boot Sequence.
            # 1. Load Data (Matches & Players).
            # 2. GLOBAL SORT: Ensures time-series logic (Form/Trends) works correctly.
            # 3. Build Stats (Runs/Wickets).
            # 4. Fix Ambiguities & Standardize Venues.
            
            print(f"⚙️ Initializing Smart Engine...")
            print(f"📂 Loading Database: {filepath}")
        
            # 1. Load Match Data
            self.raw_df = pd.read_csv(filepath, low_memory=False)
            self.raw_df.columns = self.raw_df.columns.str.strip().str.lower()
            self.raw_df['start_date'] = pd.to_datetime(self.raw_df['start_date'], errors='coerce')
            self.raw_df['year'] = self.raw_df['start_date'].dt.year
            
            # 🚨 CRITICAL FIX: GLOBAL SORT BY DATE
            # This ensures that whenever we use .tail(5) later, we get the ACTUAL most recent matches.
            self.raw_df = self.raw_df.sort_values(['start_date', 'match_id'])
            
            print(f"   Raw Data: {len(self.raw_df)} balls loaded (Sorted by Date).")

            # 👇 2. NEW: Load Player Stats & Metadata
            try:
                self.player_df = pd.read_csv('data/processed_player_stats.csv')
                self.meta_df = pd.read_csv('data/player_metadata.csv')
                print(f"✅ Player Data Loaded: {len(self.player_df)} stats rows, {len(self.meta_df)} players mapped.")
            except FileNotFoundError:
                self.player_df = pd.DataFrame()
                self.meta_df = pd.DataFrame()
                print("⚠️ Player Data Missing. Please run the processor script.")
            
            # --- BUILD MATCH SUMMARY ---
            self._create_match_summary()
            
            # --- STEP 1: RESOLVE AMBIGUITIES (Logic based) ---
            # Disambiguates "The Oval" before we rename everything.
            self._fix_ambiguous_venues()
            
            # --- 🧠 STEP 2: SMART VENUE STANDARDIZATION (Fuzzy Logic) ---
            # This replaces the old simple replace. It finds the best match for every unique name.
            self._smart_standardize_venues()
        
            print(f"✅ Engine Ready! Condensed into {len(self.match_df)} unique matches.")
            print(f"   Date Range: {self.match_df['year'].min()} to {self.match_df['year'].max()}")

    def _create_match_summary(self):
            print("   🔨 Building Match Summary (Filtering Super Overs)...")
            
            wicket_col = 'is_wicket' if 'is_wicket' in self.raw_df.columns else 'player_dismissed'
            agg_func_wicket = 'sum' if wicket_col == 'is_wicket' else 'count'
            
            wides_col = 'wides' if 'wides' in self.raw_df.columns else 'wide'
            noballs_col = 'noballs' if 'noballs' in self.raw_df.columns else 'no_ball'
            
            if wides_col in self.raw_df.columns:
                self.raw_df[wides_col] = self.raw_df[wides_col].fillna(0)
            if noballs_col in self.raw_df.columns:
                self.raw_df[noballs_col] = self.raw_df[noballs_col].fillna(0)

            if wides_col in self.raw_df.columns and noballs_col in self.raw_df.columns:
                self.raw_df['is_legal_ball'] = (
                    (self.raw_df[wides_col] == 0) & 
                    (self.raw_df[noballs_col] == 0)
                ).astype(int)
            else:
                self.raw_df['is_legal_ball'] = 1 

            innings_stats = self.raw_df.groupby(['match_id', 'innings']).agg({
                'runs_off_bat': 'sum', 
                'extras': 'sum',
                'is_legal_ball': 'sum', 
                wicket_col: agg_func_wicket 
            }).reset_index()
            
            innings_stats = innings_stats[innings_stats['innings'].isin([1, 2])]
            
            innings_stats.rename(columns={
                wicket_col: 'wickets', 
                'is_legal_ball': 'legal_balls'
            }, inplace=True)
            
            innings_stats['total_score'] = innings_stats['runs_off_bat'] + innings_stats['extras']
            
            def format_score(row):
                overs = row['legal_balls'] // 6
                balls = row['legal_balls'] % 6
                return f"{int(row['total_score'])}/{int(row['wickets'])} ({overs}.{balls})"

            innings_stats['score_display'] = innings_stats.apply(format_score, axis=1)

            scores_pivot = innings_stats.pivot(index='match_id', columns='innings', values='total_score').reset_index()
            scores_pivot.rename(columns={1: 'score_inn1', 2: 'score_inn2'}, inplace=True)
            scores_pivot.fillna(0, inplace=True)
            
            balls_pivot = innings_stats.pivot(index='match_id', columns='innings', values='legal_balls').reset_index()
            balls_pivot.rename(columns={1: 'balls_inn1', 2: 'balls_inn2'}, inplace=True)
            balls_pivot.fillna(0, inplace=True)
            
            wickets_pivot = innings_stats.pivot(index='match_id', columns='innings', values='wickets').reset_index()
            wickets_pivot.rename(columns={1: 'wickets_inn1', 2: 'wickets_inn2'}, inplace=True)
            wickets_pivot.fillna(0, inplace=True)

            display_pivot = innings_stats.pivot(index='match_id', columns='innings', values='score_display').reset_index()
            display_pivot.rename(columns={1: 'display_inn1', 2: 'display_inn2'}, inplace=True)
            display_pivot.fillna("DNB", inplace=True)
            
            cols_to_keep = ['match_id', 'season', 'year', 'start_date', 'venue', 'batting_team', 'bowling_team', 'winner']
            if 'method' in self.raw_df.columns: cols_to_keep.append('method')

            meta_data = self.raw_df.drop_duplicates(subset='match_id')[cols_to_keep].copy()
            if 'method' not in meta_data.columns: meta_data['method'] = np.nan
                
            meta_data.rename(columns={'batting_team': 'team_bat_1', 'bowling_team': 'team_bat_2'}, inplace=True)
            
            self.match_df = pd.merge(meta_data, scores_pivot, on='match_id', how='left')
            self.match_df = pd.merge(self.match_df, balls_pivot, on='match_id', how='left')
            self.match_df = pd.merge(self.match_df, wickets_pivot, on='match_id', how='left')
            self.match_df = pd.merge(self.match_df, display_pivot, on='match_id', how='left')
            
            self.match_df.fillna({
                'score_inn1': 0, 'score_inn2': 0, 
                'balls_inn1': 0, 'balls_inn2': 0,
                'wickets_inn1': 0, 'wickets_inn2': 0,
                'display_inn1': 'N/A', 'display_inn2': 'N/A'
        }, inplace=True)

            self.match_df['is_defended'] = self.match_df['winner'] == self.match_df['team_bat_1']
            self.match_df['is_chased'] = self.match_df['winner'] == self.match_df['team_bat_2']

    # =================================================================================
    # 2. VENUE STANDARDIZATION & CLEANING
    # =================================================================================
    def _fix_ambiguous_venues(self):
        print("   🔧 Auto-Fixing Ambiguous Venues...")
        
    def fix_logic(row):
            venue = row['venue']
            if venue == 'The Oval':
                t1 = row['team_bat_1']
                t2 = row['team_bat_2']
                month = pd.to_datetime(row['start_date']).month
                if 'West Indies' in [t1, t2] and month in [10, 11, 12, 1, 2, 3, 4, 5]:
                    return 'Kensington Oval, Barbados'
                elif 'New Zealand' in [t1, t2] and month in [11, 12, 1, 2, 3]:
                    return 'University Oval, Dunedin'
                else:
                    return 'The Oval, London'
            return venue

            self.match_df['venue'] = self.match_df.apply(fix_logic, axis=1)
            print("   ✅ Venue Ambiguities Resolved.")

    def _smart_standardize_venues(self):
        """
        The Permanent Solution. 🧠
        1. Identifies every unique raw venue name.
        2. Clean Match: Removes punctuation.
        3. Substring Match: Checks if a known venue is HIDDEN inside the raw name.
        4. Fuzzy Match: The final safety net for typos.
        """
        print("   🧠 Applying Smart Venue Matching (Clean -> Substring -> Fuzzy)...")
        
        # 1. Get all unique dirty names
        unique_raw_venues = self.match_df['venue'].unique()
        venue_corrections = {}
        
        # 2. Pre-process VENUE_MAP keys for cleaner matching
        # Map: "r premadasa stadium" -> "R. Premadasa Stadium" (Original Key)
        clean_map_keys = {self._clean_string(k): k for k in VENUE_MAP.keys()}
        
        for raw_name in unique_raw_venues:
            if not isinstance(raw_name, str): continue
            
            # A. Exact Match Check (Fastest)
            if raw_name in VENUE_MAP:
                venue_corrections[raw_name] = VENUE_MAP[raw_name]
                continue
            
            clean_raw = self._clean_string(raw_name)
            
            # B. Clean Match Check (Ignores punctuation/case)
            if clean_raw in clean_map_keys:
                original_key = clean_map_keys[clean_raw]
                venue_corrections[raw_name] = VENUE_MAP[original_key]
                continue

            # C. Substring Match (The "Colombo" Fix) 🕵️‍♂️
            best_substring_match = None
            max_len = 0
            
            for key_clean, original_key in clean_map_keys.items():
                if len(key_clean) > 4 and key_clean in clean_raw:
                    if len(key_clean) > max_len:
                        max_len = len(key_clean)
                        best_substring_match = original_key
            
            if best_substring_match:
                venue_corrections[raw_name] = VENUE_MAP[best_substring_match]
                continue
            
            # D. Fuzzy Match (The Safety Net)
            matches = difflib.get_close_matches(raw_name, VENUE_MAP.keys(), n=1, cutoff=0.80)
            
            if matches:
                best_match = matches[0]
                master_id = VENUE_MAP[best_match]
                venue_corrections[raw_name] = master_id
            else:
                venue_corrections[raw_name] = raw_name

        # 3. Apply the Map
        self.match_df['venue'] = self.match_df['venue'].map(venue_corrections).fillna(self.match_df['venue'])
        
        unique_venues = self.match_df['venue'].nunique()
        print(f"   ✅ Venues Standardized! Total Unique Grounds: {unique_venues}")

    def _clean_string(self, s):
        if not isinstance(s, str): return str(s)
        s = re.sub(r'[^\w\s]', '', s) # Remove punctuation
        return s.lower().strip()

    def _apply_smart_filters(self, df):
        """
        Quality Control 🛡️
        Tags matches as 'Included' or 'Excluded'.
        """
        # 1. Default Status
        df['status'] = '✅ Included'
        
        # 2. Explicit D/L or No Result
        if 'method' in df.columns: 
            df.loc[df['method'].notna(), 'status'] = '☔ Excluded (Rain/DL)'
            
        df.loc[df['winner'].isin(['No Result', np.nan]), 'status'] = '☔ Excluded (No Result)'
        
        # 3. Short 1st Innings
        mask_short_inn1 = (df['balls_inn1'] < 270) & (df['wickets_inn1'] < 10)
        df.loc[mask_short_inn1, 'status'] = '☔ Excluded (Short 1st)'
        
        # 4. Short 2nd Innings
        natural_win = (df['winner'] == df['team_bat_2']) & (df['score_inn2'] > df['score_inn1'])
        mask_short_inn2 = (df['balls_inn2'] < 270) & (df['wickets_inn2'] < 10) & (~natural_win)
        
        df.loc[mask_short_inn2, 'status'] = '☔ Excluded (Short 2nd)'
        
        return df

    # =================================================================================
    # 3. CORE LOGIC HELPERS
    # =================================================================================
    def _get_clean_scores(self, row):
        """
        HELPER: Checks if a match row is valid for Average Calculations.
        """
        s1, w1, b1 = row['score_inn1'], row['wickets_inn1'], row['balls_inn1']
        s2, w2, b2 = row['score_inn2'], row['wickets_inn2'], row['balls_inn2']
        
        valid_1 = (w1 >= 10) or (b1 >= 270)
        clean_s1 = s1 if valid_1 else None
        
        natural_chase = (s2 > s1)
        valid_2 = (w2 >= 10) or (b2 >= 270) or natural_chase
        clean_s2 = s2 if valid_2 else None
        
        return clean_s1, clean_s2

    def _calculate_team_stats(self, df, team_name, is_home_analysis=False):
        """
        Internal: Calculates detailed stats for a specific team.
        """
        def get_safe_int(series, stat_type='max'):
            if series.empty: return "-"
            val = series.max() if stat_type == 'max' else series.min()
            if pd.isna(val) or val == np.inf or val == -np.inf:
                return "-"
            return int(val)

        # 1. Batting 1st Filter
        if is_home_analysis and team_name == 'Visitors':
            bat1 = df[df['team_bat_1'] != df['home_team_ref']]
        else:
            bat1 = df[df['team_bat_1'] == team_name]
            
        avg_1st = self._get_avg_with_count(bat1, 'score_inn1')
        high_1st = get_safe_int(bat1['score_inn1'], 'max')
        low_1st = get_safe_int(bat1['score_inn1'], 'min')
        
        # Batting 1st & Won (Defended)
        if 'is_defended' in bat1.columns:
            bat1_win = bat1[bat1['is_defended'] == True]
        else:
            bat1_win = bat1[bat1['winner'] == bat1['team_bat_1']]

        avg_1st_win = self._get_avg_with_count(bat1_win, 'score_inn1')
        low_defended = get_safe_int(bat1_win['score_inn1'], 'min')
        
        # 2. Chasing Filter
        if is_home_analysis and team_name == 'Visitors':
            chase = df[df['team_bat_2'] != df['home_team_ref']]
        else:
            chase = df[df['team_bat_2'] == team_name]
            
        avg_2nd = self._get_avg_with_count(chase, 'score_inn2')
        
        # Chasing & Won
        if 'is_chased' in chase.columns:
            chase_win = chase[chase['is_chased'] == True]
        else:
            chase_win = chase[chase['winner'] == chase['team_bat_2']]

        high_chased = get_safe_int(chase_win['score_inn2'], 'max')
        avg_succ_chase = self._get_avg_with_count(chase_win, 'score_inn2')
        
        # Chasing & Lost
        if 'is_chased' in chase.columns:
            chase_loss = chase[chase['is_chased'] == False]
        else:
            chase_loss = chase[chase['winner'] != chase['team_bat_2']]
            
        avg_fail_chase = self._get_avg_with_count(chase_loss, 'score_inn2')
        
        return {
            'avg_1st': avg_1st, 
            'avg_1st_win': avg_1st_win, 
            'high_1st': high_1st, 
            'low_1st': low_1st, 
            'low_defended': low_defended,
            'avg_2nd': avg_2nd, 
            'high_chased': high_chased, 
            'avg_succ': avg_succ_chase, 
            'avg_fail': avg_fail_chase
        }

    def _calculate_smart_projection(self, player, role, venue_name):
        """
        🔮 LAW OF AVERAGES ENGINE
        Calculates a 'Smart Projection' using weighted mean reversion.
        Formula: 50% Recent Form + 30% Venue History + 20% Career Class
        """
        # 1. Get Career Stats (The Anchor)
        p_stats = self.player_df[(self.player_df['player'] == player) & (self.player_df['role'] == role)]
        
        if p_stats.empty:
            return 0, "New Player"

        # Career Average
        car_runs = p_stats[p_stats['context'] == 'vs_team']['runs'].sum()
        car_outs = p_stats[p_stats['context'] == 'vs_team']['dismissals'].sum()
        car_avg = (car_runs / car_outs) if car_outs > 0 else car_runs
        
        # 2. Get Venue Stats (The Context)
        ven_stats = p_stats[(p_stats['context'] == 'at_venue') & (p_stats['opponent'] == venue_name)]
        if not ven_stats.empty:
            ven_runs = ven_stats['runs'].sum()
            ven_outs = ven_stats['dismissals'].sum()
            ven_avg = (ven_runs / ven_outs) if ven_outs > 0 else ven_runs
        else:
            ven_avg = car_avg # Fallback to career if no venue data
            
        # 3. Get Recent Form (The Momentum)
        # We look at the raw data for the last 5 innings
        recent_avg = car_avg # Default fallback
        try:
            if role == 'batting':
                # Get last 5 scores
                p_raw = self.raw_df[self.raw_df['striker'] == player].drop_duplicates(subset=['match_id'])
                last_5 = p_raw.tail(5)
                if not last_5.empty:
                    runs_5 = 0
                    outs_5 = 0
                    for m_id in last_5['match_id'].unique():
                        m_data = self.raw_df[(self.raw_df['match_id'] == m_id) & (self.raw_df['striker'] == player)]
                        runs_5 += m_data['runs_off_bat'].sum()
                        if m_data['wicket_type'].notna().any(): outs_5 += 1
                    recent_avg = (runs_5 / outs_5) if outs_5 > 0 else runs_5
                    
            elif role == 'bowling':
                # Get last 5 matches wickets
                p_raw = self.raw_df[self.raw_df['bowler'] == player].drop_duplicates(subset=['match_id'])
                last_5 = p_raw.tail(5)
                if not last_5.empty:
                    wkts_5 = 0
                    matches_5 = len(last_5)
                    for m_id in last_5['match_id'].unique():
                        m_data = self.raw_df[(self.raw_df['match_id'] == m_id) & (self.raw_df['bowler'] == player)]
                        wicket_types = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
                        wkts_5 += m_data['wicket_type'].isin(wicket_types).sum()
                    
                    # For bowlers, we predict Wickets per Match
                    recent_avg = wkts_5 / matches_5
                    # Adjust historical avgs to 'Wickets per Match' for consistent weighing
                    # (Career Avg is usually runs/wkt, so we need Wkts/Match)
                    c_inns = p_stats[p_stats['context'] == 'vs_team']['innings'].sum()
                    c_wkts = p_stats[p_stats['context'] == 'vs_team']['dismissals'].sum()
                    car_avg = c_wkts / c_inns if c_inns > 0 else 0
                    
                    if not ven_stats.empty:
                         v_inns = ven_stats['innings'].sum()
                         v_wkts = ven_stats['dismissals'].sum()
                         ven_avg = v_wkts / v_inns if v_inns > 0 else 0
                    else:
                        ven_avg = car_avg

        except:
            pass

        # 4. THE WEIGHTED FORMULA
        # 50% Form + 30% Venue + 20% Career
        weighted_projection = (0.5 * recent_avg) + (0.3 * ven_avg) + (0.2 * car_avg)
        
        return round(weighted_projection, 1), "OK"
    
    # =================================================================================
    # 4. REPORTING & ANALYSIS METHODS
    # =================================================================================

    
    def analyze_home_fortress(self, stadium_name, home_team, opp_team='All', years_back=10):
        """
        TRADING LAYER 2: "The Fortress Check"
        """
        stadium_id = stadium_name
        
        # 1. Direct check or Key Check
        if stadium_name not in VENUE_MAP.values():
            for k, v in VENUE_MAP.items():
                if k.lower() in stadium_name.lower():
                    stadium_id = v
                    break
        
        self.match_df['start_date'] = pd.to_datetime(self.match_df['start_date'])
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        visitor_label = opp_team if opp_team != 'All' else "Visitors"
        vs_text = f"vs {visitor_label}"
        print(f"\n🏰 FORTRESS CHECK: {home_team} {vs_text} at {stadium_id}")
        print(f"📅 Analyzing data from the last {years_back} years...")
        
        venue_matches = self.match_df[
            (self.match_df['venue'] == stadium_id) &
            (self.match_df['start_date'] >= cutoff_date)
        ].copy()
        
        df = venue_matches[(venue_matches['team_bat_1'] == home_team) | (venue_matches['team_bat_2'] == home_team)].copy()
        
        if opp_team != 'All':
            df = df[(df['team_bat_1'] == opp_team) | (df['team_bat_2'] == opp_team)].copy()
        
        if df.empty:
            print(f"❌ No matches found for {home_team} {vs_text} at this venue ID.")
            return

        # RAIN FILTER: MASK INVALID SCORES AS NAN
        for index, row in df.iterrows():
            s1 = row.get('score_inn1', 0)
            w1 = row.get('wickets_inn1', 0)
            b1 = row.get('balls_inn1', 0)
            
            s2 = row.get('score_inn2', 0)
            w2 = row.get('wickets_inn2', 0)
            b2 = row.get('balls_inn2', 0)
            
            winner = row['winner']
            
            valid_1 = (w1 >= 10) or (b1 >= 270)
            natural_chase = (winner == row['team_bat_2']) and (s2 > s1)
            valid_2 = (w2 >= 10) or (b2 >= 270) or natural_chase
            
            if not valid_1: 
                df.at[index, 'score_inn1'] = np.nan
            if not valid_2: 
                df.at[index, 'score_inn2'] = np.nan
                
            if valid_1 and valid_2: 
                df.at[index, 'status'] = '✅ Included'
            elif valid_1 and not valid_2: 
                df.at[index, 'status'] = '⚠️ Inn1 Only'
            else: 
                df.at[index, 'status'] = '☔ Excluded'

        self._build_and_display_report(df, home_team, visitor_label, f"FORTRESS REPORT ({vs_text})", is_venue_mode=True)

    def analyze_venue_phases(self, stadium_id, home_team=None, away_team=None):
        """
        TRADING LAYER 3: "Phase Analysis Engine" 🕒
        """
        import os
        
        # 1. DATA LOADING
        file_path = 'data/processed_phase_stats.csv'
        if not os.path.exists(file_path):
            print("❌ Error: 'processed_phase_stats.csv' not found. Please run the Setup Script.")
            return
            
        phase_df = pd.read_csv(file_path)
        
        # 2. SMART VENUE RESOLUTION
        valid_aliases = [k for k, v in VENUE_MAP.items() if v == stadium_id]
        valid_aliases.append(stadium_id)
        
        search_terms = [x.lower() for x in valid_aliases]
        venue_stats = phase_df[phase_df['venue'].str.lower().isin(search_terms)].copy()
        
        if venue_stats.empty:
            location_part = stadium_id.split('_')[-1].lower()
            if len(location_part) > 3:
                venue_stats = phase_df[phase_df['venue'].str.lower().str.contains(location_part)]

        if venue_stats.empty:
            print(f"❌ No phase data found for venue ID: '{stadium_id}'")
            return
            
        target_venue = venue_stats['venue'].iloc[0]
        print(f"\n🕒 PHASE ANALYSIS: {target_venue.upper()}")
        print(f"📅 Sample Size: {len(venue_stats)} Innings (Modern Era Only)")
        
        # 3. VENUE METRICS
        v_summary = venue_stats.groupby('innings').agg({
            'pp_runs': 'mean', 'pp_wkts': 'mean',
            'mid_runs': 'mean', 'mid_wkts': 'mean',
            'dth_runs': 'mean', 'dth_wkts': 'mean'
        }).round(1)

        # --- NEW CALCULATION START ---
        # Calculate Total Projected Score for 1st Innings
        p1_runs = v_summary.loc[1, 'pp_runs'] if 1 in v_summary.index else 0
        m1_runs = v_summary.loc[1, 'mid_runs'] if 1 in v_summary.index else 0
        d1_runs = v_summary.loc[1, 'dth_runs'] if 1 in v_summary.index else 0
        projected_score = int(p1_runs + m1_runs + d1_runs)
        # --- NEW CALCULATION END ---
        
        print("-" * 75)
        print(f"🏟️ PROJECTED PAR SCORE (1st Innings): {projected_score} Runs")
        print(f"{'PHASE':<18} | {'1st INNINGS (Venue Avg)':<25} | {'2nd INNINGS (Venue Avg)':<25}")
        print("-" * 75)
        
        phases = [("POWERPLAY (1-10)", 'pp'), ("MIDDLE (11-40)", 'mid'), ("DEATH (41-50)", 'dth')]
        
        for name, p in phases:
            r1 = v_summary.loc[1, f'{p}_runs'] if 1 in v_summary.index else 0
            w1 = v_summary.loc[1, f'{p}_wkts'] if 1 in v_summary.index else 0
            r2 = v_summary.loc[2, f'{p}_runs'] if 2 in v_summary.index else 0
            w2 = v_summary.loc[2, f'{p}_wkts'] if 2 in v_summary.index else 0
            
            print(f"{name:<18} | 🏏 {r1} / {w1} wkts        | 🏏 {r2} / {w2} wkts")
            
        print("-" * 75)

        # 4. TEAM HABITS & COMPARISON
        if home_team and away_team and away_team != 'All':
            print(f"\n⚔️ TEAM HABITS (Global Stats Since 2015)")
            
            home_stats = phase_df[phase_df['team'] == home_team]
            away_stats = phase_df[phase_df['team'] == away_team]
            
            if home_stats.empty or away_stats.empty:
                print("⚠️ Insufficient data for team comparison.")
                return

            # SCENARIO 1: BAT FIRST
            h_avg_1 = home_stats[home_stats['innings'] == 1].mean(numeric_only=True)
            a_avg_1 = away_stats[away_stats['innings'] == 1].mean(numeric_only=True)
            
            print(f"\n📉 SCENARIO 1: BAT FIRST (Setting Target)")
            print("-" * 75)
            print(f"{'METRIC':<20} | {home_team:<20} | {away_team:<20} | {'DIFF':<10}")
            print("-" * 75)
            
            for col, label in [('pp_runs', 'Avg PP Score'), ('mid_runs', 'Avg Mid Score'), ('dth_runs', 'Avg Death Score')]:
                val_h = h_avg_1.get(col, 0)
                val_a = a_avg_1.get(col, 0)
                diff = round(val_h - val_a, 1)
                marker = "✅" if diff > 0 else "🔻"
                print(f"{label:<20} | {val_h:.1f} runs            | {val_a:.1f} runs            | {marker} {abs(diff)}")

            # SCENARIO 2: CHASING
            h_avg_2 = home_stats[home_stats['innings'] == 2].mean(numeric_only=True)
            a_avg_2 = away_stats[away_stats['innings'] == 2].mean(numeric_only=True)

            print(f"\n📉 SCENARIO 2: CHASING (Target Dependent)")
            print(f"⚠️ NOTE: Hiding Mid/Death Runs. Showing WICKETS to spot 'Collapse Risk'.")
            print("-" * 75)
            print(f"{'METRIC':<20} | {home_team:<20} | {away_team:<20} | {'DIFF':<10}")
            print("-" * 75)
            
            h_pp = h_avg_2.get('pp_runs', 0)
            a_pp = a_avg_2.get('pp_runs', 0)
            diff_pp = round(h_pp - a_pp, 1)
            marker_pp = "✅" if diff_pp > 0 else "🔻"
            print(f"{'Avg PP Score':<20} | {h_pp:.1f} runs            | {a_pp:.1f} runs            | {marker_pp} {abs(diff_pp)}")
            
            for col, label in [('mid_wkts', 'Avg Mid Wickets'), ('dth_wkts', 'Avg Death Wickets')]:
                val_h = h_avg_2.get(col, 0)
                val_a = a_avg_2.get(col, 0)
                diff = round(val_h - val_a, 1)
                marker = "✅" if diff < 0 else "🔻"
                print(f"{label:<20} | {val_h:.1f} wkts            | {val_a:.1f} wkts            | {marker} {abs(diff)}")
                
            print("-" * 75)
            
            # 5. ALGO-TRADING ALERTS
            venue_pp_1 = v_summary.loc[1, 'pp_runs'] if 1 in v_summary.index else 0
            
            h_pp_1 = h_avg_1.get('pp_runs', 0)
            if h_pp_1 > venue_pp_1 + 5:
                print(f"🚀 EDGE: {home_team} (1st Inn) outscores this venue avg ({venue_pp_1}). BACK Powerplay.")
            
            h_wkts_chase = h_avg_2.get('mid_wkts', 0)
            if h_wkts_chase > 3.0:
                print(f"⚠️ RISK: {home_team} averages {h_wkts_chase:.1f} wickets lost in Middle Overs chasing. LAY Stability.")

    def analyze_venue_bias(self, stadium_name):
        """
        Table 6: The 'Toss Bias' Report. 🪙
        """
        print(f"\n🪙 TOSS BIAS REPORT: {stadium_name}")
        
        if not self.match_df[self.match_df['venue'] == stadium_name].empty:
            venue_id = stadium_name
        else:
            all_venues = self.match_df['venue'].unique().astype(str)
            matches = [v for v in all_venues if stadium_name.lower() in v.lower()]
            
            if matches:
                venue_id = matches[0]
                print(f"🔎 Mapped '{stadium_name}' to -> '{venue_id}'")
            else:
                print(f"❌ Venue '{stadium_name}' not found in database.")
                return

        venue_matches = self.match_df[self.match_df['venue'] == venue_id].copy()
        clean_df = self._apply_smart_filters(venue_matches)
        valid_matches = clean_df[clean_df['status'] == '✅ Included']
        
        if valid_matches.empty:
            print("❌ Not enough valid matches to analyze toss bias.")
            return

        total_games = len(valid_matches)
        
        bat1_wins = len(valid_matches[valid_matches['winner'] == valid_matches['team_bat_1']])
        chase_wins = len(valid_matches[valid_matches['winner'] == valid_matches['team_bat_2']])
        
        bat1_pct = int((bat1_wins / total_games) * 100)
        chase_pct = int((chase_wins / total_games) * 100)
        
        avg_1st = self._get_avg_with_count(valid_matches, 'score_inn1')
        avg_2nd = self._get_avg_with_count(valid_matches, 'score_inn2')
        
        bias = "NEUTRAL ⚖️"
        if bat1_pct >= 55: bias = "BAT FIRST 🏏"
        elif chase_pct >= 55: bias = "BOWL FIRST 🥎"
        
        print(f"🏟️ Matches Analyzed: {total_games}")
        print(f"📊 Bias Verdict: {bias}")
        print("-" * 40)
        
        data = [
            {"Metric": "Win % Batting 1st", "Value": f"{bat1_pct}% ({bat1_wins})"},
            {"Metric": "Win % Chasing", "Value": f"{chase_pct}% ({chase_wins})"},
            {"Metric": "Avg 1st Innings Score", "Value": avg_1st},
            {"Metric": "Avg 2nd Innings Score", "Value": avg_2nd},
        ]
        
        df_display = pd.DataFrame(data)
        display(df_display.style.hide(axis='index'))

    def analyze_global_h2h(self, home_team, opp_team, years_back=5):
        """
        TRADING LAYER 3: "Global Rivalry"
        """
        self.match_df['start_date'] = pd.to_datetime(self.match_df['start_date'])
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        print(f"\n🌍 GLOBAL H2H CHECK: {home_team} vs {opp_team}")
        print(f"📅 Analyzing data from the last {years_back} years (All Venues)...")
        
        mask = (
            ((self.match_df['team_bat_1'] == home_team) & (self.match_df['team_bat_2'] == opp_team)) |
            ((self.match_df['team_bat_1'] == opp_team) & (self.match_df['team_bat_2'] == home_team))
        ) & (self.match_df['start_date'] >= cutoff_date)
        
        df = self.match_df[mask].copy()
        
        if df.empty:
            print(f"❌ No global matches found between {home_team} and {opp_team}.")
            return

        df = self._apply_smart_filters(df)
        self._build_and_display_report(df, home_team, opp_team, f"GLOBAL RIVALRY REPORT", is_venue_mode=False)

    def analyze_country_h2h(self, home_team, opp_team, country_name, years_back=10):
        """
        TRADING LAYER 4: "Host Country Analysis"
        """
        self.match_df['start_date'] = pd.to_datetime(self.match_df['start_date'])
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        print(f"\n🗺️ COUNTRY CHECK: {home_team} vs {opp_team} in {country_name.upper()}")
        print(f"📅 Period: Last {years_back} Years")
        
        country_map = {
            'India': ['India', 'IND_', 'Wankhede', 'Mumbai', 'Brabourne', 'Eden Gardens', 'Kolkata', 'Chidambaram', 'Chepauk', 'Chennai', 'Chinnaswamy', 'Bangalore', 'Bengaluru', 'Narendra Modi', 'Motera', 'Ahmedabad', 'Arun Jaitley', 'Kotla', 'Delhi', 'Rajiv Gandhi', 'Hyderabad', 'HPCA', 'Dharamshala', 'Bindra', 'Mohali', 'Holkar', 'Indore', 'Saurashtra', 'Rajkot', 'Vidarbha', 'Nagpur', 'JSCA', 'Ranchi', 'Barabati', 'Cuttack', 'Raipur', 'Guwahati', 'Pune', 'Barsapara', 'Greenfield', 'Trivandrum', 'Ekana', 'Lucknow', 'Sawai Mansingh', 'Jaipur', 'Green Park', 'Kanpur', 'Visakhapatnam'],
            'Australia': ['Australia', 'AUS_', 'Melbourne', 'Sydney', 'Gabba', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Canberra', 'Darwin', 'Townsville', 'Carrara', 'Cairns'],
            'England': ['England', 'ENG_', 'Lord\'s', 'Oval', 'London', 'Edgbaston', 'Birmingham', 'Old Trafford', 'Manchester', 'Headingley', 'Leeds', 'Trent Bridge', 'Nottingham', 'Rose Bowl', 'Southampton', 'Ageas', 'Hampshire', 'Utilita', 'Sophia Gardens', 'Cardiff', 'Riverside', 'Durham', 'Bristol'],
            'South Africa': ['South Africa', 'SA_', 'Wanderers', 'Johannesburg', 'Centurion', 'Pretoria', 'Kingsmead', 'Durban', 'Port Elizabeth', 'Gqeberha', 'Newlands', 'Cape Town', 'Paarl', 'Bloemfontein', 'Potchefstroom'],
            'New Zealand': ['New Zealand', 'NZ_', 'Auckland', 'Hamilton', 'Wellington', 'Christchurch', 'Dunedin', 'Napier', 'Nelson', 'Mount Maunganui', 'Queenstown'],
            'Sri Lanka': ['Sri Lanka', 'SL_', 'Colombo', 'Galle', 'Kandy', 'Dambulla', 'Hambantota'],
            'West Indies': ['West Indies', 'WI_', 'Barbados', 'Bridgetown', 'Trinidad', 'Port of Spain', 'Guyana', 'Georgetown', 'Jamaica', 'Kingston', 'Antigua', 'North Sound', 'St Lucia', 'Gros Islet', 'Grenada', 'St George\'s', 'Dominica', 'Roseau', 'St Kitts', 'Basseterre', 'St Vincent', 'Kingstown'],
            'Pakistan': ['Pakistan', 'PAK_', 'Lahore', 'Karachi', 'Rawalpindi', 'Multan', 'Faisalabad'],
            'Bangladesh': ['Bangladesh', 'BAN_', 'Dhaka', 'Mirpur', 'Chattogram', 'Chittagong', 'Sylhet'],
            'UAE': ['UAE', 'United Arab Emirates', 'UAE_', 'Dubai', 'Sharjah', 'Abu Dhabi']
        }
        
        keywords = country_map.get(country_name, [country_name])
        pattern = '|'.join([k for k in keywords]) 
        venue_mask = self.match_df['venue'].str.contains(pattern, case=False, na=False, regex=True)
        
        matchup_mask = (
            ((self.match_df['team_bat_1'] == home_team) & (self.match_df['team_bat_2'] == opp_team)) |
            ((self.match_df['team_bat_1'] == opp_team) & (self.match_df['team_bat_2'] == home_team))
        ) & (self.match_df['start_date'] >= cutoff_date)
        
        df = self.match_df[venue_mask & matchup_mask].copy()
        
        if df.empty:
            print(f"❌ No matches found between {home_team} and {opp_team} in {country_name}.")
            return

        df = self._apply_smart_filters(df)
        self._build_and_display_report(df, home_team, opp_team, f"HOST COUNTRY REPORT ({country_name})", is_venue_mode=False)

    def analyze_home_dominance(self, home_team, years_back=10):
        """
        The "Hostile Host" Report. 🦁
        Shows Home Team vs ALL touring teams.
        """
        print(f"\n🦁 HOME DOMINANCE REPORT: {home_team} in Home Conditions")
        print(f"📅 Period: Last {years_back} Years")
        
        country_codes = {
            'India': 'IND_', 'England': 'ENG_', 'Australia': 'AUS_',
            'South Africa': 'SA_', 'New Zealand': 'NZ_', 'Sri Lanka': 'SL_',
            'West Indies': 'WI_', 'Pakistan': 'PAK_', 'Bangladesh': 'BAN_',
            'Afghanistan': 'AFG_', 'Zimbabwe': 'ZIM_', 'Ireland': 'IRE_'
        }
        
        if home_team not in country_codes:
            print(f"❌ Could not auto-detect country code for {home_team}.")
            return

        code = country_codes[home_team]
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        home_matches = self.match_df[
            (self.match_df['venue'].str.startswith(code)) &
            ((self.match_df['team_bat_1'] == home_team) | (self.match_df['team_bat_2'] == home_team)) &
            (self.match_df['start_date'] >= cutoff_date)
        ].copy()
        
        clean_df = self._apply_smart_filters(home_matches)
        valid_matches = clean_df[clean_df['status'] == '✅ Included']
        
        if home_matches.empty:
            print(f"❌ No home matches found for {home_team} in the last {years_back} years.")
            return

        def get_opponent(row):
            return row['team_bat_2'] if row['team_bat_1'] == home_team else row['team_bat_1']

        clean_df['opponent'] = clean_df.apply(get_opponent, axis=1)
        valid_matches = valid_matches.copy()
        valid_matches['opponent'] = valid_matches.apply(get_opponent, axis=1)
        
        opponents = clean_df['opponent'].unique()
        stats_data = []
        
        for opp in opponents:
            vs_opp_full = clean_df[clean_df['opponent'] == opp]
            vs_opp_clean = valid_matches[valid_matches['opponent'] == opp]
            
            matches = len(vs_opp_full)
            wins = len(vs_opp_full[vs_opp_full['winner'] == home_team])
            losses = len(vs_opp_full[vs_opp_full['winner'] == opp])
            tie_nr = matches - wins - losses
            
            decisive = matches - tie_nr
            win_pct = int((wins / decisive) * 100) if decisive > 0 else 0
            
            form = self._get_form_guide(vs_opp_full, home_team)
            h_avg = self._get_avg_with_count(vs_opp_clean[vs_opp_clean['team_bat_1'] == home_team], 'score_inn1')
            v_avg = self._get_avg_with_count(vs_opp_clean[vs_opp_clean['team_bat_1'] == opp], 'score_inn1')
            
            stats_data.append({
                'Opponent': opp, 'Mat': matches, 'Won': wins, 'Lost': losses, 'Tie/NR': tie_nr,
                'Win %': f"{win_pct}%", 'Last 5': form,
                f'{home_team} Avg (1st)': h_avg, 'Visitor Avg (1st)': v_avg
            })
            
        df_breakdown = pd.DataFrame(stats_data).sort_values('Mat', ascending=False)
        
        total_matches = len(clean_df)
        total_wins = len(clean_df[clean_df['winner'] == home_team])
        
        winners_lower = clean_df['winner'].astype(str).str.lower().str.strip()
        is_loss = (winners_lower != home_team.lower()) & (~winners_lower.isin(['tie', 'no result', 'nan', 'none']))
        total_losses = len(clean_df[is_loss])
        
        total_tie_nr = total_matches - total_wins - total_losses
        decisive_total = total_matches - total_tie_nr
        total_pct = int((total_wins / decisive_total) * 100) if decisive_total > 0 else 0
        
        overall_form = self._get_form_guide(clean_df, home_team)
        
        all_h_avg = self._get_avg_with_count(valid_matches[valid_matches['team_bat_1'] == home_team], 'score_inn1')
        all_v_avg = self._get_avg_with_count(valid_matches[valid_matches['team_bat_1'] != home_team], 'score_inn1')

        df_overall = pd.DataFrame([{
            'Opponent': '⚡ OVERALL', 'Mat': total_matches, 'Won': total_wins, 'Lost': total_losses, 'Tie/NR': total_tie_nr,
            'Win %': f"{total_pct}%", 'Last 5': overall_form,
            f'{home_team} Avg (1st)': all_h_avg, 'Visitor Avg (1st)': all_v_avg
        }])
        
        final_df = pd.concat([df_overall, df_breakdown], ignore_index=True)
        
        print("\n📊 DOMINANCE MATRIX")
        def highlight_win_rate(val):
            try:
                pct = int(val.replace('%', ''))
                if pct > 60: return 'color: green; font-weight: bold'
                if pct < 40: return 'color: red; font-weight: bold'
            except: pass
            return ''

        styled = final_df.style.map(highlight_win_rate, subset=['Win %'])\
                               .apply(lambda x: ['font-weight: bold; background-color: #f0f0f0' if x.name == 0 else '' for _ in x], axis=1)\
                               .hide(axis='index')
        display(styled)
        self._display_audit(clean_df, home_team)

    def analyze_away_performance(self, team_name, years_back=5):
        """
        The "Traveler" Report. ✈️
        Shows how the Team performs OUTSIDE their home country (Away + Neutral).
        UPDATED: 
        - FIXED: Overall Row 'Friendly Fire' bug (wins counting as losses).
        - FIXED: Added Tie/NR logic.
        """
        print(f"\n✈️ AWAY PERFORMANCE REPORT: {team_name} (Away & Neutral venues)")
        print(f"📅 Period: Last {years_back} Years")
        
        country_codes = {
            'India': 'IND_', 'England': 'ENG_', 'Australia': 'AUS_',
            'South Africa': 'SA_', 'New Zealand': 'NZ_', 'Sri Lanka': 'SL_',
            'West Indies': 'WI_', 'Pakistan': 'PAK_', 'Bangladesh': 'BAN_',
            'Afghanistan': 'AFG_'
        }
        
        if team_name not in country_codes:
            print(f"❌ Could not auto-detect home code for {team_name}.")
            return

        home_code = country_codes[team_name]
        
        top_teams = [
            'India', 'Australia', 'England', 'South Africa', 'New Zealand', 
            'Pakistan', 'Sri Lanka', 'West Indies', 'Bangladesh', 'Afghanistan'
        ]
        
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        away_matches = self.match_df[
            ((self.match_df['team_bat_1'] == team_name) | (self.match_df['team_bat_2'] == team_name)) &
            (~self.match_df['venue'].astype(str).str.startswith(home_code)) & 
            (self.match_df['start_date'] >= cutoff_date)
        ].copy()
        
        clean_df = self._apply_smart_filters(away_matches)
        valid_matches = clean_df[clean_df['status'] == '✅ Included']
        
        if away_matches.empty:
            print(f"❌ No away/neutral matches found for {team_name} in this period.")
            return

        def get_opponent(row):
            return row['team_bat_2'] if row['team_bat_1'] == team_name else row['team_bat_1']

        clean_df['opponent'] = clean_df.apply(get_opponent, axis=1)
        valid_matches = valid_matches.copy()
        valid_matches['opponent'] = valid_matches.apply(get_opponent, axis=1)
        
        stats_data = []
        
        for opp in top_teams:
            if opp == team_name: continue
            
            vs_opp_full = clean_df[clean_df['opponent'] == opp]
            if vs_opp_full.empty: continue
            vs_opp_clean = valid_matches[valid_matches['opponent'] == opp]
            
            matches = len(vs_opp_full)
            wins = len(vs_opp_full[vs_opp_full['winner'] == team_name])
            losses = len(vs_opp_full[vs_opp_full['winner'] == opp])
            
            tie_nr = matches - wins - losses
            
            decisive = matches - tie_nr
            win_pct = int((wins / decisive) * 100) if decisive > 0 else 0
            
            form = self._get_form_guide(vs_opp_full, team_name)
            my_avg = self._get_avg_with_count(vs_opp_clean[vs_opp_clean['team_bat_1'] == team_name], 'score_inn1')
            opp_avg = self._get_avg_with_count(vs_opp_clean[vs_opp_clean['team_bat_1'] == opp], 'score_inn1')
            
            stats_data.append({
                'Opponent': opp, 'Mat': matches, 'Won': wins, 'Lost': losses, 'Tie/NR': tie_nr,
                'Win %': f"{win_pct}%", 'Last 5': form,
                f'{team_name} Avg (1st)': my_avg, 'Opponent Avg (1st)': opp_avg
            })
            
        if not stats_data:
            print("❌ No matches played against Top 10 teams away from home.")
            return

        df_breakdown = pd.DataFrame(stats_data).sort_values('Mat', ascending=False)
        
        all_top10_full = clean_df[clean_df['opponent'].isin(top_teams)]
        all_top10_clean = valid_matches[valid_matches['opponent'].isin(top_teams)]
        
        tot_mat = len(all_top10_full)
        tot_win = len(all_top10_full[all_top10_full['winner'] == team_name])
        
        winners_lower = all_top10_full['winner'].astype(str).str.lower().str.strip()
        team_lower = team_name.lower().strip()
        
        is_loss = (winners_lower != team_lower) & (~winners_lower.isin(['tie', 'no result', 'nan', 'none']))
        tot_loss = len(all_top10_full[is_loss])
        
        tot_tie_nr = tot_mat - tot_win - tot_loss
        
        decisive_tot = tot_mat - tot_tie_nr
        tot_pct = int((tot_win / decisive_tot) * 100) if decisive_tot > 0 else 0
        
        ov_form = self._get_form_guide(all_top10_full, team_name)
        ov_my_avg = self._get_avg_with_count(all_top10_clean[all_top10_clean['team_bat_1'] == team_name], 'score_inn1')
        ov_opp_avg = self._get_avg_with_count(all_top10_clean[all_top10_clean['team_bat_1'] != team_name], 'score_inn1')
        
        df_overall = pd.DataFrame([{
            'Opponent': '⚡ OVERALL (Away)', 'Mat': tot_mat, 'Won': tot_win, 'Lost': tot_loss, 'Tie/NR': tot_tie_nr,
            'Win %': f"{tot_pct}%", 'Last 5': ov_form,
            f'{team_name} Avg (1st)': ov_my_avg, 'Opponent Avg (1st)': ov_opp_avg
        }])
        
        final_df = pd.concat([df_overall, df_breakdown], ignore_index=True)

        print("\n📊 AWAY PERFORMANCE MATRIX")
        def highlight_win_rate(val):
            try:
                pct = int(val.replace('%', ''))
                if pct > 60: return 'color: green; font-weight: bold'
                if pct < 40: return 'color: red; font-weight: bold'
            except: pass
            return ''

        styled = final_df.style.map(highlight_win_rate, subset=['Win %'])\
                               .apply(lambda x: ['font-weight: bold; background-color: #f0f0f0' if x.name == 0 else '' for _ in x], axis=1)\
                               .hide(axis='index')
        display(styled)
        self._display_audit(away_matches, team_name)

    def analyze_global_performance(self, team_name, years_back=5):
        """
        The "World Tour" Report. 🌍
        Shows Team vs Top 10 Globally.
        UPDATED: 
        - ADDED: Tie/NR Column.
        - FIXED: Overall Row 'Friendly Fire' bug.
        - UPDATED: Fixed Audit to use clean_df.
        """
        print(f"\n🌍 GLOBAL PERFORMANCE REPORT: {team_name} vs Top 10")
        print(f"📅 Period: Last {years_back} Years (All Venues)")
        
        # 1. Setup
        top_teams = [
            'India', 'Australia', 'England', 'South Africa', 'New Zealand', 
            'Pakistan', 'Sri Lanka', 'West Indies', 'Bangladesh', 'Afghanistan'
        ]
        
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        # 2. Filter Global Matches
        global_matches = self.match_df[
            ((self.match_df['team_bat_1'] == team_name) | (self.match_df['team_bat_2'] == team_name)) &
            (self.match_df['start_date'] >= cutoff_date)
        ].copy()
        
        # Apply standard filters for stats calculation
        clean_df = self._apply_smart_filters(global_matches)
        valid_matches = clean_df[clean_df['status'] == '✅ Included']
        
        if global_matches.empty:
            print(f"❌ No matches found for {team_name}.")
            return
            
        # 3. Identify Opponent
        def get_opponent(row):
            return row['team_bat_2'] if row['team_bat_1'] == team_name else row['team_bat_1']

        clean_df['opponent'] = clean_df.apply(get_opponent, axis=1) 
        valid_matches = valid_matches.copy()
        valid_matches['opponent'] = valid_matches.apply(get_opponent, axis=1)
        
        # 4. Build Breakdown Stats
        stats_data = []
        
        for opp in top_teams:
            if opp == team_name: continue
            
            vs_opp_full = clean_df[clean_df['opponent'] == opp] 
            if vs_opp_full.empty: continue
            vs_opp_clean = valid_matches[valid_matches['opponent'] == opp]
            
            matches = len(vs_opp_full)
            wins = len(vs_opp_full[vs_opp_full['winner'] == team_name])
            losses = len(vs_opp_full[vs_opp_full['winner'] == opp])
            
            # Tie/NR Logic
            tie_nr = matches - wins - losses
            
            # Win Pct (Decisive)
            decisive = matches - tie_nr
            win_pct = int((wins / decisive) * 100) if decisive > 0 else 0
            
            form = self._get_form_guide(vs_opp_full, team_name)
            my_avg = self._get_avg_with_count(vs_opp_clean[vs_opp_clean['team_bat_1'] == team_name], 'score_inn1')
            opp_avg = self._get_avg_with_count(vs_opp_clean[vs_opp_clean['team_bat_1'] == opp], 'score_inn1')
            
            stats_data.append({
                'Opponent': opp, 'Mat': matches, 'Won': wins, 'Lost': losses, 'Tie/NR': tie_nr,
                'Win %': f"{win_pct}%", 'Last 5': form,
                f'{team_name} Avg (1st)': my_avg, 'Opponent Avg (1st)': opp_avg
            })
            
        if not stats_data:
            print("❌ No matches played against Top 10 teams.")
            return

        df_breakdown = pd.DataFrame(stats_data).sort_values('Mat', ascending=False)
        
        # 5. Create OVERALL Summary (Restricted to Top 10 Opponents)
        all_top10_full = clean_df[clean_df['opponent'].isin(top_teams)]
        all_top10_clean = valid_matches[valid_matches['opponent'].isin(top_teams)]
        
        tot_mat = len(all_top10_full)
        tot_win = len(all_top10_full[all_top10_full['winner'] == team_name])
        
        # 🚨 FIX: "Friendly Fire" Bug. 
        # Old code counted (winner in top_teams) as loss, even if winner was YOU.
        winners_lower = all_top10_full['winner'].astype(str).str.lower().str.strip()
        team_lower = team_name.lower().strip()
        
        is_loss = (winners_lower != team_lower) & (~winners_lower.isin(['tie', 'no result', 'nan', 'none']))
        tot_loss = len(all_top10_full[is_loss])
        
        tot_tie_nr = tot_mat - tot_win - tot_loss
        
        decisive_tot = tot_mat - tot_tie_nr
        tot_pct = int((tot_win / decisive_tot) * 100) if decisive_tot > 0 else 0
        
        ov_form = self._get_form_guide(all_top10_full, team_name)
        ov_my_avg = self._get_avg_with_count(all_top10_clean[all_top10_clean['team_bat_1'] == team_name], 'score_inn1')
        ov_opp_avg = self._get_avg_with_count(all_top10_clean[all_top10_clean['team_bat_1'] != team_name], 'score_inn1')
        
        df_overall = pd.DataFrame([{
            'Opponent': '⚡ OVERALL', 'Mat': tot_mat, 'Won': tot_win, 'Lost': tot_loss, 'Tie/NR': tot_tie_nr,
            'Win %': f"{tot_pct}%", 'Last 5': ov_form,
            f'{team_name} Avg (1st)': ov_my_avg, 'Opponent Avg (1st)': ov_opp_avg
        }])
        
        final_df = pd.concat([df_overall, df_breakdown], ignore_index=True)
        
        # 6. Display Matrix
        print("\n📊 GLOBAL PERFORMANCE MATRIX")
        def highlight_win_rate(val):
            try:
                pct = int(val.replace('%', ''))
                if pct > 60: return 'color: green; font-weight: bold'
                if pct < 40: return 'color: red; font-weight: bold'
            except: pass
            return ''

        styled = final_df.style.map(highlight_win_rate, subset=['Win %'])\
                               .apply(lambda x: ['font-weight: bold; background-color: #f0f0f0' if x.name == 0 else '' for _ in x], axis=1)\
                               .hide(axis='index')
        display(styled)
        
        # 7. Display Match Audit
        self._display_audit(clean_df, team_name)

    def analyze_continent_performance(self, team_name, continent, opp_team='All', years_back=5):
        """
        The "Conditions Check". 🌏
        Shows how a team performs in a specific geographic region OR Globally.
        UPDATED: Supports 'All' continents (Global check).
        """
        vs_text = f"vs {opp_team}" if opp_team != 'All' else "vs Top 10"
        region_text = "All Regions" if continent == 'All' else continent
        
        print(f"\n🌏 PERFORMANCE REPORT: {team_name} {vs_text} in {region_text}")
        print(f"📅 Period: Last {years_back} Years")
        
        continent_map = {
            'Asia': ['IND_', 'PAK_', 'SL_', 'BAN_', 'AFG_', 'UAE_'],
            'Europe': ['ENG_', 'IRE_', 'SCO_', 'NED_'],
            'Oceania': ['AUS_', 'NZ_'], 
            'Africa': ['SA_', 'ZIM_'],   
            'Americas': ['WI_', 'USA_', 'CAN_'] 
        }
        
        # 1. Handle 'All' vs Specific Continent
        if continent == 'All':
            prefixes = None
        elif continent not in continent_map:
            print(f"❌ Unknown continent: {continent}")
            return
        else:
            prefixes = tuple(continent_map[continent])
            
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        # 2. Build the Filter Mask
        # Base filter: Team involved + Date
        mask = (
            ((self.match_df['team_bat_1'] == team_name) | (self.match_df['team_bat_2'] == team_name)) &
            (self.match_df['start_date'] >= cutoff_date)
        )
        
        # Add Continent Filter (if not All)
        if prefixes:
            mask = mask & (self.match_df['venue'].astype(str).str.startswith(prefixes))
            
        # Add Opponent Filter (if not All)
        if opp_team != 'All':
            mask = mask & ((self.match_df['team_bat_1'] == opp_team) | (self.match_df['team_bat_2'] == opp_team))

        region_matches = self.match_df[mask].copy()
        
        # 3. Apply Data Filters
        clean_df = self._apply_smart_filters(region_matches)
        valid_matches = clean_df[clean_df['status'] == '✅ Included']
        
        if region_matches.empty:
            print(f"❌ No matches found for {team_name} {vs_text} in {region_text} in this period.")
            return

        # 4. Determine Opponent List
        if opp_team == 'All':
            top_teams = [
                'India', 'Australia', 'England', 'South Africa', 'New Zealand', 
                'Pakistan', 'Sri Lanka', 'West Indies', 'Bangladesh', 'Afghanistan'
            ]
        else:
            top_teams = [opp_team]

        def get_opponent(row):
            return row['team_bat_2'] if row['team_bat_1'] == team_name else row['team_bat_1']

        clean_df['opponent'] = clean_df.apply(get_opponent, axis=1)
        valid_matches = valid_matches.copy()
        valid_matches['opponent'] = valid_matches.apply(get_opponent, axis=1)
        
        stats_data = []
        
        for opp in top_teams:
            if opp == team_name: continue
            
            vs_opp_full = clean_df[clean_df['opponent'] == opp]
            if vs_opp_full.empty: continue
            vs_opp_clean = valid_matches[valid_matches['opponent'] == opp]
            
            matches = len(vs_opp_full)
            wins = len(vs_opp_full[vs_opp_full['winner'] == team_name])
            losses = len(vs_opp_full[vs_opp_full['winner'] == opp])
            
            tie_nr = matches - wins - losses
            decisive = matches - tie_nr
            win_pct = int((wins / decisive) * 100) if decisive > 0 else 0
            
            form = self._get_form_guide(vs_opp_full, team_name)
            my_avg = self._get_avg_with_count(vs_opp_clean[vs_opp_clean['team_bat_1'] == team_name], 'score_inn1')
            opp_avg = self._get_avg_with_count(vs_opp_clean[vs_opp_clean['team_bat_1'] == opp], 'score_inn1')
            
            stats_data.append({
                'Opponent': opp, 'Mat': matches, 'Won': wins, 'Lost': losses, 'Tie/NR': tie_nr,
                'Win %': f"{win_pct}%", 'Last 5': form,
                f'{team_name} Avg (1st)': my_avg, 'Opponent Avg (1st)': opp_avg
            })
            
        if not stats_data:
            print(f"❌ No matches played against {opp_team} in {region_text}.")
            return

        df_breakdown = pd.DataFrame(stats_data).sort_values('Mat', ascending=False)
        
        # 5. Overall Summary
        all_top10_full = clean_df[clean_df['opponent'].isin(top_teams)]
        all_top10_clean = valid_matches[valid_matches['opponent'].isin(top_teams)]
        
        tot_mat = len(all_top10_full)
        tot_win = len(all_top10_full[all_top10_full['winner'] == team_name])
        
        winners_lower = all_top10_full['winner'].astype(str).str.lower().str.strip()
        team_lower = team_name.lower().strip()
        is_loss = (winners_lower != team_lower) & (~winners_lower.isin(['tie', 'no result', 'nan', 'none']))
        tot_loss = len(all_top10_full[is_loss])
        
        tot_tie_nr = tot_mat - tot_win - tot_loss
        decisive_tot = tot_mat - tot_tie_nr
        tot_pct = int((tot_win / decisive_tot) * 100) if decisive_tot > 0 else 0
        
        ov_form = self._get_form_guide(all_top10_full, team_name)
        ov_my_avg = self._get_avg_with_count(all_top10_clean[all_top10_clean['team_bat_1'] == team_name], 'score_inn1')
        ov_opp_avg = self._get_avg_with_count(all_top10_clean[all_top10_clean['team_bat_1'] != team_name], 'score_inn1')
        
        if opp_team == 'All':
            df_overall = pd.DataFrame([{
                'Opponent': f'⚡ OVERALL ({region_text})', 'Mat': tot_mat, 'Won': tot_win, 'Lost': tot_loss, 'Tie/NR': tot_tie_nr,
                'Win %': f"{tot_pct}%", 'Last 5': ov_form,
                f'{team_name} Avg (1st)': ov_my_avg, 'Opponent Avg (1st)': ov_opp_avg
            }])
            final_df = pd.concat([df_overall, df_breakdown], ignore_index=True)
        else:
            final_df = df_breakdown

        print(f"\n📊 PERFORMANCE MATRIX: {region_text.upper()}")
        def highlight_win_rate(val):
            try:
                pct = int(val.replace('%', ''))
                if pct > 60: return 'color: green; font-weight: bold'
                if pct < 40: return 'color: red; font-weight: bold'
            except: pass
            return ''

        styled = final_df.style.map(highlight_win_rate, subset=['Win %'])\
                               .apply(lambda x: ['font-weight: bold; background-color: #f0f0f0' if x.name == 0 else '' for _ in x], axis=1)\
                               .hide(axis='index')
        display(styled)
        
        self._display_audit(region_matches, team_name)

    def analyze_team_form(self, team_name, opp_team='All', continent='All', limit=5):
        """
        Table 1: Recent Form Analysis. 📉
        Returns the detailed dataframe of the last 'limit' matches.
        UPDATED: 
        - Supports filtering by specific Opponent AND/OR Continent.
        - Dynamic Column Name (Team Name instead of 'My Score').
        - Adds (1st) or (2nd) to score.
        """
        # Construct the Report Title
        title_parts = [f"📉 RECENT FORM: {team_name}"]
        if opp_team != 'All':
            title_parts.append(f"vs {opp_team}")
        if continent != 'All':
            title_parts.append(f"in {continent}")
        title_parts.append(f"(Last {limit} Games)")
        
        print(" ".join(title_parts))
        
        # 1. Filter Matches for the Main Team
        team_matches = self.match_df[
            (self.match_df['team_bat_1'] == team_name) | 
            (self.match_df['team_bat_2'] == team_name)
        ].copy()
        
        if team_matches.empty:
            print(f"❌ No matches found for {team_name}.")
            return

        # 2. Filter by Opponent (if selected)
        if opp_team != 'All':
            team_matches = team_matches[
                (team_matches['team_bat_1'] == opp_team) | 
                (team_matches['team_bat_2'] == opp_team)
            ]
            
        # 3. Filter by Continent (if selected)
        if continent != 'All':
            continent_map = {
                'Asia': ['IND_', 'PAK_', 'SL_', 'BAN_', 'AFG_', 'UAE_'],
                'Europe': ['ENG_', 'IRE_', 'SCO_', 'NED_'],
                'Oceania': ['AUS_', 'NZ_'], 
                'Africa': ['SA_', 'ZIM_'],   
                'Americas': ['WI_', 'USA_', 'CAN_'] 
            }
            if continent in continent_map:
                prefixes = tuple(continent_map[continent])
                team_matches = team_matches[team_matches['venue'].astype(str).str.startswith(prefixes)]
            else:
                print(f"⚠️ Warning: Unknown continent '{continent}'. Ignoring continent filter.")

        if team_matches.empty:
            print(f"❌ No matches found matching these filters.")
            return

        # 4. Apply Smart Filters (Status/Rain)
        team_matches = self._apply_smart_filters(team_matches)

        # 5. Sort & Slice
        recent = team_matches.sort_values('start_date', ascending=False).head(limit).copy()
        
        # 6. Format Output
        form_data = []
        for _, row in recent.iterrows():
            # Determine Context
            is_bat1 = (row['team_bat_1'] == team_name)
            opponent = row['team_bat_2'] if is_bat1 else row['team_bat_1']
            winner = str(row['winner']).strip()
            
            # Scores & Innings Label
            if is_bat1:
                my_val = int(row['score_inn1']) if pd.notna(row['score_inn1']) else 0
                opp_val = int(row['score_inn2']) if pd.notna(row['score_inn2']) else 0
                my_score_str = f"{my_val} (1st)" if my_val > 0 else "-"
                opp_score_str = f"{opp_val} (2nd)" if opp_val > 0 else "-"
            else:
                my_val = int(row['score_inn2']) if pd.notna(row['score_inn2']) else 0
                opp_val = int(row['score_inn1']) if pd.notna(row['score_inn1']) else 0
                my_score_str = f"{my_val} (2nd)" if my_val > 0 else "-"
                opp_score_str = f"{opp_val} (1st)" if opp_val > 0 else "-"

            # --- RESULT LOGIC ---
            if my_val > 0 and my_val == opp_val:
                result = "✅ WIN (SO)" if winner == team_name else ("🤝 TIE" if winner.lower() == 'tie' else "❌ LOSS (SO)")
            elif winner == team_name:
                result = "✅ WIN"
            elif winner.lower() == 'tie': 
                result = "🤝 TIE"
            elif winner.lower() == 'no result' or winner == 'nan' or pd.isna(row['winner']):
                result = "🌧️ NR"
            else:
                result = "❌ LOSS"
            
            if "WIN" in result or "LOSS" in result:
                if row['status'] != '✅ Included':
                    result += " 🌧️"
            
            # Venue
            venue_short = str(row['venue']).split('_')[-1].title() if pd.notna(row['venue']) else "Unknown"

            form_data.append({
                "Date": row['start_date'].strftime('%Y-%m-%d'),
                "Opponent": opponent,
                "Venue": venue_short,
                "Result": result,
                team_name: my_score_str,
                "Opp Score": opp_score_str
            })
            
        df_form = pd.DataFrame(form_data)
        
        # 7. Display with Color
        def color_result(val):
            color = 'black'
            if 'WIN' in val: color = 'green'
            elif 'LOSS' in val: color = 'red'
            elif 'TIE' in val: color = 'orange'
            elif 'NR' in val: color = 'gray'
            return f'color: {color}; font-weight: bold'

        display(df_form.style.map(color_result, subset=['Result']).hide(axis='index'))
        
        # 8. Audit
        self._display_audit(recent, team_name)
    
    def _calculate_squad_metrics(self, team_name, player_list):
        """
        Calculates aggregate career stats for a list of players.
        FIXED: Calculates 'Combined Caps' by summing individual player appearances.
        """
        # 1. Filter raw data for the whole squad first (Optimization)
        # We check Striker (Batting) and Bowler roles.
        # Note: This misses games where a player ONLY fielded (no bat, no bowl), 
        # but that is a limitation of ball-by-ball data.
        mask = (self.raw_df['striker'].isin(player_list)) | (self.raw_df['bowler'].isin(player_list))
        squad_data = self.raw_df[mask]
        
        total_runs = 0
        centuries = 0
        fifties = 0
        total_wickets = 0
        five_wickets = 0
        combined_caps = 0

        # 2. Iterate Player by Player to get Individual Stats
        for player in player_list:
            # Get player specific data
            p_bat = squad_data[squad_data['striker'] == player]
            p_bowl = squad_data[squad_data['bowler'] == player]
            
            # --- CAPS (Matches Played) ---
            # Unique matches where they appeared as Striker OR Bowler
            matches_batted = set(p_bat['match_id'].unique())
            matches_bowled = set(p_bowl['match_id'].unique())
            player_caps = len(matches_batted.union(matches_bowled))
            combined_caps += player_caps # Add to Squad Total
            
            # --- BATTING STATS ---
            if not p_bat.empty:
                # Group by match to handle scores
                match_scores = p_bat.groupby('match_id')['runs_off_bat'].sum()
                total_runs += match_scores.sum()
                centuries += (match_scores >= 100).sum()
                fifties += ((match_scores >= 50) & (match_scores < 100)).sum()
            
            # --- BOWLING STATS ---
            if not p_bowl.empty:
                # Filter for wickets
                wicket_types = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
                valid_wickets = p_bowl[p_bowl['wicket_type'].isin(wicket_types)]
                
                total_wickets += len(valid_wickets)
                
                # Group by match for 5WIs
                if not valid_wickets.empty:
                    match_wickets = valid_wickets.groupby('match_id')['wicket_type'].count()
                    five_wickets += (match_wickets >= 5).sum()
        
        return {
            'Team': team_name,
            'Caps (Combined)': combined_caps, # 👈 Now sums up every player's experience
            'Total Runs': total_runs,
            '100s': centuries,
            '50s': fifties,
            'Total Wickets': total_wickets,
            '5-Wkt Hauls': five_wickets
        }
    
    def get_active_squad(self, team_name):
        """
        Returns a list of players who have played for 'team_name'.
        Used to populate the Multi-Select Widget.
        """
        if self.meta_df.empty: return []
        
        # Filter by team and sort alphabetically
        # We perform a case-insensitive check
        team_players = self.meta_df[self.meta_df['team'].str.lower() == team_name.lower()]
        return sorted(team_players['player'].unique().tolist())

    def compare_squads(self, team_a_name, team_a_players, team_b_name, team_b_players, venue_id):
        """
        The Virtual Dugout. 🏟️
        Compares two selected XIs with:
        - 🏆 SQUAD EXPERIENCE MONITOR
        - 📝 FORM (L5 Scores & Wickets Strings)
        - 🔮 SMART PROJECTIONS (Law of Averages)
        - Side-by-Side Matchups
        - Traffic Light Coloring
        - 🔗 WIRED TO VENUES.PY
        """
        import ipywidgets as widgets
        from IPython.display import display, HTML
        import numpy as np
        
        print(f"\n⚔️ SQUAD COMPARISON: {team_a_name} vs {team_b_name}")

        # --- 1. SQUAD EXPERIENCE TABLE ---
        metrics_a = self._calculate_squad_metrics(team_a_name, team_a_players)
        metrics_b = self._calculate_squad_metrics(team_b_name, team_b_players)
        
        df_experience = pd.DataFrame([metrics_a, metrics_b])
        
        print("\n🏆 SQUAD EXPERIENCE (Combined Career Stats)")
        display(df_experience.style.format({
            'Caps (Combined)': '{:,}', 
            'Total Runs': '{:,}', 
            'Total Wickets': '{:,}'
        }).hide(axis='index').set_properties(**{'text-align': 'center', 'font-size': '11pt'}))
        print("-" * 80)
        
        # 🎨 JERSEY COLOR MAP
        TEAM_COLORS = {
            'India': '#1F34D1', 'Australia': '#D4AF37', 'England': '#C51130',
            'South Africa': '#006A4E', 'New Zealand': '#222222', 'Pakistan': '#01411C',
            'West Indies': '#7B0028', 'Sri Lanka': '#0E3292', 'Bangladesh': '#006A4E',
            'Afghanistan': '#0063B2', 'Zimbabwe': '#D40000', 'Ireland': '#009D4E',
            'Netherlands': '#FF6600'
        }

        # 🧠 BOWLER STYLE DICTIONARY
        BOWLER_STYLES = {
            # --- AUSTRALIA ---
            'MA Starc': '⚡ Left-Arm Fast', 'JR Hazlewood': '⚡ Right-Arm Fast', 'PJ Cummins': '⚡ Right-Arm Fast',
            'A Zampa': '🌀 Leg Spin', 'NM Lyon': '🌀 Off Spin', 'GJ Maxwell': '🌀 Off Spin', 
            'MR Marsh': '⚡ Right-Arm Med-Fast', 'MP Stoinis': '⚡ Right-Arm Med-Fast', 
            'C Green': '⚡ Right-Arm Fast-Med', 'Sean Abbott': '⚡ Right-Arm Fast-Med', 'JA Richardson': '⚡ Right-Arm Fast',
            'NT Ellis': '⚡ Right-Arm Fast-Med', 'X Bartlett': '⚡ Right-Arm Fast-Med',
            # --- INDIA ---
            'JJ Bumrah': '⚡ Right-Arm Fast', 'Mohammed Shami': '⚡ Right-Arm Fast', 'Mohammed Siraj': '⚡ Right-Arm Fast',
            'Kuldeep Yadav': '🌀 Left-Arm Wrist', 'RA Jadeja': '🌀 Left-Arm Orth', 'R Ashwin': '🌀 Off Spin',
            'AR Patel': '🌀 Left-Arm Orth', 'HH Pandya': '⚡ Right-Arm Fast-Med', 'Shardul Thakur': '⚡ Right-Arm Med-Fast',
            'Washington Sundar': '🌀 Off Spin', 'Harshit Rana': '⚡ Right-Arm Fast', 'Nithish Kumar Reddy': '⚡ Right-Arm Fast-Med',
            'M Prasidh Krishna': '⚡ Right-Arm Fast', 'Arshdeep Singh': '⚡ Left-Arm Fast-Med', 'Ravi Bishnoi': '🌀 Leg Spin',
            # --- ENGLAND ---
            'J Archer': '⚡ Right-Arm Fast', 'MA Wood': '⚡ Right-Arm Fast', 'CR Woakes': '⚡ Right-Arm Fast-Med',
            'SM Curran': '⚡ Left-Arm Fast-Med', 'AU Rashid': '🌀 Leg Spin', 'MM Ali': '🌀 Off Spin',
            'RJW Topley': '⚡ Left-Arm Fast-Med', 'BA Carse': '⚡ Right-Arm Fast', 'O Stone': '⚡ Right-Arm Fast',
            'G Atkinson': '⚡ Right-Arm Fast-Med', 'LS Livingstone': '🌀 Off Spin', 'W Jacks': '🌀 Off Spin',
            'Rehan Ahmed': '🌀 Leg Spin', 'S Mahmood': '⚡ Right-Arm Fast-Med', 'L Wood': '⚡ Left-Arm Fast',
            # --- SOUTH AFRICA ---
            'K Rabada': '⚡ Right-Arm Fast', 'L Ngidi': '⚡ Right-Arm Fast-Med', 'A Nortje': '⚡ Right-Arm Fast',
            'M Jansen': '⚡ Left-Arm Fast-Med', 'G Coetzee': '⚡ Right-Arm Fast', 'KA Maharaj': '🌀 Left-Arm Orth',
            'T Shamsi': '🌀 Left-Arm Wrist', 'BC Fortuin': '🌀 Left-Arm Orth', 'W Mulder': '⚡ Right-Arm Med',
            'AL Phehlukwayo': '⚡ Right-Arm Fast-Med', 'N Burger': '⚡ Left-Arm Fast-Med', 'O Baartman': '⚡ Right-Arm Fast-Med',
            # --- NEW ZEALAND ---
            'TA Boult': '⚡ Left-Arm Fast-Med', 'TG Southee': '⚡ Right-Arm Fast-Med', 'MJ Henry': '⚡ Right-Arm Fast-Med',
            'LH Ferguson': '⚡ Right-Arm Fast', 'MJ Santner': '🌀 Left-Arm Orth', 'IS Sodhi': '🌀 Leg Spin',
            'KJ Jamieson': '⚡ Right-Arm Fast-Med', 'AF Milne': '⚡ Right-Arm Fast', 'GD Phillips': '🌀 Off Spin',
            'R Ravindra': '🌀 Left-Arm Orth', 'MJ Bracewell': '🌀 Off Spin', 'BN Sears': '⚡ Right-Arm Fast',
            'W O\'Rourke': '⚡ Right-Arm Fast-Med',
            # --- PAKISTAN ---
            'Shaheen Shah Afridi': '⚡ Left-Arm Fast', 'Naseem Shah': '⚡ Right-Arm Fast', 'Haris Rauf': '⚡ Right-Arm Fast',
            'Hasan Ali': '⚡ Right-Arm Fast-Med', 'Shadab Khan': '🌀 Leg Spin', 'Mohammad Nawaz': '🌀 Left-Arm Orth',
            'Usama Mir': '🌀 Leg Spin', 'Mohammad Wasim': '⚡ Right-Arm Fast-Med', 'Abrar Ahmed': '🌀 Leg Spin',
            'Iftikhar Ahmed': '🌀 Off Spin', 'Agha Salman': '🌀 Off Spin', 'Faheem Ashraf': '⚡ Right-Arm Fast-Med',
            'Zaman Khan': '⚡ Right-Arm Fast', 'Aamer Jamal': '⚡ Right-Arm Fast-Med', 'Mir Hamza': '⚡ Left-Arm Fast-Med',
            # --- SRI LANKA ---
            'PWH de Silva': '🌀 Leg Spin', 'M Theekshana': '🌀 Off Spin', 'D Madushanka': '⚡ Left-Arm Fast-Med',
            'CAK Rajitha': '⚡ Right-Arm Fast-Med', 'PVD Chameera': '⚡ Right-Arm Fast', 'M Pathirana': '⚡ Right-Arm Fast',
            'CBRLS Kumara': '⚡ Right-Arm Fast', 'D Wellalage': '🌀 Left-Arm Orth', 'J Vandersay': '🌀 Leg Spin',
            'AM Fernando': '⚡ Right-Arm Fast-Med', 'C Karunaratne': '⚡ Right-Arm Fast-Med', 'MD Shanaka': '⚡ Right-Arm Med',
            'DM de Silva': '🌀 Off Spin', 'KIC Asalanka': '🌀 Off Spin', 'N Thushara': '⚡ Right-Arm Fast-Med',
            # --- WEST INDIES ---
            'AS Joseph': '⚡ Right-Arm Fast', 'J Holder': '⚡ Right-Arm Fast-Med', 'AJ Hosein': '🌀 Left-Arm Orth',
            'G Motie': '🌀 Left-Arm Orth', 'R Shepherd': '⚡ Right-Arm Fast-Med', 'O Thomas': '⚡ Right-Arm Fast',
            'K Pierre': '🌀 Left-Arm Orth', 'RL Chase': '🌀 Off Spin', 'JNT Seales': '⚡ Right-Arm Fast',
            'JP Greaves': '🌀 Off Spin', 'S Gabriel': '⚡ Right-Arm Fast',
            # --- BANGLADESH ---
            'Mustafizur Rahman': '⚡ Left-Arm Fast', 'Taskin Ahmed': '⚡ Right-Arm Fast', 'Shakib Al Hasan': '🌀 Left-Arm Orth',
            'Mehedi Hasan Miraz': '🌀 Off Spin', 'Nasum Ahmed': '🌀 Left-Arm Orth', 'Hasan Mahmud': '⚡ Right-Arm Fast',
            'Shoriful Islam': '⚡ Left-Arm Fast', 'Taijul Islam': '🌀 Left-Arm Orth', 'Rishad Hossain': '🌀 Leg Spin',
            'Tanzim Hasan Sakib': '⚡ Right-Arm Fast-Med', 'Ebadot Hossain': '⚡ Right-Arm Fast',
            # --- AFGHANISTAN ---
            'Rashid Khan': '🌀 Leg Spin', 'Mujeeb Ur Rahman': '🌀 Off Spin', 'Mohammad Nabi': '🌀 Off Spin',
            'Fazalhaq Farooqi': '⚡ Left-Arm Fast-Med', 'Naveen-ul-Haq': '⚡ Right-Arm Fast-Med',
            'Azmatullah Omarzai': '⚡ Right-Arm Fast-Med', 'Noor Ahmad': '🌀 Left-Arm Wrist', 'Fareed Ahmad': '⚡ Left-Arm Fast-Med',
            'Gulbadin Naib': '⚡ Right-Arm Fast-Med', 'Qais Ahmad': '🌀 Leg Spin', 'AM Ghazanfar': '🌀 Off Spin'
        }

        if self.player_df.empty:
            print("❌ No player data available.")
            return

        # -------------------------------------------------------------
        # ✅ NEW VENUE LOGIC (WIRED TO VENUES.PY)
        # -------------------------------------------------------------
        from venues import get_venue_aliases
        target_venues = get_venue_aliases(venue_id)
        
        print(f"📍 Analysis Venue ID: {venue_id}")
        print(f"🔎 Aggregating stats from: {target_venues}")
        print("-" * 80)

        # --- INTERNAL HELPER: GET PLAYER STATS ---
        def get_stats(player, opponent_team, venue_list):
            # Batting
            bat_all = self.player_df[(self.player_df['player'] == player) & (self.player_df['role'] == 'batting')]
            car_runs = bat_all[bat_all['context'] == 'vs_team']['runs'].sum()
            car_outs = bat_all[bat_all['context'] == 'vs_team']['dismissals'].sum()
            car_inns = bat_all[bat_all['context'] == 'vs_team']['innings'].sum()
            car_avg = round(car_runs / car_outs, 1) if car_outs > 0 else car_runs
            
            opp_row = bat_all[(bat_all['context'] == 'vs_team') & (bat_all['opponent'] == opponent_team)]
            opp_avg = "-"
            if not opp_row.empty:
                runs, outs = opp_row['runs'].sum(), opp_row['dismissals'].sum()
                opp_avg = round(runs / outs, 1) if outs > 0 else runs

            ven_row = bat_all[(bat_all['context'] == 'at_venue') & (bat_all['opponent'].isin(venue_list))]
            ven_avg = "-"
            ven_inns = "-"
            if not ven_row.empty:
                runs = ven_row['runs'].sum()
                outs = ven_row['dismissals'].sum()
                ven_inns = ven_row['innings'].sum()
                ven_avg = round(runs / outs, 1) if outs > 0 else runs

            # -------------------------------------------------------
            # 📝 BATTING FORM (Last 5 Scores) - UPDATED
            # -------------------------------------------------------
            bat_form_display = "-"
            try:
                # 1. Get chronological innings (Uses global sort from __init__)
                p_bat_raw = self.raw_df[self.raw_df['striker'] == player].drop_duplicates(subset=['match_id'])
                last_5_bat = p_bat_raw.tail(5)['match_id'].unique()
                
                recent_scores = []
                if len(last_5_bat) > 0:
                    for m_id in last_5_bat:
                        m_data = self.raw_df[(self.raw_df['match_id'] == m_id) & (self.raw_df['striker'] == player)]
                        runs = m_data['runs_off_bat'].sum()
                        is_out = m_data['wicket_type'].notna().any()
                        score_str = f"{runs}" if is_out else f"{runs}*"
                        recent_scores.append(score_str)
                    # Show: Most Recent -> Oldest (Left to Right)
                    bat_form_display = ", ".join(recent_scores[::-1]) 
            except: pass

            # 🔮 PROJECTIONS (Runs)
            venue_primary = target_venues[0] if target_venues else venue_id
            proj_runs, _ = self._calculate_smart_projection(player, 'batting', venue_primary)

            # Bowling Stats
            bowl_all = self.player_df[(self.player_df['player'] == player) & (self.player_df['role'] == 'bowling')]
            c_runs = bowl_all[bowl_all['context'] == 'vs_team']['runs'].sum()
            c_wkts = bowl_all[bowl_all['context'] == 'vs_team']['dismissals'].sum()
            c_balls = bowl_all[bowl_all['context'] == 'vs_team']['balls'].sum()
            bowl_avg = round(c_runs / c_wkts, 1) if c_wkts > 0 else "-"
            bowl_econ = round((c_runs / c_balls) * 6, 1) if c_balls > 0 else "-"

            v_bowl_row = bowl_all[(bowl_all['context'] == 'at_venue') & (bowl_all['opponent'].isin(venue_list))]
            ven_econ = "-"
            ven_wkts = "-"
            if not v_bowl_row.empty:
                vr, vb, vw = v_bowl_row['runs'].sum(), v_bowl_row['balls'].sum(), v_bowl_row['dismissals'].sum()
                ven_econ = round((vr / vb) * 6, 1) if vb > 0 else "-"
                ven_wkts = int(vw)
            
            # -------------------------------------------------------
            # 🥎 BOWLING FORM (Last 5 Matches Wickets) - NEW
            # -------------------------------------------------------
            bowl_form_display = "-"
            try:
                # Get chronological bowling innings
                p_bowl_raw = self.raw_df[self.raw_df['bowler'] == player].drop_duplicates(subset=['match_id'])
                if not p_bowl_raw.empty:
                    last_5_bowl = p_bowl_raw.tail(5)['match_id'].unique()
                    recent_wkts = []
                    
                    wicket_types = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
                    
                    for m_id in last_5_bowl:
                        m_data = self.raw_df[(self.raw_df['match_id'] == m_id) & (self.raw_df['bowler'] == player)]
                        wkt_count = m_data['wicket_type'].isin(wicket_types).sum()
                        recent_wkts.append(f"{wkt_count}w")
                    
                    bowl_form_display = ", ".join(recent_wkts[::-1])
            except: pass

            # 🔮 PROJECTIONS (Wickets)
            proj_wkts, _ = self._calculate_smart_projection(player, 'bowling', venue_primary)
            v_short = venue_id.split('_')[-1].title() if '_' in venue_id else 'Venue'
            
            # ✅ RETURN DICTIONARY WITH ALL NEW METRICS
            return {
                'Player': player,
                'Inns': car_inns,
                'Bat Form': bat_form_display, # 👈 Score String
                'Bat Avg': car_avg,
                f'vs {opponent_team}': opp_avg,
                f'Avg ({v_short})': ven_avg, 
                '🔮 Runs': proj_runs, # 👈 Prediction
                'Bowl Form': bowl_form_display, # 👈 Wicket String
                'Bowl Econ': bowl_econ,
                f'Econ ({v_short})': ven_econ,
                f'Wkts ({v_short})': ven_wkts,
                '🔮 Wkts': proj_wkts  # 👈 Prediction
            }

        # --- DISPLAY TEAM SUMMARIES (Side by Side) ---
        out_summary_a = widgets.Output()
        out_summary_b = widgets.Output()

        # Helper to style the dataframe (Conditionally Format Forms)
        def style_df(df):
            return df.style.format(na_rep="-", precision=1).hide(axis='index')\
                .applymap(lambda v: 'color: red; font-weight: bold;' if isinstance(v, str) and v == '0' else '', subset=['Bat Form'])\
                .applymap(lambda v: 'color: green; font-weight: bold;' if isinstance(v, str) and ('3w' in v or '4w' in v or '5w' in v) else '', subset=['Bowl Form'])

        with out_summary_a:
            print(f"📊 {team_a_name.upper()}")
            data_a = [get_stats(p, team_b_name, target_venues) for p in team_a_players]
            df_a = pd.DataFrame(data_a)
            if not df_a.empty: display(style_df(df_a))

        with out_summary_b:
            print(f"📊 {team_b_name.upper()}")
            data_b = [get_stats(p, team_a_name, target_venues) for p in team_b_players]
            df_b = pd.DataFrame(data_b)
            if not df_b.empty: display(style_df(df_b))
            
        display(widgets.HBox([out_summary_a, out_summary_b], layout=widgets.Layout(width='100%')))

        # --- HELPER: BATTER VS BOWLERS DISPLAY (Existing) ---
        def display_batter_vs_bowlers(batter_name, batter_team, bowlers_list, bowling_team):
            matchup_data = []
            
            for bowler in bowlers_list:
                h2h = self.player_df[
                    (self.player_df['player'] == batter_name) & 
                    (self.player_df['opponent'] == bowler) & 
                    (self.player_df['role'] == 'h2h')
                ]
                
                if not h2h.empty:
                    balls = h2h['balls'].sum()
                    if balls > 0:
                        runs = h2h['runs'].sum()
                        outs = h2h['dismissals'].sum()
                        avg = round(runs/outs, 1) if outs > 0 else f"{runs}*"
                        sr = round((runs/balls)*100, 1)
                        
                        style = BOWLER_STYLES.get(bowler, 'Unknown')
                        bowler_display = f"{bowler} ({style})"
                        
                        matchup_data.append({
                            'Bowler': bowler_display,
                            'Runs': runs,
                            'Balls': balls,
                            'Outs': outs,
                            'Avg': avg,
                            'SR': sr
                        })
            
            if matchup_data:
                hex_code = TEAM_COLORS.get(batter_team, '#000000')
                display(HTML(f"<h4 style='color: {hex_code}; margin-bottom: 2px; margin-top: 15px;'>🏏 {batter_name}</h4>"))
                
                df_m = pd.DataFrame(matchup_data).sort_values('Balls', ascending=False)
                
                # 🎨 COLOR CODING LOGIC (Green / Orange / Red)
                def style_rows(row):
                    outs = row['Outs']
                    if outs == 0:
                        return ['color: green; font-weight: bold'] * len(row)
                    elif outs > 2:
                        return ['color: red; font-weight: bold'] * len(row)
                    elif 1 <= outs <= 2:
                        return ['color: #FF8C00; font-weight: bold'] * len(row)
                    return [''] * len(row)

                display(df_m.style.apply(style_rows, axis=1).format(precision=1).hide(axis='index'))

        # --- SIDE BY SIDE MATCHUPS ---
        print("\n⚔️ FULL MATCHUP BREAKDOWN")
        print("="*80)
        
        left_box = widgets.Output()
        right_box = widgets.Output()
        
        with left_box:
            print(f"🗡️ {team_a_name} Batting vs {team_b_name} Bowling")
            for batter in team_a_players:
                display_batter_vs_bowlers(batter, team_a_name, team_b_players, team_b_name)
        
        with right_box:
            print(f"🗡️ {team_b_name} Batting vs {team_a_name} Bowling")
            for batter in team_b_players:
                display_batter_vs_bowlers(batter, team_b_name, team_a_players, team_a_name)
        
        display(widgets.HBox([left_box, right_box], layout=widgets.Layout(width='100%', justify_content='space-around')))

    def predict_score(self, batting_team, batting_players, bowling_team, bowling_players, venue_id):
        """
        🔮 PREDICTOR ENGINE: Calculates Par Score based on Venue, Batting Form & Bowling Resistance.
        FIXED: 
        - Calculates Total Runs by adding 'runs_off_bat' + 'extras'.
        - Wired to VENUES.PY for consistent stadium alias lookups.
        """
        import ipywidgets as widgets
        from IPython.display import display, HTML
        
        print(f"\n🔮 SCORE PREDICTOR: {batting_team} Batting First at {venue_id}")
        print("="*80)
        
        # -------------------------------------------------------------
        # ✅ NEW VENUE LOGIC (WIRED TO VENUES.PY)
        # -------------------------------------------------------------
        # This replaces the old hardcoded dictionaries.
        # It automatically finds ALL variations (e.g. Wankhede + Wankhede Mumbai)
        target_venues = get_venue_aliases(venue_id)
        
        # --- 2. CALCULATE VENUE BASELINE (1st Innings Avg) ---
        venue_mask = self.raw_df['venue'].isin(target_venues) & (self.raw_df['innings'] == 1)
        venue_matches = self.raw_df[venue_mask]
        
        # We need a fallback variable for display in case data is missing
        venue_avg = 250 
        sample_size = 0
        
        if venue_matches.empty:
            print(f"⚠️ Not enough data for venue '{venue_id}'. Using Global Avg (250).")
        else:
            # 🚨 FIX: Sum runs_off_bat + extras to get total runs
            # We group by match_id, sum both columns, then add them together
            match_sums = venue_matches.groupby('match_id')[['runs_off_bat', 'extras']].sum()
            match_totals = match_sums['runs_off_bat'] + match_sums['extras']
            
            venue_avg = int(match_totals.mean())
            sample_size = len(match_totals)
            print(f"🏟️ Venue Avg (1st Inn): {venue_avg} runs (Sample: {sample_size} matches)")

        # --- 3. CALCULATE BATTING POWER (Team A) ---
        total_bat_potential = 0
        active_batters = 0
        
        for p in batting_players:
            p_stats = self.player_df[(self.player_df['player'] == p) & (self.player_df['role'] == 'batting')]
            if not p_stats.empty:
                runs = p_stats[p_stats['context'] == 'vs_team']['runs'].sum()
                outs = p_stats[p_stats['context'] == 'vs_team']['dismissals'].sum()
                
                # Cap average at 60
                avg = (runs / outs) if outs > 0 else runs
                if avg > 60: avg = 60 
                if avg < 5: avg = 5 
                
                total_bat_potential += avg
                active_batters += 1
        
        standard_bat_score = 300 
        bat_factor = total_bat_potential / standard_bat_score if standard_bat_score > 0 else 1.0
        
        # --- 4. CALCULATE BOWLING RESISTANCE (Team B) ---
        total_econ = 0
        active_bowlers = 0
        
        for p in bowling_players:
            p_stats = self.player_df[(self.player_df['player'] == p) & (self.player_df['role'] == 'bowling')]
            if not p_stats.empty:
                runs = p_stats[p_stats['context'] == 'vs_team']['runs'].sum()
                balls = p_stats[p_stats['context'] == 'vs_team']['balls'].sum()
                
                if balls > 60:
                    econ = (runs / balls) * 6
                    total_econ += econ
                    active_bowlers += 1
        
        avg_team_econ = (total_econ / active_bowlers) if active_bowlers > 0 else 5.5
        standard_econ = 5.5
        
        # Logic: If Team Econ (6.0) > Standard (5.5) -> They concede MORE runs -> Factor > 1
        bowl_factor = avg_team_econ / standard_econ
        
        # --- 5. THE PREDICTION FORMULA ---
        predicted_score = venue_avg * bat_factor * bowl_factor
        
        lower_bound = int(predicted_score - 15)
        upper_bound = int(predicted_score + 15)
        
        # --- DISPLAY DASHBOARD ---
        
        # Determine Colors
        bat_color = 'green' if bat_factor >= 1 else 'red'
        bowl_color = 'green' if bowl_factor >= 1 else 'red' # High factor (bad bowling) is 'green' for batting side!
        
        html_card = f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px;">
            <h2 style="color: #333; margin-top: 0;">🔮 Prediction: {batting_team} to score</h2>
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <div style="text-align: center; width: 30%;">
                    <div style="font-size: 24px;">🏟️</div>
                    <div style="font-weight: bold; color: #666;">Venue Baseline</div>
                    <div style="font-size: 20px; color: #333;">{venue_avg}</div>
                </div>
                <div style="text-align: center; width: 30%;">
                    <div style="font-size: 24px;">🏏</div>
                    <div style="font-weight: bold; color: #666;">Bat Strength</div>
                    <div style="font-size: 20px; color: {bat_color};">{round(bat_factor, 2)}x</div>
                </div>
                <div style="text-align: center; width: 30%;">
                    <div style="font-size: 24px;">⚡</div>
                    <div style="font-weight: bold; color: #666;">Bowl Permissiveness</div>
                    <div style="font-size: 20px; color: {bowl_color};">{round(bowl_factor, 2)}x</div>
                </div>
            </div>
            <div style="text-align: center; border-top: 1px solid #ccc; padding-top: 15px;">
                <div style="font-size: 16px; color: #555; margin-bottom: 5px;">Predicted 1st Innings Range</div>
                <div style="font-size: 36px; font-weight: bold; color: #2c3e50;">{lower_bound} - {upper_bound}</div>
                <div style="font-size: 12px; color: #888;">(Confidence: Based on {sample_size} historical matches)</div>
            </div>
        </div>
        """
        display(HTML(html_card))

    #==================================================================================================#
    # 5. PLAYERS STATS FUNCTIONS

    def analyze_player_profile(self, player_name):
        """
        Micro-Level Analysis. 🔬
        Shows Player vs Teams, Venues, and Specific Bowlers.
        Reads from the pre-processed 'processed_player_stats.csv'.
        """
        print(f"\n👤 PLAYER PROFILE: {player_name.upper()}")
        
        if self.player_df.empty:
            print("❌ Player data is missing. Please run the processor script.")
            return

        # 1. Filter for the specific player
        # We use str.lower() comparison to be safe
        p_stats = self.player_df[self.player_df['player'].str.lower() == player_name.lower()].copy()
        
        if p_stats.empty:
            print(f"❌ No data found for '{player_name}'.")
            return

        # --- SECTION 1: PERFORMANCE vs TEAMS ---
        vs_teams = p_stats[p_stats['type'] == 'vs_team'].sort_values('runs', ascending=False)
        if not vs_teams.empty:
            print("\n⚔️ PERFORMANCE vs TEAMS")
            # Format columns nicely
            cols = ['opponent', 'innings', 'runs', 'average', 'strike_rate']
            display(vs_teams[cols].style.format("{:.1f}", subset=['average', 'strike_rate']).hide(axis='index'))
        
        # --- SECTION 2: PERFORMANCE at VENUES ---
        at_venues = p_stats[p_stats['type'] == 'at_venue'].sort_values('runs', ascending=False).head(10)
        if not at_venues.empty:
            print("\n🏟️ TOP 10 VENUES")
            cols = ['opponent', 'innings', 'runs', 'average', 'strike_rate']
            # Rename 'opponent' to 'Venue' for display clarity
            display(at_venues[cols].rename(columns={'opponent': 'Venue'}).style.format("{:.1f}", subset=['average', 'strike_rate']).hide(axis='index'))
            
        # --- SECTION 3: H2H MATCHUPS (Bat vs Bowler) ---
        h2h = p_stats[p_stats['type'] == 'h2h'].sort_values('runs', ascending=False)
        if not h2h.empty:
            print("\n🥊 HEAD-TO-HEAD (Most Runs vs Bowlers)")
            
            # Highlight 'Bunnies' (High Dismissals)
            def highlight_struggle(val):
                return 'color: red; font-weight: bold' if val >= 3 else ''
            
            # Show top 10 matchups
            top_h2h = h2h.head(10)
            
            cols = ['opponent', 'runs', 'balls', 'dismissals', 'strike_rate']
            display(top_h2h[cols]
                   .rename(columns={'opponent': 'Bowler'})
                   .style.map(highlight_struggle, subset=['dismissals'])
                   .format("{:.1f}", subset=['strike_rate'])
                   .hide(axis='index'))

    # =================================================================================
    # 5. DISPLAY & FORMATTING HELPERS
    # =================================================================================
    def _build_and_display_report(self, df, home_team, visitor_label, title, is_venue_mode):
        """
        Builds and displays the standard analysis report.
        UPDATED: 
        - FIXED: 'home_team_ref' KeyError.
        - FIXED: Case-insensitive check for Ties/NR.
        """
        import pandas as pd
        import numpy as np

        # 1. PREPARE DATA & HANDLING STRINGS
        winners_lower = df['winner'].astype(str).str.lower().str.strip()
        home_lower = home_team.lower().strip()
        
        # 2. CALCULATE COUNTS
        matches_played = len(df)
        
        # A. Home Wins
        home_wins_mask = winners_lower == home_lower
        home_wins_df = df[home_wins_mask]
        won_home = len(home_wins_df)
        
        # B. Invalid Results (Ties & No Results)
        is_tie = winners_lower == 'tie'
        is_nr = winners_lower.isin(['no result', 'nan', 'none', ''])
        invalid_results = len(df[is_tie | is_nr])
        
        # C. Visitor Wins
        if visitor_label == 'Visitors':
            won_visitor = matches_played - won_home - invalid_results
            vis_wins_df = df[(~home_wins_mask) & (~is_tie) & (~is_nr)]
        else:
            vis_lower = visitor_label.lower().strip()
            vis_wins_mask = winners_lower == vis_lower
            vis_wins_df = df[vis_wins_mask]
            won_visitor = len(vis_wins_df)

        # 3. BREAKDOWN STATS
        won_home_bat1 = len(home_wins_df[home_wins_df['team_bat_1'] == home_team])
        won_home_bat2 = len(home_wins_df[home_wins_df['team_bat_2'] == home_team])
        
        won_vis_bat1 = len(vis_wins_df[vis_wins_df['team_bat_2'] == home_team]) 
        won_vis_bat2 = len(vis_wins_df[vis_wins_df['team_bat_1'] == home_team]) 

        # 4. WIN RATE
        decisive_matches = matches_played - invalid_results
        win_rate = int((won_home / decisive_matches) * 100) if decisive_matches > 0 else 0
        
        # 5. AVERAGES (Clean Data Only)
        stats_df = df[df['status'] == '✅ Included'].copy()
        
        # 🚨 FIX: Re-adding the missing column required by _calculate_team_stats
        stats_df['home_team_ref'] = home_team 
        
        overall_avg_1 = self._get_avg_with_count(stats_df, 'score_inn1')
        overall_avg_2 = self._get_avg_with_count(stats_df, 'score_inn2')
        
        bat1_winners = stats_df[stats_df['winner'] == stats_df['team_bat_1']]
        overall_avg_win = self._get_avg_with_count(bat1_winners, 'score_inn1')
        
        # Calculate Team Stats
        h_stats = self._calculate_team_stats(stats_df, home_team)
        v_stats = self._calculate_team_stats(stats_df, visitor_label, is_home_analysis=True)

        # 6. REPORT DATA
        report_data = [
            {"Metric": "Matches Played", "Value": matches_played},
            {"Metric": "Tied / No Result", "Value": invalid_results},
            {"Metric": f"{home_team} Win %", "Value": f"{win_rate}%"},

            {"Metric": f"--- {home_team.upper()} WINS ---", "Value": "---"},
            {"Metric": "Total Wins", "Value": won_home},
            {"Metric": "Won Batting 1st (Defended)", "Value": won_home_bat1},
            {"Metric": "Won Batting 2nd (Chased)", "Value": won_home_bat2},
            
            {"Metric": f"--- {visitor_label.upper()} WINS ---", "Value": "---"},
            {"Metric": "Total Wins", "Value": won_visitor},
            {"Metric": "Won Batting 1st (Defended)", "Value": won_vis_bat1},
            {"Metric": "Won Batting 2nd (Chased)", "Value": won_vis_bat2},
            
            {"Metric": "--- OVERALL SCORING STATS ---", "Value": "---"},
            {"Metric": "Overall Avg 1st Innings", "Value": overall_avg_1},
            {"Metric": "Overall Avg 2nd Innings", "Value": overall_avg_2},
            {"Metric": "Avg 1st Innings Winning Score", "Value": overall_avg_win},
            
            {"Metric": f"--- BATTING 1ST: {home_team} ---", "Value": "---"},
            {"Metric": "Average 1st Innings", "Value": h_stats['avg_1st']},
            {"Metric": "Highest 1st Innings", "Value": h_stats['high_1st']},
            {"Metric": "Lowest 1st Innings", "Value": h_stats['low_1st']},
            {"Metric": "Avg Winning Score", "Value": h_stats['avg_1st_win']},
            {"Metric": "Lowest Defended Score", "Value": h_stats['low_defended']},
            
            {"Metric": f"--- BATTING 1ST: {visitor_label} ---", "Value": "---"},
            {"Metric": "Average 1st Innings", "Value": v_stats['avg_1st']},
            {"Metric": "Highest 1st Innings", "Value": v_stats['high_1st']},
            {"Metric": "Lowest 1st Innings", "Value": v_stats['low_1st']},
            {"Metric": "Avg Winning Score", "Value": v_stats['avg_1st_win']},
            {"Metric": "Lowest Defended Score", "Value": v_stats['low_defended']},
            
            {"Metric": f"--- CHASING: {home_team} ---", "Value": "---"},
            {"Metric": "Average 2nd Innings", "Value": h_stats['avg_2nd']},
            {"Metric": "Highest Chased", "Value": h_stats['high_chased']},
            {"Metric": "Avg Successful Chase", "Value": h_stats['avg_succ']}, 
            {"Metric": "Avg Failed Chase", "Value": h_stats['avg_fail']},
            
            {"Metric": f"--- CHASING: {visitor_label} ---", "Value": "---"},
            {"Metric": "Average 2nd Innings", "Value": v_stats['avg_2nd']},
            {"Metric": "Highest Chased", "Value": v_stats['high_chased']},
            {"Metric": "Avg Successful Chase", "Value": v_stats['avg_succ']},
            {"Metric": "Avg Failed Chase", "Value": v_stats['avg_fail']},
        ]
        
        self._display_report(report_data, home_team, visitor_label, title)
        self._display_audit(df, home_team)

    def _display_report(self, data, team_a, team_b, title):
        report_df = pd.DataFrame(data)
        team_colors = {
            'India': '#1F8AC0', 'England': '#D60C0C', 'Australia': '#CBA135',
            'Pakistan': '#006400', 'South Africa': '#004d00', 'New Zealand': '#404040',
            'West Indies': '#7D000B', 'Sri Lanka': '#4d88ff', 'Bangladesh': '#006a4e',
            'Visitors': '#808080'
        }
        def get_color(val):
            for t, c in team_colors.items():
                if t in str(val): return f'color: {c}; font-weight: bold;'
            return ''
            
        print(f"\n📊 {title}")
        styled = report_df.style.map(lambda x: get_color(team_a) if team_a in str(x) else '', subset=['Metric'])\
                                .map(lambda x: get_color(team_b) if team_b in str(x) else '', subset=['Metric'])\
                                .hide(axis='index')
        with pd.option_context('display.max_rows', None): 
            display(styled)

    def _display_audit(self, df, highlight_team):
        if df.empty:
            return
        print("\n🕵️‍♂️ MATCH AUDIT (Most Recent First)")
        cols = ['start_date', 'venue', 'winner', 'team_bat_1', 'display_inn1', 'team_bat_2', 'display_inn2', 'status']
        audit_df = df[cols].sort_values('start_date', ascending=False).rename(
            columns={'display_inn1': 'score_inn1', 'display_inn2': 'score_inn2'}
        )
        
        # 🚨 FIX: Force Pandas to show ALL rows instead of collapsing them
        # context manager temporarily removes the row limit just for this display
        with pd.option_context('display.max_rows', None):
            display(audit_df)

    def _get_avg_with_count(self, df, column_name):
        """
        Helper: Returns 'Average (Count)' string. 
        Example: '285 (12)' or '-' if empty.
        """
        if df.empty or column_name not in df.columns:
            return "-"
        
        # Calculate mean
        val = df[column_name].mean()
        if pd.isna(val):
            return "-"
            
        avg = int(val)
        count = len(df)
        return f"{avg} ({count})"

    def _get_form_guide(self, df, team_name, limit=5):
        """
        Helper: Returns visual form string (e.g., '✅❌✅✅❌').
        Sorts by date descending (Newest -> Oldest).
        UPDATED: Prioritizes actual Result over Rain Status.
        """
        if df.empty:
            return "-"
        
        # Sort by date (Newest first)
        recent_matches = df.sort_values('start_date', ascending=False).head(limit)
        
        form = []
        # Standardize team name for comparison
        target_team = team_name.lower().strip()
        
        for _, row in recent_matches.iterrows():
            winner = str(row['winner']).lower().strip()
            
            # 1. Check for True No Result (Abandoned)
            if winner in ['no result', 'nan', 'none', '']:
                form.append("🌧️")
            
            # 2. Check for Win
            elif winner == target_team:
                form.append("✅")
            
            # 3. Check for Tie
            elif winner == 'tie':
                form.append("🤝")
            
            # 4. If not NR, Win, or Tie -> It's a Loss
            else:
                form.append("❌")
                
        # Join with spaces (Left = Newest)
        return " ".join(form)

if __name__ == "__main__":
    print("Engine code loaded.")