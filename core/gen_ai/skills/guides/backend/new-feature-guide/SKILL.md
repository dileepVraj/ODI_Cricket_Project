---
name: new-feature-guide
description: Enforcing checkpoint guide for new feature implementation tasks in the cricket algo-trading platform. Use when an agent must execute a mandatory outside-in workflow with hard checkpoints, gate enforcement, escalation reporting, and task reporting.
---

# New-Feature Guide

This is an enforcing guide skill - not instructional prose. It is a mandatory checkpoint script that an AI agent reads at the start of any new feature implementation task and cannot bypass. Every step is a hard checkpoint. The agent cannot proceed past a checkpoint until it is complete.

## Purpose statement

This guide governs all new feature implementation tasks on the cricket algo-trading platform. It is enforcing, not instructional. An agent that reads this file must execute every checkpoint in sequence. No step may be skipped, condensed, or self-authorised around. The outside-in sequence is non-negotiable - contract first, implementation second, truth bridge third, UI last.

---

## PHASE 0 - PRE-CONDITIONS (all must complete before any code is touched)

### Checkpoint 0.1 - Session state confirmation

Read docs/ai/SESSION_STATE.md. Confirm this new feature task appears in the current priority queue. If it does not - hard stop. Do not proceed. Report that the task is not in the priority queue and await instruction.

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

Record violation count. This is the inherited baseline. Do not fix pre-existing violations in this task unless they are in files directly involved in the new feature. Document the count in the task report.

### Checkpoint 0.4 - Scope declaration

State explicitly every file that will be created or modified to implement this feature. Organise by layer:
- Contract layer: `manifest.py`, `api/schemas/`
- Engine layer: `formats/{fmt}/engines/`, `core/interfaces/`
- Test layer: `tests/`
- UI layer: `frontend/components/renderers/`, `frontend/components/`, `frontend/lib/`

If scope is unclear - hard stop. Do not guess. Await clarification.

### Checkpoint 0.5 - Layer role classification

For every file in scope, classify its layer role using the PART 0 table from the standards file:

| File | Layer Role | Mandates That Apply |
|------|-----------|---------------------|
| [file] | [Domain Core / Interface Adapter / Data Access / UI Adapter / ETL / Live Layer] | [1,2,3,4 / 2,4 / 4 / 5,6] |

This table must be complete before proceeding. Every file gets a row. New files get a row too - classify them by what their job will be, not where they currently exist.

### Checkpoint 0.6 - PART 0 mandate pre-check

For every new file being created, state explicitly which mandates apply based on its layer role and confirm the design intent satisfies them before any code is written:

- New Domain Core file (engine, calculator, service)?
  -> Mandate 1: Will it be a pure function? No I/O, no side effects, no global state?
  -> Mandate 2: Will it have zero infrastructure imports?
  -> Mandate 3: Will all multi-row operations be vectorised? No `iterrows`, no `itertuples`?
  -> Mandate 4: Does each function have exactly one responsibility - describable without "and"?
- New Interface Adapter file (serializer, schema, route)?
  -> Mandate 2: No Domain Core logic leaking in?
  -> Mandate 4: SRP enforced?
- New UI Adapter file (React component, renderer)?
  -> Mandate 4: SRP - one renderer, one output type?
- Live Layer file?
  -> Hard stop - Phase 12 not started. Do not create Live Layer files. Await instruction.

This pre-check must be documented before Step 1.1 begins.

### Checkpoint 0.7 - High-impact file check

Check: does scope touch `core/data_access.py`, `core/interfaces/team_types.py`, or `api/serializers.py`?
- If yes and the current task prompt explicitly authorises it -> document and proceed
- If yes and the task prompt does NOT explicitly authorise it -> hard stop. Produce impact trace. Await explicit confirmation before proceeding.
- If no -> document "none" and proceed.

### Checkpoint 0.8 - Dependency scan

For every existing file being modified, list every other file in the codebase that imports from it. Use grep or equivalent. New files have no importers yet - document as "new file, no existing importers." Do not proceed without completing this scan.

---

## PHASE 1 - CONTRACT (must be complete and confirmed before any implementation)

The outside-in sequence is law. Nothing is implemented until the contract exists and is confirmed correct.

One file at a time. Complete all steps for file N before touching file N+1. No exceptions.

### Step 1.1 - Define manifest contract

Update `manifest.py` to register the new feature:
- Define the endpoint key
- Define `required_context` fields
- Define `engine_class` and `engine_method`
- Define `output_type`

No implementation code is written at this step. Manifest only.

Run incremental gates after this file:

```text
GATE 3 - manifest-contract-verifier
Path: core/gen_ai/skills/validators/backend/manifest-contract-verifier/
GATE 5 - paradigm-sentinel
Path: core/gen_ai/skills/validators/backend/paradigm-sentinel/
GATE 6 - compliance-bouncer (interim check)
Command: python core/utils/compliance_bouncer.py --root .
```

