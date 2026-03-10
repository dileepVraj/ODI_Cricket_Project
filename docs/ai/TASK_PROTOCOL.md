# TASK_PROTOCOL.md
# Cricket Algo-Trading Platform — Agent Task Protocol
# Location: docs/ai/TASK_PROTOCOL.md
#
# PURPOSE:
# This file is the authoritative routing guide for any AI agent working on
# this platform. Before touching any file, an agent MUST read this document,
# classify the task, load the correct guide skill(s), and confirm the gate
# sequence. This file is a hard protocol — not a suggestion.
#
# HOW TO USE THIS FILE:
# 0. If invoked via TASK_RUNNER — skip this file's manual steps.
#    TASK_RUNNER reads this file automatically in Phase 4.
# 1. Read Section 1 — classify your task type
# 2. Read Section 2 — load the guide skill(s) for that task type
# 3. Read Section 3 — confirm the gate sequence for your scope
# 4. Read Section 4 — mixed-scope rules if task touches both backend and frontend
# 5. Read Section 5 — hard rules that apply to every task regardless of type
# 6. Proceed to the guide skill. Do not skip this file.

---

## SECTION 1 — TASK CLASSIFICATION

Read the task description. Pick exactly one primary type from the table below.
If the task matches more than one type — read Section 4 (Mixed-Scope Rules).

| Task Type | Definition | Examples |
|---|---|---|
| **bug-fix** | Correcting incorrect behaviour in existing code. Output changes. Logic changes to fix a defect. | Wrong stat returned, API 500, type error, broken render |
| **modification** | Deliberate, intentional change to existing behaviour, logic, or configuration. Not a bug — a controlled delta. | Changing a formula, updating a config constant, adjusting a serializer field |
| **refactor** | Structural change only. Behaviour is identical before and after. No logic changes, no output changes. | Splitting a large file, renaming a class, moving code between files, extracting a helper |
| **new-feature** | Implementing a new analytical function, endpoint, or UI renderer that does not currently exist. | New engine method, new manifest entry, new renderer component |
| **frontend-bug-fix** | Bug confined to the Next.js frontend layer only. No backend files touched. | Wrong class applied, broken layout, missing aria-label, type mismatch in component |
| **frontend-modification** | Intentional change to an existing frontend component, style, or API integration. | Updating a CSS token, changing a prop, modifying a layout component |
| **frontend-new-component** | Creating a new React component, renderer, input, or layout element. | New renderer for a new output_type, new shared utility component |
| **validator-fix** | Fixing or calibrating a validator script or gate SKILL.md. No source code changes. | Rule regex fix, false positive removal, scan scope extension |
| **guide-update** | Updating a guide skill SKILL.md. No source code changes. | Path fix, trigger description update, new pattern documentation |
| **infra / hook** | Changes to git hooks, CI config, or project tooling. | Pre-commit hook wiring, bouncer config |

---

## SECTION 2 — GUIDE SKILL LOAD ORDER

### 2.1 — Backend Tasks

---

#### TASK TYPE: bug-fix (backend)

**Guide skill to load FIRST:**
```
core/gen_ai/skills/guides/backend/bug-fix-guide/SKILL.md
```

**Standards file to attach:**
```
docs/guides/ENGINEERING_STANDARDS_BACKEND.md
```

**Session state to read:**
```
docs/ai/SESSION_STATE.md
```

**Read order:**
1. `docs/ai/SESSION_STATE.md`
2. `docs/guides/ENGINEERING_STANDARDS_BACKEND.md`
3. `core/gen_ai/skills/guides/backend/bug-fix-guide/SKILL.md`
4. Execute every checkpoint in the guide in sequence.

---

#### TASK TYPE: modification (backend)

**Guide skill to load FIRST:**
```
core/gen_ai/skills/guides/backend/modification-guide/SKILL.md
```

**Standards files to attach:**
```
docs/guides/ENGINEERING_STANDARDS_BACKEND.md
docs/guides/ENGINEERING_STANDARDS_FRONTEND.md
```

