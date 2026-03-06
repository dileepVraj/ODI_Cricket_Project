# AUDIT-P09 - Presentation Purity Sweep

**Task ID:** TASK-026 / P09  
**Audit Series:** Player Engine - Phase 10  
**Date:** 2026-03-05  
**File Audited:** `formats/odi/engines/player_engine.py`  
**Output File:** `docs/audits/player_engine/AUDIT-P09-presentation-purity.md`

---

## 1. Read First Confirmation

Read in full before sweep execution:
1. `docs/guides/ENGINEERING_STANDARDS_BACKEND.md`
2. `docs/ai/SESSION_STATE.md`
3. `docs/audits/player_engine/AUDIT-P01-structural-map.md`
4. `formats/odi/engines/player_engine.py`

Context note: `SESSION_STATE.md` shows active series `TASK-026` but still lists P01 as not started.

---

## 2. Baseline Bouncer

```text
PASS: 100% compliance across 22 file(s).
```

Matches P01 baseline: YES.

---

## 3. Sweep A - Visual Silence Law

### Confirmed Violations

Function: `get_matchups`  
Line: 504  
Violation string: `'Unknown'`  
Pattern type: `UI_PLACEHOLDER`  
Context: `Style` is populated with `'Unknown'` and included in the returned matchup records list.  
Severity: `HIGH`

Function: `get_player_profile`  
Line: 657  
Violation string: `"N/A"`  
Pattern type: `UI_PLACEHOLDER`  
Context: `best_figures` is set to `"N/A"` inside `BowlingStats` and returned via `PlayerProfile`.  
Severity: `MEDIUM`

---

## 4. Sweep B - Pure Primitive Mandate

### Confirmed Violations

Function: `get_player_profile`  
Line: 657  
Return value: `BowlingStats(..., best_figures="N/A", ...)` included in returned `PlayerProfile`  
Expected primitive: `None`/typed null-style domain value for missing best-figures (not UI placeholder string)  
Severity: `MEDIUM`

---

## 5. Sweep C - Consolidation

| Function | Visual Silence Clean | Pure Primitive Clean | Flags |
|---|---|---|---|
| __init__ | YES | YES | NONE |
| _require_nonempty_dict_rule | YES | YES | NONE |
| _require_tactical_thresholds | YES | YES | NONE |
| _require_style_map | YES | YES | NONE |
| _require_player_roles | YES | YES | NONE |
| _require_default_player_role | YES | YES | NONE |
| _require_default_years_window | YES | YES | NONE |
| _require_engine_defaults | YES | YES | NONE |
| _get_player_role | YES | YES | NONE |
| _compute_reference_date | YES | YES | NONE |
| _get_reference_date | YES | YES | NONE |
| _get_years_back | YES | YES | NONE |
| _get_tactical_threshold | YES | YES | NONE |
| _get_engine_default | YES | YES | NONE |
| get_active_squad | YES | YES | NONE |
| get_last_match_xi | YES | YES | NONE |
| get_squad_comparison_data | YES | YES | NONE |
| compare_squads | YES | YES | NONE |
| analyze_squad_types | YES | YES | NONE |
| get_matchups | NO | YES | P09-FLAG-01 |
| _generate_comparison_payload | YES | YES | NONE |
| _get_batting_milestones | YES | YES | NONE |
| get_player_profile | NO | NO | P09-FLAG-02, P09-FLAG-03 |
| analyze_player_profile | YES | YES | NONE |

### Flag List

[P09-FLAG-01] PRESENTATION_PURITY - `get_matchups` line 504:  
`UI_PLACEHOLDER` - `'Unknown'` fallback in `Style` column returned to API payload.  
Severity: HIGH  
Carry to: P10 violation summary

[P09-FLAG-02] PRESENTATION_PURITY - `get_player_profile` line 657:  
`UI_PLACEHOLDER` - `"N/A"` used for `best_figures` in returned bowling payload.  
Severity: MEDIUM  
Carry to: P10 violation summary

[P09-FLAG-03] PURE_PRIMITIVE - `get_player_profile` line 657:  
Missing-data branch returns presentation string `"N/A"` instead of null-style domain value.  
Severity: MEDIUM  
Carry to: P10 violation summary

### Overall Verdict

`VIOLATIONS FOUND - 3 total`
- Pattern breakdown: `UI_PLACEHOLDER=2`, `PURE_PRIMITIVE=1`
- Severity breakdown: `HIGH=1`, `MEDIUM=2`

---

## 6. Verification Checklist

- [x] Every function from P01 map is included in the summary table (24 total).
- [x] Logger strings are not flagged.
- [x] Exception message strings are not flagged.
- [x] Every flagged string is confirmed in a return-value chain.
- [x] No fix recommendations included.
- [x] Bouncer output matches P01 baseline.
