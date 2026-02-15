# 🧠 AI Context & Memory Index

**⚠️ STOP**: This file is now a **Landing Page**. Do NOT read the whole file. Read the linked file relevant to your need.

## 🤖 AI_DIRECTIVES (The Prime Directive)
**If you are an AI Agent, you MUST follow these 3 rules:**
1.  **READ THE LAW:** Before writing code, you MUST read [ENGINEERING_STANDARDS.md](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/docs/guides/ENGINEERING_STANDARDS.md).
2.  **ENFORCE THE LAW:** You MUST run `python scripts/context_linter.py` before finishing any task. Zero violations allowed.
3.  **RESPECT THE TRUTH:** Never modify `formats/odi/data/FINAL_ODI_MASTER.csv` manually. Use the Ingestion Scripts.

### [🎯 THE MISSION (Must Read)](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/docs/MISSION_STATEMENT.md)
**Status:** `ALWAYS_ALIGN`
*   **Goal:** Beat the Market (Algo-Trading).
*   **Philosophy:** Find the "Edge" in Granularity and Context.

### [🏗️ Engineering Standards (The Gold Standard)](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/docs/guides/ENGINEERING_STANDARDS.md)
**Status:** `READ_BEFORE_CODING`
*   **Roast:** Why manual ETL fails.
*   **Principles:** ROI-Driven, Headless Engines, Automated Truth.

## 🔄 Active Sprint & Next Tasks
**Current Phase:** Phase 10 (Frontend Development — Pre-Build Audit Complete)
**Immediate Goal:** Follow `docs/plans/FRONTEND_ROADMAP.md` sequentially (start Phase 0).
**Status:** `AUDIT_COMPLETE_FRONTEND_READY`

### ⚠️ MANDATORY: Frontend Roadmap
**Before writing ANY frontend/API code, you MUST read:**
- 📍 [FRONTEND_ROADMAP.md](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/docs/plans/FRONTEND_ROADMAP.md) — Phase tracker & agent rules
- 📍 [UI_SPEC.md](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/docs/design/UI_SPEC.md) — V5 Manifest-Driven Design

### Previous Sprints (Completed)
*   [x] Phase 8: Automated Pipeline (scripts/update_data.py)
*   [x] Phase 7: Headless Refactor (TeamEngine, PlayerEngine, PredictorEngine)
*   [x] Phase 6: UI Decoupling (TeamHTMLRenderer, themes.py)
*   [x] Phase 5: Truth Bridge (Regression suites, auto-diagnosis)
*   [x] Phase 4: Documentation Sprint (ENGINEERING_STANDARDS, DEV_GUIDE)
*   [x] Create `scripts/update_data.py` (Master Orchestrator).
*   [x] Refactor Venue Analysis to be **Headless & Typed** (TeamEngine v6.1).
*   [x] Decouple UI Rendering into `TeamHTMLRenderer` (MVC Alignment).
*   [x] Refactor Refinery & DB Ingester (Config-Driven isolation).
*   [x] Automated Pipeline Verification (JSON → DuckDB flow).




## 📂 Context Modules

### 0. [Frontend Roadmap](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/docs/plans/FRONTEND_ROADMAP.md) 🆕
**Status:** `READ_BEFORE_FRONTEND_WORK`
Contains:
*   9-Phase sequential roadmap for building the web app.
*   Per-phase task checklists and Definition of Done.
*   Agent rules (no skipping phases, manifest is law, no format-specific frontend code).
*   Status tracker (which phase is current).
*   Links to: [UI_SPEC.md](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/docs/design/UI_SPEC.md)

### 1. [Active State & Rules](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/docs/context/active_state.md)
**Status:** `ALWAYS_READ`
Contains:
*   Current System Architecture (Pure DB Mode, 4-Layer MVC).
*   Active Coding Rules (Zero-Destruction, Source of Truth).
*   Anti-Patterns (Mistakes to avoid).
*   Recent Critical Decisions.