**Read order:**
1. `docs/ai/SESSION_STATE.md`
2. `docs/guides/ENGINEERING_STANDARDS_BACKEND.md`
3. `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md`
4. `core/gen_ai/skills/guides/backend/modification-guide/SKILL.md`
5. Execute every checkpoint in the guide in sequence.

---

#### TASK TYPE: refactor (backend)

**Guide skill to load FIRST:**
```
core/gen_ai/skills/guides/backend/refactor-guide/SKILL.md
```

**Standards file to attach:**
```
docs/guides/ENGINEERING_STANDARDS_BACKEND.md
```

**Read order:**
1. `docs/ai/SESSION_STATE.md`
2. `docs/guides/ENGINEERING_STANDARDS_BACKEND.md`
3. `core/gen_ai/skills/guides/backend/refactor-guide/SKILL.md`
4. Execute every checkpoint in the guide in sequence.

---

#### TASK TYPE: new-feature (backend + frontend)

**Guide skill to load FIRST:**
```
core/gen_ai/skills/guides/backend/new-feature-guide/SKILL.md
```

**Standards files to attach:**
```
docs/guides/ENGINEERING_STANDARDS_BACKEND.md
docs/guides/ENGINEERING_STANDARDS_FRONTEND.md
```

**Read order:**
1. `docs/ai/SESSION_STATE.md`
2. `docs/guides/ENGINEERING_STANDARDS_BACKEND.md`
3. `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md`
4. `core/gen_ai/skills/guides/backend/new-feature-guide/SKILL.md`
5. When Phase 4 (UI) begins — also load:
   `core/gen_ai/skills/guides/frontend/frontend-new-component-guide/SKILL.md`
6. Execute every checkpoint in both guides in sequence.

**Note:** new-feature always spans backend and frontend. Both guides are required.
Do not begin Phase 4 (UI) without having read the frontend-new-component-guide.

---

### 2.2 — Frontend Tasks

---

#### TASK TYPE: frontend-bug-fix

**Guide skill to load FIRST:**
```
core/gen_ai/skills/guides/frontend/frontend-bug-fix-guide/SKILL.md
```

**Standards file to attach:**
```
docs/guides/ENGINEERING_STANDARDS_FRONTEND.md
```

**Read order:**
1. `docs/ai/SESSION_STATE.md`
2. `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md`
3. `core/gen_ai/skills/guides/frontend/frontend-bug-fix-guide/SKILL.md`
4. Execute every checkpoint in the guide in sequence.

---

#### TASK TYPE: frontend-modification

**Guide skill to load FIRST:**
```
core/gen_ai/skills/guides/frontend/frontend-modification-guide/SKILL.md
```

**Standards file to attach:**
```
docs/guides/ENGINEERING_STANDARDS_FRONTEND.md
```

**Read order:**
1. `docs/ai/SESSION_STATE.md`
2. `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md`
3. `core/gen_ai/skills/guides/frontend/frontend-modification-guide/SKILL.md`
4. Execute every checkpoint in the guide in sequence.

---

#### TASK TYPE: frontend-new-component

**Guide skill to load FIRST:**
```
core/gen_ai/skills/guides/frontend/frontend-new-component-guide/SKILL.md
```

**Standards file to attach:**
```
docs/guides/ENGINEERING_STANDARDS_FRONTEND.md
```

**Read order:**
1. `docs/ai/SESSION_STATE.md`
2. `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md`
3. `core/gen_ai/skills/guides/frontend/frontend-new-component-guide/SKILL.md`
4. Execute every checkpoint in the guide in sequence.

---

### 2.3 — Tooling / Infrastructure Tasks

For validator-fix, guide-update, and infra/hook tasks:
- No guide skill is required.
- Read `docs/ai/SESSION_STATE.md` and `docs/guides/ENGINEERING_STANDARDS_BACKEND.md`.
- Run the baseline bouncer before and after.
- Run Gate 5 and Gate 6 as the minimum gate sequence.
- Run any gate whose script was modified to verify it still functions correctly.

