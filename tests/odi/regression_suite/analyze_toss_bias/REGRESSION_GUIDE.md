# Regression Guide: Toss Bias (Level 4)

## 🎯 Goal
Verify the integrity of **Toss Analysis** (`TeamEngine.analyze_venue_bias`).
Ensures that:
1.  **Win % Calculations** (Bat 1st vs Bowl 1st) remain accurate.
2.  **Bias Verdicts** (BAT FIRST, BOWL FIRST, NEUTRAL) are logic-consistent.
3.  **Venue Coverage** is 100% (using `venues.py`).

## 🧪 Validated Logic
- **Scope:** Dynamic loading of All Venues (via `venues.VENUE_MAP`).
- **Data Integrity:** Comparison of `1st Inn Avg`, `2nd Inn Avg`, and `Win Count` against the Golden Master.
- **Fixture:** Uses `analyze_toss_bias_expected_results.json` as the source of truth.

## 📂 File Structure
- `tools/generate_test_data.py`: **The Generator**. Loads venues dynamically and builds expected results.
- `tools/run_toss_bias_regression.py`: **The Runner**. Executes suite.
- `fixtures/analyze_toss_bias_expected_results.json`: **Golden Master**.

## 🚀 How to Run
```bash
# 1. Run Regression (CI/CD)
python tests/odi/analyze_toss_bias/tools/run_toss_bias_regression.py

# 2. Regenerate Golden Master
python tests/odi/analyze_toss_bias/tools/generate_test_data.py
```

## ⚠️ Common Pitfalls
- **Raw CSV Loading:** Do NOT load `FINAL_ODI_MASTER.csv` directly in tests. Always use `CricketAnalyzer` to get standardized venue names.
- **Metric Formatting:** If you change `55%` to `55.0%` in the engine, this regression will fail.
