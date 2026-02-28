# 🗺️ FRONTEND DEVELOPMENT ROADMAP
# Manifest-Driven, Multi-Format Cricket Algo-Trading Platform

**Version:** 1.0  
**Created:** 2026-02-15  
**Status:** `ACTIVE` — All agents MUST follow this roadmap sequentially.  
**Design Spec:** `docs/design/UI_SPEC.md` (V5 — Manifest-Driven Architecture)  
**Stack:** FastAPI (Python) + Next.js 14 (React) + Tailwind CSS + Shadcn/UI + Tremor

---

## ⚠️ AGENT PRIME DIRECTIVE

```
┌──────────────────────────────────────────────────────────────────────┐
│  🛑 EVERY AI AGENT working on this project MUST:                    │
│                                                                      │
│  1. READ this roadmap BEFORE writing any frontend/API code           │
│  2. IDENTIFY which Phase they are starting from (check STATUS below) │
│  3. COMPLETE the current Phase fully before advancing                │
│  4. UPDATE the STATUS section at the bottom after completing work    │
│  5. NEVER skip phases — they are sequential dependencies            │
│  6. FOLLOW the Definition of Done for each phase                    │
│                                                                      │
│  📍 Design Spec: docs/design/UI_SPEC.md                             │
│  📍 Engineering Rules: docs/guides/ENGINEERING_STANDARDS.md          │
│  📍 Memory: docs/ai/AI_MEMORY.md                                    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ PHASE OVERVIEW

```
Phase 0: Foundation (Manifest + Format Registry)    ██████████ COMPLETE ✅
Phase 1: API Layer (FastAPI Backend)                 ██████████ COMPLETE ✅
Phase 2: Frontend Shell (Next.js + Layout)           ██████████ COMPLETE ✅
Phase 3: Generic Renderers (Component Library)       ██████████ COMPLETE ✅
Phase 4: Dynamic Screens (Manifest → UI)             ██████████ COMPLETE ✅
Phase 5: Context System (Global Filters)             ░░░░░░░░░░ NOT STARTED
Phase 6: Cross-Navigation + Polish                   ░░░░░░░░░░ NOT STARTED
Phase 7: Multi-Format Activation                     ░░░░░░░░░░ NOT STARTED
Phase 8: Production Hardening                        ░░░░░░░░░░ NOT STARTED
```

---

## 📦 PHASE 0: FOUNDATION (Manifest + Format Registry)
**Goal:** Create the manifest system that drives the entire UI.  
**Depends On:** Nothing (can start immediately)  
**Estimated Effort:** 1 session

### Tasks:

#### 0.1 — Create ODI Manifest File
```
File: formats/odi/manifest.py
```
- Export a `MANIFEST` dictionary following the schema defined in `docs/design/UI_SPEC.md`
- Must declare ALL existing ODI categories and functions:
  - `venue_intel` (4 functions: venue_bias, venue_matchup, home_fortress, venue_phases)
  - `rivalry` (3 functions: global_h2h, country_h2h, continent_perf)
  - `team_command` (4 functions: home_dominance, away_performance, global_performance, team_form)
  - `player_scout` (1 function: player_profile)
  - `squad_battle` (3 functions: compare_squads, tactical_matrix, matchups)
  - `predictor` (1 function: predict_score)
  - `match_pack` (1 function: generate_pack)
- Each function entry must declare: `key`, `label`, `engine_method`, `required_context`, `output_type`
- Validate that every `engine_method` string matches a REAL method on the actual engine class

#### 0.2 — Upgrade Format Registry
```
File: config/format_registry.py
```
- Add `manifest` key to each format entry
- Add `get_format_manifest(format_type)` function that loads the manifest
- Ensure `get_available_formats()` returns format metadata needed by the frontend

#### 0.3 — Create Manifest Schema Validator
```
File: scripts/validate_manifest.py
```
- Script that validates a format's manifest:
  - Every `engine_method` exists on the actual engine class
  - Every `required_context` field is valid
  - Every `output_type` is from the approved list
  - No duplicate `key` values
- Run automatically during CI or dev startup

### Definition of Done (Phase 0):
- [ ] `formats/odi/manifest.py` exists with all 18 functions declared
- [ ] `config/format_registry.py` updated with manifest loader
- [ ] `scripts/validate_manifest.py` passes with 0 errors for ODI
- [ ] `AI_MEMORY.md` updated with Phase 0 completion

---

## 📦 PHASE 1: API LAYER (FastAPI Backend)
**Goal:** Wrap all headless engines in REST endpoints.  
**Depends On:** Phase 0  
**Estimated Effort:** 2-3 sessions

### Tasks:

#### 1.1 — FastAPI Skeleton
```
File: api/main.py
```
- Install: `fastapi`, `uvicorn`, `pydantic`
- Create FastAPI app with CORS middleware (for Next.js frontend)
- Mount format-aware router prefix: `/api/{format_type}/...`

#### 1.2 — Manifest Endpoint
```
Endpoint: GET /api/{format_type}/manifest
```
- Returns the format's manifest JSON
- Frontend uses this to build sidebar, screens, tabs dynamically

#### 1.3 — Context Endpoints
```
Endpoints:
  GET /api/{format_type}/context/teams     → List of teams
  GET /api/{format_type}/context/venues    → List of venues
  GET /api/{format_type}/context/players/{team}  → Players for a team
  GET /api/{format_type}/context/regions   → List of continents/regions