PASS required on all three before proceeding to Step 1.2.

### Step 1.2 - Define API schema

Update or create files in `api/schemas/` to define:
- Input Pydantic model - all fields typed, no `Any`
- Output Pydantic model - exact structure the engine will return

This is the contract the Truth Bridge will enforce. It must be precise.

Run incremental gates after this file:

```text
GATE 4 - serialization-guard
Path: core/gen_ai/skills/validators/backend/serialization-guard/
GATE 5 - paradigm-sentinel
GATE 6 - compliance-bouncer (interim check)
```

PASS required on all three before proceeding to Phase 2.

### Step 1.3 - Contract confirmation checkpoint

Before any engine code is written, state explicitly:
- Manifest entry is complete and gate-verified
- Input schema is defined - list every field and type
- Output schema is defined - list every field and type
- The engine method signature that will satisfy this contract

If any of these cannot be stated clearly - hard stop. Do not proceed to Phase 2. Resolve the contract ambiguity first.

---

## PHASE 2 - IMPLEMENTATION (engine logic only - after contract is confirmed)

One file at a time. Complete all steps for file N before touching file N+1. No exceptions.

### Step 2.1 - ABC Interface compliance check

Before writing the concrete engine, confirm:
- Does `core/interfaces/` have an ABC that this engine must satisfy?
- If yes - read it. The concrete implementation must satisfy every abstract method.
- If the ABC needs updating to accommodate this feature - that is a separate file, follow single-file discipline, run incremental gates before proceeding.

### Step 2.2 - Implement engine logic

Write the analytical logic in `formats/{fmt}/engines/`. Apply all Domain Core mandates:
- Mandate 1: Pure function - data in, results out, no side effects
- Mandate 2: Zero infrastructure imports - no `duckdb`, `fastapi`, `os`, `pathlib`
- Mandate 3: All multi-row operations vectorised - no `iterrows`, no `itertuples`
- Mandate 4: Each method has one responsibility - describe it without "and"
- Typed Truth: full type annotations, no `Any`, no `object`, no `Dict[str, Any]`
- Visual Silence: return raw primitives and TypedDicts only - no UI strings, no labels
- Zero-Literal: no hardcoded cricket constants - all via `manifest.py` or `self.rules`
- Derivative Literal: no raw numeric coefficients - all named constants in manifest

Run incremental gates after this file:

```text
GATE 1 - boundary-sentinel
Path: core/gen_ai/skills/validators/backend/boundary-sentinel/
GATE 2 - duckdb-lint-ops
Path: core/gen_ai/skills/guides/backend/duckdb-lint-ops/
Run: python core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py --root .
GATE 5 - paradigm-sentinel
GATE 6 - compliance-bouncer (interim check)
```

PASS required on all before proceeding.

### Step 2.3 - Verify contract satisfaction

After engine is implemented, explicitly verify:
- Does the engine method return exactly the structure defined in the output schema from Step 1.2?
- Does the engine method accept exactly the inputs defined in the input schema from Step 1.2?
- If there is any mismatch - fix it before proceeding. Do not adjust the schema to match a wrong implementation. The schema is the contract. The implementation must satisfy it.

---

## PHASE 3 - TRUTH BRIDGE (regression test)

### Step 3.1 - Write regression test

Add a regression test in `tests/` that:
- Calls the engine method with known inputs
- Asserts the return value matches exactly the structure promised by the output Pydantic schema from Step 1.2
- Uses no hardcoded format keys as magic strings - define a `TEST_FORMAT` constant
- Does not test CSS, styling, or third-party behaviour

This test is the Truth Bridge - it permanently asserts that the engine output and the API contract stay in sync. If the engine changes, this test breaks. That is by design.

Run incremental gates after this file:

```text
GATE 5 - paradigm-sentinel
GATE 6 - compliance-bouncer (interim check)
```

### Step 3.2 - Run the test

Execute the regression test. It must pass before proceeding to Phase 4.
If it fails - stop. Do not proceed to UI. Root-cause the failure. Fix engine or schema as appropriate, then re-run gates before proceeding.

---

## PHASE 4 - UI IMPLEMENTATION

### Step 4.1 - Renderer component

Implement the Next.js renderer component in `frontend/components/renderers/`. Apply all UI Adapter mandates:
- Mandate 4: One renderer file, one `output_type` - SRP enforced
- Renderer MUST handle null, undefined, or empty data gracefully - use `<EmptyState />`
- Silent failure (returning `null` without fallback) is forbidden
- No `Any` in TypeScript types
- No inline `@keyframes` - use design system animation classes only
- Icons from `lucide-react` only - no other icon packages
- Numeric data uses `.font-numeric` class or `data-numeric="true"`

