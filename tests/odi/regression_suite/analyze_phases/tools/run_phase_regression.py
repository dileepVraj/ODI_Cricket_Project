
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
from venues import VENUE_MAP

FIXTURES_DIR = os.path.join(PROJECT_ROOT, "tests/odi/analyze_phases/fixtures")
EXPECTED_FILE = os.path.join(FIXTURES_DIR, "analyze_phases_expected_results.json")
LATEST_FILE = os.path.join(FIXTURES_DIR, "analyze_phases_latest_results.json")
REPORT_FILE = os.path.join(FIXTURES_DIR, "analyze_phases_test_report.json")
DB_PATH = os.path.join(PROJECT_ROOT, "data/FINAL_ODI_MASTER.csv")

# Same Config as Generator
TEAMS = [
    "Australia", "Bangladesh", "England", "India", 
    "New Zealand", "Pakistan", "South Africa", "Sri Lanka", "West Indies"
]

TEAM_PREFIX_MAP = {
    'Australia': 'AUS_', 'Bangladesh': 'BAN_', 'England': 'ENG_',
    'India': 'IND_', 'New Zealand': 'NZ_', 'Pakistan': 'PAK_',
    'South Africa': 'SA_', 'Sri Lanka': 'SL_', 'West Indies': 'WI_'
}

def get_host_nation(venue_id):
    for team, prefix in TEAM_PREFIX_MAP.items():
        if venue_id.startswith(prefix):
            return team
    return None

def generate_latest_results():
    """Generates LATEST results from the Engine."""
    print("🚀 Generating Latest Phase Analysis Results...")
    engine = CricketAnalyzer(DB_PATH).team_engine
    
    final_report = {"Phase Analysis Report": {}}
    unique_venues = sorted(list(set(VENUE_MAP.values())))

    for venue_id in unique_venues:
        host_nation = get_host_nation(venue_id)
        if not host_nation: continue
        
        group_key = f"Grounds in {host_nation}"
        if group_key not in final_report["Phase Analysis Report"]:
            final_report["Phase Analysis Report"][group_key] = {}
            
        print(f"   Analyzing {venue_id}...", end="\r")
        
        try:
            # 1. Baseline
            data_baseline = engine.analyze_venue_phases(venue_id, home_team=host_nation, away_team='All', years=10)
            
            venue_data = {
                "Host": host_nation,
                "Baseline_Metrics": data_baseline
            }
            
            # 2. Matchups
            for opp in [t for t in TEAMS if t != host_nation]:
                data_rival = engine.analyze_venue_phases(venue_id, home_team=host_nation, away_team=opp, years=10)
                venue_data[f"vs_{opp}"] = data_rival

            final_report["Phase Analysis Report"][group_key][venue_id] = venue_data

        except Exception as e:
            final_report["Phase Analysis Report"][group_key][venue_id] = {"Error": str(e)}

    with open(LATEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=4, default=str)
    print(f"\n💾 Saved latest results to: {LATEST_FILE}")
    return final_report

def compare_dicts(d1, d2, path=""):
    """Recursively compares two dictionaries."""
    mismatches = []
    if d1 is None and d2 is None: return []
    if d1 is None or d2 is None:
        return [{"Path": path, "Expected": str(type(d1)), "Actual": str(type(d2)), "Message": "Type/Null Mismatch"}]
    
    if not isinstance(d1, dict) or not isinstance(d2, dict):
        if d1 != d2:
            return [{"Path": path, "Expected": d1, "Actual": d2, "Message": "Value Mismatch"}]
        return []

    for k, v in d1.items():
        if k not in d2:
            mismatches.append({"Path": f"{path}.{k}", "Expected": "Present", "Actual": "Missing", "Message": "Key Missing"})
            continue
        
        if isinstance(v, dict):
            mismatches.extend(compare_dicts(v, d2[k], path=f"{path}.{k}"))
        elif v != d2[k]:
             mismatches.append({"Path": f"{path}.{k}", "Expected": v, "Actual": d2[k], "Message": "Value Mismatch"})
            
    return mismatches

def compare_results(expected, latest):
    """Compares Expected vs Latest and generates Final Report."""
    print("\n🔍 Comparing Results...")
    discrepancies = []
    
    exp_report = expected.get("Phase Analysis Report", {})
    lat_report = latest.get("Phase Analysis Report", {})
    
    for group, venues in lat_report.items():
        exp_venues = exp_report.get(group, {})
        
        for venue_id, lat_data in venues.items():
            exp_data = exp_venues.get(venue_id)
            if not exp_data:
                discrepancies.append({"Venue": venue_id, "Status": "NEW_ENTRY"})
                continue
                
            # Deep Compare
            diffs = compare_dicts(exp_data, lat_data, path=venue_id)
            for d in diffs:
                discrepancies.append({
                    "Venue": venue_id,
                    "Status": "MISMATCH",
                    "Details": d
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
    parser = argparse.ArgumentParser(description="Run Phase Analysis Regression Suite")
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
