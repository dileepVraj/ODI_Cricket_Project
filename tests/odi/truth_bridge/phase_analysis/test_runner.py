import os
import sys
import json
import pandas as pd
from tests.odi.truth_bridge.base_runner import TruthBridgeBase
from venues import VENUE_MAP

class PhaseAnalysisTruthBridge(TruthBridgeBase):
    def __init__(self):
        truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        super().__init__("Phase Analysis Report", truth_path)
        
        # 🩹 FIX: Base runner initializes a skeleton we don't want for this specific schema
        if "Phase Analysis Report" in self.ground_truth:
             del self.ground_truth["Phase Analysis Report"]

        print("🕒 Initializing Phase Analysis Truth Bridge (Focal Mode v2.5)")
        
        # Focal Venues (2 per major region to stay efficient)
        self.focal_venues = [
            "IND_MUMBAI_WANKHEDE", "IND_AHMEDABAD_NARENDRA", 
            "AUS_MELBOURNE_MCG", "AUS_SYDNEY_SCG",
            "ENG_LONDON_LORDS", "ENG_NOTTINGHAM_TRENT",
            "SA_JOHANNESBURG_WANDERERS", "PAK_LAHORE_GADDAFI"
        ]
        
        # Focal Opponents for matchup verification
        self.focal_opponents = ["India", "Australia", "England", "South Africa"]
        
        # Standardize: 10 Years Back
        self.years = 10

    def run(self):
        SEED_MODE = os.environ.get("SEED_MODE") == "1"
        
        print(f"🔎 Scanning Phase Analysis for {len(self.focal_venues)} focal venues...")
        
        for idx, venue_id in enumerate(self.focal_venues):
            print(f"[{idx+1}/{len(self.focal_venues)}] 🕒 Processing Venue: {venue_id}")
            
            # Extract Host Country from Venue ID (e.g. IND)
            host_code = venue_id.split('_')[0]
            prefix_map = {"IND": "India", "AUS": "Australia", "ENG": "England", "SA": "South Africa", "PAK": "Pakistan"}
            host_team = prefix_map.get(host_code)
            
            # --- 1. BASELINE (Host vs All) ---
            try:
                engine_baseline = self.engine.analyze_venue_phases(
                    venue_id, home_team=host_team, away_team=None, years=self.years
                )
                
                if SEED_MODE:
                    if not self.ground_truth: self.ground_truth = {}
                    if venue_id not in self.ground_truth: self.ground_truth[venue_id] = {}
                    self.ground_truth[venue_id]["Baseline"] = engine_baseline
                else:
                    truth_baseline = self.ground_truth.get(venue_id, {}).get("Baseline")
                    if truth_baseline:
                        self.compare([venue_id, "Baseline"], engine_baseline, truth_baseline)

                # --- 2. KEY MATCHUP (Host vs 1 Rival) ---
                if host_team:
                    # Pick a rival different from host
                    rival = [t for t in self.focal_opponents if t != host_team][0]
                    engine_matchup = self.engine.analyze_venue_phases(
                        venue_id, home_team=host_team, away_team=rival, years=self.years
                    )
                    
                    if SEED_MODE:
                        self.ground_truth[venue_id][f"vs_{rival}"] = engine_matchup
                    else:
                        truth_matchup = self.ground_truth.get(venue_id, {}).get(f"vs_{rival}")
                        if truth_matchup:
                            self.compare([venue_id, f"vs_{rival}"], engine_matchup, truth_matchup)

            except Exception as e:
                print(f"      ❌ [ERROR] Engine failed for {venue_id}: {e}")

        if SEED_MODE:
            self.save_seeded_truth()
        else:
            self.save_report(os.path.join(os.path.dirname(__file__), 'report.json'))

if __name__ == "__main__":
    runner = PhaseAnalysisTruthBridge()
    runner.run()
