import pandas as pd
import numpy as np
import os

# --- CORE LOGIC (Format Agnostic) ---

def rebuild_intelligence_layer(config=None):
    """
    Refines raw ball-by-ball data into player stats and phase stats.
    Uses config for paths and phase boundaries.
    """
    if config is None:
        try:
            from formats.odi.config.settings import ODI_FORMAT_CONFIG
            config = ODI_FORMAT_CONFIG
        except ImportError:
            return

    cfg = config
    print(f"\n🏭 STARTING INTELLIGENCE REFINERY [{cfg['label']}]...")
    
    master_file = cfg['data_file']
    if not os.path.exists(master_file):
        print(f"❌ CRITICAL ERROR: '{master_file}' not found.")
        return

    # 1. LOAD MASTER
    print(f"📂 Loading Master Database ({os.path.basename(master_file)})...")
    df = pd.read_csv(master_file, low_memory=False)
    
    # 🚨 Data Type Enforcement
    df['match_id'] = df['match_id'].astype(str)
    df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
    cols_to_fix = ['runs_off_bat', 'extras', 'wides', 'noballs']
    for c in cols_to_fix: 
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    # 🚨 Ensure is_wicket exists
    if 'is_wicket' not in df.columns:
        if 'wicket_type' in df.columns:
            df['is_wicket'] = df['wicket_type'].notna().astype(int)
        elif 'player_dismissed' in df.columns:
            df['is_wicket'] = df['player_dismissed'].notna().astype(int)
        else:
            df['is_wicket'] = 0


    # ---------------------------------------------------------
    # 🏗️ PART 1: PLAYER STATS GENERATOR
    # ---------------------------------------------------------
    print("🔨 Building Player Profiles...")
    
    # A. BATTING STATS (Using 'batting_team' and 'bowling_team' from json_converter)
    # Note: We group by player/team/opponent to get vs_team context
    bat_base = df.groupby(['striker', 'batting_team', 'bowling_team']).agg({
        'match_id': 'nunique',
        'runs_off_bat': 'sum',
        'ball': 'count'
    }).reset_index()
    
    if 'player_dismissed' in df.columns:
        out_counts = df[df['player_dismissed'].notna()].groupby(['player_dismissed', 'batting_team', 'bowling_team']).size().reset_index(name='dismissals')
        bat_group = pd.merge(
            bat_base, 
            out_counts, 
            left_on=['striker', 'batting_team', 'bowling_team'], 
            right_on=['player_dismissed', 'batting_team', 'bowling_team'], 
            how='left'
        ).fillna(0)
        if 'player_dismissed' in bat_group.columns:
            bat_group.drop(columns=['player_dismissed'], inplace=True)
    else:
        bat_group = bat_base.copy()
        bat_group['dismissals'] = 0
    
    bat_group.rename(columns={
        'striker': 'player', 
        'batting_team': 'team', 
        'bowling_team': 'opponent',
        'match_id': 'innings',
        'runs_off_bat': 'runs',
        'ball': 'balls'
    }, inplace=True)
    bat_group['role'] = 'batting'
    bat_group['context'] = 'vs_team'

    # B. BOWLING STATS
    print("   ...calculating bowling stats")
    bowl_group = df.groupby(['bowler', 'bowling_team', 'batting_team']).agg({
        'match_id': 'nunique',
        'runs_off_bat': 'sum',
        'extras': 'sum',
        'ball': 'count', 
        'is_wicket': 'sum'
    }).reset_index()
    
    bowl_group['runs_conceded'] = bowl_group['runs_off_bat'] + bowl_group['extras']
    
    bowl_group.rename(columns={
        'bowler': 'player', 
        'bowling_team': 'team', 
        'batting_team': 'opponent',
        'match_id': 'innings',
        'runs_conceded': 'runs',
        'ball': 'balls',
        'is_wicket': 'dismissals' 
    }, inplace=True)
    bowl_group['role'] = 'bowling'
    bowl_group['context'] = 'vs_team'
    
    # Combine & Save
    player_stats = pd.concat([bat_group, bowl_group], ignore_index=True)
    p_path = cfg.get('player_stats_file', 'processed_player_stats.csv')
    player_stats.to_csv(p_path, index=False)
    print(f"   ✅ Saved: {p_path}")

    # Metadata
    m_path = cfg.get('metadata_file', 'player_metadata.csv')
    meta = player_stats[['player', 'team']].drop_duplicates()
    meta.to_csv(m_path, index=False)

    # ---------------------------------------------------------
    # 🏗️ PART 2: PHASE STATS GENERATOR
    # ---------------------------------------------------------
    print("🔨 Building Phase Analysis...")
    
    phases_cfg = cfg.get('phases', {})
    
    def get_phase(ball_val):
        try:
            over = int(float(ball_val))
            for p_id, p_info in phases_cfg.items():
                if p_info['start'] <= over <= p_info['end']:
                    return p_id
            return 'mid'
        except (ValueError, TypeError): return 'mid'
 
    df['phase'] = df['ball'].apply(get_phase)
    df['total_runs'] = df['runs_off_bat'] + df['extras']
    
    # Using 'batting_team' as 'team' for phase analysis
    grouped = df.groupby(['match_id', 'start_date', 'venue', 'innings', 'batting_team', 'phase']).agg({
        'total_runs': 'sum',
        'is_wicket': 'sum'
    }).reset_index()
  
    pivot_df = grouped.pivot_table(
        index=['match_id', 'start_date', 'venue', 'innings', 'batting_team'],
        columns='phase',
        values=['total_runs', 'is_wicket'],
        fill_value=0
    ).reset_index()
  
    # Flatten
    new_cols = []
    for col in pivot_df.columns:
        if isinstance(col, tuple):
            metric, phase = col
            if phase: new_cols.append(f"{phase}_{'runs' if metric=='total_runs' else 'wkts'}")
            else: new_cols.append(metric)
        else: new_cols.append(col)
    pivot_df.columns = new_cols
    pivot_df.rename(columns={'batting_team': 'team'}, inplace=True)

    ph_path = cfg.get('phase_stats_file', 'processed_phase_stats.csv')
    pivot_df.to_csv(ph_path, index=False)
    print(f"   ✅ Saved: {ph_path}")

    print(f"✨ REFINERY COMPLETE for {cfg['label']}.")

if __name__ == "__main__":
    rebuild_intelligence_layer()
