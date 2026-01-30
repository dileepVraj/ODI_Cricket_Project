import pandas as pd
import numpy as np
import os

def rebuild_intelligence_layer():
    print("🏭 STARTING INTELLIGENCE REFINERY...")
    
    # 1. LOAD MASTER
    if not os.path.exists('data/FINAL_ODI_MASTER.csv'):
        print("❌ Master CSV missing. Run json_converter.py first.")
        return

    df = pd.read_csv('data/FINAL_ODI_MASTER.csv', low_memory=False)
    df.columns = df.columns.str.strip().str.lower()
    
    # 🚨 VERIFY COLUMNS
    if 'innings' not in df.columns:
        print(f"❌ ERROR: 'innings' column missing. Columns found: {list(df.columns)}")
        return

    # Fix Types
    df['match_id'] = df['match_id'].astype(str)
    df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
    for c in ['runs_off_bat', 'extras']: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    # ---------------------------------------------------------
    # PART 1: PLAYER STATS
    # ---------------------------------------------------------
    print("🔨 Building Player Profiles...")
    
    # Create is_wicket
    if 'is_wicket' not in df.columns:
        if 'player_dismissed' in df.columns:
            df['is_wicket'] = df['player_dismissed'].notna().astype(int)
        else:
            df['is_wicket'] = 0

    # Batting
    bat_group = df.groupby(['striker', 'batting_team', 'bowling_team']).agg({
        'match_id': 'nunique', 'runs_off_bat': 'sum', 'ball': 'count', 'is_wicket': 'sum'
    }).reset_index()
    
    bat_group.columns = ['player', 'team', 'opponent', 'innings', 'runs', 'balls', 'dismissals']
    bat_group['role'] = 'batting'; bat_group['context'] = 'vs_team'

    # Bowling
    bowl_group = df.groupby(['bowler', 'bowling_team', 'batting_team']).agg({
        'match_id': 'nunique', 'runs_off_bat': 'sum', 'extras': 'sum', 'ball': 'count', 'is_wicket': 'sum'
    }).reset_index()
    
    bowl_group['runs'] = bowl_group['runs_off_bat'] + bowl_group['extras']
    bowl_group = bowl_group[['bowler', 'bowling_team', 'batting_team', 'match_id', 'runs', 'ball', 'is_wicket']]
    bowl_group.columns = ['player', 'team', 'opponent', 'innings', 'runs', 'balls', 'dismissals']
    bowl_group['role'] = 'bowling'; bowl_group['context'] = 'vs_team'
    
    pd.concat([bat_group, bowl_group], ignore_index=True).to_csv('data/processed_player_stats.csv', index=False)
    
    # Metadata
    df[['striker', 'batting_team']].rename(columns={'striker':'player','batting_team':'team'}).drop_duplicates().to_csv('data/player_metadata.csv', index=False)

    # ---------------------------------------------------------
    # PART 2: PHASE STATS
    # ---------------------------------------------------------
    print("🔨 Building Phase Analysis...")
    
    def get_phase(ball_val):
        try: return 'pp' if float(ball_val) < 10 else 'mid' if float(ball_val) < 40 else 'dth'
        except: return 'mid'

    df['phase'] = df['ball'].apply(get_phase)
    df['total_runs'] = df['runs_off_bat'] + df['extras']
    
    # Grouping
    phase_group = df.groupby(['match_id', 'start_date', 'venue', 'innings', 'batting_team', 'phase']).agg({
        'total_runs': 'sum', 'is_wicket': 'sum'
    }).reset_index()

    pivot_df = phase_group.pivot_table(
        index=['match_id', 'start_date', 'venue', 'innings', 'batting_team'],
        columns='phase', values=['total_runs', 'is_wicket'], fill_value=0
    ).reset_index()

    # Flatten
    new_cols = []
    for c in pivot_df.columns:
        if isinstance(c, tuple):
            if c[1]: new_cols.append(f"{c[1]}_{'runs' if c[0]=='total_runs' else 'wkts'}")
            else: new_cols.append(c[0])
        else: new_cols.append(c)
        
    pivot_df.columns = new_cols
    pivot_df.rename(columns={'batting_team': 'team'}, inplace=True)
    
    pivot_df.to_csv('data/processed_phase_stats.csv', index=False)
    print("✅ REFINERY COMPLETE.")

if __name__ == "__main__":
    rebuild_intelligence_layer()