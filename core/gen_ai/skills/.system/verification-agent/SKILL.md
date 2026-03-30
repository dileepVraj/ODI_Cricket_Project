---
name: verification-agent
description: Post-implementation verification subagent. Dispatched by Claude after a task is implemented. Runs all applicable gates, checks acceptance criteria, and returns a structured PASS or FAIL report. Works for both frontend and backend tasks.
---

# Verification Agent

This skill is for a **dispatched subagent** — not for inline Claude use.

Claude dispatches this agent after implementation is complete. The agent verifies the work, reports findings, and exits. It does not fix issues — it only reports them. Claude reads the report and acts.

---

## Context Required from Claude

Claude must provide all of the following when dispatching this agent. Do not proceed if any item is missing — ask Claude to resend with the missing fields.

```
Task ID     : TASK-XXX
Scope       : frontend | backend | both
Files modified:
  - path/to/file1
  - path/to/file2
Acceptance criteria:
  - AC-1: [criterion]
  - AC-2: [criterion]
  ...
```

---

## Step 1 — Read Every Modified File

Read each file listed under "Files modified" in full before running any gate.
Do not skip this. Gate results without reading the code produce useless reports.

---

## Step 2 — Run Gates

Run only the gates that apply to this task's scope. Do not run gates outside scope.

### Frontend Gates

**F1 — Lint Sentinel**
```bash
python core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/scripts/run_frontend_lint.py --root .
```
Pass condition: zero violations.

**F2 — Paradigm Sentinel**
```bash
python core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/scripts/run_frontend_paradigm.py --root .
```
Pass condition: zero violations.

**F3 — Type Sync Guard**
```bash
python core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/scripts/run_type_sync.py --root .
```
Pass condition: zero violations.

**F4 — Visual Acceptance**
Use Playwright to navigate to every route touched by the task.
For each route:
- Take a full-page screenshot
- Compare against the design reference (Stitch spec or spec doc stated in acceptance criteria)
- Flag any layout, colour, spacing, or interaction mismatch

F4 PASS requires every route to visually match its reference. A passing build is not sufficient — the browser must be checked.

### Backend Gates

Run only the gates triggered by the files modified. Use this table:

| Files modified | Gates to run |
|---|---|
| Any file in `core/` | GATE 1 (boundary-sentinel) |
| Any file in `calculators/`, `engines/`, `services/` | GATE 2 (duckdb-lint-ops) |
| `manifest.py` or any engine file in `formats/` | GATE 3 (manifest-contract-verifier) |
| `api/serializers.py` or engine return types | GATE 4 (serialization-guard) |
| Any backend file (always) | GATE 5 (paradigm-sentinel) |
| Any backend file (always, last) | GATE 6 (compliance bouncer) |

Gate commands live in their respective SKILL.md files under:
`core/gen_ai/skills/validators/backend/<gate-name>/SKILL.md`

GATE 6 command (always):
```bash
python core/utils/compliance_bouncer.py --root .
```
Pass condition: `PASS: 100% compliance`.

---

## Step 3 — Check Acceptance Criteria

For each acceptance criterion provided:
- Read the relevant code
- State explicitly: SATISFIED or NOT SATISFIED
- If NOT SATISFIED: quote the specific code or output that shows the gap

Do not infer or assume satisfaction. Only mark SATISFIED if you can point to the exact code or output that proves it.

---

## Step 4 — Write Report

Write the report in this exact format. No prose summaries. No extra sections.

```
VERIFICATION REPORT
===================
Task    : TASK-XXX
Scope   : frontend | backend
Agent   : verification-agent

Gates:
- F1 (lint-sentinel)       : PASS | FAIL — [violation count or "0 violations"]
- F2 (paradigm-sentinel)   : PASS | FAIL — [violation count or "0 violations"]
- F3 (type-sync-guard)     : PASS | FAIL — [violation count or "0 violations"]
- F4 (visual-acceptance)   : PASS | FAIL — routes checked: [list]
- GATE 1 (boundary)        : TRIGGERED | SKIPPED — PASS | FAIL
- GATE 2 (duckdb-lint-ops) : TRIGGERED | SKIPPED — PASS | FAIL
- GATE 3 (manifest)        : TRIGGERED | SKIPPED — PASS | FAIL
- GATE 4 (serialization)   : TRIGGERED | SKIPPED — PASS | FAIL
- GATE 5 (paradigm)        : TRIGGERED | SKIPPED — PASS | FAIL
- GATE 6 (bouncer)         : TRIGGERED | SKIPPED — PASS | FAIL

Acceptance Criteria:
- AC-1: SATISFIED | NOT SATISFIED — [one line of evidence]
- AC-2: SATISFIED | NOT SATISFIED — [one line of evidence]

Failures (leave empty if none):
- [Gate or AC that failed] — [exact file:line or output snippet]

Overall: PASS | FAIL
```

---

## Step 5 — Exit

Return the report to Claude. Do not attempt to fix any issues found.
Do not modify any files.
Do not commit anything.

Claude reads the report and decides next action.

---

## Failure Handling (for Claude, not this agent)

If the report is FAIL:
- Claude reads each failure item
- Claude fixes the specific issues inline
- Claude re-dispatches this agent with the same context
- If the same failure appears 3 times across 3 dispatches — stop and escalate to the human. Do not loop further.
