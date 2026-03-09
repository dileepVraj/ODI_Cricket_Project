---
name: modification-guide
description: Enforcing checkpoint guide for scoped modification tasks in the cricket algo-trading platform. Use when an agent must execute an intentional behavior/logic/configuration change with strict delta control, mandatory gates, downstream verification, and escalation reporting.
---

# Modification Guide

This is an enforcing guide skill - not instructional prose. It is a mandatory checkpoint script that an AI agent reads at the start of any scoped modification task and cannot bypass. Every step is a hard checkpoint. The agent cannot proceed past a checkpoint until it is complete.

## Purpose statement

This guide governs all scoped modification tasks on the cricket algo-trading platform. It is enforcing, not instructional. An agent that reads this file must execute every checkpoint in sequence. No step may be skipped, condensed, or self-authorised around. A modification is a deliberate, intentional change to existing behaviour, logic, or configuration - it is not a bug fix, not a refactor, and not a new feature. The delta must be explicitly scoped and confirmed before any code is touched. Everything outside the declared delta is frozen.

---

## PHASE 0 - PRE-CONDITIONS (all must complete before any code is touched)

### Checkpoint 0.1 - Session state confirmation

Read docs/ai/SESSION_STATE.md. Confirm this modification task appears in the current priority queue. If it does not - hard stop. Do not proceed. Report that the task is not in the priority queue and await instruction.

### Checkpoint 0.2 - Standards files

Confirm both files are attached and have been read in full:

docs/guides/ENGINEERING_STANDARDS_BACKEND.md
docs/guides/ENGINEERING_STANDARDS_FRONTEND.md

If either is missing - read it now before proceeding.

### Checkpoint 0.3 - Baseline bouncer

Run:

```bash
python core/utils/compliance_bouncer.py --root .
```

Record violation count. This is the inherited baseline. Document it in the task report. The modification must not introduce new violations. Pre-existing violations in files being modified must be flagged - they are not in scope to fix unless they are directly in the path of the modification.

### Checkpoint 0.4 - Document current behaviour

Before touching any code, record the current observable behaviour of every file in scope:
- What does each affected function currently do?
- What does it currently return, given known inputs?
- What are its current type signatures?
- Are there existing Truth Bridge tests? If yes -> list them.

This is the baseline. The modification delta is measured against it. If current behaviour cannot be documented - hard stop. Do not modify what you do not understand.

### Checkpoint 0.5 - Scope the delta

State explicitly and precisely what is changing:
- Which file(s) are being modified?
- What specific logic, formula, configuration, or behaviour is changing within each file?
- What is explicitly NOT changing?

Everything not listed in the delta is frozen. Any change outside the declared delta is scope creep - hard stop.

### Checkpoint 0.6 - Layer role classification

For every file in scope, classify its layer role using the PART 0 table from the standards file:

| File | Layer Role | Mandates That Apply |
|------|-----------|---------------------|
| [file] | [Domain Core / Interface Adapter / Data Access / UI Adapter / ETL / Live Layer] | [1,2,3,4 / 2,4 / 4 / 5,6] |

Then check: does the modification introduce any mandate violation in its layer?
- Domain Core modification? -> Must not introduce I/O, infrastructure imports, `iterrows`, `Any`, UI strings, hardcoded literals
- Interface Adapter modification? -> Must not introduce Domain Core logic, must not use `Any`
- Any file? -> Full type annotations on any modified function signature

### Checkpoint 0.7 - Current mandate compliance status

For every file being modified, state its current compliance status:
- Is it currently fully compliant with its applicable mandates?
- If it carries pre-existing violations -> list them explicitly
- The modification must not introduce new violations
- The modification must not intentionally entrench existing violations (e.g. adding more `iterrows` calls to a file that already has them is forbidden even if the file already had a DOD violation)

### Checkpoint 0.8 - High-impact file check

Check: does scope touch `core/data_access.py`, `core/interfaces/team_types.py`, or `api/serializers.py`?
- If yes and the current task prompt explicitly authorises it -> document and proceed
- If yes and the task prompt does NOT explicitly authorise it -> hard stop. Produce impact trace. Await explicit confirmation before proceeding.
- If no -> document "none" and proceed.

