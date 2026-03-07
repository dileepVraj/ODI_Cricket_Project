# BACKLOG.md
**Purpose:** Project planning board — all scheduled, in-review, and icebox tasks.
**Last Updated:** 2026-03-07
**Maintained by:** Human Architect
**Do NOT attach to AI agents** — use SESSION_STATE.md for agent context.

---

## HOW TO USE

- **IN REVIEW** — completed this sprint, pending final architect sign-off
- **BACKLOG** — scheduled, broken into subtasks, ready to action
- **ICEBOX** — future ideas, not scheduled, no subtasks yet

Task IDs are sequential. Never reuse an ID.
When a task moves to COMPLETE, log it in PROJECT_CONTEXT.md Section 10
and remove from this file.

---

## Tasks Status values:

- Open — not started
- In Progress — actively being worked
- Blocked — waiting on dependency
- Closed — YYYY-MM-DD — done

---

## IN REVIEW

- Nothing as of now.

---

## BACKLOG

### [TASK-010] Engine Layer Refactoring
**Status:** In Progress — Phase 10
**Priority:** Critical
**Scope:** Backend
**Blocked by:** Nothing
**Why:** Primary active work. Engine files in formats/
  need full Part 0 and Part 1 compliance verification
  and refactoring.
  **Note**: "Pre-existing DAL usage flagged at formats/odi/predictor.py lines 36, 71, 73 — confirmed in scope for predictor engine audit"
**Progress:**
  - [x] Team engine — COMPLIANT 2026-03-05
  - [x] Player engine — COMPLIANT 2026-03-06
        (audit: TASK-026, refactor: TASK-027, review: TASK-028)
  - [ ] Predictor engine — not started
  - [ ] Any additional engines in formats/
**Subtasks remaining:**
  - [ ] Audit predictor engine (repeat TASK-026 pattern)
  - [ ] Refactor predictor engine (repeat TASK-027 pattern)
  - [ ] Architect review predictor engine (repeat TASK-028 pattern)
  - [ ] Repeat for any remaining engines in formats/
  - [ ] Final bouncer pass across full codebase
  - [ ] Update TECHNICAL_AUDIT_REPORT.md on completion

---

### [TASK-011] Update TECHNICAL_AUDIT_REPORT.md
**Status:** Blocked
**Priority:** Medium
**Scope:** Documentation
**Blocked by:** TASK-010 must complete first
**Why:** Stale since 2026-02-27, predates Phase 11.3
  completion and engine refactoring.
**Subtasks:**
  - [ ] Review current report sections
  - [ ] Update phase status to reflect Phase 11.3 complete
  - [ ] Update engine compliance status after TASK-010
  - [ ] Increment version to v3.2.0
  - [ ] Update audit date

---

### [TASK-012] Token optimisation — section-aware context loading
**Status:** Open
**Priority:** Low
**Scope:** AI Tooling
**Blocked by:** Needs 1 week monitoring first (from 2026-03-03)
**Why:** Both agents burning tokens loading full standards files.
Read Discipline added as quick fix — monitor before building section-splitting.
**Subtasks:**
- [ ] Monitor agent sessions for 1 week — note any file re-reads
- [ ] Decide: is section-splitting needed after monitoring?
- [ ] If yes — design section file structure for BACKEND standards
- [ ] If yes — design section file structure for FRONTEND standards
- [ ] Update context-loader.md with section-aware attach logic
- [ ] Test with Codex and Gemini — verify token reduction

---

### [TASK-042] Input Label Accessibility Fix
**Status:** Closed - 2026-03-07
**Priority:** P0 — Blocking (regressions introduced in TASK-040)
**Scope:** Frontend
**Blocked by:** Nothing
**Why:** Three components from the TASK-040 decomposition sprint have `<label>` elements
  not programmatically associated with their controls. Screen readers will not announce
  field labels on focus. Direct accessibility regression introduced by the sprint.
**Findings addressed:** NEW-03, NEW-04, NEW-05
**Files:**
- `frontend/components/inputs/ExtraInputText.tsx`
- `frontend/components/inputs/ExtraInputSelect.tsx`
- `frontend/components/inputs/ExtraInputCombobox.tsx`
**Subtasks:**
- [ ] Add `useId()` + `id` on `<textarea>`/`<input>` + `htmlFor` in ExtraInputText.tsx
- [ ] Add `useId()` + `id` on `<select>` + `htmlFor` in ExtraInputSelect.tsx
- [ ] Add `useId()` for filter input + `htmlFor` on `<label>` in ExtraInputCombobox.tsx
- [ ] Verify no `htmlFor` targets a non-existent `id`
- [ ] Bouncer pass

