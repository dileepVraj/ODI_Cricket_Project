import pandas as pd
import numpy as np
import os

# --- CONFIG ---
MASTER_FILE = 'data/FINAL_ODI_MASTER.csv'
PLAYER_OUTPUT = 'data/processed_player_stats.csv'
PHASE_OUTPUT = 'data/processed_phase_stats.csv'
METADATA_OUTPUT = 'data/player_metadata.csv'

def rebuild_intelligence_layer():
    print("🏭 STARTING INTELLIGENCE REFINERY...")
    
    if not os.path.exists(MASTER_FILE):
        print(f"❌ CRITICAL: {MASTER_FILE} not found. Run json_converter.py first.")
        return

    # 1. LOAD MASTER
    print(f"📂 Loading Master Database ({MASTER_FILE})...")
    df = pd.read_csv(MASTER_FILE, low_memory=False)
    
    # 🚨 Data Type Enforcement
    df['match_id'] = df['match_id'].astype(str)
    df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
    cols_to_fix = ['runs_off_bat', 'extras', 'wides', 'noballs']
    for c in cols_to_fix: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    # 🚨 Ensure is_wicket exists early
    if 'is_wicket' not in df.columns:
        # Use wicket_type if available (more reliable), else player_dismissed
        if 'wicket_type' in df.columns:
            df['is_wicket'] = df['wicket_type'].notna().astype(int)
        else:
            df['is_wicket'] = df['player_dismissed'].notna().astype(int)


    # ---------------------------------------------------------
    # 🏗️ PART 1: PLAYER STATS GENERATOR
    # ---------------------------------------------------------
    print("\n🔨 Building Player Profiles...")
    
    # A. BATTING STATS
    print("   ...calculating batting stats")
    bat_group = df.groupby(['striker', 'batting_team', 'bowling_team']).agg({
        'match_id': 'nunique',
        'runs_off_bat': 'sum',
        'ball': 'count',
        'player_dismissed': 'count' # This counts distinct dismissal events
    }).reset_index()
    
    bat_group.rename(columns={
        'striker': 'player', 
        'batting_team': 'team', 
        'bowling_team': 'opponent',
        'match_id': 'innings',
        'runs_off_bat': 'runs',
        'ball': 'balls',
        'player_dismissed': 'dismissals'
    }, inplace=True)
    bat_group['role'] = 'batting'
    bat_group['context'] = 'vs_team'

    # B. BOWLING STATS
    print("   ...calculating bowling stats")
    # Filter for legal deliveries for ball counts? 
    # For simplicity, we count all records where bowler is present
    bowl_group = df.groupby(['bowler', 'bowling_team', 'batting_team']).agg({
        'match_id': 'nunique',
        'runs_off_bat': 'sum',
        'extras': 'sum',
        'ball': 'count', # This counts total deliveries logged
        'is_wicket': 'sum' # Assuming is_wicket column exists, if not calculate it
    }).reset_index()
    


    bowl_group['runs_conceded'] = bowl_group['runs_off_bat'] + bowl_group['extras']
    
    bowl_group.rename(columns={
        'bowler': 'player', 
        'bowling_team': 'team', 
        'batting_team': 'opponent',
        'match_id': 'innings',
        'runs_conceded': 'runs',
        'ball': 'balls',
        'is_wicket': 'dismissals' # re-using column name for standardization
    }, inplace=True)
    bowl_group['role'] = 'bowling'
    bowl_group['context'] = 'vs_team'
    
    # Combine
    player_stats = pd.concat([bat_group, bowl_group], ignore_index=True)
    
    print(f"💾 Saving Player Stats to {PLAYER_OUTPUT}...")
    player_stats.to_csv(PLAYER_OUTPUT, index=False)

    # 🏗️ PART 1.5: METADATA (For Squad Loading)
    print("🔨 Extracting Player Metadata...")
    # Get unique player-team combos
    meta = player_stats[['player', 'team']].drop_duplicates()
    meta.to_csv(METADATA_OUTPUT, index=False)

    # ---------------------------------------------------------
    # 🏗️ PART 2: PHASE STATS GENERATOR
    # ---------------------------------------------------------
    print("\n🔨 Building Phase Analysis...")
    
    # Helper for Phases
    def get_phase(ball_val):
        try:
            over = int(float(ball_val)) # 0.1 -> 0
            if over < 10: return 'pp'      # 0-9
            elif over < 40: return 'mid'   # 10-39
            else: return 'dth'             # 40-49
        except: return 'mid'

    df['phase'] = df['ball'].apply(get_phase)
    df['total_runs'] = df['runs_off_bat'] + df['extras']
    
    # Aggregate
    grouped = df.groupby(['match_id', 'start_date', 'venue', 'innings', 'batting_team', 'phase']).agg({
        'total_runs': 'sum',
        'is_wicket': 'sum'
    }).reset_index()

    # Pivot
    pivot_df = grouped.pivot_table(
        index=['match_id', 'start_date', 'venue', 'innings', 'batting_team'],
        columns='phase',
        values=['total_runs', 'is_wicket'],
        fill_value=0
    ).reset_index()

    # Flatten Columns
    new_cols = []
    for col in pivot_df.columns:
        if isinstance(col, tuple):
            metric, phase = col
            if phase: new_cols.append(f"{phase}_{'runs' if metric=='total_runs' else 'wkts'}")
            else: new_cols.append(metric)
        else: new_cols.append(col)
    pivot_df.columns = new_cols
    pivot_df.rename(columns={'batting_team': 'team'}, inplace=True)

    print(f"💾 Saving Phase Stats to {PHASE_OUTPUT}...")
    pivot_df.to_csv(PHASE_OUTPUT, index=False)

    print("\n✅ REFINERY COMPLETE. Dashboard is ready to launch.")

if __name__ == "__main__":
    rebuild_intelligence_layer()