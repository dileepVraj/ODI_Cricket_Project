
import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.getcwd())

from core.player_engine import get_player_engine
from core.interfaces.player_interface import IPlayerEngine, PlayerProfile


class MockDAL:
    """Minimal DAL stub aligned with the strict split batting/bowling schema."""

    def __init__(self, balls_df: pd.DataFrame):
        self._balls_df = balls_df.copy()

    def get_latest_match_date(self):
        if self._balls_df.empty or "start_date" not in self._balls_df.columns:
            return None
        dates = pd.to_datetime(self._balls_df["start_date"], errors="coerce")
        return dates.max()

    def get_balls(self, **kwargs) -> pd.DataFrame:
        df = self._balls_df.copy()
        striker = kwargs.get("striker")
        bowler = kwargs.get("bowler")
        players = kwargs.get("players")
        venue_id = kwargs.get("venue_id")

        if striker:
            df = df[df["striker"] == striker].copy()
        if bowler:
            df = df[df["bowler"] == bowler].copy()
        if players:
            df = df[df["striker"].isin(players) | df["bowler"].isin(players)].copy()
        if venue_id and "venue_id" in df.columns:
            df = df[df["venue_id"] == venue_id].copy()
        return df


def test_headless_api():
    print("Testing Headless Player API...")
    
    # 1. Mock split-role player stats (new schema: role/context aggregates)
    player_data = [
        {"player": "Kohli", "role": "batting", "context": "vs_team", "runs": 110, "innings": 2, "dismissals": 0, "balls": 110, "opponent": "Australia"},
        {"player": "Kohli", "role": "batting", "context": "at_venue", "runs": 50, "innings": 1, "dismissals": 0, "balls": 50, "opponent": "MCG"},
        {"player": "Kohli", "role": "bowling", "context": "vs_team", "runs": 120, "innings": 20, "dismissals": 8, "balls": 600, "opponent": "Australia"},
    ]
    player_df = pd.DataFrame(player_data)
    
    meta_df = pd.DataFrame()  # Not needed for this test

    # 2. Mock ball-by-ball DAL input used for batting milestones in get_player_profile
    balls_df = pd.DataFrame(
        {
            "match_id": ["1", "2", "3", "3"],
            "start_date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-03"],
            "striker": ["Kohli", "Kohli", "Smith", "Kohli"],
            "bowler": ["Starc", "Cummins", "Shami", "Shami"],
            "batting_team": ["India", "India", "Australia", "India"],
            "bowling_team": ["Australia", "Australia", "India", "India"],
            "player_dismissed": [None, None, "Smith", None],
            "wicket_type": [None, None, "caught", None],
            "runs_off_bat": [50, 60, 10, 5],
            "wides": [0, 0, 0, 0],
            "noballs": [0, 0, 0, 0],
            "extras": [0, 0, 0, 0],
            "venue_id": ["MCG", "MCG", "SCG", "MCG"],
        }
    )
    dal = MockDAL(balls_df)
    
    # 3. Initialize via strict strategy factory
    PlayerEngine = get_player_engine("odi")
    engine = PlayerEngine(player_df=player_df, meta_df=meta_df, dal=dal)
    assert isinstance(engine, IPlayerEngine)
    
    print("   > Engine Attributes:")
    for attr in dir(engine):
        if "get_player" in attr:
            print(f"     - {attr}")
    
    # 4. Test contract method
    print("   > Calling analyze_player_profile('Kohli')...")
    profile = engine.analyze_player_profile("Kohli", opposition="Australia", venue_id="MCG", years=5)
    
    # 5. Assertions
    if not isinstance(profile, PlayerProfile):
        print("FAILED: Return type is not PlayerProfile")
        sys.exit(1)
        
    print(f"   > Check Name: {profile.name}")
    assert profile.name == "Kohli"
    
    print(f"   > Check Batting Runs: {profile.batting.runs}")
    assert profile.batting.runs == 110
    assert profile.batting.innings == 2
    assert profile.batting.highest_score == 60
    assert profile.batting.fifties == 2
    
    print(f"   > Check Opp Context: {profile.vs_opponent_stats is not None}")
    assert profile.vs_opponent_stats is not None
    assert profile.vs_opponent_stats.batting.runs == 110  # Only Australia in mock
    
    print(f"   > Check Venue Context: {profile.venue_stats is not None}")
    assert profile.venue_stats is not None
    assert profile.venue_stats.batting.runs == 50
    assert profile.bowling is not None
    assert profile.bowling.wickets == 8
    
    print("Headless API Verified Successfully!")

if __name__ == "__main__":
    try:
        test_headless_api()
    except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
        print(f"EXECUTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
