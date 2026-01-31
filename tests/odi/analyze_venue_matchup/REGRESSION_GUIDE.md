# 🧪 Automated Venue Matchup Regression Suite

This document outlines the workflow, internal logic, and user guide for the **Venue Matchup Regression Testing Suite** (`tests/tools/run_venue_regression.py`).

## 🎯 Purpose

The goal of this suite is to ensuring that changes to the core cricket engine (specifically `analyze_venue_matchup`) do not introduce regressions or unexpected data changes. It compares the **Output of the Current Code** against a **Golden Master (Expected Results)**.

---

## ⚙️ How It Works

The script operates in three main phases:

### Phase 1: Generation (Latest Results)
1.  **Iterates** through every Team and their Home Venues.
2.  **Executes** `analyze_venue_matchup` against every possible Opponent for that venue.
3.  **Captures** the output (structured metrics or "No data available").
4.  **Saves** this raw data to:
    *   `tests/fixtures/odi/analyze_venue_matchup_latest_test_run_results.json`

### Phase 2: Comparison (Validation)
1.  **Loads** the "Golden Master" file:
    *   `tests/fixtures/odi/analyze_venue_matchup_expected_results.json`
2.  **Compares** every metric for every matchup between "Latest" and "Expected".
3.  **Flags** any discrepancies:
    *   **Mismatch:** The value changed (e.g., Win % went from 50% to 52%).
    *   **New Entry:** A matchup appeared that wasn't there before.
    *   **Missing Entry:** A matchup disappeared.

### Phase 3: Reporting
1.  **Generates** a final report file:
    *   `tests/fixtures/odi/analyze_venue_matchup_final_results.json`
2.  **Status:** Returns `SUCCESS` if identical, or `FAILURE` with a list of specific differences.

---

## 📚 User Manual

### 1. Running a Regression Test

Run this whenever you make changes to the engine and want to verify you haven't broken anything.

```powershell
python tests/tools/run_venue_regression.py
```

**Outcomes:**
*   **✅ SUCCESS:** Console prints `✅ SUCCESS: No regressions found.`
*   **❌ FAILURE:** Console prints `❌ FAILURE: Found X mismatches`.
    *   *Action:* Open `tests/fixtures/odi/analyze_venue_matchup_final_results.json` to see exactly what changed.

### 2. Updating the Golden Master (Merging)

If you made **intentional changes** (e.g., fixed a bug in calculation or added new data) and the "Failure" is actually the **correct new behavior**:

1.  Run the test first to generate the latest results.
2.  Review the failure report to confirm the changes are correct.
3.  Run the script with the merge flag to update the Golden Master:

```powershell
python tests/tools/run_venue_regression.py --merge
```

**Outcome:**
*   The `expected_results.json` file is overwritten with the data from `latest_test_run_results.json`.
*   Future runs will now compare against this new baseline.

---

## 📂 File Structure relative to `tests/fixtures/odi/`

├── fixtures/
│   └── analyze_venue_matchup_expected_results.json        # ✅ "Golden Master" (Baseline Truth)
│   └── analyze_venue_matchup_latest_test_run_results.json # 🆕 Output from last run
│   └── analyze_venue_matchup_test_report.json             # 📊 Comparison Report (Diffs)