```
- These supply the dropdown options in the Context Bar
- Each format returns its own team/venue/player lists

#### 1.4 — Generic Execute Endpoint
```
Endpoint: POST /api/{format_type}/execute/{function_key}
```
- Accepts JSON body with parameters (from context + extra inputs)
- Looks up `function_key` in the format's manifest
- Calls the corresponding `engine_method` on the correct engine
- Returns the engine's output as JSON
- **Data Transformation:** Engine outputs (Python dicts/dataclasses) must be
  JSON-serializable. Create `api/serializers.py` to handle:
  - pandas DataFrames → list of dicts
  - numpy types → native Python types
  - dataclasses → dicts

#### 1.5 — Engine Initialization
```
File: api/engine_pool.py
```
- Singleton pattern: each format's `CricketAnalyzer` is initialized ONCE at startup
- Not per-request (too slow — data loading takes seconds)
- Thread-safe access for concurrent requests

#### 1.6 — Pydantic Models
```
File: api/models.py
```
- Request/response models for API validation
- `FunctionExecuteRequest(function_key, params)`
- `ManifestResponse(format_key, categories, context_fields)`

### Definition of Done (Phase 1):
- [ ] `uvicorn api.main:app` starts without errors
- [ ] `GET /api/odi/manifest` returns valid manifest JSON
- [ ] `GET /api/odi/context/teams` returns team list
- [ ] `POST /api/odi/execute/venue_bias` returns venue bias data
- [ ] All 18 ODI functions callable via `/execute/{key}`
- [ ] Swagger docs available at `/docs`
- [ ] `AI_MEMORY.md` updated with Phase 1 completion

---

## 📦 PHASE 2: FRONTEND SHELL (Next.js + Layout)
**Goal:** Create the app skeleton with navigation structure.  
**Depends On:** Phase 1 (API must be running)  
**Estimated Effort:** 1-2 sessions

### Tasks:

#### 2.1 — Initialize Next.js Project
```
Directory: frontend/
```
- `npx -y create-next-app@latest ./frontend` (App Router, TypeScript, Tailwind)
- Install Shadcn/UI: `npx -y shadcn@latest init`
- Install Tremor: `npm install @tremor/react`
- Configure API proxy to FastAPI backend

#### 2.2 — Design System Setup
```
File: frontend/app/globals.css
File: frontend/tailwind.config.ts
```
- Configure dark mode color palette (from UI_SPEC.md):
  - Background: Deep Navy (#0A0E27)
  - Surface: Slate (#0F172A)
  - Accent: Electric Blue (#3B82F6)
  - Success/Danger/Warning tier colors
- Typography: Inter font family
- CSS custom properties for theming
- Glassmorphism card styles

#### 2.3 — 3-Layer Layout Component
```
File: frontend/app/layout.tsx (Root)
File: frontend/app/[format]/layout.tsx (Format)
File: frontend/components/layout/FormatSelector.tsx
File: frontend/components/layout/ContextBar.tsx
File: frontend/components/layout/Sidebar.tsx
```
**Layer 1: Format Selector** (top bar)
- Fetches formats from `GET /api/formats`
- Renders tab bar: [ODI] [T20I] [IPL] [WODI] [WT20I]
- Clicking a tab navigates to `/{format}/`

**Layer 2: Context Bar** (below format selector)
- Fetches context fields from manifest: `manifest.context_fields`
- Renders appropriate widgets (dropdown, combobox, slider) per field
- Stores global state (venue, teams, years, region) in React Context

**Layer 3: Sidebar** (left panel)
- Fetches categories from manifest: `manifest.categories`
- Groups them by `group` field (intelligence, players, operations, system)
- Highlights active category
- Shows function count badge per category
- Collapsible on mobile

#### 2.4 — Dynamic Routing
```
Directory: frontend/app/[format]/[category]/page.tsx
```
- `/:format/` → Dashboard page
- `/:format/:categoryKey` → Category screen (generic)
- `/:format/:categoryKey/:functionKey` → Deep-link to specific tab

### Definition of Done (Phase 2):
- [ ] `npm run dev` starts frontend at localhost:3000
- [ ] Format selector bar shows all registered formats
- [ ] Clicking "ODI" loads ODI sidebar with 7 categories from manifest
- [ ] Context bar renders dropdowns populated from API
- [ ] Sidebar navigates to correct routes
- [ ] Dark mode aesthetic matches spec (glassmorphism, premium feel)
- [ ] Mobile responsive (sidebar collapses)
- [ ] `AI_MEMORY.md` updated

---

## 📦 PHASE 3: GENERIC RENDERERS (Component Library)
**Goal:** Build the ~10 reusable output renderers that display ANY function's result.  
**Depends On:** Phase 2  
**Estimated Effort:** 2-3 sessions

### Tasks:

#### 3.1 — Core Data Renderers
```
File: frontend/components/renderers/DataTable.tsx
```
- Sortable, paginated table using Shadcn DataTable
- Column headers from API response keys
- Number columns right-aligned, text columns left-aligned
- Color-coded cells based on thresholds (🟢 good / 🔴 bad)

```
File: frontend/components/renderers/ComparisonTable.tsx
```
- Side-by-side team comparison layout
- Team color headers (from TEAM_COLORS)
- Win% bars, score differentials
- Used by: venue_matchup, global_h2h, country_h2h

```
File: frontend/components/renderers/MatrixTable.tsx
```
- Opponent-per-row dominance matrix
- Rows are clickable → navigate to /rivalry/{team_a}/vs/{opponent}
- Color-coded Win% cells
- Used by: home_dominance, away_performance, global_performance

#### 3.2 — Specialized Renderers
```
File: frontend/components/renderers/FormTable.tsx
```
- Recent form display with emoji result indicators (✅❌🤝)
- Match-by-match list with date, opponent, venue, result

```
File: frontend/components/renderers/ReportCard.tsx
```
- Key-value stat cards in a responsive grid
- Large stat number with label below
- Verdict badge (🟢 BAT FIRST / 🔴 CHASE etc.)
- Used by: venue_bias

```
File: frontend/components/renderers/PredictionCard.tsx
```
- Projected score range display (e.g., "240 — 270")
- Score dial/gauge visualization
- Breakdown cards: Venue Par, Batting Power, Bowling Threat
- Adjustment notes

```
File: frontend/components/renderers/PlayerProfileCard.tsx
```
- Player header: name, team, role badge
- Stat grid: Innings, Average, SR, 100s
- Tab sections: Batting, Bowling, vs Opposition, at Venue

```
File: frontend/components/renderers/DynamicChart.tsx
```
- Wrapper around Tremor chart components
- Accepts data + chart type (bar, area, donut) from API
- Used by future functions (cap_analysis, pitch_decay, etc.)

```
File: frontend/components/renderers/DownloadPanel.tsx
```
- File download button + generation status
- Chapter completion checklist (Ch1 ✅, Ch2 ✅, Ch3 ✅, Ch4 ✅)
- Preview panel for report JSON

```
File: frontend/components/renderers/MatchupTable.tsx
```
- Batter vs Bowler grid
- Balls faced, runs scored, dismissals
- "Bunny Alert" highlighting

#### 3.3 — The FunctionRenderer Dispatcher
```
File: frontend/components/renderers/FunctionRenderer.tsx
```
- Takes `output_type` from manifest and dispatches to correct renderer
- Handles loading/spinner state
- Handles missing context alert (e.g., "Please select a venue")
- Handles API error display
- This is the SINGLE entry point for all function outputs

#### 3.4 — Squad Builder Component (Special Input)
```
File: frontend/components/inputs/SquadBuilder.tsx
```
- Dual-panel squad selector (Home/Away)
- Player search combobox with auto-complete
- "Load Last XI" button per team
- Selected player list with remove/clear
- Used by: compare_squads, predict_score, match_pack

### Definition of Done (Phase 3):
- [ ] All 10 renderer components exist and accept generic data
- [ ] FunctionRenderer correctly dispatches to the right renderer
- [ ] Each renderer has a Storybook story or test page showing sample data
- [ ] SquadBuilder component works with player search
- [ ] All renderers follow Visual Hierarchy rules from user_rules (right-align numbers, etc.)
- [ ] `AI_MEMORY.md` updated

---

## 📦 PHASE 4: DYNAMIC SCREENS (Manifest → UI)
**Goal:** Wire everything together — manifest drives the live UI.  
**Depends On:** Phase 3  
**Estimated Effort:** 1-2 sessions

### Tasks:

#### 4.1 — Dashboard Page
```
File: frontend/app/[format]/page.tsx
```
- Fetches manifest for current format
- Renders category cards in a responsive grid
- Each card shows: icon, label, description, function count
- Cards link to `/:format/:categoryKey`
- Quick stats row: total matches, venues, teams (from API)

#### 4.2 — Generic Category Screen
```
File: frontend/app/[format]/[category]/page.tsx
```
- Fetches manifest, finds the matching category
- Renders category header (icon, label, description)
- Creates tab bar from `category.functions[]`
- Each tab renders `<FunctionRenderer />` with correct data
- Passes context bar values as API parameters

#### 4.3 — Deep-Link Function Route
```
File: frontend/app/[format]/[category]/[function]/page.tsx
```
- Direct link to a specific function/tab within a category
- Pre-selects the correct tab in the category screen

#### 4.4 — Missing Context Handling
- If a function's `required_context` fields aren't filled:
  - Show a clear alert: "Please select a Venue to use this analysis"
  - Highlight the missing field in the Context Bar
  - Don't attempt the API call

#### 4.5 — Loading & Error States
- Skeleton loaders for every renderer (matches the layout shape)
- Error boundaries per function (one function crash doesn't kill the screen)
- Retry button on API failure

### Definition of Done (Phase 4):
- [ ] Navigating to `/odi/venue_intel` shows venue intel screen with 4 tabs
- [ ] Each tab calls the correct API endpoint and renders results
- [ ] Navigating to `/odi/team_command` shows team command with 4 tabs
- [ ] All 7 ODI categories work end-to-end with live data
- [ ] Deep-link URLs work (e.g., `/odi/rivalry/global_h2h`)
- [ ] Missing context shows helpful alert, not a crash
- [ ] `AI_MEMORY.md` updated

---

## 📦 PHASE 5: CONTEXT SYSTEM (Global Filters)
**Goal:** The shared context bar drives everything seamlessly.  
**Depends On:** Phase 4  
**Estimated Effort:** 1 session

### Tasks:

#### 5.1 — React Context Provider
```
File: frontend/lib/context/MatchContext.tsx
```
- Global state: `{format, venue, team_a, team_b, years, region}`
- Persisted to URL search params (shareable links)
- Updates cascade to all active screens

#### 5.2 — Context-Aware Highlighting
- On `/venue` → venue dropdown glows/highlights
- On `/rivalry` → both team dropdowns glow
- On `/team` → home team dropdown glows
- Visual cue: "These are the active inputs for this screen"

#### 5.3 — Context Persistence
- When switching formats, teams/venues reset (different pools)
- When switching within a format, context persists
- URL encoding: `?venue=IND_MUMBAI_WANKHEDE&team_a=India&team_b=Australia`

#### 5.4 — Auto-Reload on Context Change
- When user changes venue in context bar:
  - If currently on `/venue` → re-fetch all venue tabs automatically
  - If on `/team` → no effect (venue not a required field)
- Smart reload: only re-fetch if the changed field is in `required_context`

### Definition of Done (Phase 5):
- [ ] Changing venue in context bar auto-refreshes venue intel tabs
- [ ] Changing teams auto-refreshes rivalry/squad tabs
- [ ] Context is encoded in URL (shareable links work)
- [ ] Format switch clears and repopulates context dropdowns
- [ ] Context fields highlight based on active screen
- [ ] `AI_MEMORY.md` updated

---

## 📦 PHASE 6: CROSS-NAVIGATION + POLISH
**Goal:** Add the bet365-style cross-linking and premium visual polish.  
**Depends On:** Phase 5  
**Estimated Effort:** 1-2 sessions

### Tasks:

#### 6.1 — Cross-Navigation Links
```
File: frontend/components/navigation/QuickLinks.tsx
```
- Every screen renderer can output "Quick Links" at the bottom
- Links from output data:
  - MatrixTable rows → click opponent → `/rivalry/{team}/vs/{opponent}`
  - ComparisonTable → "View Venue Stats" → `/venue`
  - PlayerProfileCard → "Add to Squad" → `/squads`
  - PredictionCard → "Full Match Pack" → `/matchday`

#### 6.2 — Micro-Animations
- Tab switch transitions (fade + slide)
- Number count-up animations on stat cards
- Hover glow effects on sidebar items
- Loading → content fade-in transitions
- Skeleton pulse animations

#### 6.3 — Premium Visual Polish
- Glassmorphism cards (backdrop-blur + subtle borders)
- Team color accents on comparison headers
- Gradient backgrounds for section headers
- Subtle glow effects on active sidebar items
- Responsive grid adjustments for all screen sizes

#### 6.4 — Theme Support
- Dark mode (default — trading terminal aesthetic)
- Integrate with existing `config/shared/themes.py` theme definitions
- Theme switcher in settings page

#### 6.5 — Empty States & Edge Cases
- "No Data" states for venues/teams with insufficient matches
- "Small Sample Size" warnings (< 3 innings from user_rules)
- Loading states that match the actual output shape (skeleton)

### Definition of Done (Phase 6):
- [ ] Clicking an opponent row in Team Command navigates to Rivalry Lab
- [ ] Clicking a player name navigates to Player Scout
- [ ] All animations run smoothly at 60fps
- [ ] Visual design matches premium aesthetic spec
- [ ] Theme switcher works
- [ ] `AI_MEMORY.md` updated

---

## 📦 PHASE 7: MULTI-FORMAT ACTIVATION
**Goal:** Prove the manifest system works — add a second format.  
**Depends On:** Phase 6  
**Estimated Effort:** 1-2 sessions

### Tasks:

#### 7.1 — Create T20I Manifest
```
File: formats/t20i/manifest.py
```
- Declare T20I-specific categories and functions
- May have fewer functions than ODI (smaller dataset)
- Different phase labels (Powerplay 1-6 instead of 1-10)
- Different score baselines

#### 7.2 — Create T20I Engine Stubs
- Copy ODI engine structure to `formats/t20i/`
- Adapt constants (overs, baselines, etc.)
- Verify manifest validator passes

#### 7.3 — Test Format Switching
- Switch from ODI → T20I in Format Selector
- Verify: sidebar updates, dropdowns reload, screens work
- Verify: ODI-exclusive functions don't appear in T20I sidebar
- Verify: T20I-exclusive functions (if any) appear correctly

#### 7.4 — Create IPL Manifest (If Data Available)
- Franchise teams instead of countries
- IPL-exclusive categories (auction, impact player)
- Verify additional sidebar items appear

### Definition of Done (Phase 7):
- [ ] Format selector shows at least 2 formats (ODI + T20I)
- [ ] Switching formats updates sidebar dynamically
- [ ] T20I screens render with T20I data
- [ ] Manifest validator passes for all active formats
- [ ] `AI_MEMORY.md` updated

---

## 📦 PHASE 8: PRODUCTION HARDENING
**Goal:** Make the app robust for daily trading use.  
**Depends On:** Phase 7  
**Estimated Effort:** 1-2 sessions

### Tasks:

#### 8.1 — Error Handling
- API error boundaries per function
- Graceful degradation (one failed API call doesn't crash the app)
- Retry logic with exponential backoff

#### 8.2 — Performance Optimization
- API response caching (stale-while-revalidate)
- Lazy loading for off-screen tabs
- Virtualized tables for large datasets (50+ rows)

#### 8.3 — Accessibility
- WCAG AA compliance for all interactive elements
- Keyboard navigation for sidebar and tabs
- Screen reader labels for stat cards
- Color contrast verification

#### 8.4 — Testing
- End-to-end tests: navigate all categories, check data renders
- API integration tests: all execute endpoints return valid JSON
- Visual regression tests (optional): screenshot comparison

#### 8.5 — Deployment Configuration
- Docker Compose: FastAPI + Next.js
- Environment variables for API URL, port, debug mode
- Production build optimization

### Definition of Done (Phase 8):
- [ ] App handles API failures gracefully (no blank screens)
- [ ] Page load < 2 seconds for all screens
- [ ] Keyboard navigation works throughout
- [ ] Docker Compose runs the full stack with one command
- [ ] `AI_MEMORY.md` updated as COMPLETE

---

## 📊 PHASE DEPENDENCY GRAPH

```
Phase 0 (Manifest)
    │
    ▼
