# AUDIT-F10 — VIOLATION SUMMARY
**Date:** 2026-03-06
**Task:** TASK-029 — Frontend Compliance Audit Series
**Step:** F10 — Violation Summary
**Scope:** Synthesis of F01–F09. Read-only. Zero code changes.
**Project root:** `C:\Cricket_Project_Stable\`
**Output file:** `C:\Cricket_Project_Stable\docs\audits\frontend\AUDIT-F10-violation-summary.md`
**Standards ref:** ENGINEERING_STANDARDS_FRONTEND.md v2.2

---

## SECTION 1 — AUDIT SERIES STATISTICS
```
Audit steps completed:        F01–F09 (9 steps)
Source files audited:         27
Total violations found:       90
  Pre-existing (known):        8
  New violations:             82
Severity breakdown:
  HIGH:                       18
  MEDIUM:                     52
  LOW:                        12
  UNCONFIRMED (resolved):      2 (F02-V03/F03-V04 — confirmed as F04-V01)
```

---

## SECTION 2 — MASTER VIOLATION REGISTER

### HIGH Severity

| ID | File | Rule | Description |
|----|------|------|-------------|
| F02-V01 | `frontend/package.json` | 2.2F Rule 1 | No test stack — Vitest and React Testing Library absent. No `test` npm script. PRE-EXISTING. |
| F02-V03 | `frontend/app/layout.tsx` | 2.2A Rule 3 | `AppProvider` not mounted in `layout.tsx`. Confirmed in F04 as F04-V01 — provider is in `page.tsx` instead. |
| F03-V02 | `frontend/lib/api.ts` | 2.2A Rule 6 | `ExecuteResponse.data` typed as `unknown`. PRE-EXISTING. |
| F03-V04 | `frontend/lib/context.tsx` | 2.2A Rule 3 | `AppProvider` defined but not mounted at app root. Confirmed F04-V01. |
| F04-V01 | `frontend/app/page.tsx` | 2.2A Rule 3 | `AppProvider` mounted in `page.tsx` not `layout.tsx` — wrong location. |
| F04-V02 | `frontend/app/page.tsx` | 2.2A Rule 4 | `CategoryScreen` 354 lines — SRP violation, exceeds 300-line limit. |
| F04-V05 | `frontend/app/page.tsx` | 2.2D Rules 1, 2 | No `ErrorBoundary` around `FunctionRenderer` dispatch. PRE-EXISTING. Root cause: F09-V01. |
| F05-V01 | `frontend/components/renderers/FunctionRenderer.tsx` | 2.2C Rule 1 | All renderer imports eager — `React.lazy()` not used. PRE-EXISTING. |
| F05-V04 | `frontend/components/renderers/FunctionRenderer.tsx` | 2.2D Rules 1, 2 | No `ErrorBoundary` at dispatcher level. PRE-EXISTING. Root cause: F09-V01. |
| F06-V04 | `frontend/components/layout/ContextBar.tsx` | 2.2E Rule 2 | Venue combobox lacks keyboard navigation semantics. |
| F06-V07 | `frontend/components/layout/Sidebar.tsx` | 2.2E Rules 1, 2 | Collapsed nav items icon-only with no `aria-label`. |
| F07-V20 | `frontend/components/renderers/PhaseAnalysisCard.tsx` | 2.2A Rule 4 | 425 lines — mixes header, filter, phase tables, habits, audit rendering. SRP violation. |
| F07-V21 | `frontend/components/renderers/PhaseAnalysisCard.tsx` | 2.2A Rule 5 | Derives labels, thresholds, fallback rows, and number formatting from raw payload. |
| F07-V23 | `frontend/components/renderers/VenueMatchupReport.tsx` | 2.2B Rule 8 | Returns `null` on missing team payload — no user feedback. |
| F07-V26 | `frontend/components/renderers/PredictionCard.tsx` | 2.2A Rule 5 | Calculates prediction ranges and gauge defaults from raw payload. |
| F07-V30 | `frontend/components/renderers/PlayerProfileCard.tsx` | 2.2A Rule 5 | Classifies payload fields by key-name heuristics — domain logic in renderer. |
| F08-V01 | `frontend/components/inputs/SquadBuilder.tsx` | 2.2A Rule 4 | 388 lines — `SquadPanel` combines fetching, dropdown state, and list rendering. |
| F08-V03 | `frontend/components/inputs/SquadBuilder.tsx` | Paradigm 5 | `fetchPlayers()` runs inside UI effects — violates pre-computed payload mandate. |
| F08-V05 | `frontend/components/inputs/SquadBuilder.tsx` | 2.2E Rules 1, 2 | Add/remove/toggle controls mouse-only, no keyboard access, no `aria-label`. |
| F08-V07 | `frontend/components/inputs/ExtraInputRenderer.tsx` | 2.2A Rule 4 | 326 lines — `ExtraInputField` mixes source resolution, fetching, and rendering. |
| F08-V08 | `frontend/components/inputs/ExtraInputRenderer.tsx` | 2.2A Rule 11 | Hardcodes domain field cases (`squad_builder`, `country_name`, `team_a`, `team_b`). |
| F08-V10 | `frontend/components/inputs/ExtraInputRenderer.tsx` | 2.2E Rule 2 | Combobox controls mouse-only — no keyboard support. |
| F09-V01 | `frontend/components/common/` | 2.2D Rule 1 | `ErrorBoundary` component does not exist. Root cause of F04-V05 and F05-V04. |
| F09-V03 | `frontend/components/renderers/MatrixTable.tsx` | 2.2E Rule 2 | Sortable headers and opponent cell pointer-only — no keyboard support. |

---

### MEDIUM Severity

| ID | File | Rule | Description |
|----|------|------|-------------|
| F02-V02 | `frontend/app/globals.css` | 2.2B Rule 1 | Token naming drift — `--bg-deep` missing, accent tokens renamed to non-standard aliases. |
| F02-V04 | `frontend/app/layout.tsx` | 2.2B Rule 5 | Next.js font loading and font variable injection missing. |
| F03-V01 | `frontend/lib/api.ts` | 2.2A Rule 1 | `ApiClientError.toUserMessage()` not a class method — standalone helper instead. |
| F03-V03 | `frontend/lib/api.ts` | 2.2D Rule 3 | Backend-schema-mapped types missing `@schema` JSDoc comments. |
| F04-V03 | `frontend/app/page.tsx` | 2.2A Rule 7 | `"dashboard"` hardcoded as category key. |
| F04-V04 | `frontend/app/page.tsx` | 2.2A Rule 8 | `formatExecuteError()` can surface raw `err.message` to users. |
| F04-V06 | `frontend/app/page.tsx` | 2.2E Rule 3 | Result container missing `aria-live="polite"`. |
| F04-V07 | `frontend/app/page.tsx` | 2.2E Rule 3 | Error block missing `role="alert"`. |
| F05-V02 | `frontend/components/renderers/FunctionRenderer.tsx` | 2.2A Rule 7 | Inline fallback rendering for unknown output types weakens manifest dispatch. |
| F05-V03 | `frontend/components/renderers/FunctionRenderer.tsx` | 2.2A Rule 6 | Repeated inline `as` casts on API response data. |
| F06-V03 | `frontend/components/layout/ContextBar.tsx` | 2.2A Rule 13 | Hardcodes `team_a`/`team_b` field key handling. |
| F06-V05 | `frontend/components/layout/Sidebar.tsx` | 2.2A Rule 5 | Hardcodes `dashboard` + `GROUP_META` navigation taxonomy. |
| F06-V06 | `frontend/components/layout/Sidebar.tsx` | 2.2B Rule 4 | Category icons use emoji literals instead of `lucide-react`. |
| F06-V08 | `frontend/components/navigation/QuickLinks.tsx` | 2.2B Rule 9 | Receives link definitions via props instead of context. |
| F06-V09 | `frontend/components/navigation/QuickLinks.tsx` | 2.2A Rule 13 | `resolveHref()` hardcodes `:format` placeholder substitution. |
| F06-V10 | `frontend/components/animations/CountUp.tsx` | 2.2B Rule 6 | Bespoke `requestAnimationFrame` easing outside design system. |
| F07-V01 | `frontend/components/renderers/ReportCard.tsx` | 2.2A Rule 5 | Reformats payload keys and derives percentage values from raw fields. |
| F07-V02 | `frontend/components/renderers/ReportCard.tsx` | 2.2B Rule 8 | Inline fallback `<div>` instead of `EmptyState`. |
| F07-V03 | `frontend/components/renderers/ReportCard.tsx` | 2.2A Rule 6 | Unsafe cast on `percent_breakdown`. |
| F07-V04 | `frontend/components/renderers/ReportCard.tsx` | 2.2B Rule 1 | Raw hex/rgba colour literals in gradients and badge surfaces. |
| F07-V05 | `frontend/components/renderers/ComparisonTable.tsx` | 2.2B Rule 8 | Inline fallback `<div>` instead of `EmptyState`. |
| F07-V07 | `frontend/components/renderers/ComparisonTable.tsx` | 2.2A Rule 6 | Repeated inline casts to internal row/tone types. |
| F07-V08 | `frontend/components/renderers/MatrixTable.tsx` | 2.2A Rule 5 | Parses payload strings to detect `OVERALL` rows and builds navigation targets. |
| F07-V09 | `frontend/components/renderers/MatrixTable.tsx` | 2.2B Rule 8 | Inline fallback `<div>` instead of `EmptyState`. |
| F07-V11 | `frontend/components/renderers/MatrixTable.tsx` | 2.2A Rule 6 | Inline casts to `MatrixRow` types. |
| F07-V12 | `frontend/components/renderers/FormTable.tsx` | 2.2B Rule 8 | Inline fallback `<div>` instead of `EmptyState`. |
| F07-V14 | `frontend/components/renderers/FormTable.tsx` | 2.2A Rule 6 | Inline cast from `data` to `FormRow[]`. |
| F07-V15 | `frontend/components/renderers/FormTable.tsx` | 2.2B Rule 1 | `resultClasses()` hardcodes raw Tailwind colour utilities. |
| F07-V16 | `frontend/components/renderers/DataTable.tsx` | 2.2B Rule 8 | Inline fallback `<div>` instead of `EmptyState`. |
| F07-V18 | `frontend/components/renderers/DataTable.tsx` | 2.2A Rule 6 | Inline casts from payload rows to `DataRow`. |
| F07-V19 | `frontend/components/renderers/DataTable.tsx` | 2.2D Rule 2 | `formatCell()` silently catches serialisation failures. |
| F07-V22 | `frontend/components/renderers/PhaseAnalysisCard.tsx` | 2.2B Rule 8 | Inline fallback `<div>` instead of `EmptyState`. |
| F07-V24 | `frontend/components/renderers/VenueMatchupReport.tsx` | 2.2A Rule 6 | Unsafe cast for `team_tone`. |
| F07-V25 | `frontend/components/renderers/VenueMatchupReport.tsx` | 2.2B Rule 1 | Raw Tailwind colour utilities and rgba literals. |
| F07-V27 | `frontend/components/renderers/PredictionCard.tsx` | 2.2B Rule 8 | Inline fallback `<div>` instead of `EmptyState`. |
| F07-V29 | `frontend/components/renderers/PredictionCard.tsx` | 2.2A Rule 6 | Inline casts for notes and gauge payload fragments. |
| F07-V31 | `frontend/components/renderers/PlayerProfileCard.tsx` | 2.2B Rule 3 | Team badge hardcoded as `badge-strong` — not backend-driven. |
| F07-V32 | `frontend/components/renderers/PlayerProfileCard.tsx` | 2.2B Rule 8 | Inline fallback `<div>` instead of `EmptyState`. |
| F07-V34 | `frontend/components/renderers/PlayerProfileCard.tsx` | 2.2A Rule 6 | Unsafe cast in `toObj()` for nested payload fragments. |
| F07-V36 | `frontend/components/renderers/PlayerProfileCard.tsx` | 2.2C Rule 3 | `QuickLinks` receives inline `links` array prop. |
| F07-V37 | `frontend/components/renderers/MatchupTable.tsx` | 2.2B Rule 8 | Inline fallback `<div>` instead of `EmptyState`. |
| F07-V39 | `frontend/components/renderers/MatchupTable.tsx` | 2.2B Rule 1 | Raw rgba colours in bunny-alert row styling. |
| F07-V40 | `frontend/components/renderers/DownloadPanel.tsx` | 2.2B Rule 8 | Inline fallback `<div>` instead of `EmptyState`. |
| F07-V41 | `frontend/components/renderers/DownloadPanel.tsx` | 2.2B Rule 1 | Non-token colour literals. |
| F07-V42 | `frontend/components/renderers/MatchAuditSection.tsx` | 2.2A Rule 5 | Parses dates and re-sorts audit rows client-side. |
| F07-V43 | `frontend/components/renderers/MatchAuditSection.tsx` | 2.2B Rule 8 | Returns `null` on empty audit rows. |
| F07-V44 | `frontend/components/renderers/MatchAuditSection.tsx` | 2.2A Rule 6 | Inline cast from each row to `MatchAuditRow`. |
| F08-V02 | `frontend/components/inputs/SquadBuilder.tsx` | 2.2A Rule 11 | No manifest config helper — raw props and hardcoded panel metadata. |
| F08-V04 | `frontend/components/inputs/SquadBuilder.tsx` | 2.2B Rule 1 / 2.2C Rule 3 | Dropdown portal uses raw `rgba()` and inline `style={{}}`. |
| F08-V06 | `frontend/components/inputs/SquadBuilder.tsx` | 2.2A Rule 6 | `e.target as HTMLElement` unsafe cast. |
| F08-V09 | `frontend/components/inputs/ExtraInputRenderer.tsx` | 2.2B Rule 2 | Inputs don't use `context-input` class — long inline bracket strings instead. |
| F08-V11 | `frontend/components/inputs/ExtraInputRenderer.tsx` | 2.2A Rule 6 | `e.target as Node` unsafe cast. |
| F08-V12 | `frontend/components/inputs/ExtraInputRenderer.tsx` | 2.2B Rule 1 | Raw `rgba()` literals and DOM hover style mutation. |
| F09-V02 | `frontend/components/renderers/DataTable.tsx` | 2.2E Rule 2 | Sortable column headers pointer-only — no keyboard semantics. |
| F09-V04 | `frontend/components/inputs/SquadBuilder.tsx` | 2.2E Rule 3 | Squad load error block missing `role="alert"`. |
| F09-V05 | `frontend/app/page.tsx` + `SkeletonLoader.tsx` | 2.2E Rule 3 | Execute loading states not announced to screen readers. |

---

### LOW Severity

| ID | File | Rule | Description |
|----|------|------|-------------|
| F06-V01 | `components/navigation/QuickLinks.tsx` | 2.2B Rule 10 | Wrong directory — should be `components/layout/`. |
| F06-V02 | `components/animations/CountUp.tsx` | 2.2B Rule 10 | Wrong directory — should be `components/common/`. |
| F07-V06 | `ComparisonTable.tsx` | 2.2B Rule 5 | Uses `font-variant-numeric` not `font-numeric` class. |
| F07-V10 | `MatrixTable.tsx` | 2.2B Rule 5 | Uses `font-variant-numeric` not `font-numeric` class. |
| F07-V13 | `FormTable.tsx` | 2.2B Rule 5 | Uses `font-variant-numeric` not `font-numeric` class. |
| F07-V17 | `DataTable.tsx` | 2.2B Rule 5 | Uses `font-variant-numeric` not `font-numeric` class. |
| F07-V28 | `PredictionCard.tsx` | 2.2B Rule 5 | Uses `font-variant-numeric` not `font-numeric` class. |
| F07-V33 | `PlayerProfileCard.tsx` | 2.2B Rule 5 | Uses `font-variant-numeric` not `font-numeric` class. |
| F07-V35 | `PlayerProfileCard.tsx` | 2.2B Rule 1 | Non-token colour literal `white`. |
| F07-V38 | `MatchupTable.tsx` | 2.2B Rule 5 | Uses `font-variant-numeric` not `font-numeric` class. |
| F07-V41 | `DownloadPanel.tsx` | 2.2B Rule 1 | Non-token colour literal `white`. |

---

## SECTION 3 — SYSTEMIC PATTERNS

These are not isolated bugs — they are patterns requiring a single
fix strategy applied across multiple files.

| Pattern | Violations | Affected Files | Fix Strategy |
|---------|-----------|----------------|--------------|
| Empty state — inline fallback instead of `EmptyState` | F07-V02/05/09/12/16/22/27/32/37/40/43, F07-V23 | 12 renderers | Replace all inline fallbacks with `<EmptyState />` or throw — one pass across all renderers |
| Inline `as` casts on payload data | F05-V03, F07-V03/07/11/14/18/24/29/34/44 | FunctionRenderer + 9 renderers | Introduce shared typed narrowing utilities per payload shape |
| Font system — `font-variant-numeric` not `font-numeric` | F07-V06/10/13/17/28/33/38 | 7 renderers | Replace `font-variant-numeric` with `font-numeric` class — mechanical find/replace |
| Raw colours outside CSS token system | F07-V04/15/25/39/41, F08-V04/12 | 7 files | Audit each raw rgba/hex and map to nearest CSS variable |
| Mouse-only comboboxes | F06-V04, F08-V05, F08-V10 | ContextBar, SquadBuilder, ExtraInputRenderer | Build shared accessible combobox primitive — apply to all three |
| Hardcoded domain taxonomy in components | F04-V03, F06-V03/05/08/09, F08-V08 | page.tsx, ContextBar, Sidebar, QuickLinks, ExtraInputRenderer | Manifest-driven config helpers — each component reads from context not hardcoded keys |
| Missing `role="alert"` on error displays | F04-V07, F09-V04 | page.tsx, SquadBuilder | Add `role="alert"` — 2-line fix per file |
| Missing loading state announcements | F04-V06, F09-V05 | page.tsx, SkeletonLoader | Add `aria-live="polite"` to result container, `role="status"` to skeleton |

---

## SECTION 4 — REMEDIATION SCOPE ESTIMATE

### Tier 1 — Create First (blockers for other work)
These must exist before other fixes can be implemented.

| Item | Effort | Unblocks |
|------|--------|---------|
| Create `ErrorBoundary` component in `components/common/` | Small — 1 new file | F04-V05, F05-V04, F09-V01 |
| Create shared accessible combobox primitive | Medium — 1 new component | F06-V04, F08-V05, F08-V10 |

### Tier 2 — Mechanical Fixes (low risk, high volume)
Pattern fixes that can be applied systematically.

| Item | Files Affected | Effort |
|------|---------------|--------|
| Replace inline fallbacks with `EmptyState` or throw | 12 renderers | Low per file — systematic pass |
| Replace `font-variant-numeric` with `font-numeric` | 7 renderers | Mechanical find/replace |
| Add `aria-label` to collapsed Sidebar items | Sidebar.tsx | Small |
| Add `role="alert"` to error displays | page.tsx, SquadBuilder | Trivial |
| Add `aria-live="polite"` to result container | page.tsx, SkeletonLoader | Trivial |
| Move `QuickLinks.tsx` to `components/layout/` | 1 file move + import fix | Trivial |
| Move `CountUp.tsx` to `components/common/` | 1 file move + import fix | Trivial |
| Replace emoji icons with `lucide-react` in Sidebar | Sidebar.tsx | Small — needs icon selection |

### Tier 3 — Architectural Fixes (higher risk, requires planning)
These touch data flow or component boundaries.

| Item | Files Affected | Effort | Risk |
|------|---------------|--------|------|
| Move `AppProvider` to `layout.tsx` | layout.tsx, page.tsx | Small | LOW |
| Decompose `CategoryScreen` (354 lines) | page.tsx | Medium | MEDIUM |
| Decompose `PhaseAnalysisCard` (425 lines) | PhaseAnalysisCard.tsx | Medium | MEDIUM |
| Decompose `SquadPanel` (293 lines) | SquadBuilder.tsx | Medium | MEDIUM |
| Decompose `ExtraInputField` (260 lines) | ExtraInputRenderer.tsx | Medium | MEDIUM |
| Pre-compute prediction ranges in backend | PredictionCard + backend | Large | HIGH |
| Pre-compute field classifications in backend | PlayerProfileCard + backend | Large | HIGH |
| Move `fetchPlayers()` to context pre-load | SquadBuilder + context.tsx | Large | HIGH |
| Typed narrowing utilities for payload casting | FunctionRenderer + 9 renderers | Medium | MEDIUM |
| Resolve token naming drift in globals.css | globals.css | Small | LOW |
| Add `@schema` JSDoc to all backend types | lib/api.ts | Small | LOW |
| Add `lib/types.ts` and migrate types | lib/api.ts + new file | Small | LOW |
| Install Vitest + React Testing Library | package.json | Small | LOW |

---

## SECTION 5 — ARCHITECT NOTES

**CountUp.tsx animation exception candidate.**
`CountUp` uses a bespoke `requestAnimationFrame` loop. There is no
CSS keyframe equivalent for a JS-driven numeric counter. Recommend
raising a standards exception for this component rather than
forcing a rewrite. Document as Known Intentional Pattern (KIP)
following the same pattern as backend KIP-001/KIP-002.

**Token naming drift (F02-V02) — standards update candidate.**
The actual token names in `globals.css` differ from what the standards
document specifies (`--bg-base` vs `--bg-deep`, `--accent-primary` vs
`--accent-blue`). The codebase is internally consistent — it is the
standards doc that is out of sync. Recommend updating
`ENGINEERING_STANDARDS_FRONTEND.md` Section 2.2B Rule 1 to reflect
actual token names rather than renaming tokens throughout the codebase.

**Three backend pre-computation items.**
F07-V21, F07-V26, F07-V30 require backend changes before the frontend
can be fixed. These should be scoped as part of the next backend
engine work rather than the frontend remediation sprint. Flag for
TASK-030 planning.

**Duplicate class definitions in globals.css.**
Noted in F02 findings but not raised as a named violation — no rule
explicitly covers this. Flag for the architect as a maintenance risk
during the globals.css token remediation pass.

---

## SECTION 6 — PRE-EXISTING VIOLATIONS CONFIRMED

| Original ID | Description | Confirmed In |
|-------------|-------------|-------------|
| F02-V01 | No test stack (Vitest + RTL) | F02 — known from PROJECT_CONTEXT.md |
| F03-V02 | ExecuteResponse.data typed as unknown | F03 — known from PROJECT_CONTEXT.md |
| F04-V05 / F05-V04 | No Error Boundary — root cause F09-V01 | F09 |
| F05-V01 | Eager renderer imports | F05 — known from PROJECT_CONTEXT.md |
| F02-V03 / F03-V04 | AppProvider wrong location | F04-V01 |

---

## SUMMARY
```
TASK-029 Frontend Compliance Audit Series — COMPLETE
Steps: F01–F10
Files audited: 27
Total violations: 90
  HIGH:     24
  MEDIUM:   54
  LOW:      12
Pre-existing confirmed: 8
New violations: 82

Systemic patterns: 8 (see Section 3)
Tier 1 blockers: 2 (ErrorBoundary, accessible combobox primitive)
Tier 2 mechanical fixes: 8 items — low risk
Tier 3 architectural fixes: 13 items — mixed risk

Architect exceptions recommended: 1 (CountUp animation)
Standards doc updates recommended: 1 (token naming drift)
Backend pre-computation required: 3 items (flag for TASK-030)

TASK-029 STATUS: COMPLETE — READY FOR ARCHITECT REVIEW
```