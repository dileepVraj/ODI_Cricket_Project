# AUDIT-P03 - Player Engine Mandate 1: I/O Air-Gap + SRP Sweep

**Task ID:** TASK-026 / P03  
**Audit Series:** Player Engine - Phase 10  
**Date:** 2026-03-05  
**Depends on:**
- `docs/audits/player_engine/AUDIT-P01-structural-map.md`
- `docs/audits/player_engine/AUDIT-P02-interface-contract-precheck.md`  
**Output File:** `docs/audits/player_engine/AUDIT-P03-mandate1-io-srp.md`

---

## 1. Read First Confirmation

Completed in order:
1. `docs/guides/ENGINEERING_STANDARDS_BACKEND.md` (Part 0: Mandate 1 + Mandate 2)
2. `docs/ai/SESSION_STATE.md`
3. `docs/audits/player_engine/AUDIT-P01-structural-map.md`
4. `docs/audits/player_engine/AUDIT-P02-interface-contract-precheck.md`
5. `formats/odi/engines/player_engine.py` (full file, top-to-bottom)

---

## 2. Baseline Bouncer

```text
PASS: 100% compliance across 22 file(s).
```

P01 baseline match: YES.

---

## 3. Task Steps

### SWEEP A - I/O Air-Gap (Mandate 1 + Mandate 2)

Function: __init__
I/O Clean: YES

Function: _require_nonempty_dict_rule
I/O Clean: YES

Function: _require_tactical_thresholds
I/O Clean: YES

Function: _require_style_map
I/O Clean: YES

Function: _require_player_roles
I/O Clean: YES

Function: _require_default_player_role
I/O Clean: YES

Function: _require_default_years_window
I/O Clean: YES

Function: _require_engine_defaults
I/O Clean: YES

Function: _get_player_role
I/O Clean: YES

Function: _compute_reference_date
I/O Clean: NO
If NO - violation type: GLOBAL_STATE
If NO - detail: Line 145 calls `logger.debug(...)`, which accesses module-level `logger` global state during function execution.
If NO - indirect chain: NONE

Function: _get_reference_date
I/O Clean: NO
If NO - violation type: INDIRECT_VIA_CALL
If NO - detail: Line 150 calls `_compute_reference_date()`, which accesses module-level global logger at line 145.
If NO - indirect chain: `_get_reference_date()` -> `_compute_reference_date()` -> `logger.debug(...)`

Function: _get_years_back
I/O Clean: YES

Function: _get_tactical_threshold
I/O Clean: YES

Function: _get_engine_default
I/O Clean: YES

Function: get_active_squad
I/O Clean: YES

Function: get_last_match_xi
I/O Clean: YES

Function: get_squad_comparison_data
I/O Clean: NO
If NO - violation type: INDIRECT_VIA_CALL
If NO - detail: Line 264 calls `_get_reference_date()`, which reaches global logger access through `_compute_reference_date()` line 145.
If NO - indirect chain: `get_squad_comparison_data()` -> `_get_reference_date()` -> `_compute_reference_date()` -> `logger.debug(...)`

Function: compare_squads
I/O Clean: NO
If NO - violation type: INDIRECT_VIA_CALL
If NO - detail: Line 349 delegates to `get_squad_comparison_data()`, which reaches global logger access through `_get_reference_date()` and `_compute_reference_date()`.
If NO - indirect chain: `compare_squads()` -> `get_squad_comparison_data()` -> `_get_reference_date()` -> `_compute_reference_date()` -> `logger.debug(...)`

Function: analyze_squad_types
I/O Clean: NO
If NO - violation type: INDIRECT_VIA_CALL
If NO - detail: Line 374 calls `_get_reference_date()`, which reaches global logger access through `_compute_reference_date()` line 145.
If NO - indirect chain: `analyze_squad_types()` -> `_get_reference_date()` -> `_compute_reference_date()` -> `logger.debug(...)`

Function: get_matchups
I/O Clean: YES

Function: _generate_comparison_payload
I/O Clean: NO
If NO - violation type: INDIRECT_VIA_CALL
If NO - detail: Line 548 calls `_get_reference_date()`, which reaches global logger access through `_compute_reference_date()` line 145.
If NO - indirect chain: `_generate_comparison_payload()` -> `_get_reference_date()` -> `_compute_reference_date()` -> `logger.debug(...)`

Function: _get_batting_milestones
I/O Clean: YES

Function: get_player_profile
I/O Clean: NO
If NO - violation type: INDIRECT_VIA_CALL
If NO - detail: Line 622 calls `_get_reference_date()`, which reaches global logger access through `_compute_reference_date()` line 145.
If NO - indirect chain: `get_player_profile()` -> `_get_reference_date()` -> `_compute_reference_date()` -> `logger.debug(...)`

Function: analyze_player_profile
I/O Clean: NO
If NO - violation type: INDIRECT_VIA_CALL
If NO - detail: Line 704 delegates to `get_player_profile()`, which reaches global logger access through `_get_reference_date()` and `_compute_reference_date()`.
If NO - indirect chain: `analyze_player_profile()` -> `get_player_profile()` -> `_get_reference_date()` -> `_compute_reference_date()` -> `logger.debug(...)`

