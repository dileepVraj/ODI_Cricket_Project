# 🛠️ Architecture Repair Plan — "The Cleanup"

**Date:** 2026-02-18
**Status:** ✅ COMPLETE
**Objective:** Fix critical bug causing incorrect High Scores, remove dangerous monkey-patching in API, and harden Engine logic against fuzzy inputs.

---

## 🚨 Critical Issues to Fix

### 1. The "High Score" Bug (Functional Correctness)
*   **Location:** `core/data_access.py` :: `get_player_stats_batch`
*   **Bug:** `MAX(runs_off_bat)` returns the max runs *per ball* (e.g. 6), not *per inning*.
*   **Fix:** Rewrite SQL query to aggregate runs by `(striker, match_id)` first, then take the MAX of those sums.

### 2. The "Monkey Patching" Violation (Architectural Integrity)
*   **Location:** `api/main.py` :: `execute_function`
*   **Violation:** Dynamically patching `dal.get_phase_stats` inside a request handler is fragile and unsafe.
*   **Fix:**
    1.  Modify `formats/odi/engines/team_engine.py` :: `analyze_venue_phases`.
    2.  Explicitly call `TeamService.ensure_phase_total_runs(df)` inside the engine after fetching data.
    3.  Remove the patching logic from `api/main.py`.

### 3. The "Fuzzy Logic" Leak (Domain purity)
*   **Location:** `formats/odi/engines/player_engine.py` :: `get_player_profile`
*   **Violation:** Engines doing `if name in str(p)` is non-deterministic and hides dirty data.
*   **Fix:** Remove fuzzy matching. Engines require exact names. Search/Lookup is a UI/Service responsibility (already handled by `ParamMapper` or `Context` endpoints).

---

## 📅 Execution Steps

1.  **Fix High Score Query** (`core/data_access.py`)
    *   Replace `MAX(runs_off_bat)` with a subquery/CTE approach.
    *   Verify output.

2.  **Refactor Team Engine** (`formats/odi/engines/team_engine.py`)
    *   Import `TeamService`.
    *   In `analyze_venue_phases`, normalize the DataFrame returned by `self.dal.get_phase_stats()`.

3.  **Clean up API Controller** (`api/main.py`)
    *   Remove the `if engine_method_name == "analyze_venue_phases":` block and the monkey-patching context manager.

4.  **Harden Player Engine** (`formats/odi/engines/player_engine.py`)
    *   Delete the fuzzy matching block in `get_player_profile`.
    *   Return `None` immediately if player not found in `self.player_df`.

5.  **Verification**
    *   Run API tests to ensure `venue_phases` still works.
    *   Verify Player Profile generation.
