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

class ContinentPerformanceTruthBridge(TruthBridgeBase):
    def __init__(self):
        truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        super().__init__("Continent Performance", truth_path)
        
        # 🩹 FIX: Base runner initializes a skeleton we don't want for this specific schema
        if "Continent Performance" in self.ground_truth:
             del self.ground_truth["Continent Performance"]

        print("⚖️ Initializing Continent Performance Truth Bridge (v2.5)")
        
        # Paths to legacy fixture for bootstrapping
        self.legacy_fixture_path = os.path.join(
            os.path.dirname(__file__), 
            "../../regression_suite/analyze_continent_performance/fixtures/analyze_continent_performance_latest.json"
        )

    def _load_legacy_scenarios(self):
        """Loads scenarios from the legacy fixture and flattens them."""
        try:
            with open(self.legacy_fixture_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            scenarios = {}
            for continent_group, matchups in raw_data.items():
                for matchup_name, data in matchups.items():
                    # Create a flat key for the scenario
                    scenario_key = f"{data['continent']}_{data['team']}"
                    scenarios[scenario_key] = {
                        "Meta": {
                            "team": data['team'],
                            "continent": data['continent'],
                            "years_back": data['years_back']
                        },
                        "Payload": data.get('expected_output', [])
                    }
            return scenarios
        except (OSError, ValueError, KeyError, TypeError) as e:
            print(f"⚠️ Could not load legacy scenarios: {e}")
            return {}

    def run(self):
        SEED_MODE = os.environ.get("SEED_MODE") == "1"
        
        # 1. Determine Scenario Space
        if SEED_MODE and not self.ground_truth:
            print("🆕 Bootstrapping from Legacy Scenarios...")
            scenarios = self._load_legacy_scenarios()
        else:
            scenarios = self.ground_truth

        if not scenarios:
            print("❌ No scenarios found to run. Check legacy fixture or seed ground truth.")
            return

        total_scenarios = len(scenarios)
        print(f"🔎 Scanning {total_scenarios} regional performance matrices.")

        for idx, (scenario_key, scenario_data) in enumerate(scenarios.items()):
            meta = scenario_data.get('Meta')
            if not meta:
                print(f"      ⚠️ Skipping {scenario_key}: Missing Meta.")
                continue

            print(f"[{idx+1}/{total_scenarios}] 🌏 Region: {meta['continent']} | Team: {meta['team']}")
            
            try:
                # analyze_continent_performance(self, team_name, continent, opp_team='All', years_back=5)
                # Returns list of dicts from _generate_matrix_report
                engine_data = self.engine.analyze_continent_performance(
                    meta['team'], 
                    meta['continent'], 
                    opp_team='All', 
                    years_back=meta['years_back']
                )
            except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
                print(f"      ❌ [ERROR] Engine failed for {scenario_key}: {e}")
                continue

            if SEED_MODE:
                self.ground_truth[scenario_key] = {
                    "Meta": meta,
                    "Payload": engine_data
                }
                continue

            truth_payload = scenario_data.get('Payload', [])
            if not truth_payload:
                print(f"      ⚠️ Missing ground truth payload for {scenario_key}. Run in SEED_MODE.")
                continue

            # Matrix comparison (Row-by-Row)
            # Since _generate_matrix_report returns a list of dictionaries, we use the base runner's compare
            self.compare([scenario_key, "Matrix"], engine_data, truth_payload)

        if SEED_MODE:
            self.save_seeded_truth()
        else:
            self.save_report(os.path.join(os.path.dirname(__file__), 'report.json'))

if __name__ == "__main__":
    runner = ContinentPerformanceTruthBridge()
    runner.run()
