
import pandas as pd
import os

DATA_FILE = 'data/FINAL_ODI_MASTER.csv'

if os.path.exists(DATA_FILE):
    print(f"🔧 Fixing headers in {DATA_FILE}...")
    df = pd.read_csv(DATA_FILE)
    
    renames = {}
    if 'ball_inn1' in df.columns: renames['ball_inn1'] = 'balls_inn1'
    if 'ball_inn2' in df.columns: renames['ball_inn2'] = 'balls_inn2'
    
    if renames:
        df = df.rename(columns=renames)
        df.to_csv(DATA_FILE, index=False)
        print(f"✅ Renamed: {renames}")
    else:
        print("✅ Headers already correct.")
else:
    print("❌ File not found.")