### Checkpoint 0.9 - Downstream consumer scan

For every file being modified, list every file that imports from it or depends on its output. Use grep or equivalent. This is the downstream blast radius of the modification. Document the full list. For each downstream consumer, answer: does the modification change what this consumer receives? If yes -> that consumer must be updated in this task. It is now in scope.

### Checkpoint 0.10 - Mathematical change acknowledgement

If the modification changes any engine formula or analytical calculation:
- Acknowledge explicitly that Truth Bridge tests will fail as a result
- State which tests will fail and why
- Confirm that new Golden Master JSON outputs will be generated to baseline the new math
- If this is not a mathematical change -> document "not applicable" and proceed

---

## PHASE 1 - EXECUTION (single-file-at-a-time discipline)

One file at a time. Complete all steps for file N before touching file N+1. No exceptions.

### Step 1.1 - State the delta for this file

Before touching the file, write down explicitly:
- What is changing in this file? (exact function, method, formula, config key)
- What is the current behaviour?
- What will the new behaviour be after the change?
- Which mandates apply to this file's layer role?

### Step 1.2 - Apply the delta

Make only the declared change. Nothing else. Apply all mandates applicable to this file's layer role:
- Domain Core file? -> Pure function, no I/O, no infrastructure imports, vectorised operations, no `Any`, no UI strings, no hardcoded literals, no raw numeric coefficients
- Interface Adapter file? -> No Domain Core logic leaking in, full type annotations
- Any file? -> SRP - the modification must not give any function a second responsibility
- Zero-Destruction Policy -> Never output `# ... existing logic` or `# ... rest stays same`. Every untargeted function must remain 100% intact.

If the modification requires touching code outside the declared delta - hard stop. Reclassify scope before proceeding.

### Step 1.3 - Database schema change (if applicable)

If the modification touches ETL, `json_converter.py`, `refinery_script.py`, or `odi.duckdb`:
- MUST flow through: `json_converter.py` -> `refinery_script.py` -> Atomic Swap rebuild
- Direct schema modification to `odi.duckdb` is forbidden - hard stop if attempted

If not applicable - document "not applicable" and proceed to Step 1.4.

### Step 1.4 - Run incremental gates

After every single file modification, run all applicable gates:

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

Record each gate result. A FAIL on any gate = hard stop on this file. Fix the violation before moving to the next file.

### Step 1.5 - Downstream consumer update

Check the downstream consumer scan from Checkpoint 0.9. For every consumer that receives changed output from this file: update it now. One consumer file at a time. Run incremental gates after each consumer update before moving to the next.

### Step 1.6 - API response additivity check (if applicable)

If the modification touches any API-facing file or changes any engine return type:
- API response changes MUST be additive - no existing JSON keys renamed or removed
- If an existing key must be renamed or removed -> the Next.js frontend consuming that key must be simultaneously updated in this task. It is now in scope. One file at a time.
- If not applicable -> document "not applicable" and proceed.

### Step 1.7 - Repeat for next file

Only after Steps 1.1-1.6 are complete and all incremental gates pass: move to the next file.

---

## PHASE 2 - DOWNSTREAM VERIFICATION

### Step 2.1 - Truth Bridge test handling

Run all Truth Bridge tests identified in Checkpoint 0.4 and Checkpoint 0.10:

If this modification does NOT change mathematical output:
- All existing Truth Bridge tests must still pass
- If any test fails -> hard stop. An unintended behaviour change has occurred. Do not proceed. Root-cause and fix.

If this modification DOES change mathematical output (acknowledged in Checkpoint 0.10):
- Existing Truth Bridge test failures are expected and acknowledged
- Generate new Golden Master JSON outputs to baseline the new math
- Update the Truth Bridge tests to assert the new expected output
- The updated tests must pass before proceeding

### Step 2.2 - Downstream consumer verification

For every downstream consumer updated in Step 1.5:
- Confirm it still functions correctly with the modified input it now receives
- If it has its own Truth Bridge tests -> run them

### Step 2.3 - Modification confirmed

State explicitly:
- What changed: [summary of delta]
- What did not change: [everything outside the delta]
- Mathematical output changed: [yes - Golden Master regenerated / no - Truth Bridge tests passed unchanged]