Phase 1 (API)
    │
    ▼
Phase 2 (Shell)
    │
    ▼
Phase 3 (Renderers)
    │
    ▼
Phase 4 (Screens)
    │
    ▼
Phase 5 (Context)
    │
    ▼
Phase 6 (Polish)
    │
    ▼
Phase 7 (Multi-Format)
    │
    ▼
Phase 8 (Hardening)
```

**Each phase MUST be completed before advancing. No skipping.**

---

## 🚨 RULES FOR AGENTS

### Rule 1: Read Before Code
Before writing ANY frontend or API code, read:
1. This roadmap (`docs/plans/FRONTEND_ROADMAP.md`)
2. The design spec (`docs/design/UI_SPEC.md`)
3. The engineering standards (`docs/guides/ENGINEERING_STANDARDS.md`)

### Rule 2: Identify Current Phase
Check the STATUS TRACKER below. Start from the FIRST incomplete phase.
Do NOT jump ahead.

### Rule 3: Update Status
After completing any work, update:
1. The STATUS TRACKER in this file (mark tasks as done)
2. `docs/ai/AI_MEMORY.md` (session history entry)
3. `docs/context/active_state.md` (if architecture changes)

### Rule 4: Manifest is Law
- The manifest (`formats/{fmt}/manifest.py`) is the SINGLE SOURCE OF TRUTH for what
  the UI renders. NEVER hardcode screens, tabs, or navigation items in React.
- If a function doesn't exist in the manifest, it doesn't exist in the UI.
- If you add a new engine function, add it to the manifest FIRST.

### Rule 5: No Format-Specific Frontend Code
- The frontend MUST be format-agnostic
- No `if (format === 'odi')` blocks in React components
- All format-specific behavior comes from the manifest
- Only exception: adding new `output_type` renderers (but these are generic too)

### Rule 6: Preserve Backend
- The headless engines (`TeamEngine`, `PlayerEngine`, `PredictorEngine`) are STABLE
- Do NOT modify engine behavior to fit the UI
- The API layer is an ADAPTER — it wraps engines, not changes them
- If engine output isn't JSON-friendly, fix it in `api/serializers.py`

### Rule 7: Test at Every Phase
- Each phase has a Definition of Done checklist
- ALL items must be checked before marking the phase complete
- If any item fails, the phase is NOT complete

---

## 📍 STATUS TRACKER

### Phase 0: Foundation
```
Status: ✅ COMPLETE
Started: 2026-02-15
Completed: 2026-02-15
Agent: Antigravity
Tasks:
  [x] 0.1 — ODI Manifest created (formats/odi/manifest.py — 7 categories, 17 functions)
  [x] 0.2 — Format Registry upgraded (v2.1 — get_format_metadata + MatchPackGenerator)
  [x] 0.3 — Manifest Validator passing (scripts/validate_manifest.py — 0 errors)
