---
name: frontend-new-component-guide
description: Checkpoint workflow for creating new React components. Enforces classification, directory placement, renderer lazy loading, accessibility, TypeScript strict compliance, and file size pre-check.
---

# Frontend New Component Guide

Purpose-built workflow for adding a new React component to the frontend. Follow every checkpoint in order — do not skip phases.

## Phase 0 — Pre-Conditions

### 0.1 — Standards File
Read `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md` in full.

### 0.2 — Session State
Confirm Active Task scope, no conflicting tasks.

### 0.3 — Baseline Bouncer
```powershell
python core/utils/compliance_bouncer.py --root .
```

---

## Phase 1 — Component Classification

Classify the new component before creating any file. Pick exactly one:

| Class | Description | Correct Directory |
|-------|-------------|-------------------|
| **layout** | Top-level page structure, wraps other components | `frontend/components/layout/` |
| **renderer** | Renders a specific prediction/report type from manifest | `frontend/components/renderers/` |
| **input** | User input control (text, select, combobox) | `frontend/components/inputs/` |
| **common** | Shared utility component used across categories | `frontend/components/common/` |
| **navigation** | Navigation bars, breadcrumbs, links | `frontend/components/navigation/` |

**Decision gate:** If the component does not fit cleanly into one class — stop. The component may need to be decomposed before creation.

---

## Phase 2 — Directory Placement Check

Place the file in the directory matching the class from Phase 1.

Verify the directory exists:
```powershell
ls frontend/components/<directory>/
```

If the directory does not exist — do NOT create it without architect approval. Placement contract is locked.

---

## Phase 3 — Renderer-Specific Requirements

**Only if component class = renderer:**

| Check | Requirement |
|-------|------------|
| R1 | Register the renderer in `FunctionRenderer.tsx` using `React.lazy()` |
| R2 | Wrap the renderer registration in an `<ErrorBoundary>` component |
| R3 | Register the renderer key in `formats/odi/manifest.py` under the correct function |
| R4 | Add the corresponding TypeScript type in the appropriate `frontend/lib/*.ts` file with the correct JSDoc tag: use `/** @schema {PydanticClassName} in {python_file_path} */` if the interface maps to a backend Pydantic schema in api/schemas/domain.py; use `/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */` if the interface is a frontend-only type or a sub-shape of an inline Dict[str, JsonValue] field with no standalone Pydantic class |
| R5 | Test that the renderer renders when the matching manifest key is returned from the API |

---

## Phase 4 — Layout-Specific Requirements

**Only if component class = layout:**

| Check | Requirement |
|-------|------------|
| L1 | Layout component reads data from React context — NOT from props passed by parent |
| L2 | Layout component does NOT import from `lib/api.ts` directly |
| L3 | Layout component does NOT perform domain calculations |

---

## Phase 5 — All-Class Mandate Checks

Run these for every new component regardless of class:

| Check | Mandate | Pass Condition |
|-------|---------|----------------|
| M1 | CSS tokens | Only CSS variables from globals.css used for colours — no raw hex |
| M2 | Icon library | Only `lucide-react` for icons |
| M3 | TypeScript strict | All props typed in a named interface — no `any`, no `unknown` |
| M4 | File size | Estimate final line count — if >300 lines expected, decompose first |
| M5 | Accessibility | Every button has `aria-label`, every form input has visible label |
| M6 | Keyboard nav | Tab order is logical, interactive elements reachable via keyboard |
| M7 | No domain logic | No arithmetic on API response data in component body |
| M8 | No format hardcoding | No `"odi"`, `"t20i"`, `"the_hundred"` as raw string literals |

---

## Phase 6 — Gate Sequence

```
GATE F1 — frontend-lint-sentinel
Trigger: new .tsx file created in frontend/.
Run: python core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/scripts/run_frontend_lint.py --root .
Pass: zero violations.

GATE F2 — frontend-paradigm-sentinel
Trigger: always after F1.
Run: python core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/scripts/run_frontend_paradigm.py --root .
Pass: zero violations.

GATE F3 — frontend-type-sync-guard
Trigger: always — scans all frontend/lib/*.ts files.
Run: python core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/scripts/run_type_sync.py --root .
Pass: zero violations.

GATE 5 — paradigm-sentinel
Follow: core/gen_ai/skills/validators/backend/paradigm-sentinel/SKILL.md

GATE 6 — compliance_bouncer
Run: python core/utils/compliance_bouncer.py --root .
```

---

## Phase 7 — Task Report

```
FRONTEND NEW COMPONENT REPORT
==============================
Task: [one-line description]
Date: [date]
Component Name: [name]
Component Class: [layout / renderer / input / common / navigation]
Directory: [path]

Baseline Bouncer: [PASS/FAIL — N violations]
Post-Task Bouncer: [PASS/FAIL — N violations — matches baseline: YES/NO]

Classification Checks: [Phase 1 — class confirmed]
Placement Check: [Phase 2 — directory confirmed]
Renderer Checks: [R1–R5 — PASS/SKIP]
Layout Checks: [L1–L3 — PASS/SKIP]
Mandate Checks: [M1–M8 — PASS/FAIL each]

Frontend Gates:
- GATE F1 (frontend-lint-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE F2 (frontend-paradigm-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE F3 (frontend-type-sync-guard): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 5 (paradigm-sentinel): TRIGGERED — [PASS/FAIL]
- GATE 6 (compliance_bouncer): TRIGGERED — [PASS/FAIL]

Files Created: [list]
Files Modified: [list]
Registered Files Touched: [list or NONE]
Stop-State-Trace-Confirm Used: [YES/NO — which file]

Blockers Hit: [list or NONE]

Status: [COMPLETE / BLOCKED — reason]
```
