# 🧪 Compare Squads Regression Suite (Level 4)

## 🎯 Goal
Ensure the stability of the **"Compare Selected XI's"** feature, which is the most complex analytical engine in the dashboard (4 Layers of Analysis).
This suite verifies that refactors (e.g., separating Logic from UI) do not alter the calculated values.

## 📂 Architecture
- **Location:** `tests/odi/compare_squads/`
- **Output:** `tests/odi/compare_squads/fixtures/`

### 1. The Generator (`tools/generate_squad_data.py`)
- **Role:** Creates the "Golden Master" (`compare_squads_expected_results.json`).
- **Mechanism:**
    - **Dynamic Discovery:** does NOT use hardcoded players. Instead, it queries `engine.get_last_match_xi(Team)` to find the most recent real-world XI.
    - **Scope:** 50 Years of History (by default) to stress-test the H2H engine.
    - **Scenarios:** Covers 5 specific matchups designed to test different continents and team strengths (e.g., ENG vs IND, BAN vs WI).

### 2. The Runner (`tools/run_squad_regression.py`)
- **Role:** Re-runs the logic using the *exact same* metadata (XIs, Venue) from the Golden Master and compares the output.
- **Reporting:** Generates `compare_squads_test_report.json` with a 4-section breakdown.

## 📊 Coverage (The 3 Key Layers)
The regression validates the data structure of:
1.  **Squad Comparison Header:** Experience metrics (Total Caps, Age/Runs/Wickets) and Squad Depth.
2.  **Tactical Matrix (Archetypes):** Performance against specific bowling styles (e.g., "Left Arm Fast").
3.  **H2H Matchups (Bunny Finder):** Dismissal history between specific batters and bowlers.

> [!NOTE]
> **Pro Stats** (Detailed career tables) are excluded from regression to maintain a lightweight Golden Master and focus on strategic analytical stability.

## 🚀 Usage

### To Run Regression (Standard)
```powershell
python tests/odi/compare_squads/tools/run_squad_regression.py
```
*Returns: Pass/Fail status and a report file.*

### To Regenerate Golden Master (After Approved Logic Changes)
```powershell
python tests/odi/compare_squads/tools/generate_squad_data.py
```
*Note: This is a heavy operation (can take 5-10 mins for 50-year scope).*

### To Merge Latest Results into Golden Master
If specific changes are correct and you want to update the baseline:
```powershell
python tests/odi/compare_squads/tools/run_squad_regression.py --merge
```

## 🧠 Lessons Learned & Critical Fixes
- **Missing Columns:** The suite revealed that `FINAL_ODI_MASTER.csv` lacked `bowling_team`, causing crashes. `engine.py` was patched to auto-derive this.
- **Unicode Support:** Scripts explicitly handle UTF-8 to support player names and emojis during console output.
