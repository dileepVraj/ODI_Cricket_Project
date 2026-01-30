import json
import pandas as pd
import glob
import os
import numpy as np

# --- CONFIGURATION ---
SOURCE_DIR = 'data/json_source'
OUTPUT_BBB = 'data/FINAL_ODI_MASTER.csv'   # Ball-by-Ball
OUTPUT_SQUADS = 'data/MATCH_SQUADS.csv'    # Players
OUTPUT_INFO = 'data/MATCH_INFO.csv'        # Context

def process_matches():
    print(f"🚀 IGNITION: Starting Final JSON Conversion...")
    print(f"📂 Source: {SOURCE_DIR}")
    
    json_files = glob.glob(os.path.join(SOURCE_DIR, '*.json'))
    
    if not json_files:
        print("❌ CRITICAL: No JSON files found.")
        return

    print(f"📦 Found {len(json_files)} matches. Processing...")
    
    all_deliveries = []
    all_squads = []
    all_infos = []
    
    matches_processed = 0
    
    for filepath in json_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 1. EXTRACT INFO
            info = data.get('info', {})
            match_id = os.path.splitext(os.path.basename(filepath))[0]
            dates = info.get('dates', [])
            start_date = dates[0] if dates else None
            venue = info.get('venue', 'Unknown')
            teams = info.get('teams', ["Unknown", "Unknown"])
            outcome = info.get('outcome', {})
            winner = outcome.get('winner', 'No Result')

            # 2. MATCH CONTEXT LOGGING
            all_infos.append({
                'match_id': match_id,
                'start_date': start_date,
                'venue': venue,
                'team_1': teams[0] if len(teams) > 0 else None,
                'team_2': teams[1] if len(teams) > 1 else None,
                'winner': winner,
                'toss_winner': info.get('toss', {}).get('winner', None),
                'toss_decision': info.get('toss', {}).get('decision', None)
            })

            # 3. SQUADS
            if 'players' in info:
                for team_name, players in info['players'].items():
                    for player in players:
                        all_squads.append({
                            'match_id': match_id,
                            'date': start_date,
                            'team': team_name,
                            'player': player
                        })

            # 4. BALL-BY-BALL (The Critical Logic)
            # The inspection showed 'innings' is a list. We iterate it.
            for innings_index, inn_data in enumerate(data.get('innings', [])):
                bat_team = inn_data.get('team')
                
                # Determine bowling team
                bowl_team = "Unknown"
                for t in teams:
                    if t != bat_team:
                        bowl_team = t
                        break

                # 🚨 CRITICAL: Explicitly Assign Innings Number (1-based)
                innings_num = innings_index + 1

                if 'overs' in inn_data:
                    # Flatten Overs -> Deliveries
                    df_inn = pd.json_normalize(
                        inn_data['overs'], 
                        record_path=['deliveries'], 
                        meta=['over']
                    )
                    
                    if not df_inn.empty:
                        # 🚨 FORCE CONTEXT COLUMNS ON EVERY ROW
                        df_inn['match_id'] = str(match_id)
                        df_inn['start_date'] = start_date
                        df_inn['venue'] = venue
                        df_inn['batting_team'] = bat_team
                        df_inn['bowling_team'] = bowl_team
                        df_inn['innings'] = int(innings_num) # <--- This fixes the KeyError
                        df_inn['winner'] = winner
                        
                        all_deliveries.append(df_inn)

            matches_processed += 1
            if matches_processed % 500 == 0:
                print(f"   ...parsed {matches_processed} matches")

        except Exception as e:
            # print(f"Error in {filepath}: {e}") # Uncomment to debug specific files
            continue

    print(f"✅ Parsing Complete. Merging & Saving...")

    # --- SAVE 1: MATCH INFO ---
    if all_infos:
        pd.DataFrame(all_infos).to_csv(OUTPUT_INFO, index=False)
        print(f"💾 Saved {OUTPUT_INFO}")

    # --- SAVE 2: SQUADS ---
    if all_squads:
        pd.DataFrame(all_squads).to_csv(OUTPUT_SQUADS, index=False)
        print(f"💾 Saved {OUTPUT_SQUADS}")

    # --- SAVE 3: MASTER CSV (With Validation) ---
    if all_deliveries:
        master_df = pd.concat(all_deliveries, ignore_index=True)
        
        # Rename standard columns based on your inspection
        col_map = {
            'over': 'over_num',
            'batter': 'striker',
            'bowler': 'bowler',
            'non_striker': 'non_striker',
            'runs.batter': 'runs_off_bat',
            'runs.extras': 'extras',
            # Extras breakdown (might be NaN if not present)
            'extras.wides': 'wides',
            'extras.noballs': 'noballs',
            'extras.byes': 'byes',
            'extras.legbyes': 'legbyes',
            'extras.penalty': 'penalty'
        }
        master_df.rename(columns=col_map, inplace=True)
        
        # Calculate Ball Number (0.1, 0.2, etc.)
        # We group by match/innings/over to count balls
        master_df['ball_rank'] = master_df.groupby(['match_id', 'innings', 'over_num']).cumcount() + 1
        master_df['ball'] = master_df['over_num'].astype(str) + "." + master_df['ball_rank'].astype(str)
        master_df['ball'] = master_df['ball'].astype(float)
        
        # Wicket Logic (Handle list of dicts)
        if 'wickets' in master_df.columns:
            def get_wkt(x): 
                if isinstance(x, list) and len(x) > 0 and isinstance(x[0], dict):
                    return x[0].get('kind')
                return None
            
            def get_player(x): 
                if isinstance(x, list) and len(x) > 0 and isinstance(x[0], dict):
                    return x[0].get('player_out')
                return None

            master_df['wicket_type'] = master_df['wickets'].apply(get_wkt)
            master_df['player_dismissed'] = master_df['wickets'].apply(get_player)
        else:
            master_df['wicket_type'] = None
            master_df['player_dismissed'] = None

        # 🚨 FINAL COLUMN CHECK
        # We ensure these columns exist even if the JSON didn't have them
        required_cols = [
            'match_id', 'start_date', 'venue', 'batting_team', 'bowling_team', 'innings', 'ball', 
            'striker', 'non_striker', 'bowler', 'runs_off_bat', 'extras', 
            'wides', 'noballs', 'wicket_type', 'player_dismissed', 'winner'
        ]
        
        # Add missing columns with 0 or None
        for c in required_cols:
            if c not in master_df.columns:
                if c in ['runs_off_bat', 'extras', 'wides', 'noballs']:
                    master_df[c] = 0
                else:
                    master_df[c] = None

        # Fill numeric NaNs with 0
        fill_cols = ['runs_off_bat', 'extras', 'wides', 'noballs']
        for c in fill_cols:
            master_df[c] = pd.to_numeric(master_df[c], errors='coerce').fillna(0)

        print(f"💾 Saving Ball-by-Ball: {OUTPUT_BBB} ({len(master_df)} rows)")
        # Save ONLY the required columns to keep it clean
        master_df[required_cols].to_csv(OUTPUT_BBB, index=False)

    print("\n✅ DATA RE-GENERATION SUCCESSFUL.")

if __name__ == "__main__":
    process_matches()