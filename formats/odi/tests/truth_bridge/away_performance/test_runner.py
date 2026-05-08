import os
import sys
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))  # noqa: E402

# 🚷 HEADLESS MOCK: Prevent IPython/Jupyter overhead in Truth Bridge
import builtins  # noqa: E402
def mock_display(*args, **kwargs): pass
builtins.display = mock_display  # type: ignore[attr-defined]
builtins.HTML = lambda x: x  # type: ignore[attr-defined]

from formats.odi.tests.truth_bridge.base_runner import TruthBridgeBase  # noqa: E402

class AwayPerformanceTruthBridge(TruthBridgeBase):
    def __init__(self):
        truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        super().__init__("Away Performance", truth_path)
        print("✈️ Initializing Away Performance Truth Bridge (Key-Discovery Mode v2.5)")

    def run(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
        legacy_path = os.path.join(
            project_root,
            "formats", "odi", "tests", "regression_suite",
            "analyze_away_performance", "fixtures",
            "analyze_away_performance_latest_test_run_results.json",
        )
        
        if not os.path.exists(legacy_path):
            print(f"❌ Legacy file not found: {legacy_path}")
            return

        with open(legacy_path, 'r', encoding='utf-8') as f:
            legacy_data = json.load(f)
        
        SEED_MODE = os.environ.get("SEED_MODE") == "1"
        
        # 🛡️ Force Legacy Structural Isolation in SEED_MODE
        if SEED_MODE:
            self.ground_truth = {"Teams considered": legacy_data.get("Teams considered", [])}

        # 1. Discover Focal Teams from the legacy fixture keys
        teams_considered = legacy_data.get("Teams considered", [])
        total_teams = len(teams_considered)
        print(f"🔎 Discovered {total_teams} focal teams for Away Performance.")

        for idx, team_name in enumerate(teams_considered):
            print(f"[{idx+1}/{total_teams}] ✈️ Processing Team: {team_name}")
            
            if team_name not in legacy_data:
                print(f"      ⚠️ focal team '{team_name}' not found as key in legacy fixture.")
                continue
                
            scenario_data = legacy_data[team_name]
            years = scenario_data.get("years_back", 10)
            
            try:
                # analyze_away_performance(self, team_name, years_back=5, recorder=None)
                engine_data = self.engine.analyze_away_performance(team_name, years_back=years)
            except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
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
    runner = AwayPerformanceTruthBridge()
    runner.run()
