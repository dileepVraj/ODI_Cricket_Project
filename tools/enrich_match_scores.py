
import pandas as pd
import os

MASTER_FILE = 'data/FINAL_ODI_MASTER.csv'

def enrich_scores():
    if not os.path.exists(MASTER_FILE):
        print("❌ Master file not found.")
        return

    print("🚀 Enriching Master CSV with Innings Scores...")
    df = pd.read_csv(MASTER_FILE)
    
    # Check if headers need fixing first (just in case)
    if 'ball_inn1' in df.columns and 'balls_inn1' not in df.columns:
        df = df.rename(columns={'ball_inn1': 'balls_inn1', 'ball_inn2': 'balls_inn2'})

    # Group by Match ID and Innings to sum runs
    # Total Runs = runs_off_bat + extras
    df['total_runs'] = df['runs_off_bat'] + df['extras']
    
    # 1. Aggregation
    agg_df = df.groupby(['match_id', 'innings'])['total_runs'].sum().reset_index()
    
    # 2. Pivot to get score_inn1 and score_inn2 columns per match
    scores = agg_df.pivot(index='match_id', columns='innings', values='total_runs').reset_index()
    
    # Rename columns 1 -> score_inn1, 2 -> score_inn2
    scores.rename(columns={1: 'score_inn1', 2: 'score_inn2'}, inplace=True)
    
    # Fill NaN with 0 (e.g., if match abandoned before inn2)
    scores['score_inn1'] = scores['score_inn1'].fillna(0).astype(int)
    scores['score_inn2'] = scores['score_inn2'].fillna(0).astype(int)
    
    print(f"✅ Calculated scores for {len(scores)} matches.")
    
    # 3. Merge back to Master
    # We want these columns on EVERY row of the match for easy filtering in Engine
    # Note: Merging 230k rows might take a sec but is efficient in pandas.
    
    # Drop existing if re-running
    if 'score_inn1' in df.columns: df.drop(columns=['score_inn1'], inplace=True)
    if 'score_inn2' in df.columns: df.drop(columns=['score_inn2'], inplace=True)
    
    merged_df = pd.merge(df, scores, on='match_id', how='left')
    
    # Save
    merged_df.to_csv(MASTER_FILE, index=False)
    print(f"💾 Saved enriched data to {MASTER_FILE}")

if __name__ == "__main__":
    enrich_scores()
