---
name: refactor-guide
description: Enforcing checkpoint guide for refactoring tasks in the cricket algo-trading platform. Use when an agent must execute a mandatory, no-behaviour-change structural refactor workflow with hard checkpoints, gate enforcement, escalation reporting, and parity verification.
---

# Refactor Guide

This is an enforcing guide skill - not instructional prose. It is a mandatory checkpoint script that an AI agent reads at the start of any refactoring task and cannot bypass. Every step is a hard checkpoint. The agent cannot proceed past a checkpoint until it is complete.

## Purpose statement

This guide governs all refactoring tasks on the cricket algo-trading platform. It is enforcing, not instructional. An agent that reads this file must execute every checkpoint in sequence. No step may be skipped, condensed, or self-authorised around. The non-negotiable constraint of every refactor is: behaviour is identical before and after. No logic changes. No output changes. No contract changes. Structure changes only.

---

## PHASE 0 - PRE-CONDITIONS (all must complete before any code is touched)

### Checkpoint 0.1 - Session state confirmation

Read docs/ai/SESSION_STATE.md. Confirm this refactor task appears in the current priority queue. If it does not - hard stop. Do not proceed. Report that the task is not in the priority queue and await instruction.

### Checkpoint 0.2 - Standards file

Confirm docs/guides/ENGINEERING_STANDARDS_BACKEND.md is attached and has been read in full. If not - read it now before proceeding.

### Checkpoint 0.3 - Baseline bouncer

Run:

```bash
python core/utils/compliance_bouncer.py --root .
```

Record violation count. This is the inherited baseline. Document it in the task report. Note: a refactor task may legitimately reduce the violation count - this is expected and welcome. It must never increase it.

### Checkpoint 0.4 - Scope declaration

State explicitly every file that will be modified, moved, renamed, split, or deleted as part of this refactor. If scope is unclear - hard stop. Do not guess scope. Await clarification.

### Checkpoint 0.5 - Full impact trace

This is the most critical pre-condition for a refactor. For every file in scope, produce a complete impact trace:
- Every file that imports from it
- Every file that depends on its public interface (function signatures, class names, TypedDict keys)
- Every test that references it

Use grep or equivalent. Document the full list. This is not optional. A refactor without a complete impact trace is a blind refactor - hard stop if this cannot be completed.

### Checkpoint 0.6 - Layer role classification

For every file in scope, classify its current layer role using the PART 0 table from the standards file:

| File | Current Layer Role | Mandates That Apply |
|------|-------------------|---------------------|
| [file] | [Domain Core / Interface Adapter / Data Access / UI Adapter / ETL / Live Layer] | [1,2,3,4 / 2,4 / 4 / 5,6] |

Then answer: does this refactor move any code from one layer to another?
- If yes -> the code being moved immediately inherits the mandate set of its destination layer. State the new layer role and new mandates explicitly before proceeding.
- If no -> document "no layer movement" and proceed.

This is not a formality. Code moved from `api/` into `engines/` becomes Domain Core and immediately inherits Mandates 1, 2, 3, and 4. The refactor is not complete until it satisfies those mandates.

### Checkpoint 0.7 - High-impact file check

Check: does scope touch `core/data_access.py`, `core/interfaces/team_types.py`, or `api/serializers.py`?
- If yes and the current task prompt explicitly authorises it -> document and proceed
- If yes and the task prompt does NOT explicitly authorise it -> hard stop. Produce impact trace. Await explicit confirmation before proceeding.
- If no -> document "none" and proceed.

### Checkpoint 0.8 - No-behaviour-change baseline

Before touching any code, record the current observable behaviour that must be preserved:
- What does each affected function return, given known inputs?
- Are there existing Truth Bridge tests covering these functions? If yes -> list them. They must all still pass after the refactor.
- If no Truth Bridge tests exist -> document this as a risk. The parity verification in Phase 3 becomes the only safety net.

### Checkpoint 0.9 - Deletion inventory

If any file, function, class, or endpoint will be deleted as part of this refactor:
- List every item being deleted
- List every reference to each deleted item across the entire codebase (from Checkpoint 0.5)
- Confirm: zero references will remain in live code after the refactor
- If a reference cannot be updated or removed in this task -> hard stop. Partial deletions that leave dangling references are forbidden.

---

## PHASE 1 - EXECUTION (single-file-at-a-time discipline)

One file at a time. Complete all steps for file N before touching file N+1. No exceptions.

### Step 1.1 - State the structural change

Before touching the file, write down explicitly:
- What is changing structurally? (rename, move, extract, split, inline, reorder)
- What is NOT changing? (logic, output, public interface - unless explicitly in scope)
- If this file's code is moving to a different layer -> restate the new layer role and new mandates that apply

### Step 1.2 - Apply the structural change

