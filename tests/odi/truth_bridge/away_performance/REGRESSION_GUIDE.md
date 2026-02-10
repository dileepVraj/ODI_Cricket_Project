# 🌉 Away Performance: Regression Guide (v2.5)

This suite verifies the `analyze_away_performance` function, which generates a matrix report of a team's performance at **Neutral** and **Opposition Home** venues.

## 🏗️ Suite Structure

- **Function**: `TeamEngine.analyze_away_performance(team_name, years_back=10)`
- **Key-Discovery**: Uses **Matrix Layout** (Row-per-Opponent).
- **Fingerprinting**: Uses `MATCH_IDS` (v2.5) for row-level verification.

## 📊 Legacy Schema Checklist (Zero-Destruction)

We strictly follow the schema from the legacy `analyze_away_performance_latest_test_run_results.json`:

| Metric | Type | Description |
| :--- | :--- | :--- |
| **Opponent** | string | The team played against (e.g., `⚡ OVERALL`, `India`). |
| **Mat** | integer | Total matches played away. |
| **Won** | integer | Total wins. |
| **Lost** | integer | Total losses. |
| **Tie/NR** | integer | Matches with no result. |
| **Win %** | string | Percentage formatted as `XY%`. |
| **Last 5** | string | Visual form guide (Emojis). |
| **[Team] Avg (1st)** | string | Team's batting average when batting 1st, formatted as `280 (10)`. |
| **Opp Avg (1st)** | string | Opponent's batting average when batting 1st. |
| **MATCH_IDS** | string | Comma-separated Fingerprint (Truth Bridge v2.5 Only). |

## 🚀 Execution

```powershell
# Run Verification
python -m tests.odi.truth_bridge.away_performance.test_runner

# Run Seeding (Key-Discovery Mode)
$env:SEED_MODE="1"; python -m tests.odi.truth_bridge.away_performance.test_runner
```

## 🔍 Diagnostic Logic

1. **PASS**: Metrics and Match IDs match perfectly.
2. **DATA DRIFT**: Match IDs differ from ground truth. This is normal when new matches are added to the CSV.
3. **LOGIC BUG**: Match IDs are the same, but metrics (Win %, Avgs) differ. **This requires a code fix.**
