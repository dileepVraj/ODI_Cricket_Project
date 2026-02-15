# Gap Analysis & Strategic Roadmap (Phase 3)

**Date:** 2026-02-15
**Focus:** Database Integration & Architecture Standardization

## 1. The Current State: "Hybrid Architecture"
The application currently operates in a hybrid state between a **File-Based System** and a **Database System**.

### A. The Pipeline (Modern) ✅
The `scripts/update_data.py` pipeline is fully modernized:
1.  **Ingests** raw JSON.
2.  **Refines** data using `refinery_script.py`.
3.  **Stores** structured data in `odi.duckdb` (DuckDB).
4.  **Verifies** logic using the Truth Bridge.

### B. The Engine (Legacy/Hybrid) ⚠️
The `CricketAnalyzer` engine, however, relies on **In-Memory Pandas DataFrames**:
*   It loads `FINAL_ODI_MASTER.csv` (or its `.pkl` cache) into RAM.
*   It performs vectorized operations using Pandas, not SQL.
*   **Why?** Speed. For the specific "Iterative Filtering" used in the Dashboard (e.g., "Last 5 years, in India, vs Australia"), Pandas in-memory slicing (<50ms) beats disk-based SQL queries (>200ms) for datasets under 2GB.

## 2. Identified Gaps

### GAP-1: The "Dual Truth" Problem
*   **Issue:** We have both `odi.duckdb` and `FINAL_ODI_MASTER.csv`. If the CSV generation fails but DB ingestion succeeds (or vice versa), the Dashboard and the DB will show different stats.
*   **Mitigation:** The `update_data.py` pipeline runs both sequentially. If one fails, the script exits.

### GAP-2: Memory Scalability
*   **Issue:** The current approach loads the *entire* history into RAM.
    *   **Current Size:** ~1.3 Million balls (~150MB RAM).
    *   **Limit:** This will work fine until ~10 Million balls (~1.5GB RAM).
*   **Risk:** Low for ODIs. Medium for T20s (if added). High for Test Cricket.

### GAP-3: Facade Complexity (Self-Healing)
*   **Observation:** The `engine.py` now contains complex logic to "scout" for data files (`data/` vs `formats/odi/data/`).
*   **Recommendation:** This usage of "Magic Paths" should be deprecated in Phase 4 in favor of a strict `config.settings.DATA_PATH` constant.

## 3. Strategic Roadmap (Phase 4 & Beyond)

### Phase 4: The "Lazy Loader" (Future)
**Objective:** Transition `CricketAnalyzer` to read directly from `odi.duckdb`.

**Strategy:**
1.  **Replace** `self.match_df = pd.read_csv(...)` with `self.con = duckdb.connect('odi.duckdb')`.
2.  **Refactor** `TeamEngine` to use SQL Aggregations:
    *   *Old:* `df[df['team']=='India'].runs.sum()`
    *   *New:* `con.execute("SELECT SUM(runs) FROM plays WHERE team='India'").fetchone()`
3.  **Benefit:** Zero RAM startup time. Infinite scalability.
4.  **Cost:** Significant refactor of `team_engine.py` and `player_engine.py`.

## 4. Conclusion
The current "CSV-based In-Memory Engine" is a **deliberate architectural choice** for performance and rapid iteration. It is **not a bug**. However, as the dataset grows, migrating to the DuckDB-backed engine (Phase 4) will become necessary for scalability.
