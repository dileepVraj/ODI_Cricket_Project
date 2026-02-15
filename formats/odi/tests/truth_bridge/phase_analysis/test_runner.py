import os
import sys
import json
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))

from formats.odi.tests.truth_bridge.base_runner import TruthBridgeBase
from config.shared.venues import VENUE_MAP

class PhaseAnalysisTruthBridge(TruthBridgeBase):
    def __init__(self):
        truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        super().__init__("Phase Analysis Report", truth_path)
        
        flattened = {}
        def recurse_find_venues(d):
            if not isinstance(d, dict): return
            for k, v in d.items():
                if isinstance(v, dict) and ("Baseline_Metrics" in v or "baseline" in v or "vs_India" in v):
                    flattened[k] = v
                else:
                    recurse_find_venues(v)
        
        recurse_find_venues(self.ground_truth)
        self.ground_truth = flattened
        print(f"🕒 Flattened {len(self.ground_truth)} venues. First 5: {list(self.ground_truth.keys())[:5]}")

        print(f"🕒 Flattened {len(self.ground_truth)} venues.")
        
        self.focal_venues = [
            "IND_MUMBAI_WANKHEDE", "IND_AHMEDABAD", 
            "AUS_MELBOURNE", "AUS_SYDNEY",
            "ENG_LONDON_LORDS", "ENG_NOTTINGHAM",
            "SA_JOHANNESBURG", "PAK_LAHORE"
        ]
        
        self.focal_opponents = ["India", "Australia", "England", "South Africa"]
        self.years = 10

    def run(self):
        SEED_MODE = os.environ.get("SEED_MODE") == "1"
        print(f"🔎 Scanning Phase Analysis for {len(self.focal_venues)} focal venues...")
        
        compare_count = 0
        for idx, venue_id in enumerate(self.focal_venues):
            print(f"[{idx+1}/{len(self.focal_venues)}] 🕒 Processing Venue: {venue_id}")
            host_code = venue_id.split('_')[0]
            prefix_map = {"IND": "India", "AUS": "Australia", "ENG": "England", "SA": "South Africa", "PAK": "Pakistan"}
            host_team = prefix_map.get(host_code)
            
            try:
                # --- 1. BASELINE ---
                engine_raw_baseline = self.engine.analyze_venue_phases(
                    venue_id, home_team=host_team, away_team=None, years=self.years
                )
                
                engine_baseline = {
                    "venue_baseline": engine_raw_baseline.get('baseline', {}),
                    "home_at_venue": engine_raw_baseline.get('home_at_venue', {}),
                    "away_at_venue": engine_raw_baseline.get('away_at_venue', {}),
                    "global_habits": engine_raw_baseline.get('global_habits', {}),
                    "alerts": engine_raw_baseline.get('alerts', []),
                    "MATCH_IDS": engine_raw_baseline.get('MATCH_IDS', "")
                }
                
                if SEED_MODE:
                    if venue_id not in self.ground_truth: self.ground_truth[venue_id] = {}
                    self.ground_truth[venue_id]["Baseline_Metrics"] = engine_baseline
                else:
                    truth_baseline = self.ground_truth.get(venue_id, {}).get("Baseline_Metrics")
                    if truth_baseline:
                        self.compare([venue_id, "Baseline_Metrics"], engine_baseline, truth_baseline)
                        compare_count += 1
                    else:
                        print(f"      ⚠️ No truth baseline for {venue_id}")

                # --- 2. KEY MATCHUP ---
                if host_team:
                    rival = [t for t in self.focal_opponents if t != host_team][0]
                    engine_raw_matchup = self.engine.analyze_venue_phases(
                        venue_id, home_team=host_team, away_team=rival, years=self.years
                    )
                    
                    engine_matchup = {
                        "venue_baseline": engine_raw_matchup.get('baseline', {}),
                        "home_at_venue": engine_raw_matchup.get('home_at_venue', {}),
                        "away_at_venue": engine_raw_matchup.get('away_at_venue', {}),
                        "global_habits": engine_raw_matchup.get('global_habits', {}),
                        "alerts": engine_raw_matchup.get('alerts', []),
                        "MATCH_IDS": engine_raw_matchup.get('MATCH_IDS', "")
                    }
                    
                    if SEED_MODE:
                        self.ground_truth[venue_id][f"vs_{rival}"] = engine_matchup
                    else:
                        truth_matchup = self.ground_truth.get(venue_id, {}).get(f"vs_{rival}")
                        if truth_matchup:
                            self.compare([venue_id, f"vs_{rival}"], engine_matchup, truth_matchup)
                            compare_count += 1
                        else:
                            print(f"      ⚠️ No truth matchup (vs_{rival}) for {venue_id}")

            except Exception as e:
                print(f"      ❌ [ERROR] Engine failed for {venue_id}: {e}")

        print(f"🏁 Done. Total comparisons made: {compare_count}")
        if SEED_MODE:
            self.save_seeded_truth()
        else:
            self.save_report(os.path.join(os.path.dirname(__file__), 'report.json'))

if __name__ == "__main__":
    runner = PhaseAnalysisTruthBridge()
    runner.run()
