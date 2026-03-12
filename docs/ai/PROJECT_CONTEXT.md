# PROJECT_CONTEXT.md
**Purpose:** Claude Projects knowledge base — full project history, decisions, standards, and pending work.
**Last Updated:** 2026-03-12 (TASK-107 country H2H payload restructure)
**Project:** Cricket Algo-Trading Platform

---

## 1. PROJECT OVERVIEW

**What it is:** A cricket algorithmic trading/analysis platform. FastAPI backend + Next.js 14 frontend. The backend exposes a manifest-driven engine system where each cricket format (ODI, T20I, etc.) has a manifest defining available analysis functions, their required context, and output types.

**Stack:**
- Backend: Python, FastAPI, DuckDB, TypedDict-based type system
- Frontend: Next.js 14 (App Router), TypeScript, React Context for global state
- No Jupyter/Voila/ipywidgets — those are legacy and fully removed
- AI agents: Codex CLI, Gemini/Antigravity IDE, Claude CLI (planned)

**Project root:** `C:\Cricket_Project_Stable\`

**Key directories:**
```
core/                        — Domain core (calculators, engines, interfaces, services)
core/calculators/            — Pure calculation functions (Phase 11.3 complete)
core/interfaces/             — TypedDict contracts (team_types.py is load-bearing)
core/match_pack/             — Match report generator (interpreter.py + transformer.py)
                               Orchestrates engine functions to produce insightful
                               match reports for selected teams.
core/data_access.py          — DAL (highest-risk file, do not touch without trace)
core/team_engine.py          — Strategy loader: routes to formats/odi/engines/team_engine.py
core/predictor.py            — Strategy loader: routes to formats/odi/predictor.py
core/player_engine.py        — Strategy loader: routes to formats/odi player engine
core/exceptions.py           — Shared exception classes
core/data_loader.py          — Data feeding layer into engines
core/utils/compliance_bouncer.py — 10-rule compliance enforcer
core/gen_ai/skills/          — AI agent skill system
formats/                     — Per-format manifests and engines
api/                         — FastAPI routes, serializers, engine pool
frontend/                    — Next.js 14 app
frontend/app/page.tsx        — Main app shell (3-layer layout, hash navigation)
frontend/app/globals.css     — Design system v1.0 (CSS tokens, named classes)
frontend/lib/api.ts          — Centralized API client (all fetch calls go here)
frontend/lib/types.ts        — Core TypeScript interfaces (all @schema / @schema-exempt tags resolved)
frontend/lib/comparison-types.ts — Comparison-related types (split from types.ts — TASK-065)
frontend/lib/venue-types.ts  — Venue-related types (split from types.ts — TASK-065)
frontend/lib/context.tsx     — Global React Context (AppProvider, useAppContext)
frontend/components/renderers/FunctionRenderer.tsx — Universal output dispatcher
frontend/components/layout/  — Shell, navigation, bars (FormatSelector, ContextBar, Sidebar)
frontend/components/renderers/ — One file per output_type renderer
frontend/components/inputs/  — User input components (SquadBuilder, ExtraInputRenderer)
frontend/components/common/  — Shared primitives (EmptyState, badges, loaders)
docs/guides/                 — Engineering standards
docs/ai/                     — SESSION_STATE.md (AI_MEMORY.md deprecated)
```

### 1.1 Core Strategy Loaders

Three files at `core/` root act as strategy loaders — they resolve the correct
format-specific engine class at runtime via `format_registry.py` and `importlib`.
They are NOT legacy. Do not delete them.

| File | Routes to | Used by |
|------|-----------|---------|
| `core/team_engine.py` | `formats/odi/engines/team_engine.py` | `engine_pool.py`, `main.py`, `format_registry.py` |
| `core/predictor.py` | `formats/odi/predictor.py` | `engine_pool.py`, `main.py`, `format_registry.py` |
| `core/player_engine.py` | `formats/odi/` player engine | `scripts/debug/`, `tests/` |

**Current scope:** ODI only. Pattern will extend to other formats as they are added.

---

## 2. CURRENT PROJECT PHASE

Team engine signed off COMPLIANT 2026-03-05.
Player engine signed off COMPLIANT 2026-03-06.
Frontend compliance audit COMPLETE 2026-03-06 (TASK-029).
Predictor engine signed off COMPLIANT 2026-03-07 (TASK-010 CLOSED).
Frontend sprint 2 COMPLETE 2026-03-07 (TASK-042 through TASK-045).
Manifest schema extensions COMPLETE 2026-03-08 (TASK-046 — all 6/6 frontend violations resolved).
Frontend compliance sprint 2 COMPLETE 2026-03-09 (TASK-070 through TASK-072).
Gate F1 expanded to 15 rules. Pre-commit hook Gate 3 fixed (--manifest argument).
TASK_PROTOCOL.md Rules 5.11 and 5.12 added. pre-commit.ps1 removed.

---

## 3. ENGINEERING STANDARDS — CURRENT STATE

### 3.1 Standards File Structure

| File | Version | Scope |
|------|---------|-------|
| `docs/guides/ENGINEERING_STANDARDS_CORE.md` | v2.3 (2026-03-03) | Authoritative — human maintains, do not attach to agents |
| `docs/guides/ENGINEERING_STANDARDS_BACKEND.md` | v2.2 | Backend agent context file |
| `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md` | v2.2 | Frontend agent context file — fully expanded |

CORE is the authoritative source. BACKEND and FRONTEND are scoped agent files.
Never recommend attaching AI_MEMORY.md — it is deprecated.

### 3.2 Six Core Mandates

| # | Mandate | Scope |
|---|---------|-------|
| 1 | Functional Core, Imperative Shell | Universal |
| 2 | Hexagonal Purity | Universal |
| 3 | DOD (vectorisation, no iterrows/itertuples) | Universal |
| 4 | SRP | Universal |
| 5 | Event-Driven State (Live Bridge) | Backend only |
| 6 | WebSocket-First Communication | Backend only |

**Mandate 7 (Numba AOT) deliberately REMOVED** — Phase 12 not started.

### 3.3 Gate Sentinel Order

**Backend gates (GATE 1–6):**

| Gate | Skill | Trigger |
|------|-------|---------|
| GATE 1 | `validators/backend/boundary-sentinel` | Any modification to `core/` |
| GATE 2 | `guides/backend/duckdb-lint-ops` | Any modification to `calculators/`, `engines/`, `services/` |
| GATE 3 | `validators/backend/manifest-contract-verifier` | Any modification to `manifest.py` or engine files |
| GATE 4 | `validators/backend/serialization-guard` | Any modification to `api/serializers.py` or engine return types |
| GATE 5 | `validators/backend/paradigm-sentinel` | Always — after all primary gates pass |
| GATE 6 | `core/utils/compliance_bouncer.py` | Always — last step before every commit |

**Frontend gates (GATE F1–F3) — run for any frontend/ task:**

| Gate | Skill | Trigger | Current Status |
|------|-------|---------|----------------|
| GATE F1 | `validators/frontend/frontend-lint-sentinel` | Any modification to `frontend/` files | PASS — 0 violations |
| GATE F2 | `validators/frontend/frontend-paradigm-sentinel` | Always — after F1 passes | PASS — 0 violations |
| GATE F3 | `validators/frontend/frontend-type-sync-guard` | Always-on (not conditional) | PASS — 0 violations |

Dormant: `event-state-linter` — activates when `core/live/` is created in Phase 12.

**Pre-commit hook — fully wired as of TASK-069:**
Gates 1, 2-warning, 3, 4, F1, F2, F3, 5, 6 active.
Gate 3.5 dormant (Phase 12). Hook uses LF line endings, staged-file scoping per gate.

### 3.4 Compliance Bouncer — 10 Rules

| Rule | What it checks |
|------|----------------|
| ZERO_LITERAL | Hardcoded literals not declared in manifest registries |
| ANTI_ANY | `Any` or `object` in type signatures |
| MISSING_RETURN_TYPE | Missing return annotations |
| IO_AIR_GAP | File/OS I/O inside engine execute paths |
| PRESENTATION_PURITY | UI strings in service layer |
| DOD_VIOLATION | `.iterrows()` / `.itertuples()` |
| BOUNDARY_VIOLATION | Infrastructure imports in Domain Core |
| CONSTITUTIONAL_VISUAL_SILENCE | Visual tokens inside `core/` |
| CONSTITUTIONAL_TYPED_TRUTH | Deprecated/legacy imports in engines and calculators |
| CONSTITUTIONAL_ANTI_GREASE | `Dict[str, Any]` or `object` in signatures |

### 3.5 Skills Structure

```
core/gen_ai/skills/
    .system/           — skill-creator, skill-installer (DO NOT TOUCH)
    guides/
        backend/
            duckdb-lint-ops/       — Gate 2 guide + scripts/ (run_lint.py, query_duckdb.py)
                                     Script: core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py
            context-loader/        — bootstrap context loader
            bug-fix-guide/         — enforcing 4-phase backend bug-fix workflow
            new-feature-guide/     — enforcing 7-phase outside-in new-feature workflow
            refactor-guide/        — enforcing 6-phase refactor (behaviour-identical) workflow
            modification-guide/    — enforcing 5-phase deliberate-change workflow
        frontend/
            frontend-bug-fix-guide/       — 4-phase frontend RCA + F1–F3 gates
            frontend-modification-guide/   — delta discipline for UI changes + F1–F3 gates
            frontend-new-component-guide/  — component classification, placement, @schema contract
    validators/
        backend/       — boundary-sentinel, manifest-contract-verifier,
                         event-state-linter (dormant), serialization-guard,
                         executive-auditor, paradigm-sentinel
        frontend/      — frontend-lint-sentinel, frontend-paradigm-sentinel,
                         frontend-type-sync-guard
