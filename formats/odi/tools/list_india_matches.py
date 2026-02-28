import sys
import os
import io
import numpy as np
import pandas as pd

# Force UTF-8 stdout
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root
sys.path.append(os.getcwd())

try:
    from engine import CricketAnalyzer
except ImportError:
    # Add parent dir if needed
    sys.path.append(os.path.dirname(os.getcwd()))
    from engine import CricketAnalyzer

try:
    # Initialize Engine (suppress logs)
    devnull = open(os.devnull, 'w')
    old_stdout = sys.stdout
    sys.stdout = devnull
    
    engine = CricketAnalyzer('formats/odi/data/FINAL_ODI_MASTER.csv')
    
    sys.stdout = old_stdout
    devnull.close()
    
    df = engine.match_df
    # Filter India and compute printable columns using vectorized transforms.
    india = (
        df[(df['team_bat_1'] == 'India') | (df['team_bat_2'] == 'India')]
        .sort_values('start_date', ascending=False)
        .head(6)
        .copy()
    )
    india['Date'] = pd.to_datetime(india['start_date'], errors='coerce').dt.strftime('%Y-%m-%d').fillna('-')
    india['Opponent'] = np.where(india['team_bat_1'] == 'India', india['team_bat_2'], india['team_bat_1'])
    india['Result'] = np.where(
        india['winner'] == 'India',
        'Won',
        np.where(india['winner'] == india['Opponent'], 'Lost', india['winner'].astype(str)),
    )
    india['Venue'] = (
        india['venue']
        .astype(str)
        .str.replace('IND_', '', regex=False)
        .str.replace('AUS_', '', regex=False)
        .str.title()
    )
    
    print(f"{'Date':<12} | {'Venue':<25} | {'Opponent':<15} | {'Result':<10}")
    print("-" * 70)
    display_df = india[['Date', 'Venue', 'Opponent', 'Result']].fillna('-')
    print(display_df.to_string(index=False))

except (AttributeError, KeyError, TypeError, ValueError, OSError, ImportError) as e:
    sys.stdout = sys.__stdout__
    print(f"ERROR: {e}")
