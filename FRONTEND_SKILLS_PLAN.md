# Frontend Skills Implementation Plan

**Created:** 2026-03-08
**Status:** Planning — awaiting implementation
**Purpose:** Close the enforcement gap between backend and frontend compliance governance.

---

## 1. Problem Statement

The backend has **12 skills** (6 guides + 6 validators) in `core/gen_ai/skills/` that enforce
every architectural rule from `ENGINEERING_STANDARDS_BACKEND.md`. The frontend has **zero**.

`ENGINEERING_STANDARDS_FRONTEND.md` defines **30+ hard-fail rules** across 6 categories
(2.2A–2.2F) and none of them have matching enforcement skills. Agents working on frontend
tasks are currently operating on the honour system — the standards file tells them the rules,
but nothing verifies they followed them.

---

## 2. Structural Prerequisite — Directory Reorganisation

### Current Structure
```
core/gen_ai/skills/
├── guides/
│   ├── bug-fix-guide/
│   ├── context-loader/
│   ├── duckdb-lint-ops/
│   ├── modification-guide/
│   ├── new-feature-guide/
│   └── refactor-guide/
├── validators/
│   ├── boundary-sentinel/
│   ├── event-state-linter/
│   ├── executive-auditor/
│   ├── manifest-contract-verifier/
│   ├── paradigm-sentinel/
│   └── serialization-guard/
└── .system/
    ├── skill-creator/
    └── skill-installer/
```

### New Structure (backend/frontend split)
```
core/gen_ai/skills/
├── guides/
│   ├── backend/
│   │   ├── bug-fix-guide/
│   │   ├── context-loader/
│   │   ├── duckdb-lint-ops/
│   │   ├── modification-guide/
│   │   ├── new-feature-guide/
│   │   └── refactor-guide/
│   └── frontend/
│       ├── frontend-bug-fix-guide/        ← NEW
│       ├── frontend-modification-guide/   ← NEW
│       └── frontend-new-component-guide/  ← NEW
├── validators/
│   ├── backend/
│   │   ├── boundary-sentinel/
│   │   ├── event-state-linter/
│   │   ├── executive-auditor/
│   │   ├── manifest-contract-verifier/
│   │   ├── paradigm-sentinel/
│   │   └── serialization-guard/
│   └── frontend/
│       ├── frontend-lint-sentinel/        ← NEW
│       ├── frontend-paradigm-sentinel/    ← NEW
│       └── frontend-type-sync-guard/      ← NEW
└── .system/
    ├── skill-creator/
    └── skill-installer/
```

### Path Migration Impact

The following files reference skill paths and **must be updated** when directories are moved:

| File | Approximate References | Notes |
|------|----------------------|-------|
| `GEMINI.md` (root) | ~15 paths in Part 3, Part 9 | Gate table, hard prohibitions |
| `AGENTS.md` (root) | ~12 paths in Part 3, Part 8 | Gate table, hard prohibitions |
| `CLAUDE.md` (root) | ~12 paths in Part 3, Part 8 | Gate table, hard prohibitions |
| `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md` | ~25 paths in Parts 4–5 | Gate commands, skill registry |
| `docs/guides/ENGINEERING_STANDARDS_BACKEND.md` | ~25 paths in Parts 4–5 | Gate commands, skill registry |
| `docs/guides/ENGINEERING_STANDARDS_CORE.md` | ~25 paths in Parts 4–5 | Gate commands, skill registry |
| `docs/guides/TECHNICAL_AUDIT_REPORT.md` | ~3 paths | Skill directory overview |
| All existing guide `SKILL.md` files | Variable | Internal cross-references |
| `core/gen_ai/skills/validators/paradigm-sentinel/SKILL.md` | 1 path | References boundary-sentinel |

### Path Mapping (old → new)

| Old Path | New Path |
|----------|----------|
| `core/gen_ai/skills/guides/bug-fix-guide/` | `core/gen_ai/skills/guides/backend/bug-fix-guide/` |
| `core/gen_ai/skills/guides/context-loader/` | `core/gen_ai/skills/guides/backend/context-loader/` |
| `core/gen_ai/skills/guides/duckdb-lint-ops/` | `core/gen_ai/skills/guides/backend/duckdb-lint-ops/` |
| `core/gen_ai/skills/guides/modification-guide/` | `core/gen_ai/skills/guides/backend/modification-guide/` |
| `core/gen_ai/skills/guides/new-feature-guide/` | `core/gen_ai/skills/guides/backend/new-feature-guide/` |
| `core/gen_ai/skills/guides/refactor-guide/` | `core/gen_ai/skills/guides/backend/refactor-guide/` |
| `core/gen_ai/skills/validators/boundary-sentinel/` | `core/gen_ai/skills/validators/backend/boundary-sentinel/` |
| `core/gen_ai/skills/validators/event-state-linter/` | `core/gen_ai/skills/validators/backend/event-state-linter/` |
| `core/gen_ai/skills/validators/executive-auditor/` | `core/gen_ai/skills/validators/backend/executive-auditor/` |
| `core/gen_ai/skills/validators/manifest-contract-verifier/` | `core/gen_ai/skills/validators/backend/manifest-contract-verifier/` |
| `core/gen_ai/skills/validators/paradigm-sentinel/` | `core/gen_ai/skills/validators/backend/paradigm-sentinel/` |
| `core/gen_ai/skills/validators/serialization-guard/` | `core/gen_ai/skills/validators/backend/serialization-guard/` |

