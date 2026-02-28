# ODI Data Integrity and Region H2H Hardening Plan

**Date:** 2026-02-20  
**Status:** Design Complete - Ready for Implementation  
**Owner:** Data/Platform + ODI Engine Layer  
**Primary Scope:** Prevent data loss and data-shape drift after CSV -> DuckDB migration, and enforce deterministic Region (Continent) Home-vs-Away behavior.

## 1. Why This Plan Exists

We have already seen production-facing symptoms after migration from CSV-backed logic to DuckDB-backed logic:

1. Region/continent stats dropped a valid Asia match (`match_id=1384416`, Bangalore, India) for `Sri Lanka vs England`.
2. Region Home-vs-Away output contract drifted between matrix-style and high-fidelity card-style behavior.
3. Pipeline still has integrity risks (silent extraction failure path, destructive DB rebuild path, incomplete venue canonicalization).

This plan defines the full hardening work so the same class of issue cannot repeat for other teams, venues, or regions.

## 2. Root Cause Summary (Confirmed)

### Incident A: Missing Bangalore match in Asia filter

Root cause:
- Region filters previously depended mainly on `venue_id` prefix matching (`IND_`, `SL_`, etc.).
- One valid Asia row had `matches.venue='IND_BANGALORE'` but `matches.venue_id IS NULL` after migration.
- Strict `venue_id` prefix filters excluded that row.

Why this happened post-migration:
- CSV-era logic tolerated raw venue labels more directly.
- DB migration introduced stronger dependence on canonical `venue_id`, but canonicalization coverage was incomplete.

### Incident B: Home-vs-Away region behavior drift

Root cause:
- `analyze_continent_performance` had mixed output semantics.
- `Home vs Away` and `Home vs All` paths were not explicitly separated as a stable output contract.

## 3. Non-Negotiable Architecture Constraints

This implementation must comply with:

1. `docs/ai/AI_ARCHITECTURAL_MANIFESTO.md`
2. `docs/guides/ENGINEERING_STANDARDS.md`

Specifically:
- Engines remain headless and return pure data.
- No direct DB access from engine methods; DB access remains in DAL/pipeline layers.
- Fail-fast behavior for integrity faults (no silent swallow paths).
- Vectorized or SQL-based checks over row loops.

## 4. Scope

### In Scope

1. ETL integrity hardening for ODI pipeline (`json_converter -> refinery -> ingest_to_db -> verification`).
2. Venue canonicalization and unresolved-venue governance in DuckDB load path.
3. Region filter invariants to prevent missing matches when `venue_id` is null.
4. Output contract enforcement:
- `Home vs Away in Region`: High-Fidelity Match Card format.
- `Home vs All in Region`: existing matrix behavior unchanged.
5. Test + audit gates to prevent recurrence across all teams/regions.

### Out of Scope (This Phase)

1. Full cross-format rollout (T20I/WODI/WT20I/IPL).
2. Rewriting all historical venue ontology with external data provider.
3. Replacing entire UI renderer stack.

## 5. Current Pipeline Map (As-Is)

Execution entrypoint:
- `scripts/maintenance/update_data.py`

Current stage mapping:
1. Stage 1: `formats/odi/utils/json_converter.py::run_json_conversion`
2. Stage 2: `formats/odi/utils/refinery_script.py::rebuild_intelligence_layer`
3. Stage 3: `formats/odi/utils/ingest_to_db.py::run_db_ingestion`
4. Stage 4: Truth Bridge verification

Current persistent tables in DuckDB:
1. `balls`
2. `matches`
3. `player_stats`
4. `phase_stats`
5. `player_metadata`
6. `squads`

## 6. Target End State

At completion, the system must satisfy all of the following:

1. No silent source-file drops during extraction.
2. Atomic DB replacement (no destructive delete-before-success).
3. Deterministic region inclusion even when `venue_id` is missing.
4. Enforced contract for region outputs:
- `Home vs Away`: high-fidelity card payload.
- `Home vs All`: matrix payload.
5. Automated integrity gates block pipeline promotion when checks fail.
6. Evidence artifacts are generated each run (audit JSON/CSV + summary logs).

