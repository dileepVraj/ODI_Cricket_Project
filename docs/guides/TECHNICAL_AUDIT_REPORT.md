# Cricket Algo-Trader — Full Technical Audit Report
**Audit Date:** 2026-03-08
**Auditor:** Senior Software Architect (Antigravity)
**Codebase:** `c:\Cricket_Project_Stable` — version 3.2.0

---

## SECTION 1: AUDIT SNAPSHOT & PHASE STATUS

### 1.1 Last Updated / Audit Date
**Date:** 2026-03-08 (Updated from 2026-03-03)
**Key Changes Since Previous Audit (v3.1.0):**
- **Engine Refactoring Complete (TASK-010):** All three engines — Team, Player, Predictor —
  signed off COMPLIANT. Predictor engine underwent major stateless refactor (9 violations fixed).
- **Frontend Compliance Audit (TASK-029):** Full 90-violation audit completed across 27 files.
- **Frontend Sprint 2 (TASK-042–045):** Input accessibility, type migration,
  CategoryScreen remediation, and mechanical cleanup — all closed 2026-03-07.
- **Backend Pre-compute Audit (TASK-039):** Closed — existing backend pre-computation
  already covers active items. PredictionCard deferred to Phase 12.
- **Manifest Schema Extensions (TASK-046):** source_registry, navigation_root, quick_links
  introduced. 6/6 frontend violations resolved. 9 files modified across backend + frontend.
- **Skills Expansion:** Four enforcing guide skills built (bug-fix, new-feature, refactor, modification).
  context-loader skill built and committed. All under `core/gen_ai/skills/guides/`.
- **Agent Config Hardened:** Filesystem Integrity Rules (7 rules) added to AGENTS.md and GEMINI.md
  Part 5 following Codex incident. `docs/ai/` declared human-write-only.

### 1.2 Phase Status
- **Phase 11.3 (Calculators):** ✅ **Complete** — All calculators refactored, type-hinted, and vectorized.
- **Engine Refactoring (TASK-010):** ✅ **Complete** — All 3 engines COMPLIANT (Team 2026-03-05, Player 2026-03-06, Predictor 2026-03-07).
- **Frontend Audit (TASK-029):** ✅ **Complete** — 90 violations catalogued (2026-03-06).
- **Frontend Sprint 2 (TASK-042–045):** ✅ **Complete** — Accessibility, type migration, structural remediation (2026-03-07).
- **Manifest Extensions (TASK-046):** ✅ **Complete** — Schema + consumers, all gates PASS (2026-03-08).
- **Phase 12 (Live Layer / Numba AOT):** ❌ **Not Started** — No implementation planned for current sprint.

### 1.3 Application Architecture (Verified)
The application follows a **Hexagonal Architecture** (Ports & Adapters) with a **Layered N-Tier** organizational wrapper.

| Layer | Location | Role |
|---|---|---|
| **Data Access (DAL)** | `core/data_access.py` | Exclusive DuckDB gateway |
| **Domain Calculators** | `core/calculators/` | Pure, stateless math |
| **Domain Services** | `core/services/` | Data transformation and assembly |
| **Format Engines** | `formats/odi/engines/` | Business logic orchestration |
| **Format Predictor** | `formats/odi/predictor.py` | Score prediction (stateless, DAL air-gapped) |
| **Format Manifest** | `formats/odi/manifest.py` | UI contract — categories, functions, source registry |
| **API Adapter** | `api/` | FastAPI REST bridge (main.py, serializers.py, schemas/) |
| **Frontend** | `frontend/` | Next.js 14 UI, manifest-driven |

### 1.4 Engine Compliance Status

