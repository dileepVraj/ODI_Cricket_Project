# AUDIT-F08 - INPUT + COMMON COMPONENTS
**Date:** 2026-03-06
**Task:** TASK-029 - Frontend Compliance Audit Series
**Step:** F08 - Input + Common Components
**Scope:** Read-only audit. Zero code changes.
**Files in scope:**
  - `frontend/components/inputs/SquadBuilder.tsx`
  - `frontend/components/inputs/ExtraInputRenderer.tsx`
  - `frontend/components/common/EmptyState.tsx`
**Project root:** `C:\Cricket_Project_Stable\`
**Output file:** `C:\Cricket_Project_Stable\docs\audits\frontend\AUDIT-F08-inputs-common.md`
**Standards ref:** ENGINEERING_STANDARDS_FRONTEND.md v2.2
  - 2.2A Rule 2 (Strict Tailwind CSS)
  - 2.2A Rule 4 (Component Modularity - 300-line limit)
  - 2.2A Rule 5 (No Domain Logic)
  - 2.2A Rule 6 (TypeScript Strict Mode)
  - 2.2A Rule 11 (Manifest-Driven Input Rendering)
  - 2.2B Rule 1 (CSS Variable System)
  - 2.2B Rule 2 (Named Utility Classes)
  - 2.2B Rule 4 (Icon Library - lucide-react only)
  - 2.2B Rule 5 (Font System)
  - 2.2B Rule 8 (Empty and Fallback States)
  - 2.2C Rule 3 (No Inline Object/Array Props)
  - 2.2E Rule 1 (Interactive Element Labels)
  - 2.2E Rule 2 (Keyboard Navigation)
  - Paradigm 5 (Pre-Computed Payload Mandate)

**Gate 5 note:** paradigm-sentinel will flag a pre-existing violation in
`formats/odi/predictor.py` on every step. This is architect-waived and
tracked under TASK-010. Record the waiver in the task report and proceed.

---

## SECTION 1 - SquadBuilder.tsx

### 1.1 Component Size and SRP (2.2A Rule 4)
| Requirement | Finding | Status |
|-------------|---------|--------|
| File under 300 lines | 388 lines - confirmed from F01 | FLAG |
| Component purpose describable without "and" | `SquadPanel` fetches players, manages dropdown state, and renders the selected squad list | FLAG |
| Named sub-components identified | `SquadPanel`, `resolveSquadBadgeState` identified, but decomposition is incomplete | FLAG |

List every named component or function defined in this file:

| Component / Function | Line Count | Responsibility | SRP Pass? |
|---------------------|-----------|----------------|-----------|
| `SquadBuilder` | 35 | Render the two team squad panels from parent props | PASS |
| `resolveSquadBadgeState` | 5 | Map full/partial/empty flags to a badge state | PASS |
| `SquadPanel` | 293 | Fetch player options, manage search/dropdown state, and render selected players for one side | FAIL |

### 1.2 Manifest-Driven Input Rendering (2.2A Rule 11)
| Requirement | Present | Status |
|-------------|---------|--------|
| Squad builder rendered only when manifest declares it | No in-file manifest gate; component is renderable whenever imported | FLAG |
| Config resolved via `resolveSquadBuilderConfig()` or equivalent helper | No helper present; file consumes raw props and hardcoded panel metadata | FLAG |
| No hardcoded `maxPlayers` defaults in this file | `maxPlayers` is always passed in as a prop | PASS |
| No hardcoded squad size limits | Runtime logic uses `maxPlayers`; no hardcoded limit in execution path | PASS |

### 1.3 No Domain Logic (2.2A Rule 5)
| Requirement | Present | Status |
|-------------|---------|--------|
| No cricket-specific field classification logic | No player-stat classification logic present | PASS |
| No format-specific conditional branches | No format-key branching beyond API parameter pass-through | PASS |
| No statistical thresholds on player data | No stat thresholds or player-metric formulas present | PASS |

### 1.4 Pre-Computed Payload Mandate (Paradigm 5)
| Requirement | Present | Status |
|-------------|---------|--------|
| Player list sourced from pre-loaded context/API data | No; `fetchPlayers()` is called inside UI effects and actions | FLAG |
| No arithmetic on player statistics | No statistical arithmetic present | PASS |
| No badge colour derivation from raw numbers | Badge state is not derived from player stat payloads | PASS |

### 1.5 Icon Library (2.2B Rule 4)
| Requirement | Present | Status |
|-------------|---------|--------|
| Icons imported from `lucide-react` only | Yes | PASS |
| No other icon library imports | Yes | PASS |

### 1.6 CSS Tokens and Named Classes (2.2B Rules 1, 2)
| Requirement | Present | Status |
|-------------|---------|--------|
| No raw hex colours | No raw hex colours found | PASS |
| CSS variables used for colours | Mixed; raw `rgba()` box-shadow still present in dropdown portal | FLAG |
| Named utility classes used where applicable | Repeated long bracket-class strings remain inline | FLAG |

### 1.7 Accessibility (2.2E Rules 1, 2)
| Requirement | Present | Status |
|-------------|---------|--------|
| Search input has label or aria-label | No label or `aria-label` on the search input | FLAG |
| Player add/remove buttons have aria-label | Add/remove controls are clickable `div`/icon nodes without labels | FLAG |
| All interactive elements keyboard accessible | Dropdown toggle, option rows, and remove control are mouse-only | FLAG |
| Icon-only buttons have aria-label | Clickable `ChevronDown` and `X` icons have no `aria-label` | FLAG |

### 1.8 TypeScript Strict Mode (2.2A Rule 6)
| Requirement | Status |
|-------------|--------|
| No `any` type annotations | PASS |
| Props interface fully typed | PASS |
| No unsafe inline casts | FLAG |

### 1.9 Inline Props (2.2C Rule 3)
| Requirement | Present | Status |
|-------------|---------|--------|
| No inline object literals as props | No; dropdown portal uses inline `style={{ ... }}` | FLAG |
| No inline array literals as props | No inline array literals found | PASS |

### 1.10 Findings
- `SquadPanel` combines fetching, filtering, dropdown positioning, selection state, and list rendering in one 293-line component (`96-388`).
- Manifest-driven configuration is not resolved through a helper in this file; panel titles and accent handling are hardcoded at the render site (`46-63`).
- `fetchPlayers()` is executed inside the component both on mount/team change and on "Load Squad", which breaks the pre-computed payload expectation (`117-144`, `169-182`).
- The search input lacks an accessible label, and add/remove/toggle controls rely on clickable icons or `div` nodes rather than keyboard-accessible buttons (`297-320`, `337-343`, `376-379`).
- The dropdown portal uses a raw `rgba()` token and inline `style` object, and the outside-click handler uses `e.target as HTMLElement` (`198-203`, `329-334`).

---

## SECTION 2 - ExtraInputRenderer.tsx

### 2.1 Component Size and SRP (2.2A Rule 4)
| Requirement | Finding | Status |
|-------------|---------|--------|
| File under 300 lines | 326 lines - confirmed from F01 | FLAG |
| Component purpose describable without "and" | `ExtraInputField` resolves sources, fetches remote options, and renders three field variants | FLAG |

List every named component or function defined in this file:

| Component / Function | Line Count | Responsibility | SRP Pass? |
|---------------------|-----------|----------------|-----------|
| `ExtraInputRenderer` | 32 | Filter manifest `extra_inputs` entries and delegate field rendering | PASS |
| `ExtraInputField` | 260 | Resolve source metadata, fetch option lists, and render dropdown/combobox/text controls | FAIL |

### 2.2 Manifest-Driven Input Rendering (2.2A Rule 11)
| Requirement | Present | Status |
|-------------|---------|--------|
| Input fields rendered from manifest `extra_inputs` definition | Yes; fields are built from `Object.entries(extraInputs)` | PASS |
| No hardcoded input field names or types | No; file special-cases `squad_builder`, `country_name`, `dropdown`, and `combobox` | FLAG |
| Config resolved via helper function | No helper present; source parsing and field specialization are inline | FLAG |

### 2.3 No Domain Logic (2.2A Rule 5)
| Requirement | Present | Status |
|-------------|---------|--------|
| No cricket-specific field classification | No; renderer parses `/context/players/`, `team_a`, `team_b`, and host-country sources inline | FLAG |
| No format-specific conditional branches | No format-specific branch found beyond API parameter pass-through | PASS |
| Input validation limited to form-level checks only | Yes; no statistical or engine validation present | PASS |

### 2.4 Icon Library (2.2B Rule 4)
| Requirement | Present | Status |
|-------------|---------|--------|
| Icons imported from `lucide-react` only | Yes | PASS |
| No other icon library imports | Yes | PASS |

### 2.5 CSS Tokens and Named Classes (2.2B Rules 1, 2)
| Requirement | Present | Status |
|-------------|---------|--------|
| No raw hex colours | No raw hex colours found | PASS |
| `context-input` class used for input elements | No; inputs/selects use long inline bracket-class strings instead | FLAG |

### 2.6 Accessibility (2.2E Rules 1, 2)
| Requirement | Present | Status |
|-------------|---------|--------|
| All input fields have labels or aria-label | Labels are present for dropdown, combobox, and text input variants | PASS |
| All interactive elements keyboard accessible | No; combobox wrapper, clear icon, and option rows are click-only `div`/icon controls | FLAG |

### 2.7 TypeScript Strict Mode (2.2A Rule 6)
| Requirement | Status |
|-------------|--------|
| No `any` type annotations | PASS |
| Props interface fully typed | PASS |
| No unsafe inline casts | FLAG |

### 2.8 Findings
- `ExtraInputField` mixes manifest interpretation, remote option fetching, source parsing, and rendering in one 260-line function (`67-326`).
- The renderer hardcodes domain-specific cases for `squad_builder`, `country_name`, `/context/players/`, and `team_a`/`team_b` instead of delegating to a manifest/config helper (`38-39`, `94-108`, `125-141`, `165`).
- Input controls do not use the shared `context-input` class, and the dropdown styling still relies on inline bracket utilities (`176-180`, `234-251`, `317-322`).
- Keyboard accessibility is incomplete because the combobox shell, clear icon, and option rows are not semantic buttons/options with keyboard handlers (`208-231`, `261-300`).
- The outside-click handler uses `e.target as Node`, and hover state is driven through raw `rgba()` literals plus direct `style.background` mutation (`146-152`, `264`, `287-295`).

---

## SECTION 3 - EmptyState.tsx

### 3.1 Component Purpose (2.2A Rule 4)
| Requirement | Present | Status |
|-------------|---------|--------|
| Single responsibility - display empty/no-data state only | Yes | PASS |
| File under 300 lines | 54 lines | PASS |

### 3.2 Usage Contract (2.2B Rule 8)
| Requirement | Present | Status |
|-------------|---------|--------|
| Accepts message or description prop | Accepts `message` prop | PASS |
| Never returns `null` or `<></>` | Always returns visible markup | PASS |
| Renders visible feedback to user | Yes | PASS |

### 3.3 CSS Tokens and Named Classes (2.2B Rules 1, 2)
| Requirement | Present | Status |
|-------------|---------|--------|
| No raw hex colours | No raw hex colours found | PASS |
| Uses design system tokens for styling | Yes; uses CSS variables and existing `btn-ghost` class | PASS |

### 3.4 Icon Library (2.2B Rule 4)
| Requirement | Present | Status |
|-------------|---------|--------|
| Icons imported from `lucide-react` only | Yes | PASS |
| No other icon library imports | Yes | PASS |

### 3.5 TypeScript Strict Mode (2.2A Rule 6)
| Requirement | Status |
|-------------|--------|
| No `any` type annotations | PASS |
| Props interface fully typed | PASS |

### 3.6 Findings
- No confirmed violations in `EmptyState.tsx`. The component stays within SRP, uses typed props, and renders a visible empty state with design-token styling.

---

## VIOLATION REGISTER

| ID | File | Rule | Description | Severity |
|----|------|------|-------------|----------|
| F08-V01 | `frontend/components/inputs/SquadBuilder.tsx` | 2.2A Rule 4 | File is 388 lines, and `SquadPanel` (`96-388`) combines data fetching, dropdown state, and list rendering. | HIGH |
| F08-V02 | `frontend/components/inputs/SquadBuilder.tsx` | 2.2A Rule 11 | Manifest gating/config resolution is not enforced in-file; the component consumes raw props and hardcoded panel metadata instead of a helper contract (`46-63`). | MEDIUM |
| F08-V03 | `frontend/components/inputs/SquadBuilder.tsx` | Paradigm 5 | `fetchPlayers()` runs inside UI effects/actions instead of consuming pre-loaded payload data (`117-144`, `169-182`). | HIGH |
| F08-V04 | `frontend/components/inputs/SquadBuilder.tsx` | 2.2B Rule 1 / 2.2C Rule 3 | Dropdown portal uses a raw `rgba()` color token and inline `style={{ top, left, width }}` object (`329-334`). | MEDIUM |
| F08-V05 | `frontend/components/inputs/SquadBuilder.tsx` | 2.2E Rules 1, 2 | Search input lacks a label, and add/remove/toggle controls use click-only icon or `div` nodes without accessible labels (`297-320`, `337-343`, `376-379`). | HIGH |
| F08-V06 | `frontend/components/inputs/SquadBuilder.tsx` | 2.2A Rule 6 | Outside-click logic uses unsafe inline cast `e.target as HTMLElement` (`198-203`). | MEDIUM |
| F08-V07 | `frontend/components/inputs/ExtraInputRenderer.tsx` | 2.2A Rule 4 | File is 326 lines, and `ExtraInputField` (`67-326`) mixes source resolution, remote fetching, and multi-variant rendering. | HIGH |
| F08-V08 | `frontend/components/inputs/ExtraInputRenderer.tsx` | 2.2A Rule 11 | Renderer hardcodes domain field cases (`squad_builder`, `country_name`) and inline source parsing for `/context/players/`, `team_a`, and `team_b` instead of using a helper contract (`38-39`, `94-108`, `125-141`, `165`). | HIGH |
| F08-V09 | `frontend/components/inputs/ExtraInputRenderer.tsx` | 2.2B Rule 2 | Input and select controls do not use the shared `context-input` class and instead repeat long inline bracket-class strings (`176-180`, `234-251`, `317-322`). | MEDIUM |
| F08-V10 | `frontend/components/inputs/ExtraInputRenderer.tsx` | 2.2E Rule 2 | Combobox shell, clear icon, and option rows are not keyboard-accessible semantic controls (`208-231`, `261-300`). | HIGH |
| F08-V11 | `frontend/components/inputs/ExtraInputRenderer.tsx` | 2.2A Rule 6 | Outside-click logic uses unsafe inline casts `e.target as Node` (`146-152`). | MEDIUM |
| F08-V12 | `frontend/components/inputs/ExtraInputRenderer.tsx` | 2.2B Rule 1 | Dropdown styling uses raw `rgba()` literals and direct DOM hover style mutation instead of CSS-token styling (`264`, `287-295`). | MEDIUM |

---

## SUMMARY
```
Files audited: 3
  SquadBuilder.tsx (388 lines) - VIOLATIONS
  ExtraInputRenderer.tsx (326 lines) - VIOLATIONS
  EmptyState.tsx (54 lines) - COMPLIANT

Total violations found this step: 12
New violations (not in pre-existing list): 12
Pre-existing violations confirmed: 0

F08 STATUS: COMPLETE
```