---

## PHASE 3 - FINAL GATE SEQUENCE

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

## PHASE 4 - HARD STOPS AND ESCALATION

Any of the following conditions fires an immediate hard stop. Work halts. An escalation report is produced. No self-authorised workarounds.

| Trigger | Stop condition |
|---|---|
| Task not in SESSION_STATE priority queue | Stop at Checkpoint 0.1 |
| Current behaviour cannot be documented | Stop at Checkpoint 0.4 |
| Delta scope unclear - cannot state what changes precisely | Stop at Checkpoint 0.5 |
| High-impact file in scope without explicit task prompt authorisation | Stop at Checkpoint 0.8 |
| Downstream consumer scan incomplete | Stop at Checkpoint 0.9 |
| Mathematical change not acknowledged before execution | Stop at Checkpoint 0.10 |
| Modification introduces new mandate violation | Stop at Step 1.2 |
| Modification intentionally entrenches existing violation | Stop at Step 1.2 |
| Scope creep - change touches code outside declared delta | Stop at Step 1.2 - reclassify |
| Direct schema modification to odi.duckdb attempted | Stop at Step 1.3 - ETL flow only |
| Incremental gate FAIL | Stop on that file at Step 1.4 |
| Downstream consumer broken by modification | Stop at Step 1.5 - fix before proceeding |
| API response removes or renames existing key without frontend update | Stop at Step 1.6 |
| Unintended Truth Bridge test failure (non-mathematical change) | Stop at Step 2.1 - regression detected |
| Final gate FAIL | Stop at Phase 3 - task is BLOCKED |
| Live Layer file detected in scope | Stop - Phase 12 not started, await instruction |
| Zero-Destruction Policy violated - existing methods dropped | Stop at Step 1.2 - rewrite in full |

Escalation report format - produce this for every hard stop:

```text
## Escalation Report
Task ID: [from SESSION_STATE]
Task type: modification
Timestamp: [when stop occurred]

### Stop trigger
[Which hard stop condition fired - exact trigger from table above]

### Context at time of stop
- File being worked on: [file path]
- Phase and step: [e.g. Phase 1, Step 1.2]
- Gate being run (if applicable): [gate name + result]

### What was found
[Detailed description - exact violation, unintended change, regression, or scope drift]

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

## PHASE 5 - TASK REPORT

Produce this report upon task completion or block. No omissions.

```text
## Task Report
Task type: modification
Task ID: [from SESSION_STATE backlog]

### Pre-condition snapshot
- SESSION_STATE check: [confirmed in queue]
- Standards files attached: ENGINEERING_STANDARDS_BACKEND.md, ENGINEERING_STANDARDS_FRONTEND.md
- Baseline bouncer: [PASS/FAIL - N violations inherited]
- Files in scope: [list]
- Current behaviour documented: [yes - summary per file]
- Delta scoped: [exact description of what changed]
- Layer role classifications:
  | File | Layer Role | Mandates Applied | Pre-existing violations |
  |------|-----------|-----------------|------------------------|
  | [file] | [role] | [mandates] | [none / list] |
- Downstream consumers:
  | File | Consumers | Consumer updated? |
  |------|----------|-----------------|
  | [file] | [list] | [yes/no/not applicable] |
- High-impact files touched: [none / file + impact trace]
- Mathematical change: [yes - Golden Master regenerated / no - not applicable]

### Execution log
| File | Step | Delta applied | Incremental gates |
|------|------|--------------|-------------------|
| [file] | [1.2 / 1.5] | [description] | [G1:PASS G2:PASS ...] |

### Downstream verification (Phase 2)
- Truth Bridge tests run: [list]
- Truth Bridge outcome: [all PASS unchanged / intentional failures - Golden Master regenerated]
- Golden Master updated: [yes / not applicable]
- Consumer verification: [confirmed / not applicable]
- Modification confirmed statement: [what changed / what did not / mathematical output status]

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
- Pre-existing violations entrenched: [none - confirmed]
- Scope drift: [none / description]
- API additivity: [confirmed - no keys renamed or removed / frontend updated simultaneously]

### Status
[COMPLETE / BLOCKED - reason + see escalation report]
```
