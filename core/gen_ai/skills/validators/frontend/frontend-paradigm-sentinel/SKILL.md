---
name: frontend-paradigm-sentinel
description: Deep architectural scan for frontend paradigm violations — domain logic in components, SRP violations, directory placement contract breaches, external state libs, and context usage patterns.
---

# Frontend Paradigm Sentinel

Runs after frontend-lint-sentinel (GATE F1) passes. Checks for structural and architectural violations that regex-only linting cannot catch.

## Mission

Detect paradigm violations where components exceed their role: domain logic leaking into React, wrong directory placement, components exceeding 300 lines, external state management imports, and silent error swallowing in renderers.

## Trigger Condition

Always — after GATE F1 (frontend-lint-sentinel) passes.

## Gate Command

```powershell
python core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/scripts/run_frontend_paradigm.py --root .
```

Pass condition: zero violations reported.

## Checks Performed

| # | Rule | Description |
|---|------|-------------|
| 1 | 2.2A-R5 | Domain logic (arithmetic on API data) in component files |
| 2 | 2.2A-R4 | Component file exceeds 300 lines |
| 3 | 2.2B-R7 | Renderer component not located in `components/renderers/` |
| 4 | 2.2B-R9 | Layout component receives data as props instead of using context |
| 5 | 2.2B-R10 | Component file in wrong directory per placement contract |
| 6 | 2.2A-R3 | External state management library imports (Redux, Zustand, MobX, Jotai) |
| 7 | 2.2A-R14 | `setInterval`/`setTimeout` making `/execute/` endpoint calls |
| 8 | 2.2D-R2 | `try/catch` in renderer component swallowing errors silently |

## Output Format

```
PASS: zero violations
```

or on failure:

```
FAIL: N violation(s) found

[RULE 2.2A-R4] Component file exceeds 300 lines (412 lines)
  frontend/components/layout/CategoryScreen.tsx:1:1

[RULE 2.2A-R3] External state management library import
  frontend/components/common/Store.tsx:3:1
```

## Exit Contract

- `PASS` — zero violations. Gate cleared.
- `FAIL` — one or more violations. Fix all before proceeding.
