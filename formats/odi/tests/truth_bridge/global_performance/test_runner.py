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

class GlobalPerformanceTruthBridge(TruthBridgeBase):
    def __init__(self):
        truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        super().__init__("Global Performance", truth_path)
        
        # 🩹 FIX: Base runner initializes a skeleton we don't want for this specific schema
        # We want strict adherence to the "Teams considered" root structure
        if "Global Performance" in self.ground_truth:
            del self.ground_truth["Global Performance"]

        print("🌍 Initializing Global Performance Truth Bridge (Key-Discovery Mode v2.5)")
        # Focal teams for discovery since no legacy fixture exists
        self.focal_teams = [
            "Australia", "Bangladesh", "England", "India", "New Zealand", 
            "Pakistan", "South Africa", "Sri Lanka", "West Indies"
        ]

    def run(self):
        SEED_MODE = os.environ.get("SEED_MODE") == "1"
        
        # In SEED_MODE for global performance, we start fresh if ground truth doesn't exist
        # or we update existing keys if it does.
        
        total_teams = len(self.focal_teams)
        print(f"🔎 Scanning {total_teams} focal teams for Global Performance.")

        for idx, team_name in enumerate(self.focal_teams):
            print(f"[{idx+1}/{total_teams}] 🌍 Processing Team: {team_name}")
            
            # Use standard 10 years back for consistency with other suites
            years = 10 
            
            try:
                # analyze_global_performance(self, team_name, years_back=5)
                # We enforce 10 years to match other benchmarks
                engine_data = self.engine.analyze_global_performance(team_name, years_back=years)
            except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
                print(f"      ❌ [ERROR] Engine failed for {team_name}: {e}")
                continue

            if SEED_MODE:
                # Initialize with explicit order if empty
                if not self.ground_truth:
                    self.ground_truth = {"Teams considered": self.focal_teams}
                elif "Teams considered" not in self.ground_truth:
                    # If exists but missing key, insert at top (Python 3.7+ preserves insertion order, 
                    # but for JSON dump typically we construct a new dict to ensure order)
                    new_gt = {"Teams considered": self.focal_teams}
                    new_gt.update(self.ground_truth)
                    self.ground_truth = new_gt

                # Construct schema
                self.ground_truth[team_name] = {
                    "team": team_name,
                    "years_back": years,
                    "expected_output": engine_data
                }
                continue

            truth_scenario = self.ground_truth.get(team_name)
            if not truth_scenario:
                print(f"      ⚠️ Missing ground truth for {team_name}. Run in SEED_MODE to generate.")
                continue

            # Matrix comparison (list of dicts)
            self.compare([team_name], engine_data, truth_scenario["expected_output"])

        if SEED_MODE:
            self.save_seeded_truth()
        else:
            self.save_report(os.path.join(os.path.dirname(__file__), 'report.json'))

if __name__ == "__main__":
    runner = GlobalPerformanceTruthBridge()
    runner.run()
