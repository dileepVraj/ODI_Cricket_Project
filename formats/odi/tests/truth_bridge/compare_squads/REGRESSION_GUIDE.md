# ⚖️ Compare Squads: Truth Bridge Guide

Verification of the 3-layer analytical engine: Squad Experience, Tactical Matrix, and H2H Matchups.

## 🏗️ Metrics & Layers

### 1. SquadComparison (Experience)
Verifies Caps, Runs, 100s, 50s, and Wickets for the selected XIs.

### 2. TacticalMatrix (Archetypes)
Verifies performance against specific bowling styles (e.g., Left Arm Fast). 
- **Checks:** `_raw` values and formatted HTML strings.

### 3. Matchups (Bunnies)
Verifies dismissal history and averages between specific batters and bowlers.

### 4. `MATCH_IDS` (Fingerprint)
A comma-separated string of Match IDs analyzed. Essential for v2.5 auto-diagnosis.

## 📂 Suite Configuration
The suite uses 5 specific matchups to provide diversity:
1.  **AUS vs BAN** (Cross-Continent, High Bias)
2.  **ENG vs IND** (Elite Matchup, High Volume)
3.  **PAK vs WI** (Neutral Volume)
4.  **SL vs SA** (Varied Conditions)
5.  **NZ vs AFG** (Emerging Matchup)

## 🚀 Operations

### Run Verification
```powershell
python -m tests.odi.truth_bridge.compare_squads.test_runner
```

### Seed Ground Truth
```powershell
$env:SEED_MODE="1"; python -m tests.odi.truth_bridge.compare_squads.test_runner
```

## 🔍 Diagnosis
- **PASS**: All 3 layers match exactly.
- **LOGIC_REGRESSION**: Metrics changed while `MATCH_IDS` remained identical (Indicates a bug in stats calculation).
- **DATA_DRIFT**: Metrics changed because new matches were ingested (Indicates a database update).