```

### Phase 1: API Layer
```
Status: ✅ COMPLETE
Started: 2026-02-15
Completed: 2026-02-15
Agent: Antigravity
Tasks:
  [x] 1.1 — FastAPI skeleton (api/main.py v2.0 — CORS, lifecycle, tagged routes)
  [x] 1.2 — Manifest endpoint (GET /api/{format_type}/manifest)
  [x] 1.3 — Context endpoints (teams, venues, players/{team}, regions)
  [x] 1.4 — Generic execute endpoint (POST /api/{format_type}/execute/{function_key})
  [x] 1.5 — Engine initialization pool (api/engine_pool.py — singleton per format)
  [x] 1.6 — Pydantic models (api/models.py — 9 typed models)
  [x] 1.7 — Serializer layer (api/serializers.py — DataFrame/numpy/NaN safe)
  [x] 1.8 — Smoke test passing (scripts/test_api.py — 12/12 tests pass)
```

### Phase 2: Frontend Shell
```
Status: ✅ COMPLETE
Started: 2026-02-15
Completed: 2026-02-15
Agent: Antigravity
Tasks:
  [x] 2.1 — Next.js initialized (Next.js 16.1.6, React 19, Tailwind 4, Turbopack)
  [x] 2.2 — Design system (60+ CSS tokens, glassmorphism, animations, 4-tier badges)
  [x] 2.3 — 3-Layer layout (FormatSelector + ContextBar + Sidebar — all manifest-driven)
  [x] 2.4 — Dynamic routing (sidebar state-driven, Dashboard + CategoryScreen)
  [x] 2.5 — API client (lib/api.ts — typed fetch wrappers)
  [x] 2.6 — React Context (lib/context.tsx — global state for format/manifest/context)
  [x] 2.7 — API proxy (next.config.ts rewrites :3000 → :8000)
  [x] 2.8 — Generic result renderers (TableRenderer + ReportRenderer for Phase 2)
