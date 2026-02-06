# 🌍 Global H2H Regression Guide

This directory contains the automated test suite for the `analyze_global_h2h` function.

## 📂 Directory Structure

```text
tests/odi/analyze_global_h2h/
├── fixtures/
│   └── analyze_global_h2h_expected_results.json    # ✅ "Golden Master" (Baseline Truth)
│   └── analyze_global_h2h_latest_test_run_results.json  # 🆕 Output from last run
│   └── analyze_global_h2h_test_report.json         # 📊 Comparison Report (Diffs)
├── runners/
│   └── test_global_h2h.py                          # 🧪 Standard Unittest Runner
├── tools/
│   └── run_global_h2h_regression.py                # ⚙️ Regression Logic
```

## 🚀 How to Run

### 1. Check for Regressions
```powershell
python tests/odi/analyze_global_h2h/tools/run_global_h2h_regression.py
```

### 2. Update Golden Master
```powershell
python tests/odi/analyze_global_h2h/tools/run_global_h2h_regression.py --merge
```

### 3. Run Unit Tests
```powershell
python tests/odi/analyze_global_h2h/runners/test_global_h2h.py
```

## 🧠 Coverage
- **Metric:** Head-to-Head Performance (Neutral & Home/Away included).
- **Scope:** 
    - Full Pairwise Permutations of all 9 Top Teams.
    - Matches in last 5 years.