## 7. Data Contracts (Hard Rules)

### 7.1 `balls` Contract

Required fields:
- `match_id`, `innings`, `over_num`, `ball_rank`, `ball`, `batting_team`, `bowling_team`, `runs_off_bat`, `extras`

Identity rule:
- Delivery identity is `(match_id, innings, over_num, ball_rank)`.
- `ball` is display-only, not identity.

### 7.2 `matches` Contract

Required fields:
- `match_id`, `start_date`, `venue`, `venue_id`, `team_bat_1`, `team_bat_2`, `winner`

Integrity rule:
- One row per `match_id`.
- For declared-result matches, innings summary fields must be structurally complete.

### 7.3 Cross-Table Contract

1. Every `matches.match_id` must exist in `balls`.
2. Every `balls.match_id` must exist in `matches`.
3. Region inclusion logic must not rely on only one venue representation column.

### 7.4 Region Output Contract

1. If `opp_team != 'All'`: return metric-row report compatible with high-fidelity card.
2. If `opp_team == 'All'`: return matrix rows (`Opponent`, `Mat`, etc.) unchanged.
3. Last-5 form must be based on newest matches by date (deterministic sort).

## 8. Detailed Implementation Phases

## Phase 0 - Baseline, Freeze, and Repro Artifacts

Goal:
- Lock current behavior and capture reproducible evidence before additional refactors.

Files:
1. `scripts/maintenance/etl_reconciliation_report.py` (new)
2. `scripts/maintenance/continent_coverage_audit.py` (new)
3. `docs/reports/` outputs

Actions:
1. Generate baseline counts:
- row counts by table
- distinct `match_id` parity between `balls`/`matches`
- unresolved `matches.venue_id` count and ratio
2. Generate continent pair audit for top team pairs + all regions.
3. Persist baseline artifacts with timestamp.

Acceptance:
1. Baseline report generated and stored.
2. Bangalore gap case recorded as baseline defect evidence.

## Phase 1 - Extraction Hardening (No Silent Drops)

Goal:
- Remove hidden data loss at source conversion.

Files:
1. `formats/odi/utils/json_converter.py`
2. `scripts/maintenance/update_data.py`

Actions:
1. Replace broad `except Exception: continue` with structured error collection.
2. Add strict mode (default): any file parse failure fails stage.
3. Add optional `--allow-partial` mode for non-production diagnosis only.
4. Emit conversion audit artifact with:
- files discovered
- files processed
- files failed
- per-file row counts
- exception metadata

Acceptance:
1. Corrupted JSON in strict mode causes non-zero exit.
2. Audit report is generated every run.

## Phase 2 - Delivery Identity Hardening

Goal:
- Eliminate float-key ambiguity risks.

Files:
1. `formats/odi/utils/json_converter.py`
2. `formats/odi/utils/refinery_script.py`
3. `formats/odi/utils/ingest_to_db.py`
4. `core/data_access.py` (compatibility validation only)

Actions:
1. Ensure `over_num` and `ball_rank` are persisted and loaded end-to-end.
2. Keep `ball` as convenience/display field only.
3. Add validation query to detect duplicates on `(match_id, innings, over_num, ball_rank)`.
4. Fail ingestion if duplicate delivery identities remain.

Acceptance:
1. Duplicate identity count is zero on canonical key.
2. Existing analysis functions continue to run with no contract break.

## Phase 3 - Atomic DuckDB Load

Goal:
- Prevent target DB destruction on partial failures.

Files:
1. `formats/odi/utils/ingest_to_db.py`

Actions:
1. Replace delete-rebuild flow with temp-build flow:
- build `odi.tmp.duckdb`
- run schema + reconciliation checks
- atomic rename swap to `odi.duckdb`
2. Keep rollback copy (`odi.prev.duckdb`) during cutover.
3. If validation fails, do not touch active DB.

Acceptance:
1. Simulated stage failure leaves active DB unchanged.
2. Successful run atomically replaces DB.

## Phase 4 - Venue Canonicalization Governance

