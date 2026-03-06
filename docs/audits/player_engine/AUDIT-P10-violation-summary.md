# AUDIT-P10 - Violation Summary & Refactor Register

**Task ID:** TASK-026 / P10  
**Audit Series:** Player Engine - Phase 10  
**Date:** 2026-03-05  
**Output file:** `docs/audits/player_engine/AUDIT-P10-violation-summary.md`

---

## 1. Baseline Bouncer

```text
PASS: 100% compliance across 22 file(s).
```

P01 baseline match: YES.

---

## 2. Step 3.1 - Master Violation Register

### Rule: MANDATE_1_IO

ID: P03-FLAG-01  
Source audit: P03  
Rule violated: MANDATE_1_IO  
Function: _compute_reference_date  
File: player_engine.py  
Severity: CRITICAL  
Fix type: ENGINE_CHANGE  
One-line description: Remove execute-path global logger access from `_compute_reference_date`.

ID: P03-FLAG-02  
Source audit: P03  
Rule violated: MANDATE_1_IO  
Function: _get_reference_date  
File: player_engine.py  
Severity: CRITICAL  
Fix type: ENGINE_CHANGE  
One-line description: Remove indirect logger side-effect chain via `_compute_reference_date`.

ID: P03-FLAG-03  
Source audit: P03  
Rule violated: MANDATE_1_IO  
Function: get_squad_comparison_data  
File: player_engine.py  
Severity: CRITICAL  
Fix type: ENGINE_CHANGE  
One-line description: Break indirect execute-path logger side-effect chain from reference-date call.

ID: P03-FLAG-04  
Source audit: P03  
Rule violated: MANDATE_1_IO  
Function: compare_squads  
File: player_engine.py  
Severity: CRITICAL  
Fix type: ENGINE_CHANGE  
One-line description: Remove delegated path that reaches logger side-effect chain.

ID: P03-FLAG-05  
Source audit: P03  
Rule violated: MANDATE_1_IO  
Function: analyze_squad_types  
File: player_engine.py  
Severity: CRITICAL  
Fix type: ENGINE_CHANGE  
One-line description: Remove indirect logger side-effect chain from reference-date dependency.

ID: P03-FLAG-06  
Source audit: P03  
Rule violated: MANDATE_1_IO  
Function: _generate_comparison_payload  
File: player_engine.py  
Severity: CRITICAL  
Fix type: ENGINE_CHANGE  
One-line description: Remove indirect logger side-effect chain from reference-date dependency.

ID: P03-FLAG-07  
Source audit: P03  
Rule violated: MANDATE_1_IO  
Function: get_player_profile  
File: player_engine.py  
Severity: CRITICAL  
Fix type: ENGINE_CHANGE  
One-line description: Remove indirect logger side-effect chain from reference-date dependency.

ID: P03-FLAG-08  
Source audit: P03  
Rule violated: MANDATE_1_IO  
Function: analyze_player_profile  
File: player_engine.py  
Severity: CRITICAL  
Fix type: ENGINE_CHANGE  
One-line description: Remove delegated path that reaches logger side-effect chain.

### Rule: MANDATE_1_SRP

ID: P03-FLAG-09  
Source audit: P03  
Rule violated: MANDATE_1_SRP  
Function: __init__  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Separate object setup responsibility from dataframe normalization responsibility.

ID: P03-FLAG-10  
Source audit: P03  
Rule violated: MANDATE_1_SRP  
Function: _require_tactical_thresholds  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Split rule-validation and value-normalization responsibilities.

ID: P03-FLAG-11  
Source audit: P03  
Rule violated: MANDATE_1_SRP  
Function: _require_default_years_window  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Split presence/range validation from type coercion responsibility.

ID: P03-FLAG-12  
Source audit: P03  
Rule violated: MANDATE_1_SRP  
Function: _require_engine_defaults  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Split map validation and map transformation responsibilities.

ID: P03-FLAG-13  
Source audit: P03  
Rule violated: MANDATE_1_SRP  
Function: _get_reference_date  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Separate cache-routing behavior from compute execution behavior.

ID: P03-FLAG-14  
Source audit: P03  
Rule violated: MANDATE_1_SRP  
Function: get_last_match_xi  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Remove mixed dual-source execution paths from one method body.

ID: P03-FLAG-15  
Source audit: P03  
Rule violated: MANDATE_1_SRP  
Function: get_squad_comparison_data  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Separate context-path routing from multi-step comparison orchestration.

ID: P03-FLAG-16  
Source audit: P03  
Rule violated: MANDATE_1_SRP  
Function: analyze_squad_types  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Separate context availability routing from tactical analysis execution.

ID: P03-FLAG-17  
Source audit: P03  
Rule violated: MANDATE_1_SRP  
Function: get_matchups  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Separate context availability routing from matchup computation execution.

