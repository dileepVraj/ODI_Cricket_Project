import pandas as pd
import sys
import json
import os

# Add project root to path
sys.path.append(os.getcwd())
from formats.odi.config.players import BOWLER_STYLES, PLAYER_ROLES

def find_missing():
    # Load dataset
    df = pd.read_csv('formats/odi/data/FINAL_ODI_MASTER.csv')
    df['start_date'] = pd.to_datetime(df['start_date'])
    
    # Filter for last 10 years
    cutoff = pd.Timestamp.now().floor('D') - pd.DateOffset(years=10)
    recent = df[df['start_date'] >= cutoff]
    
    major_teams = [
        'India', 'Australia', 'England', 'South Africa', 'New Zealand', 
        'Pakistan', 'Sri Lanka', 'West Indies', 'Bangladesh', 'Afghanistan',
        'Zimbabwe', 'Ireland', 'Netherlands'
    ]
    
    report = {}
    
    for team in major_teams:
        # Bowlers for this team
        team_bowlers = recent[recent['team_bat_2'] == team]['bowler'].unique()
        # All players for this team (batters and bowlers)
        team_batters = recent[recent['team_bat_1'] == team]['striker'].unique()
        team_players = set(team_bowlers) | set(team_batters)
        
        missing_bowlers = [b for b in team_bowlers if b not in BOWLER_STYLES]
        missing_players = [p for p in team_players if p not in PLAYER_ROLES]
        
        report[team] = {
            'missing_bowlers': sorted(missing_bowlers),
            'missing_players': sorted(missing_players)
        }
        
    with open('missing_players_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    print("Report generated: missing_players_report.json")

if __name__ == "__main__":
    find_missing()
