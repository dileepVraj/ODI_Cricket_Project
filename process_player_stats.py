import pandas as pd
import zipfile
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# 🛠️ SETTINGS
ZIP_PATH = 'data/raw_odi_backup.zip'
OUTPUT_FILE = 'data/processed_player_stats.csv'
METADATA_FILE = 'data/player_metadata.csv' # New file to map Player -> Country

def process_ball_by_ball():
    print(f"📂 Scanning {ZIP_PATH}...")
    
    all_match_data = []
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        csv_files = [f for f in z.namelist() if f.endswith('.csv')]
        total_files = len(csv_files)
        print(f"🚀 Found {total_files} files. Identifying Ball-by-Ball data...")
        
        for i, file_name in enumerate(csv_files):
            if i % 200 == 0: print(f"   Scanning file {i}/{total_files}...", end='\r')
            
            with z.open(file_name) as f:
                try:
                    # Quick header check
                    header_df = pd.read_csv(f, nrows=0)
                    cols = set(header_df.columns)
                    if 'striker' in cols and 'runs_off_bat' in cols and 'bowler' in cols:
                        f.seek(0)
                        df = pd.read_csv(f)
                        all_match_data.append(df)
                except:
                    continue

    if not all_match_data:
        print("❌ No valid data found.")
        return

    print(f"\n🧩 Merging {len(all_match_data)} matches...")
    full_df = pd.concat(all_match_data, ignore_index=True)
    
    # --- PRE-PROCESSING ---
    print("🧹 Cleaning & Tagging Data...")
    
    # 1. Legal Balls (For Batting SR and Bowling Econ)
    # Note: Wides count as runs for bowler, but NOT as a ball bowled
    full_df['is_legal_ball'] = (full_df['wides'].isna()) | (full_df['wides'] == 0)
    
    # 2. Bowler Wickets (Exclude Run Outs)
    bowler_wicket_types = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    full_df['is_bowler_wicket'] = full_df['wicket_type'].isin(bowler_wicket_types).astype(int)
    
    # 3. Total Runs Conceded by Bowler (Batsman Runs + Wides + NoBalls)
    # We treat NaNs as 0
    full_df['extras'] = full_df['extras'].fillna(0)
    full_df['total_runs'] = full_df['runs_off_bat'] + full_df['extras']
    # Note: Byes/Legbyes usually don't count against bowler economy in strict stats, 
    # but for simple trading data, 'total_runs' is a safe proxy.
    
    # --- PART A: PLAYER METADATA (Map Player -> Team) ---
    print("🌍 Extracting Player Nationalities...")
    # We determine a player's team by seeing who they batted for last
    player_teams = full_df.sort_values('start_date').groupby('striker')['batting_team'].last().reset_index()
    player_teams.columns = ['player', 'team']
    player_teams.to_csv(METADATA_FILE, index=False)
    
    # --- PART B: BATTING STATS ---
    print("🏏 Calculating Batting Stats...")
    
    # 1. Batting vs Team
    bat_vs_team = full_df.groupby(['striker', 'bowling_team']).agg(
        runs=('runs_off_bat', 'sum'),
        balls=('is_legal_ball', 'sum'),
        dismissals=('player_dismissed', 'count'), # Any dismissal counts for batting avg
        innings=('match_id', 'nunique')
    ).reset_index()
    bat_vs_team.rename(columns={'striker': 'player', 'bowling_team': 'opponent'}, inplace=True)
    bat_vs_team['role'] = 'batting'
    bat_vs_team['context'] = 'vs_team'

    # 2. Batting at Venue
    bat_at_venue = full_df.groupby(['striker', 'venue']).agg(
        runs=('runs_off_bat', 'sum'),
        balls=('is_legal_ball', 'sum'),
        dismissals=('player_dismissed', 'count'),
        innings=('match_id', 'nunique')
    ).reset_index()
    bat_at_venue.rename(columns={'striker': 'player', 'venue': 'opponent'}, inplace=True)
    bat_at_venue['role'] = 'batting'
    bat_at_venue['context'] = 'at_venue'

    # --- PART C: BOWLING STATS ---
    print("🥎 Calculating Bowling Stats...")
    
    # 1. Bowling vs Team (Not strictly necessary, but good to have)
    bowl_vs_team = full_df.groupby(['bowler', 'batting_team']).agg(
        runs=('total_runs', 'sum'),
        balls=('is_legal_ball', 'sum'),
        wickets=('is_bowler_wicket', 'sum'),
        innings=('match_id', 'nunique')
    ).reset_index()
    bowl_vs_team.rename(columns={'bowler': 'player', 'batting_team': 'opponent'}, inplace=True)
    bowl_vs_team['role'] = 'bowling'
    bowl_vs_team['context'] = 'vs_team' # Reusing 'context' column
    # For bowling, 'dismissals' column will hold 'wickets'
    bowl_vs_team.rename(columns={'wickets': 'dismissals'}, inplace=True)

    # 2. Bowling at Venue
    bowl_at_venue = full_df.groupby(['bowler', 'venue']).agg(
        runs=('total_runs', 'sum'),
        balls=('is_legal_ball', 'sum'),
        wickets=('is_bowler_wicket', 'sum'),
        innings=('match_id', 'nunique')
    ).reset_index()
    bowl_at_venue.rename(columns={'bowler': 'player', 'venue': 'opponent'}, inplace=True)
    bowl_at_venue['role'] = 'bowling'
    bowl_at_venue['context'] = 'at_venue'
    bowl_at_venue.rename(columns={'wickets': 'dismissals'}, inplace=True)

    # --- PART D: H2H (MATCHUPS) ---
    print("⚔️ Calculating H2H Matchups...")
    h2h = full_df.groupby(['striker', 'bowler']).agg(
        runs=('runs_off_bat', 'sum'),
        balls=('is_legal_ball', 'sum'),
        dismissals=('is_bowler_wicket', 'sum'),
        innings=('match_id', 'nunique')
    ).reset_index()
    h2h.rename(columns={'striker': 'player', 'bowler': 'opponent'}, inplace=True)
    h2h['role'] = 'h2h'
    h2h['context'] = 'h2h'
    h2h = h2h[h2h['balls'] > 5] # Only relevant matchups

    # --- MERGE & SAVE ---
    print("💾 Saving Master Player Database...")
    final_df = pd.concat([bat_vs_team, bat_at_venue, bowl_vs_team, bowl_at_venue, h2h], ignore_index=True)
    
    # Calculate Generic Stats
    # For Batting: Avg = Runs/Outs, SR = (Runs/Balls)*100
    # For Bowling: Avg = Runs/Wickets, Econ = (Runs/Balls)*6, SR = Balls/Wickets
    
    # To save space, we store raw numbers. We will calculate ratios (Avg/Econ) in the Engine on the fly.
    # This avoids messy NaNs/Infs in the CSV.
    
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ DONE! Stats saved to {OUTPUT_FILE}")
    print(f"✅ Metadata saved to {METADATA_FILE}")

if __name__ == "__main__":
    process_ball_by_ball()