ID: P03-FLAG-18  
Source audit: P03  
Rule violated: MANDATE_1_SRP  
Function: _generate_comparison_payload  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Separate orchestration of sub-analyses from payload composition.

ID: P03-FLAG-19  
Source audit: P03  
Rule violated: MANDATE_1_SRP  
Function: get_player_profile  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Separate baseline profile aggregation from optional raw-ball enrichment path.

ID: P03-FLAG-20  
Source audit: P03  
Rule violated: MANDATE_1_SRP  
Function: analyze_player_profile  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Separate existence gate routing from delegated profile execution.

### Rule: DUAL_DATA_PATH

ID: P07-REC-DUAL-PATH  
Source audit: P07  
Rule violated: DUAL_DATA_PATH  
Function: get_last_match_xi|get_player_profile|analyze_squad_types|get_matchups|get_squad_comparison_data  
File: player_engine.py  
Severity: HIGH  
Fix type: ARCHITECT_DECISION  
One-line description: Resolve dual-path pattern direction (standardize Group A, remove Group B) before refactor implementation.

ID: P03-FLAG-21  
Source audit: P03  
Rule violated: DUAL_DATA_PATH  
Function: get_last_match_xi  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ARCHITECT_DECISION  
One-line description: Method uses constructor squad path plus injected fallback reconstruction path.

ID: P03-FLAG-22  
Source audit: P03  
Rule violated: DUAL_DATA_PATH  
Function: get_squad_comparison_data  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ARCHITECT_DECISION  
One-line description: Optional `context_df` creates divergent empty-path vs compute-path behavior.

ID: P03-FLAG-23  
Source audit: P03  
Rule violated: DUAL_DATA_PATH  
Function: analyze_squad_types  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ARCHITECT_DECISION  
One-line description: Optional `context_df` creates early-empty path and full-compute path split.

ID: P03-FLAG-24  
Source audit: P03  
Rule violated: DUAL_DATA_PATH  
Function: get_matchups  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ARCHITECT_DECISION  
One-line description: Optional `context_df` creates early-empty path and full-compute path split.

ID: P03-FLAG-25  
Source audit: P03  
Rule violated: DUAL_DATA_PATH  
Function: get_player_profile  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ARCHITECT_DECISION  
One-line description: Baseline constructor-data path plus optional injected raw-ball enrichment path.

### Rule: MANDATE_3_ZERO_LITERAL

ID: P05-FLAG-01  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: get_last_match_xi  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register XI-size cutoff constant and replace hardcoded `11` usage.

ID: P05-FLAG-02  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: _get_batting_milestones  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register century threshold constant and replace hardcoded `100` usage.

ID: P05-FLAG-03  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: _get_batting_milestones  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register fifty lower-bound constant and replace hardcoded `50` usage.

ID: P05-FLAG-04  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: _get_batting_milestones  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register fifty upper-bound constant and replace hardcoded `100` usage.

ID: P05-FLAG-07  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: get_player_profile  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register bowling-inclusion gate constant and replace hardcoded `60` usage.

ID: P05-FLAG-09  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: get_player_profile  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register context token for `'vs_team'` and remove hardcoded filter literal.

ID: P05-FLAG-10  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: get_player_profile  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register role token for `'batting'` and remove hardcoded filter literal.

ID: P05-FLAG-11  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: get_player_profile  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register role token for `'bowling'` and remove hardcoded filter literal.

ID: P05-FLAG-12  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: get_player_profile  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register context token for `'at_venue'` and remove hardcoded filter literal.

ID: P05-FLAG-05  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: get_player_profile  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register default-years constant and remove hardcoded `10` default.

ID: P05-FLAG-06  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: analyze_player_profile  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register wrapper default-years constant and remove hardcoded `10` default.

ID: P05-FLAG-08  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: get_player_profile  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register rounding-precision constants and remove hardcoded precision `2` literals.

ID: P05-FLAG-13  
Source audit: P05  
Rule violated: MANDATE_3_ZERO_LITERAL  
Function: get_player_profile  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_AND_MANIFEST  
One-line description: Register opposition sentinel token for `'All'` and remove hardcoded branch literal.

### Rule: MANDATE_3_DERIVATIVE_LITERAL

ID: P05-FLAG-14  
Source audit: P05  
Rule violated: MANDATE_3_DERIVATIVE_LITERAL  
Function: get_matchups  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_CHANGE  
One-line description: Replace hardcoded `* 100` with manifest constant `SPORT_CONSTANTS.percent_scale`.

ID: P05-FLAG-15  
Source audit: P05  
Rule violated: MANDATE_3_DERIVATIVE_LITERAL  
Function: get_player_profile  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_CHANGE  
One-line description: Replace hardcoded strike-rate `* 100` operations with manifest percent-scale constant.

