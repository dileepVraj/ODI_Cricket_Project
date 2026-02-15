import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))

# 🚷 HEADLESS MOCK: Prevent IPython/Jupyter overhead in Truth Bridge
import builtins
def mock_display(*args, **kwargs): pass
builtins.display = mock_display
builtins.HTML = lambda x: x

from formats.odi.tests.truth_bridge.base_runner import TruthBridgeBase

class HomeDominanceTruthBridge(TruthBridgeBase):
    def __init__(self):
        truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        super().__init__("Home Dominance", truth_path)
        print("🦁 Initializing Home Dominance Truth Bridge (Key-Discovery Mode v2.5)")

    def run(self):
        SEED_MODE = os.environ.get("SEED_MODE") == "1"
        
        # 1. Discover Focal Teams from ground truth or search
        # If ground_truth has "Teams considered", use it. Otherwise, use all keys that aren't metadata.
        teams_considered = self.ground_truth.get("Teams considered", [])
        if not teams_considered:
             teams_considered = [k for k in self.ground_truth.keys() if k not in ["Teams considered", self.suite_name]]
        
        total_teams = len(teams_considered)
        print(f"🔎 Discovered {total_teams} focal teams for Home Dominance.")

        for idx, team_name in enumerate(teams_considered):
            print(f"[{idx+1}/{total_teams}] 🏠 Processing Team: {team_name}")
            
            years = 10 # Default
            if team_name in self.ground_truth:
                years = self.ground_truth[team_name].get("years_back", 10)
            
            try:
                # analyze_home_dominance(self, home_team, years_back=10)
                engine_data = self.engine.analyze_home_dominance(team_name, years_back=years)
            except Exception as e:
                print(f"      ❌ [ERROR] Engine failed for {team_name}: {e}")
                continue

            if not engine_data:
                if SEED_MODE:
                    self.ground_truth[team_name] = {
                        "team": team_name,
                        "years_back": years,
                        "expected_output": "No data available"
                    }
                continue

            if SEED_MODE:
                # Construct legacy-loyal structure
                self.ground_truth[team_name] = {
                    "team": team_name,
                    "years_back": years,
                    "expected_output": engine_data
                }
                continue

            truth_scenario = self.ground_truth.get(team_name)
            if not truth_scenario:
                print(f"      ⚠️ Missing ground truth for {team_name}.")
                continue

            # Matrix comparison (list of dicts)
            self.compare([team_name], engine_data, truth_scenario["expected_output"])

        if SEED_MODE:
            self.save_seeded_truth()
        else:
            self.save_report(os.path.join(os.path.dirname(__file__), 'report.json'))

if __name__ == "__main__":
    runner = HomeDominanceTruthBridge()
    runner.run()
