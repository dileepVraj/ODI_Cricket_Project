---
name: bug-fix-guide
description: Enforcing checkpoint guide for bug-fix tasks in the cricket algo-trading platform. Use when an agent must execute a mandatory, sequential, no-skip bug-fix workflow with hard stops, gate enforcement, escalation reporting, and final task reporting.
---

# Bug-Fix Guide

This is an enforcing guide skill - not instructional prose. It is a mandatory checkpoint script that an AI agent reads at the start of any bug-fix task and cannot bypass. Every step is a hard checkpoint. The agent cannot proceed past a checkpoint until it is complete.

## Purpose statement

This guide governs all bug-fix tasks on the cricket algo-trading platform. It is enforcing, not instructional. An agent that reads this file must execute every checkpoint in sequence. No step may be skipped, condensed, or self-authorised around.

---

## PHASE 0 - PRE-CONDITIONS (all must complete before any code is touched)

### Checkpoint 0.1 - Session state confirmation

Read docs/ai/SESSION_STATE.md. Confirm this bug-fix task appears in the current priority queue. If it does not - hard stop. Do not proceed. Report that the task is not in the priority queue and await instruction.

### Checkpoint 0.2 - Standards file

Confirm docs/guides/ENGINEERING_STANDARDS_BACKEND.md is attached and has been read in full. If not - read it now before proceeding.

### Checkpoint 0.3 - Baseline bouncer

Run:

```bash
python core/utils/compliance_bouncer.py --root .
```

Record violation count. This is the inherited baseline. Do not fix pre-existing violations in this task unless they are in the exact file being fixed. Document the count in the task report.

### Checkpoint 0.4 - Scope declaration

State explicitly: which file(s) are in scope for this bug fix. List every layer touched: `core/`, `calculators/`, `engines/`, `services/`, `api/`, `frontend/`. If scope is unclear - hard stop. Do not guess scope. Await clarification.

### Checkpoint 0.5 - Layer role classification

For every file in scope, classify its layer role using the PART 0 table from the standards file:

| File | Layer Role | Mandates That Apply |
|------|-----------|---------------------|
| [file] | [Domain Core / Interface Adapter / Data Access / UI Adapter / ETL / Live Layer] | [1,2,3,4 / 2,4 / 4 / 5,6] |

This table must be complete before proceeding. Every file gets a row.

### Checkpoint 0.6 - High-impact file check

Check: does scope touch `core/data_access.py`, `core/interfaces/team_types.py`, or `api/serializers.py`?
- If yes and the current task prompt explicitly authorises it -> document and proceed
- If yes and the task prompt does NOT explicitly authorise it -> hard stop. Produce impact trace. Await explicit confirmation before proceeding.
- If no -> document "none" and proceed.

### Checkpoint 0.7 - Dependency scan

For every file in scope, list every other file in the codebase that imports from it. Use grep or equivalent. This is the blast radius if the fix has unintended side effects. Document the full list. Do not proceed without completing this scan.

---

## PHASE 1 - EXECUTION (single-file-at-a-time discipline)

One file at a time. Complete all steps for file N before touching file N+1. No exceptions.

### Step 1.1 - Reproduce

Document the exact reproduction steps for the bug. What input triggers it? What is the observed output? What is the expected output? Write this down before touching any code.

### Step 1.2 - Isolate

Identify the exact file and line where the defect originates. State it explicitly. Then:
- Re-confirm the layer role of this file (from Checkpoint 0.5)
- Ask: is this bug itself a mandate violation? (e.g. `iterrows` in Domain Core = Mandate 3 violation, infrastructure import in Domain Core = Mandate 2 violation)
- If yes: the fix must resolve the mandate violation, not work around it. A workaround that leaves the violation in place is not a valid fix.

### Step 1.3 - Hypothesise root cause

Write the root cause hypothesis before writing any fix. One sentence minimum. This forces diagnosis before implementation. If you cannot state a root cause - do not proceed. Investigate further.

### Step 1.4 - Fix minimal surface

Fix the minimum code required to resolve the bug. Do not refactor adjacent code. Do not improve unrelated logic. Do not rename variables that are not part of the bug. Scope creep at this step is a hard stop.

The fix must comply with all mandates applicable to this file's layer role (from Step 1.2). Specifically check:
- Domain Core file? -> No I/O, no infrastructure imports, no side effects, vectorised operations only, full type annotations, no `Any`, no UI strings, no hardcoded literals
- Interface Adapter? -> No Domain Core logic leaking in, full type annotations
- Any file? -> SRP - the fix must not give the function a second responsibility

### Step 1.5 - Run incremental gates

After fixing this file, before touching any other file, run all applicable gates:

