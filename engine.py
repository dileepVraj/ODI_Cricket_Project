import pandas as pd
import numpy as np
import difflib  # <--- 🧠 THE BRAIN IMPLANT (Fuzzy Logic)
import re
from IPython.display import display
from venues import VENUE_MAP  # <--- Imports our 'Source of Truth'

class CricketAnalyzer:
    """
    The Brain of the Operation. 🧠
    Now equipped with Fuzzy Logic to auto-correct messy venue names.
    """

    def __init__(self, filepath):
        # 🧠 UNDERSTANDING & CONTEXT:
        # The Boot Sequence.
        # 1. Load Data.
        # 2. Build Stats (Runs/Wickets).
        # 3. Fix Ambiguities (Logic-based).
        # 4. SMART STANDARDIZE: The new "Fuzzy" step that fixes typos automatically.
        
        print(f"⚙️ Initializing Smart Engine...")
        print(f"📂 Loading Database: {filepath}")
        
        # Use low_memory=False to prevent DtypeWarnings
        self.raw_df = pd.read_csv(filepath, low_memory=False)
        self.raw_df.columns = self.raw_df.columns.str.strip().str.lower()
        
        self.raw_df['start_date'] = pd.to_datetime(self.raw_df['start_date'], errors='coerce')
        self.raw_df['year'] = self.raw_df['start_date'].dt.year
        
        print(f"   Raw Data: {len(self.raw_df)} balls loaded.")
        
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
            # Checks if "r premadasa stadium" is inside "r premadasa stadium colombo"
            # We look for the LONGEST known key that appears in the raw name.
            best_substring_match = None
            max_len = 0
            
            for key_clean, original_key in clean_map_keys.items():
                # We enforce len > 4 to avoid matching generic words like "oval" or "park" wrongly
                if len(key_clean) > 4 and key_clean in clean_raw:
                    if len(key_clean) > max_len:
                        max_len = len(key_clean)
                        best_substring_match = original_key
            
            if best_substring_match:
                venue_corrections[raw_name] = VENUE_MAP[best_substring_match]
                # print(f"      🔹 Substring Match: '{raw_name}' -> ID: {VENUE_MAP[best_substring_match]}")
                continue
            
            # D. Fuzzy Match (The Safety Net)
            matches = difflib.get_close_matches(raw_name, VENUE_MAP.keys(), n=1, cutoff=0.80) # Lowered to 0.80
            
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
        """
        Aggressive cleaning: lowercase, remove dots, commas, hyphens.
        'R. Premadasa, Colombo' -> 'r premadasa colombo'
        """
        if not isinstance(s, str): return str(s)
        s = re.sub(r'[^\w\s]', '', s) # Remove punctuation
        return s.lower().strip()

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
    
    def _apply_smart_filters(self, df):
        df['status'] = '✅ Included'
        if 'method' in df.columns: df.loc[df['method'].notna(), 'status'] = '❌ Excluded (Rain/DL)'
        df.loc[df['winner'].isin(['No Result', np.nan]), 'status'] = '❌ Excluded (No Result)'
        
        mask_short_game = (df['balls_inn1'] < 288) & (df['wickets_inn1'] < 10)
        df.loc[mask_short_game, 'status'] = '❌ Excluded (Shortened)'
        
        return df
    
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

    def _calculate_team_stats(self, df, team_name, is_home_analysis=False):
        # 1. Batting 1st Filter
        if is_home_analysis and team_name == 'Visitors':
            bat1 = df[df['team_bat_1'] != df['home_team_ref']]
        else:
            bat1 = df[df['team_bat_1'] == team_name]
            
        # [UPDATED] Use helper for Average, keep others as int
        avg_1st = self._get_avg_with_count(bat1, 'score_inn1')
        high_1st = int(bat1['score_inn1'].max()) if not bat1.empty else 0
        low_1st = int(bat1['score_inn1'].min()) if not bat1.empty else 0
        
        # Batting 1st & Won (Defended)
        # Note: I added a fallback check for 'is_defended' just in case. 
        # If your DF has it, it uses it. If not, it uses the standard 'winner' check.
        if 'is_defended' in bat1.columns:
            bat1_win = bat1[bat1['is_defended'] == True]
        else:
            # Robust fallback: Winner is the team that batted 1st
            bat1_win = bat1[bat1['winner'] == bat1['team_bat_1']]

        # [UPDATED] Use helper
        avg_1st_win = self._get_avg_with_count(bat1_win, 'score_inn1')
        low_defended = int(bat1_win['score_inn1'].min()) if not bat1_win.empty else 0
        
        # 2. Chasing Filter
        if is_home_analysis and team_name == 'Visitors':
            chase = df[df['team_bat_2'] != df['home_team_ref']]
        else:
            chase = df[df['team_bat_2'] == team_name]
            
        # [UPDATED] Use helper
        avg_2nd = self._get_avg_with_count(chase, 'score_inn2')
        
        # Chasing & Won
        if 'is_chased' in chase.columns:
            chase_win = chase[chase['is_chased'] == True]
        else:
             # Robust fallback: Winner is the team that batted 2nd
            chase_win = chase[chase['winner'] == chase['team_bat_2']]

        high_chased = int(chase_win['score_inn2'].max()) if not chase_win.empty else 0
        # [UPDATED] Use helper
        avg_succ_chase = self._get_avg_with_count(chase_win, 'score_inn2')
        
        # Chasing & Lost
        if 'is_chased' in chase.columns:
            chase_loss = chase[chase['is_chased'] == False]
        else:
            chase_loss = chase[chase['winner'] != chase['team_bat_2']]
            
        # [UPDATED] Use helper
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

    # -------------------------------------------------------------------------------------
    # FUNCTION 1: VENUE ANALYSIS
    # -------------------------------------------------------------------------------------
    def analyze_home_fortress(self, stadium_name, home_team, opp_team='All', years_back=10):
        # 🧠 UNDERSTANDING & CONTEXT:
        # TRADING LAYER 2: "The Fortress Check"
        # The Fuzzy Logic in __init__ has already converted "Wankhede" to "IND_MUMBAI_WANKHEDE".
        # But if the user types "Wankhede" manually in the UI, we still need to resolve it to the ID.
        
        # Quick check against our mapped values to map manual input -> Master ID
        stadium_id = stadium_name
        
        # 1. Direct check (Is it already a Master ID like 'IND_MUMBAI_WANKHEDE'?)
        if stadium_name not in VENUE_MAP.values():
            # 2. Key check (Did user type 'Wankhede'?)
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

        self._build_and_display_report(df, home_team, visitor_label, f"FORTRESS REPORT ({vs_text})", is_venue_mode=True)

    # -------------------------------------------------------------------------------------
    # FUNCTION 2: GLOBAL H2H ANALYSIS
    # -------------------------------------------------------------------------------------
    def analyze_global_h2h(self, home_team, opp_team, years_back=5):
        # 🧠 UNDERSTANDING & CONTEXT:
        # TRADING LAYER 3: "Global Rivalry"
        # Used to check current form between two teams, regardless of where they play.
        
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

        self._build_and_display_report(df, home_team, opp_team, f"GLOBAL RIVALRY REPORT", is_venue_mode=False)

    # -------------------------------------------------------------------------------------
    # FUNCTION 3: COUNTRY H2H ANALYSIS
    # -------------------------------------------------------------------------------------
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

    def analyze_country_h2h(self, home_team, opp_team, country_name, years_back=10):
        # 🧠 UNDERSTANDING & CONTEXT:
        # TRADING LAYER 4: "Host Country Analysis"
        # Includes the latest Safety Net updates (City Names, Keywords).
        
        self.match_df['start_date'] = pd.to_datetime(self.match_df['start_date'])
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        print(f"\n🗺️ COUNTRY CHECK: {home_team} vs {opp_team} in {country_name.upper()}")
        print(f"📅 Period: Last {years_back} Years")
        
        country_map = {
            'India': [
                'India', 'IND_',
                'Wankhede', 'Mumbai', 'Brabourne', 'Eden Gardens', 'Kolkata', 
                'Chidambaram', 'Chepauk', 'Chennai', 'Chinnaswamy', 'Bangalore', 'Bengaluru',
                'Narendra Modi', 'Motera', 'Ahmedabad', 'Arun Jaitley', 'Kotla', 'Delhi', 
                'Rajiv Gandhi', 'Hyderabad', 'HPCA', 'Dharamshala', 'Bindra', 'Mohali', 
                'Holkar', 'Indore', 'Saurashtra', 'Rajkot', 'Vidarbha', 'Nagpur', 
                'JSCA', 'Ranchi', 'Barabati', 'Cuttack', 'Raipur', 'Guwahati', 'Pune',
                'Barsapara', 'Greenfield', 'Trivandrum', 'Ekana', 'Lucknow', 
                'Sawai Mansingh', 'Jaipur', 'Green Park', 'Kanpur', 'Visakhapatnam'
            ],
            'Australia': [
                'Australia', 'AUS_', 
                'Melbourne', 'Sydney', 'Gabba', 'Brisbane', 'Adelaide', 'Perth', 
                'Hobart', 'Canberra', 'Darwin', 'Townsville', 'Carrara', 'Cairns'
            ],
            'England': [
                'England', 'ENG_', 
                'Lord\'s', 'Oval', 'London', 'Edgbaston', 'Birmingham', 
                'Old Trafford', 'Manchester', 'Headingley', 'Leeds', 
                'Trent Bridge', 'Nottingham', 
                'Rose Bowl', 'Southampton', 'Ageas', 'Hampshire', 'Utilita',
                'Sophia Gardens', 'Cardiff', 'Riverside', 'Durham', 'Bristol'
            ],
            'South Africa': [
                'South Africa', 'SA_',
                'Wanderers', 'Johannesburg', 'Centurion', 'Pretoria', 
                'Kingsmead', 'Durban', 'Port Elizabeth', 'Gqeberha', 
                'Newlands', 'Cape Town', 'Paarl', 'Bloemfontein', 'Potchefstroom'
            ],
            'New Zealand': [
                'New Zealand', 'NZ_',
                'Auckland', 'Hamilton', 'Wellington', 'Christchurch', 
                'Dunedin', 'Napier', 'Nelson', 'Mount Maunganui', 'Queenstown'
            ],
            'Sri Lanka': [
                'Sri Lanka', 'SL_',
                'Colombo', 'Galle', 'Kandy', 'Dambulla', 'Hambantota'
            ],
            'West Indies': [
                'West Indies', 'WI_',
                'Barbados', 'Bridgetown',           
                'Trinidad', 'Port of Spain',        
                'Guyana', 'Georgetown',             
                'Jamaica', 'Kingston',              
                'Antigua', 'North Sound',           
                'St Lucia', 'Gros Islet',           
                'Grenada', 'St George\'s',          
                'Dominica', 'Roseau',               
                'St Kitts', 'Basseterre',
                'St Vincent', 'Kingstown'
            ],
            'Pakistan': [
                'Pakistan', 'PAK_',
                'Lahore', 'Karachi', 'Rawalpindi', 'Multan', 'Faisalabad'
            ],
            'Bangladesh': [
                'Bangladesh', 'BAN_',
                'Dhaka', 'Mirpur', 'Chattogram', 'Chittagong', 'Sylhet'
            ],
            'UAE': [
                'UAE', 'United Arab Emirates', 'UAE_',
                'Dubai', 'Sharjah', 'Abu Dhabi'
            ]
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

        self._build_and_display_report(df, home_team, opp_team, f"HOST COUNTRY REPORT ({country_name})", is_venue_mode=False)

    # -------------------------------------------------------------------------------------
    # FUNCTION 5: HOME DOMINANCE CHECK (Home vs Everyone)
    # -------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    # FUNCTION 5: HOME DOMINANCE CHECK (Home vs Everyone)
    # -------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    # FUNCTION 5: HOME DOMINANCE CHECK (Home vs Everyone)
    # -------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    # FUNCTION 5: HOME DOMINANCE CHECK (Home vs Everyone)
    # -------------------------------------------------------------------------------------
    def analyze_home_dominance(self, home_team, years_back=10):
        """
        The "Hostile Host" Report. 🦁
        Shows how the Home Team performs against ALL touring teams in their own backyard.
        UPDATED: Now shows Sample Size next to Average Scores ex: 320 (5).
        """
        print(f"\n🦁 HOME DOMINANCE REPORT: {home_team} in Home Conditions")
        print(f"📅 Period: Last {years_back} Years")
        
        # 1. Determine Country Code
        country_codes = {
            'India': 'IND_', 'England': 'ENG_', 'Australia': 'AUS_',
            'South Africa': 'SA_', 'New Zealand': 'NZ_', 'Sri Lanka': 'SL_',
            'West Indies': 'WI_', 'Pakistan': 'PAK_', 'Bangladesh': 'BAN_'
        }
        
        if home_team not in country_codes:
            print(f"❌ Could not auto-detect country code for {home_team}.")
            return

        code = country_codes[home_team]
        
        # 2. Set Date Cutoff
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        # 3. Filter Matches
        home_matches = self.match_df[
            (self.match_df['venue'].str.startswith(code)) &
            ((self.match_df['team_bat_1'] == home_team) | (self.match_df['team_bat_2'] == home_team)) &
            (self.match_df['start_date'] >= cutoff_date)
        ].copy()
        
        # Clean list (Exclude Rain/Short games for stats)
        clean_df = self._apply_smart_filters(home_matches)
        valid_matches = clean_df[clean_df['status'] == '✅ Included']
        
        if home_matches.empty:
            print(f"❌ No home matches found for {home_team} in the last {years_back} years.")
            return

        print(f"📅 Analyzing {len(home_matches)} matches played in {home_team}...")
        
        # 4. Group by Opponent
        def get_opponent(row):
            return row['team_bat_2'] if row['team_bat_1'] == home_team else row['team_bat_1']

        home_matches['opponent'] = home_matches.apply(get_opponent, axis=1)
        valid_matches = valid_matches.copy()
        valid_matches['opponent'] = valid_matches.apply(get_opponent, axis=1)
        
        # 5. Build Stats Per Opponent
        opponents = home_matches['opponent'].unique()
        stats_data = []
        
        for opp in opponents:
            # Win/Loss (Use Full Data)
            vs_opp_full = home_matches[home_matches['opponent'] == opp]
            matches = len(vs_opp_full)
            wins = len(vs_opp_full[vs_opp_full['winner'] == home_team])
            losses = len(vs_opp_full[vs_opp_full['winner'] == opp])
            win_pct = int((wins / matches) * 100) if matches > 0 else 0
            
            # --- BATTING STATS (Use Clean Data) ---
            vs_opp_clean = valid_matches[valid_matches['opponent'] == opp]
            
            # A. Home Team Batting 1st Avg
            home_bat1_df = vs_opp_clean[vs_opp_clean['team_bat_1'] == home_team]
            if not home_bat1_df.empty:
                h_avg = int(home_bat1_df['score_inn1'].mean())
                h_count = len(home_bat1_df)
                h_display = f"{h_avg} ({h_count})"
            else:
                h_display = "-"
            
            # B. Visitor Batting 1st Avg
            vis_bat1_df = vs_opp_clean[vs_opp_clean['team_bat_1'] == opp]
            if not vis_bat1_df.empty:
                v_avg = int(vis_bat1_df['score_inn1'].mean())
                v_count = len(vis_bat1_df)
                v_display = f"{v_avg} ({v_count})"
            else:
                v_display = "-"
            
            stats_data.append({
                'Opponent': opp,
                'Mat': matches,
                'Won': wins,
                'Lost': losses,
                'Win %': f"{win_pct}%",
                f'{home_team} Avg (1st)': h_display, 
                'Visitor Avg (1st)': v_display
            })
            
        # 6. Create DataFrame & Sort
        report_df = pd.DataFrame(stats_data).sort_values('Mat', ascending=False)
        
        # Display Matrix
        print("\n📊 DOMINANCE MATRIX")
        def highlight_win_rate(val):
            try:
                pct = int(val.replace('%', ''))
                if pct > 60: return 'color: green; font-weight: bold'
                if pct < 40: return 'color: red; font-weight: bold'
            except: pass
            return ''

        styled = report_df.style.map(highlight_win_rate, subset=['Win %'])\
                                .hide(axis='index')
        display(styled)
        
        # 7. Display Match Audit (Pass the FULL filtered list)
        self._display_audit(home_matches, home_team)

    def _build_and_display_report(self, df, home_team, visitor_label, title, is_venue_mode):
        # 1. Apply Filters
        df = self._apply_smart_filters(df)
        
        # 2. Counts
        matches_played = len(df)
        
        home_wins_df = df[df['winner'] == home_team]
        won_home = len(home_wins_df)
        won_home_bat1 = len(home_wins_df[home_wins_df['team_bat_1'] == home_team])
        won_home_bat2 = len(home_wins_df[home_wins_df['team_bat_2'] == home_team])

        if visitor_label == 'Visitors':
            vis_wins_df = df[(df['winner'] != home_team) & (df['winner'] != 'Tie') & (df['winner'].notna())]
        else:
            vis_wins_df = df[df['winner'] == visitor_label]
            
        won_visitor = len(vis_wins_df)
        won_vis_bat1 = len(vis_wins_df[vis_wins_df['team_bat_2'] == home_team]) 
        won_vis_bat2 = len(vis_wins_df[vis_wins_df['team_bat_1'] == home_team]) 
        
        invalid_results = matches_played - won_home - won_visitor
        win_rate = int((won_home / matches_played) * 100) if matches_played > 0 else 0
        
        # 3. Averages (Clean Data Only)
        stats_df = df[df['status'] == '✅ Included'].copy()
        stats_df['home_team_ref'] = home_team 
        
        # [UPDATED] Use helper for Overall Stats
        overall_avg_1 = self._get_avg_with_count(stats_df, 'score_inn1')
        overall_avg_2 = self._get_avg_with_count(stats_df, 'score_inn2')
        
        bat1_winners = stats_df[stats_df['winner'] == stats_df['team_bat_1']]
        overall_avg_win = self._get_avg_with_count(bat1_winners, 'score_inn1')
        
        # Calculate Team Stats (Using the updated function above)
        h_stats = self._calculate_team_stats(stats_df, home_team)
        v_stats = self._calculate_team_stats(stats_df, visitor_label, is_home_analysis=True)

        # 4. Report Data
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
        display(audit_df)

if __name__ == "__main__":
    print("Engine code loaded.")