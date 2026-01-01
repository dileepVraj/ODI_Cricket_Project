import os
import pandas as pd
import glob

# --- CONFIGURATION ---
# PATH to where you will unzip the files if you need to run this again
SOURCE_FOLDER = 'data/temp_odi' 
# OUTPUT PATH (Updated to save inside data folder)
OUTPUT_FILE = 'data/FINAL_ODI_MASTER.csv'

print(f"🚀 STARTING SMART MERGE SYSTEM")

# Check if source exists
if not os.path.exists(SOURCE_FOLDER):
    print(f"❌ ERROR: Folder '{SOURCE_FOLDER}' not found.")
    print("   If you need to rebuild the data, Unzip 'raw_odi_backup.zip' into 'data/temp_odi' first.")
    exit()

print(f"📂 Reading from: {SOURCE_FOLDER}")

# 1. Get all the Clean Ball-by-Ball files
all_files = glob.glob(os.path.join(SOURCE_FOLDER, "*.csv"))
ball_files = [f for f in all_files if "_info" not in f]

print(f"📊 Found {len(ball_files)} matches to process.")

master_data = []
count = 0

# 2. Loop through every match
for ball_file_path in ball_files:
    try:
        # A. Derive Info Filename
        info_file_path = ball_file_path.replace(".csv", "_info.csv")
        
        # B. Extract WINNER or OUTCOME
        winner = "No Result" # Default
        
        if os.path.exists(info_file_path):
            with open(info_file_path, 'r') as f:
                for line in f:
                    # Case 1: Normal Winner
                    if line.startswith("info,winner,"):
                        parts = line.strip().split(',')
                        if len(parts) >= 3:
                            winner = parts[2]
                            break 
                    
                    # Case 2: Tie or No Result
                    elif line.startswith("info,outcome,"):
                        parts = line.strip().split(',')
                        if len(parts) >= 3:
                            outcome = parts[2]
                            if outcome == "tie":
                                winner = "tie"
                            elif outcome == "no result":
                                winner = "No Result"
                            break
        
        # C. Read Data
        df = pd.read_csv(ball_file_path)
        
        # D. Stamp Winner
        df['winner'] = winner
        
        master_data.append(df)
        
        count += 1
        if count % 100 == 0:
            print(f"   ⚡ Stitched {count} matches...", end='\r')

    except Exception as e:
        print(f"   ⚠️ Error on {ball_file_path}: {e}")

# 3. Save
if master_data:
    print(f"\n✅ Combining all data... (This uses RAM)")
    final_df = pd.concat(master_data, ignore_index=True)
    
    print(f"💾 Saving to {OUTPUT_FILE}...")
    final_df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"🎉 SUCCESS! File Created.")
    print(f"   Total Rows: {len(final_df)}")
    print(f"   Columns: {list(final_df.columns)}")
else:
    print("❌ FAILED. No data found.")