Make the structural change to this file only. Apply all mandates applicable to this file's layer role. Specifically:
- Renamed or moved to Domain Core? -> Enforce Mandates 1, 2, 3, 4 immediately
- Any file? -> Full type annotations, no `Any`, no `object`, no `Dict[str, Any]`
- Any analytical file? -> No hardcoded literals, no raw numeric coefficients
- Any Domain Core file? -> No infrastructure imports, no I/O in execute paths, vectorised operations only

Do not fix unrelated violations in the same file unless they are directly in the path of code being refactored. Scope creep is a hard stop.

### Step 1.3 - Update all references

Using the impact trace from Checkpoint 0.5, update every file that references the changed item. One reference file at a time. Run incremental gates after each reference update before moving to the next.

For deletions: remove the reference entirely and verify the referencing file still functions correctly without it.

### Step 1.4 - Run incremental gates

After every single file change (the refactored file and each reference update), run all applicable gates:

```text
GATE 1 - boundary-sentinel
Trigger: file is in core/
Path: core/gen_ai/skills/validators/boundary-sentinel/
Run: python core/gen_ai/skills/validators/boundary-sentinel/scripts/run_sentinel.py --root . --paths core/

GATE 2 - duckdb-lint-ops
Trigger: file is in calculators/, engines/, or services/
Path: core/gen_ai/skills/guides/duckdb-lint-ops/
Run: per SKILL.md in that directory

GATE 3 - manifest-contract-verifier
Trigger: file is manifest.py or engine file in formats/
Path: core/gen_ai/skills/validators/manifest-contract-verifier/

GATE 4 - serialization-guard
Trigger: file is api/serializers.py or engine return type changed
Path: core/gen_ai/skills/validators/serialization-guard/

GATE 5 - paradigm-sentinel
Trigger: always, after all primary gates
Path: core/gen_ai/skills/validators/paradigm-sentinel/
```

Record each gate result. A FAIL on any gate = hard stop on this file. Fix the violation before proceeding to the next file.

### Step 1.5 - Deletion zero-reference verification

If any item was deleted in this step: grep the entire codebase for every reference to the deleted item. The result must be zero. If any references remain - they are now in scope. Return to Step 1.3 and clean them before proceeding.

### Step 1.6 - Repeat for next file

Only after Steps 1.1-1.5 are complete and all incremental gates pass: move to the next file.

---

## PHASE 2 - DATABASE SCHEMA CHANGES (only if refactor touches ETL or DuckDB)

If the refactor does not touch ETL, `json_converter.py`, `refinery_script.py`, or `odi.duckdb` - skip this phase, document "not applicable", and proceed to Phase 3.

If it does touch any of the above:

### Step 2.1 - ETL flow only

Database schema changes MUST flow through:
1. `json_converter.py` modifications
2. `refinery_script.py` modifications
3. Atomic Swap rebuild

Direct schema modifications to `odi.duckdb` are forbidden. Hard stop if this constraint cannot be satisfied.

### Step 2.2 - Mathematical change acknowledgement

If any engine formula was altered (even unintentionally during refactor) - stop. A refactor must not alter mathematical output. If a formula changed, this is no longer a pure refactor - escalate immediately.

---

## PHASE 3 - PARITY VERIFICATION

This phase confirms the non-behaviour-change constraint holds.

### Step 3.1 - Run existing Truth Bridge tests

Run every Truth Bridge test identified in Checkpoint 0.8. Every test must pass. If any test fails - hard stop. The refactor has changed behaviour. Do not ship. Diagnose the regression and fix it before proceeding.

### Step 3.2 - API response parity check

If any API-facing file was refactored, confirm:
- No existing JSON keys renamed
- No existing JSON keys removed
- No change in response structure for any existing endpoint

If any of these are violated - hard stop. API changes during a refactor are out of scope unless explicitly authorised in the task prompt.

### Step 3.3 - Parity confirmed

State explicitly: "Behaviour is identical before and after this refactor." This statement must be supportable by the Truth Bridge test results and the API parity check above.

---

## PHASE 4 - FINAL GATE SEQUENCE

After all files are complete and all incremental gates have passed per file, run the full gate sequence once as the authoritative final check:

```text
GATE 1 - boundary-sentinel    -> PASS required
GATE 2 - duckdb-lint-ops      -> PASS required
GATE 3 - manifest-contract-verifier -> PASS required
GATE 4 - serialization-guard  -> PASS required
GATE 5 - paradigm-sentinel    -> PASS required
GATE 6 - compliance-bouncer   -> PASS: 100% compliance required
```

No gates skipped. No gates omitted. Every gate runs regardless of whether its trigger condition was met during incremental gating. The final run is the authoritative result.
GATE 6 command:

```bash
python core/utils/compliance_bouncer.py --root .
```

If any gate fails - task status is BLOCKED. Do not mark complete. Produce escalation report.

