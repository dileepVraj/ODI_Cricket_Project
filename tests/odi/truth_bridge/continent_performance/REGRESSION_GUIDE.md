# 🌏 Continent Performance: Truth Bridge Guide

Verification of regional performance analytics across major cricketing continents (Asia, Europe, etc.).

## 🏗️ Metrics & Layers

### 1. Matrix Statistics
Verifies "Overall" and "Per-Opponent" metrics within the region:
- **Mat / Won / Lost / Tie/NR**: Volume and outcome stats.
- **Win %**: Percentage of matches won (excluding ties/NR).
- **Last 5**: Recent form sequence within that region.
- **Avg Scores**: Batting/Bowling averages for both teams.

### 2. `MATCH_IDS` (Fingerprint)
Each row in the matrix contains a `MATCH_IDS` string. This allows the system to distinguish between:
- **LOGIC_REGRESSION**: Metrics changed but the matches analyzed are identical.
- **DATA_DRIFT**: Metrics changed because the dataset has been updated with new regional matches.

## 📂 Suite Configuration
Bootstraps from legacy fixtures including performance stats for:
- Australia in Asia
- England in Asia
- India in Asia
- New Zealand in Asia
- Pakistan in Asia
- South Africa in Asia
- Sri Lanka in Asia
- Bangladesh in Asia

## 🚀 Operations

### Run Verification
```powershell
python -m tests.odi.truth_bridge.continent_performance.test_runner
```

### Seed Ground Truth
```powershell
$env:SEED_MODE="1"; python -m tests.odi.truth_bridge.continent_performance.test_runner
```

## 🔍 Diagnosis
- **PASS**: All regional metrics match exactly.
- **FAIL**: Metrics mismatch. Check `report.json` for specific row/opponent discrepancies and fingerprints.
