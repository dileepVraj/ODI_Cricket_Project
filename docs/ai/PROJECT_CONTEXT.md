# PROJECT_CONTEXT.md
**Purpose:** Claude Projects knowledge base — full project history, decisions, standards, and pending work.
**Last Updated:** 2026-03-03
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
core/utils/compliance-bouncer.py — 10-rule compliance enforcer
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

**Phase:** Post Phase 11.3 — calculators fully refactored and compliant.
**Next phase:** Engine-layer refactoring (active work area).
**Phase 12 (live layer / Numba AOT): NOT started — do not push agents toward it.**

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
| GATE 6 | `core/utils/compliance-bouncer.py` | Always — last step before every commit |

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

```
core/gen_ai/skills/
    .system/      — skill-creator, skill-installer (DO NOT TOUCH)
    guides/       — duckdb-lint-ops, context-loader
    validators/   — boundary-sentinel, manifest-contract-verifier,
                    event-state-linter (dormant), serialization-guard,
                    executive-auditor, paradigm-sentinel
```

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

### 5.2 Filesystem Integrity Rules (added 2026-03-03)

Added to Part 5 of AGENTS.md and GEMINI.md after Codex deleted `core/` contents
during a worktree task. Rules cover:

- Never delete files outside task scope
- Never run destructive git operations (`git clean`, `git reset --hard`, `git rm`)
- Missing reference files = hard stop, do not improvise workarounds
- No speculative recursive filesystem exploration
- Run `git status` on target directory before AND after every file operation
- If unexpected deletions appear in git status — stop immediately, report as CRITICAL DEVIATION

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

### 7.1 Frontend Compliance Debt (tracked — not yet actioned)

| Item | File | Action needed |
|------|------|---------------|
| Eager renderer imports | `FunctionRenderer.tsx` | Refactor to `React.lazy()` + Suspense |
| No Error Boundary | `page.tsx` CategoryScreen | Wrap renderer output in Error Boundary |
| Types in api.ts not types.ts | `frontend/lib/api.ts` | Create `lib/types.ts`, migrate types |
| Missing aria-live/role | `page.tsx` | Add to result container and error display |
| No test stack | `package.json` | Add Vitest + React Testing Library |

---

## 8. PENDING WORK — EXECUTION PLAN

In priority order:

1. **Engine refactoring** — primary active work, engine files need refactoring
2. **Wire context-loader bootstrap into AGENTS.md + GEMINI.md** — skill is built,
   needs wiring so it fires automatically at agent session start
3. **Add Filesystem Integrity Rules to AGENTS.md + GEMINI.md** — Part 5 addition,
   prevents repeat of Codex worktree deletion incident
4. **Core/ file audit** — verify no stray/legacy files remain. `backtester.py` and
   `base_engine.py` confirmed safe to delete — pending commit.
5. **Update TECHNICAL_AUDIT_REPORT.md** — stale since 2026-02-27, predates Phase 11.3
6. **Create CLAUDE.md** — when Claude CLI pro sub is activated, copy from AGENTS.md
7. **Frontend compliance debt** — 5 items above, after engine queue clears

---

## 9. IMPORTANT CONVENTIONS

- **Never attach AI_MEMORY.md to agents** — deprecated, noise
- **Bouncer must pass before every commit** — `python core/utils/compliance-bouncer.py --root .`
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

---

*End of PROJECT_CONTEXT.md — Generated 2026-03-03*
*For ongoing session state, see SESSION_STATE.md — update between every session.*
