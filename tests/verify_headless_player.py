
import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from core.player_engine import PlayerEngine
from core.interfaces.player_interface import PlayerProfile, BattingStats, ContextStats
from formats.odi.renderers.player_renderer import PlayerHTMLRenderer

def test_headless_api():
    print("Testing Headless Player API...")
    
    # 1. Mock Data
    raw_data = {
        'match_id': ['1', '2', '3'],
        'start_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'striker': ['Kohli', 'Kohli', 'Smith'],
        'bowler': ['Bumrah', 'Starc', 'Bumrah'],
        'runs_off_bat': [50, 60, 10], 
        'innings': [1, 2, 1],
        'venue': ['MCG', 'SCG', 'MCG'],
        'batting_team': ['India', 'India', 'Australia'],
        'bowling_team': ['Australia', 'Australia', 'India'],
        'role': ['batting', 'batting', 'batting'],
        'player_dismissed': [None, None, 'Smith'], # Kohli Not out twice
        'wicket_type': [None, None, 'bowled'],
        'balls': [50, 60, 10], # Dummy
        'runs': [50, 60, 10], # Dummy
        'dismissals': [0, 0, 1]
    }
    raw_df = pd.DataFrame(raw_data)
    
    player_data = [
        {'player': 'Kohli', 'role': 'batting', 'context': 'vs_team', 'runs': 110, 'innings': 2, 'dismissals': 0, 'balls': 110, 'opponent': 'Australia'},
        {'player': 'Kohli', 'role': 'batting', 'context': 'at_venue', 'runs': 50, 'innings': 1, 'dismissals': 0, 'balls': 50, 'opponent': 'MCG'}, # Venue logic uses opponent col
    ]
    player_df = pd.DataFrame(player_data)
    
    meta_df = pd.DataFrame() # Not used for this test
    
    # 2. Initialize Engine
    engine = PlayerEngine(raw_df=raw_df, player_df=player_df, meta_df=meta_df)
    
    print("   > Engine Attributes:")
    for attr in dir(engine):
        if "get_player" in attr:
            print(f"     - {attr}")
    
    # 3. Test get_player_profile
    print("   > Calling get_player_profile('Kohli')...")
    profile = engine.get_player_profile("Kohli", opposition="Australia", venue_id="MCG", years=5)
    
    # 4. Assertions
    if not isinstance(profile, PlayerProfile):
        print("FAILED: Return type is not PlayerProfile")
        sys.exit(1)
        
    print(f"   > Check Name: {profile.name}")
    assert profile.name == "Kohli"
    
    print(f"   > Check Batting Runs: {profile.batting.runs}")
    assert profile.batting.runs == 110
    
    print(f"   > Check Opp Context: {profile.vs_opponent_stats is not None}")
    assert profile.vs_opponent_stats is not None
    assert profile.vs_opponent_stats.batting.runs == 110 # Only Played Aus in mock
    
    print(f"   > Check Venue Context: {profile.venue_stats is not None}")
    assert profile.venue_stats is not None
    # Venue stats come from p_stats logic, check generic return
    
    # 5. Test Renderer
    print("   > Testing Renderer...")
    html = PlayerHTMLRenderer.render_profile_card(profile, 5)
    mini_html = PlayerHTMLRenderer.render_mini_card("Test", profile.vs_opponent_stats.batting, None, "Test")
    
    if "kohli" in html.lower() and "110" in html:
        print("Headless API Verified Successfully!")
    else:
        print(f"Renderer output missing key data. Found: {html[:200]}...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        test_headless_api()
    except Exception as e:
        print(f"EXECUTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
