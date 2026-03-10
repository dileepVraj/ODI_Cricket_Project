# Cricket Project — Full Filesystem Cleanup Audit Report
**Date:** 2026-03-10
**Auditor:** Read-only audit (no files modified)
**Scope:** All directories except `frontend/node_modules/`, `.git/`, `docs/ai/`

---

## PRELIMINARY NOTE — Git Staging State

Several files shown in `git status` with ` D` (deleted from working tree, staged for deletion) no longer exist on disk. They have already been physically removed and just need a commit to finalise the deletions. These include all deleted items under `docs/` (plans, context, Function_Screenshots, etc.), `.githooks/pre-commit.ps1`, `CurrentTaskFile.md`, `FRONTEND_SKILLS_PLAN.md`, and `tmp_type_sync_out.txt`.

**Action required from architect: commit the staged deletions to clean the git index.**

---

## ROOT LEVEL

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `AGENTS.md` | MUST STAY | Agent governing law for Codex CLI. | Referenced at runtime by Codex CLI |
| `CLAUDE.md` | MUST STAY | Agent governing law for Claude Code. | Active — system-reminder loads it |
| `GEMINI.md` | MUST STAY | Agent governing law for Gemini/Antigravity IDE. | Active — Gemini agent reads it |
| `README.md` | MUST STAY | Project overview. | Human reference |
| `pyproject.toml` | MUST STAY | Build system + pytest config + dependency declarations. | Actively used |
| `requirements.txt` | MUST STAY | Dependency file. | Actively used |
| `.env` | MUST STAY | Live environment configuration. Not committed — correctly in .gitignore. | Used by config/settings.py |
| `.env.example` | MUST STAY | Template for .env. Documents expected variables. | Human reference |
| `taskFile.md` | SAFE TO DELETE | Untracked. Contains the task description that initiated this audit session — not a project document. | No imports found |
| `.mcp.json` | UNCERTAIN | Untracked MCP server config for Claude Code. Contains a GitHub PAT in plaintext — **security concern**. The duckdb path inside (`C:\Cricket_Project_Stable\data\odi.duckdb`) is wrong — `data/` root does not exist; the real DB is at `formats/odi/data/odi.duckdb`. Needs architect review before committing. | Local dev tool config — no code imports |

---

## `.githooks/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `pre-commit` | MUST STAY | Full gate sequence (Gates 1–6 + F1–F3) enforced on every commit. | Enforced by git |
| `pre-commit.ps1` | ALREADY DELETED | Staged deletion in git index. PowerShell version superseded by bash version. | Gone from disk |

---

## `core/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `core/__init__.py` | MUST STAY | Package marker. | Standard |
| `core/data_access.py` | MUST STAY | **REGISTERED HIGH-IMPACT FILE.** Every engine and service imports from it. | All engines + services |
| `core/data_loader.py` | MUST STAY | Used by the API lifespan to load data into the engine pool. | `api/lifespan.py` |
| `core/exceptions.py` | MUST STAY | `DataIntegrityError` used in `formats/odi/utils/ingest_to_db.py`. | Imported |
| `core/team_engine.py` | MUST STAY | Strategy loader — `get_team_engine()`. | `api/engine_pool.py`, `scripts/debug/inspect_sigs.py`, `tests/verify_headless_player.py` |
| `core/player_engine.py` | MUST STAY | Strategy loader — `get_player_engine()`. | Same callers |
| `core/predictor.py` | MUST STAY | Strategy loader — `get_predictor_engine()`. | api/engine_pool chain |
| `core/calculators/` (all files) | MUST STAY | Active calculation layer — matchup, performance, phase, player_math, team/. | Imported by services |
| `core/interfaces/` (all files) | MUST STAY | **REGISTERED HIGH-IMPACT FILE (`team_types.py`).** All interface contracts and TypedDicts. | All engines + API |
| `core/services/` (all files) | MUST STAY | All 8 service files actively used by API and engines. | `api/main.py`, engines |
| `core/match_pack/` (all files) | MUST STAY | `interpreter.py` and `transformer.py` — used by `formats/odi/match_pack.py` and tests. | `formats/odi/match_pack.py`, `tests/run_v31_tests.py` |
| `core/utils/compliance_bouncer.py` | MUST STAY | Gate 6 tool — runs on every commit and as part of task protocol. | Pre-commit hook + manual use |
| `core/utils/cricket_math.py` | MUST STAY | Safe division utility. | Imported by calculators |
| `core/utils/data_snapshot.py` | UNCERTAIN | Untracked new file. Utility to snapshot and diff `data/` directory contents. No code imports it. Output goes to `.snapshots/`. The `data/` path resolves incorrectly (captures `odi.duckdb` at 12KB vs real 19MB). Architect should decide: adopt officially (commit + add `.snapshots/` to .gitignore) or remove. | No imports found — standalone CLI tool |
| `core/gen_ai/` (entire tree) | MUST STAY | All skills, gate validators, guides — the AI agent operational framework. Required by pre-commit hooks and agent task protocols. | Pre-commit hook + agent session bootstrap |