### SWEEP B - SRP (Single Responsibility - Mandate 1)

Function: __init__
SRP Clean: NO
If NO - violation type: VALIDATE_AND_TRANSFORM
If NO - detail: Initializes rule/service dependencies and also transforms `squads_df['match_id']` dtype.
If NO - severity: MEDIUM

Function: _require_nonempty_dict_rule
SRP Clean: YES

Function: _require_tactical_thresholds
SRP Clean: NO
If NO - violation type: VALIDATE_AND_TRANSFORM
If NO - detail: Validates the required rule exists and also normalizes every threshold value into ints.
If NO - severity: MEDIUM

Function: _require_style_map
SRP Clean: YES

Function: _require_player_roles
SRP Clean: YES

Function: _require_default_player_role
SRP Clean: YES

Function: _require_default_years_window
SRP Clean: NO
If NO - violation type: VALIDATE_AND_TRANSFORM
If NO - detail: Validates presence/range of the setting and also coerces it to integer output.
If NO - severity: MEDIUM

Function: _require_engine_defaults
SRP Clean: NO
If NO - violation type: VALIDATE_AND_TRANSFORM
If NO - detail: Validates engine-default rule structure and also normalizes values to ints.
If NO - severity: MEDIUM

Function: _get_player_role
SRP Clean: YES

Function: _compute_reference_date
SRP Clean: YES

Function: _get_reference_date
SRP Clean: NO
If NO - violation type: ROUTE_AND_EXECUTE
If NO - detail: Routes based on cache presence and executes date computation path when cache is absent.
If NO - severity: MEDIUM

Function: _get_years_back
SRP Clean: YES

Function: _get_tactical_threshold
SRP Clean: YES

Function: _get_engine_default
SRP Clean: YES

Function: get_active_squad
SRP Clean: YES

Function: get_last_match_xi
SRP Clean: NO
If NO - violation type: DUAL_DATA_PATH
If NO - detail: Uses `self.squads_df` preferred path and an alternate injected `team_matches`/`match_balls_df` path with different execution flow.
If NO - severity: MEDIUM

Function: get_squad_comparison_data
SRP Clean: NO
If NO - violation type: DUAL_DATA_PATH
If NO - detail: Accepts optional `context_df` and runs different data-input behavior when context is absent versus provided.
If NO - severity: MEDIUM

Function: compare_squads
SRP Clean: YES

Function: analyze_squad_types
SRP Clean: NO
If NO - violation type: DUAL_DATA_PATH
If NO - detail: Accepts optional `context_df` and short-circuits on one path while running tactical-analysis pipeline on the other.
If NO - severity: MEDIUM

Function: get_matchups
SRP Clean: NO
If NO - violation type: DUAL_DATA_PATH
If NO - detail: Accepts optional `context_df` and returns early without computation in one path while running matchup computation in the other.
If NO - severity: MEDIUM

Function: _generate_comparison_payload
SRP Clean: NO
If NO - violation type: ORCHESTRATE_AND_CALCULATE
If NO - detail: Builds context filters and coordinates metrics/matrix/matchup calculations before payload assembly.
If NO - severity: MEDIUM

Function: _get_batting_milestones
SRP Clean: YES

Function: get_player_profile
SRP Clean: NO
If NO - violation type: DUAL_DATA_PATH
If NO - detail: Uses internal `self.player_df` as base data and conditionally executes additional raw-ball milestone path via optional `raw_balls_df`.
If NO - severity: MEDIUM

Function: analyze_player_profile
SRP Clean: NO
If NO - violation type: ROUTE_AND_EXECUTE
If NO - detail: Performs existence gating on internal player index and then delegates full profile execution.
If NO - severity: MEDIUM

### SWEEP C - Consolidated Findings

| Function | I/O Clean | SRP Clean | Flags |
|---|---|---|---|
| __init__ | YES | NO | P03-FLAG-09 |
| _require_nonempty_dict_rule | YES | YES | NONE |
| _require_tactical_thresholds | YES | NO | P03-FLAG-10 |
| _require_style_map | YES | YES | NONE |
| _require_player_roles | YES | YES | NONE |
| _require_default_player_role | YES | YES | NONE |
| _require_default_years_window | YES | NO | P03-FLAG-11 |
| _require_engine_defaults | YES | NO | P03-FLAG-12 |
| _get_player_role | YES | YES | NONE |
| _compute_reference_date | NO | YES | P03-FLAG-01 |
| _get_reference_date | NO | NO | P03-FLAG-02, P03-FLAG-13 |
| _get_years_back | YES | YES | NONE |
| _get_tactical_threshold | YES | YES | NONE |
| _get_engine_default | YES | YES | NONE |
| get_active_squad | YES | YES | NONE |
| get_last_match_xi | YES | NO | P03-FLAG-14, P03-FLAG-21 |
| get_squad_comparison_data | NO | NO | P03-FLAG-03, P03-FLAG-15, P03-FLAG-22 |
| compare_squads | NO | YES | P03-FLAG-04 |
| analyze_squad_types | NO | NO | P03-FLAG-05, P03-FLAG-16, P03-FLAG-23 |
| get_matchups | YES | NO | P03-FLAG-17, P03-FLAG-24 |
| _generate_comparison_payload | NO | NO | P03-FLAG-06, P03-FLAG-18 |
| _get_batting_milestones | YES | YES | NONE |
| get_player_profile | NO | NO | P03-FLAG-07, P03-FLAG-19, P03-FLAG-25 |
| analyze_player_profile | NO | NO | P03-FLAG-08, P03-FLAG-20 |

