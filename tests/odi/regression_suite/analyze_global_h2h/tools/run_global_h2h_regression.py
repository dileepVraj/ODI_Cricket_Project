import sys
import os
import json
import argparse

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from engine import CricketAnalyzer
from utils.test_recorder import SnapshotRecorder

# CONFIGURATION
TEAMS = [
    "Australia", "Bangladesh", "England", "India", 
    "New Zealand", "Pakistan", "South Africa", "Sri Lanka", "West Indies"
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures")
EXPECTED_FILE = os.path.join(FIXTURES_DIR, "analyze_global_h2h_expected_results.json")
LATEST_FILE = os.path.join(FIXTURES_DIR, "analyze_global_h2h_latest_test_run_results.json")
FINAL_REPORT_FILE = os.path.join(FIXTURES_DIR, "analyze_global_h2h_test_report.json")

def generate_data():
    print(f"🚀 Starting Global H2H Benchmark Generation...")
    
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

    for team_a in TEAMS:
        parent_key = f"{team_a} vs rest"
        output_data[parent_key] = {}
        print(f"\n🌍 Analyzing Group: {parent_key}")
        
        for team_b in TEAMS:
            if team_a == team_b: continue
            
            # Note: We now explicitly run BOTH directions (Aus vs Eng AND Eng vs Aus)
            # because the user requested a full matrix in the template.
            
            scenario_key = f"{team_a} vs {team_b}"
            print(f"   ⚔️  {scenario_key}...")
            
            try:
                # Core Function Call
                result = engine.analyze_global_h2h(team_a, team_b, years_back=5)
                
                if result is None:
                    result = "No data available"
                
                output_data[parent_key][scenario_key] = {
                    "team_a": team_a,
                    "team_b": team_b,
                    "years_back": 5,
                    "expected_output": recorder._serialize(result)
                }
                total_tests += 1
                
            except Exception as e:
                print(f"     ❌ Error: {e}")
                output_data[parent_key][scenario_key] = {"error": str(e)}

    # Save Latest
    with open(LATEST_FILE, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"\n💾 Saved {total_tests} Global H2H snapshots to {LATEST_FILE}")
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
    
    for group_key, group_data in latest.items():
        if group_key == "Teams considered": continue
        
        if group_key not in expected:
            mismatches.append(f"➕ NEW GROUP: {group_key}")
            continue
            
        for scenario_key, data in group_data.items():
            if scenario_key not in expected[group_key]:
                mismatches.append(f"➕ NEW SCENARIO: {group_key} -> {scenario_key}")
                continue

            exp_val = expected[group_key][scenario_key].get("expected_output")
            act_val = data.get("expected_output")
            
            if json.dumps(exp_val, sort_keys=True) != json.dumps(act_val, sort_keys=True):
                mismatches.append(f"❌ MISMATCH: {scenario_key}")

    # Report
    with open(FINAL_REPORT_FILE, 'w') as f:
        json.dump({"mismatches": mismatches}, f, indent=4)
            
    if not mismatches:
        print("✅ SUCCESS: No regressions found.")
    else:
        print(f"❌ FAILURE: Found {len(mismatches)} regressions. See test report.")

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
