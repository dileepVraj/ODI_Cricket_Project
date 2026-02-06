
import unittest
import sys
import os
import json
import pandas as pd

# Define Project Root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.append(PROJECT_ROOT)

# 🚨 CRITICAL FIX: Import the Facade (CricketAnalyzer) to ensure standardized data
from engine import CricketAnalyzer

# 📂 Paths
FIXTURES_DIR = os.path.join(PROJECT_ROOT, "tests/odi/analyze_toss_bias/fixtures")
GOLDEN_MASTER_FILE = os.path.join(FIXTURES_DIR, "analyze_toss_bias_expected_results.json")
REPORT_FILE = os.path.join(FIXTURES_DIR, "analyze_toss_bias_test_report.json")
DATA_FILE = os.path.join(PROJECT_ROOT, "data/FINAL_ODI_MASTER.csv")

class TestTossBiasRegression(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("🚀 Setting up Toss Bias Regression Suite...")
        if not os.path.exists(DATA_FILE):
            raise FileNotFoundError(f"❌ Data file missing: {DATA_FILE}")
            
        cls.df = pd.read_csv(DATA_FILE)
        # 🚨 CRITICAL: Ensure start_date is datetime for engine comparisons
        cls.df['start_date'] = pd.to_datetime(cls.df['start_date'], errors='coerce')
        cls.df['match_date'] = cls.df['start_date']
        # Load Database via Facade
        bot = CricketAnalyzer(DATA_FILE)
        cls.engine = bot.team_engine
        
        if not os.path.exists(GOLDEN_MASTER_FILE):
            raise FileNotFoundError(f"❌ Golden Master missing: {GOLDEN_MASTER_FILE}. Run 'generate_test_data.py' first.")
            
        with open(GOLDEN_MASTER_FILE, 'r', encoding='utf-8') as f:
            cls.golden_master = json.load(f)

    def _get_val(self, data_list, metric_name):
        for item in data_list:
            if item['Metric'] == metric_name:
                return item['Value']
        return "-"
            
    def test_venue_bias_consistency(self):
        """
        REGRESSION TEST: Compare current engine output against Golden Master for all venues.
        """
        # Load from nested structure "Toss bias report"
        if "Toss bias report" not in self.golden_master:
             self.fail("❌ Invalid Golden Master Format: Missing 'Toss bias report' key")
             
        print(f"   Structure: Grouped by Country.")
        diffs = {}
        passed = 0
        total_venues = 0
        
        # Iterate Groups
        for group, venues in self.golden_master.get("Toss bias report", {}).items():
            print(f"   📂 {group}...")
            
            for venue, expected in venues.items():
                if expected == "Insufficient Data" or isinstance(expected, str):
                    continue
                    
                total_venues += 1
                try:
                    # Run Engine (Returns List format)
                    raw_actual = self.engine.analyze_venue_bias(venue, years_back=10)
                    
                    # 1. Check Win % Bat 1st
                    actual_w1 = self._get_val(raw_actual, "Win % Batting 1st")
                    if actual_w1 != expected["Win % Batting First"]:
                         diffs[venue] = f"Win % Mismatch: Got {actual_w1}, Expected {expected['Win % Batting First']}"
                         print(f"      ❌ FAIL: {venue} (Win %)")
                         continue

                    # 2. Check Avg Score 1
                    actual_score1 = self._get_val(raw_actual, "Avg 1st Innings Score")
                    if actual_score1 != expected["Avg 1st innings score"]:
                        diffs[venue] = f"Score 1 Mismatch: {actual_score1} != {expected['Avg 1st innings score']}"
                        continue
                        
                    # If we reach here, basic checks passed
                    passed += 1
                    
                except Exception as e:
                    print(f"      🔥 EXCEPTION: {venue} -> {e}")
                    diffs[venue] = f"Exception: {str(e)}"

        # Save Report
        with open(REPORT_FILE, 'w') as f:
            json.dump(diffs, f, indent=4)
            
        # Assertions
        print(f"\n📊 Summary: {passed}/{total_venues} Passed.")
        if diffs:
            print(f"⚠️ Found {len(diffs)} regressions! Check '{REPORT_FILE}'")
            # Fail the test if any diffs found
            self.fail(f"Regression detected in {len(diffs)} venues.")
        else:
            print("✅ ALL TESTS PASSED. Logic is stable.")

if __name__ == "__main__":
    unittest.main()