---

## SECTION 3 — GATE SEQUENCE BY SCOPE

Every task runs gates. The gate sequence depends on which files are touched.
Gates are cumulative — if multiple scopes are touched, all applicable gates run.

### 3.1 — Backend Gate Sequence

Run these gates when any backend file is modified:

```
GATE 1 — boundary-sentinel
Trigger: any file in core/ is modified
Script:  core/gen_ai/skills/validators/backend/boundary-sentinel/scripts/run_sentinel.py
Command: python core/gen_ai/skills/validators/backend/boundary-sentinel/scripts/run_sentinel.py --root .
Pass:    zero violations

GATE 2 — duckdb-lint-ops
Trigger: any file in calculators/, engines/, or services/ is modified
Script:  core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py
Command: python core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py --root .
Pass:    zero DOD violations (no iterrows, itertuples, manual DataFrame loops)

GATE 3 — manifest-contract-verifier
Trigger: manifest.py or any engine file in formats/ is modified
Script:  core/gen_ai/skills/validators/backend/manifest-contract-verifier/scripts/run_verifier.py
Command: python core/gen_ai/skills/validators/backend/manifest-contract-verifier/scripts/run_verifier.py --root .
Pass:    zero violations

GATE 4 — serialization-guard
Trigger: api/serializers.py is modified OR any engine return type changes
Script:  core/gen_ai/skills/validators/backend/serialization-guard/scripts/run_lint.py
Command: python core/gen_ai/skills/validators/backend/serialization-guard/scripts/run_lint.py --root .
Pass:    zero violations
```

### 3.2 — Frontend Gate Sequence

Run these gates when any frontend file is modified:

```
GATE F1 — frontend-lint-sentinel
Trigger: any .tsx or .ts file in frontend/ is modified
Script:  core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/scripts/run_frontend_lint.py
Command: python core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/scripts/run_frontend_lint.py --root .
Pass:    zero violations

GATE F2 — frontend-paradigm-sentinel
Trigger: always after F1 passes (any frontend/ modification)
Script:  core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/scripts/run_frontend_paradigm.py
Command: python core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/scripts/run_frontend_paradigm.py --root .
Pass:    zero violations

GATE F3 — frontend-type-sync-guard
Trigger: ALWAYS — runs on every task that touches any frontend/ file.
         Scans all frontend/lib/*.ts for @schema and @schema-exempt compliance.
Script:  core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/scripts/run_type_sync.py
Command: python core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/scripts/run_type_sync.py --root .
Pass:    zero violations
```

### 3.3 — Always-On Gates (every task, every scope)

```
GATE 5 — paradigm-sentinel (meta-gate)
Trigger: ALWAYS — runs after all primary gates regardless of scope
Guide:   core/gen_ai/skills/validators/backend/paradigm-sentinel/SKILL.md
         Follow instructions in the SKILL.md — do not skip any check.
Pass:    zero violations across all paradigm checks

GATE 6 — compliance-bouncer (final gate)
Trigger: ALWAYS — last step before every task is marked complete
Command: python core/utils/compliance_bouncer.py --root .
Pass:    PASS: 100% compliance
         Violation count must match or improve on the baseline recorded
         at the start of the task.
```

### 3.4 — Dormant Gates (DO NOT activate)

```
GATE 3.5 — event-state-linter
Status:  DORMANT — activate only when core/live/ is created (Phase 12)
Script:  core/gen_ai/skills/validators/backend/event-state-linter/scripts/run_lint.py
Trigger: any file in core/live/ or api/live/ is modified
Note:    Phase 12 has not started. Do not reference, activate, or create
         any live layer files. Hard stop if scope touches core/live/ or api/live/.
```

### 3.5 — Gate Sequence Summary Table