```

**IMPORTANT:** Gate 2 (duckdb-lint-ops) is in `guides/backend/` not `validators/`.
Gate 2 script path: `core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py`
All four backend guide skills have the explicit `run_lint.py` command — "per SKILL.md" removed.

**Gate F3 (frontend-type-sync-guard):** Always-on. Scans all `frontend/lib/*.ts` files.
Not limited to `lib/types.ts`. Trigger condition updated in all three frontend guide skills.

**@schema-exempt pattern introduced (2026-03-09):**
TypeScript interfaces that are frontend-only (no Pydantic equivalent) must carry:
`/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */`
Interfaces that map to a backend Pydantic schema must carry:
`/** @schema {PydanticClassName} in {python_file_path} */`
Both tags are accepted by Gate F3. Missing either tag is a Gate F3 violation.
Documented in: frontend-new-component-guide/SKILL.md Phase 3 check R4,
all three frontend guide skills Phase 3 Gate F3 trigger, Rule 5.8 in TASK_PROTOCOL.md.

### 3.6 High-Impact File Registry

| File | Risk |
|------|------|
| `core/data_access.py` | CRITICAL — corrupts all downstream outputs |
| `core/interfaces/team_types.py` | HIGH — silent type breakage across engines/services/serializers |
| `api/serializers.py` | HIGH — affects every API response |

Stop-state-trace-confirm required before any modification not explicitly stated in task prompt.

---

## 4. CONTEXT PIPELINE — 3-TIER SYSTEM

### 4.1 Tier Structure

**Tier 1 — Always attach (scoped agent file):**
- Backend tasks: `ENGINEERING_STANDARDS_BACKEND.md`
- Frontend tasks: `ENGINEERING_STANDARDS_FRONTEND.md`

**Tier 2 — Always attach:**
- `docs/ai/SESSION_STATE.md`

**Tier 3 — Architecture tasks only:**
- `docs/guides/TECHNICAL_AUDIT_REPORT.md`

Never attach `AI_MEMORY.md` — deprecated.

### 4.2 SESSION_STATE.md Template

```markdown
# Session State
**Last Updated:** [date]
**Current Phase:** [phase status]

## Current Priority Queue
1. [highest priority]
2. [next]

## In Progress
- [actively half-done work]

## Last Completed
- [most recent completions]

## Known Blockers
- [anything blocking progress]

## Active Task
Scope: [Backend | Frontend | AI Tooling]
Files likely touched: [list]
Attach: [standards file]