---

## 3. New Frontend Validator Skills

### 3.1 frontend-lint-sentinel

**Location:** `core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/`
**Language:** Python (regex-based `.tsx`/`.ts` scanning — consistent with backend validators)
**Trigger:** Any modification to `frontend/` files.

**What it auto-scans (12 rules from 2.2A/2.2B):**

| # | Rule Source | Check | Detection Pattern |
|---|-----------|-------|-------------------|
| 1 | 2.2A-R1 | Raw `fetch()` outside `lib/api.ts` | `fetch(` in any `.tsx`/`.ts` file except `lib/api.ts` |
| 2 | 2.2A-R6 | `any` or `unknown` in domain types | `: any` or `: unknown` in type annotations (not comments) |
| 3 | 2.2A-R7 | Hardcoded function/category keys | String literals matching known manifest keys in component files |
| 4 | 2.2A-R13 | Hardcoded format strings | `"odi"`, `"t20i"`, `"the_hundred"` as raw strings |
| 5 | 2.2B-R1 | Raw hex colors | `#[0-9a-fA-F]{3,8}` outside `globals.css` |
| 6 | 2.2B-R4 | Non-`lucide-react` icon imports | `import.*from ['"](@heroicons\|react-icons\|@phosphor)` |
| 7 | 2.2B-R5 | Wrong font application | `font-family:` in inline styles or arbitrary Tailwind |
| 8 | 2.2B-R6 | Custom keyframes in components | `@keyframes` in `.tsx` or component CSS files |
| 9 | 2.2C-R1 | Eager renderer imports | Non-`React.lazy()` imports in `FunctionRenderer.tsx` |
| 10 | 2.2D-R3 | Missing `@schema` JSDoc | Types in `lib/types.ts` without `@schema` comment |
| 11 | 2.2E-R1 | Icon buttons without `aria-label` | `<button>` containing only `<Icon>` with no `aria-label` |
| 12 | 2.2F-R1 | Non-Vitest test framework | `import.*from ['"]jest\|mocha\|enzyme` |

**Script:** `scripts/run_frontend_lint.py`
**Output format:** Same as boundary-sentinel (`Pass` / `Fail` with `file:line:col` evidence)

### 3.2 frontend-paradigm-sentinel

**Location:** `core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/`
**Language:** Python
**Trigger:** Always — after primary frontend gates pass.

**What it checks:**

| # | Rule Source | Check |
|---|-----------|-------|
| 1 | 2.2A-R5 | Domain logic in components — arithmetic on API response data |
| 2 | 2.2A-R4 | Component file size >300 lines |
| 3 | 2.2B-R7 | Renderer not in `components/renderers/` |
| 4 | 2.2B-R9 | Layout component receiving data as props instead of context |
| 5 | 2.2B-R10 | Component in wrong directory per placement contract |
| 6 | 2.2A-R3 | External state library imports (Redux, Zustand, MobX, Jotai) |
| 7 | 2.2A-R14 | `setInterval`/`setTimeout` calling `/execute/` endpoint |
| 8 | 2.2D-R2 | `try/catch` inside a renderer component swallowing errors |

**Script:** `scripts/run_frontend_paradigm.py`

### 3.3 frontend-type-sync-guard

**Location:** `core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/`
**Language:** Python
**Trigger:** Any modification to `lib/types.ts` or backend schema types.

**What it checks:**

| # | Check |
|---|-------|
| 1 | Every interface in `lib/types.ts` mapping to a backend schema has `@schema` JSDoc |
| 2 | Cross-reference: if a backend Pydantic model changed, the corresponding frontend type must also be updated in the same task |

**Script:** `scripts/run_type_sync.py`

---

## 4. New Frontend Guide Skills

### 4.1 frontend-bug-fix-guide

**Location:** `core/gen_ai/skills/guides/frontend/frontend-bug-fix-guide/`
**Structure:** Mirrors `bug-fix-guide` but with frontend-adapted checkpoints.

**Key differences from backend bug-fix-guide:**
- Standards file reference: `ENGINEERING_STANDARDS_FRONTEND.md` (not `_BACKEND.md`)
- RCA trace follows the frontend path: Next.js → API → Engine → DAL → ETL
- Mandate checks use frontend rules (CSS tokens, manifest-driven UI, no domain logic)
- Gate sequence uses **frontend gates** (F1–F3) plus existing Gates 5–6
- Component SRP check: verify the fix doesn't give a component a second responsibility

**Checkpoint phases:** Same 4-phase structure as backend (pre-conditions → execution → final gates → task report)

### 4.2 frontend-modification-guide

**Location:** `core/gen_ai/skills/guides/frontend/frontend-modification-guide/`
**Structure:** Mirrors `modification-guide` but with frontend-specific delta discipline.

