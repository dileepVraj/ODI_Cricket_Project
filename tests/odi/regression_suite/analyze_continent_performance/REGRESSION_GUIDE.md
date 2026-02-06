# Regression Guide: Continent Performance (Level 4)

## 🎯 Goal
Verify the "Global vs Regional" performance matrices (`TeamEngine.analyze_continent_performance`).
Ensures that:
1.  **Metric Accuracy:** Win % and Batting/Bowling Averages are correct for each continent.
2.  **Regional Logic:** Correctly categorizes venues into continents (Asia, SENA, etc.).
3.  **Visualization:** Verifies that HTML outputs for "Performance Matrix" are generated.

## 🧪 Validated Logic
- **Scope:** Tests Top 10 Nations across all major continents.
- **Fixture:** Uses `analyze_continent_performance_expected_results.json`.
- **Logic:** Compares `Win %`, `Bat Avg`, `Bowl Avg` for Home/Away/Neutral contexts.

## 📂 File Structure
- `tools/generate_test_data.py`: **The Generator**. Iterates Teams and Continents.
- `tools/run_continent_regression.py`: **The Runner**. Executes suite.
- `fixtures/analyze_continent_performance_expected_results.json`: **Golden Master**.

## 🚀 How to Run
```bash
# 1. Run Regression (CI/CD)
python tests/odi/analyze_continent_performance/tools/run_continent_regression.py

# 2. Regenerate Golden Master
python tests/odi/analyze_continent_performance/tools/generate_test_data.py
```