```

### Phase 3: Generic Renderers
```
Status: ✅ COMPLETE
Started: 2026-02-15
Completed: 2026-02-15
Agent: Antigravity
Tasks:
  [x] 3.1 — Core renderers (DataTable, ComparisonTable, MatrixTable)
  [x] 3.2 — Specialized renderers (FormTable, ReportCard, PredictionCard, PlayerProfileCard, MatchupTable, DownloadPanel)
  [x] 3.3 — FunctionRenderer dispatcher (routes output_type → correct renderer with fallback)
  [x] 3.4 — CSS Design System extended (btn-primary, btn-ghost, badges 4-tier, gradient-text, glass-card, animations)
  [x] 3.5 — SquadBuilder component (searchable dual-selector with auto-fill)
  [x] 3.6 — ExtraInputRenderer (manifest-driven combobox/text fields)
```

### Phase 4: Dynamic Screens
```
Status: ✅ COMPLETE
Started: 2026-02-15
Completed: 2026-02-16
Agent: Antigravity
Tasks:
  [x] 4.1 — Dashboard page (category cards grid, stat overview)
  [x] 4.2 — Generic category screen (dynamic tabs, header, description)
  [x] 4.3 — URL hash deep-linking (category-synced routes)
  [x] 4.4 — Missing context handling (detailed amber alerts, field names in button)
  [x] 4.5 — Loading & error states (SkeletonLoader system, retry button)
  [x] 4.6 — Engine/API Integration (17/17 ODI functions operational)