| Engine | File | Status | Date | Key Changes |
|---|---|---|---|---|
| Team Engine | `formats/odi/engines/team_engine.py` | ✅ COMPLIANT | 2026-03-05 | Constructor discard pattern (KIP-001), stateless design |
| Player Engine | `formats/odi/engines/player_engine.py` | ✅ COMPLIANT | 2026-03-06 | 62 violations resolved (TASK-026–028), ARCH-DEC-01/02/03 |
| Predictor Engine | `formats/odi/predictor.py` | ✅ COMPLIANT | 2026-03-07 | 9 violations fixed: DAL air-gap, stateful constructor, Anti-Any, zero-literal, visual silence |

**Bouncer Status:** `PASS: 100% compliance across 22 file(s)` (verified 2026-03-08)

---

## SECTION 2: ENGINEERING GOVERNANCE & STANDARDS

### 2.1 Engineering Standards State
The standards are split to reduce context load while maintaining a single source of truth:
- **`ENGINEERING_STANDARDS_CORE.md` (v2.3):** Authoritative source for human architects.
- **`ENGINEERING_STANDARDS_BACKEND.md` (v2.2):** Scoped for backend-only agents. Includes KIP registry (Part 7).
- **`ENGINEERING_STANDARDS_FRONTEND.md` (v2.2):** Scoped for frontend agents; expanded to 38 rules (2.2A–2.2F).

### 2.2 Governance Sentinel Pipeline (Six-Gate Order)
Every task MUST pass through these gates in order:
1. **GATE 1 — boundary-sentinel:** Layered import enforcement (`core/`).
2. **GATE 2 — duckdb-lint-ops (guides/):** Vectorization/DOD enforcement.
3. **GATE 3 — manifest-contract-verifier:** Manifest-to-engine signature sync.
4. **GATE 4 — serialization-guard:** API response validation and schema compatibility.
5. **GATE 5 — paradigm-sentinel:** Meta-check for all mandates.
6. **GATE 6 — compliance_bouncer:** Final 10-rule check (ZERO_LITERAL, ANTI_ANY, IO_AIR_GAP, etc.).

**Dormant:** `event-state-linter` (reserved for Phase 12).
**Note:** Gates 1–5 are currently prompt-based skills. Automation as runnable Python scripts is in ICEBOX.

### 2.3 High-Impact File Registry
The following files carry disproportionate architectural risk and require the **stop-state-trace-confirm** protocol:
- **`core/data_access.py` — [CRITICAL]** — Every engine and service depends on it.
- **`core/interfaces/team_types.py` — [HIGH]** — Load-bearing type contract.
- **`api/serializers.py` — [HIGH]** — Handles every API response edge case.

### 2.4 Skills Structure
Current directory layout under `core/gen_ai/skills/`:
- **`.system/`:** `skill-creator`, `skill-installer` (Internal agent management).
- **`guides/`:** `duckdb-lint-ops`, `context-loader`, `bug-fix-guide`,
  `new-feature-guide`, `refactor-guide`, `modification-guide`.
- **`validators/`:** `boundary-sentinel`, `manifest-contract-verifier`,
  `event-state-linter` (dormant), `serialization-guard`, `executive-auditor`,
  `paradigm-sentinel`.

### 2.5 Known Intentional Patterns (KIP)
Documented in `ENGINEERING_STANDARDS_BACKEND.md` Part 7:
- **KIP-001:** Constructor discard pattern `_ = (match_df, phase_df, dal)` in `team_engine.py` — intentional stateless design.
- **KIP-002:** `_context_match_df` defined in lower file section of `team_engine.py` — file layout choice, not missing method.

---

## SECTION 3: FRONTEND STATE & COMPLIANCE

### 3.1 Frontend Standards State
The frontend operates under 38 specific mandates (v2.2) grouped into six categories:
- **2.2A — Architectural Rules (15):** Boundary enforcement, manifest contract, state purity, format agnosticism, async cancellation.
- **2.2B — UI Implementation (10):** CSS tokens, named utilities, badge semantics, icon library, font system, animations.
- **2.2C — Performance (3):** Lazy loading renderers, memoisation discipline, no inline object/array props.
- **2.2D — Resilience (3):** Error boundary isolation, placement rules, backend type sync contract.
- **2.2E — Accessibility (3):** Interactive labels, keyboard navigation, loading/error announcements.
- **2.2F — Testing (3):** Vitest + React Testing Library (RTL) stack requirements.

