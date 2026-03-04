"""Full regression test of ALL 17 ODI functions."""
import requests
from config.settings import API_BASE_URL, API_V1_PREFIX

BASE = API_BASE_URL

tests = [
    # ── Venue Intelligence (no squad needed) ──
    ("venue_bias", {"venue": "wankhede_mumbai"}),
    ("venue_matchup", {"venue": "wankhede_mumbai", "team_a": "India", "team_b": "Australia"}),
    ("home_fortress", {"venue": "wankhede_mumbai", "team_a": "India"}),
    ("venue_phases", {"venue": "wankhede_mumbai", "team_a": "India", "team_b": "Australia"}),
    # ── Rivalry Lab ──
    ("global_h2h", {"team_a": "India", "team_b": "Australia"}),
    ("country_h2h", {"team_a": "India", "team_b": "Australia", "region": "India"}),
    ("continent_perf", {"team_a": "India", "region": "Asia"}),
    # ── Team Command ──
    ("home_dominance", {"team_a": "India"}),
    ("away_performance", {"team_b": "India"}),
    ("global_performance", {"team_a": "India"}),
    ("team_form", {"team_a": "India", "years": 3}),
    # ── Squad-dependent ──
    ("compare_squads", {
        "venue": "IND_MUMBAI_WANKHEDE", "team_a": "India", "team_b": "Australia",
        "home_xi": ["V Kohli", "RG Sharma", "S Dhawan"],
        "away_xi": ["DA Warner", "AJ Finch", "SPD Smith"],
    }),
    ("tactical_matrix", {
        "team_a": "India", "team_b": "Australia",
        "home_xi": ["V Kohli", "RG Sharma", "S Dhawan"],
        "away_xi": ["PJ Cummins", "MA Starc", "A Zampa"],
    }),
    ("matchups", {
        "player_name": "V Kohli",
        "away_xi": ["MA Starc", "PJ Cummins", "A Zampa"],
    }),
    ("predict_score", {
        "venue": "IND_MUMBAI_WANKHEDE", "team_a": "India", "team_b": "Australia",
        "years": 5,
        "home_xi": ["V Kohli", "RG Sharma", "S Dhawan"],
        "away_xi": ["PJ Cummins", "MA Starc", "A Zampa"],
    }),
    ("player_profile", {"team_b": "Australia", "player_name": "V Kohli"}),
    ("generate_pack", {
        "venue": "IND_MUMBAI_WANKHEDE", "team_a": "India", "team_b": "Australia",
        "home_xi": ["V Kohli", "RG Sharma"],
        "away_xi": ["DA Warner", "AJ Finch"],
        "match_time": "2023-01-01",
        "toss_result": "India won toss and chose to bat",
        "pitch_report": "Good batting track"
    }),
]

results = []
pass_count = 0
fail_count = 0
for fn, params in tests:
    try:
        r = requests.post(f"{BASE}{API_V1_PREFIX}/odi/execute/{fn}", json={"params": params}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            has_data = bool(data.get("data"))
            results.append(f"  OK  {fn}")
            pass_count += 1
        else:
            err = r.json().get("detail", "?")[:80]
            results.append(f"  FAIL  {fn}: {err}")
            fail_count += 1
    except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
        results.append(f"  ERR  {fn}: {str(e)[:60]}")
        fail_count += 1

results.append(f"\n=== {pass_count}/{pass_count+fail_count} PASSED ===")
output = "\n".join(results)
with open("scripts/full_results.txt", "w") as f:
    f.write(output)
print(output)