Goal:
- Prevent region/host-country exclusion from incomplete `venue_id` mapping.

Files:
1. `config/shared/venues.py`
2. `formats/odi/utils/ingest_to_db.py`
3. `scripts/maintenance/backfill_match_venue_ids.py`
4. `scripts/maintenance/venue_mapping_gap_report.py` (new)

Actions:
1. Keep deterministic backfill during ingestion for null/blank `venue_id`.
2. Add unresolved-venue report with frequency ranking.
3. Expand aliases by highest-frequency unresolved venues first.
4. Add threshold gate (example policy):
- warn above 2%
- fail above 5%

Acceptance:
1. `matches.venue_id` coverage reaches configured threshold.
2. Top unresolved venues are visible in generated report.

## Phase 5 - Region Filter Canonical Guardrail

Goal:
- Guarantee inclusion for all valid matches in selected region even with mixed data shape.

Files:
1. `formats/odi/engines/team_engine.py`
2. `core/data_access.py` (if any DAL-side region helper is introduced)

Actions:
1. Enforce region mask strategy using OR union of:
- `venue_id` prefix
- `venue` prefix when it already contains canonical ID-like token
- `resolve_venue_id(venue)` fallback
2. Keep helper centralized (`_build_continent_mask`) and reused by all region-based analyses.
3. Add deterministic behavior for unknown region labels (empty result + explicit message path).

Acceptance:
1. For `Sri Lanka vs England` in `Asia`, matches played must include Bangalore fixture.
2. No pair/region audit case shows `robust_count < expected_count`.

## Phase 6 - Region Output Contract Enforcement

Goal:
- Lock rendering contract so Home-vs-Away and Home-vs-All cannot regress silently.

Files:
1. `formats/odi/engines/team_engine.py`
2. `formats/odi/manifest.py`
3. `frontend/components/renderers/FunctionRenderer.tsx`
4. `frontend/components/renderers/VenueMatchupReport.tsx`

Actions:
1. Enforce engine branching:
- `opp_team == 'All'` -> matrix rows.
- `opp_team != 'All'` -> metric rows for card renderer.
2. Include last-5 fields for both sides in metric rows.
3. Renderer detects metric-row shape under `continent_perf` and dispatches to `VenueMatchupReport`.
4. Keep Home-vs-All matrix unchanged.

Acceptance:
1. Region Home-vs-Away renders high-fidelity card.
2. Region Home-vs-All renders matrix exactly as before.
3. Last-5 in card reflects most recent five by date.

## Phase 7 - Integrity Gate in Orchestrator

Goal:
- Make checks mandatory, not optional.

Files:
1. `scripts/maintenance/update_data.py`
2. `scripts/maintenance/etl_reconciliation_report.py`

Actions:
1. Add reconciliation stage after ingestion and before success.
2. Promote warnings to failures for hard-contract violations.
3. Produce run summary artifact each pipeline run.

Acceptance:
1. Pipeline exits non-zero when hard checks fail.
2. Success banner shown only after reconciliation pass.

## Phase 8 - Test Coverage and Recurrence Prevention

Goal:
- Prevent recurrence with automated regression around the exact failure mode.

Files:
1. `tests/test_continent_performance_regression.py`
2. `tests/test_param_mapper.py`
3. `tests/test_team_engine_matrix_regression.py`
4. `tests/test_etl_integrity_gates.py` (new)
5. `tests/test_venue_mapping_integrity.py` (new)

Actions:
1. Keep Bangalore-specific regression case.
2. Add generic region-pair parameterized tests across major teams/regions.
3. Add ETL integrity tests for:
- extraction strict fail
- duplicate delivery key detection
- atomic load rollback behavior
4. Add venue coverage threshold tests.

Acceptance:
1. All integrity tests pass in CI.
2. Any regression in region inclusion fails CI immediately.

## Phase 9 - Rollout Strategy

Goal:
- Safe transition with measurable confidence.

Steps:
1. Shadow mode for 3 pipeline runs:
- generate reconciliation artifacts
- do not block deployment yet
2. Compare drift across runs.
3. Enable hard blocking after 3 green runs.
4. Keep rollback DB copy for each production run window.

