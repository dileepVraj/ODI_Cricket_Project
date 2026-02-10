# 🌉 Truth Bridge: Analyze Venue Matchup

This suite automates the manual 16-hour verification process by cross-referencing engine results against a "Ground Truth" ledger derived from ESPN Statsguru.

## 📁 Structure
- `ground_truth.json`: The source of truth containing 240+ manually verified benchmarks.
- `test_runner.py`: The automated verification engine (v2.0 - Auto-Diagnosis Enabled).
- `report.json`: Detailed diagnostic results of the latest execution.

## 🚀 How to Run
From the project root:
```powershell
python tests/odi/truth_bridge/analyze_venue_matchup/test_runner.py
```

## 🧬 Auto-Diagnosis System (Fingerprinting v2.5)
The v2.5 runner uses **Signature-Based Verification**. Every benchmark in the ledger now tracks the exact `match_ids` used to generate the stats. This eliminates "Ambiguous" failures and false positives:

### 1. 📊 DATA_DRIFT (Benign)
*   **Trigger:** `truth_ids` is a subset of `engine_ids` AND counts differ.
*   **Meaning:** DEFINITIVE: You have ingested new matches. The engine is seeing everything it used to see, plus new data.
*   **Action:** Update the baseline via **Seed Mode**.

### 2. 🧱 LOGIC_REGRESSION (Critical)
*   **Trigger:** `engine_ids == truth_ids` BUT stats (Win %, Avg) differ.
*   **Meaning:** DEFINITIVE BUG: The matches are identical, but the calculation has changed.
*   **Action:** Investigate the code in `TeamEngine`. Do **NOT** seed.

### 3. 📉 FILTERING_REGRESSION (Critical)
*   **Trigger:** `engine_ids` is a subset of `truth_ids` (Engine sees fewer matches).
*   **Meaning:** Engine has lost visibility of matches due to a filtering bug or data corruption.
*   **Action:** Check `_apply_smart_filters` in `TeamEngine`.

## 💾 Seed Mode (Baseline Update)
To overwrite the truth ledger with current engine results after validating data updates:
```powershell
$env:SEED_MODE="1"; python tests/odi/truth_bridge/analyze_venue_matchup/test_runner.py
```

## 📋 Interpreting report.json
Failures are logged with a `diagnosis` string and a `mismatches` array:
```json
{
    "matchup": "India vs Australia",
    "venue": "IND_MUMBAI_WANKHEDE",
    "status": "FAIL",
    "diagnosis": "DATA_DRIFT: New matches detected...",
    "mismatches": [
        {
            "metric": "Matches Played",
            "expected": "12",
            "actual": "13"
        }
    ]
}
```

> [!IMPORTANT]
> The `ground_truth.json` is the anchor of the project's data integrity. Always verify 🔴 Failures manually on Statsguru before updating the baseline.