---

## `api/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `api/__init__.py` | MUST STAY | Package marker. | Standard |
| `api/main.py` | MUST STAY | FastAPI application — all API routes. | Primary server entry point |
| `api/engine_pool.py` | MUST STAY | Engine lifecycle management. | `api/lifespan.py` |
| `api/lifespan.py` | MUST STAY | FastAPI lifespan handler. | `api/main.py` |
| `api/context_builder.py` | MUST STAY | Builds execution context for API calls. | `api/main.py` |
| `api/serializers.py` | MUST STAY | **REGISTERED HIGH-IMPACT FILE.** All API response serialization. | `api/main.py` |
| `api/schemas/` | MUST STAY | Pydantic request/response schemas. | `api/main.py` |

---

## `formats/`

### `formats/odi/` — Core Files

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `formats/odi/manifest.py` | MUST STAY | **REGISTERED HIGH-IMPACT FILE.** Defines all 17 functions, categories, context fields. | `api/main.py`, `api/context_builder.py`, `scripts/maintenance/validate_manifest.py` |
| `formats/odi/match_pack.py` | MUST STAY | 39KB — generates the 4-chapter match pack. | `api/main.py` |
| `formats/odi/predictor.py` | MUST STAY | `PredictorEngine` class — predict score function. | `api/engine_pool.py` |
| `formats/odi/player_engine.py` (stub) | UNCERTAIN | 6-line stub that re-exports `PlayerEngine` from `engines/player_engine.py`. No code currently imports this stub — all callers use the `core/player_engine.py` strategy loader which resolves to `engines/player_engine.py` directly. May be legacy scaffolding from pre-strategy-loader era. | No direct imports found |
| `formats/odi/team_engine.py` (stub) | UNCERTAIN | Same situation — 5-line stub re-exporting `TeamEngine`. No direct importer found. | No direct imports found |

### `formats/odi/engines/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `engines/__init__.py` | MUST STAY | Package marker. | Standard |
| `engines/player_engine.py` | MUST STAY | 31KB `PlayerEngine` — core ODI player analysis. | `api/engine_pool.py` via strategy loader |
| `engines/team_engine.py` | MUST STAY | 18KB `TeamEngine` — core ODI team analysis. | `api/engine_pool.py` via strategy loader |

### `formats/odi/config/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `config/__init__.py` | MUST STAY | Package marker. | Standard |
| `config/players.py` | MUST STAY | 45KB player roles and bowler styles registry. | `core/match_pack/interpreter.py`, `formats/odi/manifest.py`, `formats/odi/match_pack.py` |
| `config/rankings.py` | UNCERTAIN | Contains hardcoded `ODI_RANKINGS` dict with team names — potential Law 7 concern. This is a `config/` file, not an engine, so it may be acceptable. Architect should decide if this data should move into `manifest.py` as a registry. | `core/match_pack/interpreter.py`, `formats/odi/match_pack.py` |
| `config/settings.py` | MUST STAY | ODI-specific settings (audit reference, conversion audit path). | Imported by utils |

### `formats/odi/data/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `odi.duckdb` | MUST STAY | Live production database. | All engines via DAL |
| `odi.duckdb.prev` | SAFE TO DELETE | Leftover backup from previous ETL run (18MB). Not referenced anywhere in code. Created by ETL pipeline as rollback point, never used. | No references found |
| `FINAL_ODI_MASTER.csv`, `MATCH_INFO.csv`, `MATCH_SQUADS.csv`, `player_metadata.csv`, `processed_*.csv` | MUST STAY | Source and processed data. In `.gitignore`. | ETL pipeline |
| `README.txt` | MUST STAY | Data provenance documentation. | Human reference |
| `json_source/` (dir of ~1000+ JSONs) | MUST STAY | Raw ball-by-ball JSON files. In `.gitignore`. | `formats/odi/utils/json_converter.py` |

