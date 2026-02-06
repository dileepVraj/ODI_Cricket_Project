# 🏰 Home Fortress Regression Guide

This directory contains the automated test suite for the `analyze_home_fortress` function (Phase 5).

## 📂 Directory Structure

```text
tests/odi/analyze_home_fortress/
├── fixtures/
│   └── analyze_home_fortress_expected_results.json    # ✅ "Golden Master" (Baseline Truth)
│   └── analyze_home_fortress_latest_test_run_results.json  # 🆕 Output from last run
│   └── analyze_home_fortress_test_report.json         # 📊 Comparison Report (Diffs)
├── runners/
│   └── test_home_fortress.py                          # 🧪 Standard Unittest Runner
├── tools/
│   └── run_fortress_regression.py                     # ⚙️ Regression Logic (Generate & Compare)
│   └── update_snapshots.py                            # 🔄 Helper to update Golden Master
```

## 🚀 How to Run Regression Tests

### 1. Check for Regressions
Run the regression script to verify that current code produces the same output as the Golden Master.

```powershell
python tests/odi/analyze_home_fortress/tools/run_fortress_regression.py
```

- **Success:** Prints `✅ SUCCESS: No regressions found.`
- **Failure:** Prints `❌ FAILURE` and saves details to `fixtures/analyze_home_fortress_final_results.json`.

### 2. Update Golden Master (Snapshot Update)
If you made **intentional changes** to the logic (e.g., metric formulas), run with the merge flag to update the expected results.

```powershell
python tests/odi/analyze_home_fortress/tools/run_fortress_regression.py --merge
```

### 3. Run Unit Tests
To run the tests within the standard CI/Unit Test framework:

```powershell
python tests/odi/analyze_home_fortress/runners/test_home_fortress.py
```

## 🧠 What is Tested?
- **Scope:** All major Teams at their active Venues.
- **Scenario:** "vs All" Opponents (Global Fortress View) for 10 years back.
- **Metrics Verified:** 
    - Win %
    - Batting 1st / Chasing Records
    - Average Scores
    - Defensive Records

## ⚠️ Notes
- The "Golden Master" file is large. Do not manually edit it unless fixing a minor typo. Use the `--merge` tool.
- If you change the **structure** of the output (e.g., rename keys like `HDR_HOME`), you MUST update the snapshots.
