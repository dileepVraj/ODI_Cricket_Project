# BACKLOG.md
**Purpose:** Project planning board — all scheduled, in-review, and icebox tasks.
**Last Updated:** 2026-03-08
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
**Status:** Closed — 2026-03-07
**Priority:** Critical
**Scope:** Backend
**Blocked by:** Nothing
**Why:** Primary active work. Engine files in formats/
  need full Part 0 and Part 1 compliance verification
  and refactoring.
**Progress:**
  - [x] Team engine — COMPLIANT 2026-03-05
  - [x] Player engine — COMPLIANT 2026-03-06
        (audit: TASK-026, refactor: TASK-027, review: TASK-028)
  - [x] Predictor engine — COMPLIANT 2026-03-07
        (9 violations fixed: DAL air-gap, stateful constructor, Anti-Any, zero-literal, visual silence)
  - [x] Additional engines — match_pack.py is orchestration/facade, not Domain Core. N/A.
**Subtasks completed:**
  - [x] Audit predictor engine
  - [x] Refactor predictor engine (stateless pattern, all gates passed)
  - [x] Final bouncer pass — PASS 100% compliance across 22 files
  - [ ] Update TECHNICAL_AUDIT_REPORT.md on completion → deferred to TASK-011

---

### [TASK-011] Update TECHNICAL_AUDIT_REPORT.md
**Status:** Closed — 2026-03-08
**Priority:** Medium
**Scope:** Documentation
**Blocked by:** TASK-010 (completed 2026-03-07)
**Why:** Stale since 2026-02-27, predates Phase 11.3
  completion and engine refactoring.
**Subtasks:**
  - [x] Review current report sections
  - [x] Update phase status to reflect Phase 11.3 complete
  - [x] Update engine compliance status after TASK-010
  - [x] Increment version to v3.2.0
  - [x] Update audit date

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

### [TASK-039] Backend: pre-compute renderer fields
**Status:** Closed — 2026-03-07
**Priority:** High
**Scope:** Backend
**Blocked by:** TASK-010 (completed 2026-03-07)
**Why:** Three renderers perform domain logic on payload data — violates Paradigm 5.
**Audit findings (2026-03-07):**
- F07-V21: PhaseAnalysisCard — LOW. Backend already sends `scenario_rows`. Fallback is backward-compat only.
- F07-V26: PredictionCard — BLOCKED. `predict_score()` removed. No data flows through this card. Dead code until Phase 12.
- F07-V30: PlayerProfileCard — LOW. Backend sends structured `PlayerProfile` dataclass. Flat key matching is fallback only.
**Resolution:** No backend changes needed. Existing pre-computation already covers active items.
  PredictionCard fields deferred to Phase 12 `predict_score()` rebuild.

---

### [TASK-046] Manifest Schema Extensions
**Status:** Closed — 2026-03-08
**Priority:** Medium
**Scope:** Backend + Frontend
**Blocked by:** Nothing (design complete — see agent artifacts)
**Why:** Five frontend violations (F04-V03, F06-V03, F06-V05, F06-V08,
  ExtraInput hardcoded paths) are blocked because the manifest has no slots
  for navigation roots, source registries, or navigation config.
  This task designs and builds those slots, then updates all consumers.
**Design doc:** `TASK-046_manifest_extensions_design.md` (agent artifacts)
**Registered file note:** `api/schemas/manifest.py` modification required
  and approved per task scope.
**Subtasks (execute in order):**
  - [x] 046-A — Backend Pydantic schema extension (`api/schemas/manifest.py`)
        Add `SourceRegistryEntry`, `NavigationRoot`, `QuickLinkDesc` models.
        Add `source_params` to `ContextFieldDesc`.
        Add `quick_links` to `CategoryDesc`.
        Add `source_registry` and `navigation_root` to `ManifestResponse`.
        All new fields Optional — zero breakage.
  - [x] 046-B — Populate ODI manifest (`formats/odi/manifest.py`)
        Add `source_registry` dict (teams, venues, players, host_countries, regions).
        Add `navigation_root` (key=dashboard, label=Dashboard, icon=home).
        Change `context_fields[].source` from full API paths to semantic keys.
        Change `extra_inputs[].source` from full API paths to semantic keys + source_params.
        Add `quick_links` to selected categories.
  - [x] 046-C — Frontend type updates (`frontend/lib/api.ts`)
        Add `SourceRegistryEntry`, `NavigationRoot`, `QuickLink` TS interfaces.
        Extend `Manifest`, `ManifestCategory`, `ContextField` interfaces.
  - [x] 046-D — Frontend consumer updates (5 files updated)
        `page.tsx` — use `manifest.navigation_root?.key` instead of `"dashboard"`.
        `Sidebar.tsx` — derive DASHBOARD_ITEM from `manifest.navigation_root`.
        `ContextBar.tsx` — source checks now match semantic keys naturally (no change needed).
        `ExtraInputSelect.tsx` — resolve source via registry key.
        `ExtraInputCombobox.tsx` — resolve source via registry key + source_params.
        `QuickLinks.tsx` — rewritten for category_key hash navigation.
        `PlayerProfileCard.tsx` — reads quick_links from manifest category.
  - [x] 046-E — Validation and gates
        Gates 3, 4, 5, 6 — all PASS.
        Bouncer: PASS 100% compliance across 22 files, matches baseline.
        TypeScript: zero errors.
        5 of 6 violations resolved. F06-V08 deferred to follow-up.
        UPDATE 2026-03-08: F06-V08 resolved. All 6/6 violations closed.
**Note:** F06-V08 (QuickLinks) — RESOLVED 2026-03-08. QuickLinks.tsx rewritten for
  category_key hash navigation. PlayerProfileCard.tsx reads from manifest quick_links.

---

## Execution Order

```
Frontend sprint 2 — COMPLETE 2026-03-07 (removed from backlog):
  TASK-042 — Input label accessibility        CLOSED
  TASK-043 — FunctionRenderer type migration  CLOSED
  TASK-044 — CategoryScreen remediation       CLOSED
  TASK-045 — Mechanical cleanup pass          CLOSED
  Post-sprint compliance verification COMPLETE 2026-03-07
    (accent-blue → accent-primary fix in CategoryBanners.tsx)

Next:
  TASK-011 — Update TECHNICAL_AUDIT_REPORT.md     CLOSED 2026-03-08 (v3.1.0 → v3.2.0)
  TASK-046 — Manifest Schema Extensions            CLOSED 2026-03-08
    046-A: Backend Pydantic schema                 CLOSED
    046-B: Populate ODI manifest                   CLOSED
    046-C: Frontend type updates                   CLOSED
    046-D: Frontend consumer updates               CLOSED (all 6/6 violations resolved)
    046-E: Validation & gates                      CLOSED — all gates PASS
  TASK-012 — Token optimisation (needs 1 week monitoring first)
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

---

*End of BACKLOG.md — Last Updated 2026-03-08*
*For current session state, see docs/ai/SESSION_STATE.md*
*For permanent project knowledge, see docs/ai/PROJECT_CONTEXT.md*
