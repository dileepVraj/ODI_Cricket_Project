# AUDIT-F03 - CORE LIB
**Date:** 2026-03-06
**Task:** TASK-029 - Frontend Compliance Audit Series
**Step:** F03 - Core Lib
**Scope:** Read-only audit. Zero code changes.
**Files in scope:**
  - `frontend/lib/api.ts`
  - `frontend/lib/context.tsx`
**Project root:** `C:\Cricket_Project_Stable\`
**Output file:** `C:\Cricket_Project_Stable\docs\audits\frontend\AUDIT-F03-core-lib.md`
**Standards ref:** ENGINEERING_STANDARDS_FRONTEND.md v2.2
  - 2.2A Rule 1 (API Wrapper Mandate)
  - 2.2A Rule 3 (Global State Purity)
  - 2.2A Rule 6 (TypeScript Strict Mode)
  - 2.2A Rule 9 (Hash-Based Navigation)
  - 2.2A Rule 10 (Async Effect Cancellation)
  - 2.2A Rule 13 (Format String Agnosticism)
  - 2.2A Rule 15 (No Unapproved State Libraries)
  - 2.2D Rule 3 (Backend Type Sync Contract)

---

## SECTION 1 - frontend/lib/api.ts

### 1.1 API Wrapper Mandate (2.2A Rule 1)
Verify all fetch calls are centralised here and no raw fetch
calls exist outside this file.

| Requirement | Present | Status |
|-------------|---------|--------|
| Single `requestJson<T>()` wrapper exists | YES | PASS |
| All API calls flow through wrapper | YES | PASS |
| No raw `fetch()` calls in components | [verify in F04-F08] | DEFERRED |
| Custom error class defined (`ApiClientError` or equivalent) | YES | PASS |
| Error class exposes `status`, `code`, `details` | YES | PASS |
| `toUserMessage()` method present | NO | FAIL |

### 1.2 TypeScript Strict Mode (2.2A Rule 6)
| Requirement | Status |
|-------------|--------|
| No `any` type annotations present | PASS |
| No `unknown` used as final type for domain data | FAIL |
| All API response shapes typed as interfaces | FAIL |

### 1.3 Type Location Contract (2.2D Rule 3)
| Requirement | Status |
|-------------|--------|
| API response types defined in `lib/api.ts` or `lib/types.ts` | PASS |
| Every type mapping to a backend Pydantic schema has `@schema` JSDoc comment | FAIL |
| `lib/types.ts` exists as separate file | NO - types currently live only in `lib/api.ts` |

### 1.4 Key Types Present
| Type | Present | Notes |
|------|---------|-------|
| `FormatInfo` | YES | Interface defined |
| `Manifest` | YES | Interface defined |
| `ManifestFunction` | YES | Interface defined |
| `ExecuteResponse` | YES | Interface defined, but `data` is typed as `unknown` |
| `ApiClientError` | YES | Class defined |

### 1.5 Base URL and Endpoint Patterns
| Requirement | Present | Status |
|-------------|---------|--------|
| Base URL is empty string (same-origin) | YES | PASS |
| Key endpoints use `/api/v1/` prefix | YES | PASS |
| No hardcoded format strings (e.g. `"odi"`) in endpoint paths | YES | PASS |

### 1.6 Findings
- `requestJson<T>()` is the single wrapper and all domain API functions call through it.
- `ApiClientError` stores `status`, `code`, and `details`, but user-message conversion lives in a standalone helper instead of a `toUserMessage()` class method.
- The strict typing contract is loose in several places: `ExecuteResponse.data` is `unknown`, error/details payloads are `unknown`, and multiple endpoint responses are typed inline instead of through named interfaces.
- Backend-mapped response types do not carry `@schema` JSDoc comments.

---

## SECTION 2 - frontend/lib/context.tsx

### 2.1 Global State Purity (2.2A Rule 3)
| Requirement | Present | Status |
|-------------|---------|--------|
| Single `AppProvider` wrapping entire app | NO | FAIL |
| State accessed exclusively via `useAppContext()` | YES | PASS |
| No external state library imports | YES | PASS |
| Local `useState` used only for strictly local UI concerns | YES | PASS |

### 2.2 ContextValues Shape
| Field | Present | Notes |
|-------|---------|-------|
| `venue` | YES | String field present |
| `team_a` | YES | String field present |
| `team_b` | YES | String field present |
| `years` | YES | Number field present |
| `region` | YES | String field present |
| `[key: string]: string \| number` (index signature) | YES | Present |

### 2.3 Async Effect Cancellation (2.2A Rule 10)
| Requirement | Present | Status |
|-------------|---------|--------|
| `let cancelled = false` guard in async effects | YES | PASS |
| Cleanup function sets `cancelled = true` | YES | PASS |
| All state setters check guard before execution | YES | PASS |

### 2.4 Hash-Based Navigation (2.2A Rule 9)
| Requirement | Present | Status |
|-------------|---------|--------|
| `window.history.replaceState()` used for URL sync | YES | PASS |
| No `router.push()` for internal view transitions | YES | PASS |
| Bidirectional sync implemented | YES | PASS |

### 2.5 Format Agnosticism (2.2A Rule 13)
| Requirement | Present | Status |
|-------------|---------|--------|
| No hardcoded format strings (e.g. `"odi"`) | YES | PASS |
| `years` default sourced from `manifest.context_fields.years.default` | YES | PASS |
| Fallback value used when manifest default absent | YES | PASS |

### 2.6 Format Switching Behaviour
| Requirement | Present | Status |
|-------------|---------|--------|
| Format switching clears `contextValues` to defaults | YES | PASS |
| Manifest loaded on format change | YES | PASS |

### 2.7 TypeScript Strict Mode (2.2A Rule 6)
| Requirement | Status |
|-------------|--------|
| No `any` type annotations | PASS |
| All context state shapes fully typed | PASS |

### 2.8 Findings
- `AppProvider` and `useAppContext()` are implemented here, but F02 already confirmed `frontend/app/layout.tsx` does not mount the provider, so the global-state contract is still violated at runtime.
- Async effect cancellation is consistently guarded with `cancelled` flags and cleanup functions.
- URL synchronization is bidirectional: query params hydrate context state and `replaceState()` writes non-default context back to the URL.
- Format switching reloads manifest data and resets context values to defaults, with `years` correctly sourced from manifest defaults and falling back to `5`.

---

## VIOLATION REGISTER

| ID | File | Rule | Description | Severity |
|----|------|------|-------------|----------|
| F03-V01 | `frontend/lib/api.ts` | 2.2A Rule 1 | `ApiClientError` does not expose a `toUserMessage()` method; message conversion is handled by a separate helper function. | MEDIUM |
| F03-V02 | `frontend/lib/api.ts` | 2.2A Rule 6 | Domain response typing is not strict enough: `ExecuteResponse.data` is `unknown` and several endpoint payloads use inline object literals instead of named interfaces. | HIGH |
| F03-V03 | `frontend/lib/api.ts` | 2.2D Rule 3 | Backend-schema-mapped types do not include `@schema` JSDoc comments. | MEDIUM |
| F03-V04 | `frontend/lib/context.tsx` | 2.2A Rule 3 | `AppProvider` is defined here but is not mounted at the app root at runtime (confirmed in F02 `layout.tsx` audit). | HIGH |

*(Populate only confirmed violations - no speculative entries)*

---

## SUMMARY
```text
Files audited: 2
  frontend/lib/api.ts - API wrapper: VIOLATION
  frontend/lib/api.ts - TypeScript strict: FAIL
  frontend/lib/api.ts - type location contract: VIOLATION
  frontend/lib/context.tsx - AppProvider: VIOLATION
  frontend/lib/context.tsx - async cancellation: COMPLIANT
  frontend/lib/context.tsx - hash navigation: COMPLIANT
  frontend/lib/context.tsx - format agnosticism: COMPLIANT

Total violations found this step: 4
New violations (not in pre-existing list): 3
Pre-existing violations confirmed: 1

F03 STATUS: COMPLETE
```
