import unittest
import json
import os
import sys
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from engine import CricketAnalyzer

class TestCountryH2H(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = CricketAnalyzer("data/FINAL_ODI_MASTER.csv")
        cls.fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
        cls.fixture_file = os.path.join(cls.fixtures_dir, "analyze_country_h2h_expected_results.json")

    def test_h2h_scenarios(self):
        """Run all Country H2H scenarios from expected_results.json"""
        if not os.path.exists(self.fixture_file):
            print(f"⚠️ Fixture file not found: {self.fixture_file}")
            return

        with open(self.fixture_file, 'r') as f:
            all_data = json.load(f)

        print(f"\n🗺️ Running Country H2H Tests from Fixture...")
        
        for scenario_key, data in all_data.items():
            if scenario_key == "Teams considered": continue
            
            # Data validation
            if "expected_output" not in data: continue
            
            home = data.get("home_team")
            opp = data.get("opp_team")
            host = data.get("host_country")
            years = data.get("years_back", 10)
            expected_raw = data["expected_output"]
            
            with self.subTest(msg=scenario_key):
                try:
                    actual = self.engine.analyze_country_h2h(home, opp, country_name=host, years_back=years)
                    
                    if actual is None:
                        self.assertEqual(expected_raw, "No data available")
                    else:
                        # Compare serialized structure length/content
                        # Since actual is a list of dicts (Metrics)
                        self.assertEqual(len(expected_raw), len(actual), "Metric count mismatch")
                        for i, metric in enumerate(actual):
                            self.assertEqual(metric['Metric'], expected_raw[i]['Metric'])
                            self.assertEqual(str(metric['Value']), str(expected_raw[i]['Value']))
                            
                except Exception as e:
                    self.fail(f"Execution failed for {scenario_key}: {e}")

if __name__ == '__main__':
    unittest.main()
