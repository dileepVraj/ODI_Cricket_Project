"""
engine.py — The CricketAnalyzer Facade (v3.0 — Format-Aware)

The single entry point for all cricket analysis. Manages data loading and
delegates analysis to specialized Core Engines.

Supports two initialization modes:
    1. Legacy:  CricketAnalyzer("formats/odi/data/FINAL_ODI_MASTER.csv")
    2. Modern:  CricketAnalyzer(format_type="odi")

Both produce an identical, fully functional analyzer.
"""
import os
import re
import logging
import difflib

import pandas as pd
import numpy as np

from config.shared.venues import VENUE_MAP
from config.format_registry import FORMATS, get_format_engines
from core.data_loader import load_csv_or_pickle

# ==============================================================================
# JUPYTER-PROOF LOGGER SETUP
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
    The Facade (Manager) — v3.0 Format-Aware.

    Manages Data Loading and delegates analysis to specialized Core Engines.
    Now supports dynamic format selection via the Format Registry.
    """

    def __init__(self, filepath=None, format_type="odi"):
        """
        Initialize the analyzer.

        Args:
            filepath:    Path to the master CSV file (legacy mode).
                         If provided, auto-detects format from path.
            format_type: Format key from the registry (e.g., "odi", "t20i", "ipl").
                         Only used if filepath is not provided.
        """
        # Resolve format type from filepath if provided
        self.format_type = self._detect_format(filepath) if filepath else format_type

        # Load format-specific config
        try:
            from config.format_registry import get_format_config
            self.format_config = get_format_config(self.format_type)
        except (AttributeError, KeyError):
            self.format_config = {}

        # Resolve filepath
        if filepath:
            self.filepath = filepath
        else:
            self.filepath = self.format_config.get("data_file", f"formats/{self.format_type}/data/FINAL_ODI_MASTER.csv")

        logger.info(f"Initializing CricketAnalyzer (v3.0) — Format: {self.format_type.upper()}")
        self.load_data()

    @staticmethod
    def _detect_format(filepath: str) -> str:
        """Auto-detect format from the filepath string."""
        path_lower = filepath.lower().replace("\\", "/")
        for fmt_key in FORMATS:
            if f"formats/{fmt_key}/" in path_lower or f"formats\\{fmt_key}\\" in path_lower:
                return fmt_key
        return "odi"  # Default fallback

    def load_data(self):
        """
        Hot Reload function — reads data and rebuilds all sub-engines.
        Uses core.data_loader for DRY CSV/Pickle caching.
        """
        logger.info(f"Loading Database: {self.filepath}")

        # 1. RESOLVE FILEPATH (Handle legacy paths)
        if not os.path.exists(self.filepath):
            possible_fix = os.path.join('formats', self.format_type, self.filepath)
            if os.path.exists(possible_fix):
                logger.warning(f"Redirecting '{self.filepath}' -> '{possible_fix}'")
                self.filepath = possible_fix
            else:
                fallback = self.format_config.get("data_file")
                if fallback and os.path.exists(fallback):
                    logger.warning(f"Legacy path detected. Redirecting to '{fallback}'")
                    self.filepath = fallback
                else:
                    logger.error(f"Data file not found at {self.filepath}")

        # 2. LOAD DATA via shared loader (DRY — no duplicate cache logic)
        self.raw_df = load_csv_or_pickle(self.filepath)
        logger.info(f"   Raw Data: {len(self.raw_df)} balls loaded.")

        # 3. SELF-HEALING: Derive critical columns if missing
        if 'season' not in self.raw_df.columns and 'year' in self.raw_df.columns:
            self.raw_df['season'] = self.raw_df['year']

        if 'bowling_team' not in self.raw_df.columns and 'team_bat_1' in self.raw_df.columns:
            logger.info("   Deriving batting/bowling teams from match metadata...")
            self.raw_df['batting_team'] = np.where(
                self.raw_df['innings'] == 1,
                self.raw_df['team_bat_1'],
                self.raw_df['team_bat_2']
            )
            self.raw_df['bowling_team'] = np.where(
                self.raw_df['innings'] == 1,
                self.raw_df['team_bat_2'],
                self.raw_df['team_bat_1']
            )

        data_dir = os.path.dirname(self.filepath)

        # 4. LOAD PLAYER STATS & METADATA
        try:
            p_stats_path = self.format_config.get(
                "player_stats_file",
                os.path.join(data_dir, 'processed_player_stats.csv')
            )
            p_meta_path = self.format_config.get(
                "metadata_file",
                os.path.join(data_dir, 'player_metadata.csv')
            )
            self.player_df = pd.read_csv(p_stats_path)
            self.meta_df = pd.read_csv(p_meta_path)
            logger.info(f"   Player Data Loaded: {len(self.player_df)} stats rows.")
        except FileNotFoundError as e:
            logger.warning(f"   Player data not found: {e}")
            self.player_df = pd.DataFrame()
            self.meta_df = pd.DataFrame()

        # 5. LOAD SQUADS DB
        try:
            squads_path = self.format_config.get(
                "squads_file",
                os.path.join(data_dir, 'MATCH_SQUADS.csv')
            )
            self.squads_df = pd.read_csv(squads_path)
            self.squads_df = self.squads_df[['match_id', 'player', 'date', 'team']]
            self.squads_df['match_id'] = self.squads_df['match_id'].astype(str)
            logger.info(f"   Squads Database Loaded: {len(self.squads_df)} entries.")
        except FileNotFoundError:
            self.squads_df = pd.DataFrame(columns=['match_id', 'player'])
            logger.warning("   Squads DB Missing. 'DNB' logic will be usage-based only.")

        # 6. BUILD MATCH SUMMARY & CLEAN VENUES
        self._create_match_summary()
        self._fix_ambiguous_venues()
        self._smart_standardize_venues()

        logger.info(f"   Engine Ready! Condensed into {len(self.match_df)} unique matches.")

        # 7. INITIALIZE SUB-ENGINES (Format-Aware)
        engines = get_format_engines(self.format_type)

        TeamEngineClass = engines.get("TeamEngine")
        PlayerEngineClass = engines.get("PlayerEngine")
        PredictorEngineClass = engines.get("PredictorEngine")

        if TeamEngineClass:
            self.team_engine = TeamEngineClass(self.match_df)
        else:
            logger.warning(f"   No TeamEngine for format '{self.format_type}'")

        if PlayerEngineClass:
            self.player_engine = PlayerEngineClass(
                self.raw_df, self.player_df, self.meta_df, self.squads_df
            )
        else:
            logger.warning(f"   No PlayerEngine for format '{self.format_type}'")

        if PredictorEngineClass:
            self.predictor_engine = PredictorEngineClass(self.raw_df, self.player_df)
        else:
            logger.warning(f"   No PredictorEngine for format '{self.format_type}'")

    def reload_database(self):
        """Public method to trigger the reload safely."""
        logger.info("RELOADING DATABASE FROM DISK...")
        CACHE_PATH = self.filepath.replace('.csv', '.pkl')
        if os.path.exists(CACHE_PATH):
            os.remove(CACHE_PATH)
            logger.info("   Cache cleared.")
        self.load_data()
        logger.info("DATABASE RELOAD COMPLETE.")

    # =========================================================================
    # MATCH SUMMARY BUILDER
    # =========================================================================

    def _create_match_summary(self):
        logger.info("   Building Match Summary...")
        wicket_col = 'is_wicket' if 'is_wicket' in self.raw_df.columns else 'player_dismissed'
        agg_func_wicket = 'sum' if wicket_col == 'is_wicket' else 'count'

        # Handle Extras
        for col in ['wides', 'noballs', 'wide', 'no_ball']:
            if col in self.raw_df.columns:
                self.raw_df[col] = self.raw_df[col].fillna(0)

        w_col = 'wides' if 'wides' in self.raw_df.columns else 'wide'
        n_col = 'noballs' if 'noballs' in self.raw_df.columns else 'no_ball'

        # Legal Ball Logic
        if w_col in self.raw_df.columns and n_col in self.raw_df.columns:
            self.raw_df['is_legal_ball'] = (
                (self.raw_df[w_col] == 0) & (self.raw_df[n_col] == 0)
            ).astype(int)
        else:
            self.raw_df['is_legal_ball'] = 1

        # Group by Innings
        innings_stats = self.raw_df.groupby(['match_id', 'innings']).agg({
            'runs_off_bat': 'sum', 'extras': 'sum',
            'is_legal_ball': 'sum', wicket_col: agg_func_wicket
        }).reset_index()

        innings_stats = innings_stats[innings_stats['innings'].isin([1, 2])]
        innings_stats.rename(
            columns={wicket_col: 'wickets', 'is_legal_ball': 'legal_balls'}, inplace=True
        )
        innings_stats['total_score'] = innings_stats['runs_off_bat'] + innings_stats['extras']

        def format_score(row):
            return (
                f"{int(row['total_score'])}/{int(row['wickets'])} "
                f"({row['legal_balls'] // 6}.{row['legal_balls'] % 6})"
            )

        innings_stats['score_display'] = innings_stats.apply(format_score, axis=1)

        scores = innings_stats.pivot(
            index='match_id', columns='innings', values='total_score'
        ).add_prefix('score_inn').reset_index()
        balls = innings_stats.pivot(
            index='match_id', columns='innings', values='legal_balls'
        ).add_prefix('balls_inn').reset_index()
        wickets = innings_stats.pivot(
            index='match_id', columns='innings', values='wickets'
        ).add_prefix('wickets_inn').reset_index()
        display_s = innings_stats.pivot(
            index='match_id', columns='innings', values='score_display'
        ).add_prefix('display_inn').reset_index()

        # ROBUST COLUMN SELECTION
        available_cols = self.raw_df.columns.tolist()

        target_map = {
            'match_id': ['match_id'],
            'year': ['year'],
            'start_date': ['start_date'],
            'venue': ['venue'],
            'team_bat_1': ['batting_team', 'team_bat_1'],
            'team_bat_2': ['bowling_team', 'team_bat_2'],
            'winner': ['winner']
        }

        selected_cols = []
        rename_map = {}

        for target, aliases in target_map.items():
            found = next((c for c in aliases if c in available_cols), None)
            if found:
                selected_cols.append(found)
                if found != target:
                    rename_map[found] = target

        if 'season' in available_cols:
            selected_cols.append('season')
        if 'method' in available_cols:
            selected_cols.append('method')

        meta = self.raw_df.drop_duplicates(subset='match_id')[selected_cols].copy()

        if rename_map:
            meta.rename(columns=rename_map, inplace=True)

        self.match_df = pd.merge(meta, scores, on='match_id', how='left')
        self.match_df = pd.merge(self.match_df, balls, on='match_id', how='left')
        self.match_df = pd.merge(self.match_df, wickets, on='match_id', how='left')
        self.match_df = pd.merge(self.match_df, display_s, on='match_id', how='left')

        self.match_df.fillna(0, inplace=True)
        self.match_df['is_defended'] = self.match_df['winner'] == self.match_df['team_bat_1']
        self.match_df['is_chased'] = self.match_df['winner'] == self.match_df['team_bat_2']

    # =========================================================================
    # VENUE STANDARDIZATION
    # =========================================================================

    def _fix_ambiguous_venues(self):
        logger.info("   Auto-Fixing Ambiguous Venues...")

        def fix(row):
            if row['venue'] == 'The Oval':
                month = row['start_date'].month
                teams = [row['team_bat_1'], row['team_bat_2']]
                if 'West Indies' in teams and month < 6:
                    return 'Kensington Oval, Barbados'
                elif 'New Zealand' in teams and month in [11, 12, 1, 2, 3]:
                    return 'University Oval, Dunedin'
                return 'The Oval, London'
            return row['venue']

        self.match_df['venue'] = self.match_df.apply(fix, axis=1)

    def _smart_standardize_venues(self):
        logger.info("   Applying Smart Venue Matching (Exact -> Substring -> Fuzzy)...")
        unique_raw = self.match_df['venue'].unique()
        corrections = {}

        clean_keys = {self._clean_string(k): k for k in VENUE_MAP.keys()}

        for raw in unique_raw:
            if not isinstance(raw, str):
                continue

            if raw in VENUE_MAP:
                corrections[raw] = VENUE_MAP[raw]
                continue

            clean_raw = self._clean_string(raw)

            if clean_raw in clean_keys:
                corrections[raw] = VENUE_MAP[clean_keys[clean_raw]]
                continue

            found_substring = False
            for c_key, original_key in clean_keys.items():
                if len(c_key) > 5 and c_key in clean_raw:
                    corrections[raw] = VENUE_MAP[original_key]
                    found_substring = True
                    break

            if found_substring:
                continue

            matches = difflib.get_close_matches(raw, VENUE_MAP.keys(), n=1, cutoff=0.80)
            if matches:
                corrections[raw] = VENUE_MAP[matches[0]]
            else:
                corrections[raw] = raw

        self.match_df['venue'] = (
            self.match_df['venue'].map(corrections).fillna(self.match_df['venue'])
        )

    @staticmethod
    def _clean_string(s):
        return re.sub(r'[^\w\s]', '', str(s)).lower().strip()

    # =========================================================================
    # DELEGATED METHODS (The Interface connects to these)
    # =========================================================================

    def analyze_home_fortress(self, *args, **kwargs):
        return self.team_engine.analyze_home_fortress(*args, **kwargs)

    def analyze_venue_matchup(self, stadium_name, home_team, opp_team,
                              years_back=5, recorder=None):
        return self.team_engine.analyze_home_fortress(
            stadium_name, home_team, opp_team, years_back, recorder
        )

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
    logger.info("Facade Engine Loaded. Ready to serve.")