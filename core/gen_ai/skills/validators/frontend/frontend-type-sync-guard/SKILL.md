---
name: frontend-type-sync-guard
description: Validates that all TypeScript interfaces in lib/types.ts mapping to backend schemas carry @schema JSDoc, and flags when backend Pydantic models change without a corresponding frontend type update.
---

# Frontend Type Sync Guard

Prevents silent drift between backend Pydantic schemas and frontend TypeScript interfaces.

## Mission

Every interface in `lib/types.ts` that maps to a backend API response shape must declare `@schema <BackendModelName>` in its JSDoc. When backend schemas change, the corresponding frontend types must be updated in the same task.

## Trigger Condition

Always-on. Run this gate on every frontend task regardless of which files were modified.
`lib/types.ts` is a live contract — drift can exist independently of what the current task touches.
Previously conditional (only on lib/types.ts or Pydantic schema changes) — changed 2026-03-09.

## Gate Command

```powershell
python core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/scripts/run_type_sync.py --root .
```

Pass condition: zero violations reported.

## Checks Performed

| # | Check |
|---|-------|
| 1 | Every `export interface` in all `frontend/lib/*.ts` files has a `@schema` JSDoc tag in the preceding comment block |
| 2 | No orphaned `@schema` tags referencing non-existent backend model names (basic name format check) |
| 3 | Interfaces tagged with `@schema-exempt` are treated as compliant — no @schema tag required. Use for frontend-only shapes that do not map to a standalone backend API endpoint. |

## Output Format

```
PASS: zero violations
```

or on failure:

```
FAIL: N violation(s) found

[RULE 2.2D-R3] Interface 'PredictionResult' missing @schema JSDoc
  frontend/lib/types.ts:47:1

[RULE 2.2D-R3] Interface 'VenueOption' missing @schema JSDoc
  frontend/lib/types.ts:82:1
```

## Exit Contract

- `PASS` — zero violations.
- `FAIL` — add `@schema <BackendModelName>` JSDoc to every flagged interface before proceeding.

## @schema JSDoc Format

```typescript
/**
 * @schema PredictionResult
 * Maps to the PredictionResult Pydantic model in api/schemas/
 */
export interface PredictionResult {
  // ...
}
```

## @schema-exempt JSDoc Format

Use for interfaces that are frontend-only and do not map to a backend endpoint:
```typescript
/**
 * @schema-exempt frontend-only — nested sub-shape of Manifest
 */
export interface ManifestFunction {
  // ...
}
```
