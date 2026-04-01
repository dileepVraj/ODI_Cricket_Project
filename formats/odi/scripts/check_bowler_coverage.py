import pandas as pd
import sys
import os

def analyze():
    df_path = 'formats/odi/data/FINAL_ODI_MASTER.csv'
    if not os.path.exists(df_path):
        print(f"Error: {df_path} not found")
        return

    df = pd.read_csv(df_path, usecols=['bowler', 'start_date'])
    unique_bowlers = df['bowler'].unique()
    cutoff = '2014-01-01'
    recent_df = df[df['start_date'] >= cutoff]
    recent_bowlers = recent_df['bowler'].unique()
    
    sys.path.append('.')
    from formats.odi.config.players import BOWLER_STYLES
    config_bowlers = set(BOWLER_STYLES.keys())
    
    missing_all = len([b for b in unique_bowlers if b not in config_bowlers])
    missing_recent = len([b for b in recent_bowlers if b not in config_bowlers])

    print("\nFINAL SUMMARY")
    print("-------------")
    print(f"All-Time Unique Bowlers: {len(unique_bowlers)}")
    print(f"Bowlers in Configuration: {len(config_bowlers)}")
    print(f"Missing (All-Time): {missing_all} ({missing_all/len(unique_bowlers):.1%})")
    print(f"Missing (Post-2014): {missing_recent} ({missing_recent/len(recent_bowlers):.1%})")

if __name__ == "__main__":
    analyze()
