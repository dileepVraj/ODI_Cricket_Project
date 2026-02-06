
import pandas as pd
import os

DATA_FILE = 'data/FINAL_ODI_MASTER.csv'

if os.path.exists(DATA_FILE):
    print(f"🔧 Fixing TEAM headers in {DATA_FILE}...")
    df = pd.read_csv(DATA_FILE)
    
    renames = {}
    if 'batting_team' in df.columns and 'team_bat_1' not in df.columns:
        renames['batting_team'] = 'team_bat_1'
    
    if 'bowling_team' in df.columns and 'team_bat_2' not in df.columns:
        renames['bowling_team'] = 'team_bat_2'
        
    if renames:
        df = df.rename(columns=renames)
        df.to_csv(DATA_FILE, index=False)
        print(f"✅ Renamed: {renames}")
    else:
        print("✅ Team Headers already standard.")
else:
    print("❌ File not found.")
