# PROJECT_CONTEXT.md (SLIM)
**Purpose:** Claude Projects Knowledge Base - Core Architecture & Active Sprint State.
**Last Updated:** 2026-03-16
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
1. **TASK-137:** Suppress team_b→opp_team global mapping for analyze_squad_types in ParamMapperService to fix Tactical Matrix runtime error.
2. **TASK-136:** Added SquadComparisonCard renderer for output_type "squad_comparison" — displays squad metrics comparison and per-team player stats tables; wired into FunctionRenderer and SkeletonLoader.
3. **TASK-135:** Slimmed compare_squads to squad-metrics only — removed tactical matrix and matchup computation from get_squad_comparison_data; deleted GlobalCompareEnvelope serialization layer; output_type set to "squad_comparison".
4. **TASK-134:** Squad Battle now uses a single combobox search field per team panel, with `AccessibleCombobox` owning all player filtering and `SquadBuilder.tsx` no longer duplicating that search state.
5. **TASK-133:** `get_last_match_xi()` now supplements short `is_playing_xi=True` squads with remaining same-match rows ordered by `player_order`, preventing compare-squad XI padding from injecting historical ghost players while keeping the balls fallback unchanged.

---
*Archived history (TASK-001 to TASK-105) moved to ARCHIVE_HISTORY.md.*