### `formats/odi/renderers/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `renderers/__init__.py` | UNCERTAIN | Package marker — but nothing imports from this package. | No callers found |
| `renderers/player_renderer.py` | UNCERTAIN | 19KB — appears to be a pre-API era rendering layer for player data. Not imported by any current file. May predate the FastAPI serialization approach. **Strongly suspect dead code.** | No imports found |
| `renderers/team_renderer.py` | UNCERTAIN | Same — 19KB, no importer found. | No imports found |

### `formats/odi/reports/`

| File | Category | Reason |
|------|----------|---------|
| `MatchPack_Australia_vs_India_20260212_160327.json` | SAFE TO DELETE | Dev test output from Feb 12. 98KB. No code references it. |
| `MatchPack_India_vs_Australia_2026021*.json` (×11 files) | SAFE TO DELETE | 11 near-identical dev test outputs from Feb 16–18. ~370KB total. Accumulated from iterative testing. No production use. |
| `continent_coverage_audit.json` | SAFE TO DELETE | 201-byte audit output generated by `scripts/maintenance/continent_coverage_audit.py`. Dev artifact — output file, not input. |
| `conversion_audit.json` | SAFE TO DELETE | 308KB audit output generated during ETL. No code reads it. |
| `reconciliation_audit.json` | SAFE TO DELETE | 2KB audit output. Dev artifact. |
| `matchpack_review_comments.txt` | SAFE TO DELETE | 4KB developer review notes from Feb 12. No code reads it. |

**Note:** The entire `formats/odi/reports/` directory has no `.gitignore` exclusion and all files are git-tracked. Architect should add a `.gitignore` entry to exclude this directory or its contents going forward.

### `formats/odi/scripts/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `check_bowler_coverage.py` | UNCERTAIN | Manually run maintenance utility — checks which bowlers from the CSV are in `players.py`. Referenced in `TECHNICAL_DOCUMENTATION.md`. | Only referenced in docs |
| `find_missing_players.py` | UNCERTAIN | Same — manually run maintenance utility. | Only referenced in docs |

### `formats/odi/tools/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `enrich_match_scores.py` | UNCERTAIN | Older ETL enrichment script. No references in current codebase. Unclear if superseded by `ingest_to_db.py`. | No imports found |
| `list_india_matches.py` | SAFE TO DELETE | Developer one-off analysis script. No imports, no references. | No imports found |
| `process_player_stats.py` | UNCERTAIN | 5KB ETL script. May be superseded by `formats/odi/utils/refinery_script.py`. Unclear which is canonical. | No imports found |

### `formats/odi/tests/truth_bridge/`

| File/Dir | Category | Reason | Usage Check |
|----------|----------|---------|-------------|
| All 16 active test dirs (full contents) | MUST STAY | Regression test suite — `ground_truth.json`, `report.json`, `test_runner.py` in each. | `run_all.py`, `tests/test_match_pack.py` |
| `away_stats/` (empty dir) | SAFE TO DELETE | Empty directory — old name superseded by `away_performance/`. | Empty |
| `continent_stats/` (empty dir) | SAFE TO DELETE | Empty directory — old name superseded by `continent_performance/`. | Empty |
| `global_power/` (empty dir) | SAFE TO DELETE | Empty directory — old name, no longer in use. | Empty |
| `base_runner.py` | MUST STAY | Base class for all truth_bridge test runners. | All test runners in subdirs |
| `run_all.py` | MUST STAY | Orchestrates all regression tests. | Manual + CI use |
| `diagnose_test.py` | UNCERTAIN | 1.2KB diagnostic helper. Last modified Feb 13. No direct imports from other files. Dev utility for debugging test failures. | No imports found |
| `REGRESSION_GUIDE.md` | MUST STAY | Documentation for the truth_bridge test framework. | Human reference |
| `technical_document.md` | UNCERTAIN | 4KB technical doc inside the tests directory. Non-standard location for documentation. | No code references |

