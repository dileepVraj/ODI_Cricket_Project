import sys
import os

# Add root
sys.path.append(os.getcwd())

from formats.odi.tests.truth_bridge.compare_squads.test_runner import CompareSquadsTruthBridge
from formats.odi.tests.truth_bridge.predictor_validation.test_runner import PredictorValidationRunner
from formats.odi.tests.truth_bridge.player_stats_validation.test_runner import PlayerStatsValidationRunner
from formats.odi.tests.truth_bridge.team_form_validation.test_runner import TeamFormValidationRunner

def run_all_verification():
    print("\n🔍 STARTING VERIFICATION SUITE...")
    
    bridge_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define runners and their run methods
    # (Instance, MethodName)
    runners = [
        (CompareSquadsTruthBridge(), "run"),
        (PredictorValidationRunner(
            "PredictorValidation", 
            os.path.join(bridge_dir, "predictor_validation", "ground_truth.json")
        ), "run_tests"),
        (PlayerStatsValidationRunner(
            "PlayerStatsValidation", 
            os.path.join(bridge_dir, "player_stats_validation", "ground_truth.json")
        ), "run_tests"),
        (TeamFormValidationRunner(
            "TeamFormValidation", 
            os.path.join(bridge_dir, "team_form_validation", "ground_truth.json")
        ), "run_tests")
    ]
    
    failures = 0
    passed = 0
    
    for runner, method_name in runners:
        print(f"\n🚀 Running {runner.suite_name}...")
        try:
            # Execute the run method
            getattr(runner, method_name)()
            
            # Aggregate stats
            failures += runner.results["summary"]["fail"]
            passed += runner.results["summary"]["pass"]
            
            # Save Report for standardization if not already handled
            if method_name == "run_tests":
                 # Construct default report path
                 folder = os.path.dirname(runner.truth_file)
                 report_path = os.path.join(folder, "report.json")
                 runner.save_report(report_path)
            
        except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
            print(f"❌ Runner {runner.suite_name} Failed: {e}")
            import traceback
            traceback.print_exc()
            failures += 1

    print(f"\n📊 TOTAL SUMMARY: Passed: {passed}, Failed: {failures}")
    if failures > 0:
        print("❌ VERIFICATION FAILED: Regressions Detected.")
        sys.exit(1)
    else:
        print("✅ VERIFICATION PASSED: No Regressions.")
        sys.exit(0)

if __name__ == "__main__":
    run_all_verification()