### 2. [Holographic Index](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/docs/context/project_map.json)
**Status:** `ON_DEMAND`
Contains:
*   Project Dependency Graph.
*   Class & Function Signatures.
*   File Location Map.

### 3. Episodic Memory (Archives)
**Status:** `READ_LATEST`
*   [Feb 2026 Logs](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/docs/context/history/2026_02.md)
*   **Session 2026-02-15c (Phase 0: Foundation — COMPLETE ✅):**
    - **formats/odi/manifest.py**: Created ODI manifest — 7 categories, 17 functions. Each function declares `engine_class`, `engine_method`, `required_context`, `output_type`, and `extra_inputs`. Includes `context_fields` (venue, team_a, team_b, years, region) and approved `output_types` list.
    - **config/format_registry.py**: Upgraded to v2.1. Added `get_format_metadata()` for frontend format selector. Added `MatchPackGenerator` loading to `get_format_engines()`.
    - **scripts/validate_manifest.py**: Created manifest integrity validator. Runs 6 checks: engine_class loadability, engine_method existence (reflection), output_type approval, required_context validity, duplicate key detection, required field presence. Passes with 0 errors for ODI. 4 other formats correctly skipped (no manifest yet).
    - **FRONTEND_ROADMAP.md**: Phase 0 status → COMPLETE.
    - **Linter fixes**: Fixed 6 bare `except:` → `except (ValueError, TypeError)` in `player_renderer.py` (5) and `refinery_script.py` (1). Context linter now shows 0 violations.
*   **Session 2026-02-15d (Phase 1: API Layer — COMPLETE ✅):**
    - **api/main.py**: Complete rewrite to v2.0. Manifest-driven FastAPI with CORS middleware, lifecycle startup, tagged routes. Single generic `/execute/{function_key}` endpoint dispatches to any of the 17 engine functions via manifest lookup. Parameter mapping layer translates frontend context names to engine-specific argument names.
    - **api/models.py**: 9 Pydantic models — `ExecuteRequest`, `ExecuteResponse`, `HealthResponse`, `ManifestResponse`, `FormatInfo`, `ContextTeamsResponse`, `ContextVenuesResponse`, `ContextPlayersResponse`, `ErrorResponse`.
    - **api/serializers.py**: DataFrame/numpy/NaN serializer. Recursively converts all engine outputs to JSON-safe Python types. Handles DataFrames, numpy scalars, NaN→None, dataclasses, nested dicts.
    - **api/engine_pool.py**: Singleton CricketAnalyzer pool. Auto-discovers formats with manifests, initializes once at startup.
    - **scripts/test_api.py**: 12-endpoint smoke test — all passing (10 happy-path 200s + 2 error-path 404s).
    - **FRONTEND_ROADMAP.md**: Phase 1 status → COMPLETE.
