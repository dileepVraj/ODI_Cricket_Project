# 🌉 The Truth Bridge: Master Regression Guide (v2.5)

The Truth Bridge is the "Golden Source" for verifying the Cricket Project's analysis engines. It uses **Fingerprint-First Diagnostics** to automatically distinguish between "new data" and "broken code."

---

## 🏗️ Core Philosophy
Standard unit tests often fail when data changes. The Truth Bridge avoids this by using **`MATCH_IDS` Fingerprinting**.

### 2. Standardized Schema (v2.5)
All Truth Bridge suites must adhere to the **Fingerprint Protocol**:

```json
{
    "Metric": "Win %",
    "Value": "55%",
    "MATCH_IDS": "12345,67890"  // <--- MANDATORY: Enables Auto-Diagnosis
}
```

**Rule:** If the engine function does not return `MATCH_IDS`, you **MUST** refactor the engine to include it. Do not skip this step.
- If Match IDs are unchanged but results differ -> **Logic Bug** (Code is broken).
- If Match IDs are new/different -> **Data Drift** (Expected updates).

---

## 📂 Navigation & Suite Guides
Each analysis function has its own specialized folder containing a **detailed** `REGRESSION_GUIDE.md` specific to its logic:

| Analysis Function | Folder Path | Status |
| :--- | :--- | :--- |
| **Venue Matchups** | [`analyze_venue_matchup/`](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/tests/odi/truth_bridge/analyze_venue_matchup/REGRESSION_GUIDE.md) | ✅ Active |
| **Fortress Check** | [`check_fortress/`](file:///c:/c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/tests/odi/truth_bridge/check_fortress/REGRESSION_GUIDE.md) | ✅ Active |
| **Host Country Stats** | [`check_host_country_stats/`](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/tests/odi/truth_bridge/check_host_country_stats/REGRESSION_GUIDE.md) | ✅ Active |
| **Global Head-to-Head** | [`global_h2h/`](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/tests/odi/truth_bridge/global_h2h/REGRESSION_GUIDE.md) | ✅ Active |
| **Home Dominance** | [`home_dominance/`](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/tests/odi/truth_bridge/home_dominance/REGRESSION_GUIDE.md) | ✅ Active |
| **Away Performance** | [`away_performance/`](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/tests/odi/truth_bridge/away_performance/REGRESSION_GUIDE.md) | ✅ Active |
| **Global Performance** | [`global_performance/`](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/tests/odi/truth_bridge/global_performance/REGRESSION_GUIDE.md) | ✅ Active |
| **Recent Form** | [`recent_form/`](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/tests/odi/truth_bridge/recent_form/REGRESSION_GUIDE.md) | ✅ Active |
| **Compare Squads** | [`compare_squads/`](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/tests/odi/truth_bridge/compare_squads/REGRESSION_GUIDE.md) | ✅ Active |
| **Continent Perf** | [`continent_performance/`](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/tests/odi/truth_bridge/continent_performance/REGRESSION_GUIDE.md) | ✅ Active |

---

## 🚀 Standard Operations

### 1. Running Individual Suites
To run a specific suite from the project root:
```powershell
python -m tests.odi.truth_bridge.analyze_venue_matchup.test_runner
python -m tests.odi.truth_bridge.check_fortress.test_runner
python -m tests.odi.truth_bridge.check_host_country_stats.test_runner
python -m tests.odi.truth_bridge.global_h2h.test_runner
python -m tests.odi.truth_bridge.home_dominance.test_runner
```

### 2. Updating Baselines (Seed Mode)
Only update the baseline after verifying new data on Statsguru:
```powershell
$env:SEED_MODE="1"; python -m tests.odi.truth_bridge.home_dominance.test_runner
```

---

## � Diagnostic Summary
| Diagnosis | Meaning | Action |
| :--- | :--- | :--- |
| **PASS** | Everything matches | Success. |
| **LOGIC BUG** | Code logic has regressed | **Fix Code.** Do NOT seed. |
| **DATA DRIFT** | New matches ingested | **Seed Mode.** Update baseline. |

---
> [!IMPORTANT]
> Always refer to the **local `REGRESSION_GUIDE.md`** inside each suite folder for detailed metric definitions and key structure specific to that function.