| Scope touched | Gates to run |
|---|---|
| `core/` only | 1, 5, 6 |
| `calculators/` / `engines/` / `services/` | 1, 2, 5, 6 |
| `manifest.py` or `formats/` engines | 1, 2, 3, 5, 6 |
| `api/serializers.py` or engine return type | 1, 2, 3, 4, 5, 6 |
| `frontend/` only | F1, F2, F3, 5, 6 |
| Backend + Frontend (new-feature, modification) | 1, 2, 3, 4, F1, F2, F3, 5, 6 |
| Tooling / infra only | 5, 6 |

---

## SECTION 4 — MIXED-SCOPE RULES

A task is mixed-scope when it touches both backend and frontend files.
This happens most often with new-feature and modification tasks.

### Rule 4.1 — Both guide skills are required

Load the backend guide first. Load the frontend guide when UI work begins.
Do not skip either. Both must be read in full before the relevant phase starts.

| Primary type | Backend guide | Frontend guide |
|---|---|---|
| new-feature | new-feature-guide | frontend-new-component-guide (Phase 4) |
| modification (full-stack) | modification-guide | frontend-modification-guide (when frontend files are in scope) |
| bug-fix (full-stack) | bug-fix-guide | frontend-bug-fix-guide (when frontend files are in scope) |

### Rule 4.2 — Gate sequence is cumulative

Run all backend gates for backend files. Run all frontend gates for frontend files.
Do not skip a gate because the other scope's gates passed.
The final gate sequence must include every applicable gate from both scopes.

### Rule 4.3 — Single-file discipline applies across scope boundaries

Complete all backend files and pass all backend gates before starting
any frontend files. Do not interleave backend and frontend changes.

### Rule 4.4 — API additivity is always checked in mixed-scope tasks

Any backend change that modifies an API response shape must be verified as
additive before the frontend work begins. No existing JSON keys may be renamed
or removed. If the frontend must change to accommodate a renamed key — that
frontend update is in scope and must be completed in the same task.

---

## SECTION 5 — HARD RULES (apply to every task, every type)

These rules apply regardless of task type, scope, or guide skill loaded.
They cannot be waived by a task prompt or self-authorised around.

### Rule 5.1 — Session state check is mandatory

Every task must begin by reading `docs/ai/SESSION_STATE.md`.
If the task does not appear in the current priority queue — hard stop.
Do not proceed. Report and await instruction.

### Rule 5.2 — Baseline bouncer before any code change

Run `python core/utils/compliance_bouncer.py --root .` before touching any file.
Record the violation count. This is the inherited baseline.
The task must not increase the violation count.

### Rule 5.3 — High-impact file protection

The following files require explicit task prompt authorisation before modification.
If the task prompt does not explicitly authorise touching them — hard stop.
Produce an impact trace. Await confirmation before proceeding.

```
core/data_access.py
core/interfaces/team_types.py
api/serializers.py
```

### Rule 5.4 — Phase 12 hard stop

Phase 12 (live layer / Numba AOT) has not started.
Any task that requires creating or modifying files in `core/live/` or `api/live/`
is an immediate hard stop. Do not proceed. Report and await instruction.
Do not reference Phase 12 in code comments, docstrings, or log output.

### Rule 5.5 — Zero-Destruction Policy

When modifying any file, every function and method not in the declared
scope of the task must remain 100% intact. Never output placeholder comments
like `# ... existing logic` or `# ... rest stays same`. Write the full file.

### Rule 5.6 — Single-file discipline

One file at a time. Complete all steps (code change + incremental gates) for
file N before touching file N+1. No exceptions. No interleaving.

### Rule 5.7 — AI_MEMORY.md is deprecated

Do not read, write, or reference AI_MEMORY.md. It is deprecated.
The authoritative session source is `docs/ai/SESSION_STATE.md`.

### Rule 5.8 — @schema contract for new frontend types

Any new TypeScript interface added to `frontend/lib/*.ts` that maps to a
backend Pydantic schema in `api/schemas/domain.py` MUST include:
```
/** @schema {PydanticClassName} in {python_file_path} */
```

Any new TypeScript interface that is frontend-only (no Pydantic equivalent,
or a sub-shape of an inline Dict[str, JsonValue] field) MUST include:
```
/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
```

