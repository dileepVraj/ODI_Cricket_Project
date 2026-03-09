---
name: frontend-bug-fix-guide
description: Checkpoint workflow for diagnosing and fixing bugs in the Next.js frontend. Enforces frontend standards compliance, correct RCA trace, and frontend gate sequence before task close.
---

# Frontend Bug Fix Guide

Structured checkpoint workflow for all frontend bug-fix tasks. Mirrors the backend bug-fix-guide but with frontend-specific trace paths, mandate checks, and gate sequence.

## Phase 0 — Pre-Conditions (complete before writing any code)

### 0.1 — Standards File
Read `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md` in full before proceeding.

### 0.2 — Session State
Read `docs/ai/SESSION_STATE.md`. Confirm:
- Active Task matches the bug being fixed
- No conflicting in-progress tasks
- No blockers that affect frontend scope

### 0.3 — Baseline Bouncer
Run before touching any file:
```powershell
python core/utils/compliance_bouncer.py --root .
```
Record output. This is your before-snapshot. If bouncer fails at baseline — stop and report. Do not proceed.

### 0.4 — Bug Classification
Classify the bug in one of these categories before starting:
- **A** — UI rendering / display (wrong data shown, missing element)
- **B** — API integration (wrong endpoint, payload mismatch, missing field)
- **C** — State / context (stale data, missing context provider, re-render issue)
- **D** — Accessibility (missing aria, keyboard trap, broken focus)
- **E** — CSS / styling (wrong token, broken layout, z-index conflict)
- **F** — Type error (TypeScript compile error, runtime type mismatch)

---

## Phase 1 — Root Cause Analysis (RCA Trace)

Follow this trace path. Stop at the layer where the bug lives.

```
STEP 1 — Frontend Component
  Is the component reading from the right context/prop?
  Is it rendering the correct field from the API response?
  Is it using the manifest key or a hardcoded string?

STEP 2 — API Client (lib/api.ts)
  Is the correct endpoint being called?
  Is the request payload shaped correctly?
  Is the response being typed correctly against lib/types.ts?

STEP 3 — Backend API Response
  Does the API return the expected shape?
  Check api/serializers.py and the relevant engine return type.

STEP 4 — Engine / Calculator Layer
  Is the engine returning the correct value?
  Check formats/odi/ engine files.

STEP 5 — Data Access Layer
  Is the DAL query returning the correct data?
  Check core/data_access.py queries.
```

Document where the bug lives before writing any fix.

---

## Phase 2 — Mandate Checks (verify these before writing the fix)

Before modifying any file, confirm the fix will comply with all of the following:

| Check | Mandate | Pass Condition |
|-------|---------|----------------|
| M1 | CSS tokens only | Fix uses CSS variables from globals.css — no raw hex, no inline RGB |
| M2 | No domain logic | Fix does not add arithmetic on API response data to a component |
| M3 | Manifest-driven | If fix touches a function/category label — it reads from manifest, not hardcoded |
| M4 | Component SRP | Fix does not give the component a second responsibility |
| M5 | Typed | Fix adds or preserves complete TypeScript types — no `any`, no `unknown` |
| M6 | Accessibility | If fix touches interactive elements — aria-labels and keyboard nav preserved |
| M7 | Registered file | If fix requires touching core/data_access.py, team_types.py, or serializers.py — stop-state-trace-confirm first |

---

## Phase 3 — Gate Sequence (all triggered gates must pass)

Run gates in this order. Record each result.

```
GATE F1 — frontend-lint-sentinel
Trigger: any modification to frontend/ files.
Run: python core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/scripts/run_frontend_lint.py --root .
Pass: zero violations.

GATE F2 — frontend-paradigm-sentinel
Trigger: always after F1 passes.
Run: python core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/scripts/run_frontend_paradigm.py --root .
Pass: zero violations.

GATE F3 — frontend-type-sync-guard
Trigger: always — scans all frontend/lib/*.ts files.
Run: python core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/scripts/run_type_sync.py --root .
Pass: zero violations.

GATE 5 — paradigm-sentinel (backend meta-check)
Trigger: always — catch cross-layer violations.
Follow: core/gen_ai/skills/validators/backend/paradigm-sentinel/SKILL.md

GATE 6 — compliance_bouncer (final gate)
Trigger: always.
Run: python core/utils/compliance_bouncer.py --root .
Pass: PASS: 100% compliance
```

---

## Phase 4 — Task Report

Submit in this format when all gates pass:

```
FRONTEND BUG FIX REPORT
=======================
Task: [one-line description]
Date: [date]
Bug Class: [A/B/C/D/E/F — see Phase 0.4]
RCA Layer: [component / api / serializer / engine / dal]

Baseline Bouncer: [PASS/FAIL — N violations]
Post-Task Bouncer: [PASS/FAIL — N violations — matches baseline: YES/NO]

Frontend Gates:
- GATE F1 (frontend-lint-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE F2 (frontend-paradigm-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE F3 (frontend-type-sync-guard): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 5 (paradigm-sentinel): TRIGGERED — [PASS/FAIL]
- GATE 6 (compliance_bouncer): TRIGGERED — [PASS/FAIL]

Files Modified: [list]
Registered Files Touched: [list or NONE]
Stop-State-Trace-Confirm Used: [YES/NO — which file]

Mandate Checks: [M1–M7 — PASS/SKIP each]
Blockers Hit: [list or NONE]

Status: [COMPLETE / BLOCKED — reason]
```