### `formats/odi/tests/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `verify_boundary_fix.py` | UNCERTAIN | Standalone script to verify a specific boundary fix. Not imported by any test. Last modified Feb 14. Likely a one-off verification that is now stale. | No imports found |
| `__init__.py` | MUST STAY | Package marker. | Standard |

### `formats/odi/utils/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `ingest_to_db.py` | MUST STAY | Primary ETL pipeline. | `tests/test_etl_integrity_gates.py` |
| `json_converter.py` | MUST STAY | Converts raw JSON source files to master CSV. | `tests/test_etl_integrity_gates.py` |
| `refinery_script.py` | MUST STAY | Rebuilds processed stats layer. | `tests/test_refinery_contracts.py` |

---

## `config/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `config/__init__.py` | MUST STAY | Package marker. | Standard |
| `config/format_registry.py` | MUST STAY | `FORMATS` registry — maps format keys to module paths. | `core/team_engine.py`, `core/player_engine.py`, `core/predictor.py` |
| `config/settings.py` | MUST STAY | Environment config loading. | `api/main.py`, `scripts/`, `tests/` |
| `config/shared/__init__.py` | MUST STAY | Package marker. | Standard |
| `config/shared/team_colors.py` | MUST STAY | Team color constants. | `api/main.py`, renderers |
| `config/shared/themes.py` | MUST STAY | Theme definitions. | `api/main.py`, renderers |
| `config/shared/venues.py` | MUST STAY | `VENUE_MAP` and `resolve_venue_id`. | `core/data_access.py`, `core/services/`, ETL |

---

## `scripts/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `scripts/context_linter.py` | UNCERTAIN | Thin wrapper calling `scripts/maintenance/context_linter.py`. Broken — depends on `docs/context/rules.json` which no longer exists on disk. Fix or retire. | Depends on deleted file |
| `scripts/fn_results.json` | SAFE TO DELETE | Dev test output from Feb 16. Output file, not input. | Output artifact |
| `scripts/fn_status.txt` | SAFE TO DELETE | Garbled-encoding dev output. Feb 16 test run artifact. | Output artifact |
| `scripts/fn_status_utf8.txt` | SAFE TO DELETE | UTF-8 version of the same garbled output. | Output artifact |
| `scripts/full_results.txt` | SAFE TO DELETE | 17/17 PASSED summary from a past test run. Output artifact from Feb 18. | Output artifact |
| `scripts/squad_results.txt` | SAFE TO DELETE | 6-line squad test results. Feb 18 output artifact. | Output artifact |
| `scripts/signatures.json` | SAFE TO DELETE | Generated by `inspect_sigs.py` — stale engine method signatures snapshot. | Output artifact |
| `scripts/linter_report.txt` | SAFE TO DELETE | Stale output reporting violations for files that no longer exist. | Output artifact |

### `scripts/debug/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `_check_db.py` | UNCERTAIN | Quick DB inspection script. Imports `duckdb` directly — not part of any test or gate. Dev diagnostic tool. | Standalone dev tool |
| `check_predictor.py` | SAFE TO DELETE | One-off script posting to predict_score endpoint with hardcoded India/Australia data. Dead scaffolding, last modified Mar 4. | No imports |
| `inspect_sigs.py` | SAFE TO DELETE | Generated `scripts/signatures.json` (stale snapshot). Debugging work complete. | No imports from other files |