Interfaces without one of these two tags will fail Gate F3.

### Rule 5.9 — duckdb-lint-ops script path

When running Gate 2 manually (outside the pre-commit hook), use this exact path:
```
python core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py --root .
```
The legacy path `core/gen_ai/skills/duckdb-lint-ops/scripts/` does not exist.

### Rule 5.10 — Report format

Every task produces a task report on completion or block.
Use the report format defined in the relevant guide skill's final phase.
No omissions. A task is not complete until the report is produced.

### Rule 5.11 — Mandatory disk verify after every file write

After writing or modifying any file, the agent MUST immediately verify
the write landed correctly on disk before proceeding to the next step.
Verification is not optional and cannot be skipped.

For every file modified, run:

```bash
# Confirm file exists and line count is in expected range
wc -l <filepath>

# Confirm key markers are present
grep -c "<expected_marker>" <filepath>

# Confirm absent identifiers are not present (for strip/refactor tasks)
grep -l "<stripped_identifier>" <filepath> || echo "ABSENT: confirmed"
```

If any check fails:
- STOP immediately
- Do NOT proceed to the next file or next task step
- Report as BLOCKED with exact mismatch details
- Await architect instruction before retrying

A task report MUST include disk verify results for every file modified.
A task marked COMPLETE without disk verify results is invalid.

### Rule 5.12 — Pre-existing dirty files do not constitute a block

Running `git status` before a task will often show files modified outside
task scope. These are pre-existing uncommitted changes that predate the task.
The agent must NOT block on their presence.

The correct behaviour:
- Read `docs/ai/SESSION_STATE.md` — the Pre-Task Dirty File Notice section
  lists all known pre-existing dirty files for the current session.
- Block ONLY if the agent itself modifies a file outside the declared
  task scope during execution.
- To isolate agent-caused changes, use:
  `git diff --name-only` — shows only unstaged changes since last stage point.

Blocking on pre-existing dirty files is a false positive. Do not do it.

---

## SECTION 6 — QUICK REFERENCE CARD

Cut to this section if you need a fast answer.

```
WHAT TYPE IS MY TASK?
─────────────────────
Fixing wrong behaviour?              → bug-fix
Intentional logic/config change?     → modification
Structure only, same behaviour?      → refactor
New function/endpoint/renderer?      → new-feature
Frontend component bug only?         → frontend-bug-fix
Changing existing frontend only?     → frontend-modification
Creating new frontend component?     → frontend-new-component
Fixing a validator script?           → validator-fix / infra
Updating a guide SKILL.md?           → guide-update / infra

WHICH GUIDE DO I LOAD?
──────────────────────
bug-fix (backend)          → guides/backend/bug-fix-guide/SKILL.md
modification (backend)     → guides/backend/modification-guide/SKILL.md
refactor                   → guides/backend/refactor-guide/SKILL.md
new-feature                → guides/backend/new-feature-guide/SKILL.md
                             + guides/frontend/frontend-new-component-guide/SKILL.md (Phase 4)
frontend-bug-fix           → guides/frontend/frontend-bug-fix-guide/SKILL.md
frontend-modification      → guides/frontend/frontend-modification-guide/SKILL.md
frontend-new-component     → guides/frontend/frontend-new-component-guide/SKILL.md
infra / tooling            → no guide — bouncer + Gate 5 + Gate 6 only

WHICH STANDARDS FILE DO I ATTACH?
──────────────────────────────────
Backend tasks              → ENGINEERING_STANDARDS_BACKEND.md
Frontend tasks             → ENGINEERING_STANDARDS_FRONTEND.md
Mixed / new-feature        → BOTH

WHICH GATES RUN?
────────────────
core/ touched              → Gate 1
engines/calculators/       → Gate 2
manifest/formats/engines   → Gate 3
serializers/schemas        → Gate 4
frontend/ .tsx/.ts         → Gate F1, F2
any frontend/              → Gate F3 (always-on for frontend)
ALWAYS                     → Gate 5, Gate 6

HARD STOPS — NO EXCEPTIONS
───────────────────────────
Task not in SESSION_STATE?          → Stop at start (TASK_RUNNER handles this in Phase 1)
Touching core/data_access.py etc    → Stop — need explicit authorisation
Scope touches core/live/ or api/live/ → Stop — Phase 12 not started
Any gate FAIL?                      → Stop on that file — fix before continuing
Final bouncer FAIL?                 → Task is BLOCKED — do not mark complete
```

