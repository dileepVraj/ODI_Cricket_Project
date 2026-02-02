import unittest
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from tests.odi.analyze_away_performance.tools.run_away_regression import compare_results, EXPECTED_FILE, FINAL_REPORT_FILE

class TestAwayPerformanceRegression(unittest.TestCase):
    def test_regression_no_mismatches(self):
        """
        Runs the regression comparison and fails if any mismatches are found.
        """
        # Ensure we have a baseline
        if not os.path.exists(EXPECTED_FILE):
            self.fail(f"Baseline file not found at {EXPECTED_FILE}. Run generation script first.")

        # Run comparison (This assumes latest results are already generated or will be generated)
        # For CI/CD, we might want to trigger generation here. For now, we assume standard workflow.
        # But to be safe, let's trigger a fresh generation if we are running this test.
        from tests.odi.analyze_away_performance.tools.run_away_regression import generate_data
        generate_data()
        
        # Now compare
        compare_results()
        
        # Check report
        if os.path.exists(FINAL_REPORT_FILE):
            with open(FINAL_REPORT_FILE, 'r') as f:
                report = json.load(f)
                mismatches = report.get("mismatches", [])
                
            if mismatches:
                print("\n❌ REGRESSION FAILURES FOUND:")
                for m in mismatches:
                    print(m)
                self.fail(f"Found {len(mismatches)} regressions in Away Performance. See report.")
        else:
            # If no report file, it means compare_results didn't even run properly or logic error
            pass

if __name__ == '__main__':
    unittest.main()
