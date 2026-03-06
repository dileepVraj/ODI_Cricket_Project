# AUDIT-P05 - Mandate 3: Literals Sweep

**Task ID:** TASK-026 / P05  
**Audit Series:** Player Engine - Phase 10  
**Date:** 2026-03-05  
**File Audited:** `formats/odi/engines/player_engine.py`  
**Depends on:** `docs/audits/player_engine/AUDIT-P01-structural-map.md`  

---

## 1. Read First Confirmation

Read in full before Step 2:
1. `docs/guides/ENGINEERING_STANDARDS_BACKEND.md` (Mandate 3 + Zero-Literal + Derivative Literal sections)
2. `docs/ai/SESSION_STATE.md`
3. `formats/odi/manifest.py`
4. `docs/audits/player_engine/AUDIT-P01-structural-map.md`
5. `formats/odi/engines/player_engine.py`

---

## 2. Baseline Bouncer

```text
PASS: 100% compliance across 22 file(s).
```

Baseline check against P01 baseline: **MATCH (YES)**.

---

## 3. Sweep A - Zero-Literal Law Findings

Function: `get_last_match_xi`  
Line: 235  
Literal: `11`  
Context: Hard cap for squad extraction completeness (`len(squad) >= 11`).  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

Function: `_get_batting_milestones`  
Line: 602  
Literal: `100`  
Context: Century threshold in milestone classification.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

Function: `_get_batting_milestones`  
Line: 603  
Literal: `50`  
Context: Fifty threshold lower bound in milestone classification.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

Function: `_get_batting_milestones`  
Line: 603  
Literal: `100`  
Context: Fifty band upper bound in milestone classification.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 612  
Literal: `10`  
Context: Default years window in method signature.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: MEDIUM

Function: `analyze_player_profile`  
Line: 694  
Literal: `10`  
Context: Default years window in wrapper method signature.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: MEDIUM

Function: `get_player_profile`  
Line: 654  
Literal: `60`  
Context: Bowling-stat inclusion threshold gate (`b_balls > 60`).  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 633  
Literal: `2`  
Context: Hardcoded batting average precision rounding.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: MEDIUM

Function: `get_player_profile`  
Line: 655  
Literal: `2`  
Context: Hardcoded bowling average precision rounding.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: MEDIUM

Function: `get_player_profile`  
Line: 656  
Literal: `2`  
Context: Hardcoded bowling economy precision rounding.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: MEDIUM

Function: `get_player_profile`  
Line: 666  
Literal: `2`  
Context: Hardcoded opposition-context average precision rounding.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: MEDIUM

Function: `get_player_profile`  
Line: 676  
Literal: `2`  
Context: Hardcoded venue-context average precision rounding.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: MEDIUM

Function: `get_player_profile`  
Line: 626  
Literal: `'vs_team'`  
Context: Hardcoded context category filter key in batting slice.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 626  
Literal: `'batting'`  
Context: Hardcoded role category filter key in batting slice.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 648  
Literal: `'vs_team'`  
Context: Hardcoded context category filter key in bowling slice.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 648  
Literal: `'bowling'`  
Context: Hardcoded role category filter key in bowling slice.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 661  
Literal: `'All'`  
Context: Hardcoded opposition sentinel branch control.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: MEDIUM

Function: `get_player_profile`  
Line: 663  
Literal: `'vs_team'`  
Context: Hardcoded context category filter key in opponent slice.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 663  
Literal: `'batting'`  
Context: Hardcoded role category filter key in opponent slice.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 673  
Literal: `'at_venue'`  
Context: Hardcoded venue context category filter key.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 673  
Literal: `'batting'`  
Context: Hardcoded role category filter key in venue slice.  
In manifest.py: NO  
Violation type: ZERO_LITERAL  
Severity: HIGH

---

## 4. Sweep B - Derivative Literal Law Findings

Function: `get_matchups`  
Line: 522  
Literal: `* 100`  
Context: Strike-rate scale multiplier applied directly in calculation.  
In manifest.py: YES  
Named constant: `SPORT_CONSTANTS.percent_scale`  
Violation type: DERIVATIVE_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 634  
Literal: `* 100`  
Context: Career batting strike-rate scale multiplier applied directly.  
In manifest.py: YES  
Named constant: `SPORT_CONSTANTS.percent_scale`  
Violation type: DERIVATIVE_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 656  
Literal: `* 6`  
Context: Economy conversion coefficient (balls-to-over scale) applied directly.  
In manifest.py: YES  
Named constant: `SPORT_CONSTANTS.balls_per_over`  
Violation type: DERIVATIVE_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 666  
Literal: `* 100`  
Context: Opposition-context strike-rate scale multiplier applied directly.  
In manifest.py: YES  
Named constant: `SPORT_CONSTANTS.percent_scale`  
Violation type: DERIVATIVE_LITERAL  
Severity: HIGH

Function: `get_player_profile`  
Line: 676  
Literal: `* 100`  
Context: Venue-context strike-rate scale multiplier applied directly.  
In manifest.py: YES  
Named constant: `SPORT_CONSTANTS.percent_scale`  
Violation type: DERIVATIVE_LITERAL  
Severity: HIGH

---

## 5. Sweep C - Consolidation

### 5.1 Summary Table

