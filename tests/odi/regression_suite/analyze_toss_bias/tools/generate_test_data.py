
import pandas as pd
import json
import os
import sys

# Define Project Root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.append(PROJECT_ROOT)

# 🚨 CRITICAL FIX: Import the Facade (CricketAnalyzer) to ensure standardized data
from engine import CricketAnalyzer
from venues import VENUE_MAP

# 📂 Paths
FIXTURES_DIR = os.path.join(PROJECT_ROOT, "tests/odi/analyze_toss_bias/fixtures")
OUTPUT_FILE = os.path.join(FIXTURES_DIR, "analyze_toss_bias_expected_results.json")
DATA_FILE = os.path.join(PROJECT_ROOT, "data/FINAL_ODI_MASTER.csv")

# 🌍 DYNAMIC VENUE MAPPING (100% Coverage from venues.py)
def get_all_venues_grouped():
    """
    Dynamically builds the venue list from VENUE_MAP to ensure we cover 
    ALL stadiums defined in the system.
    """
    groups = {}
    
    # helper for clean naming
    country_map = {
        "IND": "India", "AUS": "Australia", "ENG": "England", "SA": "South Africa",
        "NZ": "New Zealand", "PAK": "Pakistan", "SL": "Sri Lanka", "WI": "West Indies",
        "BAN": "Bangladesh", "UAE": "UAE", "ZIM": "Zimbabwe", "IRE": "Ireland",
        "SCO": "Scotland", "NED": "Netherlands", "AFG": "Afghanistan"
    }

    unique_ids = sorted(list(set(VENUE_MAP.values())))
    
    for v_id in unique_ids:
        prefix = v_id.split('_')[0]
        country_name = country_map.get(prefix, f"Others ({prefix})")
        group_key = f"Grounds in {country_name}"
        
        if group_key not in groups:
            groups[group_key] = []
        
        groups[group_key].append(v_id)
        
    return groups

VENUE_GROUPS = get_all_venues_grouped()

def parse_engine_output(data_list, years=10):
    """
    Converts the Engine's UI-List format into the User's Dictionary Format.
    """
    if not data_list: return None
    
    def get_val(metric_name):
        for item in data_list:
            if item['Metric'] == metric_name:
                return item['Value']
        return "-"

    w1_str = get_val("Win % Batting 1st")
    w2_str = get_val("Win % Chasing")
    
    # Extract total from parens: "57% (16)" -> 16
    try:
        n1 = int(w1_str.split('(')[1].replace(')', ''))
        n2 = int(w2_str.split('(')[1].replace(')', ''))
        total = n1 + n2 
    except:
        total = 0
        
    pct1 = int(w1_str.split('%')[0]) if '%' in w1_str else 0
    pct2 = int(w2_str.split('%')[0]) if '%' in w2_str else 0
    
    verdict = "Neutral"
    if pct1 >= 55: verdict = "Bat First"
    elif pct2 >= 55: verdict = "Bat Second"
    if "BOWL" in verdict: verdict = "Bat Second" 
    
    return {
        "Period": f"Last {years} years",
        "Matches analyzed": total,
        "Bias Verdict": verdict,
        "Win % Batting First": w1_str,
        "Win % Chasing": w2_str,
        "Avg 1st innings score": get_val("Avg 1st Innings Score"),
        "Avg 2nd innings score": get_val("Avg 2nd Innings Score")
    }

def generate_golden_master():
    print(f"🚀 Generating Structured Golden Master (Top 10 Nations)...")
    
    if not os.path.exists(DATA_FILE):
        print(f"❌ Data file not found: {DATA_FILE}")
        return

    # 🚨 CRITICAL CHANGE: Initialize the Full System (Facade)
    # This triggers column cleaning, venue standardization, and correct Match ID merging.
    bot = CricketAnalyzer(DATA_FILE)
    engine = bot.team_engine
    
    final_report = {"Toss bias report": {}}
    
    for group, venues in VENUE_GROUPS.items():
        print(f"   📂 {group}...")
        final_report["Toss bias report"][group] = {}
        
        for venue_id in venues:
            try:
                # 5 Years to match User's Screenshot preference (or keep 10 if standard)
                # User screenshot showed "Last 5 Years". Let's stick to 10 for regression stability unless asked.
                # Actually, user complained about discrepancy.
                # But regression is usually 10. The screenshot was manual usage.
                # I will keep 10 but ensure it WORKS (finds data).
                raw_data = engine.analyze_venue_bias(venue_id, years_back=10)
                
                if raw_data:
                    parsed = parse_engine_output(raw_data)
                    final_report["Toss bias report"][group][venue_id] = parsed
                else:
                    print(f"      ⚠️ No Data for {venue_id}")
                    final_report["Toss bias report"][group][venue_id] = "Insufficient Data"
                    
            except Exception as e:
                print(f"      ❌ Error: {venue_id} -> {e}")
                final_report["Toss bias report"][group][venue_id] = {"Error": str(e)}

    os.makedirs(FIXTURES_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=4, ensure_ascii=True) 
        
    print(f"\n✅ Structured Golden Master saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_golden_master()
