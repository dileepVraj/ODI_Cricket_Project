import os
import sys
import json
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))

# 🚷 HEADLESS MOCK: Prevent IPython/Jupyter overhead in Truth Bridge
import builtins
def mock_display(*args, **kwargs): pass
builtins.display = mock_display
builtins.HTML = lambda x: x

from formats.odi.tests.truth_bridge.base_runner import TruthBridgeBase
from config.shared.venues import VENUE_MAP

class TossBiasTruthBridge(TruthBridgeBase):
    def __init__(self):
        truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        super().__init__("Toss Policy", truth_path)
        print("🪙 Initializing Toss Bias Truth Bridge (Legacy Fixture Mode v2.5)")
        
        # Standardize: 10 Years Back
        self.years = 10
        
        # Load Venues from shared config
        # VENUE_MAP is Name->ID. We need to invert it to get unique IDs and group by Country.
        self.target_venues = self._group_venues_by_country(VENUE_MAP)

    def _group_venues_by_country(self, venue_map):
        """Helper to group IND_MUMBAI -> 'India' based on prefix."""
        unique_ids = sorted(list(set(venue_map.values())))
        grouped = {}
        
        prefix_map = {
            "AUS": "Australia", "BAN": "Bangladesh", "ENG": "England",
            "IND": "India", "IRE": "Ireland", "NZ": "New Zealand",
            "PAK": "Pakistan", "SA": "South Africa", "SL": "Sri Lanka",
            "WI": "West Indies", "ZIM": "Zimbabwe", "UAE": "UAE",
            "AFG": "Afghanistan", "SCO": "Scotland", "NED": "Netherlands"
        }
        
        for vid in unique_ids:
            # Extract prefix (e.g., IND from IND_MUMBAI)
            parts = vid.split('_')
            if not parts: continue
            code = parts[0]
            
            country_name = prefix_map.get(code, "Others")
            if country_name not in grouped: grouped[country_name] = []
            grouped[country_name].append(vid)
            
        return grouped

    def run(self):
        SEED_MODE = os.environ.get("SEED_MODE") == "1"
        results = {}
        
        # Reset if seeding
        if SEED_MODE and os.path.exists(self.truth_file):
            print("🌱 SEED MODE: Resetting ground truth...")
            self.ground_truth = {"Toss bias report": {}, "Toss Policy": {"Details": {}, "Stats": {}}}

        print(f"🔎 Scanning Venues in {len(self.target_venues)} countries...")

        for country, venues in self.target_venues.items():
            country_key = f"Grounds in {country}"
            print(f"🌍 Processing {country} ({len(venues)} venues)...")
            
            country_results = {}
            
            for venue_code in venues:
                try:
                    # analyze_venue_bias(stadium_name, years_back=10)
                    engine_raw = self.engine.analyze_venue_bias(venue_code, years_back=self.years)
                    
                    if not engine_raw:
                        # Handle 'Insufficient Data' case
                        country_results[venue_code] = "Insufficient Data"
                        continue
                    
                    # 🌉 BRIDGING: Map new Headless snake_case (ints) to Legacy Display (strings)
                    engine_data = {
                        "Period": f"Last {self.years} years",
                        "Matches analyzed": engine_raw['total_matches'],
                        "Bias Verdict": engine_raw['bias_verdict'],
                        "Win % Batting First": f"{engine_raw['bat1_win_pct']}% ({engine_raw['bat1_wins']})",
                        "Win % Chasing": f"{engine_raw['chase_win_pct']}% ({engine_raw['chase_wins']})",
                        "Avg 1st innings score": engine_raw['avg_1st_inn'],
                        "Avg 2nd innings score": engine_raw['avg_2nd_inn'],
                        "MATCH_IDS": engine_raw['MATCH_IDS']
                    }
                    
                    country_results[venue_code] = engine_data
                    
                except Exception as e:
                    print(f"      ❌ [ERROR] Engine failed for {venue_code}: {e}")
                    continue

            if SEED_MODE:
                # Update Ground Truth Structure
                if "Toss bias report" not in self.ground_truth:
                    self.ground_truth["Toss bias report"] = {}
                self.ground_truth["Toss bias report"][country_key] = country_results
            else:
                # Verification Mode
                expected_country_data = self.ground_truth.get("Toss bias report", {}).get(country_key, {})
                for venue_code, actual_val in country_results.items():
                    expected_val = expected_country_data.get(venue_code)
                    
                    if expected_val is None:
                        print(f"      ⚠️ New Venue Found: {venue_code} (Not in Truth). Run SEED to capture.")
                        continue
                        
                    # Compare
                    self.compare([country_key, venue_code], actual_val, expected_val)

        if SEED_MODE:
            self.save_seeded_truth()
        else:
            self.save_report(os.path.join(os.path.dirname(__file__), 'report.json'))

if __name__ == "__main__":
    runner = TossBiasTruthBridge()
    runner.run()
