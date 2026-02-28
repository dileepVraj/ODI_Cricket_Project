# Phase 4 Fix Plan — All Functions Working Correctly

## Status: 🟢 IMPLEMENTED + BUILD VERIFIED

## Issues Found (9 total)

### 🔴 Critical (Function broken/unusable)

| # | Function | Issue | Root Cause |
|---|----------|-------|------------|
| 1 | `country_h2h` | Always returns empty | Region dropdown sends "Asia"/"Europe" but engine expects country names like "India" |
| 2 | `venue_phases` | Renders nothing useful | Engine returns nested Dict but output_type="table" expects List[Dict] |
| 3 | `venue_phases` | Missing away team data | team_b not in required_context + wrong param mapping (opp_team vs away_team) |

### 🟡 Major (Function works but data incomplete)

| # | Function | Issue | Root Cause |
|---|----------|-------|------------|
| 4 | ALL report fns | No match audit table | Engine returns MATCH_IDS but not raw match records |
| 5 | `venue_bias` | Match records hidden | raw_matches in data but ReportCard hides it |
| 6 | `continent_perf` | Can't pass team_b | Frontend only sends required_context params; team_b not included |

### 🟢 Minor (Enhancement)

| # | Function | Issue | Root Cause |
|---|----------|-------|------------|
| 7 | All context | Optional params lost | Frontend only sends required_context; useful optional values dropped |

---

## Fix Execution Order

### Fix 1: API `_map_params` — country_h2h + venue_phases
**File:** `api/main.py`
- country_h2h: Use team_a as country_name (team = country in cricket)
- venue_phases: Map team_b → `away_team` (not `opp_team`)

### Fix 2: Manifest updates
**File:** `formats/odi/manifest.py`
- country_h2h: Remove `region` from required_context
- venue_phases: Add `team_b` to required_context  
- venue_phases: Change output_type to `"phase_analysis"`

### Fix 3: Frontend — Send all context values
**File:** `frontend/app/page.tsx`
- Send all filled context values, not just required_context ones
- API filtering handles the rest

### Fix 4: PhaseAnalysisCard renderer
**File:** `frontend/components/renderers/PhaseAnalysisCard.tsx` (NEW)
- Handles nested dict from venue_phases engine
- Shows: Venue Baseline → Home Team → Away Team → Global Habits tables

### Fix 5: FunctionRenderer dispatch update
**File:** `frontend/components/renderers/FunctionRenderer.tsx`
- Add `"phase_analysis"` → PhaseAnalysisCard route

### Fix 6: Match Audit Enrichment (API)
**File:** `api/main.py`
- After engine call, extract MATCH_IDS from result
- Fetch raw match records from analyzer.match_df
- Return enriched response with `match_audit` field

### Fix 7: Match Audit Display (Renderers)
**Files:** `ReportCard.tsx`, `ComparisonTable.tsx`, `MatrixTable.tsx`
- Detect `match_audit` or `raw_matches` in data
- Render as a table below main content

### Fix 8: API optional_keys expansion
**File:** `api/main.py`
- Add `team_a`, `team_b`, `venue`, `years`, `region` to optional_keys
- Ensures optional params pass through filtering
