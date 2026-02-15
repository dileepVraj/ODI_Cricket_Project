# 🦁 Truth Bridge: Analyze Home Dominance (Home Record Matrix)

This suite verifies a team's performance at home against all major opponents in a matrix format. It ensures that the engine correctly identifies home venues for each team and aggregates their record (Mat/Won/Lost/Avg) accurately.

## 📁 Structure
- `ground_truth.json`: The source of truth containing matrix rows for each focal team (e.g., "India", "Australia").
- `test_runner.py`: The automated verification engine (v2.5 - Discovery Mode).
- `report.json`: Detailed diagnostic results of the latest execution.

## 🚀 How to Run
From the project root:
```powershell
python -m tests.odi.truth_bridge.home_dominance.test_runner
```

## 🧬 Diagnostic Logic (Fingerprinting)
This suite uses the **Match ID Fingerprint** for every row in the matrix.
- **Matrix Row Signatures**: Each entry (e.g., "Australia vs India") contains its own `MATCH_IDS` string.
- **Overall Summary**: The first row (`⚡ OVERALL`) summarizes performance against all top-tier teams.
- **Venue Mapping**: The suite relies on the `c_codes` dictionary in `team_engine.py` to map teams to their geographic venue prefixes (e.g., `IND_`, `AUS_`).

### Failure Diagnosis:
1.  **📊 DATA_DRIFT**: The engine sees the same historic matches but includes a new home series.
    *   **Action**: Verify new stats and update baseline via **Seed Mode**.
2.  **🧱 LOGIC_REGRESSION**: Fingerprints match exactly, but Win % or Averages for a specific row have shifted.
    *   **Action**: **Bug detected** in `_generate_matrix_report` or `analyze_home_dominance`.
3.  **📉 FILTERING_REGRESSION**: The row's `Mat` count dropped because the engine stopped "seeing" some home matches.

## 💾 Seed Mode (Baseline Update)
To set a new baseline after confirming engine updates:
```powershell
$env:SEED_MODE="1"; python -m tests.odi.truth_bridge.home_dominance.test_runner
```

> [!IMPORTANT]
> The Home Dominance suite is sensitive to the `c_codes` mapping. If a new home stadium prefix is added to the dataset, Ensure `team_engine.py` is updated before running verification.
