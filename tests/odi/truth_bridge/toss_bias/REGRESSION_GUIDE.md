# 🪙 Truth Bridge: Toss Bias Suite
**Status:** ✅ Migrated to Truth Bridge (Legacy Fixture Mode)
**Diagnosis:** 🧬 Fingerprinting Enabled (Match IDs)
**Legacy Source:** `tests/odi/regression_suite/analyze_toss_bias/fixtures/analyze_toss_bias_expected_results.json`

## 1. Suite Structure
- **Target Function**: `TeamEngine.analyze_venue_bias`
- **Output Schema**: Nested Dictionary (Legacy "Fixture" Format)
- **Key Discovery**: Iterates through `venues.py` (VENUE_MAP).

## 2. Schema Checklist
The `ground_truth.json` strictly follows this structure:
```json
{
    "Toss bias report": {
        "Grounds in [Country]": {
            "VENUE_CODE": {
                "Period": "Last 10 years",
                "Matches analyzed": 12,
                "Bias Verdict": "Bat First",
                "Win % Batting First": "55% (15)",
                "...": "..."
            } or "Insufficient Data"
        }
    }
}
```
- **Insufficient Data:** Venues with fewer than 3 matches may be flagged or omitted depending on strictness.
- **Fingerprinting:** Each venue result includes a hidden `MATCH_IDS` field used by the base runner to detect Data Drift vs Logic Regression.

## 3. Metrics Tested
- **Bias Verdict**: Critical decision logic (Bat First / Bowl First / Neutral).
- **Sample Size**: `Matches analyzed`.
- **Win Rates**: `Win % Batting First` vs `Win % Chasing`.
- **Averages**: `Avg 1st innings score` vs `Avg 2nd innings score`.

## 4. Execution
```powershell
# Standard Verification
python -m tests.odi.truth_bridge.toss_bias.test_runner

# Update Baseline (Seed)
$env:SEED_MODE="1"; python -m tests.odi.truth_bridge.toss_bias.test_runner
```
