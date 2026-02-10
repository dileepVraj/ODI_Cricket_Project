import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# 🚷 HEADLESS MOCK: Prevent IPython/Jupyter overhead in Truth Bridge
import builtins
def mock_display(*args, **kwargs): pass
builtins.display = mock_display
builtins.HTML = lambda x: x

from tests.odi.truth_bridge.base_runner import TruthBridgeBase

class RecentFormTruthBridge(TruthBridgeBase):
    def __init__(self):
        truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        super().__init__("Recent Form", truth_path)
        
        # 🩹 FIX: Base runner initializes a skeleton we don't want for this specific schema
        if "Recent Form" in self.ground_truth:
            del self.ground_truth["Recent Form"]

        print("📉 Initializing Recent Form Truth Bridge (v2.5)")
        
        # Focal teams for verification
        self.focal_teams = [
            "Australia", "Bangladesh", "England", "India", "New Zealand", 
            "Pakistan", "South Africa", "Sri Lanka", "West Indies"
        ]
        
        # Focal Rivalries for H2H Form logic
        self.focal_rivalries = [
            ("India", "Pakistan"),
            ("Australia", "England"),
            ("South Africa", "India")
        ]
        
        # Standard continents
        self.continents = ['Global', 'Asia', 'Africa', 'Europe', 'Oceania', 'Americas']

    def run(self):
        SEED_MODE = os.environ.get("SEED_MODE") == "1"
        
        # 1. Verification of General and Regional Form
        total_teams = len(self.focal_teams)
        print(f"🔎 Scanning {total_teams} teams for General & Regional Form.")

        for idx, team_name in enumerate(self.focal_teams):
            print(f"[{idx+1}/{total_teams}] 📉 Team: {team_name}")
            
            if SEED_MODE and team_name not in self.ground_truth:
                self.ground_truth[team_name] = {}

            for continent in self.continents:
                cont_param = 'All' if continent == 'Global' else continent
                
                try:
                    # Variation A: Team form in Region
                    engine_data = self.engine.analyze_team_form(team_name, opp_team='All', continent=cont_param)
                    
                    if SEED_MODE:
                        self.ground_truth[team_name][continent] = engine_data
                    else:
                        truth_scenario = self.ground_truth.get(team_name, {}).get(continent)
                        if truth_scenario:
                            self.compare([team_name, continent], engine_data, truth_scenario)
                except Exception as e:
                    print(f"      ❌ [ERROR] Engine failed for {team_name} in {continent}: {e}")

        # 2. Verification of Head-to-Head (H2H) Form logic
        print(f"\n🔎 Scanning {len(self.focal_rivalries)} Rivalries for H2H Form Logic.")
        for team_a, team_b in self.focal_rivalries:
            scenario_key = f"{team_a}_vs_{team_b}"
            print(f"⚔️ H2H Form: {team_a} vs {team_b}")
            
            # Sub-variation: Global H2H and specific Regional H2H
            # (e.g. India vs Pak in Asia is a critical check)
            check_configs = [("Global", "All")]
            if team_a == "India" or team_a == "Pakistan": check_configs.append(("Asia", "Asia"))

            for label, cont_val in check_configs:
                try:
                    # Variation B: Team vs Opponent form
                    engine_h2h = self.engine.analyze_team_form(team_a, opp_team=team_b, continent=cont_val)
                    
                    key = f"{scenario_key}_{label}"
                    if SEED_MODE:
                        if "H2H_Form" not in self.ground_truth: self.ground_truth["H2H_Form"] = {}
                        self.ground_truth["H2H_Form"][key] = engine_h2h
                    else:
                        truth_h2h = self.ground_truth.get("H2H_Form", {}).get(key)
                        if truth_h2h:
                            self.compare(["H2H", key], engine_h2h, truth_h2h)
                except Exception as e:
                    print(f"      ❌ [ERROR] H2H Engine failed for {key}: {e}")

        if SEED_MODE:
            self.save_seeded_truth()
        else:
            self.save_report(os.path.join(os.path.dirname(__file__), 'report.json'))

if __name__ == "__main__":
    runner = RecentFormTruthBridge()
    runner.run()