ID: P05-FLAG-16  
Source audit: P05  
Rule violated: MANDATE_3_DERIVATIVE_LITERAL  
Function: get_player_profile  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_CHANGE  
One-line description: Replace hardcoded economy `* 6` with manifest balls-per-over constant.

### Rule: ABC_CONTRACT

ID: P02-FLAG-01  
Source audit: P02  
Rule violated: ABC_CONTRACT  
Function: get_last_match_xi  
File: player_interface.py  
Severity: HIGH  
Fix type: ABC_CHANGE  
One-line description: Expand ABC signature to include optional injected fallback inputs used by engine.

ID: P02-FLAG-02  
Source audit: P02  
Rule violated: ABC_CONTRACT  
Function: get_squad_comparison_data  
File: player_interface.py  
Severity: HIGH  
Fix type: ABC_CHANGE  
One-line description: Expand ABC signature to include optional `context_df` expected by engine.

ID: P02-FLAG-03  
Source audit: P02  
Rule violated: ABC_CONTRACT  
Function: compare_squads  
File: player_interface.py  
Severity: HIGH  
Fix type: ABC_CHANGE  
One-line description: Align ABC parameter list with engine typed `recorder` and optional `context_df`.

ID: P02-FLAG-04  
Source audit: P02  
Rule violated: ABC_CONTRACT  
Function: analyze_squad_types  
File: player_interface.py  
Severity: HIGH  
Fix type: ABC_CHANGE  
One-line description: Align ABC return and parameter types with engine tactical analysis contract.

ID: P02-FLAG-05  
Source audit: P02  
Rule violated: ABC_CONTRACT  
Function: get_player_profile  
File: player_interface.py  
Severity: HIGH  
Fix type: ABC_CHANGE  
One-line description: Align ABC years typing and optional raw-ball enrichment parameter with engine.

ID: P02-FLAG-06  
Source audit: P02  
Rule violated: ABC_CONTRACT  
Function: get_matchups  
File: player_interface.py  
Severity: HIGH  
Fix type: ABC_CHANGE  
One-line description: Align ABC optional bowlers, keyword-only context inputs, and return contract with engine.

ID: P02-FLAG-07  
Source audit: P02  
Rule violated: ABC_CONTRACT  
Function: analyze_player_profile  
File: player_interface.py  
Severity: HIGH  
Fix type: ABC_CHANGE  
One-line description: Align ABC years typing and optional raw-ball enrichment parameter with engine.

ID: ABC-REC-01  
Source audit: P07  
Rule violated: ABC_CONTRACT  
Function: get_last_match_xi  
File: player_interface.py  
Severity: MEDIUM  
Fix type: ABC_CHANGE  
One-line description: Formalize fallback-context signature change in ABC contract.

ID: ABC-REC-02  
Source audit: P07  
Rule violated: ABC_CONTRACT  
Function: get_squad_comparison_data  
File: player_interface.py  
Severity: MEDIUM  
Fix type: ABC_CHANGE  
One-line description: Formalize `context_df` injection capability in ABC contract.

ID: ABC-REC-06  
Source audit: P07  
Rule violated: ABC_CONTRACT  
Function: get_player_profile  
File: player_interface.py  
Severity: MEDIUM  
Fix type: ABC_CHANGE  
One-line description: Formalize optional years and optional raw-ball parameter in ABC contract.

ID: ABC-REC-08  
Source audit: P07  
Rule violated: ABC_CONTRACT  
Function: analyze_player_profile  
File: player_interface.py  
Severity: MEDIUM  
Fix type: ABC_CHANGE  
One-line description: Formalize optional years and optional raw-ball parameter in ABC contract.

### Rule: MANDATE_4_ANTI_ANY

ID: ABC-REC-03  
Source audit: P07  
Rule violated: MANDATE_4_ANTI_ANY  
Function: compare_squads  
File: player_interface.py  
Severity: HIGH  
Fix type: ABC_CHANGE  
One-line description: Replace `recorder: Any` with typed `Optional[TacticalRecorderPort]` in ABC.

ID: ABC-REC-04  
Source audit: P07  
Rule violated: MANDATE_4_ANTI_ANY  
Function: analyze_squad_types  
File: player_interface.py  
Severity: HIGH  
Fix type: ABC_CHANGE  
One-line description: Replace `recorder: Any` with typed `Optional[TacticalRecorderPort]` in ABC.

ID: ABC-REC-05  
Source audit: P07  
Rule violated: MANDATE_4_ANTI_ANY  
Function: analyze_squad_types  
File: player_interface.py  
Severity: HIGH  
Fix type: ABC_CHANGE  
One-line description: Replace `List[Dict[str, Any]]` return with typed `List[DisplayRecord]` in ABC.

