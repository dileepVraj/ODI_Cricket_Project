# PROJECT_CONTEXT.md (SLIM)
**Purpose:** Claude Projects Knowledge Base - Core Architecture & Active Sprint State.
**Last Updated:** 2026-03-18
**Project:** Vantage | Strategic Algo Exchange (Cricket)

---

## 1. ARCHITECTURAL MAP
**Stack:** FastAPI (Python) | Next.js 14 (TS) | DuckDB | Supabase.
**Core Pattern:** Manifest-driven engine system. Each format (ODI, etc.) defines logic/outputs via a central manifest.

### 1.1 Load-Bearing Files (Do Not Delete)
| File | Role |
|------|------|
| `core/data_access.py` | CRITICAL - DAL for all engines. |
| `core/team_engine.py` | Strategy loader for format-specific logic. |
| `api/serializers.py` | High-Impact - Global API response mapping. |
| `frontend/lib/api.ts` | Centralized fetch wrapper (ApiClientError). |

---

## 2. ACTIVE ENGINEERING STANDARDS
Refer to the following files for full rules. Do not hallucinate patterns.
* **Core:** `docs/guides/ENGINEERING_STANDARDS_CORE.md`
* **Backend:** `docs/guides/ENGINEERING_STANDARDS_BACKEND.md` (6 Gates)
* **Frontend:** `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md` (38 Rules, 3 Gates)
* **Protocol:** `docs/ai/TASK_PROTOCOL.md` (Mandatory Task Routing)

### 2.1 Essential Constraints
- **Gate 6 (Bouncer):** Must pass `python core/utils/compliance_bouncer.py` before every commit.
- **Visual Silence:** No UI strings or colors in `core/`.
- **Type Truth:** No `Any` or `object` in signatures. Use `TypedDict` for contracts.

---

## 3. CURRENT SPRINT STATE
**Phase:** Phase 10 (Engine Refactoring) COMPLETE. Phase 11 (Calculators) ACTIVE.
**Recent Milestone:** MatrixTable UI and Backend integrated with jersey-color support (2026-03-13).

### 3.1 Active Context Summary
- **Frontend:** Next.js 14 App Router. Uses a 3-layer layout (Format -> Context -> Sidebar).
- **Branding:** Renamed to "Vantage." Cascadia Code is the default UI font.
- **Bugs:** - (None currently listed as blockers).

---

## 4. RECENT ARCHITECTURAL DECISIONS (Last 5)
1. **TASK-161:** Add 7 venue bias enrichment helpers to venue_calculator.py (Wilson CI, sample reliability, score stats/distribution/extremes, bias trend, toss intelligence)
2. **TASK-160:** VenueBiasReport extended with 6 enrichment TypedDicts (CI, score stats/distribution/extremes, bias trend, toss intelligence) â€” Phase A of analyze_venue_bias overhaul.
3. **TASK-159:** Player Matchups complete redesign â€” Concept C Dossier layout: batter chips bar, 2-col card grid, all 47 backend fields surfaced (phase mini-tables, innings splits, confidence blocks, dismissal breakdown, venue badge).
4. **TASK-158:** Engine upgrade â€” MatchCount/BoundaryRate/DotBallRate added to _aggregate_matchup_window; Inn1/Inn2 innings split via _build_innings_stats; VenueFiltered bool param; IsBunny removed; ConfigurationError on missing required cols.
5. **TASK-157:** Schema cleanup â€” removed 4 dead fields from MatchupStatsSchema, added 17 new matchup stat fields; directional mask + venue_id passthrough in context_builder; venue optional_context in matchups manifest function.

---
*Archived history (TASK-001 to TASK-105) moved to ARCHIVE_HISTORY.md.*
