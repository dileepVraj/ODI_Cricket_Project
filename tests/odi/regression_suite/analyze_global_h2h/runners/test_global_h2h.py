import unittest
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from engine import CricketAnalyzer

class TestGlobalH2H(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = CricketAnalyzer("data/FINAL_ODI_MASTER.csv")
        cls.fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
        cls.fixture_file = os.path.join(cls.fixtures_dir, "analyze_global_h2h_expected_results.json")

    def test_global_h2h_scenarios(self):
        """Run all Global H2H scenarios from expected_results.json"""
        if not os.path.exists(self.fixture_file):
            print(f"⚠️ Fixture file not found: {self.fixture_file}")
            return

        with open(self.fixture_file, 'r') as f:
            all_data = json.load(f)

        print(f"\n🌍 Running Global H2H Tests from Fixture...")
        
        for group_key, group_data in all_data.items():
            if not isinstance(group_data, dict): continue # Skip metadata keys
            
            for scenario_key, data in group_data.items():
                # Data validation
                if "expected_output" not in data: continue
                
                team_a = data.get("team_a")
                team_b = data.get("team_b")
                years = data.get("years_back", 5)
                expected_raw = data["expected_output"]
                
                with self.subTest(msg=scenario_key):
                    try:
                        actual = self.engine.analyze_global_h2h(team_a, team_b, years_back=years)
                        
                        if actual is None:
                            self.assertEqual(expected_raw, "No data available")
                        else:
                            # Metrics Comparison
                            self.assertEqual(len(expected_raw), len(actual), "Metric count mismatch")
                            for i, metric in enumerate(actual):
                                self.assertEqual(metric['Metric'], expected_raw[i]['Metric'])
                                self.assertEqual(str(metric['Value']), str(expected_raw[i]['Value']))
                                
                    except Exception as e:
                        self.fail(f"Execution failed for {scenario_key}: {e}")

if __name__ == '__main__':
    unittest.main()
