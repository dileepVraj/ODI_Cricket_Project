# Regression Guide: Recent Form Analysis (Level 3)

## 🎯 Goal
Verify the integrity of **Recent Form** Logic (`check_recent_form` -> `analyze_team_form`).
Ensures that:
1.  **Form Sequence:** Correct W/L/T pattern is returned (e.g., `["W", "L", "W"]`).
2.  **Match Sorting:** Matches are strictly ordered by Start Date (Newest First).
3.  **Scopes:** Logic holds for Global, Rivalry (vs Opponent), and Regional (in Continent) contexts.

## 🧪 Validated Logic
- **Scope:**
    - **Global:** Overall recent form (vs All).
    - **Continental:** Iterates through **Asia, Africa, Europe, Oceania, Americas**.
- **Fixture:** Uses `recent_form_expected_results.json`.
- **Logic:** Compares `summary_code` sequence ONLY (e.g. `['W', 'L', 'W']`).
    - **Ignored:** Match Dates, Opponent Names (removed from Golden Master).

## 📂 File Structure
- `tools/generate_form_data.py`: **The Generator**. Iterates multi-level scenarios.
- `tools/run_form_regression.py`: **The Runner**. Validates Engine output.
- `fixtures/recent_form_expected_results.json`: **Golden Master**.

## 🚀 How to Run
```bash
# 1. Run Regression (CI/CD)
python tests/odi/analyze_recent_form/tools/run_form_regression.py

# 2. Regenerate Golden Master
python tests/odi/analyze_recent_form/tools/generate_form_data.py
```

## ⚠️ Common Pitfalls
- **Import Errors:** Ensure `sys.path` includes the Project Root to import `engine.py`.
- **Date Sort:** If the engine sort order breaks, the regression will fail on "Date Mismatch".