ID: ABC-REC-07  
Source audit: P07  
Rule violated: MANDATE_4_ANTI_ANY  
Function: get_matchups  
File: player_interface.py  
Severity: HIGH  
Fix type: ABC_CHANGE  
One-line description: Replace `List[Dict[str, Any]]` return with typed `List[DisplayRecord]` in ABC.

### Rule: STALE_TYPE

ID: P08-FLAG-01  
Source audit: P08  
Rule violated: STALE_TYPE  
Function: MatchupStats  
File: player_interface.py  
Severity: MEDIUM  
Fix type: ABC_CHANGE  
One-line description: Remove stale dataclass unused by engine signatures or engine bodies.

ID: P08-FLAG-02  
Source audit: P08  
Rule violated: STALE_TYPE  
Function: TacticalMatrixRow  
File: player_interface.py  
Severity: MEDIUM  
Fix type: ABC_CHANGE  
One-line description: Remove stale dataclass unused by engine signatures or engine bodies.

### Rule: PRESENTATION_PURITY

ID: P09-FLAG-01  
Source audit: P09  
Rule violated: PRESENTATION_PURITY  
Function: get_matchups  
File: player_engine.py  
Severity: HIGH  
Fix type: ENGINE_CHANGE  
One-line description: Remove UI placeholder fallback `'Unknown'` from return payload chain.

ID: P09-FLAG-02  
Source audit: P09  
Rule violated: PRESENTATION_PURITY  
Function: get_player_profile  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Remove UI placeholder string `"N/A"` from returned bowling profile path.

ID: P09-FLAG-03  
Source audit: P09  
Rule violated: PRESENTATION_PURITY  
Function: get_player_profile  
File: player_engine.py  
Severity: MEDIUM  
Fix type: ENGINE_CHANGE  
One-line description: Replace presentation string in missing-data branch with domain-null primitive behavior.

---

## 3. Step 3.2 - Architectural Decisions Block

ARCH-DEC-01: Standardise dual-path contract for Group A methods  
Methods: get_last_match_xi, get_player_profile  
Decision: Formalise constructor-data-primary + injection-enrichment  
          pattern in ABC with explicit docstrings  
Status: RECOMMENDED - pending architect sign-off

ARCH-DEC-02: Remove dead empty-return paths in Group B methods  
Methods: analyze_squad_types, get_matchups, get_squad_comparison_data  
Decision: Make context_df a required parameter. Remove [] / empty  
          default execution paths. All 19 caller files confirmed  
          passing context_df - no breaking changes.  
Status: RECOMMENDED - pending architect sign-off

Additional architectural decisions surfaced: NONE.

---

## 4. Step 3.3 - Refactor Scope Summary

REFACTOR SCOPE SUMMARY
======================
Files requiring changes:
  formats/odi/engines/player_engine.py - 45 violations
  core/interfaces/player_interface.py  - 17 ABC/type fixes
  formats/odi/manifest.py              - 13 additions required

Violation breakdown by rule:
  MANDATE_1_IO:               8  (single root source: _compute_reference_date logger chain)
  MANDATE_1_SRP:             12  (0 HIGH, 12 MEDIUM)
  DUAL_DATA_PATH:             6  (Group A: 2 standardise, Group B: 3 remove, +1 cross-cutting decision)
  MANDATE_3_ZERO_LITERAL:    13
  MANDATE_3_DERIVATIVE:       3  (all constants already present in manifest - engine ref swap only)
  ABC_CONTRACT:              11  (P02 mismatches + P07 signature formalisation)
  MANDATE_4_ANTI_ANY:         4  (ABC typing upgrades)
  STALE_TYPE:                 2
  PRESENTATION_PURITY:        3

Estimated fix complexity:
  MECHANICAL:  27 violations - direct type/signature swap, stale-type removal, or literal ref swap
  STRUCTURAL:  22 violations - decomposition/path removal or architecture-dependent execution routing
  ADDITIVE:    13 violations - manifest registrations required for zero-literal closure

Bouncer status at audit close: PASS - 0 violations
Expected bouncer delta after refactor: No expected net new violations at completion; transient ZERO_LITERAL failures are possible if engine and manifest edits are split across intermediate commits.

---

## 5. Step 3.4 - Known Intentional Patterns Check

KIP CANDIDATES FROM FULL AUDIT REVIEW: NONE

P07 KIP status reconfirmed: no intentional-pattern candidates across consolidated P02-P09 findings.

---

## 6. Verification

- [x] Every flag/recommendation from P02-P09 is represented exactly once (P02:7, P03:25, P04:0, P05:16, P06:0, P07:9, P08:2, P09:3).
- [x] No new source-code findings were introduced in P10 synthesis.
- [x] Both required ARCH-DEC entries are present.
- [x] Refactor scope summary includes concrete numeric counts.
- [x] Bouncer output confirms match with P01 baseline.
