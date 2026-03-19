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
1. **TASK-144:** MatchupTable restructured with split two-column layout, legend strip, batter danger summary, and computeThreatRating() helper.
2. **TASK-143:** SquadBuilder redesigned with compact collapsed chip bar; auto-collapse when squads loaded, expand to full layout on click.
3. **TASK-142:** Visual polish on MatchupTable card layout; explicit RGB for contrast, SR fallback lookup, and BUNNY tag styling refined.
4. **TASK-141:** Rewrite MatchupTable as batter-grouped card layout; advantage bar and bunny tags driven by pre-computed API signals.
5. **TASK-140:** Gemini CLI MCP config created — filesystem, context7, playwright, sequential-thinking registered in .gemini/settings.json

---
*Archived history (TASK-001 to TASK-105) moved to ARCHIVE_HISTORY.md.*
