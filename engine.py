import pandas as pd
import numpy as np
import difflib
import re
import os
import logging  # <--- NEW IMPORT

from venues import VENUE_MAP
from core.team_engine import TeamEngine
from core.player_engine import PlayerEngine
from core.predictor import PredictorEngine

# ==============================================================================
# 🛡️ JUPYTER-PROOF LOGGER SETUP
# ==============================================================================
logger = logging.getLogger("CricketAnalyzer")
if logger.hasHandlers():
    logger.handlers.clear()

handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class CricketAnalyzer:
    """
    🏗️ THE FACADE (Manager)
    This class manages Data Loading and delegates analysis to specialized Core Engines.
    It maintains the exact public API of the old Monolith for interface compatibility.
    Now supports Hot Reloading (v3.0).
    """
    def __init__(self, filepath):
        self.filepath = filepath # Store for reloading
        print(f"⚙️ Initializing Smart Engine (v2.1 - Robust)...")
        self.load_data() # <--- CALLS THE NEW LOADER

    def load_data(self):
        """
        🔥 HOT RELOAD FUNCTION
        Reads the CSV again and rebuilds all sub-engines.
        """
        print(f"📂 Loading Database: {self.filepath}")
    
        # 1. Load Match Data
        CACHE_PATH = self.filepath.replace('.csv', '.pkl')
        
        # Check if Cache Exists and is Valid (Newer than CSV)
        use_cache = False
        if os.path.exists(CACHE_PATH):
            csv_mtime = os.path.getmtime(self.filepath)
            cache_mtime = os.path.getmtime(CACHE_PATH)
            if cache_mtime > csv_mtime:
                use_cache = True
        
        if use_cache:
            print(f"🚀 FAST LOAD: Reading from Cache ({CACHE_PATH})...")
            self.raw_df = pd.read_pickle(CACHE_PATH)
        else:
            print(f"⏳ SLOW LOAD: Reading CSV and building cache...")
            self.raw_df = pd.read_csv(self.filepath, low_memory=False)
            self.raw_df.columns = self.raw_df.columns.str.strip().str.lower()
            self.raw_df['start_date'] = pd.to_datetime(self.raw_df['start_date'], errors='coerce')
            self.raw_df['year'] = self.raw_df['start_date'].dt.year
            
            # 🚨 SELF-HEALING: Fix missing 'season' column
            if 'season' not in self.raw_df.columns:
                self.raw_df['season'] = self.raw_df['year']
                
            # 🚨 GLOBAL SORT
            self.raw_df = self.raw_df.sort_values(['start_date', 'match_id'])
            
            # SAVE CACHE
            print(f"💾 Saving Cache to {CACHE_PATH}...")
            self.raw_df.to_pickle(CACHE_PATH)
            
        print(f"   Raw Data: {len(self.raw_df)} balls loaded.")

        # 2. Load Player Stats & Metadata & Squads
        try:
            self.player_df = pd.read_csv('data/processed_player_stats.csv')
            self.meta_df = pd.read_csv('data/player_metadata.csv')
            print(f"✅ Player Data Loaded: {len(self.player_df)} stats rows.")
        except FileNotFoundError:
            self.player_df = pd.DataFrame()
            self.meta_df = pd.DataFrame()
            
        # 🆕 LOAD SQUADS DB (The Missing Link)
        try:
            self.squads_df = pd.read_csv('data/MATCH_SQUADS.csv')
            # Minimize memory
            self.squads_df = self.squads_df[['match_id', 'player', 'date', 'team']]
            self.squads_df['match_id'] = self.squads_df['match_id'].astype(str) # Match raw_df type
            print(f"✅ Squads Database Loaded: {len(self.squads_df)} entries.")
        except FileNotFoundError:
            self.squads_df = pd.DataFrame(columns=['match_id', 'player'])
            print("⚠️ Squads DB Missing. 'DNB' logic will be usage-based only.")
        
        # 3. Build Match Summary & Clean Venues
        self._create_match_summary()
        self._fix_ambiguous_venues()
        self._smart_standardize_venues()
        
        print(f"✅ Engine Ready! Condensed into {len(self.match_df)} unique matches.")

        # =========================================================================
        # 🤖 INITIALIZE SUB-ENGINES
        # =========================================================================
        self.team_engine = TeamEngine(self.match_df)
        self.team_engine = TeamEngine(self.match_df)
        self.player_engine = PlayerEngine(self.raw_df, self.player_df, self.meta_df, self.squads_df)
        self.predictor_engine = PredictorEngine(self.raw_df, self.player_df)

    def reload_database(self):
        """Public method to trigger the reload safely."""
        print("\n🔄 RELOADING DATABASE FROM DISK...")
        # Delete cache to force fresh load
        CACHE_PATH = self.filepath.replace('.csv', '.pkl')
        if os.path.exists(CACHE_PATH):
            os.remove(CACHE_PATH)
            print("🗑️ Cache cleared.")
        self.load_data()
        print("✅ DATABASE RELOAD COMPLETE.\n")

    def _create_match_summary(self):
        print("   🔨 Building Match Summary...")
        wicket_col = 'is_wicket' if 'is_wicket' in self.raw_df.columns else 'player_dismissed'
        agg_func_wicket = 'sum' if wicket_col == 'is_wicket' else 'count'
        
        # Handle Extras
        for col in ['wides', 'noballs', 'wide', 'no_ball']:
            if col in self.raw_df.columns: self.raw_df[col] = self.raw_df[col].fillna(0)

        w_col = 'wides' if 'wides' in self.raw_df.columns else 'wide'
        n_col = 'noballs' if 'noballs' in self.raw_df.columns else 'no_ball'
        
        # Legal Ball Logic
        if w_col in self.raw_df.columns and n_col in self.raw_df.columns:
            self.raw_df['is_legal_ball'] = ((self.raw_df[w_col] == 0) & (self.raw_df[n_col] == 0)).astype(int)
        else:
            self.raw_df['is_legal_ball'] = 1 

        # Group by Innings
        innings_stats = self.raw_df.groupby(['match_id', 'innings']).agg({
            'runs_off_bat': 'sum', 'extras': 'sum',
            'is_legal_ball': 'sum', wicket_col: agg_func_wicket 
        }).reset_index()
        
        innings_stats = innings_stats[innings_stats['innings'].isin([1, 2])]
        innings_stats.rename(columns={wicket_col: 'wickets', 'is_legal_ball': 'legal_balls'}, inplace=True)
        innings_stats['total_score'] = innings_stats['runs_off_bat'] + innings_stats['extras']
        
        def format_score(row):
            return f"{int(row['total_score'])}/{int(row['wickets'])} ({row['legal_balls'] // 6}.{row['legal_balls'] % 6})"

        innings_stats['score_display'] = innings_stats.apply(format_score, axis=1)

        scores = innings_stats.pivot(index='match_id', columns='innings', values='total_score').add_prefix('score_inn').reset_index()
        balls = innings_stats.pivot(index='match_id', columns='innings', values='legal_balls').add_prefix('balls_inn').reset_index()
        wickets = innings_stats.pivot(index='match_id', columns='innings', values='wickets').add_prefix('wickets_inn').reset_index()
        display_s = innings_stats.pivot(index='match_id', columns='innings', values='score_display').add_prefix('display_inn').reset_index()
        
        # 🚨 ROBUST COLUMN SELECTION
        # Only select columns that definitely exist
        cols = ['match_id', 'year', 'start_date', 'venue', 'batting_team', 'bowling_team', 'winner']
        if 'season' in self.raw_df.columns: cols.append('season')
        if 'method' in self.raw_df.columns: cols.append('method')
        
        meta = self.raw_df.drop_duplicates(subset='match_id')[cols].copy()
        
        # Polyfill missing columns for downstream compatibility
        if 'season' not in meta.columns: meta['season'] = meta['year']
        if 'method' not in meta.columns: meta['method'] = np.nan
            
        meta.rename(columns={'batting_team': 'team_bat_1', 'bowling_team': 'team_bat_2'}, inplace=True)
        
        self.match_df = pd.merge(meta, scores, on='match_id', how='left')
        self.match_df = pd.merge(self.match_df, balls, on='match_id', how='left')
        self.match_df = pd.merge(self.match_df, wickets, on='match_id', how='left')
        self.match_df = pd.merge(self.match_df, display_s, on='match_id', how='left')
        
        self.match_df.fillna(0, inplace=True)
        self.match_df['is_defended'] = self.match_df['winner'] == self.match_df['team_bat_1']
        self.match_df['is_chased'] = self.match_df['winner'] == self.match_df['team_bat_2']

    def _fix_ambiguous_venues(self):
        print("   🔧 Auto-Fixing Ambiguous Venues...")
        def fix(row):
            if row['venue'] == 'The Oval':
                month = row['start_date'].month
                if 'West Indies' in [row['team_bat_1'], row['team_bat_2']] and month < 6: return 'Kensington Oval, Barbados'
                elif 'New Zealand' in [row['team_bat_1'], row['team_bat_2']] and month in [11, 12, 1, 2, 3]: return 'University Oval, Dunedin'
                return 'The Oval, London'
            return row['venue']
        self.match_df['venue'] = self.match_df.apply(fix, axis=1)

    def _smart_standardize_venues(self):
        print("   🧠 Applying Smart Venue Matching (Exact -> Substring -> Fuzzy)...")
        unique_raw = self.match_df['venue'].unique()
        corrections = {}
        
        clean_keys = {self._clean_string(k): k for k in VENUE_MAP.keys()}
        
        for raw in unique_raw:
            if not isinstance(raw, str): continue
            
            if raw in VENUE_MAP:
                corrections[raw] = VENUE_MAP[raw]; continue
            
            clean_raw = self._clean_string(raw)
            
            if clean_raw in clean_keys:
                corrections[raw] = VENUE_MAP[clean_keys[clean_raw]]; continue
            
            found_substring = False
            for c_key, original_key in clean_keys.items():
                if len(c_key) > 5 and c_key in clean_raw:
                    corrections[raw] = VENUE_MAP[original_key]
                    found_substring = True
                    break
            
            if found_substring: continue

            matches = difflib.get_close_matches(raw, VENUE_MAP.keys(), n=1, cutoff=0.80)
            if matches: corrections[raw] = VENUE_MAP[matches[0]]
            else: corrections[raw] = raw 
            
        self.match_df['venue'] = self.match_df['venue'].map(corrections).fillna(self.match_df['venue'])

    def _clean_string(self, s):
        return re.sub(r'[^\w\s]', '', str(s)).lower().strip()

    # =================================================================================
    # 3. DELEGATED METHODS (The Interface connects to these)
    # =================================================================================

    def analyze_home_fortress(self, *args, **kwargs):
        return self.team_engine.analyze_home_fortress(*args, **kwargs)

    def analyze_venue_matchup(self, stadium_name, home_team, opp_team, years_back=5, recorder=None):
        return self.team_engine.analyze_home_fortress(stadium_name, home_team, opp_team, years_back, recorder)

    def analyze_venue_phases(self, *args, **kwargs):
        return self.team_engine.analyze_venue_phases(*args, **kwargs)

    def analyze_venue_bias(self, *args, **kwargs):
        return self.team_engine.analyze_venue_bias(*args, **kwargs)

    def analyze_global_h2h(self, *args, **kwargs):
        return self.team_engine.analyze_global_h2h(*args, **kwargs)

    def analyze_country_h2h(self, *args, **kwargs):
        return self.team_engine.analyze_country_h2h(*args, **kwargs)

    def analyze_home_dominance(self, *args, **kwargs):
        return self.team_engine.analyze_home_dominance(*args, **kwargs)

    def analyze_away_performance(self, *args, **kwargs):
        return self.team_engine.analyze_away_performance(*args, **kwargs)

    def analyze_global_performance(self, *args, **kwargs):
        return self.team_engine.analyze_global_performance(*args, **kwargs)

    def analyze_continent_performance(self, *args, **kwargs):
        return self.team_engine.analyze_continent_performance(*args, **kwargs)

    def analyze_team_form(self, *args, **kwargs):
        return self.team_engine.analyze_team_form(*args, **kwargs)
    
    def check_recent_form(self, *args, **kwargs):
        return self.team_engine.analyze_team_form(*args, **kwargs)

    def get_active_squad(self, *args, **kwargs):
        return self.player_engine.get_active_squad(*args, **kwargs)

    def compare_squads(self, *args, **kwargs):
        return self.player_engine.compare_squads(*args, **kwargs)

    def analyze_player_profile(self, *args, **kwargs):
        return self.player_engine.analyze_player_profile(*args, **kwargs)

    def predict_score(self, *args, **kwargs):
        return self.predictor_engine.predict_score(*args, **kwargs)
    
    def get_last_match_xi(self, team_name):
        return self.player_engine.get_last_match_xi(team_name)
    

if __name__ == "__main__":
    print("✅ Facade Engine Loaded. Ready to serve.")