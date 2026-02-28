import json
import os
import sys
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))

from engine import CricketAnalyzer

class TruthBridgeRunner:
    def __init__(self):
        print("🚀 Initializing Truth Bridge: Analyze Venue Matchup (Self-Diagnosis Mode)")
        self.engine = CricketAnalyzer('formats/odi/data/FINAL_ODI_MASTER.csv')
        self.truth_file = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
        
        with open(self.truth_file, 'r') as f:
            self.ground_truth = json.load(f)
        
        self.results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {"pass": 0, "fail": 0},
            "failures": [],
            "details": [],
            "metadata": {}
        }

    def run(self):
        root = self.ground_truth["Analyze venue matchup"]
        matchup_groups = [
            "Australia stats at it's grounds",
            "England stats at it's grounds",
            "India stats at it's grounds",
            "New Zealand stats at it's grounds",
            "South Africa stats at it's grounds"
        ]

        SEED_MODE = os.environ.get("SEED_MODE") == "1"

        # Get file timestamps for diagnosis
        data_path = os.path.join(self.base_dir, 'data', 'FINAL_ODI_MASTER.pkl')
        self.data_mtime = os.path.getmtime(data_path) if os.path.exists(data_path) else 0
        self.truth_mtime = os.path.getmtime(self.truth_file) if os.path.exists(self.truth_file) else 0

        self.results["metadata"] = {
            "data_last_modified": datetime.fromtimestamp(self.data_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "truth_last_modified": datetime.fromtimestamp(self.truth_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "lookback_years": 10
        }

        for group_name in matchup_groups:
            print(f"\n📂 Processing Group: {group_name}")
            venue_map = self._get_venue_map(group_name)
            
            for matchup_key, venues_truth in root[group_name].items():
                print(f"⚔️  {matchup_key}")
                teams = [t.strip() for t in matchup_key.split(" vs ")]
                home_team, opp_team = teams[0], teams[1]

                for venue_id, truth_data in venues_truth.items():
                    venue_name = next((name for name, vid in venue_map.items() if vid == venue_id), venue_id)
                    print(f"   🔎 Checking: {matchup_key} @ {venue_name} ({venue_id})")
                    
                    try:
                        engine_data = self.engine.analyze_venue_matchup(venue_id, home_team, opp_team, years_back=10)
                    except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
                        print(f"      ❌ [ERROR] Engine failed: {e}")
                        continue

                    # Process engine output (list of dicts -> flat dict with standardized keys)
                    engine_dict = {}
                    if isinstance(engine_data, list) and len(engine_data) > 36:
                        engine_dict = {
                            "Matches Played": engine_data[0]['Value'],
                            "Tied / No Result": engine_data[1]['Value'],
                            "Home Win %": engine_data[2]['Value'],
                            "Home Total Wins": engine_data[4]['Value'],
                            "Visitor Total Wins": engine_data[8]['Value'],
                            "Overall Avg 1st Innings": engine_data[12]['Value'],
                            "Overall Avg 2nd Innings": engine_data[13]['Value'],
                            "MATCH_IDS": engine_data[37]['Value'] # Hidden metric (v2.5)
                        }
                    else:
                        engine_dict = "No data available"

                    if SEED_MODE:
                        venues_truth[venue_id] = engine_dict
                        print(f"      💾 [SEED] Writing engine data to {venue_id}")
                        continue

                    self._compare(matchup_key, venue_name, engine_dict, truth_data)

        if SEED_MODE:
            self._save_seeded_truth()
        else:
            self._save_results()

    def _get_venue_map(self, group_name):
        root = self.ground_truth["Analyze venue matchup"]
        group_data = group_name.replace(" stats at it's grounds", "")
        venue_key = f"{group_data} venues"
        venue_map = root["Details"].get(venue_key)
        if not venue_map:
            print(f"⚠️ Warning: Could not find venues for '{venue_key}'")
            return {}
        return venue_map

    def _save_seeded_truth(self):
        with open(self.truth_file, 'w') as f:
            json.dump(self.ground_truth, f, indent=4)
        print(f"✅ Ground Truth SEEDED successfully: {self.truth_file}")

    def _compare(self, matchup, venue, engine_dict, truth_data):
        mismatches = []
        
        # Handle cases where truth or engine says "No data available"
        if isinstance(truth_data, str) or isinstance(engine_dict, str):
            if str(truth_data) != str(engine_dict):
                mismatches.append({
                    "metric": "Data Availability",
                    "expected": truth_data,
                    "actual": engine_dict
                })
        else:
            # Both are dicts, compare metrics (exclude MATCH_IDS from visual mismatch)
            for metric, expected_val in truth_data.items():
                if metric == "MATCH_IDS": continue
                actual_val = engine_dict.get(metric)
                if str(actual_val) != str(expected_val):
                    mismatches.append({
                        "metric": metric,
                        "expected": expected_val,
                        "actual": actual_val
                    })

        status = "PASS" if not mismatches else "FAIL"
        diagnosis = None

        if status == "FAIL":
            # 🧬 FINGERPRINT-BASED DIAGNOSIS (v2.5)
            truth_ids = set(str(truth_data.get("MATCH_IDS", "")).split(",")) if isinstance(truth_data, dict) else set()
            engine_ids = set(str(engine_dict.get("MATCH_IDS", "")).split(",")) if isinstance(engine_dict, dict) else set()
            
            # Clean empty strings from sets
            truth_ids.discard("")
            engine_ids.discard("")

            # Case 1: Identical Data Footprint, Different Stats (Definitive Bug)
            if engine_ids == truth_ids:
                diagnosis = "LOGIC_REGRESSION: Identical matches detected, but engine calculation differs. Potential Bug."
            # Case 2: Growth in Data (Benign)
            elif truth_ids.issubset(engine_ids) and len(engine_ids) > len(truth_ids):
                diagnosis = "DATA_DRIFT: New matches detected in dataset. Baseline needs update."
            # Case 3: Missing Data / Filtering regression (Critical)
            elif engine_ids.issubset(truth_ids) and len(engine_ids) < len(truth_ids):
                diagnosis = "LOGIC_REGRESSION: Engine is seeing FEWER matches than baseline. Filtering bug."
            # Case 4: Complex Shift (Both new and missing matches)
            else:
                diagnosis = "COMPLEX_DRIFT: Match IDs have shifted significantly. Manual verification required."
            
            self.results["summary"]["fail"] += 1
            print(f"      🔴 [FAIL] Diagnosis: {diagnosis}")
        else:
            self.results["summary"]["pass"] += 1
            print("      🟢 [PASS]")

        result_entry = {
            "matchup": matchup,
            "venue": venue,
            "status": status
        }
        if diagnosis:
            result_entry["diagnosis"] = diagnosis
        if mismatches:
            result_entry["mismatches"] = mismatches
            self.results["failures"].append(result_entry)
        
        self.results["details"].append(result_entry)

    def _save_results(self):
        report_path = os.path.join(os.path.dirname(__file__), 'report.json')
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=4)
        print(f"\n✅ Truth Bridge Run Complete. Detailed report saved to {report_path}")
        print(f"📊 Totals: Pass: {self.results['summary']['pass']}, Fail: {self.results['summary']['fail']}")

if __name__ == "__main__":
    runner = TruthBridgeRunner()
    runner.run()
