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

class CountryH2HTruthBridge(TruthBridgeBase):
    def __init__(self):
        truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        super().__init__("Country H2H", truth_path)
        # 🛡️ Legacy Template Structural Isolation
        if not os.path.exists(truth_path) or os.stat(truth_path).st_size == 0:
            self.ground_truth = {"Teams considered": []}
        print("🗺️ Initializing Country H2H Truth Bridge (Key-Discovery Mode v2.5)")

    def run(self):
        legacy_path = 'formats/odi/tests/regression_suite/analyze_country_h2h/fixtures/analyze_country_h2h_latest_test_run_results.json'
        
        if not os.path.exists(legacy_path):
            print(f"❌ Legacy file not found: {legacy_path}")
            return

        with open(legacy_path, 'r') as f:
            legacy_data = json.load(f)
        
        SEED_MODE = os.environ.get("SEED_MODE") == "1"
        
        # 1. Sync Teams Considered
        if SEED_MODE:
            self.ground_truth["Teams considered"] = legacy_data.get("Teams considered", [])

        # 2. Discover all composite keys (e.g., "Australia: Australia vs England")
        # Legacy items have "home_team" and "opp_team" keys
        legacy_keys = [k for k in legacy_data.keys() if isinstance(legacy_data[k], dict) and "home_team" in legacy_data[k]]
        total_keys = len(legacy_keys)
        print(f"🔎 Discovered {total_keys} country-H2H combinations in legacy file.")

        for idx, composite_key in enumerate(legacy_keys):
            scenario_data = legacy_data[composite_key]
            home_team = scenario_data.get("home_team")
            opp_team = scenario_data.get("opp_team")
            host_country = scenario_data.get("host_country")
            years = scenario_data.get("years_back", 10)
            
            print(f"[{idx+1}/{total_keys}] 🗺️ Processing: {composite_key}")

            try:
                # analyze_country_h2h(self, home_team, opp_team, country_name, years_back=10)
                engine_data = self.engine.analyze_country_h2h(home_team, opp_team, host_country, years_back=years)
            except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
                print(f"      ❌ [ERROR] Engine failed for {composite_key}: {e}")
                continue

            if not engine_data:
                if SEED_MODE:
                    self.ground_truth[composite_key] = {
                        "home_team": home_team,
                        "opp_team": opp_team,
                        "host_country": host_country,
                        "years_back": years,
                        "expected_output": "No data available"
                    }
                continue

            if SEED_MODE:
                # Construct legacy-loyal structure
                self.ground_truth[composite_key] = {
                    "home_team": home_team,
                    "opp_team": opp_team,
                    "host_country": host_country,
                    "years_back": years,
                    "expected_output": engine_data
                }
                continue

            truth_scenario = self.ground_truth.get(composite_key)
            if not truth_scenario:
                print(f"      ⚠️ Missing ground truth for {composite_key}.")
                continue

            # Use base_runner's optimized list comparison
            self.compare([composite_key], engine_data, truth_scenario["expected_output"])

        if SEED_MODE:
            self.save_seeded_truth()
        else:
            self.save_report(os.path.join(os.path.dirname(__file__), 'report.json'))

if __name__ == "__main__":
    runner = CountryH2HTruthBridge()
    runner.run()
