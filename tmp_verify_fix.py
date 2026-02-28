
import sys
import os
import pandas as pd
from typing import Dict, Any

# Add project root to path
sys.path.append(os.getcwd())

from core.player_engine import get_player_engine
from formats.odi.manifest import FORMAT_RULES

def test_squad_comparison_payload():
    print("Verifying Squad Comparison Payload type contract...")
    
    # 1. Mock minimal data
    player_df = pd.DataFrame(columns=['player', 'role', 'context', 'runs', 'innings', 'dismissals', 'balls', 'opponent'])
    meta_df = pd.DataFrame(columns=['player', 'team'])
    
    # 2. Get engine via factory
    PlayerEngine = get_player_engine("odi")
    engine = PlayerEngine(player_df=player_df, meta_df=meta_df, format_rules=FORMAT_RULES)
    
    # 3. Test _generate_comparison_payload (Violation #15 target)
    print("   > Calling _generate_comparison_payload...")
    # This might return empty structure but shouldn't crash
    try:
        payload = engine._generate_comparison_payload(
            team_a_name="India",
            team_a_players=["Kohli"],
            team_b_name="Australia",
            team_b_players=["Starc"],
            venue_id="MCG",
            context_df=pd.DataFrame(columns=['match_id', 'striker', 'bowler', 'runs_off_bat', 'player_dismissed', 'start_date'])
        )
        print("   > Payload structure type: " + str(type(payload)))
        assert isinstance(payload, dict)
        print("   > SQUAD COMPARISON TEST: PASS")
    except Exception as e:
        print(f"   > SQUAD COMPARISON TEST: FAIL - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_squad_comparison_payload()