**Key differences from backend modification-guide:**
- CSS token compliance verification on any styling change
- Manifest-driven rendering verification (is the change reflected in manifest?)
- Pre-computed payload mandate check (agent isn't adding domain logic to frontend?)
- Component placement contract verification
- Frontend gate sequence

### 4.3 frontend-new-component-guide

**Location:** `core/gen_ai/skills/guides/frontend/frontend-new-component-guide/`
**Structure:** Purpose-built guide for adding new React components.

**Checkpoints:**
1. Component classification: layout / renderer / input / common
2. Directory placement per 2.2B-R10 contract
3. If renderer: lazy loading in FunctionRenderer, error boundary wrapping, manifest registration
4. If layout: must read from context, not receive as props
5. CSS token usage (no raw hex, use design system classes)
6. Accessibility: aria-labels, keyboard navigation, aria-live
7. TypeScript strict: no `any`, all props typed
8. File size pre-check: plan decomposition if >300 lines likely

---

## 5. Frontend Gate Sequence

To be added to `ENGINEERING_STANDARDS_FRONTEND.md` Part 4.3:

```
GATE F1 — frontend-lint-sentinel
Trigger: any modification to frontend/ files.
Path: core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/
Run: python core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/scripts/run_frontend_lint.py --root .
Pass: zero violations.

GATE F2 — frontend-paradigm-sentinel
Trigger: always — after F1 passes.
Path: core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/
Run: python core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/scripts/run_frontend_paradigm.py --root .
Pass: zero violations.

GATE F3 — frontend-type-sync-guard
Trigger: any modification to lib/types.ts or backend schema types.
Path: core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/
Run: python core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/scripts/run_type_sync.py --root .
Pass: zero violations.

GATE 5 — paradigm-sentinel (existing backend meta-check)
Trigger: always — catch cross-layer violations.

GATE 6 — compliance_bouncer (final gate, unchanged)
Trigger: always.
```

---

## 6. Script Language Decision

**Python** is the correct choice for frontend validators. Rationale:

1. **Consistency** — All 6 existing backend validators use Python. One language for all governance scripts.
2. **Regex is sufficient** — The frontend checks are pattern-matching (raw fetch, hex colors, format strings). No AST parsing of TypeScript is needed.
3. **No Node dependency** — Running Node scripts adds `npx` overhead and potential version mismatches. Python is already the project's governance runtime.
4. **Bouncer integration** — The compliance bouncer is Python. Frontend gates integrating with the same runtime is natural.

---

## 7. Implementation Order

### Phase 1 — Structural (must come first)
| Task | Description |
|------|------------|
| TASK-048 | Create `backend/` and `frontend/` subdirectories under `guides/` and `validators/` |
| TASK-049 | Move existing backend skills into `*/backend/` subdirectories |
| TASK-050 | Update all path references in GEMINI.md, AGENTS.md, CLAUDE.md, all 3 ENGINEERING_STANDARDS files, TECHNICAL_AUDIT_REPORT, and all existing SKILL.md cross-references |

### Phase 2 — Frontend Validators (automated checks)
| Task | Description |
|------|------------|
| TASK-051 | Build `frontend-lint-sentinel` — SKILL.md + Python scanner script |
| TASK-052 | Build `frontend-paradigm-sentinel` — SKILL.md + Python scanner script |
| TASK-053 | Build `frontend-type-sync-guard` — SKILL.md + Python scanner script |

### Phase 3 — Frontend Guides (workflow enforcement)
| Task | Description |
|------|------------|
| TASK-054 | Build `frontend-bug-fix-guide` — SKILL.md with checkpoint workflow |
| TASK-055 | Build `frontend-modification-guide` — SKILL.md with checkpoint workflow |
| TASK-056 | Build `frontend-new-component-guide` — SKILL.md with checkpoint workflow |

### Phase 4 — Integration
| Task | Description |
|------|------------|
| TASK-057 | Add frontend gates (F1–F3) to ENGINEERING_STANDARDS_FRONTEND.md Part 4.3 |
| TASK-058 | Update report templates in GEMINI.md, AGENTS.md, CLAUDE.md to include frontend gates |

---

## 8. Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Path references missed during migration | Grep scan all `.md` and `.py` files for old paths. Script-assisted verification. |
| Existing backend gate commands break | Each move task includes a gate smoke test — run all 6 existing gates after the move. |
| False positives in frontend lint | Start strict, whitelist known exceptions. Better to over-flag than under-flag. |
| Agents confused by dual gate sequences | Gate naming convention: `GATE 1–6` = backend, `GATE F1–F3` = frontend. Standards files specify which sequence applies per task scope. |

---

## 9. Success Criteria

1. All existing backend skills in `*/backend/` subdirectories, all gates still passing.
2. All path references across 8+ files updated correctly, zero stale references.
3. 3 new frontend validators operational with Python scripts.
4. 3 new frontend guides with checkpoint workflows.
5. Frontend gate sequence (F1–F3) integrated into `ENGINEERING_STANDARDS_FRONTEND.md`.
6. Report templates updated to include frontend gate results.

---

*End of FRONTEND_SKILLS_PLAN.md — Created 2026-03-08*
