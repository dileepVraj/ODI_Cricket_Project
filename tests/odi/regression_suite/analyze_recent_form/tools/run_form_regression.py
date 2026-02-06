
import json
import os
import sys
import argparse
import pandas as pd

# -------------------------------------------------------------------------
# ⚙️ CONFIG UTILITY
# -------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.append(PROJECT_ROOT)

from engine import CricketAnalyzer

FIXTURES_DIR = os.path.join(PROJECT_ROOT, "tests/odi/analyze_recent_form/fixtures")
EXPECTED_FILE = os.path.join(FIXTURES_DIR, "recent_form_expected_results.json")
LATEST_FILE = os.path.join(FIXTURES_DIR, "recent_form_latest_results.json")
REPORT_FILE = os.path.join(FIXTURES_DIR, "recent_form_test_report.json")
DB_PATH = os.path.join(PROJECT_ROOT, "data/FINAL_ODI_MASTER.csv")

def generate_latest_results():
    """Generates LATEST results from the Engine."""
    print(f"🚀 Generating Latest Form Results...")
    engine = CricketAnalyzer(DB_PATH)
    
    # Same Scope as Golden Master
    target_teams = ['India', 'Australia', 'England', 'Pakistan', 'South Africa', 'New Zealand', 'West Indies', 'Sri Lanka']
    continents = ['Asia', 'Africa', 'Europe', 'Oceania', 'Americas']
    
    latest_data = {}

    for team in target_teams:
        print(f"   Analyzing {team}...", end="\r")
        latest_data[team] = {}
        
        # 1. GLOBAL FORM
        res_global = engine.team_engine.analyze_team_form(team, opp_team='All', continent='All')
        latest_data[team]['Global'] = { "summary_code": res_global['summary_code'] } if res_global else None

        # 2. CONTINENTAL FORM
        for cont in continents:
            res_cont = engine.team_engine.analyze_team_form(team, opp_team='All', continent=cont)
            latest_data[team][cont] = { "summary_code": res_cont['summary_code'] } if res_cont else None

    with open(LATEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(latest_data, f, indent=4, default=str)
    print(f"\n💾 Saved latest results to: {LATEST_FILE}")
    return latest_data

def compare_results(expected, latest):
    """Compares Expected vs Latest and generates Final Report."""
    print("\n🔍 Comparing Results...")
    discrepancies = []
    
    for team, scenarios in latest.items():
        expected_team = expected.get(team, {})
        
        for scenario, latest_val in scenarios.items():
            expected_val = expected_team.get(scenario)
            
            # Comparison Logic (Sequence Only)
            seq_act = latest_val.get('summary_code') if latest_val else None
            seq_exp = expected_val.get('summary_code') if expected_val else None
            
            if seq_act != seq_exp:
                discrepancies.append({
                    "Team": team,
                    "Scenario": scenario,
                    "Status": "MISMATCH",
                    "Expected": seq_exp,
                    "Actual": seq_act
                })

    # Generate Report
    final_output = {}
    if not discrepancies:
        final_output = {"Result": "SUCCESS", "Message": "Test run successful! No mismatches found."}
        print("✅ SUCCESS: No regressions found.")
    else:
        final_output = {
            "Result": "FAILURE", 
            "Message": f"Found {len(discrepancies)} discrepancies.",
            "Discrepancies": discrepancies
        }
        print(f"❌ FAILURE: Found {len(discrepancies)} mismatches. Check output file.")

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4)
    print(f"📄 Validation report updated: {REPORT_FILE}")

def merge_results():
    """Merges Latest into Expected."""
    if not os.path.exists(LATEST_FILE):
        print("❌ No latest results found to merge. Run tests first.")
        return

    print("\n🔄 Merging Latest Results into Expected Golden Master...")
    with open(LATEST_FILE, 'r') as f:
        latest = json.load(f)
    
    with open(EXPECTED_FILE, 'w') as f:
        json.dump(latest, f, indent=4)
        
    print(f"✅ Merge Complete. {EXPECTED_FILE} is now updated.")

def main():
    parser = argparse.ArgumentParser(description="Run Recent Form Regression Suite")
    parser.add_argument("--merge", action="store_true", help="Merge latest results into expected results")
    args = parser.parse_args()

    if args.merge:
        merge_results()
    else:
        # 1. Load Expected
        if os.path.exists(EXPECTED_FILE):
             with open(EXPECTED_FILE, 'r') as f:
                expected_data = json.load(f)
        else:
            print("⚠️ No expected results found. Run will be baseline.")
            expected_data = {}

        # 2. Generate Latest
        latest_data = generate_latest_results()

        # 3. Compare
        compare_results(expected_data, latest_data)

if __name__ == '__main__':
    main()
