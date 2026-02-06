
import sys
import os
import json
import pandas as pd

# Define Project Root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.append(PROJECT_ROOT)

from engine import CricketAnalyzer
from venues import VENUE_MAP
from utils.test_recorder import SnapshotRecorder

# 📂 Paths
FIXTURES_DIR = os.path.join(PROJECT_ROOT, "tests/odi/analyze_phases/fixtures")
OUTPUT_FILE = os.path.join(FIXTURES_DIR, "analyze_phases_expected_results.json")
DATA_FILE = os.path.join(PROJECT_ROOT, "data/FINAL_ODI_MASTER.csv")

# 🌍 Config
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

def generate_golden_master():
    print(f"🚀 Generating Phase Analysis Golden Master...")
    
    if not os.path.exists(DATA_FILE):
        print(f"❌ Data file not found: {DATA_FILE}")
        return

    # Initialize Facade
    bot = CricketAnalyzer(DATA_FILE)
    engine = bot.team_engine
    
    # We use the generic recorder serialization, or just capture the return dict
    recorder = SnapshotRecorder(base_path=FIXTURES_DIR) 
    
    final_report = {"Phase Analysis Report": {}}
    
    # 1. Group Venues by Country
    unique_venues = sorted(list(set(VENUE_MAP.values())))
    
    for venue_id in unique_venues:
        host_nation = get_host_nation(venue_id)
        if not host_nation: continue  # Skip neutral/unknown venues for this specific 'Host vs World' test
        
        group_key = f"Grounds in {host_nation}"
        if group_key not in final_report["Phase Analysis Report"]:
            final_report["Phase Analysis Report"][group_key] = {}
            
        print(f"   🏟️  {venue_id} (Host: {host_nation})...")
        
        # Test Case 1: Host vs 'All' Visitors (Baseline)
        # outcome = engine.analyze_venue_phases(venue_id, home_team=host_nation, away_team='All', years=10)
        # Oops, function signature is `analyze_venue_phases(stadium_name, home_team=None, away_team=None, years=5)`
        
        # Test Case: Host vs 'All' Visitors (Baseline)
        try:
            # 1. Baseline (Host vs All)
            data_baseline = engine.analyze_venue_phases(venue_id, home_team=host_nation, away_team='All', years=10)
            
            final_report["Phase Analysis Report"][group_key][venue_id] = {
                "Host": host_nation,
                "Baseline_Metrics": data_baseline
            }
            
            # 2. Comprehensive Matchups: Host vs EVERY Opponent
            # This satisfies "Every country vs every country in every ground"
            opponents = [t for t in TEAMS if t != host_nation]
            
            for opp in opponents:
                print(f"      ⚔️  vs {opp}...")
                data_rival = engine.analyze_venue_phases(venue_id, home_team=host_nation, away_team=opp, years=10)
                final_report["Phase Analysis Report"][group_key][venue_id][f"vs_{opp}"] = data_rival

        except Exception as e:
            print(f"      ❌ Error: {e}")
            final_report["Phase Analysis Report"][group_key][venue_id] = {"Error": str(e)}

    os.makedirs(FIXTURES_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=4)
        
    print(f"\n✅ Structured Golden Master saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_golden_master()