### `scripts/maintenance/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `backfill_match_venue_ids.py` | MUST STAY | Active maintenance tool for missing venue_id values. | Standalone — referenced in context |
| `context_indexer.py` | UNCERTAIN | Generates `docs/context/project_map.json` — output target directory no longer exists. Cannot produce output. Fix output path or retire. | Output target deleted |
| `context_linter.py` | UNCERTAIN | Real context linter. Depends on `docs/context/rules.json` which is deleted. Currently broken. | Depends on deleted `docs/context/rules.json` |
| `continent_coverage_audit.py` | MUST STAY | Active ETL integrity tool. | Referenced from `formats/odi/config/settings.py` |
| `etl_reconciliation_report.py` | MUST STAY | Used by `tests/test_etl_integrity_gates.py`. Active. | `tests/test_etl_integrity_gates.py` |
| `focus_manager.py` | SAFE TO DELETE | Old AI session focus tracking tool. `docs/context/` directory is gone. Superseded by `docs/ai/SESSION_STATE.md`. | No imports. Target dir deleted. |
| `memory_manager.py` | SAFE TO DELETE | Generates `docs/context/memory_index.json` — directory gone. Superseded by new docs/ai/ system. | No imports. Target dirs deleted. |
| `refresh_ground_truth.py` | MUST STAY | Refreshes truth_bridge ground truth fixtures. Active maintenance tool. | Standalone, referenced in truth_bridge workflow |
| `update_data.py` | MUST STAY | Data update pipeline script. | Standalone maintenance tool |
| `validate_manifest.py` | UNCERTAIN | Validates manifest.py against engine classes. Partially overlaps with Gate 3 (`manifest-contract-verifier`). Also referenced from `formats/odi/manifest.py` `__main__` block. Architect should decide: retire in favour of Gate 3 or retain as standalone dev tool. | `formats/odi/manifest.py` (`__main__`) |

### `scripts/tests/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `check_functions.py` | UNCERTAIN | API function smoke tester — hits all manifest functions via HTTP. Overlaps with `test_all_fns.py` at a different level. | Standalone |
| `test_all_fns.py` | MUST STAY | Full regression test of all 17 ODI functions via API. Active dev tool. | Standalone test runner |
| `test_api.py` | MUST STAY | API smoke test — validates all endpoints. | Standalone |
| `test_squad_fns.py` | MUST STAY | Squad function tests. | Standalone |

---

## `tests/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `tests/__init__.py` | MUST STAY | Package marker. | Standard |
| `test_api_integration.py` | MUST STAY | Proper pytest integration tests using FastAPI TestClient. | `pyproject.toml` testpaths |
| `test_continent_performance_regression.py` | MUST STAY | Targeted regression test. Proper pytest. | `pyproject.toml` testpaths |
| `test_etl_integrity_gates.py` | MUST STAY | ETL integrity gate tests. Proper pytest. | `pyproject.toml` testpaths |
| `test_match_pack.py` | MUST STAY | Match pack tests. Proper pytest. | `pyproject.toml` testpaths |
| `test_param_mapper.py` | MUST STAY | Param mapper tests. Proper pytest. | `pyproject.toml` testpaths |
| `test_refinery_contracts.py` | MUST STAY | Refinery contract tests. Proper pytest. | `pyproject.toml` testpaths |
| `test_team_engine_matrix_regression.py` | MUST STAY | Team engine regression. Proper pytest. | `pyproject.toml` testpaths |
| `run_v31_tests.py` | UNCERTAIN | Match Pack v3.2 quick verification script. Not proper pytest — standalone. May be superseded by `test_match_pack.py`. Architect should confirm unique coverage. | No imports from other tests |
| `verify_headless_player.py` | UNCERTAIN | Headless player API test from Feb 21. Errored during its last run (traceback in `tests/output.txt`). May be incomplete/unresolved. | No imports |
| `ideas_docs.md` | MUST STAY | Active backlog of unimplemented test ideas with concrete specs. Marked "Pending". | Human reference — active backlog |
| `output.txt` | SAFE TO DELETE | Garbled double-byte encoded traceback output from running `verify_headless_player.py`. Feb 14 artifact. | Output artifact |
| `runners/conftest.py` | UNCERTAIN | Empty pytest conftest with placeholder comment. No actual configuration. May be scaffolding. | No content |
| `truth_bridge/new_ground_truth.json` | UNCERTAIN | Feb 23 snapshot. Possible working file from `scripts/maintenance/refresh_ground_truth.py` or stale artifact. May belong in `formats/odi/tests/truth_bridge/`. | No imports |
| `truth_bridge/refresh_report.json` | SAFE TO DELETE | Feb 24 report from a past ground truth refresh run. Output artifact. | Output artifact |

---

## `docs/` (excluding `docs/ai/`)

### `docs/guides/`

