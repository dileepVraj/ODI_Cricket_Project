# Away Performance Regression Guide

## 📌 Overview
This suite verifies the stability of the `analyze_away_performance` function in `core/team_engine.py`.  
It ensures that calculations for **Away Matches Only** remain accurate for all major teams.

## 📂 Structure
- **Runners**: `runners/test_away_performance.py` (Main Entry Point)
- **Tools**: `tools/run_away_regression.py` (data generation & comparison logic)
- **Fixtures**: `fixtures/analyze_away_performance_expected_results.json` (The Truth Source)

## 🚀 How to Run
### 1. Run Verification (Standard)
```bash
python -m unittest tests/odi/analyze_away_performance/runners/test_away_performance.py
```

### 2. Update Baseline (Regression Fix)
If logic changes are intentional, update the snapshots:
```bash
python tests/odi/analyze_away_performance/tools/run_away_regression.py --merge
```

## 📊 Coverage
- **Teams Checked**: Australia, Bangladesh, England, India, New Zealand, Pakistan, South Africa, Sri Lanka, West Indies.
- **Metrics Verified**:
    - Win/Loss Record (Away)
    - Last 5 Form string
    - Per-Opponent breakdown
    - Away Batting Averages (Self vs Opponent)
