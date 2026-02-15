import pandas as pd
import json
import os
import sys

# Add project root to path for imports
sys.path.append(os.getcwd())
from engine import CricketAnalyzer

class TruthBridgeBase:
    """
    Standardized Base Class for all Truth Bridge Runners (Fingerprinting v2.5).
    Centralizes comparison, auto-diagnosis, and reporting logic.
    """
    def __init__(self, suite_name, truth_file_path):
        self.suite_name = suite_name
        self.truth_file = truth_file_path
        self.data_file = 'formats/odi/data/FINAL_ODI_MASTER.csv'
        
        # Initialize Engine
        self.analyzer = CricketAnalyzer(self.data_file)
        self.engine = self.analyzer.team_engine
        
        # Load Ground Truth
        if not os.path.exists(self.truth_file):
            # Create minimal skeleton if file doesn't exist
            self.ground_truth = {self.suite_name: {"Details": {}, "Stats": {}}}
        else:
            with open(self.truth_file, 'r') as f:
                self.ground_truth = json.load(f)
            
        self.results = {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {"pass": 0, "fail": 0},
            "failures": [],
            "details": []
        }

    def _get_ids(self, data):
        """Extracts unique Match IDs from engine output or truth dictionary."""
        if isinstance(data, dict):
            # Flat dict mode
            ids_str = str(data.get("MATCH_IDS", ""))
            ids = set(ids_str.split(","))
            ids.discard("")
            return ids
        elif isinstance(data, list):
            # List of dicts mode (Metric/Value)
            for item in data:
                if isinstance(item, dict) and item.get("Metric") == "MATCH_IDS":
                    ids_str = str(item.get("Value", ""))
                    ids = set(ids_str.split(","))
                    ids.discard("")
                    return ids
        return set()

    def compare(self, key_path, engine_data, truth_data):
        """
        Performs fingerprint-based comparison and auto-diagnosis.
        
        Args:
            key_path (list): Breadcrumbs for the item being tested
            engine_data (any): The data extracted from engine output (dict or list).
            truth_data (any): The expected data from ground_truth.json (dict or list).
        """
        mismatches = []
        item_label = " > ".join(key_path)

        # 1. Comparison Logic
        if isinstance(truth_data, str) or isinstance(engine_data, str):
            if str(truth_data) != str(engine_data):
                mismatches.append({"metric": "Availability", "expected": truth_data, "actual": engine_data})
        elif isinstance(truth_data, list) and isinstance(engine_data, list):
            # List of dicts comparison
            if len(truth_data) != len(engine_data):
                mismatches.append({"metric": "List Length", "expected": len(truth_data), "actual": len(engine_data)})
            else:
                for i, t_item in enumerate(truth_data):
                    e_item = engine_data[i]
                    if t_item.get("Metric") == "MATCH_IDS": continue
                    if str(t_item.get("Value")) != str(e_item.get("Value")):
                        mismatches.append({
                            "metric": t_item.get("Metric"),
                            "expected": t_item.get("Value"),
                            "actual": e_item.get("Value")
                        })
        elif isinstance(truth_data, dict) and isinstance(engine_data, dict):
            # Flat dict comparison
            for metric, expected_val in truth_data.items():
                if metric == "MATCH_IDS": continue
                actual_val = engine_data.get(metric)
                if str(actual_val) != str(expected_val):
                    mismatches.append({"metric": metric, "expected": expected_val, "actual": actual_val})

        status = "PASS" if not mismatches else "FAIL"
        diagnosis = None

        if status == "FAIL":
            # 🧬 FINGERPRINT-BASED DIAGNOSIS (v2.5)
            truth_ids = self._get_ids(truth_data)
            engine_ids = self._get_ids(engine_data)

            if engine_ids == truth_ids:
                diagnosis = "LOGIC_REGRESSION: Identical matches detected, but stats differ. Potential Bug."
            elif truth_ids.issubset(engine_ids) and len(engine_ids) > len(truth_ids):
                diagnosis = "DATA_DRIFT: New matches detected in dataset. Baseline needs update."
            elif engine_ids.issubset(truth_ids) and len(engine_ids) < len(truth_ids):
                diagnosis = "FILTERING_REGRESSION: Engine is seeing FEWER matches than baseline."
            else:
                diagnosis = "COMPLEX_DRIFT: Match IDs have shifted significantly. Manual verification required."

            self.results["summary"]["fail"] += 1
            failure_entry = {
                "item": item_label,
                "status": status,
                "diagnosis": diagnosis,
                "mismatches": mismatches
            }
            self.results["failures"].append(failure_entry)
            print(f"      🔴 [FAIL] {item_label} | Diagnosis: {diagnosis}")
        else:
            self.results["summary"]["pass"] += 1
            print(f"      🟢 [PASS] {item_label}")

        self.results["details"].append({"item": item_label, "status": status})

    def save_report(self, report_path):
        """Saves the test results to a JSON file."""
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=4, default=str)
        print(f"\n✅ Report generated: {report_path}")
        print(f"📊 Totals: Pass: {self.results['summary']['pass']}, Fail: {self.results['summary']['fail']}")

    def save_seeded_truth(self):
        """Saves the updated ground_truth.json in SEED_MODE."""
        with open(self.truth_file, 'w') as f:
            json.dump(self.ground_truth, f, indent=4, default=str)
        print(f"✅ Ground Truth SEEDED successfully: {self.truth_file}")