Acceptance:
1. Three consecutive green runs.
2. No unresolved critical diffs in audit artifacts.

## 9. Exact File Change Matrix

1. `formats/odi/utils/json_converter.py`
- strict error handling
- audit output
- deterministic file order

2. `formats/odi/utils/refinery_script.py`
- preserve delivery identity fields through transforms

3. `formats/odi/utils/ingest_to_db.py`
- atomic temp build and swap
- hard validation hooks
- venue backfill + threshold checks

4. `scripts/maintenance/update_data.py`
- fail-fast orchestration
- mandatory reconciliation stage

5. `scripts/maintenance/backfill_match_venue_ids.py`
- keep operational backfill and diagnostics

6. `scripts/maintenance/etl_reconciliation_report.py` (new)
- run-level integrity contract checks

7. `scripts/maintenance/continent_coverage_audit.py` (new)
- region inclusion audit over team pairs

8. `scripts/maintenance/venue_mapping_gap_report.py` (new)
- unresolved venue ranking and trend

9. `formats/odi/engines/team_engine.py`
- centralized robust region mask
- enforce away-vs-all output contract
- deterministic last-5 extraction

10. `frontend/components/renderers/FunctionRenderer.tsx`
- `continent_perf` dispatch logic for card/matrix split

11. `frontend/components/renderers/VenueMatchupReport.tsx`
- render last-5 rows for both teams

12. `formats/odi/manifest.py`
- verify optional away context contract for continent function

## 10. Validation Checklist (Must Pass)

## 10.1 Data Integrity Gates

1. No extraction file failures in strict mode.
2. `balls`/`matches` distinct `match_id` parity holds.
3. Duplicate delivery identity count = 0 on `(match_id, innings, over_num, ball_rank)`.
4. Venue unresolved ratio under threshold.

## 10.2 Region Behavior Gates

1. `Sri Lanka vs England` in `Asia` includes Bangalore match.
2. Region Home-vs-Away returns card-compatible metric rows.
3. Region Home-vs-All returns matrix rows.
4. Last-5 form reflects latest five chronological results.

## 10.3 Regression Gates

1. Existing truth-bridge suites remain green or have explicit approved drift notes.
2. New recurrence tests pass for multi-team, multi-region samples.

## 11. Risks and Mitigations

1. Risk: Compatibility break from identity-key tightening.
- Mitigation: dual-column support (`ball` + integer identity) during migration window.

2. Risk: Alias ambiguity for similarly named venues.
- Mitigation: unresolved queue + manual review for top-frequency ambiguities.

3. Risk: Longer pipeline runtime due added checks.
- Mitigation: SQL-vectorized reconciliation and lightweight summary artifacts.

4. Risk: Renderer mismatch from mixed payload shapes.
- Mitigation: explicit function-key + schema-shape dispatch checks.

## 12. Definition of Done

All must be true:

1. Pipeline is fail-fast for extraction and reconciliation faults.
2. DB load is atomic and rollback-safe.
3. Venue canonicalization has measurable coverage with threshold policy.
4. Region filters are robust against null/dirty `venue_id`.
5. Home-vs-Away region analysis renders high-fidelity card.
6. Home-vs-All region behavior remains unchanged.
7. Automated tests and audits prove no recurrence for other teams/regions.

## 13. Implementation Order (Execution Sequence)

1. Phase 0 baseline artifacts
2. Phase 1 extraction hardening
3. Phase 3 atomic load (safety first)
4. Phase 4 venue governance
5. Phase 5 region guardrail
6. Phase 6 output contract enforcement
7. Phase 7 orchestrator gating
8. Phase 8 expanded tests
9. Phase 9 rollout and hard gate enablement

## 14. Notes on Certainty

Absolute mathematical certainty ("100% forever") is not realistic in evolving data systems. The production standard we are targeting is:

1. deterministic contracts,
2. explicit integrity gates,
3. auditable run artifacts,
4. automatic prevention of silent loss,
5. fast detection/containment when upstream data drifts.

This is the highest practical integrity posture for this pipeline architecture.
