# 🗺️ Truth Bridge: Analyze Country H2H (Host Country Stats)

This suite verifies head-to-head performance within specific host countries (e.g., India vs Pakistan in the UAE). It ensures that the engine correctly filters matches by venue location across different geographic and historical contexts.

## 📁 Structure
- `ground_truth.json`: The source of truth containing 72 seeded team-country-opponent combinations.
- `test_runner.py`: The automated verification engine (v2.5 - Discovery Mode).
- `report.json`: Detailed diagnostic results of the latest execution.

## 🚀 How to Run
From the project root:
```powershell
python -m tests.odi.truth_bridge.check_host_country_stats.test_runner
```

## 🧬 Diagnostic Logic (Fingerprinting)
This suite uses the **Match ID Fingerprint** to validate results.
- **Composite Keys**: Scenarios are stored using the format `HomeTeam: HomeTeam vs OppTeam` (e.g., `"Australia: Australia vs India"`).
- **Metadata**: Each record strictly preserves the host country and lookback years to match the legacy test suite.

### Failure Diagnosis:
1.  **📊 DATA_DRIFT**: The engine sees the same matches as the truth, plus new ones. This is expected after a CSV update.
2.  **🧱 LOGIC_REGRESSION**: The match IDs match exactly, but the Win % or averages differ. This indicates a bug in `analyze_country_h2h`.
3.  **📉 FILTERING_REGRESSION**: The engine sees fewer matches than the truth, suggesting a regression in country-based filtering logic.

## 💾 Seed Mode (Updating the Ledger)
If you have verified new data on Statsguru and want to set a new baseline:
```powershell
$env:SEED_MODE="1"; python -m tests.odi.truth_bridge.check_host_country_stats.test_runner
```

> [!IMPORTANT]
> The `analyze_country_h2h` function uses fuzzy country matching (e.g., "UAE" matches "Dubai", "Sharjah"). Always verify that the `MATCH_IDS` in the report accurately cover all expected venues in the host country.
