import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import argparse

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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures")
EXPECTED_FILE = os.path.join(FIXTURES_DIR, "analyze_home_fortress_expected_results.json")
LATEST_FILE = os.path.join(FIXTURES_DIR, "analyze_home_fortress_latest_test_run_results.json")
FINAL_REPORT_FILE = os.path.join(FIXTURES_DIR, "analyze_home_fortress_test_report.json")

def get_unique_venues_for_team(team_name):
    prefix = TEAM_PREFIX_MAP.get(team_name)
    if not prefix:
        return []
    
    unique_venues = {}
    for raw_name, master_id in VENUE_MAP.items():
        if master_id.startswith(prefix):
            if master_id not in unique_venues:
                unique_venues[master_id] = raw_name
    
    return list(unique_venues.values())

def generate_data():
    print(f"🚀 Starting Fortress Benchmark Generation...")
    
    print("⚙️ Loading Engine...")
    try:
        engine = CricketAnalyzer("data/FINAL_ODI_MASTER.csv")
    except Exception as e:
        print(f"❌ Failed to load engine: {e}")
        return None

    recorder = SnapshotRecorder(base_path=FIXTURES_DIR)
    
    output_data = {
        "Teams considered": TEAMS
    }
    
    total_tests = 0

    for home_team in TEAMS:
        print(f"\n🏠 Analyzing Fortress: {home_team.upper()}")
        venues = get_unique_venues_for_team(home_team)
        
        if not venues:
            continue

        for stadium in venues:
            # We group by Venue
            venue_key = f"{home_team} at {stadium}"
            output_data[venue_key] = {}
            print(f"   🏟️  {stadium}...")
            
            # Test Case: "All" Opponents (Global Fortress View)
            try:
                # Core Function Call
                result = engine.analyze_home_fortress(stadium, home_team, opp_team='All', years_back=10)
                
                if result is None:
                    result = "No data available"
                
                output_data[venue_key]["vs All"] = {
                    "opponent": "All",
                    "years_back": 10,
                    "expected_output": recorder._serialize(result)
                }
                total_tests += 1
                
            except Exception as e:
                print(f"     ❌ Error: {e}")
                output_data[venue_key]["vs All"] = {"error": str(e)}

    # Save Latest
    with open(LATEST_FILE, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"\n💾 Saved {total_tests} fortress snapshots to {LATEST_FILE}")
    return output_data

def compare_results():
    if not os.path.exists(EXPECTED_FILE):
        print("⚠️ No expected results found. Run generation first or use this as baseline.")
        return

    print("\n🔍 Comparing Results...")
    
    with open(EXPECTED_FILE, 'r') as f:
        expected = json.load(f)
    with open(LATEST_FILE, 'r') as f:
        latest = json.load(f)
        
    mismatches = []
    
    # Simple logic: Iterate Latest, check vs Expected
    # Note: Deep comparison needed for the list of dicts structure
    
    for venue_key, scenarios in latest.items():
        if venue_key == "Teams considered": continue
        
        if venue_key not in expected:
            mismatches.append(f"➕ NEW VENUE: {venue_key}")
            continue
            
        for scenario_key, data in scenarios.items():
            if scenario_key not in expected[venue_key]:
                 mismatches.append(f"➕ NEW SCENARIO: {venue_key} -> {scenario_key}")
                 continue
                 
            exp_val = expected[venue_key][scenario_key].get("expected_output")
            act_val = data.get("expected_output")
            
            # Compare JSON strings equality (Simplest robust check for serialized lists)
            if json.dumps(exp_val, sort_keys=True) != json.dumps(act_val, sort_keys=True):
                mismatches.append(f"❌ MISMATCH: {venue_key} -> {scenario_key}")

    # Report
    with open(FINAL_REPORT_FILE, 'w') as f:
        json.dump({"mismatches": mismatches}, f, indent=4)
            
    if not mismatches:
        print("✅ SUCCESS: No regressions found.")
    else:
        print(f"❌ FAILURE: Found {len(mismatches)} regressions. See final report.")

def merge_results():
    print("🔄 Merging Latest Results into Golden Master...")
    if os.path.exists(LATEST_FILE):
        with open(LATEST_FILE, 'r') as f:
            data = json.load(f)
        with open(EXPECTED_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print("✅ Golden Master Updated.")
    else:
        print("❌ No latest run found to merge.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--merge", action="store_true", help="Update expected results with latest run")
    args = parser.parse_args()
    
    generate_data()
    
    if args.merge:
        merge_results()
    else:
        compare_results()
