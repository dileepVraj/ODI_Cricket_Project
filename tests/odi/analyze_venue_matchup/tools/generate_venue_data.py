import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

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

def get_unique_venues_for_team(team_name):
    prefix = TEAM_PREFIX_MAP.get(team_name)
    if not prefix:
        return []
    
    # 1. Group by Master ID to avoid duplications (Aliases)
    unique_venues = {}
    for raw_name, master_id in VENUE_MAP.items():
        if master_id.startswith(prefix):
            if master_id not in unique_venues:
                unique_venues[master_id] = raw_name # Pick the first available name as representative
    
    return list(unique_venues.values())

def generate_data():
    print(f"🚀 Starting Massive Data Generation (Nested Format)...")
    print(f"📅 Time: {datetime.now()}")
    
    # 1. Initialize Engine
    print("⚙️ Loading Engine (This may take a moment)...")
    try:
        engine = CricketAnalyzer("data/FINAL_ODI_MASTER.csv")
    except Exception as e:
        print(f"❌ Failed to load engine: {e}")
        return

    recorder = SnapshotRecorder(base_path="tests/odi/analyze_venue_matchup/fixtures")
    
    # OUTPUT STRUCTURE 
    final_output = {
        "Teams considered": TEAMS,
        # Other keys will be added dynamically
    }
    
    total_matchups = 0

    # 2. Iterate Logic
    for home_team in TEAMS:
        print(f"\n🏠 HOME TEAM: {home_team.upper()}")
        
        venues = get_unique_venues_for_team(home_team)
        print(f"   📍 Found {len(venues)} Venues: {venues[:3]}...")
        
        if not venues:
            continue

        for stadium in venues:
            # Create Section Key for this Venue
            section_key = f"{home_team} vs all remaining teams results at {stadium}"
            final_output[section_key] = {}
            
            print(f"      🏟️  Processing: {section_key}")
            
            for away_team in TEAMS:
                if home_team == away_team:
                    continue
                
                matchup_key = f"{home_team} vs {away_team}"
                
                try:
                    # EXECUTE CORE FUNCTION (Default: 5 years)
                    result = engine.analyze_venue_matchup(stadium, home_team, away_team)
                    
                    # Convert None to readable string if no data
                    if result is None:
                        result = "No data available"
                    
                    # Prepare the Value Object
                    matchup_data = {
                        "home_team": home_team,
                        "opp_team": away_team,
                        "years_back": 5,
                        "expected_output": recorder._serialize(result)
                    }
                    
                    # Add to nested structure
                    final_output[section_key][matchup_key] = matchup_data
                    total_matchups += 1
                    
                except Exception as e:
                    print(f" ❌ Error for {matchup_key}: {e}")
                    final_output[section_key][matchup_key] = {
                        "home_team": home_team,
                        "opp_team": away_team,
                        "years_back": 5,
                        "expected_output": f"Error: {str(e)}"
                    }

    # 3. Save
    output_path = "tests/odi/analyze_venue_matchup/fixtures/analyze_venue_matchup_expected_results.json"
    print(f"\n💾 Saving {total_matchups} matchup results to {output_path}...")
    
    with open(output_path, 'w') as f:
        json.dump(final_output, f, indent=4)
        
    print("✅ GENERATION COMPLETE.")

if __name__ == "__main__":
    generate_data()
