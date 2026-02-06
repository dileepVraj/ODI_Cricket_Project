import sys
import os
import json
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
# from deepdiff import DeepDiff # Optional, but good for robust comparison.
# Since I cannot assume deepdiff is installed, I will use custom logic or simple equality.

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from engine import CricketAnalyzer
from venues import VENUE_MAP
from utils.test_recorder import SnapshotRecorder

# CONFIGURATION
TEAMS = [
    "Australia", "Bangladesh", "England", "India", 
    "New Zealand", "Pakistan", "South Africa", "Sri Lanka", "West Indies"
]

TEAM_PREFIX_MAP = {
    'Australia': 'AUS_',
    'Bangladesh': 'BAN_',
    'England': 'ENG_',
    'India': 'IND_',
    'New Zealand': 'NZ_',
    'Pakistan': 'PAK_',
    'South Africa': 'SA_',
    'Sri Lanka': 'SL_',
    'West Indies': 'WI_'
}

FIXTURES_DIR = "tests/odi/analyze_venue_matchup/fixtures"
EXPECTED_FILE = os.path.join(FIXTURES_DIR, "analyze_venue_matchup_expected_results.json")
LATEST_FILE = os.path.join(FIXTURES_DIR, "analyze_venue_matchup_latest_test_run_results.json")
FINAL_REPORT_FILE = os.path.join(FIXTURES_DIR, "analyze_venue_matchup_test_report.json")

def get_unique_venues_for_team(team_name):
    prefix = TEAM_PREFIX_MAP.get(team_name)
    if not prefix: return []
    unique_venues = {}
    for raw_name, master_id in VENUE_MAP.items():
        if master_id.startswith(prefix) and master_id not in unique_venues:
            unique_venues[master_id] = raw_name 
    return list(unique_venues.values())

def generate_latest_results(engine, recorder):
    """Generates the LATEST results."""
    print("🚀 Generating Latest Test Run Results...")
    results = {"Teams considered": TEAMS}
    
    for home_team in TEAMS:
        venues = get_unique_venues_for_team(home_team)
        if not venues: continue

        for stadium in venues:
            section_key = f"{home_team} vs all remaining teams results at {stadium}"
            results[section_key] = {}
            print(f"   Analysing: {section_key}...")
            
            for away_team in TEAMS:
                if home_team == away_team: continue
                matchup_key = f"{home_team} vs {away_team}"
                
                try:
                    res = engine.analyze_venue_matchup(stadium, home_team, away_team)
                    if res is None: res = "No data available"
                    
                    results[section_key][matchup_key] = {
                        "home_team": home_team, "opp_team": away_team, "years_back": 5,
                        "expected_output": recorder._serialize(res)
                    }
                except Exception as e:
                    results[section_key][matchup_key] = {
                        "home_team": home_team, "opp_team": away_team, "years_back": 5,
                        "expected_output": f"Error: {str(e)}"
                    }
    
    with open(LATEST_FILE, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"💾 Saved latest results to {LATEST_FILE}")
    return results

def compare_results(expected, latest):
    """Compares Expected vs Latest and generates Final Report."""
    print("\n🔍 Comparing Results...")
    discrepancies = []
    
    # Iterate through Latest Sections
    for section_key, latest_section in latest.items():
        if section_key == "Teams considered": continue
        
        expected_section = expected.get(section_key, {})
        
        for matchup_key, latest_data in latest_section.items():
            expected_data = expected_section.get(matchup_key)
            
            # Case 1: New Matchup (Not in Expected)
            if not expected_data:
                discrepancies.append({
                    "Status": "NEW_ENTRY",
                    "Details": f"Matchup '{matchup_key}' in '{section_key}' is NEW.",
                    "Expected": "Not Present",
                    "Actual": latest_data['expected_output']
                })
                continue
            
            # Case 2: Compare Values
            val_exp = expected_data.get('expected_output')
            val_act = latest_data.get('expected_output')
            
            # Simple JSON string comparison (Robust enough for serialized data)
            # For deeper diffs we'd need recursive dict comparison, but serialized string/json dump is good proxy.
            if json.dumps(val_exp, sort_keys=True) != json.dumps(val_act, sort_keys=True):
                discrepancies.append({
                    "Status": "MISMATCH",
                    "Details": f"Difference found in '{matchup_key}' ({section_key})",
                    "Expected": val_exp,
                    "Actual": val_act
                })

    # Generate Final Report
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
        print(f"❌ FAILURE: Found {len(discrepancies)} mismatches/new items. Check log.")
        
    with open(FINAL_REPORT_FILE, 'w') as f:
        json.dump(final_output, f, indent=4)
        print(f"📄 Validation report updated: {FINAL_REPORT_FILE}")

def merge_results():
    """Merges Latest into Expected."""
    if not os.path.exists(LATEST_FILE):
        print("❌ No latest results found to merge. Run tests first.")
        return

    print("\n🔄 Merging Latest Results into Expected Golden Master...")
    try:
        with open(LATEST_FILE, 'r') as f:
            latest = json.load(f)
        
        with open(EXPECTED_FILE, 'w') as f:
            json.dump(latest, f, indent=4)
            
        print(f"✅ Merge Complete. {EXPECTED_FILE} is now updated.")
    except Exception as e:
        print(f"❌ Merge Failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run Venue Regression Tests")
    parser.add_argument("--merge", action="store_true", help="Merge latest results into expected results (Update Snapshots)")
    args = parser.parse_args()

    if args.merge:
        merge_results()
    else:
        try:
            engine = CricketAnalyzer("data/FINAL_ODI_MASTER.csv")
            recorder = SnapshotRecorder(base_path="tests/fixtures")
            
            # 1. Load Expected
            expected_data = {}
            if os.path.exists(EXPECTED_FILE):
                with open(EXPECTED_FILE, 'r') as f:
                    expected_data = json.load(f)
            else:
                print("⚠️ No expected results found. First run will be baseline.")
            
            # 2. Run & Save Latest
            latest_data = generate_latest_results(engine, recorder)
            
            # 3. Compare
            compare_results(expected_data, latest_data)
            
        except Exception as e:
            print(f"❌ Fatal Error: {e}")

if __name__ == "__main__":
    main()