---

### [TASK-043] FunctionRenderer Type Migration
**Status:** Closed - 2026-03-07
**Priority:** P1 — Immediate (unblocked TODO from TASK-038, not executed)
**Scope:** Frontend
**Blocked by:** Nothing
**Why:** `FunctionRenderer.tsx:38–41` defines `isJsonRecordArray()` locally with a
  `// TODO TASK-038: move to lib/types.ts` comment. TASK-038 is complete. The unblock
  condition has passed. Function belongs in `lib/types.ts` alongside all other narrowing utilities.
**Findings addressed:** NEW-08
**Files:**
- `frontend/lib/types.ts`
- `frontend/components/renderers/FunctionRenderer.tsx`
**Subtasks:**
- [ ] Add `isJsonRecordArray` to `lib/types.ts` as exported function after `isJsonRecord`
- [ ] Add `@schema` JSDoc comment consistent with existing pattern
- [ ] In FunctionRenderer.tsx replace local definition with import from `@/lib/types`
- [ ] Remove the `// TODO TASK-038` comment
- [ ] Bouncer pass

---

### [TASK-044] CategoryScreen Structural Remediation
**Status:** Closed - 2026-03-07
**Priority:** P2 — Scheduled
**Scope:** Frontend
**Blocked by:** Nothing
**Why:** CategoryScreen.tsx has four distinct violations to fix in one pass to avoid
  partial states: 497 lines (limit 300), domain logic in component, inline as casts,
  and raw rgba() literals.
**Findings addressed:** NEW-01, NEW-06, A4, A5, A6 (CategoryScreen casts), B1
**Files:**
- `frontend/components/layout/CategoryScreen.tsx`
- `frontend/lib/executeHelpers.ts` (new file)
- `frontend/app/globals.css` (if tokens missing)
**Subtasks:**
- [ ] Create `frontend/lib/executeHelpers.ts` — move pure helpers out of CategoryScreen:
      `parsePositiveInteger`, `resolveSquadBuilderConfig`, `getExtraInputFields`,
      `getMissingContext`, `buildExecuteParams`, `formatExecuteError`
- [ ] Replace inline `as` casts at lines 49, 66, 81 with narrowing checks using `isRecord`
- [ ] Replace four `rgba()` literals (lines 349, 398, 411, 451) with CSS token equivalents
- [ ] Verify tokens exist in globals.css — add semantic tokens if missing
- [ ] Verify CategoryScreen.tsx is under 300 lines after extraction
- [ ] Bouncer pass

---

### [TASK-045] Mechanical Cleanup Pass
**Status:** Closed - 2026-03-07
**Priority:** P2 — Scheduled (can run alongside TASK-044 — no shared files)
**Scope:** Frontend
**Blocked by:** Nothing
**Why:** Four small isolated violations — each a one-to-two line change in a known location.
**Findings addressed:** NEW-02, NEW-07, F09-V05, A6 (ContextBar cast), B5
**Files:**
- `frontend/components/common/CountUp.tsx`
- `frontend/app/page.tsx`
- `frontend/app/globals.css` (if StatCard tokens needed)
- `frontend/components/layout/CategoryScreen.tsx` (loading announcement only)
- `frontend/components/layout/ContextBar.tsx`
**Subtasks:**
- [ ] CountUp.tsx:82 — replace `[font-variant-numeric:tabular-nums]` with `font-numeric`
- [ ] Verify `font-numeric` exists in tailwind.config.js — add if missing
- [ ] page.tsx:203 (StatCard) — replace `[background:${color}15]` with a valid CSS token
      pattern (variant class map or explicit opacity token in globals.css)
- [ ] CategoryScreen.tsx:477 — add `aria-busy="true"` + `aria-label="Loading analysis..."`
      to loading container, or add `role="status"` to `<SkeletonLoader>`
- [ ] ContextBar.tsx:44 — remove inline `as` cast; extend `ContextField` type with
      optional `placeholder?: string` or use direct `Record<string, unknown>` narrowing
- [ ] Bouncer pass

---

### [TASK-039] Backend: pre-compute renderer fields
**Status:** Blocked
**Priority:** High
**Scope:** Backend
**Blocked by:** TASK-010 (predictor engine must complete first)
**Why:** Three renderers perform domain logic on payload data — violates Paradigm 5.
  Backend must pre-compute these values before frontend can be fixed.
