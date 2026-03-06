# AUDIT-F07 - RENDERER COMPONENTS
**Date:** 2026-03-06
**Task:** TASK-029 - Frontend Compliance Audit Series
**Step:** F07 - Renderer Components
**Scope:** Read-only audit. Zero code changes.
**Files in scope:**
  - `frontend/components/renderers/ReportCard.tsx`
  - `frontend/components/renderers/ComparisonTable.tsx`
  - `frontend/components/renderers/MatrixTable.tsx`
  - `frontend/components/renderers/FormTable.tsx`
  - `frontend/components/renderers/DataTable.tsx`
  - `frontend/components/renderers/PhaseAnalysisCard.tsx`
  - `frontend/components/renderers/VenueMatchupReport.tsx`
  - `frontend/components/renderers/PredictionCard.tsx`
  - `frontend/components/renderers/PlayerProfileCard.tsx`
  - `frontend/components/renderers/MatchupTable.tsx`
  - `frontend/components/renderers/DownloadPanel.tsx`
  - `frontend/components/renderers/MatchAuditSection.tsx`
  - `frontend/components/renderers/SkeletonLoader.tsx`
**Project root:** `C:\Cricket_Project_Stable\`
**Output file:** `C:\Cricket_Project_Stable\docs\audits\frontend\AUDIT-F07-renderers.md`
**Standards ref:** ENGINEERING_STANDARDS_FRONTEND.md v2.2
  - 2.2A Rule 1 (API Wrapper Mandate)
  - 2.2A Rule 2 (Strict Tailwind CSS)
  - 2.2A Rule 4 (Component Modularity - 300-line limit)
  - 2.2A Rule 5 (No Domain Logic)
  - 2.2A Rule 6 (TypeScript Strict Mode)
  - 2.2B Rule 1 (CSS Variable System)
  - 2.2B Rule 3 (Four-Tier Badge Semantics)
  - 2.2B Rule 4 (Icon Library - lucide-react only)
  - 2.2B Rule 5 (Font System)
  - 2.2B Rule 6 (Animation - Design System Only)
  - 2.2B Rule 7 (Renderer Pattern - One File Per Output Type)
  - 2.2B Rule 8 (Empty and Fallback States)
  - 2.2C Rule 3 (No Inline Object/Array Props)
  - 2.2D Rule 2 (Error Boundary Placement - renderers must throw, not catch)
  - 2.2E Rule 1 (Interactive Element Labels)
  - Paradigm 5 (Pre-Computed Payload Mandate)

**Gate 5 note:** paradigm-sentinel will flag a pre-existing violation in
`formats/odi/predictor.py` on every step. This is architect-waived and
tracked under TASK-010. Record the waiver in the task report and proceed.

---

## SECTION 1 - Per-File Checklist

For each renderer file, complete the following checks.
Use PASS / FAIL / N/A for each cell.

### Key to checks:
- **SRP** - Can the component's purpose be described without "and"? Line count under 300?
- **No domain logic** - No arithmetic, string parsing, or statistical thresholds on API data
- **No raw fetch** - No direct `fetch()` calls
- **Badge semantics** - Badge classes driven by pre-computed backend flags, not frontend calculations
- **Empty state** - Uses `EmptyState` component or throws on null/empty data - never returns `null` or `<></>`
- **No @keyframes** - No custom keyframe definitions in this file
- **lucide-react only** - Icons only from lucide-react
- **Font system** - Numeric data uses `font-numeric` class or `var(--font-numeric)`
- **No any** - No `any` type annotations
- **CSS tokens** - No raw hex colours - uses CSS variables from globals.css
- **No inline objects/arrays as props** - No `style={{}}` except runtime-computed, no inline object/array props
- **No silent catch** - No try/catch swallowing render errors

| File | SRP | No domain logic | No raw fetch | Badge semantics | Empty state | No @keyframes | lucide-react only | Font system | No any | CSS tokens | No inline props | No silent catch |
|------|-----|----------------|--------------|----------------|-------------|---------------|------------------|-------------|--------|------------|-----------------|-----------------|
| `ReportCard.tsx` | PASS | FAIL | PASS | PASS | FAIL | PASS | PASS | PASS | FAIL | FAIL | PASS | PASS |
| `ComparisonTable.tsx` | PASS | PASS | PASS | PASS | FAIL | PASS | PASS | FAIL | FAIL | PASS | PASS | PASS |
| `MatrixTable.tsx` | PASS | FAIL | PASS | PASS | FAIL | PASS | PASS | FAIL | FAIL | PASS | PASS | PASS |
| `FormTable.tsx` | PASS | PASS | PASS | PASS | FAIL | PASS | PASS | FAIL | FAIL | FAIL | PASS | PASS |
| `DataTable.tsx` | PASS | PASS | PASS | PASS | FAIL | PASS | PASS | FAIL | FAIL | PASS | PASS | FAIL |
| `PhaseAnalysisCard.tsx` | FAIL | FAIL | PASS | N/A | FAIL | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `VenueMatchupReport.tsx` | PASS | PASS | PASS | N/A | FAIL | PASS | PASS | PASS | FAIL | FAIL | PASS | PASS |
| `PredictionCard.tsx` | PASS | FAIL | PASS | N/A | FAIL | PASS | PASS | FAIL | FAIL | PASS | PASS | PASS |
| `PlayerProfileCard.tsx` | PASS | FAIL | PASS | FAIL | FAIL | PASS | PASS | FAIL | FAIL | FAIL | FAIL | PASS |
| `MatchupTable.tsx` | PASS | PASS | PASS | PASS | FAIL | PASS | PASS | FAIL | PASS | FAIL | PASS | PASS |
| `DownloadPanel.tsx` | PASS | PASS | PASS | N/A | FAIL | PASS | PASS | PASS | PASS | FAIL | PASS | PASS |
| `MatchAuditSection.tsx` | PASS | FAIL | PASS | PASS | FAIL | PASS | PASS | PASS | FAIL | PASS | PASS | PASS |
| `SkeletonLoader.tsx` | PASS | PASS | PASS | N/A | N/A | PASS | PASS | N/A | PASS | PASS | PASS | PASS |

---

## SECTION 2 - File Size Flags

| File | Line Count | Flag |
|------|-----------|------|
| `PhaseAnalysisCard.tsx` | 425 | FLAG - confirmed from F01, exceeds 300-line limit |
| `ReportCard.tsx` | 151 | OK |
| `ComparisonTable.tsx` | 132 | OK |
| `MatrixTable.tsx` | 176 | OK |
| `FormTable.tsx` | 137 | OK |
| `DataTable.tsx` | 216 | OK |
| `VenueMatchupReport.tsx` | 287 | OK |
| `PredictionCard.tsx` | 194 | OK |
| `PlayerProfileCard.tsx` | 225 | OK |
| `MatchupTable.tsx` | 141 | OK |
| `DownloadPanel.tsx` | 111 | OK |
| `MatchAuditSection.tsx` | 129 | OK |
| `SkeletonLoader.tsx` | 125 | OK |

List any additional files found to exceed 300 lines during audit.

None beyond `PhaseAnalysisCard.tsx`.

---

## SECTION 3 - Domain Logic Deep Check (Paradigm 5)

For any renderer where domain logic is suspected, document
the specific lines and nature of the violation here.

| File | Line(s) | Violation Type | Description |
|------|---------|---------------|-------------|
| `ReportCard.tsx` | 21-24, 36-42 | String parsing + frontend numeric derivation | The renderer reformats payload keys and recomputes percentage display values from raw payload fields before rendering. |
| `MatrixTable.tsx` | 27-33, 49-60, 129-133, 149-150 | String parsing + route derivation | The renderer detects special `OVERALL` rows, sorts payload values, and derives rivalry navigation from row data. |
| `PhaseAnalysisCard.tsx` | 116-120, 186-201, 319-320, 347-352, 420-424 | Payload transformation + fallback thresholds | The renderer derives venue labels, injects fallback filter thresholds, reconstructs fallback scenario rows, and formats numbers from raw payload data. |
| `PredictionCard.tsx` | 39-58 | Arithmetic + fallback defaults | The renderer calculates score ranges and gauge positions with hardcoded defaults instead of consuming a fully precomputed payload. |
| `PlayerProfileCard.tsx` | 34-49, 62-70, 72-137, 180-184 | Heuristic payload classification | The renderer infers batting/bowling/context sections from key-name heuristics and constructs quick-link routes from payload values. |
| `MatchAuditSection.tsx` | 31-42 | Date parsing + payload resorting | The renderer parses `start_date` values and re-sorts audit rows client-side. |

---

## SECTION 4 - Badge Semantics Deep Check (2.2B Rule 3)

For any renderer where badge class derivation is suspected,
document whether the class is driven by a pre-computed backend
flag or a frontend calculation.

| File | Line(s) | Badge Class | Driven By | Status |
|------|---------|-------------|-----------|--------|
| `PlayerProfileCard.tsx` | 149 | `badge badge-strong` | Hardcoded frontend class for the team label; no backend tone/flag is consulted. | FAIL |

---

## SECTION 5 - Empty State Deep Check (2.2B Rule 8)

For any renderer where empty state handling is missing or
returns null/empty fragment, document here.

| File | Finding | Status |
|------|---------|--------|
| `ReportCard.tsx` | Returns an inline fallback `<div>` for missing data instead of `EmptyState` or throwing. | FAIL |
| `ComparisonTable.tsx` | Returns an inline fallback `<div>` for empty arrays instead of `EmptyState` or throwing. | FAIL |
| `MatrixTable.tsx` | Returns an inline fallback `<div>` for empty data instead of `EmptyState` or throwing. | FAIL |
| `FormTable.tsx` | Returns an inline fallback `<div>` for empty form rows instead of `EmptyState` or throwing. | FAIL |
| `DataTable.tsx` | Returns an inline fallback `<div>` for empty data instead of `EmptyState` or throwing. | FAIL |
| `PhaseAnalysisCard.tsx` | Returns an inline fallback `<div>` for invalid payloads instead of `EmptyState` or throwing. | FAIL |
| `VenueMatchupReport.tsx` | Returns `null` when `team_a` or `team_b` is missing. | FAIL |
| `PredictionCard.tsx` | Returns an inline fallback `<div>` for invalid payloads instead of `EmptyState` or throwing. | FAIL |
| `PlayerProfileCard.tsx` | Returns an inline fallback `<div>` for invalid payloads instead of `EmptyState` or throwing. | FAIL |
| `MatchupTable.tsx` | Returns an inline fallback `<div>` for empty data instead of `EmptyState` or throwing. | FAIL |
| `DownloadPanel.tsx` | Returns an inline fallback `<div>` for invalid payloads instead of `EmptyState` or throwing. | FAIL |
| `MatchAuditSection.tsx` | Returns `null` when `records` is empty. | FAIL |

---

## SECTION 6 - TypeScript Issues Deep Check (2.2A Rule 6)

For any renderer with `any` annotations or unsafe casts,
document the specific usage.

| File | Line(s) | Issue | Status |
|------|---------|-------|--------|
| `ReportCard.tsx` | 38 | Unsafe cast of `percent_breakdown` to `Record<string, unknown>`. | FAIL |
| `ComparisonTable.tsx` | 45, 55, 85 | Repeated inline casts from payload rows to `ComparisonRow` / `SectionTone` / `ValueTone`. | FAIL |
| `MatrixTable.tsx` | 28, 32 | Inline casts from filtered payload rows to `MatrixRow` / `MatrixRow[]`. | FAIL |
| `FormTable.tsx` | 59 | Inline cast of `data` to `FormRow[]`. | FAIL |
| `DataTable.tsx` | 38, 126 | Inline casts from `data` / `row` to `DataRow`. | FAIL |
| `VenueMatchupReport.tsx` | 208 | Unsafe cast of `team_tone` to `TeamTone`. | FAIL |
| `PredictionCard.tsx` | 49-50 | Inline casts of notes and gauge payload fragments to `string[]` and `Record<string, unknown>`. | FAIL |
| `PlayerProfileCard.tsx` | 35 | Unsafe cast in `toObj()` from unknown payload values to `Record<string, unknown>`. | FAIL |
| `MatchAuditSection.tsx` | 104 | Inline cast of each row to `MatchAuditRow`. | FAIL |

---

## VIOLATION REGISTER

| ID | File | Rule | Description | Severity |
|----|------|------|-------------|----------|
| F07-V01 | `frontend/components/renderers/ReportCard.tsx` | 2.2A Rule 5 | The renderer reformats payload keys and derives percentage values from raw payload fields before rendering. | MEDIUM |
| F07-V02 | `frontend/components/renderers/ReportCard.tsx` | 2.2B Rule 8 | Missing-data handling uses an inline fallback `<div>` instead of `EmptyState` or a thrown error. | MEDIUM |
| F07-V03 | `frontend/components/renderers/ReportCard.tsx` | 2.2A Rule 6 | The file uses an unsafe cast for `percent_breakdown`. | MEDIUM |
| F07-V04 | `frontend/components/renderers/ReportCard.tsx` | 2.2B Rule 1 | Styling includes raw hex/rgba colour literals in gradients and badge surfaces. | MEDIUM |
| F07-V05 | `frontend/components/renderers/ComparisonTable.tsx` | 2.2B Rule 8 | Empty-state handling uses an inline fallback `<div>` instead of `EmptyState` or a thrown error. | MEDIUM |
| F07-V06 | `frontend/components/renderers/ComparisonTable.tsx` | 2.2B Rule 5 | Numeric values use `font-variant-numeric` only and do not opt into `font-numeric` / `var(--font-numeric)`. | LOW |
| F07-V07 | `frontend/components/renderers/ComparisonTable.tsx` | 2.2A Rule 6 | The renderer relies on repeated inline casts from payload rows to internal row/tone types. | MEDIUM |
| F07-V08 | `frontend/components/renderers/MatrixTable.tsx` | 2.2A Rule 5 | The renderer parses payload strings to detect `OVERALL` rows and builds domain navigation targets from row data. | MEDIUM |
| F07-V09 | `frontend/components/renderers/MatrixTable.tsx` | 2.2B Rule 8 | Empty-state handling uses an inline fallback `<div>` instead of `EmptyState` or a thrown error. | MEDIUM |
| F07-V10 | `frontend/components/renderers/MatrixTable.tsx` | 2.2B Rule 5 | Numeric table cells use `font-variant-numeric` only and do not opt into the numeric font system. | LOW |
| F07-V11 | `frontend/components/renderers/MatrixTable.tsx` | 2.2A Rule 6 | The renderer uses inline casts to coerce payload rows into `MatrixRow` types. | MEDIUM |
| F07-V12 | `frontend/components/renderers/FormTable.tsx` | 2.2B Rule 8 | Empty-state handling uses an inline fallback `<div>` instead of `EmptyState` or a thrown error. | MEDIUM |
| F07-V13 | `frontend/components/renderers/FormTable.tsx` | 2.2B Rule 5 | Numeric score displays use `font-variant-numeric` only and do not opt into the numeric font system. | LOW |
| F07-V14 | `frontend/components/renderers/FormTable.tsx` | 2.2A Rule 6 | The renderer uses an inline cast from `data` to `FormRow[]`. | MEDIUM |
| F07-V15 | `frontend/components/renderers/FormTable.tsx` | 2.2B Rule 1 | `resultClasses()` hardcodes raw Tailwind colour utilities instead of relying on CSS-variable tokens. | MEDIUM |
| F07-V16 | `frontend/components/renderers/DataTable.tsx` | 2.2B Rule 8 | Empty-state handling uses an inline fallback `<div>` instead of `EmptyState` or a thrown error. | MEDIUM |
| F07-V17 | `frontend/components/renderers/DataTable.tsx` | 2.2B Rule 5 | Numeric table cells use `font-variant-numeric` only and do not opt into the numeric font system. | LOW |
| F07-V18 | `frontend/components/renderers/DataTable.tsx` | 2.2A Rule 6 | The renderer uses inline casts from payload rows into `DataRow`. | MEDIUM |
| F07-V19 | `frontend/components/renderers/DataTable.tsx` | 2.2D Rule 2 | `formatCell()` silently catches serialization failures and substitutes fallback strings. | MEDIUM |
| F07-V20 | `frontend/components/renderers/PhaseAnalysisCard.tsx` | 2.2A Rule 4 | File size is 425 lines and the component mixes header, filter notice, phase tables, global habits, and audit rendering responsibilities. | HIGH |
| F07-V21 | `frontend/components/renderers/PhaseAnalysisCard.tsx` | 2.2A Rule 5 | The renderer derives labels, fallback thresholds, fallback scenario rows, and number formatting from raw payload data. | HIGH |
| F07-V22 | `frontend/components/renderers/PhaseAnalysisCard.tsx` | 2.2B Rule 8 | Invalid payload handling uses an inline fallback `<div>` instead of `EmptyState` or a thrown error. | MEDIUM |
| F07-V23 | `frontend/components/renderers/VenueMatchupReport.tsx` | 2.2B Rule 8 | Missing team payloads cause the renderer to return `null`. | HIGH |
| F07-V24 | `frontend/components/renderers/VenueMatchupReport.tsx` | 2.2A Rule 6 | The renderer uses an unsafe cast for `team_tone`. | MEDIUM |
| F07-V25 | `frontend/components/renderers/VenueMatchupReport.tsx` | 2.2B Rule 1 | The component relies heavily on raw Tailwind colour utilities and rgba literals instead of CSS-variable tokens. | MEDIUM |
| F07-V26 | `frontend/components/renderers/PredictionCard.tsx` | 2.2A Rule 5 | The renderer calculates prediction ranges and gauge defaults from raw payload values instead of consuming a fully precomputed payload. | HIGH |
| F07-V27 | `frontend/components/renderers/PredictionCard.tsx` | 2.2B Rule 8 | Invalid payload handling uses an inline fallback `<div>` instead of `EmptyState` or a thrown error. | MEDIUM |
| F07-V28 | `frontend/components/renderers/PredictionCard.tsx` | 2.2B Rule 5 | Primary numeric displays use `font-variant-numeric` only and do not opt into the numeric font system. | LOW |
| F07-V29 | `frontend/components/renderers/PredictionCard.tsx` | 2.2A Rule 6 | The renderer uses inline casts for notes and gauge payload fragments. | MEDIUM |
| F07-V30 | `frontend/components/renderers/PlayerProfileCard.tsx` | 2.2A Rule 5 | The renderer classifies payload fields by key-name heuristics and derives links from payload values. | HIGH |
| F07-V31 | `frontend/components/renderers/PlayerProfileCard.tsx` | 2.2B Rule 3 | The team badge is hardcoded as `badge-strong` instead of being driven by a backend tone/flag. | MEDIUM |
| F07-V32 | `frontend/components/renderers/PlayerProfileCard.tsx` | 2.2B Rule 8 | Invalid payload handling uses an inline fallback `<div>` instead of `EmptyState` or a thrown error. | MEDIUM |
| F07-V33 | `frontend/components/renderers/PlayerProfileCard.tsx` | 2.2B Rule 5 | Numeric stat tiles use `font-variant-numeric` only and do not opt into the numeric font system. | LOW |
| F07-V34 | `frontend/components/renderers/PlayerProfileCard.tsx` | 2.2A Rule 6 | The renderer uses an unsafe cast in `toObj()` for nested payload fragments. | MEDIUM |
| F07-V35 | `frontend/components/renderers/PlayerProfileCard.tsx` | 2.2B Rule 1 | Styling includes non-token colour literals such as `white`. | LOW |
| F07-V36 | `frontend/components/renderers/PlayerProfileCard.tsx` | 2.2C Rule 3 | `QuickLinks` receives an inline `links` array prop. | MEDIUM |
| F07-V37 | `frontend/components/renderers/MatchupTable.tsx` | 2.2B Rule 8 | Empty-state handling uses an inline fallback `<div>` instead of `EmptyState` or a thrown error. | MEDIUM |
| F07-V38 | `frontend/components/renderers/MatchupTable.tsx` | 2.2B Rule 5 | Numeric table cells use `font-variant-numeric` only and do not opt into the numeric font system. | LOW |
| F07-V39 | `frontend/components/renderers/MatchupTable.tsx` | 2.2B Rule 1 | Bunny-alert row styling hardcodes raw rgba colours outside the CSS token system. | MEDIUM |
| F07-V40 | `frontend/components/renderers/DownloadPanel.tsx` | 2.2B Rule 8 | Invalid payload handling uses an inline fallback `<div>` instead of `EmptyState` or a thrown error. | MEDIUM |
| F07-V41 | `frontend/components/renderers/DownloadPanel.tsx` | 2.2B Rule 1 | Styling includes non-token colour literals such as `white`. | LOW |
| F07-V42 | `frontend/components/renderers/MatchAuditSection.tsx` | 2.2A Rule 5 | The renderer parses dates and re-sorts audit rows client-side. | MEDIUM |
| F07-V43 | `frontend/components/renderers/MatchAuditSection.tsx` | 2.2B Rule 8 | Empty-state handling returns `null` when there are no audit rows. | MEDIUM |
| F07-V44 | `frontend/components/renderers/MatchAuditSection.tsx` | 2.2A Rule 6 | The renderer uses an inline cast from each row to `MatchAuditRow`. | MEDIUM |

*(Populate only confirmed violations - no speculative entries)*

---

## SUMMARY
```
Files audited: 13
Renderer coverage: 11 output_types - all covered by dedicated files

Per-file results:
  ReportCard.tsx - VIOLATIONS
  ComparisonTable.tsx - VIOLATIONS
  MatrixTable.tsx - VIOLATIONS
  FormTable.tsx - VIOLATIONS
  DataTable.tsx - VIOLATIONS
  PhaseAnalysisCard.tsx - VIOLATIONS
  VenueMatchupReport.tsx - VIOLATIONS
  PredictionCard.tsx - VIOLATIONS
  PlayerProfileCard.tsx - VIOLATIONS
  MatchupTable.tsx - VIOLATIONS
  DownloadPanel.tsx - VIOLATIONS
  MatchAuditSection.tsx - VIOLATIONS
  SkeletonLoader.tsx - COMPLIANT

Total violations found this step: 44
New violations (not in pre-existing list): 43
Pre-existing violations confirmed: 1

F07 STATUS: COMPLETE
```