---

## PHASE 5 - HARD STOPS AND ESCALATION

Any of the following conditions fires an immediate hard stop. Work halts. An escalation report is produced. No self-authorised workarounds.

| Trigger | Stop condition |
|---|---|
| Task not in SESSION_STATE priority queue | Stop at Checkpoint 0.1 |
| Scope unclear - cannot list files confidently | Stop at Checkpoint 0.4 |
| Impact trace incomplete - cannot list all dependents | Stop at Checkpoint 0.5 |
| High-impact file in scope without explicit task prompt authorisation | Stop at Checkpoint 0.7 |
| No-behaviour-change baseline cannot be established | Stop at Checkpoint 0.8 |
| Deletion has references that cannot be cleaned in this task | Stop at Checkpoint 0.9 |
| Code moves to new layer - new mandate set not applied | Stop at Step 1.2 |
| Logic change detected during structural refactor | Stop at Step 1.2 - escalate, this is no longer a refactor |
| Scope creep - files touched outside declared scope | Stop immediately, reclassify scope |
| Deletion leaves dangling references after Step 1.5 | Stop at Step 1.5 - clean before proceeding |
| Direct schema modification to odi.duckdb attempted | Stop at Phase 2 - ETL flow only |
| Engine formula altered during refactor | Stop at Step 2.2 - escalate immediately |
| Truth Bridge test fails after refactor | Stop at Step 3.1 - regression detected |
| API response structure changed during refactor | Stop at Step 3.2 - out of scope |
| Incremental gate FAIL | Stop on that file at Step 1.4 |
| Final gate FAIL | Stop at Phase 4 - task is BLOCKED |
| Live Layer file detected in scope | Stop - Phase 12 not started, await instruction |

Escalation report format - produce this for every hard stop:

```text
## Escalation Report
Task ID: [from SESSION_STATE]
Task type: refactor
Timestamp: [when stop occurred]

### Stop trigger
[Which hard stop condition fired - exact trigger from table above]

### Context at time of stop
- File being worked on: [file path]
- Phase and step: [e.g. Phase 1, Step 1.2]
- Gate being run (if applicable): [gate name + result]

### What was found
[Detailed description - exact violation, logic change, regression, or scope drift found]

### Files already modified before stop
[List every file changed before the stop occurred]

### State of those files
[PASS (incremental gates passed) / modified-but-ungated / reverted]

### Decision required
[The exact question that needs a human answer before work can resume]

### Resumption instruction
[What the agent needs to be explicitly told to continue safely]
```

---

## PHASE 6 - TASK REPORT

Produce this report upon task completion or block. No omissions.

```text
## Task Report
Task type: refactor
Task ID: [from SESSION_STATE backlog]

### Pre-condition snapshot
- SESSION_STATE check: [confirmed in queue]
- Standards file attached: ENGINEERING_STANDARDS_BACKEND.md
- Baseline bouncer: [PASS/FAIL - N violations inherited]
- Files in scope: [list - modified, moved, renamed, deleted]
- Full impact trace:
  | File | Dependents |
  |------|-----------|
  | [file] | [list of all files that import or depend on it] |
- Layer role classifications:
  | File | Layer Role | Mandates Applied | Layer movement? |
  |------|-----------|-----------------|-----------------|
  | [file] | [role] | [mandates] | [none / from X to Y] |
- No-behaviour-change baseline: [Truth Bridge tests listed / no tests - risk noted]
- Deletion inventory: [none / items deleted + zero-reference confirmed]
- High-impact files touched: [none / file + impact trace]

### Execution log
| File | Step | Structural change | Layer movement | Incremental gates |
|------|------|------------------|----------------|-------------------|
| [file] | [1.2 / 1.3] | [description] | [none / from->to] | [G1:PASS G2:PASS ...] |

### Parity verification (Phase 3)
- Truth Bridge tests run: [list]
- Truth Bridge results: [all PASS]
- API response parity: [confirmed - no keys renamed or removed]
- Parity statement: [Behaviour is identical before and after this refactor]

### Final gate results
- GATE 1 boundary-sentinel: [PASS/FAIL]
- GATE 2 duckdb-lint-ops: [PASS/FAIL]
- GATE 3 manifest-contract-verifier: [PASS/FAIL]
- GATE 4 serialization-guard: [PASS/FAIL]
- GATE 5 paradigm-sentinel: [PASS/FAIL]
- GATE 6 compliance-bouncer: [PASS/FAIL]

### Hard stops encountered
[none / escalation report above]

### Post-condition snapshot
- Final bouncer result: [PASS - 100% compliance]
- Violations introduced: [0 - confirmed]
- Violations resolved: [N - list them]
- Scope drift: [none / description]
- Dangling references: [none - confirmed]

### Status
[COMPLETE / BLOCKED - reason + see escalation report]
```
