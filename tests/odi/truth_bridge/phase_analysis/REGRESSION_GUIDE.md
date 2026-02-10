# 🕒 Phase Analysis Truth Bridge (Regression Guide)

## 1. Suite Overview
**Target Function:** `TeamEngine.analyze_venue_phases`
**Status:** ✅ Migrated to Truth Bridge
**Schema Mode:** **Legacy Fixture Loyalty**
**Diagnosis:** 🧬 Fingerprinting Enabled (Match IDs)
**Legacy Source:** `tests/odi/regression_suite/analyze_phases/fixtures/analyze_phases_latest_results.json`

This suite verifies the granular "Phase Analysis" logic, which breaks down scoring into Powerplay (1-10), Middle (11-40), and Death (41-50) overs. It validates Venue Baselines, Team History at Venue, and Global Habits.

---

## 2. Execution Command
To run the verification suite:
```powershell
python -m tests.odi.truth_bridge.phase_analysis.test_runner
```

To **regenerate** the ground truth (Seed Mode):
```powershell
$env:SEED_MODE="1"; python -m tests.odi.truth_bridge.phase_analysis.test_runner
```

---

## 3. Schema Structure
The output is a complex nested dictionary designed to power detailed UI reports.

### Root Keys
- `Phase Analysis Report`: Top-level container.
- `Grounds in [Country]`: Grouping by Host Country.
- `[Venue Code]`: Specific Venue Data (e.g., `AUS_ADELAIDE`).

### Venue Data Structure
For each venue, we capture:
1.  **`Host`**: The name of the host country.
2.  **`Baseline_Metrics`**: Context for the Home Team vs "All" Opponents.
3.  **`vs_[Opponent]`**: Detailed Matchup context for specific opponents.

### Inner Metrics (`venue_baseline`)
Contains averages and wicket rates for each phase:
```json
"venue_baseline": {
    "pp_avg_1st": 45.1,
    "pp_wkts_1st": 2.1,
    "mid_avg_1st": 154.0,
    ...
    "dth_wkts_2nd": 1.6
}
```

### Inner Metrics (`global_habits`)
Used for strategic comparison (e.g., "Edge" detection):
```json
"global_habits": {
    "bat_first": { "h_pp_runs": 50.3, "a_pp_runs": 42.1, ... },
    "chasing": { "h_mid_wkts": 3.3, ... }
}
```

---

## 4. Key Metrics Monitored
- **Phase Definitions:**
    - PP: Overs 1-10
    - Mid: Overs 11-40
    - Death: Overs 41-50
- **Contexts:**
    - `venue_baseline`: All teams at this venue.
    - `home_at_venue`: Home team's record at this venue.
    - `away_at_venue`: Away team's record at this venue.
    - `global_habits`: Recent form (Global) for strategic comparison.

## 5. Known Behaviors
- **Insufficient Data:** Venues with no data return `"Insufficient Data"` or empty inner dictionaries.
- **Alerts:** Strategic alerts (e.g., "RIKS: Australia collapses chasing") are generated based on logic thresholds (e.g., >3 wkts lost in middle overs).
- **Fingerprinting:** Each venue result includes a hidden `MATCH_IDS` key. This allows the test runner to automatically diagnose if a failure is due to **Data Drift** (New Matches) or **Logic Regression** (Bug).
