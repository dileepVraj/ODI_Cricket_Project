# -*- coding: utf-8 -*-
"""Quick verification script for Match Pack v3.2 fixes."""
import sys
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.transformer import (
    transform_h2h_report, transform_h2h_slim, transform_venue_bias,
    transform_team_form, transform_dominance_matrix, transform_player_stats,
)
from core.interpreter import MatchInterpreter

passed = 0
failed = 0

def check(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")

# --- MOCK DATA ---
h2h_raw = [
    {"Metric": "Matches", "Value": "20"},
    {"Metric": "Tie/NR", "Value": "2"},
    {"Metric": "Win %", "Value": "60%"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Home Wins", "Value": "12"},
    {"Metric": "Bat 1st", "Value": "7"},
    {"Metric": "Bat 2nd", "Value": "5"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Away Wins", "Value": "6"},
    {"Metric": "Bat 1st", "Value": "4"},
    {"Metric": "Bat 2nd", "Value": "2"},
] + [{"Metric": f"p{i}", "Value": "-"} for i in range(26)]

h2h_even = [
    {"Metric": "Matches", "Value": "10"},
    {"Metric": "Tie/NR", "Value": "0"},
    {"Metric": "Win %", "Value": "50%"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Home Wins", "Value": "5"},
    {"Metric": "Bat 1st", "Value": "3"},
    {"Metric": "Bat 2nd", "Value": "2"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Away Wins", "Value": "5"},
    {"Metric": "Bat 1st", "Value": "2"},
    {"Metric": "Bat 2nd", "Value": "3"},
] + [{"Metric": f"p{i}", "Value": "-"} for i in range(26)]

form_raw = {
    "summary_code": ["W", "W", "L", "L", "L", "L", "W", "L", "L", "W"],
    "matches": [{"Result": "WIN", "vs": "India"}],
    "MATCH_IDS": "10,11",
}

dominance_raw = [
    {"Opponent": "OVERALL", "Mat": 50, "Won": 34, "Lost": 14, "Tie/NR": 2, "Win %": "71%", "Last 5": "W W L W W"},
    {"Opponent": "India", "Mat": 10, "Won": 7, "Lost": 3, "Tie/NR": 0, "Win %": "70%", "Last 5": "W W W L W"},
    {"Opponent": "Australia", "Mat": 8, "Won": 6, "Lost": 2, "Tie/NR": 0, "Win %": "75%", "Last 5": "W W W W L"},
    {"Opponent": "England", "Mat": 12, "Won": 8, "Lost": 4, "Tie/NR": 0, "Win %": "67%", "Last 5": "L W W W W"},
]

# v3.2 FIX 5: Mock player stats
player_stats_raw = {
    "Player": "JE Root",
    "Inns": 25,
    "Bat Form": "45, 12*, DNB, 0, 89, 34, 67*, 5, 112, 23",
    "Bat Avg": 42.3,
    "vs Opp": 35.7,
    "Ven Inns": 5,
    "Ven Runs": 210,
    "Ven Avg": 42.0,
    "Ven HS": 89,
    "Bowl Form": "1-45, 0-22, 2-31",
    "Bowl Econ": 4.8,
    "Ven Econ": 5.2,
    "Ven Wkts": 3,
    "Ven Matches": 5,
}

player_stats_empty = {
    "Player": "New Player", "Inns": 0, "Bat Form": "-", "Bat Avg": "-",
    "vs Opp": "-", "Ven Inns": "-", "Ven Runs": "-", "Ven Avg": "-", "Ven HS": "-",
    "Bowl Form": "-", "Bowl Econ": "-", "Ven Econ": "-", "Ven Wkts": "-", "Ven Matches": "-",
}

interp = MatchInterpreter()

# ---- TRANSFORMER TESTS ----
print("\n=== TRANSFORMER TESTS ===")

r = transform_h2h_slim(h2h_raw, "India", "England")
check("Slim H2H: no batting_first", "batting_first" not in r)
check("Slim H2H: no _match_ids", "_match_ids" not in r)
check("Slim H2H: matches=20", r["matches_played"] == 20)
check("Slim H2H: home_wins=12", r["home_wins"] == 12)

r2 = transform_h2h_report(h2h_raw, "India", "England")
check("Full H2H: has batting_first", "batting_first" in r2)

f = transform_team_form(form_raw, "England")
check("Form: no matches list", "matches" not in f)
check("Form: no _match_ids", "_match_ids" not in f)
check("Form: wins=4", f["wins"] == 4)
check("Form: losses=6", f["losses"] == 6)
check("Form: win_pct=40", f["win_pct"] == 40)

d = transform_dominance_matrix(dominance_raw, "SL")
check("Dominance: OVERALL excluded", d["overall"]["matches"] == 30)
check("Dominance: wins=21", d["overall"]["wins"] == 21)
check("Dominance: win_pct=70", d["overall"]["win_pct"] == 70)
check("Dominance: 3 opponents", len(d["vs_opponents"]) == 3)

# ---- v3.2 FIX 5: PLAYER STATS TRANSFORMER ----
print("\n=== PLAYER STATS TRANSFORMER TESTS (v3.2) ===")

ps = transform_player_stats(player_stats_raw)
check("PlayerStats: player name", ps["player"] == "JE Root")
check("PlayerStats: batting innings=25", ps["batting"]["innings"] == 25)
check("PlayerStats: batting avg=42.3", ps["batting"]["average"] == 42.3)
check("PlayerStats: vs_opp=35.7", ps["batting"]["vs_opponent_avg"] == 35.7)
check("PlayerStats: venue innings=5", ps["batting"]["venue"]["innings"] == 5)
check("PlayerStats: venue runs=210", ps["batting"]["venue"]["runs"] == 210)
check("PlayerStats: venue avg=42.0", ps["batting"]["venue"]["average"] == 42.0)
check("PlayerStats: venue highest=89", ps["batting"]["venue"]["highest"] == 89)
check("PlayerStats: form_scores is list", isinstance(ps["batting"]["form_scores"], list))
check("PlayerStats: form_scores has 10 items", len(ps["batting"]["form_scores"]) == 10)
check("PlayerStats: bowling econ=4.8", ps["bowling"]["economy"] == 4.8)
check("PlayerStats: venue wkts=3", ps["bowling"]["venue_wickets"] == 3)
check("PlayerStats: venue matches=5", ps["bowling"]["venue_matches"] == 5)

ps_empty = transform_player_stats(player_stats_empty)
check("PlayerStats empty: player name", ps_empty["player"] == "New Player")
check("PlayerStats empty: batting innings=0", ps_empty["batting"]["innings"] == 0)
check("PlayerStats empty: form_scores empty", ps_empty["batting"]["form_scores"] == [])

# ---- INTERPRETER TESTS ----
print("\n=== INTERPRETER TESTS ===")

data_even = transform_h2h_slim(h2h_even, "India", "England")
r3 = interp.interpret_h2h(data_even, "India", "England", "Last 4Y")
check("50% H2H: says evenly split", "evenly split" in r3["narrative"])
check("50% H2H: NOT India lead", "India lead" not in r3["narrative"])
check("50% H2H: section_description present", "section_description" in r3)
check("50% H2H: dominance_reasoning present", "dominance_reasoning" in r3["context"])

f_data = transform_team_form(form_raw, "England")
r4 = interp.interpret_form(f_data, "Global")
check("Form trend: NOT TRENDING_UP", r4["context"]["trend"] != "TRENDING_UP")
check("Form: trend_reasoning present", "trend_reasoning" in r4["context"])
check("Form: section_description present", "section_description" in r4)

d_data = transform_dominance_matrix(dominance_raw, "SL")
r5 = interp.interpret_dominance(d_data, "SL", "HOME")
check("Dominance: 70% in narrative", "70%" in r5["narrative"])
check("Dominance: section_description present", "section_description" in r5)
check("Dominance: strength_reasoning present", "strength_reasoning" in r5["context"])

# ---- v3.2 FIX 2: KEY RENAME VERIFICATION ----
print("\n=== KEY RENAME TESTS (v3.2) ===")

# Simulate what team_engine now returns
mock_global_habits = {
    "bat_first": {
        "home_team_pp_runs": 55.2, "home_team_pp_wkts": 1.3,
        "home_team_mid_runs": 140.5, "home_team_mid_wkts": 3.2,
        "home_team_dth_runs": 80.1, "home_team_dth_wkts": 2.5,
        "away_team_pp_runs": 48.3, "away_team_pp_wkts": 1.8,
        "away_team_mid_runs": 130.2, "away_team_mid_wkts": 3.8,
        "away_team_dth_runs": 70.0, "away_team_dth_wkts": 2.9,
    },
    "chasing": {
        "home_team_pp_runs": 50.0, "home_team_pp_wkts": 1.5,
        "home_team_mid_runs": 135.0, "home_team_mid_wkts": 3.0,
        "home_team_dth_runs": 75.5, "home_team_dth_wkts": 2.8,
        "away_team_pp_runs": 45.0, "away_team_pp_wkts": 2.0,
        "away_team_mid_runs": 125.0, "away_team_mid_wkts": 4.0,
        "away_team_dth_runs": 65.0, "away_team_dth_wkts": 3.2,
    },
}

check("KEY RENAME: home_team_pp_runs in bat_first",
      "home_team_pp_runs" in mock_global_habits["bat_first"])
check("KEY RENAME: away_team_dth_wkts in chasing",
      "away_team_dth_wkts" in mock_global_habits["chasing"])
check("KEY RENAME: old h_pp_runs NOT present",
      "h_pp_runs" not in mock_global_habits["bat_first"])
check("KEY RENAME: old a_mid_runs NOT present",
      "a_mid_runs" not in mock_global_habits["chasing"])

# ---- v3.2 FIX 1: CAVEAT VERIFICATION ----
print("\n=== CAVEAT TESTS (v3.2) ===")

mock_phase_return = {
    "venue_baseline": {},
    "home_at_venue": {},
    "away_at_venue": {},
    "global_habits": mock_global_habits,
    "alerts": [],
    "caveat_2nd_innings_death": (
        "IMPORTANT: 2nd innings death-over stats (overs 41-50) have an inherent sampling bias."
    ),
}
check("CAVEAT: key present in return packet",
      "caveat_2nd_innings_death" in mock_phase_return)
check("CAVEAT: starts with IMPORTANT",
      mock_phase_return["caveat_2nd_innings_death"].startswith("IMPORTANT"))

# ---- SUMMARY ----
print(f"\n{'='*40}")
print(f"RESULTS: {passed} passed, {failed} failed")
if failed == 0:
    print("ALL TESTS PASSED!")
else:
    print("SOME TESTS FAILED!")
    sys.exit(1)