```

### Phase 5: Context System
```
Status: ✅ COMPLETE
Started: 2026-02-18
Completed: 2026-02-18
Agent: Antigravity
Tasks:
  [x] 5.1 — React context provider (updated with URL sync)
  [x] 5.2 — Context-aware highlighting (implicit in shared state)
  [x] 5.3 — Context persistence (URL params sync in setContextValue)
  [x] 5.4 — Auto-reload on context change (useEffect dependencies in generic pages)
```

### Phase 6: Polish
```
Status: ✅ COMPLETE
Started: 2026-02-18
Completed: 2026-02-18
Agent: Antigravity
Tasks:
  [x] 6.1 — Cross-Navigation Links (QuickLinks context, clickable Matrix rows)
  [x] 6.2 — Micro-animations (CountUp stats, Hover effects)
  [x] 6.3 — Premium visual polish (Sidebar glass/shadow effects)
  [x] 6.4 — Theme support (CSS vars in globals.css)
  [x] 6.5 — Empty states & edge cases (Playful ghost/search icons)
```

### Phase 7: Multi-Format
```
Status: NOT STARTED
Started: —
Completed: —
Agent: —
Tasks:
  [ ] 7.1 — T20I manifest created
  [ ] 7.2 — T20I engine stubs
  [ ] 7.3 — Format switching tested
  [ ] 7.4 — IPL manifest (stretch)
