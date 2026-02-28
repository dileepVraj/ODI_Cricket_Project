import json
import os
import sys
from typing import Any, Dict, List, Set

import pandas as pd

# Add project root to path for imports
sys.path.append(os.getcwd())
from engine import CricketAnalyzer


class TruthBridgeBase:
    """
    Standardized Base Class for all Truth Bridge runners.
    Centralizes comparison, auto-diagnosis, and reporting logic.
    """

    def __init__(self, suite_name: str, truth_file_path: str):
        self.suite_name = suite_name
        self.truth_file = truth_file_path
        self.data_file = "formats/odi/data/FINAL_ODI_MASTER.csv"

        # Initialize engine
        self.analyzer = CricketAnalyzer(self.data_file)
        self.engine = self.analyzer.team_engine

        # Load Ground Truth
        if not os.path.exists(self.truth_file):
            self.ground_truth = {self.suite_name: {"Details": {}, "Stats": {}}}
        else:
            with open(self.truth_file, "r", encoding="utf-8") as f:
                self.ground_truth = json.load(f)

        self.results: Dict[str, Any] = {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {"pass": 0, "fail": 0},
            "failures": [],
            "details": [],
        }

    def _get_ids(self, data: Any) -> Set[str]:
        """Extract unique MATCH_IDS from dict/list payloads."""
        if isinstance(data, dict):
            ids_str = str(data.get("MATCH_IDS", ""))
            ids = set(ids_str.split(","))
            ids.discard("")
            return ids

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("Metric") == "MATCH_IDS":
                    ids_str = str(item.get("Value", ""))
                    ids = set(ids_str.split(","))
                    ids.discard("")
                    return ids
        return set()

    def compare(self, key_path: List[str], engine_data: Any, truth_data: Any) -> None:
        """Perform value comparison and append diagnosis on mismatch."""
        mismatches: List[Dict[str, Any]] = []
        item_label = " > ".join(key_path)

        if isinstance(truth_data, str) or isinstance(engine_data, str):
            if str(truth_data) != str(engine_data):
                mismatches.append(
                    {"metric": "Availability", "expected": truth_data, "actual": engine_data}
                )
        elif isinstance(truth_data, list) and isinstance(engine_data, list):
            if len(truth_data) != len(engine_data):
                mismatches.append(
                    {"metric": "List Length", "expected": len(truth_data), "actual": len(engine_data)}
                )
            else:
                for i, t_item in enumerate(truth_data):
                    e_item = engine_data[i]
                    if t_item.get("Metric") == "MATCH_IDS":
                        continue
                    if str(t_item.get("Value")) != str(e_item.get("Value")):
                        mismatches.append(
                            {
                                "metric": t_item.get("Metric"),
                                "expected": t_item.get("Value"),
                                "actual": e_item.get("Value"),
                            }
                        )
        elif isinstance(truth_data, dict) and isinstance(engine_data, dict):
            for metric, expected_val in truth_data.items():
                if metric == "MATCH_IDS":
                    continue
                actual_val = engine_data.get(metric)
                if str(actual_val) != str(expected_val):
                    mismatches.append(
                        {"metric": metric, "expected": expected_val, "actual": actual_val}
                    )

        status = "PASS" if not mismatches else "FAIL"
        diagnosis = None

        if status == "FAIL":
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
            self.results["failures"].append(
                {
                    "item": item_label,
                    "status": status,
                    "diagnosis": diagnosis,
                    "mismatches": mismatches,
                }
            )
            print(f"      [FAIL] {item_label} | Diagnosis: {diagnosis}")
        else:
            self.results["summary"]["pass"] += 1
            print(f"      [PASS] {item_label}")

        self.results["details"].append({"item": item_label, "status": status})

    def save_report(self, report_path: str) -> None:
        """Save results to JSON report. Gracefully degrades on write restrictions."""
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=4, default=str)
            print(f"\nReport generated: {report_path}")
        except PermissionError:
            print(f"\nCould not write report to {report_path} (PermissionError).")
            print("Summary printed to console only for this run.")
        print(
            f"Totals: Pass: {self.results['summary']['pass']}, "
            f"Fail: {self.results['summary']['fail']}"
        )

    def save_seeded_truth(self) -> None:
        """Save seeded ground truth in SEED_MODE."""
        try:
            with open(self.truth_file, "w", encoding="utf-8") as f:
                json.dump(self.ground_truth, f, indent=4, default=str)
            print(f"Ground Truth SEEDED successfully: {self.truth_file}")
        except PermissionError:
            print(f"Could not write seeded ground truth to {self.truth_file} (PermissionError).")
