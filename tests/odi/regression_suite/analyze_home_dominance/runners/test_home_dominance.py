import unittest
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from engine import CricketAnalyzer

class TestHomeDominance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = CricketAnalyzer("data/FINAL_ODI_MASTER.csv")
        cls.fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
        cls.fixture_file = os.path.join(cls.fixtures_dir, "analyze_home_dominance_expected_results.json")

    def test_home_dominance_scenarios(self):
        """Run all Home Dominance scenarios from expected_results.json"""
        if not os.path.exists(self.fixture_file):
            print(f"⚠️ Fixture file not found: {self.fixture_file}")
            return

        with open(self.fixture_file, 'r') as f:
            all_data = json.load(f)

        print(f"\n🦁 Running Home Dominance Tests from Fixture...")
        
        for team_key, data in all_data.items():
            if team_key == "Teams considered": continue
            
            # Data validation
            if "expected_output" not in data: continue
            
            team = data.get("team")
            years = data.get("years_back", 10)
            expected_raw = data["expected_output"]
            
            with self.subTest(msg=team_key):
                try:
                    actual = self.engine.analyze_home_dominance(team, years_back=years)
                    
                    if actual is None:
                        self.assertEqual(expected_raw, "No data available")
                    else:
                        # List of Dicts Comparison (Row by Row)
                        self.assertEqual(len(expected_raw), len(actual), "Row count mismatch")
                        
                        for i, row in enumerate(actual):
                            exp_row = expected_raw[i]
                            # Check key columns
                            self.assertEqual(row['Opponent'], exp_row['Opponent'])
                            self.assertEqual(str(row['Win %']), str(exp_row['Win %']))
                            # Check Form Guide Text (Won/Lost vs Emojis)
                            self.assertEqual(row['Last 5'], exp_row['Last 5'], "Form Guide text mismatch")
                            
                except Exception as e:
                    self.fail(f"Execution failed for {team_key}: {e}")

if __name__ == '__main__':
    unittest.main()