| File | Category | Reason |
|------|----------|---------|
| `ENGINEERING_STANDARDS_BACKEND.md` | MUST STAY | Agent-authoritative backend standards. Read by agents each session. |
| `ENGINEERING_STANDARDS_FRONTEND.md` | MUST STAY | Agent-authoritative frontend standards. |
| `ENGINEERING_STANDARDS_CORE.md` | MUST STAY | Human architect reference. |
| `DEV_GUIDE.md` | MUST STAY | Developer onboarding and architecture overview. |
| `TECHNICAL_AUDIT_REPORT.md` | MUST STAY | Current audit report (2026-03-08). Active reference for compliance tracking. |
| `TECHNICAL_DOCUMENTATION.md` | UNCERTAIN | Feb 21 system documentation. Some content still accurate, but contains Mermaid diagrams referencing `dashboard.ipynb` which no longer exists. Partially stale. Architect may want to archive or update. |

### `docs/audits/team_engine/`

| File | Category | Reason |
|------|----------|---------|
| `audit_01_bouncer.md` through `audit_05_final_report.md` | UNCERTAIN | Complete team_engine audit series from March 5. Work is complete (closed task). Historical records not referenced by any code. Architect should decide: archive under a completed audits folder or delete. |

### `docs/audits/player_engine/`

| File | Category | Reason |
|------|----------|---------|
| `AUDIT-P01` through `AUDIT-P10` | UNCERTAIN | Complete player_engine audit series from March 5. Same situation as team_engine audits — historical record. |

### `docs/audits/frontend/`

| File | Category | Reason |
|------|----------|---------|
| `ComplianceAuditReport.md` | MUST STAY | Untracked but current — dated 2026-03-09 with complete frontend compliance audit results. Working record for the active frontend sprint. Should be committed or added to `.gitignore` if agent-generated output. |

### `docs/hypotheses/`

| File | Category | Reason |
|------|----------|---------|
| `ROI_METRICS.md` | MUST STAY | Trading hypothesis documentation — foundational domain knowledge. |

---

## `frontend/`

| File/Dir | Category | Reason |
|----------|----------|---------|
| `app/`, `components/`, `lib/`, `public/` | MUST STAY | Active Next.js application files — all in use. |
| `next.config.ts`, `tsconfig.json`, `eslint.config.mjs`, `postcss.config.mjs`, `package.json`, `package-lock.json`, `next-env.d.ts` | MUST STAY | Frontend build configuration. |
| `tsconfig.tsbuildinfo` | UNCERTAIN | TypeScript build cache (102KB). Normally in `.gitignore` for frontend projects — currently tracked. Should be added to `frontend/.gitignore` or root `.gitignore`. |
| `.next/` | UNCERTAIN | Next.js build output directory. Normally excluded from git. Should be in `.gitignore`. |
| `frontend/README.md` | UNCERTAIN | Default Next.js boilerplate README — not project-specific. Could be replaced with project-specific content or removed. |

---

## `utils/` (root level)

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `utils/test_recorder.py` | SAFE TO DELETE | Legacy script from Feb 6. No imports found anywhere in the codebase. Oldest file in directory. Superseded by truth_bridge framework. | No imports found |

---

## `dev/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `dev/handoff_prompt.txt` | SAFE TO DELETE | Feb 16 agent handoff prompt for old `docs/ai/AI_MEMORY.md` pipeline. References files that no longer exist. Superseded by AGENTS.md/CLAUDE.md governance system. | No imports |
| `dev/linter_report.txt` | SAFE TO DELETE | Feb 18 linter report output (40 violations about `scripts/debug_generate_pack.py` which does not exist on disk). Stale output artifact. | Output artifact |
| `dev/_db_report.txt` | SAFE TO DELETE | DB inspection report from Feb 18 (generated by `scripts/debug/_check_db.py`). Stale against current schema. | Output artifact |

---

## `.snapshots/`

| File | Category | Reason |
|------|----------|---------|
| `data_snap_20260310_125721.json` | UNCERTAIN | Generated by `core/utils/data_snapshot.py`. The `data/` path resolves incorrectly (captured `odi.duckdb` at 12KB vs real 19MB — wrong path). `.snapshots/` has no `.gitignore` entry. Architect should: add to `.gitignore`, delete, or fix the `data_snapshot.py` path. |
| `data_snap_20260310_130128.json` | UNCERTAIN | Second snapshot from same session. Same issues. |

---

