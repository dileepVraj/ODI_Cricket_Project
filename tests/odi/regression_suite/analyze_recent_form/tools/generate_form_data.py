
import pandas as pd
import json
import os
import sys

# -------------------------------------------------------------------------
# 🚨 STRICT IMPORT: Use Facade, NOT pd.read_csv
# -------------------------------------------------------------------------
# Go up 4 levels: tests -> odi -> analyze_recent_form -> tools -> PROJECT_ROOT
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
sys.path.append(project_root)

from engine import CricketAnalyzer

# -------------------------------------------------------------------------
# ⚙️ CONFIG UTILITY
# -------------------------------------------------------------------------
DB_PATH = os.path.join(project_root, "data", "FINAL_ODI_MASTER.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../fixtures/recent_form_expected_results.json")

def generate_form_master():
    print("🚀 Generating Recent Form Golden Master (Global + Continents)...")
    
    # 1. Initialize Engine
    engine = CricketAnalyzer(DB_PATH)
    
    master_data = {}

    # Define Scope
    target_teams = ['India', 'Australia', 'England', 'Pakistan', 'South Africa', 'New Zealand', 'West Indies', 'Sri Lanka']
    continents = ['Asia', 'Africa', 'Europe', 'Oceania', 'Americas']

    for team in target_teams:
        print(f"   Analyzing {team}...")
        master_data[team] = {}
        
        # 1. GLOBAL FORM (Overall)
        res_global = engine.team_engine.analyze_team_form(team, opp_team='All', continent='All')
        if res_global:
            master_data[team]['Global'] = { "summary_code": res_global['summary_code'] }
        else:
            master_data[team]['Global'] = None

        # 2. CONTINENTAL FORM
        for cont in continents:
            res_cont = engine.team_engine.analyze_team_form(team, opp_team='All', continent=cont)
            if res_cont:
                master_data[team][cont] = { "summary_code": res_cont['summary_code'] }
            else:
                 master_data[team][cont] = None # Capture 'None' to verify lack of data persists

    # ---------------------------------------------------------------------
    # 💾 SAVE SNAPSHOT
    # ---------------------------------------------------------------------
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, indent=4, default=str)
        
    print(f"✅ Saved Golden Master to: {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_form_master()
