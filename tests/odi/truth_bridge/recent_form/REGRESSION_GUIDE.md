# 📉 Recent Form: Truth Bridge Guide

Verification of team form sequences (`W`, `L`, `T`, `NR`) across global and continental contexts.

## 🏗️ Metrics & Fingerprinting

### 1. `summary_code`
A sequence of strings representing the result of the last 5 matches:
- `W`: Win
- `L`: Loss
- `T`: Tie
- `NR`: No Result

### 2. `MATCH_IDS` (Fingerprint)
A sorted, comma-separated list of the 5 Match IDs used to calculate the form. This is mandatory for v2.5 auto-diagnosis.

## 📂 Data Structure
The `ground_truth.json` covers three distinct form variations:
1. **General Form**: `Team > Global`
2. **Regional Form**: `Team > Continent` (e.g. Asia, Europe)
3. **H2H Form**: `H2H_Form > TeamA_vs_TeamB_Global`
4. **Regional H2H Form**: `H2H_Form > TeamA_vs_TeamB_Asia`

### Example
```json
{
    "India": {
        "Global": { "summary_code": ["L", "L", "W", "W", "L"], "MATCH_IDS": "..." },
        "Asia": { ... }
    },
    "H2H_Form": {
        "India_vs_Pakistan_Global": { ... },
        "India_vs_Pakistan_Asia": { ... }
    }
}
```

## 🚀 Operations

### Run Verification
```powershell
python -m tests.odi.truth_bridge.recent_form.test_runner
```

### Seed Ground Truth
```powershell
$env:SEED_MODE="1"; python -m tests.odi.truth_bridge.recent_form.test_runner
```

## 🔍 Diagnosis
- **PASS**: Form sequence matches exactly for all teams/continents.
- **LOGIC_REGRESSION**: Result sequence differs even though Match IDs are the same (Bug in result calculation).
- **DATA_DRIFT**: Result sequence differs because newer matches were ingested (Normal behavior).
