"""Quick test of squad-dependent functions via the API."""
import requests
from config.settings import API_BASE_URL, API_LEGACY_PREFIX

BASE = API_BASE_URL

tests = [
    ("compare_squads", {
        "venue": "wankhede_mumbai", "team_a": "India", "team_b": "Australia",
        "home_xi": ["V Kohli", "RG Sharma", "S Dhawan"],
        "away_xi": ["DA Warner", "AJ Finch", "SPD Smith"],
    }),
    ("tactical_matrix", {
        "team_a": "India", "team_b": "Australia",
        "home_xi": ["V Kohli", "RG Sharma", "S Dhawan"],
        "away_xi": ["PJ Cummins", "MA Starc", "A Zampa"],
    }),
    ("matchups", {
        "team_a": "India", "team_b": "Australia",
        "player_name": "V Kohli",
        "away_xi": ["MA Starc", "PJ Cummins", "A Zampa"],
    }),
    # TEST DISABLED -- predict_score() removed pending Phase 12 rebuild
    # Re-enable and rewrite this test when predict_score() is rebuilt
    # See formats/odi/predictor.py for rebuild requirements
    # ("predict_score", {
    #     "venue": "wankhede_mumbai", "team_a": "India", "team_b": "Australia",
    #     "years": 5,
    #     "home_xi": ["V Kohli", "RG Sharma", "S Dhawan"],
    #     "away_xi": ["PJ Cummins", "MA Starc", "A Zampa"],
    # }),
    ("player_profile", {
        "team_b": "Australia", "player_name": "V Kohli",
    }),
    ("generate_pack", {
        "venue": "wankhede_mumbai", "team_a": "India", "team_b": "Australia",
        "home_xi": ["V Kohli", "RG Sharma"],
        "away_xi": ["DA Warner", "AJ Finch"],
    }),
]

results = []
for fn, params in tests:
    try:
        r = requests.post(f"{BASE}{API_LEGACY_PREFIX}/odi/execute/{fn}", json={"params": params}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            has_data = bool(data.get("data"))
            results.append(f"OK  {fn} (has_data={has_data})")
        else:
            err = r.json().get("detail", "?")
            results.append(f"FAIL-{r.status_code}  {fn}\n   ERR: {err}")
    except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
        results.append(f"ERR  {fn}: {e}")

output = "\n".join(results)
with open("scripts/squad_results.txt", "w") as f:
    f.write(output)
print("Results written to scripts/squad_results.txt")
