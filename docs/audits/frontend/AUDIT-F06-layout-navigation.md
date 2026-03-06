# AUDIT-F06 - LAYOUT + NAVIGATION COMPONENTS
**Date:** 2026-03-06
**Task:** TASK-029 - Frontend Compliance Audit Series
**Step:** F06 - Layout + navigation components
**Scope:** Read-only audit. Zero code changes.
**Files in scope:**
  - `frontend/components/layout/FormatSelector.tsx`
  - `frontend/components/layout/ContextBar.tsx`
  - `frontend/components/layout/Sidebar.tsx`
  - `frontend/components/navigation/QuickLinks.tsx`
  - `frontend/components/animations/CountUp.tsx`
**Project root:** `C:\Cricket_Project_Stable\`
**Output file:** `C:\Cricket_Project_Stable\docs\audits\frontend\AUDIT-F06-layout-navigation.md`
**Standards ref:** ENGINEERING_STANDARDS_FRONTEND.md v2.2
  - 2.2A Rule 1 (API Wrapper Mandate)
  - 2.2A Rule 2 (Strict Tailwind CSS)
  - 2.2A Rule 4 (Component Modularity)
  - 2.2A Rule 5 (No Domain Logic)
  - 2.2A Rule 6 (TypeScript Strict Mode)
  - 2.2A Rule 13 (Format String Agnosticism)
  - 2.2B Rule 1 (CSS Variable System)
  - 2.2B Rule 2 (Named Utility Classes)
  - 2.2B Rule 4 (Icon Library - lucide-react only)
  - 2.2B Rule 6 (Animation - Design System Only)
  - 2.2B Rule 9 (Layout Component Pattern)
  - 2.2B Rule 10 (Component Placement - Directory Contract)
  - 2.2C Rule 3 (No Inline Object/Array Props)
  - 2.2E Rule 1 (Interactive Element Labels)
  - 2.2E Rule 2 (Keyboard Navigation)

---

## SECTION 1 - Directory Contract (2.2B Rule 10)

| File | Current Directory | Expected Directory | Status |
|------|------------------|-------------------|--------|
| `FormatSelector.tsx` | `components/layout/` | `components/layout/` | COMPLIANT |
| `ContextBar.tsx` | `components/layout/` | `components/layout/` | COMPLIANT |
| `Sidebar.tsx` | `components/layout/` | `components/layout/` | COMPLIANT |
| `QuickLinks.tsx` | `components/navigation/` | `components/layout/` | VIOLATION - confirmed from F01 |
| `CountUp.tsx` | `components/animations/` | `components/common/` | VIOLATION - confirmed from F01 |

---

## SECTION 2 - FormatSelector.tsx

### 2.1 Layout Component Pattern (2.2B Rule 9)
| Requirement | Present | Status |
|-------------|---------|--------|
| Reads format/manifest data from `useAppContext()` - not props | Yes - `formats`, `activeFormat`, `switchFormat`, and `manifest` come from context at line 7. | PASS |
| No manifest or format data received as props from page.tsx | Yes - component has no props. | PASS |
| Uses `fmt.has_manifest` to control enabled/disabled states | Yes - button disabled state and class use `fmt.has_manifest` at lines 31-34. | PASS |

### 2.2 Format Agnosticism (2.2A Rule 13)
| Requirement | Present | Status |
|-------------|---------|--------|
| No hardcoded format strings (e.g. `"odi"`) | Yes - format keys and labels come from `formats.map(...)` at lines 27-37. | PASS |
| Format list derived from context/manifest | Yes - tabs are derived from `formats` from context. | PASS |

### 2.3 Icon Library (2.2B Rule 4)
| Requirement | Present | Status |
|-------------|---------|--------|
| Icons imported from `lucide-react` only | Yes - `Activity` and `Zap` are imported from `lucide-react` at line 4. | PASS |
| No other icon library imports | Yes - no other icon imports present. | PASS |

### 2.4 Accessibility (2.2E Rules 1, 2)
| Requirement | Present | Status |
|-------------|---------|--------|
| Icon-only buttons have `aria-label` | N/A - format tabs include visible text labels at lines 36-37. | PASS |
| All interactive elements keyboard accessible | Yes - all interactions use native `<button>` elements. | PASS |
| Format tabs respond to Enter/Space | Yes - native buttons provide keyboard activation. | PASS |

### 2.5 TypeScript Strict Mode (2.2A Rule 6)
| Requirement | Status |
|-------------|--------|
| No `any` type annotations | PASS |
| Props interface fully typed | PASS - component has no props |

### 2.6 Findings
No confirmed violations in `FormatSelector.tsx`.

---

## SECTION 3 - ContextBar.tsx

### 3.1 Layout Component Pattern (2.2B Rule 9)
| Requirement | Present | Status |
|-------------|---------|--------|
| Reads context data from `useAppContext()` - not props | Yes - manifest, context values, loaders, teams, and venues come from context at lines 9-17. | PASS |
| No domain data received as props from page.tsx | Yes - top-level component has no props. | PASS |

### 3.2 No Domain Logic (2.2A Rule 5)
| Requirement | Present | Status |
|-------------|---------|--------|
| No arithmetic on context values | Yes - values are passed through; no derived metrics are computed. | PASS |
| No statistical thresholds | Yes - no analytic thresholds are applied to API data. | PASS |
| No format-specific conditional branches | No - option building hardcodes `team_a` and `team_b` field keys at line 50. | FAIL |

### 3.3 CSS Token Usage (2.2B Rule 1)
| Requirement | Present | Status |
|-------------|---------|--------|
| Inputs use `context-input` named class | Yes - select and text input use `context-input` at lines 115 and 223. | PASS |
| No raw hex colours | Yes - colors use CSS variables; no raw hex values are present. | PASS |

### 3.4 Accessibility (2.2E Rules 1, 2)
| Requirement | Present | Status |
|-------------|---------|--------|
| All inputs have labels or aria-label | Yes - each control is paired with a `<label>` at lines 107-112, 214-219, and 260-266. | PASS |
| All interactive elements keyboard accessible | No - the custom venue combobox opens on focus/change only and provides no `onKeyDown`, option roles, or keyboard selection path at lines 220-238 and 194-205. | FAIL |

### 3.5 TypeScript Strict Mode (2.2A Rule 6)
| Requirement | Status |
|-------------|--------|
| No `any` type annotations | PASS |
| Props interface fully typed | PASS - helper props are explicitly typed at lines 97-103, 138-144, and 250-256 |

### 3.6 Findings
- Hardcoded branching on `team_a` / `team_b` injects special-case UI logic instead of deriving dropdown behaviour from manifest metadata (line 50).
- The portal-based venue combobox is pointer-oriented and lacks keyboard navigation semantics for option traversal and selection (lines 194-205, 220-238).

---

## SECTION 4 - Sidebar.tsx

### 4.1 Layout Component Pattern (2.2B Rule 9)
| Requirement | Present | Status |
|-------------|---------|--------|
| Reads manifest/category data from `useAppContext()` - not props | Yes - `manifest` comes from context at line 45. | PASS |
| No manifest or category data received as props | Yes - props carry only UI state (`activeCategory`, `onCategorySelect`). | PASS |

### 4.2 No Domain Logic (2.2A Rule 5)
| Requirement | Present | Status |
|-------------|---------|--------|
| No format-specific conditional branches | Yes - no format-key branching is present. | PASS |
| No hardcoded category or function keys | No - `dashboard` is hardcoded at lines 81-82 and group keys are hardcoded in `GROUP_META` at lines 20-25. | FAIL |

### 4.3 Named Utility Classes (2.2B Rule 2)
| Requirement | Present | Status |
|-------------|---------|--------|
| `sidebar-item` class used for nav items | Yes - used on dashboard, group items, and collapse controls at lines 81, 91, 118, and 144. | PASS |
| `sidebar-group-label` class used for group headers | Yes - used at line 108. | PASS |
| `fn-count` class used for function count badges | Yes - used at line 130. | PASS |

### 4.4 Icon Library (2.2B Rule 4)
| Requirement | Present | Status |
|-------------|---------|--------|
| Icons imported from `lucide-react` only | No - category icons are rendered from emoji literals in `ICON_MAP` at lines 27-37. | FAIL |
| No other icon library imports | Yes - no second icon package is imported, but emoji icon literals still bypass the design-system icon rule. | PASS |

### 4.5 Accessibility (2.2E Rules 1, 2)
| Requirement | Present | Status |
|-------------|---------|--------|
| Sidebar items keyboard accessible | Yes - navigation uses native `<button>` elements. | PASS |
| Icon-only elements have `aria-label` | No - collapsed dashboard/category buttons rely on icons and `title`, but do not expose `aria-label` at lines 79-85 and 115-123. | FAIL |
| Collapsed sidebar icons have `aria-label` | No - collapsed category entries and the collapsed dashboard entry omit explicit labels. | FAIL |

### 4.6 TypeScript Strict Mode (2.2A Rule 6)
| Requirement | Status |
|-------------|--------|
| No `any` type annotations | PASS |
| Props interface fully typed | PASS |

### 4.7 Findings
- `GROUP_META` and the hardcoded dashboard entry encode navigation taxonomy in the component instead of deriving it entirely from manifest data (lines 20-25, 79-82).
- `ICON_MAP` uses emoji literals rather than `lucide-react` icons, breaking the icon library constraint (lines 27-37).
- Collapsed navigation states are not fully labelled for assistive technology; `title` attributes are present, but `aria-label` is missing on icon-only category/dashboard buttons (lines 79-85, 115-123).

---

## SECTION 5 - QuickLinks.tsx

### 5.1 Directory Contract (2.2B Rule 10)
| Finding | Status |
|---------|--------|
| File lives in `components/navigation/` - not in contract | VIOLATION - confirmed from F01 |
| Should be in `components/layout/` | Remediation required |

### 5.2 Layout Component Pattern (2.2B Rule 9)
| Requirement | Present | Status |
|-------------|---------|--------|
| Reads data from `useAppContext()` - not props | No - link definitions are passed as `links` props at line 13. | FAIL |
| No domain data received as props | No - navigational link data is supplied externally through props. | FAIL |

### 5.3 No Domain Logic (2.2A Rule 5)
| Requirement | Present | Status |
|-------------|---------|--------|
| No hardcoded category or function keys | Yes - no category/function keys are hardcoded. | PASS |
| No format-specific branches | No - `resolveHref()` hardcodes `:format` substitution rules at lines 17-20. | FAIL |

### 5.4 Accessibility (2.2E Rules 1, 2)
| Requirement | Present | Status |
|-------------|---------|--------|
| Links keyboard accessible | Yes - rendered with native `Link` anchors. | PASS |
| Icon-only elements have `aria-label` | N/A - links include visible text labels at line 32. | PASS |

### 5.5 TypeScript Strict Mode (2.2A Rule 6)
| Requirement | Status |
|-------------|--------|
| No `any` type annotations | PASS |
| Props interface fully typed | PASS - `QuickLinkItem` is typed at lines 7-10 |

### 5.6 Findings
- `QuickLinks` is not a context-driven layout component; it depends on a `links` prop payload instead of sourcing layout data from app context (line 13).
- `resolveHref()` embeds a format placeholder protocol (`:format`) in component logic, which makes the component non-agnostic across manifest contracts (lines 17-20).

---

## SECTION 6 - CountUp.tsx

### 6.1 Directory Contract (2.2B Rule 10)
| Finding | Status |
|---------|--------|
| File lives in `components/animations/` - not in contract | VIOLATION - confirmed from F01 |
| Should be in `components/common/` | Remediation required |

### 6.2 Animation System (2.2B Rule 6)
| Requirement | Present | Status |
|-------------|---------|--------|
| No custom `@keyframes` defined in this file | Yes - none defined in the component. | PASS |
| Animation uses only design system classes or JS-driven transitions | No - the component implements a bespoke `requestAnimationFrame` loop with local easing logic at lines 37-63. | FAIL |
| No custom transition durations defined in component | No - `duration` is exposed as a component prop and defaults to `1.6` seconds at lines 17 and 27. | FAIL |

### 6.3 Inline Style Usage (2.2A Rule 2)
| Requirement | Present | Status |
|-------------|---------|--------|
| No inline `style={{}}` except runtime-computed values | Yes - no inline `style` prop is used. | PASS |
| Any inline style is justified by runtime computation | Yes - no inline `style` prop is used. | PASS |

### 6.4 TypeScript Strict Mode (2.2A Rule 6)
| Requirement | Status |
|-------------|--------|
| No `any` type annotations | PASS |
| Props interface fully typed | PASS |

### 6.5 Findings
- The component owns custom easing and duration behaviour instead of consuming animation behaviour from the design system (lines 37-63).

---

## VIOLATION REGISTER

| ID | File | Rule | Description | Severity |
|----|------|------|-------------|----------|
| F06-V01 | `frontend/components/navigation/QuickLinks.tsx` | 2.2B Rule 10 | File lives in non-contract directory `components/navigation/` - should be in `components/layout/`. | LOW |
| F06-V02 | `frontend/components/animations/CountUp.tsx` | 2.2B Rule 10 | File lives in non-contract directory `components/animations/` - should be in `components/common/`. | LOW |
| F06-V03 | `frontend/components/layout/ContextBar.tsx` | 2.2A Rule 13 | Dropdown option logic hardcodes `team_a` / `team_b` handling instead of deriving field behaviour from manifest metadata. | MEDIUM |
| F06-V04 | `frontend/components/layout/ContextBar.tsx` | 2.2E Rule 2 | The custom venue combobox lacks keyboard navigation semantics for traversing and selecting portal-rendered options. | HIGH |
| F06-V05 | `frontend/components/layout/Sidebar.tsx` | 2.2A Rule 5 | Sidebar hardcodes navigation taxonomy via `dashboard` and `GROUP_META` keys instead of remaining fully manifest-driven. | MEDIUM |
| F06-V06 | `frontend/components/layout/Sidebar.tsx` | 2.2B Rule 4 | Sidebar category icons are rendered from emoji literals rather than `lucide-react` components. | MEDIUM |
| F06-V07 | `frontend/components/layout/Sidebar.tsx` | 2.2E Rules 1, 2 | Collapsed dashboard/category items become icon-only controls without explicit `aria-label` values. | HIGH |
| F06-V08 | `frontend/components/navigation/QuickLinks.tsx` | 2.2B Rule 9 | `QuickLinks` receives link definitions via props instead of sourcing layout data from app context. | MEDIUM |
| F06-V09 | `frontend/components/navigation/QuickLinks.tsx` | 2.2A Rule 5 / 2.2A Rule 13 | `resolveHref()` hardcodes `:format` placeholder substitution logic inside the component. | MEDIUM |
| F06-V10 | `frontend/components/animations/CountUp.tsx` | 2.2B Rule 6 | `CountUp` implements bespoke easing and duration control rather than using design-system animation primitives only. | MEDIUM |

*(Populate only confirmed violations - no speculative entries)*

---

## SUMMARY
```
Files audited: 5
  FormatSelector.tsx - layout pattern: COMPLIANT
  ContextBar.tsx - layout pattern: COMPLIANT
  Sidebar.tsx - layout pattern: COMPLIANT
  QuickLinks.tsx - directory: VIOLATION (confirmed F01)
  CountUp.tsx - directory: VIOLATION (confirmed F01)

Total violations found this step: 10
New violations (not in pre-existing list): 8
Pre-existing violations confirmed: 2
  (F01 directory violations F06-V01, F06-V02 confirmed)

F06 STATUS: COMPLETE
```
