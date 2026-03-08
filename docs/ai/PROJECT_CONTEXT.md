# PROJECT_CONTEXT.md
**Purpose:** Claude Projects knowledge base — full project history, decisions, standards, and pending work.
**Last Updated:** 2026-03-08
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

### 3.3 Six-Gate Sentinel Order

| Gate | Skill | Trigger |
|------|-------|---------|
| GATE 1 | `validators/boundary-sentinel` | Any modification to `core/` |
| GATE 2 | `guides/duckdb-lint-ops` | Any modification to `calculators/`, `engines/`, `services/` |
| GATE 3 | `validators/manifest-contract-verifier` | Any modification to `manifest.py` or engine files |
| GATE 4 | `validators/serialization-guard` | Any modification to `api/serializers.py` or engine return types |
| GATE 5 | `validators/paradigm-sentinel` | Always — after all primary gates pass |
| GATE 6 | `core/utils/compliance_bouncer.py` | Always — last step before every commit |

Dormant: `event-state-linter` — activates when `core/live/` is created in Phase 12.

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

core/gen_ai/skills/
    .system/      — skill-creator, skill-installer (DO NOT TOUCH)
    guides/       — duckdb-lint-ops, context-loader,
                    bug-fix-guide, new-feature-guide,
                    refactor-guide, modification-guide
    validators/   — boundary-sentinel, manifest-contract-verifier,
                    event-state-linter (dormant), serialization-guard,
                    executive-auditor, paradigm-sentinel

IMPORTANT: Gate 2 (duckdb-lint-ops) is in guides/ not validators/.

**IMPORTANT:** Gate 2 (duckdb-lint-ops) is in `guides/` not `validators/`.

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
- **Pre-commit hook enforces compliance** — `.githooks/pre-commit`
- **No `--no-verify` commits** — bouncer is not optional
- **High-impact files require stop-state-trace-confirm** — Section 3.6
- **Engine refactoring is the active work** — Phase 12 NOT started
- **duckdb-lint-ops is in `guides/`** not `validators/` — use correct path in Gate 2
- **Agent report format** — keep under 30 lines, use strict template
- **Phase state lives in SESSION_STATE.md only** — never hardcode phase in agent config files
- **Agent config files share a common structure** — diverge only where tool-specific behaviour requires it
- **core/ strategy loaders are active files** — team_engine.py, predictor.py, player_engine.py
  are NOT legacy. Do not delete them.
- **match_pack/ is a legitimate feature** — report generator, not clutter
- **Codex worktree can delete files** — always run `git status` after Codex tasks,
  restore with `git restore core/` if deletions appear

---

## 10. KEY ARCHITECTURAL DECISIONS (HISTORY)

| Decision | Outcome | Rationale |
|----------|---------|-----------|
| Remove Mandate 7 (Numba AOT) | Removed from v2.2 | Premature — agents kept pushing Phase 12 |
| Do-Not-Touch Registry → High-Impact Registry | 3 files, stop-trace-confirm rule | Active refactoring needs engines/manifest/calculators accessible |
| `executive-auditor` kept but not in gate sequence | Redundant with paradigm-sentinel | paradigm-sentinel does everything executive-auditor does, plus more |
| `duckdb-lint-ops` stays in `guides/` | Dual classification | Guides DuckDB usage AND validates DOD compliance |
| AI_MEMORY.md → deprecate | Replaced with SESSION_STATE.md | Memory file became git-log noise |
| Standards split CORE/BACKEND/FRONTEND | Reduces context load per agent | Frontend agent does not need WebSocket-first mandate |
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
---

*End of PROJECT_CONTEXT.md — Updated 2026-03-08*
*For ongoing session state, see SESSION_STATE.md — update between every session.*
