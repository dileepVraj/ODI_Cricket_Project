# 🗺️ Country H2H Regression Guide

This directory contains the automated test suite for the `analyze_country_h2h` function (Phase 5).

## 📂 Directory Structure

```text
tests/odi/analyze_country_h2h/
├── fixtures/
│   └── analyze_country_h2h_expected_results.json    # ✅ "Golden Master" (Baseline Truth)
│   └── analyze_country_h2h_latest_test_run_results.json  # 🆕 Output from last run
│   └── analyze_country_h2h_test_report.json         # 📊 Comparison Report (Diffs)
├── runners/
│   └── test_country_h2h.py                          # 🧪 Standard Unittest Runner
├── tools/
│   └── run_h2h_regression.py                        # ⚙️ Regression Logic
│   └── update_snapshots.py                          # 🔄 Helper to update Golden Master
```

## 🚀 How to Run

### 1. Check for Regressions
```powershell
python tests/odi/analyze_country_h2h/tools/run_h2h_regression.py
```

### 2. Update Golden Master
```powershell
python tests/odi/analyze_country_h2h/tools/run_h2h_regression.py --merge
```

### 3. Run Unit Tests
```powershell
python tests/odi/analyze_country_h2h/runners/test_country_h2h.py
```

## 🧠 Coverage
- **Metric:** Head-to-Head Performance in Host Nation.
- **Scope:** 
    - Full Permutation: (9 Host Nations) x (8 Visiting Teams).
    - Scenario: Home Team vs Visitor in Home Country.
- **Depth:** Last 10 years.
