import sys
import os
import json
import pandas as pd

# FORCE UTF-8 ENV (Must be before other imports might init streams)
os.environ["PYTHONIOENCODING"] = "utf-8"

# 1. SETUP PATHS
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.append(PROJECT_ROOT)

try:
    from engine import CricketAnalyzer
except ImportError:
    print("❌ Critical: Could not import CricketAnalyzer from engine.py")
    sys.exit(1)

# FORCE UTF-8
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

# 2. CONFIGURATION
FIXTURES_DIR = os.path.join(PROJECT_ROOT, "tests/odi/compare_squads/fixtures")
OUTPUT_FILE = os.path.join(FIXTURES_DIR, "compare_squads_expected_results.json")
YEARS_SCOPE = 50

# Matchups to Test (As requested by User)
MATCHUPS = [
    ("Australia", "Bangladesh"),
    ("England", "India"),
    ("New Zealand", "Pakistan"),
    ("South Africa", "Sri Lanka"),
    ("Bangladesh", "West Indies")
]
# We need a venue for context (picking neutral or home venues for stability)
# For simplicity in regression, we can use a generic venue or a known one.
# Let's use a venue that exists in the database to ensure we get venue stats.
TEST_VENUE = "Generic Stadium" # Or pick specific ones per matchup if needed.
# Better strategy: Pick a major venue for one of the teams to ensure "Venue Stats" populate.
MATCHUP_VENUES = {
    "Australia": "Melbourne Cricket Ground",
    "England": "Lord's, London",
    "New Zealand": "Eden Park, Auckland",
    "South Africa": "Wanderers Stadium, Johannesburg",
    "Bangladesh": "Sher-e-Bangla National Cricket Stadium, Mirpur"
}

def generate_golden_master():
    print("Initializing Engine for Squad Comparison Golden Master...")
    # Suppress output during init
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
    try:
        engine = CricketAnalyzer('data/FINAL_ODI_MASTER.csv')
    except Exception as e:
        sys.stdout = original_stdout
        print(f"Engine Init Failed: {e}")
        return
    finally:
        sys.stdout = original_stdout

    full_report = {}

    print(f"Processing {len(MATCHUPS)} Matchups (Scope: {YEARS_SCOPE} Years)...")

    for home, away in MATCHUPS:
        print(f"   {home} vs {away}...", end=" ")
        
        # A. Discover Last XIs
        home_xi = engine.get_last_match_xi(home)
        away_xi = engine.get_last_match_xi(away)
        
        if not home_xi or not away_xi:
            print(f"SKIPPING: Could not find XI for {home} or {away}")
            continue

        # B. Pick Venue (Host's home ground)
        venue = MATCHUP_VENUES.get(home, "Generic Stadium")
        
        # C. Generate Payload (The Refactored "Brain" Method)
        # We catch any print output from the engine to keep console clean
        sys.stdout = open(os.devnull, 'w', encoding='utf-8')
        try:
            payload = engine.player_engine._generate_comparison_payload(
                home, home_xi, away, away_xi, venue, years=YEARS_SCOPE
            )
        except Exception as e:
            sys.stdout = original_stdout
            print(f"Error: {e}")
            continue
        finally:
             sys.stdout = original_stdout
        
        # D. Store in Report
        key = f"{home}_vs_{away}"
        full_report[key] = {
            "Meta": {
                "HomeXI": home_xi,
                "AwayXI": away_xi,
                "Venue": venue,
                "Years": YEARS_SCOPE
            },
            "Payload": payload
        }
        print("Done.")

    # E. Save to JSON
    os.makedirs(FIXTURES_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(full_report, f, indent=4, default=str)

    print(f"\n💾 Golden Master Saved: {OUTPUT_FILE}")
    print(f"   Contains {len(full_report)} scenarios.")

if __name__ == "__main__":
    generate_golden_master()
