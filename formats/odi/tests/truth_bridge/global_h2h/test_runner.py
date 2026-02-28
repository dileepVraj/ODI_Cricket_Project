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

class GlobalH2HTruthBridge(TruthBridgeBase):
    def __init__(self):
        truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        super().__init__("Global H2H", truth_path)
        print("🌍 Initializing Global H2H Truth Bridge (Key-Discovery Mode v2.5)")

    def run(self):
        legacy_path = 'formats/odi/tests/regression_suite/analyze_global_h2h/fixtures/analyze_global_h2h_latest_test_run_results.json'
        
        if not os.path.exists(legacy_path):
            print(f"❌ Legacy file not found: {legacy_path}")
            return

        with open(legacy_path, 'r') as f:
            legacy_data = json.load(f)
        
        SEED_MODE = os.environ.get("SEED_MODE") == "1"
        
        # 🛡️ Force Legacy Structural Isolation in SEED_MODE
        if SEED_MODE:
            self.ground_truth = {"Teams considered": legacy_data.get("Teams considered", [])}

        # 2. Discover all "Team vs rest" groups
        group_keys = [k for k in legacy_data.keys() if " vs rest" in k]
        total_groups = len(group_keys)
        print(f"🔎 Discovered {total_groups} focal groups in legacy file.")

        for g_idx, group_key in enumerate(group_keys):
            print(f"[{g_idx+1}/{total_groups}] 📁 Processing Group: {group_key}")
            matchups = legacy_data[group_key]
            
            if SEED_MODE and group_key not in self.ground_truth:
                self.ground_truth[group_key] = {}

            matchup_keys = list(matchups.keys())
            total_matchups = len(matchup_keys)

            for m_idx, matchup_key in enumerate(matchup_keys):
                scenario_data = matchups[matchup_key]
                team_a = scenario_data.get("team_a")
                team_b = scenario_data.get("team_b")
                years = scenario_data.get("years_back", 5)
                
                print(f"   ({m_idx+1}/{total_matchups}) ⚔️ Matchup: {matchup_key}")

                try:
                    # analyze_global_h2h(self, home_team, opp_team, years_back=5)
                    engine_data = self.engine.analyze_global_h2h(team_a, team_b, years_back=years)
                except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
                    print(f"      ❌ [ERROR] Engine failed for {matchup_key}: {e}")
                    continue

                if not engine_data:
                    if SEED_MODE:
                        self.ground_truth[group_key][matchup_key] = {
                            "team_a": team_a,
                            "team_b": team_b,
                            "years_back": years,
                            "expected_output": "No data available"
                        }
                    continue

                if SEED_MODE:
                    # Construct legacy-loyal structure
                    self.ground_truth[group_key][matchup_key] = {
                        "team_a": team_a,
                        "team_b": team_b,
                        "years_back": years,
                        "expected_output": engine_data
                    }
                    continue

                truth_scenario = self.ground_truth.get(group_key, {}).get(matchup_key)
                if not truth_scenario:
                    print(f"      ⚠️ Missing ground truth for {group_key} > {matchup_key}.")
                    continue

                # Use base_runner's optimized list comparison
                self.compare([group_key, matchup_key], engine_data, truth_scenario["expected_output"])

        if SEED_MODE:
            self.save_seeded_truth()
        else:
            self.save_report(os.path.join(os.path.dirname(__file__), 'report.json'))

if __name__ == "__main__":
    runner = GlobalH2HTruthBridge()
    runner.run()
