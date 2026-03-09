---
name: frontend-modification-guide
description: Checkpoint workflow for modifying existing frontend components or styles. Enforces delta discipline — CSS token compliance, manifest-driven rendering, pre-computed payload mandate, and component placement contract.
---

# Frontend Modification Guide

Structured checkpoint workflow for all frontend modification tasks (changing existing components, styles, layouts, or API integration). Use this guide instead of the backend modification-guide when the task scope is frontend-only.

## Phase 0 — Pre-Conditions

### 0.1 — Standards File
Read `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md` in full.

### 0.2 — Session State
Confirm Active Task, no conflicting tasks, no blockers.

### 0.3 — Baseline Bouncer
```powershell
python core/utils/compliance_bouncer.py --root .
```

### 0.4 — Change Classification
Classify the modification type:
- **Style** — CSS, Tailwind classes, layout, colours
- **Data** — API integration, types, payload handling
- **Structure** — component decomposition, directory moves, new props
- **Behaviour** — event handlers, state, side effects
- **Accessibility** — aria attributes, keyboard navigation, focus management

---

## Phase 1 — Delta Discipline Checks

Before writing any code, answer all of these. If any answer is NO — design the fix to make it YES first.

| # | Question | Expected Answer |
|---|----------|----------------|
| D1 | Is the change scoped to one component / one responsibility? | YES |
| D2 | If styling change — does it use only CSS variables from globals.css? | YES |
| D3 | If adding a new UI string / label — does it come from the manifest or a backend field? | YES |
| D4 | If consuming API data — is all computation done in the backend, not in the component? | YES |
| D5 | If the component grows — will it remain under 300 lines after the change? | YES |
| D6 | If touching FunctionRenderer — does the change preserve React.lazy() for all renderer imports? | YES |
| D7 | If adding interactive elements — does every button/input have aria-label or visible label? | YES |

---

## Phase 2 — Mandate Checks

| Check | Mandate |
|-------|---------|
| M1 | No raw hex colours — use CSS variables |
| M2 | No hardcoded format strings — use manifest lookups |
| M3 | No domain arithmetic in component files |
| M4 | No external state library imports (Redux, Zustand, etc.) |
| M5 | No `any` or `unknown` in new type annotations |
| M6 | Component placement contract preserved — file stays in correct directory |
| M7 | If renderers touched — lazy loading and error boundary preserved |

---

## Phase 3 — Gate Sequence

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

GATE 5 — paradigm-sentinel
Follow: core/gen_ai/skills/validators/backend/paradigm-sentinel/SKILL.md

GATE 6 — compliance_bouncer
Run: python core/utils/compliance_bouncer.py --root .
```

---

## Phase 4 — Task Report

```
FRONTEND MODIFICATION REPORT
============================
Task: [one-line description]
Date: [date]
Change Type: [Style / Data / Structure / Behaviour / Accessibility]

Baseline Bouncer: [PASS/FAIL — N violations]
Post-Task Bouncer: [PASS/FAIL — N violations — matches baseline: YES/NO]

Delta Discipline: [D1–D7 — YES/SKIP each]

Frontend Gates:
- GATE F1 (frontend-lint-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE F2 (frontend-paradigm-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE F3 (frontend-type-sync-guard): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 5 (paradigm-sentinel): TRIGGERED — [PASS/FAIL]
- GATE 6 (compliance_bouncer): TRIGGERED — [PASS/FAIL]

Files Modified: [list]
Registered Files Touched: [list or NONE]
Stop-State-Trace-Confirm Used: [YES/NO — which file]

Blockers Hit: [list or NONE]

Status: [COMPLETE / BLOCKED — reason]
```
