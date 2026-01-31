import unittest
import json
import os
import sys
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from engine import CricketAnalyzer

class TestHomeFortress(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = CricketAnalyzer("data/FINAL_ODI_MASTER.csv")
        cls.fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
        cls.fixture_file = os.path.join(cls.fixtures_dir, "analyze_home_fortress_expected_results.json")

    def _deserialize(self, obj):
        if isinstance(obj, dict):
            if obj.get('__type__') == 'pandas_dataframe':
                return pd.DataFrame.from_dict(obj['data'], orient='split')
            elif obj.get('__type__') == 'pandas_series':
                return pd.Series(obj['data'])
            else:
                return {k: self._deserialize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deserialize(i) for i in obj]
        return obj

    def test_fortress_scenarios(self):
        """Run all fortress scenarios from expected_results.json"""
        if not os.path.exists(self.fixture_file):
            print(f"⚠️ Fixture file not found: {self.fixture_file}")
            return

        with open(self.fixture_file, 'r') as f:
            all_data = json.load(f)

        print(f"\n🏰 Running Fortress Tests from Fixture...")
        
        for venue_key, scenarios in all_data.items():
            if venue_key == "Teams considered": continue
            
            # extract stadium and team from key logic if needed, or rely on internal data
            # Key format: "{Team} at {Stadium}"
            if " at " not in venue_key: continue
            
            parts = venue_key.split(" at ")
            home_team = parts[0]
            stadium = parts[1]
            
            for scenario_name, data in scenarios.items():
                if isinstance(data, dict) and "expected_output" in data:
                    # It's a valid test case
                    opp_team = data.get("opponent", "All")
                    years = data.get("years_back", 10)
                    expected_raw = data["expected_output"]
                    
                    with self.subTest(msg=f"{venue_key} - {scenario_name}"):
                        try:
                            actual = self.engine.analyze_home_fortress(stadium, home_team, opp_team=opp_team, years_back=years)
                            
                            # Normalize actual for comparison (serialize then deserialize or just compare structure?)
                            # The expected data is SERIALIZED (lists/dicts).
                            # Actual is a list of dicts (metrics). 
                            # If actual is None ("No data"), expected should be string "No data available".
                            
                            if actual is None:
                                self.assertEqual(expected_raw, "No data available")
                            else:
                                # Convert actual to list of dicts if it isn't already (it is)
                                # Compare content
                                self.assertEqual(len(expected_raw), len(actual), "Metric count mismatch")
                                for i, metric in enumerate(actual):
                                    self.assertEqual(metric['Metric'], expected_raw[i]['Metric'])
                                    self.assertEqual(str(metric['Value']), str(expected_raw[i]['Value']))
                                    
                        except Exception as e:
                            self.fail(f"Execution failed: {e}")

if __name__ == '__main__':
    unittest.main()
