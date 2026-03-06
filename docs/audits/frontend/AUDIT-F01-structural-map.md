# F01 — STRUCTURAL MAP
=====================

**Date:** 2026-03-06
**Task:** TASK-029 — Frontend Compliance Audit Series
**Step:** F01 — Structural Map + Directory Classification
**Scope:** Read-only audit. Zero code changes.
**Standards ref:** ENGINEERING_STANDARDS_FRONTEND.md v2.2 (Part 0, Rule 10 / 2.2B)

---

## INVENTORY TABLE

### app/ (3 source files)

| File | Layer Role | Primary Responsibility |
|------|-----------|----------------------|
| `app/layout.tsx` | UI Adapter | Root Next.js layout shell — font injection, HTML metadata, AppProvider wrapper |
| `app/globals.css` | ETL Infrastructure | Design system v1.0 — all CSS tokens, named utility classes, keyframes |
| `app/page.tsx` | UI Adapter | Main app shell — 3-layer layout orchestration, CategoryScreen state management |

### lib/ (2 source files)

| File | Layer Role | Primary Responsibility |
|------|-----------|----------------------|
| `lib/api.ts` | ETL Infrastructure | Centralized API client — all fetch calls, error handling, typed wrappers |
| `lib/context.tsx` | ETL Infrastructure | Global React Context — AppProvider, state management, URL bidirectional sync |

### components/layout/ (3 source files)

| File | Layer Role | Primary Responsibility |
|------|-----------|----------------------|
| `components/layout/Sidebar.tsx` | UI Adapter | Sidebar navigation — category listing, function enumeration |
| `components/layout/ContextBar.tsx` | UI Adapter | Context input bar — venue, team, years inputs |
| `components/layout/FormatSelector.tsx` | UI Adapter | Format tab selector — reads manifest status from context |

### components/renderers/ (14 source files)

| File | Layer Role | Primary Responsibility |
|------|-----------|----------------------|
| `components/renderers/FunctionRenderer.tsx` | UI Adapter | Universal output dispatcher — switch on `output_type`, routes to dedicated renderers |
| `components/renderers/ReportCard.tsx` | UI Adapter | Renders `report` output type |
| `components/renderers/ComparisonTable.tsx` | UI Adapter | Renders `comparison_table` output type |
| `components/renderers/MatrixTable.tsx` | UI Adapter | Renders `matrix_table` output type |
| `components/renderers/FormTable.tsx` | UI Adapter | Renders `form_table` output type |
| `components/renderers/DataTable.tsx` | UI Adapter | Renders `table` output type |
| `components/renderers/PhaseAnalysisCard.tsx` | UI Adapter | Renders `phase_analysis` output type |
| `components/renderers/VenueMatchupReport.tsx` | UI Adapter | Renders `venue_matchup_report` output type |
| `components/renderers/PredictionCard.tsx` | UI Adapter | Renders `prediction_card` output type |
| `components/renderers/PlayerProfileCard.tsx` | UI Adapter | Renders `profile_card` output type |
| `components/renderers/MatchupTable.tsx` | UI Adapter | Renders `matchup_table` output type |
| `components/renderers/DownloadPanel.tsx` | UI Adapter | Renders `download_json` output type |
| `components/renderers/MatchAuditSection.tsx` | UI Adapter | Renders match audit enrichment sibling alongside primary renderer |
| `components/renderers/SkeletonLoader.tsx` | UI Adapter | Renders loading skeleton placeholder for renderer output |

### components/inputs/ (2 source files)

| File | Layer Role | Primary Responsibility |
|------|-----------|----------------------|
| `components/inputs/ExtraInputRenderer.tsx` | UI Adapter | Renders manifest-declared extra input fields dynamically |
| `components/inputs/SquadBuilder.tsx` | UI Adapter | Home XI / Away XI squad selection UI |

### components/common/ (1 source file)

| File | Layer Role | Primary Responsibility |
|------|-----------|----------------------|
| `components/common/EmptyState.tsx` | UI Adapter | Shared empty/no-data primitive used across multiple layers |

### components/animations/ (1 source file — ANOMALOUS DIRECTORY)

| File | Layer Role | Primary Responsibility |
|------|-----------|----------------------|
| `components/animations/CountUp.tsx` | UI Adapter | Animated numeric counter primitive |

### components/navigation/ (1 source file — ANOMALOUS DIRECTORY)

| File | Layer Role | Primary Responsibility |
|------|-----------|----------------------|
| `components/navigation/QuickLinks.tsx` | UI Adapter | Quick-links navigation component |