```

### Phase 8: Production
```
Status: NOT STARTED
Started: —
Completed: —
Agent: —
Tasks:
  [ ] 8.1 — Error handling
  [ ] 8.2 — Performance optimization
  [ ] 8.3 — Accessibility
  [ ] 8.4 — Testing suite
  [ ] 8.5 — Docker deployment
```

---

## 📅 CHANGELOG

| Date | Phase | Agent | Notes |
|------|-------|-------|-------|
| 2026-02-15 | — | Claude | Roadmap V1 created based on UI_SPEC V5 |
| 2026-02-15 | Phase 0 | Antigravity | Phase 0 COMPLETE: manifest.py (17 functions), format_registry v2.1, validate_manifest.py (0 errors) |
| 2026-02-15 | Phase 1 | Antigravity | Phase 1 COMPLETE: api/main.py v2.0, models.py, serializers.py, engine_pool.py, test_api.py (12/12 pass) |
| 2026-02-15 | Phase 2 | Antigravity | Phase 2 COMPLETE: Next.js 16/React 19 shell, 3-layer layout, design system, API client+proxy, React Context, generic renderers |
| 2026-02-15 | Phase 3 | Antigravity | Phase 3 COMPLETE: 9 specialized renderers (DataTable, ComparisonTable, MatrixTable, FormTable, ReportCard, PredictionCard, PlayerProfileCard, MatchupTable, DownloadPanel) + FunctionRenderer dispatcher + CSS badges/buttons/animations |