---

## SECTION 7 — SKILL REGISTRY (all paths, authoritative)

### Guide Skills

| Skill | Path |
|---|---|
| bug-fix-guide | `core/gen_ai/skills/guides/backend/bug-fix-guide/SKILL.md` |
| modification-guide | `core/gen_ai/skills/guides/backend/modification-guide/SKILL.md` |
| refactor-guide | `core/gen_ai/skills/guides/backend/refactor-guide/SKILL.md` |
| new-feature-guide | `core/gen_ai/skills/guides/backend/new-feature-guide/SKILL.md` |
| duckdb-lint-ops | `core/gen_ai/skills/guides/backend/duckdb-lint-ops/SKILL.md` |
| context-loader | `core/gen_ai/skills/guides/backend/context-loader/SKILL.md` |
| frontend-bug-fix-guide | `core/gen_ai/skills/guides/frontend/frontend-bug-fix-guide/SKILL.md` |
| frontend-modification-guide | `core/gen_ai/skills/guides/frontend/frontend-modification-guide/SKILL.md` |
| frontend-new-component-guide | `core/gen_ai/skills/guides/frontend/frontend-new-component-guide/SKILL.md` |

### Validator Skills (Scripts)

| Gate | Script Path |
|---|---|
| Gate 1 — boundary-sentinel | `core/gen_ai/skills/validators/backend/boundary-sentinel/scripts/run_sentinel.py` |
| Gate 2 — duckdb-lint-ops | `core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py` |
| Gate 3 — manifest-contract-verifier | `core/gen_ai/skills/validators/backend/manifest-contract-verifier/scripts/run_verifier.py` |
| Gate 4 — serialization-guard | `core/gen_ai/skills/validators/backend/serialization-guard/scripts/run_lint.py` |
| Gate F1 — frontend-lint-sentinel | `core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/scripts/run_frontend_lint.py` |
| Gate F2 — frontend-paradigm-sentinel | `core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/scripts/run_frontend_paradigm.py` |
| Gate F3 — frontend-type-sync-guard | `core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/scripts/run_type_sync.py` |
| Gate 3.5 — event-state-linter (DORMANT) | `core/gen_ai/skills/validators/backend/event-state-linter/scripts/run_lint.py` |
| Gate 5 — paradigm-sentinel | `core/gen_ai/skills/validators/backend/paradigm-sentinel/SKILL.md` |
| Gate 6 — compliance-bouncer | `core/utils/compliance_bouncer.py` |

### Orchestration

| Skill | Path |
|---|---|
| task-runner | `docs/ai/TASK_RUNNER.md` |
| task-input  | `taskFile.md` (project root — not committed) |

### Doc Management

| File | Path |
|---|---|
| Post-Task Checklist | `docs/ai/POST_TASK_CHECKLIST.md` |
| Task Runner | `docs/ai/TASK_RUNNER.md` |
| Backlog | `docs/ai/BACKLOG.md` |

### DuckDB Query Tool

| Tool | Path |
|---|---|
| query_duckdb.py | `core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/query_duckdb.py` |

### Session / Standards Files

| File | Path |
|---|---|
| Session State | `docs/ai/SESSION_STATE.md` |
| Backend Standards | `docs/guides/ENGINEERING_STANDARDS_BACKEND.md` |
| Frontend Standards | `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md` |
| This file | `docs/ai/TASK_PROTOCOL.md` |

---

*Last updated: 2026-03-09*
*Update this file whenever a new guide skill is added, a gate path changes,*
*or a new hard rule is introduced. Version this file alongside SESSION_STATE.md.*
