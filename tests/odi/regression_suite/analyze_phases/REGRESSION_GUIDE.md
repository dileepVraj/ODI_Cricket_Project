# Regression Guide: Phase Analysis (Level 5)

## 🎯 Goal
Verify that **Powerplay (1-10)**, **Middle (11-40)**, and **Death (41-50)** statistics are calculated correctly for:
1.  **Venue Baselines** (Overall Ground Averages).
2.  **Home Team** specifics.
3.  **Away Team** specifics.
4.  **Global Habits** (Bat First vs Chasing comparisons).

## 🧪 Validated Logic
- **N-vs-N Coverage:** Logic loops through **Every Opponent** for **Every Venue** (approx 450 scenarios).
- **Metric Integrity:** Checks `pp_runs`, `pp_wkts`, `dth_runs`, etc. against the Golden Master.
- **Strategic Alerts:** Verifies that "EDGE" and "RISK" flags trigger correctly based on specific thresholds.

## 📂 File Structure
- `tools/generate_phase_data.py`: **The Generator**. Runs the "N-vs-N" loop.
- `tools/run_phase_regression.py`: **The Runner**. Compares Engine Output vs Golden Master.
- `fixtures/analyze_phases_expected_results.json`: **Golden Master**. The Source of Truth.

## 🚀 How to Run
```bash
# 1. Run Regression (CI/CD)
python tests/odi/analyze_phases/tools/run_phase_regression.py

# 2. Regenerate Golden Master (If Logic Changes)
python tests/odi/analyze_phases/tools/generate_phase_data.py
```

## ⚠️ Common Pitfalls
- **"Insufficient Data" Error:** Ensure `venues.py` is mapping names correctly.
- **Timeouts:** The full N-vs-N generation takes ~2-3 minutes. Be patient.
- **Metric Drift:** If you change the definition of "Middle Overs" (e.g. 11-35), you MUST regenerate the master.
