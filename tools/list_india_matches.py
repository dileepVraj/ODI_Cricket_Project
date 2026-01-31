import sys
import os
import io

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
    
    engine = CricketAnalyzer('data/FINAL_ODI_MASTER.csv')
    
    sys.stdout = old_stdout
    devnull.close()
    
    df = engine.match_df
    # Filter India
    india = df[(df['team_bat_1']=='India') | (df['team_bat_2']=='India')].sort_values('start_date', ascending=False).head(6)
    
    print(f"{'Date':<12} | {'Venue':<25} | {'Opponent':<15} | {'Result':<10}")
    print("-" * 70)
    
    for _, row in india.iterrows():
        try:
            d = row['start_date'].strftime('%Y-%m-%d')
            opp = row['team_bat_2'] if row['team_bat_1'] == 'India' else row['team_bat_1']
            
            if row['winner'] == 'India':
                res = "Won"
            elif row['winner'] == opp:
                res = "Lost"
            else:
                res = str(row['winner'])
                
            # Clean Venue Name
            ven = str(row['venue']).replace('IND_', '').replace('AUS_', '').title()
            
            # Safe Print
            print(f"{d:<12} | {ven:<25} | {opp:<15} | {res:<10}")
        except Exception as row_e:
            print(f"Error printing row: {row_e}")

except Exception as e:
    sys.stdout = sys.__stdout__
    print(f"ERROR: {e}")