[P03-FLAG-01] I/O VIOLATION - `_compute_reference_date`: accesses module-level `logger` via `logger.debug(...)`.
Carry to: P10 violation summary

[P03-FLAG-02] I/O VIOLATION - `_get_reference_date`: indirect global-state access through `_compute_reference_date()` logger path.
Carry to: P10 violation summary

[P03-FLAG-03] I/O VIOLATION - `get_squad_comparison_data`: indirect global-state access through `_get_reference_date()` -> `_compute_reference_date()`.
Carry to: P10 violation summary

[P03-FLAG-04] I/O VIOLATION - `compare_squads`: indirect global-state access through `get_squad_comparison_data()` chain.
Carry to: P10 violation summary

[P03-FLAG-05] I/O VIOLATION - `analyze_squad_types`: indirect global-state access through `_get_reference_date()` chain.
Carry to: P10 violation summary

[P03-FLAG-06] I/O VIOLATION - `_generate_comparison_payload`: indirect global-state access through `_get_reference_date()` chain.
Carry to: P10 violation summary

[P03-FLAG-07] I/O VIOLATION - `get_player_profile`: indirect global-state access through `_get_reference_date()` chain.
Carry to: P10 violation summary

[P03-FLAG-08] I/O VIOLATION - `analyze_player_profile`: indirect global-state access through `get_player_profile()` chain.
Carry to: P10 violation summary

[P03-FLAG-09] SRP VIOLATION - `__init__`: combines object setup with dataframe normalization.
Carry to: P10 violation summary

[P03-FLAG-10] SRP VIOLATION - `_require_tactical_thresholds`: validates rule presence and transforms values.
Carry to: P10 violation summary

[P03-FLAG-11] SRP VIOLATION - `_require_default_years_window`: validates and coerces default-years rule.
Carry to: P10 violation summary

[P03-FLAG-12] SRP VIOLATION - `_require_engine_defaults`: validates and normalizes engine default map.
Carry to: P10 violation summary

[P03-FLAG-13] SRP VIOLATION - `_get_reference_date`: performs route-by-cache and executes compute path.
Carry to: P10 violation summary

[P03-FLAG-14] SRP VIOLATION - `get_last_match_xi`: contains two distinct data-source execution paths.
Carry to: P10 violation summary

[P03-FLAG-15] SRP VIOLATION - `get_squad_comparison_data`: routes by context input and orchestrates multi-step analysis assembly.
Carry to: P10 violation summary

[P03-FLAG-16] SRP VIOLATION - `analyze_squad_types`: routes by context availability and executes tactical analysis pipeline.
Carry to: P10 violation summary

[P03-FLAG-17] SRP VIOLATION - `get_matchups`: routes by context availability and executes matchup aggregation pipeline.
Carry to: P10 violation summary

[P03-FLAG-18] SRP VIOLATION - `_generate_comparison_payload`: orchestrates multiple analysis branches and payload composition.
Carry to: P10 violation summary

[P03-FLAG-19] SRP VIOLATION - `get_player_profile`: merges baseline profile aggregation with optional raw-ball enrichment path.
Carry to: P10 violation summary

[P03-FLAG-20] SRP VIOLATION - `analyze_player_profile`: performs routing guard and delegates profile execution.
Carry to: P10 violation summary

[P03-FLAG-21] DUAL_DATA_PATH - `get_last_match_xi`: uses `self.squads_df` plus injected `team_matches`/`match_balls_df` fallback path.
Carry to: P07 for architectural decision

[P03-FLAG-22] DUAL_DATA_PATH - `get_squad_comparison_data`: optional `context_df` drives alternate input path behavior.
Carry to: P07 for architectural decision

[P03-FLAG-23] DUAL_DATA_PATH - `analyze_squad_types`: optional `context_df` path returns early when absent and computes when present.
Carry to: P07 for architectural decision

[P03-FLAG-24] DUAL_DATA_PATH - `get_matchups`: optional `context_df` path returns early when absent and computes when present.
Carry to: P07 for architectural decision

[P03-FLAG-25] DUAL_DATA_PATH - `get_player_profile`: combines internal `self.player_df` path with optional `raw_balls_df` enrichment path.
Carry to: P07 for architectural decision

---

## 4. Verification

- [x] Every function from P01 map has entries in Sweep A and Sweep B (24/24).
- [x] Every INDIRECT_VIA_CALL finding includes full call chain trace.
- [x] Every DUAL_DATA_PATH flag is marked carry to P07.
- [x] No fix recommendations appear in this report.
- [x] Bouncer output confirms match with P01 baseline.