### Root config files (5)

| File | Layer Role | Primary Responsibility |
|------|-----------|----------------------|
| `package.json` | ETL Infrastructure | Project dependency declarations and npm scripts |
| `tsconfig.json` | ETL Infrastructure | TypeScript compiler configuration |
| `next.config.ts` | ETL Infrastructure | Next.js framework configuration (rewrites, etc.) |
| `eslint.config.mjs` | ETL Infrastructure | ESLint rules configuration |
| `postcss.config.mjs` | ETL Infrastructure | PostCSS / Tailwind transformation pipeline |

Non-source files (not classified): `.gitignore`, `README.md`, `package-lock.json`, `public/` (5 SVGs), `app/icon.png`

---

## DIRECTORY CONTRACT AUDIT

Contract from Rule 10 (2.2B):
- `components/layout/` — navigation, shell, bars
- `components/renderers/` — output renderers + FunctionRenderer dispatcher
- `components/inputs/` — squad builders, extra input fields, forms
- `components/common/` — shared primitives used by multiple layers

| File | Current Directory | Compliance |
|------|------------------|------------|
| `components/layout/Sidebar.tsx` | `components/layout/` | COMPLIANT |
| `components/layout/ContextBar.tsx` | `components/layout/` | COMPLIANT |
| `components/layout/FormatSelector.tsx` | `components/layout/` | COMPLIANT |
| `components/renderers/FunctionRenderer.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/ReportCard.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/ComparisonTable.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/MatrixTable.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/FormTable.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/DataTable.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/PhaseAnalysisCard.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/VenueMatchupReport.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/PredictionCard.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/PlayerProfileCard.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/MatchupTable.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/DownloadPanel.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/MatchAuditSection.tsx` | `components/renderers/` | COMPLIANT |
| `components/renderers/SkeletonLoader.tsx` | `components/renderers/` | COMPLIANT |
| `components/inputs/ExtraInputRenderer.tsx` | `components/inputs/` | COMPLIANT |
| `components/inputs/SquadBuilder.tsx` | `components/inputs/` | COMPLIANT |
| `components/common/EmptyState.tsx` | `components/common/` | COMPLIANT |
| `components/animations/CountUp.tsx` | `components/animations/` | VIOLATION — directory not in contract |
| `components/navigation/QuickLinks.tsx` | `components/navigation/` | VIOLATION — directory not in contract |

---

## ANOMALOUS DIRECTORIES

| Directory | Files Contained | Contract Status |
|-----------|----------------|----------------|
| `components/animations/` | `CountUp.tsx` (1 file) | NOT IN CONTRACT — likely belongs in `components/common/` (shared animation primitive) |
| `components/navigation/` | `QuickLinks.tsx` (1 file) | NOT IN CONTRACT — likely belongs in `components/layout/` (navigation component) |

---

## FILE SIZE FLAGS

| File | Line Count | Flag |
|------|-----------|------|
| `app/globals.css` | 649 | WARNING (>500 lines) |
| `app/page.tsx` | 777 | WARNING (>500 lines) |
| `components/renderers/PhaseAnalysisCard.tsx` | 425 | FLAG (>300 lines) |
| `components/inputs/SquadBuilder.tsx` | 388 | FLAG (>300 lines) |
| `components/inputs/ExtraInputRenderer.tsx` | 326 | FLAG (>300 lines) |
| `app/page.tsx` → `CategoryScreen` component | ~353 lines | FLAG (component >300 lines — SRP violation candidate, separate from file-level warning) |

**Note:** CategoryScreen component identified by Agent 2 cross-check. 
File-level flag (777 lines) and component-level flag (353 lines) are 
separate concerns. Component-level violation will be examined in F04.

No files exceed 800 lines — no VIOLATIONS.

---

## SUMMARY

```
Total source files: 27 (app/ + lib/ + components/ — .tsx/.ts/.css)
Total config files: 5 (package.json, tsconfig.json, next.config.ts, eslint.config.mjs, postcss.config.mjs)

Component files audited (in components/): 22
COMPLIANT placements: 20
VIOLATIONS: 2
  - components/animations/CountUp.tsx (directory not in contract)
  - components/navigation/QuickLinks.tsx (directory not in contract)
UNCLASSIFIED: 0

Anomalous directories: 2 (animations/, navigation/)
Size flags (>300 lines): 5 files
Size warnings (>500 lines): 2 files (globals.css 649, page.tsx 777)
Size violations (>800 lines): 0

F01 STATUS: COMPLETE
```