*   **Session 2026-02-15e (Phase 2: Frontend Shell — COMPLETE ✅):**
    - **frontend/**: Initialized Next.js 16.1.6 project with React 19, Tailwind 4, TypeScript, Turbopack.
    - **frontend/app/globals.css**: Complete design system — 60+ CSS custom properties (design tokens): color layers (deepest→elevated), accent palette (blue/purple/cyan), 4-tier badges (elite/strong/caution/danger), glassmorphism, scrollbar, animations (fadeIn/slideIn/shimmer), format tabs, sidebar items with active indicator.
    - **frontend/lib/api.ts**: Typed API client with TypeScript interfaces mirroring Pydantic models. All components import from here instead of raw fetch().
    - **frontend/lib/context.tsx**: React Context for global app state — active format, manifest, context bar values (venue/team_a/team_b/years/region), teams/venues lists. Auto-fetches on mount.
    - **frontend/components/layout/FormatSelector.tsx**: Top bar with format tabs from /api/formats. Disabled tabs for formats without manifests. LIVE indicator.
    - **frontend/components/layout/ContextBar.tsx**: Dynamic context inputs from manifest.context_fields. Three widget types: Dropdown (teams/regions), Combobox with search (venues), Slider (years). Skeleton loading state.
    - **frontend/components/layout/Sidebar.tsx**: Dynamic sidebar from manifest.categories. Groups by `group` field, function count badges, collapsible, active state with accent glow + left border.
    - **frontend/app/page.tsx**: App shell composing 3 layers. Dashboard with stat cards + quick access grid. CategoryScreen with tabs, execute button, context validation, generic TableRenderer + ReportRenderer.
    - **frontend/next.config.ts**: API proxy — rewrites /api/* and /health from :3000 → :8000.
    - **FRONTEND_ROADMAP.md**: Phase 2 status → COMPLETE.
*   **Session 2026-02-15f (Phase 3: Generic Renderers — COMPLETE ✅):**
    - **frontend/components/renderers/DataTable.tsx**: Sortable, paginated generic data table. Click-to-sort columns, auto right-align numbers, Win% 4-tier color coding, OVERALL row highlight, hidden MATCH_IDS columns, prev/next pagination.
    - **frontend/components/renderers/ComparisonTable.tsx**: Section-grouped comparison view. Parses "---" section dividers from engine data, colored accent bars per section (blue=home, purple=visitor, cyan=venue), Win% color coding, hover highlights.
    - **frontend/components/renderers/MatrixTable.tsx**: Dominance matrix table. OVERALL row rendered as premium summary card with Trophy icon, sortable columns, form guide emoji display, Win% 4-tier coloring.
    - **frontend/components/renderers/FormTable.tsx**: Team form display. Streak dots (W/L/T bubbles), match-by-match cards with left-border color coding, emoji result indicators (✅❌🤝), date/venue metadata, score comparison.
    - **frontend/components/renderers/ReportCard.tsx**: Venue bias report. Hero verdict badge (BAT FIRST/BOWL FIRST/NEUTRAL), animated dual-bar Win% visualization, auto-generated stat card grid.
    - **frontend/components/renderers/PredictionCard.tsx**: Score prediction display. Giant gradient predicted score, animated range gauge bar (150-350 scale with par marker), breakdown cards (Venue Par/Batting Strength/Bowling Threat), adjustment notes.
    - **frontend/components/renderers/PlayerProfileCard.tsx**: Player profile. Gradient avatar, team badge + role chip, auto-categorized batting/bowling/details stat sections with responsive grid cards.
    - **frontend/components/renderers/MatchupTable.tsx**: Batter vs bowler grid. Bunny Alert detection (3+ dismissals), red background highlighting, AlertTriangle warning icon.
    - **frontend/components/renderers/DownloadPanel.tsx**: Match report download. Gradient header, Download JSON + Copy buttons, chapter completion checklist, collapsible JSON preview.
    - **frontend/components/renderers/FunctionRenderer.tsx**: Universal dispatcher. Routes output_type → correct renderer. Smart fallback auto-detection for unexpected data shapes. FallbackBanner warning.
    - **frontend/app/page.tsx**: Replaced Phase 2 generic ResultRenderer with FunctionRenderer dispatcher.
    - **frontend/app/globals.css**: Extended with btn-primary, btn-ghost, badges (4-tier), gradient-text, glass-card, animations (fadeIn/slideIn/shimmer/spin), skeleton loader.
    - **FRONTEND_ROADMAP.md**: Phase 3 status → COMPLETE.
*   **Session 2026-02-16a (Phase 4: API Wiring & Bug Fixes — IN PROGRESS):**
    - **frontend/components/layout/ContextBar.tsx**: Rewrote ComboboxField using ReactDOM.createPortal — dropdown now renders in document.body, fixing venue search clipping. Added "All" option to Home Team / Away Team dropdowns.
    - **api/main.py (_map_params)**: CRITICAL FIX — Added param filtering to only include `required_context` keys before mapping. Previously all context values leaked through causing "unexpected keyword argument" errors on every function call.
    - **api/main.py (_map_params)**: Fixed team_a mapping for `analyze_home_dominance` (needs `home_team`, not `team_name`). Fixed years mapping for `analyze_venue_phases` (needs `years`, not `years_back`). Separated `analyze_squad_types` team_a mapping.
    - **Function Status**: 11/17 functions now fully operational end-to-end. Remaining 6 need SquadBuilder UI (player_profile, compare_squads, tactical_matrix, matchups, predict_score, generate_pack). venue_phases has internal engine bug (FAIL-500).
    - **scripts/check_functions.py**: Created diagnostic script to test all 17 manifest functions via API.
    - **Git**: Committed as `6230817 feat(frontend): Phase 4 — Full-stack API wiring, venue search portal, param mapping fixes`
*   **Session 2026-02-15b (Documentation Overhaul):**
    - **README.md**: Complete rewrite. Updated from v1 ODI-only description to v3.0 multi-format architecture with proper directory structure, tech stack, roadmap table, and quick start guide.
    - **active_state.md**: Full rewrite. Updated CricketAnalyzer v2.1 → v3.0, added factory pattern details, format registry v2.0, packaging info, pipeline stages. Added 3 new anti-patterns from audit (bare except, IPython in core, ghost files).
    - **handover.md**: Complete rewrite. Was Truth Bridge-only; now covers full project state, all completed sprints, architecture overview, key files for new agents.
    - **ENGINEERING_STANDARDS.md**: Added achievement status table (10 standards tracked), added Format-Agnostic Core principle, updated roadmap (Phases 6-9 DONE, 10-13 planned).
    - **applicationArchitecture.md**: Updated Logic Layer to show factory pattern, added format_registry.py section, corrected directory structure with 15+ new/renamed files, added Factory and Format Registry to design patterns table.
    - **DEV_GUIDE.md**: Updated Logic Layer to list all 11 core components with factory descriptions, corrected directory structure, replaced prose roadmap with status table.
    - **TECHNICAL_DOCUMENTATION.md**: Updated engine.py section (v3.0 with two init modes), marked core engines as factories, updated design patterns (added Factory, Format Registry, Self-Healing Cache).
    - **GEMINI.md**: Added Section 7 (Onboarding Protocol — 4-step read order for new agents) and Section 8 (Documentation Auto-Update Protocol — trigger-based checklist for which docs to update after which changes).
    - **NEXT_GEN_UI.md**: Added readiness status (headless engines ✅, format registry ✅) and format-parameterized API endpoints.

*   **Session 2026-02-15 (Codebase Audit & Surgery):**
    - **Full Audit**: Scored codebase 5/10 overall. Engines strong (7/10), glue layer weak (3/10). Report: `docs/reports/CODEBASE_AUDIT_2026_02_15.md`.
    - **Ghost File Cleanup**: Deleted `core/player_engine_CORRUPTED.py` (70KB) and `core/player_engine_TEMP.py` (70KB).
    - **Shim Removal**: Removed all 5 `BACKWARD_COMPAT_SHIM` blocks from `core/team_engine.py`, `core/player_engine.py`, `core/predictor.py`, `formats/odi/engines/team_engine.py`, `formats/odi/engines/player_engine.py`.
    - **Factory Pattern**: Replaced hardcoded shims with `get_team_engine()`, `get_player_engine()`, `get_predictor_engine()` factories that dynamically load format-specific engines via the registry.
    - **Facade Rewrite**: `engine.py` v3.0 — now format-aware (`CricketAnalyzer(format_type='odi')`), uses `logger` instead of `print()`, uses shared `data_loader` (DRY). Full backward compat maintained.
    - **Format Registry v2.0**: Added `get_format_engines()`, `get_format_manifest()`, `get_format_config()` to `config/format_registry.py`.
    - **IPython Decoupled**: Removed IPython import from `core/predictor.py`. Core is now fully API-safe.
    - **Bare except Eradicated**: Fixed ALL 7 `except: pass` blocks across 5 files with specific exception types.
    - **Settings Rationalized**: Documented that `config/settings.py` constants are defaults; format configs override. Added prediction constants to `formats/odi/config/settings.py`.
    - **Interfaces Updated**: Fixed orphaned `ITeamEngine` protocol to match real engine API signatures.
    - **Packaging**: Added `pyproject.toml`, `.env.example`, updated `.gitignore`, pinned DuckDB, removed Streamlit.
    - **BaseEngine Enhanced**: Added `_safe_float()`, `_safe_divide()`, `_format_pct()` utilities.
    - **Tests Verified**: Both legacy `CricketAnalyzer(filepath)` and modern `CricketAnalyzer(format_type='odi')` produce identical results. All engines functional.
    - **Truth Bridge Expansion (Phase 2)**: Created `player_stats_validation` and `team_form_validation` suites. Seeded Ground Truth for Player Profiles (Kohli, Rohit, etc.) and Team Form logic.
    - **Pipeline Integration**: Created `formats/odi/tests/truth_bridge/run_all.py` as master verifier. Integrated as **Stage 4** in `scripts/update_data.py`. Automatic failure on regression.
    - **Facade Fix**: Patched `engine.py` to correctly locate `processed_player_stats.csv` relative to the format file path, preventing crashes on startup.
    - **Phase 3 (Documentation):** Updated `DEV_GUIDE.md` with "Data Intelligence Pipeline" and "Verification Suite" sections. Created `docs/reports/GAP_ANALYSIS_PHASE3.md` detailing the Hybrid Architecture rationale and roadmap.
    - **Session 2026-02-15 (Previous):** Completed **Headless Refactor (Phase 6)** for `TeamEngine` and `PlayerEngine`.
    - **TeamEngine**: Removed UI/IPython dependencies, vectorized `_generate_matrix_report` and helpers using `np.where`. Added comprehensive type hints.
    - **PlayerEngine**: Removed UI/IPython dependencies. Vectorized `_calculate_squad_metrics`. Fixed tuple-vs-list serialization bug in `analyze_squad_types` that caused regression failures.
    - **Truth Bridge**: Achieved 100% pass rate (188/188) for `compare_squads` regression suite after fixing `analyze_squad_types` to return native Python lists/types.
    - Verified `TeamHTMLRenderer` usage in `interface.py` for headless architecture compliance.
    - **PredictorEngine (Phase 6)**: Refactored `formats/odi/predictor.py` to be fully **Vectorized** (removed O(N*M) loops), **Typed**, and **Headless** (removed IPython).
    - **Interface**: Extracted huge CSS/Theme logic into `config/shared/themes.py`, reducing `interface.py` clutter and centralization UI constants.
    - **Truth Bridge (Predictor)**: Created new `predictor_validation` suite. 3/3 scenarios (High Scoring, Low Scoring, Neutral) **PASSED** against new vectorized logic.
    - **Renderer Fix**: Updated `team_renderer.py` to use `TEAM_COLORS` constant, eliminating hardcoded hex values.
    - **Linter Certified**: Ran `context_linter.py` and achieved **0 Violations**. All Hex codes are now centralized in `config/shared/team_colors.py`.
    - **Context Pipeline**: Embedded `ENGINEERING_STANDARDS.md` into `docs/context/rules.json`. The `context_linter.py` now enforces: API-First (No HTML), Vectorization (No iterrows), Type Hints, and Crash Early policies.
*   **Session 2026-02-14:** Completed Phase 8 (Automated Pipeline). Created `scripts/update_data.py`. Refactored Refinery and DB Ingester to be config-driven, ensuring format isolation for phase-stats and databases. Verified successful JSON → DuckDB flow for 2500+ ODI matches.
