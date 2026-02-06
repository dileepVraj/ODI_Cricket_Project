import sys
import os
import json
import argparse
import unittest
from datetime import datetime

# 1. SETUP PATHS
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.append(PROJECT_ROOT)

try:
    from engine import CricketAnalyzer
except ImportError:
    print("❌ Critical: Could not import CricketAnalyzer")
    sys.exit(1)

# FORCE UTF-8
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

# 2. CONFIGURATION
FIXTURES_DIR = os.path.join(PROJECT_ROOT, "tests/odi/compare_squads/fixtures")
EXPECTED_FILE = os.path.join(FIXTURES_DIR, "compare_squads_expected_results.json")
LATEST_FILE = os.path.join(FIXTURES_DIR, "compare_squads_latest_results.json")
REPORT_FILE = os.path.join(FIXTURES_DIR, "compare_squads_test_report.json")

def load_expected_results():
    if not os.path.exists(EXPECTED_FILE):
        print(f"⚠️ Expected results not found at {EXPECTED_FILE}")
        return {}
    with open(EXPECTED_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_latest_results(expected_data):
    """
    Re-runs the logic for every scenario found in the Expected Data.
    Uses the EXACT SAME lineups from Expected Data to ensure regression validity.
    """
    print("Initializing Engine for Latest Results...")
    # Suppress output
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
    try:
        engine = CricketAnalyzer('data/FINAL_ODI_MASTER.csv')
    except Exception as e:
        sys.stdout = original_stdout
        print(f"Engine Init Failed: {e}")
        return {}
    finally:
        sys.stdout = original_stdout

    latest_report = {}
    
    # We iterate over the EXPECTED keys to ensure we match the scenario 1:1
    for scenario_key, scenario_data in expected_data.items():
        meta = scenario_data['Meta']
        home = scenario_key.split("_vs_")[0]
        away = scenario_key.split("_vs_")[1]
        
        # Use Meta to get inputs (Ensures we compare Apples to Apples)
        home_xi = meta['HomeXI']
        away_xi = meta['AwayXI']
        venue = meta['Venue']
        years = meta['Years']
        
        print(f"   Re-running {scenario_key}...", end=" ")
        
        sys.stdout = open(os.devnull, 'w', encoding='utf-8')
        try:
            payload = engine.player_engine._generate_comparison_payload(
                home, home_xi, away, away_xi, venue, years=years
            )
        except Exception as e:
             sys.stdout = original_stdout
             print(f"Error: {e}")
             continue
        finally:
            sys.stdout = original_stdout
        
        latest_report[scenario_key] = {
            "Meta": meta,
            "Payload": payload
        }
        print("Done.")

    # Save Latest
    with open(LATEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(latest_report, f, indent=4, default=str)
    
    return latest_report

def deep_compare(expected, actual, path=""):
    """
    Recursive dictionary comparison. Returns list of mismatches.
    """
    issues = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        for k, v in expected.items():
            if k not in actual:
                issues.append(f"Missing Key: {path}.{k}")
            else:
                issues.extend(deep_compare(v, actual[k], f"{path}.{k}"))
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
             issues.append(f"List Length Mismatch: {path} (Expected {len(expected)}, Got {len(actual)})")
        else:
            for i, (e, a) in enumerate(zip(expected, actual)):
                issues.extend(deep_compare(e, a, f"{path}[{i}]"))
    else:
        # Value Comparison
        # Normalize strings/ints for robustness
        e_str = str(expected).strip()
        a_str = str(actual).strip()
        if e_str != a_str:
            issues.append(f"Value Mismatch: {path} (Expected '{e_str}', Got '{a_str}')")
            
    return issues

def compare_results(expected, latest):
    print("\nComparing Results (Deep Diff)...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "PASS",
        "failures": {}
    }
    
    for key, data in expected.items():
        if key not in latest:
            report["failures"][key] = ["Scenario Missing in Latest Results"]
            report["status"] = "FAIL"
            continue
            
        # Section-based Comparison
        exp_payload = data['Payload']
        lat_payload = latest[key]['Payload']
        
        # 1. SquadComparison
        squad_issues = deep_compare(exp_payload.get('SquadComparison'), lat_payload.get('SquadComparison'), "SquadComparison")
        
        # 2. TacticalMatrix
        matrix_issues = deep_compare(exp_payload.get('TacticalMatrix'), lat_payload.get('TacticalMatrix'), "TacticalMatrix")
        
        # 3. Matchups
        matchup_issues = deep_compare(exp_payload.get('Matchups'), lat_payload.get('Matchups'), "Matchups")
        
        all_issues = squad_issues + matrix_issues + matchup_issues
        
        if all_issues:
            report["status"] = "FAIL"
            report["failures"][key] = {
                "SquadComparison": squad_issues,
                "TacticalMatrix": matrix_issues,
                "Matchups": matchup_issues
            }

    # Save Report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)
        
    if report["status"] == "PASS":
        print("SUCCESS: No regressions detected.")
    else:
        print(f"FAILURE: Regressions detected. Check {REPORT_FILE}")
        
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--merge', action='store_true', help="Update Expected Results with Latest")
    args = parser.parse_args()

    # 1. Load Expected
    expected = load_expected_results()
    if not expected and not args.merge:
        print("⚠️ No Expected Data found. Please run generate_squad_data.py first or use --merge.")
        return

    # 2. Generate Latest
    # If merge is on, we generate fresh data assuming it is correct
    # If expected is present, we use its keys to drive generation
    latest = generate_latest_results(expected if expected else {}) 
    
    if args.merge:
        print(f"\n💾 Merging Latest -> Expected ({EXPECTED_FILE})")
        with open(EXPECTED_FILE, 'w', encoding='utf-8') as f:
            json.dump(latest, f, indent=4, default=str)
        print("✅ Merge Complete.")
        return

    # 3. Compare
    compare_results(expected, latest)

if __name__ == "__main__":
    main()