Run incremental gates after this file:

```text
GATE 5 - paradigm-sentinel
GATE 6 - compliance-bouncer (interim check)
```

### Step 4.2 - Register in FunctionRenderer

Add the new `output_type` case to `frontend/components/renderers/FunctionRenderer.tsx`. One change only - add the case and import. Do not refactor anything else in this file.

Run incremental gates after this file:

```text
GATE 5 - paradigm-sentinel
GATE 6 - compliance-bouncer (interim check)
```

### Step 4.3 - API response additivity check

Confirm the new feature's API response is purely additive:
- No existing JSON keys renamed
- No existing JSON keys removed
- If the frontend consuming existing keys must change - that work is in scope and must be completed in this task. One file at a time.

---

## PHASE 5 - FINAL GATE SEQUENCE

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

## PHASE 6 - HARD STOPS AND ESCALATION

Any of the following conditions fires an immediate hard stop. Work halts. An escalation report is produced. No self-authorised workarounds.

| Trigger | Stop condition |
|---|---|
| Task not in SESSION_STATE priority queue | Stop at Checkpoint 0.1 |
| Scope unclear - cannot list files confidently | Stop at Checkpoint 0.4 |
| Live Layer file required by feature | Stop at Checkpoint 0.6 - Phase 12 not started |
| High-impact file in scope without explicit task prompt authorisation | Stop at Checkpoint 0.7 |
| Contract ambiguous - schema or manifest incomplete | Stop at Step 1.3 |
| Implementation started before contract confirmed | Stop immediately - revert to Phase 1 |
| Engine return does not match output schema | Stop at Step 2.3 - fix before proceeding |
| Truth Bridge test fails | Stop at Step 3.2 - root-cause, do not proceed to UI |
| API response removes or renames existing keys | Stop at Step 4.3 - additive only |
| Scope creep - files touched outside declared scope | Stop immediately, reclassify scope |
| Incremental gate FAIL | Stop on that file |
| Final gate FAIL | Stop at Phase 5 - task is BLOCKED |
| Ambiguous type signature in shared interface requiring a guess | Stop - flag for human decision |
| New Domain Core file contains infrastructure import | Stop at Step 2.2 - Mandate 2 violation |
| `iterrows` or `itertuples` in engine code | Stop at Step 2.2 - Mandate 3 violation |

Escalation report format - produce this for every hard stop:

```text
## Escalation Report
Task ID: [from SESSION_STATE]
Task type: new-feature
Timestamp: [when stop occurred]

### Stop trigger
[Which hard stop condition fired - exact trigger from table above]

### Context at time of stop
- File being worked on: [file path]
- Phase and step: [e.g. Phase 2, Step 2.2]
- Gate being run (if applicable): [gate name + result]

### What was found
[Detailed description - exact violation, conflict, ambiguity, or scope drift found]

### Files already created or modified before stop
[List every file changed before the stop occurred]

### State of those files
[PASS (incremental gates passed) / modified-but-ungated / reverted]

### Decision required
[The exact question that needs a human answer before work can resume]

### Resumption instruction
[What the agent needs to be explicitly told to continue safely]
```

---

## PHASE 7 - TASK REPORT

Produce this report upon task completion or block. No omissions.

```text
## Task Report
Task type: new-feature
Task ID: [from SESSION_STATE backlog]

### Pre-condition snapshot
- SESSION_STATE check: [confirmed in queue]
- Standards files attached: ENGINEERING_STANDARDS_BACKEND.md, ENGINEERING_STANDARDS_FRONTEND.md
- Baseline bouncer: [PASS/FAIL - N violations inherited]
- Files in scope: [list - created and modified]
- Layer role classifications:
  | File | Layer Role | Mandates Applied |
  |------|-----------|-----------------|
  | [file] | [role] | [mandates] |
- PART 0 mandate pre-check: [confirmed per layer role]
- Dependency scan:
  | File | Imported by |
  |------|------------|
  | [file] | [list of importers / new file - no importers] |
- High-impact files touched: [none / file + impact trace]

### Contract snapshot (Phase 1)
- Manifest entry: [endpoint key, output_type, engine_class, engine_method]
- Input schema: [fields + types]
- Output schema: [fields + types]
- Contract confirmed at Step 1.3: [yes]

### Execution log
| File | Phase/Step | What changed | Incremental gates |
|------|-----------|-------------|-------------------|
| [file] | [e.g. Phase 2, Step 2.2] | [description] | [G1:PASS G2:PASS ...] |

### Truth Bridge
- Test file: [path]
- Test result: [PASS]

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
- API additivity confirmed: [yes - no existing keys renamed or removed]

### Status
[COMPLETE / BLOCKED - reason + see escalation report]
```