## Do Not Touch (Active)
Full registry in ENGINEERING_STANDARDS_CORE.md Part 6.
Short list: core/data_access.py, core/interfaces/team_types.py, api/serializers.py
```

### 4.3 Context-Loader Skill

Path: `core/gen_ai/skills/guides/context-loader/`
Status: **BUILT** — committed 2026-03-03
Pending enhancement: ICE-004 — output correct guide skill path based on task type

What it does:
1. Reads `SESSION_STATE.md`, extracts Active Task scope
2. Based on scope, outputs the correct ordered file attach list
3. Injects phase-awareness block into agent context
4. Warns if SESSION_STATE.md is stale (>7 days)
5. Confirms context loaded and agent is ready to proceed

**How it triggers:** Invoked as Step 1 in every agent task prompt, OR wired into
the agent config file (AGENTS.md / GEMINI.md / CLAUDE.md) so it fires automatically
at session start.

**Next step:** Wire bootstrap block into AGENTS.md and GEMINI.md (Priority 2).

### 4.4 Task Protocol — Authoritative Agent Routing Guide

Path: `docs/ai/TASK_PROTOCOL.md`
Status: **CREATED** — 2026-03-09

This file supersedes all ad-hoc task routing guidance. Any AI agent starting a task
MUST read `TASK_PROTOCOL.md` before touching any file.

What it contains:
- Section 1: Task classification table (10 task types)
- Section 2: Guide skill load order per task type (backend, frontend, tooling)
- Section 3: Gate sequence by scope (explicit script commands, not "per SKILL.md")
- Section 4: Mixed-scope rules (new-feature, full-stack modifications)
- Section 5: Hard rules (apply to every task, every type)
- Section 6: Quick reference card (cut-to for fast answers)
- Section 7: Skill registry (all paths, authoritative — single source of truth)

**Rule 5.9 in TASK_PROTOCOL.md:** duckdb-lint-ops script path is
`core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py`
The legacy path `core/gen_ai/skills/duckdb-lint-ops/scripts/` does not exist.

**Rule 5.8 in TASK_PROTOCOL.md:** @schema and @schema-exempt contract for
new TypeScript interfaces in `frontend/lib/*.ts` — both patterns documented.

---

## 5. AGENT CONFIG FILES — CURRENT STATE

Three agent config files govern AI agent behaviour at the project root.

| File | Tool | Status |
|------|------|--------|
| `AGENTS.md` | Codex CLI | v2.0 — refactored 2026-03-03 |
| `GEMINI.md` | Gemini / Antigravity IDE | v2.0 — refactored 2026-03-03 |
| `CLAUDE.md` | Claude CLI | Not yet created — pending Claude pro enrolment |

### 5.1 Shared Structure (all three files)

```
Part 1 — Mandatory Bootstrap
Part 2 — Architectural Laws
Part 3 — Six-Gate Sentinel Sequence
Part 4 — High-Impact File Registry
Part 5 — Coding Standards (includes Filesystem Integrity Rules)
Part 6 — [GEMINI ONLY] Scope Boundaries
Part 6/7 — Definition of Done
Part 7/8 — Report Format
Part 8/9 — Hard Prohibitions
```

### 5.2 AI Agent Filesystem Integrity Rules

Added 2026-03-03 following a Codex incident where `core/` contents were deleted during a worktree task.

Rules are documented in `AGENTS.md Part 5` and `GEMINI.md Part 5`. Both files are the source of truth for agent constraints.

**Summary of enforced rules:**
- No file deletion/move/rename unless explicitly listed in the task prompt
- Banned commands: `git clean`, `git reset --hard`, `git rm`, `git checkout -- .`
- Missing reference file = hard stop with `CRITICAL BLOCKER` output
- No recursive filesystem scans
- `git status` required before and after every file operation
- Unexpected deletions = immediate halt + `CRITICAL DEVIATION` report

### 5.3 Key Decisions in Agent Config Files

- Phase state is NOT hardcoded — SESSION_STATE.md is sole source
- `AI_MEMORY.md` explicitly deprecated and prohibited in all files
- Gate 2 path (`guides/duckdb-lint-ops`) called out in gate table AND hard prohibitions
- GEMINI.md has extra scope boundaries section
- `CLAUDE.md` will copy from `AGENTS.md` when Claude CLI is added

### 5.4 What Was Wrong in Previous Versions (v1.0)

| Issue | Old behaviour | Fixed in v2.0 |
|-------|--------------|---------------|
| `AI_MEMORY.md` treated as live | Agents read and updated a deprecated file | Explicitly deprecated, prohibited |
| Wrong standards file path | Pointed to monolithic `ENGINEERING_STANDARDS.md` | Points to scoped BACKEND/FRONTEND files |
| `AI_ARCHITECTURAL_MANIFESTO.md` referenced | File does not exist | Removed |
| No gate sequence | 5 skills listed with no order or trigger conditions | Full 6-gate sequence with paths and triggers |
| No High-Impact File Registry | Agents could freely touch protected files | Registry and stop-state-confirm rule added |
| Phase-blind | No phase awareness | SESSION_STATE.md bootstrap covers this |
| Emoji noise | Decorative headers wasting tokens | All emoji removed |
| Two diverging files | AGENTS.md and GEMINI.md had different content | Shared core, diverge only on Gemini scope section |
| No filesystem integrity rules | Codex deleted core/ contents during worktree task | Filesystem Integrity Rules added to Part 5 |

---

## 6. FRONTEND CODEBASE — PATTERNS

### 6.1 lib/api.ts — Key Patterns

- All components call centralised wrappers — never raw `fetch()`
- Custom `ApiClientError` class with `status`, `code`, `details`, `toUserMessage()`
- Single `requestJson<T>()` wraps all fetch calls
- Base URL: empty string (same-origin, proxied by Next.js rewrites)
- Key endpoints: `/api/v1/formats`, `/api/v1/{format}/manifest`, `/api/v1/{format}/execute/{functionKey}`
- Key types: `FormatInfo`, `Manifest`, `ManifestFunction`, `ExecuteResponse`, `ApiClientError`
- Manifest-driven types (TASK-046): `SourceRegistryEntry`, `NavigationRoot`, `QuickLink`
- `ContextField` extended with `source_params` for parameterised source resolution
- `ManifestCategory` extended with `quick_links` for category-level navigation
- `Manifest` extended with `source_registry` and `navigation_root`
- All source fields use semantic keys (e.g., `"teams"`, `"venues"`) not API paths

### 6.2 lib/context.tsx — Key Patterns

- Single `AppProvider` wrapping entire app — no prop drilling
- `ContextValues`: `{ venue, team_a, team_b, years, region, [key: string]: string | number }`
- Cancellation pattern: `let cancelled = false` with cleanup in all async effects
- URL bidirectional sync via `window.history.replaceState` — back-stack not polluted
- Format switching clears contextValues to defaults
- `years` default from `manifest.context_fields.years.default` (fallback: 5)

### 6.3 page.tsx — Key Patterns

- 3-layer layout: FormatSelector (top) → ContextBar → Sidebar + Main
- Hash-based deep-linking: `/#category_key` syncs to active category state
- `AppShell` composes layout — `DashboardScreen` and `CategoryScreen` are content renderers
- Navigation root derived from `manifest.navigation_root?.key` — never hardcoded (TASK-046)
- `CategoryScreen` manages: activeTab, result, isLoading, error, homeXI, awayXI, extraInputValues
- Execute params built via `buildExecuteParams()` — never inline in event handlers
- Error formatted via `formatExecuteError()` — never raw `err.message`
- Squad builder and extra inputs rendered only when manifest declares them

### 6.4 FunctionRenderer.tsx — Key Patterns

- Single entry point for all function output rendering
- Switch dispatch on `output_type` → dedicated renderer component
- `extractEnrichedData()` detects API enrichment shape `{ stats, match_audit }`
- `MatchAuditSection` rendered as sibling — never embedded inside renderers
- Fallback auto-detection for unknown output types — safety net only
- `EmptyState` from `components/common/` for null/undefined data
- Current output_types: `report`, `comparison_table`, `matrix_table`, `form_table`,
  `table`, `phase_analysis`, `venue_matchup_report`, `prediction_card`,
  `profile_card`, `matchup_table`, `download_json`

### 6.5 globals.css — Design System v1.0

**CSS Token Groups:**
- `--bg-*` — background layers (deepest → elevated)
- `--accent-*` — Electric Blue, Purple, Cyan palette
- `--tier-*` — 4-tier semantic: elite (green), strong (teal), caution (amber), danger (red)
- `--text-*` — text hierarchy (primary → disabled)
- `--border-*` — border variants (subtle → accent)
- `--glass-*` — glassmorphism (bg, border, blur)
- `--shadow-*` — shadow scale (sm → glow)
- `--radius-*` — border radius (sm → xl)
- `--transition-*` — timing (fast/normal/slow)
- `--sidebar-width`, `--topbar-height`, `--context-bar-height` — layout dimensions

**Named Utility Classes:**
`glass-card`, `glass-card-hover`, `gradient-text`, `gradient-text-purple`,
`btn-primary`, `btn-ghost`, `badge`, `badge-elite`, `badge-strong`,
`badge-caution`, `badge-danger`, `format-tab`, `sidebar-item`,
`sidebar-group-label`, `context-input`, `fn-count`, `skeleton`,
`animate-fade-in`, `animate-slide-in`, `animate-spin`, `animate-pulse-glow`

**Font System:**
- Body/UI: `var(--font-text)` — Cascadia Code monospace
- Numeric/stats: `var(--font-numeric)` — Segoe UI with tabular-nums

---

## 7. FRONTEND ENGINEERING STANDARDS — CURRENT STATE

`ENGINEERING_STANDARDS_FRONTEND.md` is fully expanded as of 2026-03-03.

| Section | Rules | Coverage |
|---------|-------|----------|
| 2.2A — Architectural Rules | 15 | Boundary enforcement, manifest contract, state discipline, error handling, navigation, async cancellation, parameter construction, format agnosticism, no polling |
| 2.2B — UI Implementation Standards | 10 | CSS tokens, named classes, badge semantics, icon library, font system, animation, renderer pattern, empty states, layout pattern, directory contract |
| 2.2C — Performance Standards | 3 | Lazy loading renderers, memoisation discipline, no inline object/array props |
| 2.2D — Resilience Standards | 3 | Error boundary isolation, error boundary placement, backend type sync contract |
| 2.2E — Accessibility Standards | 3 | Interactive element labels, keyboard navigation, loading/error announcements |
| 2.2F — Testing Standards | 4 | Vitest + RTL stack, what to test, what not to test, no hardcoded format keys |

**Total: 38 frontend rules. All grounded in actual codebase patterns.**

### 7.1 Frontend Compliance Debt — Post TASK-029 Audit

Full violation register: docs/audits/frontend/AUDIT-F10-violation-summary.md

Statistics:
  Total violations: 90
  HIGH: 24 | MEDIUM: 54 | LOW: 12
  Pre-existing confirmed: 8
  New violations found: 82

Systemic patterns (require single fix strategy across multiple files):
  - Empty state: 12/13 renderers use inline fallback instead of EmptyState
  - Inline as casts: FunctionRenderer + 9 renderers
  - Font system: 7 renderers use font-variant-numeric not font-numeric
  - Raw colours outside CSS token system: 7 files
  - Mouse-only comboboxes: ContextBar, SquadBuilder, ExtraInputRenderer
  - Hardcoded domain taxonomy: PARTIALLY RESOLVED (TASK-046 fixed 6/6 violations —
    page.tsx, ContextBar, Sidebar, QuickLinks, ExtraInputSelect, ExtraInputCombobox
    now all manifest-driven)
  - Missing role="alert": page.tsx, SquadBuilder
  - Missing loading state announcements: page.tsx, SkeletonLoader

Tier 1 blockers (must be created first):
  - ErrorBoundary component in components/common/ — unblocks F04-V05, F05-V04, F09-V01
  - Shared accessible combobox primitive — unblocks F06-V04, F08-V05, F08-V10

Architect exceptions recommended:
  - CountUp.tsx animation — KIP candidate, no CSS keyframe equivalent for JS counter

Standards doc updates recommended:
  - ENGINEERING_STANDARDS_FRONTEND.md 2.2B Rule 1 — token names out of sync with globals.css
    (--bg-base vs --bg-deep, --accent-primary vs --accent-blue)

Backend pre-computation required before frontend fix possible:
  - F07-V21: PhaseAnalysisCard — labels/thresholds must be pre-computed
  - F07-V26: PredictionCard — prediction ranges/gauge defaults must be pre-computed
  - F07-V30: PlayerProfileCard — field classifications must be pre-computed
  Flag for TASK-030 planning.

Resolved by TASK-046 (2026-03-08):
  - F04-V03: page.tsx hardcoded "dashboard" — RESOLVED (manifest.navigation_root)
  - F06-V03: ContextBar hardcoded source keys — RESOLVED (semantic keys match naturally)
  - F06-V05: Sidebar hardcoded DASHBOARD_ITEM — RESOLVED (derived from manifest)
  - F06-V08: QuickLinks hardcoded link definitions — RESOLVED (manifest quick_links)
  - ExtraInputSelect hardcoded API path matching — RESOLVED (semantic key comparison)
  - ExtraInputCombobox hardcoded API path parsing — RESOLVED (source_params)

---

## 8. PENDING WORK — EXECUTION PLAN

In priority order:

1. **Frontend remediation sprint** — TASK-030 (not yet created)
   Scope: 90 violations from TASK-029 audit (6 resolved by TASK-046, ~84 remaining)
   Start with Tier 1 blockers (ErrorBoundary, accessible combobox)
   Full scope in docs/audits/frontend/AUDIT-F10-violation-summary.md
2. **Update TECHNICAL_AUDIT_REPORT.md** — TASK-011 (UNBLOCKED)
3. **Token optimisation** — section-aware context loading (TASK-012) — monitor first
4. **Frontend compliance debt** — remaining items, after engine queue clears
5. **MCP Integration** — ICEBOX, revisit when Phase 12 scoping begins


---

## 9. IMPORTANT CONVENTIONS

- **Never attach AI_MEMORY.md to agents** — deprecated, noise
- **Bouncer must pass before every commit** — `python core/utils/compliance_bouncer.py --root .`
- **Pre-commit hook enforces compliance** — `.githooks/pre-commit` — Gates 1, 2 (script + exit 1), 3, 4, F1, F2, F3, 5, 6 wired (TASK-069/guide sprint). Gate 3.5 dormant (Phase 12).
- **No `--no-verify` commits** — bouncer is not optional
- **High-impact files require stop-state-trace-confirm** — Section 3.6
- **Engine refactoring is the active work** — Phase 12 NOT started
- **duckdb-lint-ops is in `guides/backend/`** not `validators/` — script path: `core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py`
- **Gate F3 is always-on** — scans all `frontend/lib/*.ts`, not just `types.ts`
- **@schema-exempt is a valid Gate F3 tag** — frontend-only interfaces must carry it
- **TASK_PROTOCOL.md is the agent routing guide** — any agent starting a task MUST read `docs/ai/TASK_PROTOCOL.md` first
- **Agent report format** — keep under 30 lines, use strict template
- **Phase state lives in SESSION_STATE.md only** — never hardcode phase in agent config files
- **Agent config files share a common structure** — diverge only where tool-specific behaviour requires it
- **core/ strategy loaders are active files** — team_engine.py, predictor.py, player_engine.py
  are NOT legacy. Do not delete them.
- **match_pack/ is a legitimate feature** — report generator, not clutter
- **Codex worktree can delete files** — always run `git status` after Codex tasks,
  restore with `git restore core/` if deletions appear

**Gate State Snapshot (2026-03-09):**
| Gate | Status |
|------|--------|
| Gate 1 — boundary-sentinel | Operational |
| Gate 2 — duckdb-lint-ops | Operational (script + exit 1 in pre-commit hook) |
| Gate 3 — manifest-contract-verifier | Operational |
| Gate 4 — serialization-guard | Operational |
| Gate F1 — frontend-lint-sentinel | PASS — 0 violations |
| Gate F2 — frontend-paradigm-sentinel | PASS — 0 violations |
| Gate F3 — frontend-type-sync-guard | PASS — 0 violations (always-on) |
| Gate 5 — paradigm-sentinel | Operational |
| Gate 6 — compliance-bouncer | PASS — 22 files, 100% compliance |
| Pre-commit hook | Fully wired, exit 0 confirmed |

---

## 10. KEY ARCHITECTURAL DECISIONS (HISTORY)

| Decision | Outcome | Rationale |
|----------|---------|-----------|
| TASK-107 closed | `calculate_country_h2h_payload()` now returns a structured `VenueMatchupReport`-compatible payload built directly from `clean_df`, without changing `_comparison_rows()` or `core/services/report_builder.py` | The flat `rows` path hid the structured stats this report needed; extracting the builder in `matchup_calculator.py` surfaces summary, team splits, venue averages, and MATCH_IDS while keeping the upstream builder untouched | 2026-03-12 |
| Remove Mandate 7 (Numba AOT) | Removed from v2.2 | Premature — agents kept pushing Phase 12 |
| Do-Not-Touch Registry → High-Impact Registry | 3 files, stop-trace-confirm rule | Active refactoring needs engines/manifest/calculators accessible |
| `executive-auditor` kept but not in gate sequence | Redundant with paradigm-sentinel | paradigm-sentinel does everything executive-auditor does, plus more |
| `duckdb-lint-ops` stays in `guides/` | Dual classification | Guides DuckDB usage AND validates DOD compliance |
| AI_MEMORY.md → deprecate | Replaced with SESSION_STATE.md | Memory file became git-log noise |
| Standards split CORE/BACKEND/FRONTEND | Reduces context load per agent | Frontend agent does not need WebSocket-first mandate |
| Venue Matchup frontend display merge | TASK-098 complete 2026-03-11 | Tightened team-card geometry and merged innings scores into batting columns without backend payload changes |
| TASK-099 closed | Match Audit team-name spans now reuse the existing heading outline, audit columns were compacted to fit the viewport, and status pills render compact display labels | Fixes jersey-colour contrast and horizontal scroll without changing backend payloads or renderer ownership | 2026-03-11 |
| TASK-100A closed | Home Fortress now has a typed structured payload path (`HomeFortressReport`) alongside the legacy flat comparison rows, with a separate manifest function keyed to `home_fortress` | Preserves the existing fortress table while exposing venue averages, split metrics, and team-colour context for structured consumers | 2026-03-11 |
| TASK-100B closed | Added `FortressReport.tsx` and registered the `home_fortress` dispatch in `FunctionRenderer.tsx`, reusing the Venue Matchup glass cards, stat badges, footer averages, and low-sample warning pattern | Keeps the structured fortress UI additive to the existing table path while preserving token-only styling, lazy loading, and match-audit ownership in the dispatcher | 2026-03-11 |
| TASK-101 closed | `analyze_home_fortress_structured()` no longer accepts `opp_team`, hardcodes `"All"` internally, and the manifest now exposes a single `home_fortress` entry pointing at the structured engine method | Removes the runtime missing-argument failure and eliminates the duplicate Fortress Report tabs introduced by the parallel legacy/structured entries | 2026-03-11 |
| TASK-104 closed | Home Fortress structured payload now exposes a `team_colors` map for all unique audit-table teams, and FortressReport injects CSS vars for those entries at render time | Restores jersey-colour resolution for Match Audit team names in Fortress Report without adding frontend colour logic or changing serializer ownership | 2026-03-11 |
| URL bidirectional sync in context | `window.history.replaceState` only | Back-stack pollution from slider drags would break UX |
| CORE updated to v2.3 | Part 2.2 and Part 5.4 rewritten | Frontend rules expanded to 38, 3-tier pipeline formalised |
| Frontend rules expanded 6 → 38 | 2.2A through 2.2F | Grounded in page.tsx, globals.css, FunctionRenderer.tsx, FormatSelector.tsx |
| AGENTS.md + GEMINI.md refactored to v2.0 | Both files rewritten from scratch | v1.0 was stale — wrong standards path, AI_MEMORY.md treated as live, no gate sequence, no High-Impact Registry, emoji noise |
| Phase state removed from agent config files | SESSION_STATE.md is sole source | Hardcoding phase in config files creates drift when phase changes |
| Shared agent config structure adopted | AGENTS.md / GEMINI.md / CLAUDE.md share Parts 1–5 and 7–9 | Single maintenance point for shared rules — diverge only on tool-specific sections |
| Context-loader trigger mechanism clarified | Fires via Step 1 in task prompt OR via agent config file bootstrap | No automatic runtime hook exists — enforcement is prompt-discipline or config-file wiring |
| CLAUDE.md deferred | Not yet created | Pending Claude CLI pro sub activation — copy from AGENTS.md when ready |
| context-loader skill built | `core/gen_ai/skills/guides/context-loader/` | SKILL.md + context-loader.md committed 2026-03-03 |
| Filesystem Integrity Rules added to agent config | Part 5 addition pending AGENTS.md + GEMINI.md | Codex deleted core/ during worktree task — hard stops prevent repeat |
| core/ strategy loaders documented | team_engine.py, predictor.py, player_engine.py in Section 1.1 | Were undocumented — agents treated them as clutter candidates |
| match_pack/ documented | Section 1 key directories | Undocumented feature — invisible to agents |
| backtester.py + base_engine.py removed | Confirmed dead scaffolding | No imports found anywhere, print("Skeleton Initialized") confirmed placeholder status |
| context-loader skill built and verified | TASK-007 COMPLETE 2026-03-03 | 
SKILL.md + context-loader.md — all spec items passed human review |
| TASK-008 closed | Filesystem Integrity Rules committed to AGENTS.md + GEMINI.md Part 5 | 2026-03-04 |
| TASK-009 closed | backtester.py + base_engine.py confirmed never git-tracked, already absent | 2026-03-04 |
| BACKLOG.md Status field adopted | All tasks now carry Status: Open / In Progress / Blocked / Closed — YYYY-MM-DD | 2026-03-04 |
| MCP Integration icebox'd | ICE-001 created — revisit at Phase 12 scoping | 2026-03-04 |
| AGENTS.md + GEMINI.md Part 5 consolidated | Single unified filesystem rules block | Two overlapping duplicate blocks removed — Rules 1–7 replacing old prose+bullet format |
| docs/ai/ declared human-write-only | Rule 5 in Part 5 | Codex modified SESSION_STATE.md outside task scope on 2026-03-04 |
| git status --short . banned | Rule 3 in Part 5 + Part 8 prohibition | Codex repeatedly ran root-scoped git status causing noise and audit drift |
| Report format hardened | Part 7 + Part 8 prohibition | TASK-017 Codex submitted prose summary instead of required template |
| compliance-bouncer.py renamed | compliance_bouncer.py — snake_case | Module Naming standard (Engineering Standard 8) — hyphens break Python imports |
| python-dotenv introduced | config/settings.py — all hardcoded config moved to .env | TASK-015 — environment-specific literals removed from source |
| api/ layer extracted | context_builder.py + lifespan.py split from main.py | TASK-017 + TASK-018 — single responsibility principle applied to api/main.py |
| requirements.txt + pyproject.toml aligned | 13 mismatches resolved, python-dotenv added | TASK-016 — single source of truth for dependencies |
| ipywidgets removed | Not a project dependency — Jupyter legacy | Removed from requirements.txt and pyproject.toml |
| TASK-014 through TASK-019 closed | Pre-engine housekeeping complete | Path clear for TASK-010 engine refactoring |
| bug-fix-guide SKILL.md built | TASK-020 COMPLETE 2026-03-04 | Enforcing guide skill — 4 phases, 7 pre-condition checkpoints, single-file discipline, incremental gating, PART 0 mandate enforcement, hard stops, escalation reporting |
| new-feature-guide SKILL.md built | TASK-021 COMPLETE 2026-03-04 | Enforcing guide — 7 phases, outside-in sequence, contract confirmation hard stop, Truth Bridge, UI mandates, 15 hard stop triggers |
| refactor-guide SKILL.md built | TASK-022 COMPLETE 2026-03-04 | Enforcing guide — 6 phases, 9 pre-condition checkpoints, layer reclassification hard stop, no-behaviour-change constraint, parity verification phase, deletion zero-reference rule, 17 hard stop triggers |
| modification-guide SKILL.md built | TASK-023 COMPLETE 2026-03-04 | Enforcing guide — 5 phases, 10 pre-condition checkpoints, delta scoping, entrenchment rule, Golden Master regeneration, downstream verification, 17 hard stop triggers |
| Task-type guide skill system agreed and built | 2026-03-04 | Four enforcing guides: bug-fix, new-feature, refactor, modification. Enforcing not instructional. Single-file discipline. Incremental gating. PART 0 mandatory. ICE-004 for context-loader enhancement. |
| Player engine audit series introduced | docs/audits/player_engine/ AUDIT-P01 to P10 | 10-step methodology — more granular than team engine 5-step |
| ARCH-DEC-01 signed off | Group A dual-path standardised — get_last_match_xi, get_player_profile | Constructor-data primary, injection is enrichment — document in ABC |
| ARCH-DEC-02 signed off | Group B dead paths removed — analyze_squad_types, get_matchups, get_squad_comparison_data | All 19 caller files verified safe — context_df made required |
| ABC stale — player engine ahead | player_interface.py has 8 fixes required | TASK-027f — update ABC to match engine, not reverse |
| TASK-026 complete | Player engine audit series — 62 violations, 0 bouncer violations throughout | 2026-03-05 |
| ARCH-DEC-03 signed off | Rounding precision + innings threshold split | stat_precision_avg=0, stat_precision_rate=1, min_innings_career/context/form replacing min_innings_threshold | 2026-03-06 |
| TASK-027 complete | Player engine refactor series — 62 violations resolved across 027a–027f | player_engine.py, player_interface.py, manifest.py — all compliant | 2026-03-06 |
| TASK-028 complete | Architect review — player engine signed off COMPLIANT | 62/62 violations confirmed resolved, ARCH-DEC-01/02/03 verified | 2026-03-06 |
| TASK-010 progress | Player engine now COMPLIANT | Two of N engines done — predictor engine next | 2026-03-06 |
| team_interface.py cleaned | Removed unused VenueStats and TeamMatchup dataclasses | Confirmed zero usages via grep before removal | 2026-03-06 |
| ARCH-DEC-01 signed off | Group A dual-path standardised — get_last_match_xi, get_player_profile | Constructor-data primary, injection is enrichment — documented in ABC |
| ARCH-DEC-02 signed off | Group B dead paths removed — analyze_squad_types, get_matchups, get_squad_comparison_data | All 19 caller files verified safe — context_df made required |
| ARCH-DEC-03 signed off | Rounding precision + innings threshold split | stat_precision_avg=0, stat_precision_rate=1, min_innings_career/context/form |
| TASK-026 complete | Player engine audit series — 62 violations, 0 bouncer violations throughout | 2026-03-05 |
| TASK-027 complete | Player engine refactor — all 62 violations resolved, 027a through 027f | 2026-03-06 |
| TASK-028 complete | Architect review — player engine COMPLIANT, 62/62 confirmed | 2026-03-06 |
| TASK-010 progress | Player engine COMPLIANT — predictor engine is next | 2026-03-06 |
| TASK-029 complete | Frontend compliance audit — 90 violations found across 27 files | 2026-03-06 |
| Frontend compliance debt documented | Full register in AUDIT-F10-violation-summary.md — 82 new, 8 pre-existing | 2026-03-06 |
| CountUp KIP candidate | Bespoke requestAnimationFrame loop — no CSS keyframe equivalent — recommend KIP not rewrite | 2026-03-06 |
| Token naming drift identified | globals.css uses --bg-base/--accent-primary not --bg-deep/--accent-blue as per standards doc — standards doc needs update not codebase | 2026-03-06 |
| 3 backend pre-computation items | PredictionCard, PhaseAnalysisCard, PlayerProfileCard renderers require backend changes before frontend fix — flag for TASK-030 | 2026-03-06 |


```

Also update the skills registry in PROJECT_CONTEXT.md Section 3.5 and ENGINEERING_STANDARDS_CORE.md to reflect all four new guides:
```
core/gen_ai/skills/
    guides/
        duckdb-lint-ops/
        context-loader/
        bug-fix-guide/        ← NEW
        new-feature-guide/    ← NEW
        refactor-guide/       ← NEW
        modification-guide/   ← NEW
```

| Phase 10 named | Engine Layer Refactoring | Formalised 2026-03-05 — team engine first |
| ABC stale — engine is source of truth | team_interface.py updated to match engine | TASK-024 — 11 HIGH violations resolved |
| Stale dataclasses removed | 5 removed from team_interface.py | TASK-024 + TASK-024b — zero-reference confirmed |
| KIP-001 documented | Constructor discard pattern intentional | Stateless engine design — do not fix |
| KIP-002 documented | _context_match_df defined in lower file section | File layout choice — not missing method |
| Known Intentional Patterns registry | ENGINEERING_STANDARDS_BACKEND.md Part 7 | Protects intentional patterns from agent tampering |
| Audit series introduced | docs/audits/team_engine/ — AUDIT-01 to 05 | Structured compliance audit methodology for Phase 10 |
| TASK-029 initiated | Frontend compliance audit series — F01–F10 planned | Audit only, zero code changes, new chat session | 2026-03-06 |
| Frontend sprint 2 complete | TASK-042 through TASK-045 closed | Input accessibility, type migration, category screen remediation, mechanical cleanup | 2026-03-07 |
| TASK-010 closed | Engine Layer Refactoring — all 3 engines COMPLIANT | Team, Player, Predictor engines all pass bouncer + all gates | 2026-03-07 |
| TASK-039 closed | Backend pre-compute renderer fields — no changes needed | Existing pre-computation covers active items. PredictionCard blocked on Phase 12 | 2026-03-07 |
| Manifest schema extensions designed | TASK-046 design doc — 5 frontend violations required manifest infrastructure | source_registry, navigation_root, quick_links architecture agreed | 2026-03-07 |
| Source registry introduced | `source_registry` maps semantic keys to API path templates | Frontend resolves `{format_key}` and `{team}` at runtime — no hardcoded API paths | 2026-03-08 |
| Navigation root introduced | `navigation_root` declares default screen (key, label, icon) | Frontend never hardcodes "dashboard" — reads from manifest | 2026-03-08 |
| Quick links introduced | `quick_links` on manifest categories link to related categories | Hash-based navigation via `category_key` — no URL path construction | 2026-03-08 |
| Semantic source keys adopted | context_fields and extra_inputs use `"teams"` not `/api/v1/odi/context/teams` | API path template resolution centralised in source_registry | 2026-03-08 |
| source_params introduced | Extra inputs can pass `{team: "{team}"}` or `{team: "All"}` to parameterise source | Replaces URL segment parsing in ExtraInputCombobox.tsx | 2026-03-08 |
| api/schemas/manifest.py extended | SourceRegistryEntry, NavigationRoot, QuickLinkDesc Pydantic models added | All new fields Optional — backward compatible, zero breakage | 2026-03-08 |
| TASK-046 closed | Manifest Schema Extensions — all 6/6 frontend violations resolved | 9 files modified across backend + frontend, all gates PASS | 2026-03-08 |
| Frontend Skills Initiative — TASK-048 to TASK-057 | Skills directory restructured: backend/ + frontend/ subdirectories under guides/ and validators/ | 10 new skills: 3 frontend validators + 3 frontend guides. GATE F1–F3 registered in ENGINEERING_STANDARDS_FRONTEND.md and all agent config files | 2026-03-08 |
| TASK-048 closed | Skills directory reorganisation — backend/frontend split | All 6 guide skills → guides/backend/, all 6 validator skills → validators/backend/, frontend/ dirs created | 2026-03-08 |
| TASK-049 closed | All stale skill path references updated | CLAUDE.md, AGENTS.md, GEMINI.md, 3 ENGINEERING_STANDARDS files, paradigm-sentinel/SKILL.md — zero stale paths | 2026-03-08 |
| TASK-050 closed | frontend-lint-sentinel built | SKILL.md + run_frontend_lint.py — 15 checks covering 2.2A/2.2B/2.2C/2.2E/2.2F rules | 2026-03-09 |
| TASK-051 closed | frontend-paradigm-sentinel built | SKILL.md + run_frontend_paradigm.py — 8 architectural checks | 2026-03-08 |
| TASK-052 closed | frontend-type-sync-guard built | SKILL.md + run_type_sync.py — @schema JSDoc compliance for lib/types.ts | 2026-03-08 |
| TASK-053 closed | frontend-bug-fix-guide built | SKILL.md — 4-phase workflow with frontend RCA trace and F1–F3 gate sequence | 2026-03-08 |
| TASK-054 closed | frontend-modification-guide built | SKILL.md — delta discipline for UI changes, 7 delta checks + F1–F3 gates | 2026-03-08 |
| TASK-055 closed | frontend-new-component-guide built | SKILL.md — component classification, placement contract, renderer/layout specific checks | 2026-03-08 |
| TASK-056 closed | GATE F1–F3 added to ENGINEERING_STANDARDS_FRONTEND.md | Part 4.3 gate sequence, Part 4 note, Part 5.1 registry, Part 5.2 gate requirement all updated | 2026-03-08 |
| TASK-057 closed | Report templates updated in CLAUDE.md, AGENTS.md, GEMINI.md | GATE F1/F2/F3 rows added with "frontend scope only" annotation — parity with backend gate rows | 2026-03-08 |
| TASK-066 closed | Rule 2.2A-R6 calibration — `: unknown` exempt from `any` check | run_frontend_lint.py regex updated; SKILL.md rule description updated; F1 PASS | 2026-03-09 |
| TASK-067 closed | Gate F3 scan scope extended to all frontend/lib/*.ts | run_type_sync.py updated to scan all .ts files under lib/; SKILL.md updated | 2026-03-09 |
| TASK-065 closed | lib/types.ts split into three files — types.ts, comparison-types.ts, venue-types.ts | All files under 300-line limit; all import sites updated; @schema/@schema-exempt tags fully resolved across all three files | 2026-03-09 |
| TASK-068 closed | Rule 2.2B-R5 calibration — CSS files exempt from font-family check | run_frontend_lint.py exempts path.suffix==".css"; SKILL.md updated; 18 false positives eliminated; 11 real .tsx violations identified for follow-up | 2026-03-09 |
| TASK-069 closed | Pre-commit hook fully wired — all F1/F2/F3 + backend gates active | .githooks/pre-commit updated; Gates 1, 2-warning, 3, 4, F1, F2, F3, 5, 6 wired; LF line endings; staged-file scoping; Gate 3.5 dormant (Phase 12) | 2026-03-09 |
| : unknown exempt from 2.2A-R6 | Idiomatic TypeScript — type guard parameters and boundary inputs legitimately use : unknown | Rule calibrated — only `: any` flagged | 2026-03-09 |
| CSS files exempt from 2.2B-R5 | font-family declarations in .css are correct and canonical | Rule calibrated — only .tsx/.ts component files checked | 2026-03-09 |
| All 15 uncertain @schema interfaces confirmed @schema-exempt | None have standalone Pydantic equivalents in domain.py | frontend-only shapes marked @schema-exempt; F3 always-on | 2026-03-09 |
| Pre-commit hook wired — exit 0 confirmed | .githooks/pre-commit — LF line endings, staged-file scoping | All 9 gates active; Gate 3.5 dormant | 2026-03-09 |
| Guide skill audit sprint COMPLETE | All 9 SKILL.md files audited and corrected — duckdb-lint-ops paths, Gate 2 run command, Gate F3 trigger, @schema-exempt R4 | 2026-03-09 |
| duckdb-lint-ops/SKILL.md paths fixed | query_duckdb.py and run_lint.py paths corrected to include guides/backend/ segment | Legacy short paths did not exist — caused agent failures when following guide | 2026-03-09 |
| Gate 2 run command made explicit | Four backend guides (bug-fix, modification, refactor, new-feature) now have explicit run_lint.py command | Replaced vague "per SKILL.md" instruction — agents had correct path, no ambiguity | 2026-03-09 |
| Gate 2 pre-commit upgraded | .githooks/pre-commit Gate 2 block now runs run_lint.py and exits 1 on failure | Was warning-only — now blocks commits on DOD violations, matching all other gates | 2026-03-09 |
| Gate F3 trigger updated in all frontend guides | frontend-bug-fix-guide, frontend-modification-guide, frontend-new-component-guide — trigger now "always — scans all frontend/lib/*.ts" | Was conditional on lib/types.ts changes only — F3 is always-on per TASK-067 | 2026-03-09 |
| @schema-exempt R4 updated in frontend-new-component-guide | Phase 3 check R4 now documents both @schema and @schema-exempt patterns with correct JSDoc format | Enables agents to correctly tag frontend-only interfaces — previously only @schema was documented | 2026-03-09 |
| TASK_PROTOCOL.md created | docs/ai/TASK_PROTOCOL.md — authoritative agent routing guide, 545 lines, 7 sections | Covers task classification, guide load order, gate sequences, mixed-scope rules, hard rules, quick reference, full skill registry | 2026-03-09 |
| TASK-070 closed | Rules 2.2E-R2 + 2.2E-R3 added to frontend-lint-sentinel | check_onclick_non_interactive, check_live_region_announcements — false positives fixed for Context Provider and CSS variable substrings | 2026-03-09 |
| TASK-071 closed | Rule 2.2C-R3 added to frontend-lint-sentinel | check_inline_object_array_props — value prop on Context Provider exempt | 2026-03-09 |
| TASK-072 closed | Rule 2.2A-R14 added to frontend-lint-sentinel | check_polling_execute — setInterval/setTimeout calling /execute/ | 2026-03-09 |
| Gate F1 expanded to 15 rules | 4 new rules added: 2.2A-R14, 2.2C-R3, 2.2E-R2, 2.2E-R3 | Full rule inventory in SESSION_STATE.md | 2026-03-09 |
| value={{}} exempt from 2.2C-R3 | React Context Provider value prop — required JSX syntax, no alternative | Negative lookahead added to object_prop regex | 2026-03-09 |
| CSS variable substrings exempt from 2.2E-R3 | --tier-danger matched danger as substring — false positive | Word boundary regex via negative lookbehind/lookahead | 2026-03-09 |
| Rule 5.11 added to TASK_PROTOCOL.md | Mandatory disk verify after every file write — wc -l + grep checks required | Task marked invalid without disk verify results | 2026-03-09 |
| Rule 5.12 added to TASK_PROTOCOL.md | Pre-existing dirty files do not constitute a block — use git diff --name-only | Fixes recurring false block pattern | 2026-03-09 |
| Gate 3 pre-commit hook fixed | run_verifier.py requires --manifest argument — hook now loops over formats/*/manifest.py | Was failing on every commit attempt | 2026-03-09 |
| pre-commit.ps1 removed | Redundant PowerShell hook — Git never calls it, caused confusion | Only pre-commit (no extension) is active | 2026-03-09 |
---
| TASK-090 closed | Venue matchup structured payload now normalizes scalar score extremes to string values | Frontend venue adapter reads these fields as strings; raw ints rendered as "-" despite valid backend data | 2026-03-10 |
| TASK-091 closed | Venue matchup calculator returns raw int score extremes again while serializer stringifies only high/low/highest-chased | Restores Visual Silence layer ownership without regressing the TASK-090 frontend fix | 2026-03-10 |
| TASK-092 closed | Match audit exclusion-label regression traced to enrichment rebuilding MATCH_IDS audit rows from raw match_df | Confirmed the 2018-10-23 Colombo match carried STATUS_SHORT_SECOND_DROP and the calculator counts remained 4 matches / 3 valid / 1 short-second | 2026-03-10 |
| TASK-093 closed | Enrichment now status-tags fortress Match Audit rows before formatting | Preserves Excluded (Short 2nd) labels for excluded matches while keeping included matches and aggregate counts unchanged | 2026-03-10 |
| TASK-094 closed | Venue matchup frontend renderers now wrap long chase values and add audit-table column dividers | Fixes Avg Fail Chase truncation, removes the visible placeholder-gap effect in the chasing block, and restores Match Audit readability without backend changes | 2026-03-10 |
| TASK-095 closed | Refined Venue Matchup Report styling and contrast with team color coding, improved hierarchy, and pill-styled status badges | Applied dark theme polish pass across renderers and section components; all gates PASS | 2026-03-10 |
| TASK-096 closed | Venue matchup team headings and Match Audit team-name cells now resolve config-sourced jersey colours, with softer metric styling and wider layout spacing | Uses the existing team_color payload plus runtime CSS variables to keep exact team colours without raw hex literals in frontend source; panel padding and table column sizing remove clipping and jammed columns | 2026-03-10 |
| TASK-097 closed | Match Audit venue rows now prefer DAL `venue_id` and otherwise resolve raw venue text to a canonical venue ID before falling back to raw text | Normalizes venue-name variants such as the two R Premadasa strings to one audit identifier without touching DAL, serializer, or frontend layers | 2026-03-10 |
| TASK-102 closed | Home Fortress structured payload now labels the aggregate away side as `VISITORS`, computes aggregate visitor wins/defended/chased for `opp_team="All"`, and emits `MATCH_IDS` | Restores correct all-opponent fortress comparison semantics and re-enables enrichment-driven Match Audit rendering without changing serializer or frontend ownership | 2026-03-11 |
| TASK-103 closed | Home Fortress structured payload now routes aggregate visitor batting/chasing metrics through the existing `"Visitors"` sentinel branch using a `visitor_df` copy with `home_team_ref` | Restores populated all-visitor batting/chasing stats for Fortress Report while preserving the `VISITORS` display label and keeping specific-opponent behavior unchanged | 2026-03-11 |

| TASK-105 closed | Frontend paradigm sentinel now detects renderer payload extractors whose first parameter is `unknown` and whose typed return is a domain object | Captures the FortressReport SRP leak at the validator layer while preserving display-safe helpers and local type predicates | 2026-03-11 |

| TASK-106 closed | FortressReport payload types and extraction helpers now live in `frontend/lib/fortress-types.ts`, and FortressReport imports that adapter instead of parsing unknown payloads inline | Removes the Gate F2 renderer-SRP violation while preserving fortress UI output and restoring the renderer to a formatted sub-300-line file | 2026-03-11 |

*End of PROJECT_CONTEXT.md - Updated 2026-03-11 (TASK-106 fortress type extraction)*
*For ongoing session state, see SESSION_STATE.md — update between every session.*
*For agent task routing, see docs/ai/TASK_PROTOCOL.md — read before every task.*