### 3.2 Frontend Compliance Debt
**Source:** TASK-029 audit (2026-03-06). Full register: `docs/audits/frontend/AUDIT-F10-violation-summary.md`

**Statistics:**
  Total violations found: 90 (HIGH: 24, MEDIUM: 54, LOW: 12)
  Resolved by TASK-042–045: ~20 (input accessibility, type migration, structure, cleanup)
  Resolved by TASK-046: 6 (manifest-driven navigation, source keys, quick links)
  Remaining: ~64

**Resolved Violations (TASK-046):**
- F04-V03: page.tsx hardcoded "dashboard" → manifest.navigation_root
- F06-V03: ContextBar hardcoded source keys → semantic keys match naturally
- F06-V05: Sidebar hardcoded DASHBOARD_ITEM → derived from manifest
- F06-V08: QuickLinks hardcoded link definitions → manifest quick_links
- ExtraInputSelect hardcoded API path matching → semantic key comparison
- ExtraInputCombobox hardcoded API path parsing → source_params

**Remaining Systemic Patterns:**
- Empty state: 12/13 renderers use inline fallback instead of EmptyState
- Inline `as` casts: FunctionRenderer + 9 renderers
- Font system: 7 renderers use `font-variant-numeric` not `font-numeric`
- Raw colours outside CSS token system: 7 files
- Mouse-only comboboxes: ContextBar, SquadBuilder, ExtraInputRenderer
- Missing `role="alert"`: page.tsx, SquadBuilder
- Missing loading state announcements: page.tsx, SkeletonLoader

**Tier 1 Blockers (must be created first):**
- ErrorBoundary component in `components/common/` — unblocks F04-V05, F05-V04, F09-V01
- Shared accessible combobox primitive — unblocks F06-V04, F08-V05, F08-V10

**Backend Pre-computation (TASK-039 audit findings):**
- F07-V21: PhaseAnalysisCard — LOW, backend already sends data, fallback is backward-compat
- F07-V26: PredictionCard — BLOCKED on Phase 12 (`predict_score` removed)
- F07-V30: PlayerProfileCard — LOW, backend sends structured dataclass

### 3.3 Manifest Schema (TASK-046)

The manifest (`formats/odi/manifest.py`) was extended with three new slots:

| Slot | Purpose | Entries |
|---|---|---|
| `source_registry` | Maps semantic keys to API path templates | teams, venues, players, host_countries, regions |
| `navigation_root` | Declares default screen (key, label, icon) | dashboard / Dashboard / home |
| `quick_links` | Category-level navigation chips | venue_intel(2), rivalry(2), player_scout(2) |

**Key Design Decisions:**
- All `context_fields[].source` and `extra_inputs[].source` use semantic keys, not API paths
- `source_params` supports parameterised resolution (e.g., `{team: "{team}"}` or `{team: "All"}`)
- All new Pydantic models and TS interfaces are Optional — zero breakage for future formats
- Frontend resolves `{format_key}` and `{team}` template variables at runtime
- `preload: true` marks sources that should be fetched eagerly (teams, venues)
- QuickLinks uses hash-based navigation (`#category_key`), not Next.js URL routing

---

## SECTION 4: PENDING WORK & PRIORITIES

### 4.1 Priority Queue (Active)
Reflecting the current state of `SESSION_STATE.md` and `BACKLOG.md`:

1. **Frontend Remediation Sprint — TASK-030** (not yet created)
   Scope: ~64 remaining violations from TASK-029 audit.
   Start with Tier 1 blockers: ErrorBoundary, accessible combobox.
   Full register: `docs/audits/frontend/AUDIT-F10-violation-summary.md`
