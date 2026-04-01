import os
import sys
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))  # noqa: E402

# 🚷 HEADLESS MOCK: Prevent IPython/Jupyter overhead in Truth Bridge
import builtins
def mock_display(*args, **kwargs): pass
builtins.display = mock_display
builtins.HTML = lambda x: x

from formats.odi.tests.truth_bridge.base_runner import TruthBridgeBase  # noqa: E402

class FortressTruthBridge(TruthBridgeBase):
    def __init__(self):
        truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        super().__init__("Check Fortress", truth_path)
        # 🛡️ Legacy Template Skeleton Override
        if not os.path.exists(truth_path) or os.stat(truth_path).st_size == 0:
            self.ground_truth = {"Teams considered": []}
        print("🏰 Initializing Fortress Truth Bridge (Key-Discovery Mode v2.5)")

    def run(self):
        legacy_path = 'formats/odi/tests/regression_suite/analyze_home_fortress/fixtures/analyze_home_fortress_latest_test_run_results.json'
        
        if not os.path.exists(legacy_path):
            print(f"❌ Legacy file not found: {legacy_path}")
            return

        with open(legacy_path, 'r') as f:
            legacy_data = json.load(f)
        
        SEED_MODE = os.environ.get("SEED_MODE") == "1"
        
        # 🛡️ Legacy Template Structural Isolation
        if SEED_MODE:
            self.ground_truth = {"Teams considered": legacy_data.get("Teams considered", [])}

        # 2. Discover all "Team at Venue" keys from legacy data
        legacy_keys = [k for k in legacy_data.keys() if " at " in k]
        total_keys = len(legacy_keys)
        print(f"🔎 Discovered {total_keys} team-venue combinations in legacy file.")

        for idx, venue_key in enumerate(legacy_keys):
            parts = venue_key.split(" at ")
            home_team = parts[0]
            stadium = parts[1]
            
            scenarios = legacy_data[venue_key]
            
            if SEED_MODE and venue_key not in self.ground_truth:
                self.ground_truth[venue_key] = {}

            print(f"[{idx+1}/{total_keys}] 🏟️ Processing: {venue_key}")

            for scenario_name, scenario_data in scenarios.items():
                opp_team = scenario_data.get("opponent", "All")
                years = scenario_data.get("years_back", 10)
                
                try:
                    # engine_data is a LIST of Metric/Value dicts
                    engine_data = self.engine.analyze_home_fortress(stadium, home_team, opp_team=opp_team, years_back=years)
                except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
                    print(f"      ❌ [ERROR] Engine failed for {venue_key} ({scenario_name}): {e}")
                    continue

                if not engine_data:
                    if SEED_MODE:
                        self.ground_truth[venue_key][scenario_name] = {
                            "opponent": opp_team,
                            "years_back": years,
                            "expected_output": "No data available"
                        }
                    continue

                if SEED_MODE:
                    # Construct legacy-loyal structure
                    self.ground_truth[venue_key][scenario_name] = {
                        "opponent": opp_team,
                        "years_back": years,
                        "expected_output": engine_data
                    }
                    continue

                truth_scenario = self.ground_truth.get(venue_key, {}).get(scenario_name)
                if not truth_scenario:
                    print(f"      ⚠️ Missing ground truth for {venue_key} - {scenario_name}.")
                    continue

                # Use base_runner's optimized list comparison
                self.compare([venue_key, scenario_name], engine_data, truth_scenario["expected_output"])

        if SEED_MODE:
            self.save_seeded_truth()
        else:
            self.save_report(os.path.join(os.path.dirname(__file__), 'report.json'))

if __name__ == "__main__":
    runner = FortressTruthBridge()
    runner.run()
