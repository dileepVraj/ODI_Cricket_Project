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
EXPECTED_FILE = os.path.join(FIXTURES_DIR, "analyze_away_performance_expected_results.json")
LATEST_FILE = os.path.join(FIXTURES_DIR, "analyze_away_performance_latest_test_run_results.json")
FINAL_REPORT_FILE = os.path.join(FIXTURES_DIR, "analyze_away_performance_test_report.json")

def generate_data():
    print(f"🚀 Starting Away Performance Benchmark Generation...")
    
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

    for team in TEAMS:
        print(f"\n✈️ Analyzing Away Performance: {team.upper()}")
        
        try:
            # Core Function Call
            # analyze_away_performance(self, team_name, years_back=5, recorder=None)
            result = engine.analyze_away_performance(team, years_back=10)
            
            if result is None:
                result = "No data available"
            
            output_data[team] = {
                "team": team,
                "years_back": 10,
                "expected_output": recorder._serialize(result)
            }
            total_tests += 1
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
            output_data[team] = {"error": str(e)}

    # Save Latest
    with open(LATEST_FILE, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"\n💾 Saved {total_tests} Away Performance snapshots to {LATEST_FILE}")
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
    
    for key, data in latest.items():
        if key == "Teams considered": continue
        
        if key not in expected:
            mismatches.append(f"➕ NEW SCENARIO: {key}")
            continue
            
        exp_val = expected[key].get("expected_output")
        act_val = data.get("expected_output")
        
        if json.dumps(exp_val, sort_keys=True) != json.dumps(act_val, sort_keys=True):
            mismatches.append(f"❌ MISMATCH: {key}")

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
