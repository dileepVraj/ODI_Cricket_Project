# 🦁 Home Dominance Regression Guide

This directory contains the automated test suite for the `analyze_home_dominance` function.

## 📂 Directory Structure

```text
tests/odi/analyze_home_dominance/
├── fixtures/
│   └── analyze_home_dominance_expected_results.json    # ✅ "Golden Master" (Baseline Truth)
│   └── analyze_home_dominance_latest_test_run_results.json  # 🆕 Output from last run
│   └── analyze_home_dominance_test_report.json         # 📊 Comparison Report (Diffs)
├── runners/
│   └── test_home_dominance.py                          # 🧪 Standard Unittest Runner
├── tools/
│   └── run_home_dominance_regression.py                # ⚙️ Regression Logic
```

## 🚀 How to Run

### 1. Check for Regressions
```powershell
python tests/odi/analyze_home_dominance/tools/run_home_dominance_regression.py
```

### 2. Update Golden Master
```powershell
python tests/odi/analyze_home_dominance/tools/run_home_dominance_regression.py --merge
```

### 3. Run Unit Tests
```powershell
python tests/odi/analyze_home_dominance/runners/test_home_dominance.py
```

## 🧠 Coverage
- **Metric:** Home Advantage & Dominance Matrix.
- **Scope:** All 9 Major Teams as Home Hosts.
- **Verification:** 
    - Checks "Won/Lost" text format in Form Guide.
    - Validates Win % and 1st Innings Averages.
