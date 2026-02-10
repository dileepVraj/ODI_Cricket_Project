# 🌍 Truth Bridge: Analyze Global H2H (Global Rivalry Stats)

This suite verifies head-to-head performance between two teams globally across all venues and host countries. It ensures that the engine correctly aggregates matches based on team pairings and lookback periods.

## 📁 Structure
- `ground_truth.json`: The source of truth containing pairwise team matchups grouped by focal teams (e.g., "Australia vs rest").
- `test_runner.py`: The automated verification engine (v2.5 - Discovery Mode).
- `report.json`: Detailed diagnostic results of the latest execution.

## 🚀 How to Run
From the project root:
```powershell
python -m tests.odi.truth_bridge.global_h2h.test_runner
```

## 🧬 Diagnostic Logic (Fingerprinting)
This suite uses the **Match ID Fingerprint** to validate results.
- **Nested Focal Groups**: Scenarios are grouped by a focus team followed by individual matchups (e.g., `"Australia vs rest" > "Australia vs India"`).
- **Global Context**: The engine searches for all matches between Team A and Team B across the entire historical database (subject to time filters).

### Failure Diagnosis:
1.  **📊 DATA_DRIFT**: New global matches have been played. The engine results are valid but newer than the baseline.
    *   **Action**: Update the baseline via **Seed Mode**.
2.  **🧱 LOGIC_REGRESSION**: The match IDs used in the calculation are identical, but the win percentages or averages differ.
    *   **Action**: **INVESTIGATE Engine.** Check `analyze_global_h2h` in `team_engine.py`.
3.  **📉 FILTERING_REGRESSION**: The engine results are based on fewer matches than the truth, indicating a loss of data visibility.

## 💾 Seed Mode (Baseline Update)
To set a new baseline after confirming engine reliability:
```powershell
$env:SEED_MODE="1"; python -m tests.odi.truth_bridge.global_h2h.test_runner
```

> [!NOTE]
> This suite preserves the exact nested structure of legacy Global H2H fixtures, ensuring compatibility with historical reporting tools while adding modern diagnostic fingerprints.