```text
GATE 1 - boundary-sentinel
Trigger: file is in core/
Path: core/gen_ai/skills/validators/backend/boundary-sentinel/
Run: python core/gen_ai/skills/validators/backend/boundary-sentinel/scripts/run_sentinel.py --root . --paths core/

GATE 2 - duckdb-lint-ops
Trigger: file is in calculators/, engines/, or services/
Path: core/gen_ai/skills/guides/backend/duckdb-lint-ops/
Run: python core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py --root .

GATE 3 - manifest-contract-verifier
Trigger: file is manifest.py or engine file in formats/
Path: core/gen_ai/skills/validators/backend/manifest-contract-verifier/

GATE 4 - serialization-guard
Trigger: file is api/serializers.py or engine return type changed
Path: core/gen_ai/skills/validators/backend/serialization-guard/

GATE 5 - paradigm-sentinel
Trigger: always, after all primary gates
Path: core/gen_ai/skills/validators/backend/paradigm-sentinel/
```

Record each gate result. A FAIL on any gate = hard stop on this file. Fix the violation before moving to any other file.

### Step 1.6 - Verify adjacent behaviour

Check the dependency scan from Checkpoint 0.7. For every file that imports from the fixed file: does the fix break its expected inputs? If yes - that file is now in scope. Return to Checkpoint 0.5 and classify it. Then apply Steps 1.1-1.5 to it.

### Step 1.7 - Repeat for next file

Only after Steps 1.1-1.6 are complete and all incremental gates pass for the current file: move to the next file in scope.

---

## PHASE 2 - FINAL GATE SEQUENCE

After all files are fixed and all incremental gates have passed per file, run the full gate sequence once more as a complete final check:

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

If any gate fails at this stage - task status is BLOCKED. Do not mark complete. Produce escalation report.

---

## PHASE 3 - HARD STOPS AND ESCALATION

Any of the following conditions fires an immediate hard stop. Work halts. An escalation report is produced. No self-authorised workarounds.

| Trigger | Stop condition |
|---|---|
| Task not in SESSION_STATE priority queue | Stop at Checkpoint 0.1 |
| Scope unclear - cannot list files confidently | Stop at Checkpoint 0.4 |
| High-impact file in scope without explicit task prompt authorisation | Stop at Checkpoint 0.6 |
| Bug is a mandate violation and fix attempts to work around rather than resolve it | Stop at Step 1.4 |
| Scope creep - fix requires touching files not declared in Checkpoint 0.4 | Stop at Step 1.4, reclassify scope |
| Incremental gate FAIL | Stop on that file at Step 1.5 |
| Final gate FAIL | Stop at Phase 2 |
| Ambiguous type signature in a shared interface requiring a guess | Stop at Step 1.4 |
| Test breakage after fix | Stop at Step 1.6 - root-cause, do not ship workaround |
| Live Layer file detected in scope | Stop - Phase 12 not started, await instruction |

Escalation report format - produce this for every hard stop:

```text
## Escalation Report
Task ID: [from SESSION_STATE]
Task type: bug-fix
Timestamp: [when stop occurred]

### Stop trigger
[Which hard stop condition fired - exact trigger from table above]

### Context at time of stop
- File being worked on: [file path]
- Phase and step: [e.g. Phase 1, Step 1.4]
- Gate being run (if applicable): [gate name + result]

### What was found
[Detailed description - exact violation, conflict, ambiguity, or scope drift found]

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

## PHASE 4 - TASK REPORT

Produce this report upon task completion or block. No omissions.

```text
## Task Report
Task type: bug-fix
Task ID: [from SESSION_STATE backlog]

### Pre-condition snapshot
- SESSION_STATE check: [confirmed in queue]
- Standards file attached: ENGINEERING_STANDARDS_BACKEND.md
- Baseline bouncer: [PASS/FAIL - N violations inherited]
- Files in scope: [list]
- Layer role classifications:
  | File | Layer Role | Mandates Applied |
  |------|-----------|-----------------|
  | [file] | [role] | [mandates] |
- Dependency scan:
  | File | Imported by |
  |------|------------|
  | [file] | [list of importers] |
- High-impact files touched: [none / file + impact trace]

### Execution log
| File | What changed | Root cause resolved | Incremental gates |
|------|-------------|--------------------|--------------------|
| [file] | [description] | [yes/no + explanation] | [G1:PASS G2:PASS ...] |

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
- Violations introduced by this task: [0 - confirmed]
- Scope drift: [none / description]
- Downstream impact: [none / files affected + how resolved]

### Status
[COMPLETE / BLOCKED - reason + see escalation report]
```

---


