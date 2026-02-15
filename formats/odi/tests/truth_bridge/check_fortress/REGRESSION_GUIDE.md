# 🏰 Truth Bridge: Check Fortress (Home Performance)

This suite verifies a team's dominance at their home venues (e.g., Australia at the MCG, India at Wankhede). It ensures that the engine correctly filters matches where the focus team is playing at a specific stadium, calculating their win percentages, venue averages, and chasing/defending records.

## 📁 Structure
- `ground_truth.json`: The source of truth containing 92 seeded team-venue combinations.
- `test_runner.py`: The automated verification engine (v2.5 - Discovery Mode).
- `report.json`: Detailed diagnostic results of the latest execution.

## 🚀 How to Run
From the project root:
```powershell
python -m tests.odi.truth_bridge.check_fortress.test_runner
```

## 🧬 Diagnostic Logic (Fingerprinting)
This suite uses the **Match ID Fingerprint** to validate results.
- **Key-Discovery Mode**: The runner scans the legacy fixture and discovers keys like `"Australia at Melbourne Cricket Ground"`.
- **Fuzzy Naming**: The engine maps legacy names (e.g., "Shaheed Veercket Narayan Singh...") to internal IDs using fuzzy matching logic in `team_engine.py`.

### Failure Diagnosis:
1.  **📊 DATA_DRIFT**: The engine sees the same matches as the truth, plus new ones (e.g., a match played last week).
    *   **Action**: Validate the new stats and update the baseline via **Seed Mode**.
2.  **🧱 LOGIC_REGRESSION**: Fingerprints match exactly, but metrics like "Australia Win %" have changed.
    *   **Action**: **CRITICAL BUG.** Investigate `analyze_home_fortress` in `team_engine.py`. Do NOT seed.
3.  **📉 FILTERING_REGRESSION**: The engine sees fewer matches than the truth.
    *   **Action**: Check if the stadium name mapping or date cutoff logic has regressed.

## 💾 Seed Mode (Baseline Update)
To set a new baseline after confirming engine updates:
```powershell
$env:SEED_MODE="1"; python -m tests.odi.truth_bridge.check_fortress.test_runner
```

> [!TIP]
> **Data Integrity**: This suite verifies over 40 distinct metrics per scenario, including "Avg Successful Chase" and "Lowest Defended Score." Always check the `report.json` for specific metric mismatches before seeding.