2. **Token Optimisation — TASK-012** (needs 1-week monitoring from 2026-03-03)
   Section-aware context loading to reduce agent token burn.

### 4.2 Completed Since Last Audit (v3.1.0)

| Task | Status | Date | Summary |
|---|---|---|---|
| TASK-010 | ✅ CLOSED | 2026-03-07 | Engine Layer Refactoring — all 3 engines COMPLIANT |
| TASK-039 | ✅ CLOSED | 2026-03-07 | Backend pre-compute audit — no changes needed |
| TASK-042 | ✅ CLOSED | 2026-03-07 | Input Label Accessibility Fix |
| TASK-043 | ✅ CLOSED | 2026-03-07 | FunctionRenderer Type Migration |
| TASK-044 | ✅ CLOSED | 2026-03-07 | CategoryScreen Structural Remediation |
| TASK-045 | ✅ CLOSED | 2026-03-07 | Mechanical Cleanup Pass |
| TASK-046 | ✅ CLOSED | 2026-03-08 | Manifest Schema Extensions — 6/6 violations resolved |

---

## SECTION 5: KEY ARCHITECTURAL DECISIONS (Post 2026-02-27)

| Decision | Date | Outcome | Rationale |
|---|---|---|---|
| **Remove Mandate 7 (Numba AOT)** | 2026-03-03 | Removed from Backend standards | Phase 12 is too early for agents to push towards. |
| **Deprecate `AI_MEMORY.md`** | 2026-03-03 | Replaced by `SESSION_STATE.md` | Memory files became unreliable git-log noise. |
| **Context Pipeline (3-Tier)** | 2026-03-03 | Mandatory 3-document context loading | Formalized context loading (Tier 1 standards, Tier 2 state, Tier 3 audit). |
| **Standards Split** | 2026-03-03 | CORE/BACKEND/FRONTEND files | Reduces context-token load per agent. |
| **High-Impact Registry** | 2026-03-03 | `stop-state-trace-confirm` rule | Prevents accidental modification of volatile system files. |
| **Filesystem Integrity Rules** | 2026-03-04 | 7 rules in AGENTS.md/GEMINI.md Part 5 | Codex deleted `core/` during worktree task — hard stops prevent repeat. |
| **Guide Skills System** | 2026-03-04 | 4 enforcing guides built | bug-fix, new-feature, refactor, modification — prompt-discipline enforcement. |
| **ARCH-DEC-01** | 2026-03-06 | Group A dual-path standardised | Constructor-data primary, injection is enrichment. |
| **ARCH-DEC-02** | 2026-03-06 | Group B dead paths removed | All 19 caller files verified safe. |
| **ARCH-DEC-03** | 2026-03-06 | Rounding precision + innings threshold split | stat_precision_avg=0, stat_precision_rate=1. |
| **Source Registry** | 2026-03-08 | Semantic source keys in manifest | No hardcoded API paths in frontend — centralised resolution. |
| **Navigation Root** | 2026-03-08 | Default screen declared in manifest | Frontend never hardcodes "dashboard". |
| **Quick Links** | 2026-03-08 | Category-level navigation in manifest | Hash-based nav via `category_key`, not URL paths. |
| **Source Params** | 2026-03-08 | Parameterised source resolution | `{team: "{team}"}` replaces URL segment parsing. |

---

## SECTION 6: UNVERIFIED / RESOLVED SECTIONS

### 6.1 Resolved (Verified as of v3.2.0)
- **`backtester.py` + `base_engine.py`:** Confirmed dead scaffolding, never git-tracked. Removed (TASK-009).
- **Engine compliance:** All 3 engines fully audited and compliant (TASK-010, TASK-026–028).

### 6.2 Remaining Unverified
- **`formats/t20i/`, `formats/ipl/`, etc.:** [UNVERIFIED]. Registered in code but no directories exist. Will be addressed during format expansion (ICEBOX).

---
*End of Technical Audit Report — Version 3.2.0 — 2026-03-08*