## `data_templates/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `functions_slider_checklist` | UNCERTAIN | User-facing guide for setting year slider before each analysis function. No code imports it. Feb 6 vintage. Domain knowledge may still be accurate. Could move to `docs/` if retained. | No imports |
| `manual_log.json` | UNCERTAIN | 34KB manual log of function test runs. Feb 6. Old format — predates truth_bridge framework. No code imports it. Possibly historical reference. | No imports |
| `manual_log copy.json` | SAFE TO DELETE | Literal filesystem copy of `manual_log.json` (7KB truncated version). Duplicate artifact. | No imports |
| `prompts/` (6 AI prompt template files) | UNCERTAIN | Feb 6 vintage prompt templates for an older AI analysis workflow. No code imports them. May be domain knowledge worth archiving or completely superseded. | No imports |

---

## `.gemini/`

| File | Category | Reason | Usage Check |
|------|----------|---------|-------------|
| `refactor_script.py` | SAFE TO DELETE | One-time refactor script with a hardcoded OneDrive path (`c:\Users\khaisar jaha\OneDrive\Desktop\Cricket_Project_Stable\...`) that no longer exists. The refactor it performed has long since been completed. Dead scaffolding. | No imports |

---

## `temp_pytest/`

| Directory | Category | Reason |
|-----------|----------|---------|
| `temp_pytest/` (empty dir) | SAFE TO DELETE | Completely empty directory. Leftover from a pytest run configured to use a temp directory. Not in `.gitignore`. Not tracked by git. | Empty |

---

## SUMMARY — SAFE TO DELETE

| File/Directory | Size (approx) | Reason |
|----------------|---------------|--------|
| `taskFile.md` | 1KB | Task prompt document, not a project file |
| `utils/test_recorder.py` | 2.5KB | Orphaned legacy script, no imports |
| `.gemini/refactor_script.py` | 11KB | Dead one-time refactor, hardcoded old path |
| `temp_pytest/` | 0 | Empty directory |
| `formats/odi/data/odi.duckdb.prev` | 18MB | Stale ETL backup, no references |
| `formats/odi/reports/MatchPack_*.json` (×12 files) | ~370KB | Dev test output artifacts |
| `formats/odi/reports/continent_coverage_audit.json` | 0.2KB | Output artifact |
| `formats/odi/reports/conversion_audit.json` | 301KB | Output artifact |
| `formats/odi/reports/reconciliation_audit.json` | 3KB | Output artifact |
| `formats/odi/reports/matchpack_review_comments.txt` | 4KB | Dev notes, not consumed by code |
| `formats/odi/tests/truth_bridge/away_stats/` | 0 | Empty dir, superseded |
| `formats/odi/tests/truth_bridge/continent_stats/` | 0 | Empty dir, superseded |
| `formats/odi/tests/truth_bridge/global_power/` | 0 | Empty dir, superseded |
| `formats/odi/tools/list_india_matches.py` | 2KB | One-off analysis, no imports |
| `scripts/debug/check_predictor.py` | 0.7KB | One-off API test with hardcoded data |
| `scripts/debug/inspect_sigs.py` | 1.5KB | Generated stale signatures.json, now obsolete |
| `scripts/fn_results.json` | 5KB | Output artifact |
| `scripts/fn_status.txt` | 6.5KB | Garbled output artifact |
| `scripts/fn_status_utf8.txt` | 3.3KB | Output artifact |
| `scripts/full_results.txt` | 0.4KB | Output artifact |
| `scripts/squad_results.txt` | 0.2KB | Output artifact |
| `scripts/signatures.json` | 4KB | Stale generated output |
| `scripts/linter_report.txt` | 0.9KB | Stale output artifact |
| `scripts/maintenance/focus_manager.py` | 3.4KB | Old AI session tool, target dir deleted |
| `scripts/maintenance/memory_manager.py` | 2.7KB | Old AI session tool, target dir deleted |
| `dev/handoff_prompt.txt` | 6.5KB | Obsolete handoff prompt for old AI pipeline |
| `dev/linter_report.txt` | 6.6KB | Stale output artifact |
| `dev/_db_report.txt` | 1.4KB | Stale DB inspection output |
| `data_templates/manual_log copy.json` | 7KB | Literal duplicate of manual_log.json |
| `tests/output.txt` | 3.5KB | Garbled error traceback output artifact |
| `tests/truth_bridge/refresh_report.json` | 13KB | Output artifact from past refresh run |

