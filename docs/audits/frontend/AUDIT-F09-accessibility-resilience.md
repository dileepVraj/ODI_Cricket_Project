# AUDIT-F09 - ACCESSIBILITY + RESILIENCE CROSS-CUT
**Date:** 2026-03-06
**Task:** TASK-029 - Frontend Compliance Audit Series
**Step:** F09 - Accessibility + resilience cross-cut
**Scope:** Read-only audit. Zero code changes.
**Files in scope:** All 27 frontend source files - cross-cutting pass
**Project root:** `C:\Cricket_Project_Stable\`
**Output file:** `C:\Cricket_Project_Stable\docs\audits\frontend\AUDIT-F09-accessibility-resilience.md`
**Standards ref:** ENGINEERING_STANDARDS_FRONTEND.md v2.2
  - 2.2D Rule 1 (Error Boundary - Renderer Isolation)
  - 2.2D Rule 2 (Error Boundary Placement)
  - 2.2D Rule 3 (Backend Type Sync Contract)
  - 2.2E Rule 1 (Interactive Element Labels)
  - 2.2E Rule 2 (Keyboard Navigation)
  - 2.2E Rule 3 (Loading and Error State Announcements)

**Gate 5 note:** paradigm-sentinel will flag a pre-existing violation in
`formats/odi/predictor.py` on every step. This is architect-waived and
tracked under TASK-010. Record the waiver in the task report and proceed.

**Important:** This is a cross-cutting audit step. Do not re-audit files
already covered in F02-F08 in full - focus only on the specific rules
listed above that were deferred or require a codebase-wide view.
Where a finding was already confirmed in a prior step, record it as
CONFIRMED with a reference to the original violation ID. Only raise
NEW findings not captured in F02-F08.

---

## SECTION 1 - Error Boundary Audit (2.2D Rules 1, 2)

### 1.1 Error Boundary Component
| Requirement | Finding | Status |
|-------------|---------|--------|
| `ErrorBoundary` component exists in `components/common/` | No `ErrorBoundary.tsx` exists under `frontend/components/common/`; only `EmptyState.tsx` is present. | FAIL |
| Component catches render errors from children | No shared boundary component exists to catch child render errors. | FAIL |
| Displays recoverable error state using `badge-danger` + `btn-ghost` retry | No recoverable renderer-failure UI exists because the boundary component is absent. | FAIL |
| Never displays blank screen on error | Not guaranteed. Renderer errors would currently bypass any dedicated boundary recovery path. | FAIL |

### 1.2 Error Boundary Placement
| Requirement | Finding | Status |
|-------------|---------|--------|
| `FunctionRenderer` output wrapped in Error Boundary in `page.tsx` | Confirmed missing - F04-V05, F05-V04 | CONFIRMED |
| Error Boundary placed at renderer dispatch level | Confirmed missing - F04-V05 | CONFIRMED |
| Individual renderers throw on bad data - do not catch silently | F07-V19 (`DataTable.formatCell()` silent catch) confirmed | CONFIRMED |
| Any additional silent catches found in this pass | No additional renderer-layer silent catches found beyond F07-V19. | PASS |

### 1.3 Error Boundary Coverage Map
For each file that renders output, record whether it is covered
by an Error Boundary or not.

| File | Error Boundary Present | Notes |
|------|----------------------|-------|
| `app/page.tsx` - FunctionRenderer dispatch | NO | F04-V05 confirmed |
| `components/renderers/FunctionRenderer.tsx` | NO | F05-V04 confirmed |
| All individual renderers | NO | No boundary at dispatch level |
| Any other rendering site found in this pass | NONE | No alternate renderer boundary found elsewhere in frontend |

---

## SECTION 2 - Backend Type Sync Contract (2.2D Rule 3)

### 2.1 @schema JSDoc Audit
Every TypeScript type in `frontend/lib/api.ts` or `frontend/lib/types.ts`
that maps to a backend Pydantic schema MUST have:
`/** @schema {PydanticClassName} in {python_file_path} */`

| Type | File | @schema comment present | Status |
|------|------|------------------------|--------|
| `FormatInfo` | `lib/api.ts` | NO | CONFIRMED - F03-V03 |
| `Manifest` | `lib/api.ts` | NO | CONFIRMED - F03-V03 |
| `ManifestFunction` | `lib/api.ts` | NO | CONFIRMED - F03-V03 |
| `ExecuteResponse` | `lib/api.ts` | NO | CONFIRMED - F03-V03 |
| Any other backend-mapped types found | `ContextField`, `ManifestCategory`, `HealthStatus`, `VenueItem` in `lib/api.ts` also have no `@schema` JSDoc. | CONFIRMED - F03-V03 |

### 2.2 lib/types.ts
| Requirement | Status |
|-------------|--------|
| `lib/types.ts` exists as separate file | Confirmed absent - F03 finding | CONFIRMED |
| All backend-mapped types migrated to types.ts | Deferred - `lib/types.ts` does not exist | CONFIRMED |

---

## SECTION 3 - Interactive Element Labels (2.2E Rule 1)

Cross-cutting check: any interactive element containing only an icon
with no visible text MUST have `aria-label` or `aria-labelledby`.

Focus on files not fully covered in F06-F08 or where new icon-only
elements may exist.

| File | Element | aria-label present | Status |
|------|---------|-------------------|--------|
| `components/layout/Sidebar.tsx` | Collapsed nav items | NO - F06-V07 | CONFIRMED |
| `components/inputs/SquadBuilder.tsx` | Add/remove/toggle icons | NO - F08-V05 | CONFIRMED |
| `components/inputs/ExtraInputRenderer.tsx` | Combobox clear icon | NO - F08-V10 | CONFIRMED |
| Any additional icon-only elements found in this pass | None beyond previously confirmed violations; sidebar collapse toggles already expose `aria-label`. | PASS |

---

## SECTION 4 - Keyboard Navigation (2.2E Rule 2)

Cross-cutting check: all `onClick` handlers on non-interactive elements
(`div`, `span`) MUST have `onKeyDown` + `role="button"` + `tabIndex={0}`.

| File | Element | Keyboard handler present | Status |
|------|---------|------------------------|--------|
| `components/layout/ContextBar.tsx` | Venue combobox | NO - F06-V04 | CONFIRMED |
| `components/inputs/SquadBuilder.tsx` | Dropdown + controls | NO - F08-V05 | CONFIRMED |
| `components/inputs/ExtraInputRenderer.tsx` | Combobox controls | NO - F08-V10 | CONFIRMED |
| `components/renderers/DataTable.tsx` | Sortable `<th>` headers at lines 89-91 | NO - clickable table headers have no keyboard activation semantics. | NEW |
| `components/renderers/MatrixTable.tsx` | Sortable `<th>` headers and clickable opponent `<td>` at lines 101-103 and 126-133 | NO - sortable headers and rivalry navigation cell are pointer-only interactions. | NEW |

---

## SECTION 5 - Loading and Error State Announcements (2.2E Rule 3)

### 5.1 aria-live Regions
Every result container MUST have `aria-live="polite"`.

| File | Element | aria-live present | Status |
|------|---------|------------------|--------|
| `app/page.tsx` - result container | NO - F04-V06 | CONFIRMED |
| Any other result containers found in this pass | None additional found beyond the page-level async result region. | PASS |

### 5.2 role="alert" on Error Displays
Every error display MUST have `role="alert"`.

| File | Element | role="alert" present | Status |
|------|---------|---------------------|--------|
| `app/page.tsx` - error block | NO - F04-V07 | CONFIRMED |
| `components/inputs/SquadBuilder.tsx` | `loadError` block at lines 282-286 | NO - async squad-loading failures render as plain text only. | NEW |

### 5.3 Loading State Announcements
| File | Loading indicator | Announced to screen reader | Status |
|------|------------------|--------------------------|--------|
| `app/page.tsx` | isLoading state at lines 688-746 | NO - button text changes and skeleton mount without `aria-live`, `role="status"`, or screen-reader text. | NEW |
| `components/renderers/SkeletonLoader.tsx` | Skeleton | NO - skeleton variants expose no live/status semantics or assistive text. | NEW |
| Any other loading states found | `SquadBuilder.tsx` and `ExtraInputRenderer.tsx` async player-loading flows also lack live status semantics. | NEW - same pattern |

---

## SECTION 6 - New Findings Only

Record here any accessibility or resilience violations found
in this cross-cutting pass that were NOT already captured
in F02-F08. Do not re-record confirmed findings.

| File | Rule | Description | Severity |
|------|------|-------------|----------|
| `frontend/components/common/` | 2.2D Rule 1 | No shared `ErrorBoundary` component exists in `components/common/`, so renderer failures have no dedicated recovery surface. | HIGH |
| `frontend/components/renderers/DataTable.tsx` | 2.2E Rule 2 | Sortable table headers use clickable `<th>` elements without keyboard activation semantics. | MEDIUM |
| `frontend/components/renderers/MatrixTable.tsx` | 2.2E Rule 2 | Sortable `<th>` headers and the clickable opponent `<td>` are pointer-only interactions with no keyboard support. | HIGH |
| `frontend/components/inputs/SquadBuilder.tsx` | 2.2E Rule 3 | The async squad-loading error message renders without `role="alert"`, so failures are not announced to assistive technology. | MEDIUM |
| `frontend/app/page.tsx`, `frontend/components/renderers/SkeletonLoader.tsx` | 2.2E Rule 3 | Execute loading states are not announced through `aria-live`, `role="status"`, or equivalent assistive text. | MEDIUM |

---

## VIOLATION REGISTER

| ID | File | Rule | Description | Severity |
|----|------|------|-------------|----------|
| F09-V01 | `frontend/components/common/` | 2.2D Rule 1 | No shared `ErrorBoundary` component exists in `components/common/`, so renderer failures have no dedicated recovery UI or retry surface. | HIGH |
| F09-V02 | `frontend/components/renderers/DataTable.tsx` | 2.2E Rule 2 | Sortable column headers are clickable `<th>` elements with no keyboard activation semantics. | MEDIUM |
| F09-V03 | `frontend/components/renderers/MatrixTable.tsx` | 2.2E Rule 2 | Sortable column headers and the clickable opponent cell rely on pointer-only `onClick` interactions without keyboard support. | HIGH |
| F09-V04 | `frontend/components/inputs/SquadBuilder.tsx` | 2.2E Rule 3 | The async squad-loading error message at lines 282-286 lacks `role="alert"`. | MEDIUM |
| F09-V05 | `frontend/app/page.tsx`, `frontend/components/renderers/SkeletonLoader.tsx` | 2.2E Rule 3 | Execute loading states are not announced to screen readers; the loading button/skeleton flow has no `aria-live`, `role="status"`, or equivalent assistive text. | MEDIUM |

**Previously confirmed violations carried forward:**
- F04-V05 / F05-V04 - No Error Boundary at renderer dispatch level
- F04-V06 - Result container missing aria-live="polite"
- F04-V07 - Error block missing role="alert"
- F06-V04 - ContextBar venue combobox keyboard inaccessible
- F06-V07 - Sidebar collapsed icons missing aria-label
- F08-V05 - SquadBuilder controls keyboard inaccessible
- F08-V10 - ExtraInputRenderer combobox keyboard inaccessible

*(New violations only in violation register above -
confirmed violations are tracked in their original step)*

---

## SUMMARY
```
Cross-cutting audit scope: all 27 frontend source files
Focus rules: 2.2D Rules 1-3, 2.2E Rules 1-3

Error Boundary:
  Component exists in components/common/: NO
  Renderer dispatch covered: NO - confirmed F04-V05 / F05-V04

Backend type sync:
  @schema JSDoc present on backend-mapped types: NO - confirmed F03-V03
  lib/types.ts exists: NO - confirmed F03

Accessibility confirmed violations: 5 (from F04, F06, F08)
Accessibility new violations found this pass: 5

Loading state announcements: VIOLATIONS

Total new violations found this step: 5
Previously confirmed violations referenced: 7

F09 STATUS: COMPLETE
```