**Items:**
- F07-V21: PhaseAnalysisCard — phase labels and threshold indicators
- F07-V26: PredictionCard — prediction range defaults and gauge boundaries
- F07-V30: PlayerProfileCard — field category classifications
**Subtasks:**
- [ ] Audit what PhaseAnalysisCard currently derives — define pre-computed schema fields
- [ ] Audit what PredictionCard derives — define pre-computed schema fields
- [ ] Audit what PlayerProfileCard derives — define pre-computed schema fields
- [ ] Update backend Pydantic schemas and engine return values accordingly
- [ ] Update corresponding frontend types in lib/types.ts
- [ ] Remove domain logic from the three renderer components
- [ ] Bouncer pass (backend gates 1–6)

---

## Execution Order

```
Frontend sprint 2 — COMPLETE 2026-03-07:
  TASK-042 — Input label accessibility        CLOSED
  TASK-043 — FunctionRenderer type migration  CLOSED
  TASK-044 — CategoryScreen remediation       CLOSED
  TASK-045 — Mechanical cleanup pass          CLOSED

Next (backend):
  TASK-010 — Predictor engine refactor        IN PROGRESS
  TASK-039 — Backend pre-compute renderer fields (unblocks after TASK-010)
  TASK-011 — Update TECHNICAL_AUDIT_REPORT.md (unblocks after TASK-010)
```

---

## ICEBOX
Future ideas — not scheduled. No subtasks. No commitment.

- Frontend compliance debt — 5 items in PROJECT_CONTEXT.md Section 7.1.
  Action after engine queue clears.
- Phase 12 planning — live layer / Numba AOT. NOT started.
  Do not action until architect gives explicit go-ahead.
- Format expansion — extend strategy loaders beyond ODI to T20I and other formats.
- match_pack/ expansion — add more report types as engine functions grow.
- Pre-commit hook audit — verify .githooks/pre-commit cannot be bypassed.
- Automate Gates 1–5 as runnable Python scripts — currently prompt-based skills
  relying on agent honesty. Automation makes them trustworthy and agent-independent.
  Reference: validators/boundary-sentinel, duckdb-lint-ops, manifest-contract-verifier,
  serialization-guard, paradigm-sentinel.

### [ICE-001] MCP Integration
**Status:** Icebox
**Why parked:** No actionable work until Phase 12 live layer is scoped.
Engine refactoring must complete first.
**Potential value:**
- Expose DuckDB data layer to agents via MCP server
- Wrap compliance bouncer as an invokable MCP tool
- Live match feed exposure in Phase 12 without custom connectors
**Revisit trigger:** Phase 12 scoping begins

### [ICE-002] Extract engine dispatcher from api/main.py
**Status:** Icebox
**Why parked:** Dispatch logic will change during TASK-010 engine refactoring.
Extracting before refactor means doing it twice.
**Revisit trigger:** TASK-010 complete

### [ICE-003] Extract error handler from api/main.py
**Status:** Icebox
**Why parked:** Low priority, not blocking anything.
**Revisit trigger:** TASK-018 and TASK-010 complete

### [ICE-004] Enhance context-loader to output correct guide skill path based on task type
**Status:** Icebox
**Why parked:** Guide skills just built — context-loader enhancement is a quality-of-life
improvement, not a blocker. TASK-010 takes priority.
**What it does:**
- Reads task type from SESSION_STATE.md Active Task section
- Outputs the correct guide skill path alongside the standards file attach list
**Revisit trigger:** After TASK-010 engine refactoring completes

### [TASK-046] Manifest-Gated Deferred Items
**Status:** Icebox — Blocked on manifest schema extensions
**Priority:** P3
**Scope:** Frontend
**Blocked by:** Manifest schema extensions (team selector slot, source registry slot,
  navigation config slot) — none currently available
**Why parked:** Five violations from AUDIT-F10 and the compliance review are genuinely
  blocked on manifest features that do not exist yet.
**Items:**
- F04-V03: `"dashboard"` hardcoded in page.tsx:52, 53, 75 — needs manifest navigation root config
- F06-V03: `"teams"`/`"venues"` source strings in ContextBar.tsx:36, 49 — needs manifest source registry
- F06-V05: `"dashboard"` key in Sidebar.tsx DASHBOARD_ITEM — needs manifest nav root entry
- F06-V08: QuickLinks link definitions — TODO already logged, blocked on manifest navigation config
- ExtraInputSelect/ExtraInputCombobox — hardcoded API path strings — needs manifest source registry
**Action required before unblocking:** Manifest must declare navigation root config,
  team source, and venue source identifiers.
**Revisit trigger:** Manifest schema extended with navigation and source registry slots

---

*End of BACKLOG.md — Last Updated 2026-03-07*
*For current session state, see docs/ai/SESSION_STATE.md*
*For permanent project knowledge, see docs/ai/PROJECT_CONTEXT.md*