**Total estimated safe-to-delete size: ~440KB tracked + 18MB `odi.duckdb.prev` + empty dirs**

---

## SUMMARY — UNCERTAIN (Needs Architect Decision)

| File/Directory | Decision Needed |
|----------------|-----------------|
| `.mcp.json` | Security: GitHub PAT in plaintext. Wrong duckdb path. Commit, fix path, or gitignore? |
| `core/utils/data_snapshot.py` + `.snapshots/` | Adopt officially (commit + add `.snapshots/` to .gitignore) or remove? Path resolves wrongly. |
| `formats/odi/player_engine.py` (stub) | Dead re-export stub — remove if strategy loader is sole resolution path? |
| `formats/odi/team_engine.py` (stub) | Same. |
| `formats/odi/renderers/` (entire dir) | No importer found — dead code or planned for future use? |
| `formats/odi/config/rankings.py` | Hardcoded team names — move into manifest.py registry? |
| `formats/odi/scripts/check_bowler_coverage.py` | Manual maintenance tool — keep or retire? |
| `formats/odi/scripts/find_missing_players.py` | Same. |
| `formats/odi/tools/enrich_match_scores.py` | Superseded by ingest_to_db.py? Or still needed? |
| `formats/odi/tools/process_player_stats.py` | Superseded by refinery_script.py? Or still needed? |
| `formats/odi/tests/truth_bridge/diagnose_test.py` | Dev utility — keep or retire? |
| `formats/odi/tests/truth_bridge/technical_document.md` | Move to docs/? Or delete? |
| `formats/odi/tests/verify_boundary_fix.py` | One-off verification, likely complete — delete? |
| `scripts/context_linter.py` | Broken — depends on deleted `docs/context/`. Fix or retire? |
| `scripts/maintenance/context_linter.py` | Same — depends on deleted `docs/context/rules.json`. |
| `scripts/maintenance/context_indexer.py` | Output target deleted — fix output path or retire? |
| `scripts/maintenance/validate_manifest.py` | Overlaps Gate 3. Keep as dev tool or retire? |
| `scripts/debug/_check_db.py` | Dev diagnostic tool — keep or retire? |
| `scripts/tests/check_functions.py` | Overlaps test_all_fns.py — retire? |
| `docs/audits/team_engine/` (5 files) | Historical audit records — archive or delete? |
| `docs/audits/player_engine/` (10 files) | Same. |
| `docs/audits/frontend/ComplianceAuditReport.md` | Current — commit or add to .gitignore? |
| `docs/guides/TECHNICAL_DOCUMENTATION.md` | Partially stale — update or archive? |
| `data_templates/functions_slider_checklist` | Move to docs/ or delete? |
| `data_templates/manual_log.json` | Historical record — archive or delete? |
| `data_templates/prompts/` (6 files) | Old AI prompt templates — archive or delete? |
| `tests/run_v31_tests.py` | Standalone — does it duplicate pytest coverage? |
| `tests/verify_headless_player.py` | Errored during last run — complete or remove? |
| `tests/runners/conftest.py` | Empty placeholder — remove or populate? |
| `tests/truth_bridge/new_ground_truth.json` | Working file or stale artifact? Move to formats/odi/tests/? |
| `frontend/tsconfig.tsbuildinfo` | Should be in .gitignore (102KB build cache). |
| `frontend/.next/` | Should be in .gitignore (build output). |
| `frontend/README.md` | Default Next.js boilerplate — replace with project-specific content or remove? |

---

## ADDITIONAL ACTIONS RECOMMENDED (non-deletion)

1. **Commit staged deletions** — many files are already deleted but not committed. Run `git commit` to finalise.
2. **Add `.gitignore` entries**:
   - `formats/odi/reports/` (or `*.json` within it)
   - `.snapshots/`
   - `frontend/.next/`
   - `frontend/tsconfig.tsbuildinfo`
3. **Fix `.mcp.json`** — wrong duckdb path + PAT exposure.
4. **Context toolchain** — `scripts/context_linter.py`, `scripts/maintenance/context_linter.py`, `scripts/maintenance/context_indexer.py` all depend on `docs/context/` which is deleted. Decide: retire all three or rebuild the dependency.

---

**This report is read-only. No files were modified, moved, or deleted during this audit.**
