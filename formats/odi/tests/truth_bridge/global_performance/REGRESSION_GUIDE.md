# 🌍 Global Performance: Regression Guide (v2.5)

This suite verifies the `analyze_global_performance` function, which generates a comprehensive matrix report of a team's performance **EVERYWHERE** (Home + Away + Neutral).

## 🏗️ Suite Structure

- **Function**: `TeamEngine.analyze_global_performance(team_name, years_back=10)`
- **Key-Discovery**: Iterates through major 9 teams.
- **Fingerprinting**: Uses `MATCH_IDS` (v2.5) for row-level verification.
- **Metadata**: Includes `Teams considered` list for coverage auditing.

## 📊 Matrix Schema Checklist

We adhere to the standard Matrix Report schema:

| Metric | Type | Description |
| :--- | :--- | :--- |
| **Opponent** | string | The team played against (e.g., `⚡ OVERALL`, `India`). |
| **Mat** | integer | Total matches played globally. |
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
python -m tests.odi.truth_bridge.global_performance.test_runner

# Run Seeding (Key-Discovery Mode)
$env:SEED_MODE="1"; python -m tests.odi.truth_bridge.global_performance.test_runner
```

## 🔍 Diagnostic Logic

1. **PASS**: Metrics and Match IDs match perfectly.
2. **DATA DRIFT**: Match IDs differ from ground truth. This is normal when new matches are added to the CSV.
3. **LOGIC BUG**: Match IDs are the same, but metrics (Win %, Avgs) differ. **This requires a code fix.**
