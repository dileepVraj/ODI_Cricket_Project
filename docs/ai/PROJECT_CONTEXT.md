# PROJECT_CONTEXT.md (SLIM)
**Purpose:** Claude Projects Knowledge Base - Core Architecture & Active Sprint State.
**Last Updated:** 2026-03-15
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
1. **TASK-129:** Player profile now adds Bowling Intel as a third execute path, with venue-aware phase bowling metrics and parsed last-10 wicket chips flowing from engine/interface/schema to the renderer.
2. **TASK-128:** Player profile phase runs now derive from venue-filtered `raw_bat_ground`; redundant `phase_runs_raw` contract removed from the engine, interface, and schema layers.
3. **TASK-127:** Player profile redesigned - venue combobox + years text input replace host country dropdown; dual Profile/Batting Intel buttons replace single execute; `_view` injection drives conditional rendering.
4. **TASK-125:** PlayerProfileCard "Batting Intel" toggle panel added - phase runs table, vs-style CSS bar chart, last_10_runs sparkline chips.
5. **TASK-124:** analyze_player_profile enriched with phase-wise runs, vs-bowling-style breakdown, and last_10_runs numeric field; country pre-filter applied at context_builder layer.

---
*Archived history (TASK-001 to TASK-105) moved to ARCHIVE_HISTORY.md.*