| Function | Line | Literal | In Manifest | Violation Type | Severity |
|---|---|---|---|---|---|
| get_last_match_xi | 235 | 11 | NO | ZERO_LITERAL | HIGH |
| _get_batting_milestones | 602 | 100 | NO | ZERO_LITERAL | HIGH |
| _get_batting_milestones | 603 | 50 | NO | ZERO_LITERAL | HIGH |
| _get_batting_milestones | 603 | 100 | NO | ZERO_LITERAL | HIGH |
| get_player_profile | 612 | 10 | NO | ZERO_LITERAL | MEDIUM |
| analyze_player_profile | 694 | 10 | NO | ZERO_LITERAL | MEDIUM |
| get_player_profile | 654 | 60 | NO | ZERO_LITERAL | HIGH |
| get_player_profile | 633 | 2 | NO | ZERO_LITERAL | MEDIUM |
| get_player_profile | 655 | 2 | NO | ZERO_LITERAL | MEDIUM |
| get_player_profile | 656 | 2 | NO | ZERO_LITERAL | MEDIUM |
| get_player_profile | 666 | 2 | NO | ZERO_LITERAL | MEDIUM |
| get_player_profile | 676 | 2 | NO | ZERO_LITERAL | MEDIUM |
| get_player_profile | 626 | 'vs_team' | NO | ZERO_LITERAL | HIGH |
| get_player_profile | 626 | 'batting' | NO | ZERO_LITERAL | HIGH |
| get_player_profile | 648 | 'vs_team' | NO | ZERO_LITERAL | HIGH |
| get_player_profile | 648 | 'bowling' | NO | ZERO_LITERAL | HIGH |
| get_player_profile | 661 | 'All' | NO | ZERO_LITERAL | MEDIUM |
| get_player_profile | 663 | 'vs_team' | NO | ZERO_LITERAL | HIGH |
| get_player_profile | 663 | 'batting' | NO | ZERO_LITERAL | HIGH |
| get_player_profile | 673 | 'at_venue' | NO | ZERO_LITERAL | HIGH |
| get_player_profile | 673 | 'batting' | NO | ZERO_LITERAL | HIGH |
| get_matchups | 522 | * 100 | YES (`SPORT_CONSTANTS.percent_scale`) | DERIVATIVE_LITERAL | HIGH |
| get_player_profile | 634 | * 100 | YES (`SPORT_CONSTANTS.percent_scale`) | DERIVATIVE_LITERAL | HIGH |
| get_player_profile | 656 | * 6 | YES (`SPORT_CONSTANTS.balls_per_over`) | DERIVATIVE_LITERAL | HIGH |
| get_player_profile | 666 | * 100 | YES (`SPORT_CONSTANTS.percent_scale`) | DERIVATIVE_LITERAL | HIGH |
| get_player_profile | 676 | * 100 | YES (`SPORT_CONSTANTS.percent_scale`) | DERIVATIVE_LITERAL | HIGH |

### 5.2 Flag List

[P05-FLAG-01] ZERO_LITERAL - `get_last_match_xi` line 235: literal `11` controls XI-size stop condition. Carry to: P10 violation summary  
[P05-FLAG-02] ZERO_LITERAL - `_get_batting_milestones` line 602: literal `100` used as century cutoff. Carry to: P10 violation summary  
[P05-FLAG-03] ZERO_LITERAL - `_get_batting_milestones` line 603: literal `50` used as fifty lower bound. Carry to: P10 violation summary  
[P05-FLAG-04] ZERO_LITERAL - `_get_batting_milestones` line 603: literal `100` used as fifty upper bound. Carry to: P10 violation summary  
[P05-FLAG-05] ZERO_LITERAL - `get_player_profile` line 612: literal `10` as default years window. Carry to: P10 violation summary  
[P05-FLAG-06] ZERO_LITERAL - `analyze_player_profile` line 694: literal `10` as default years window. Carry to: P10 violation summary  
[P05-FLAG-07] ZERO_LITERAL - `get_player_profile` line 654: literal `60` gates bowling output inclusion. Carry to: P10 violation summary  
[P05-FLAG-08] ZERO_LITERAL - `get_player_profile` lines 633/655/656/666/676: literal `2` used for hardcoded rounding precision. Carry to: P10 violation summary  
[P05-FLAG-09] ZERO_LITERAL - `get_player_profile` lines 626/648/663: literal `'vs_team'` used as hardcoded context filter key. Carry to: P10 violation summary  
[P05-FLAG-10] ZERO_LITERAL - `get_player_profile` lines 626/663/673: literal `'batting'` used as hardcoded role filter key. Carry to: P10 violation summary  
[P05-FLAG-11] ZERO_LITERAL - `get_player_profile` line 648: literal `'bowling'` used as hardcoded role filter key. Carry to: P10 violation summary  
[P05-FLAG-12] ZERO_LITERAL - `get_player_profile` line 673: literal `'at_venue'` used as hardcoded context filter key. Carry to: P10 violation summary  
[P05-FLAG-13] ZERO_LITERAL - `get_player_profile` line 661: literal `'All'` used as hardcoded sentinel branch key. Carry to: P10 violation summary  
[P05-FLAG-14] DERIVATIVE_LITERAL - `get_matchups` line 522: `* 100` strike-rate coefficient is hardcoded. Carry to: P10 violation summary  
[P05-FLAG-15] DERIVATIVE_LITERAL - `get_player_profile` lines 634/666/676: `* 100` strike-rate coefficient is hardcoded. Carry to: P10 violation summary  
[P05-FLAG-16] DERIVATIVE_LITERAL - `get_player_profile` line 656: `* 6` economy coefficient is hardcoded. Carry to: P10 violation summary

### 5.3 Overall Verdict

**VIOLATIONS FOUND - 26 total**  
- ZERO_LITERAL: 21 (HIGH: 13, MEDIUM: 8)  
- DERIVATIVE_LITERAL: 5 (HIGH: 5, MEDIUM: 0)

---

## 6. Verification

- [x] Every function from P01 map (24 total) reviewed in Sweep A and Sweep B.
- [x] Every numeric literal not `0`, `1`, or `0.0` was assessed against `manifest.py`.
- [x] No fix recommendations included (violations/flags only).
- [x] Bouncer output matches P01 baseline.

