# 🏗️ ARCHITECTURE REDEVELOPMENT PLAN — "The Clean Break"
**Date:** 2026-02-18  
**Last Updated:** 2026-02-18 (Phase 2 Complete)  
**Objective:** Transition from a prototype "Monolithic Script" to an industry-standard "Layered Service Architecture".

---

## 📊 STATUS TRACKER

| Phase | Name | Status | Date Completed |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Data Foundation (DuckDB SSOT) | ✅ COMPLETE | 2026-02-18 |
| **Phase 1a** | CSV Graveyard Cleanup | ✅ COMPLETE | 2026-02-18 |
| **Phase 2** | Kill raw_df (Per-Query SQL) | ✅ COMPLETE | 2026-02-18 |
| **Phase 3** | Service Layer Extraction | ✅ COMPLETE | 2026-02-18 |
| **Phase 4** | API Controller Cleanup | ✅ COMPLETE | 2026-02-18 |
| **Phase 5** | Advanced Serialization | ✅ COMPLETE | 2026-02-18 |

---

## 🛑 1. The Problem We're Solving

### Before Phase 1 (The Old World)
```
Startup: JSON → CSV (174MB) → Pickle Cache (174MB) → RAM → Pandas DataFrame  
         ↳ 6-10s startup, 350MB RAM, fragile file paths
```

### After Phase 1 (Current State ✅)
```
Pipeline:  JSON → json_converter → CSVs → refinery_script → ingest_to_db → odi.duckdb (17MB)
Runtime:   odi.duckdb → DataAccess Layer → DataFrames → Engines
           ↳ ~5s startup, DuckDB as single source of truth
```

### Remaining Issues
1. **Dead files** — 350MB of CSV/pickle files still sitting in `/data` (Phase 1a)
2. **raw_df hog** — 1.3M ball rows still loaded into RAM at startup for PlayerEngine/PredictorEngine (Phase 2)
3. **God Adapter** — `api/main.py` is 1,020 lines of tangled logic (Phase 3/4)

---

## 🎯 2. Target Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│  api/main.py (~200 lines)                                       │
│  Routes → Validate → Dispatch to Service                        │
├─────────────────────────────────────────────────────────────────┤
│                     SERVICE LAYER                                │
│  core/services/team_service.py                                  │
│  core/services/player_service.py                                │
│  core/services/predictor_service.py                             │
│  Orchestration, param mapping, data enrichment                  │
├─────────────────────────────────────────────────────────────────┤
│                     DOMAIN LAYER (Engines)                       │
│  formats/odi/engines/team_engine.py                             │
│  formats/odi/engines/player_engine.py                           │
│  formats/odi/engines/predictor_engine.py                        │
│  Pure cricket math. No I/O. Receive data, return results.       │
├─────────────────────────────────────────────────────────────────┤
│                     DATA ACCESS LAYER                            │
│  core/data_access.py → DuckDB (odi.duckdb)                     │
│  SQL queries. Returns DataFrames. Single source of truth.       │
└─────────────────────────────────────────────────────────────────┘
```

| Layer | Responsibility | Current Status |
| :--- | :--- | :--- |
| **Presentation (API)** | Routes, Auth, Validation | ⚠️ Bloated (1,020 lines) |
| **Service Layer** | Business Logic, Orchestration | ❌ Missing (logic in API) |
| **Domain (Engines)** | Pure Cricket Math / Rules | ✅ Good (stable) |
| **Data Access (DAL)** | SQL Queries (DuckDB) | ✅ Active (single source of truth) |

---

## 📅 3. Implementation Plan (Detailed)

---

### Phase 1: Data Foundation (DuckDB SSOT) ✅ COMPLETE
**Completed:** 2026-02-18

**What was done:**
- `engine.py` → v5.0: Removed `_load_from_csv()`, `_create_match_summary()`, `load_csv_or_pickle` import
- `core/data_loader.py` → `create_data_source()` returns `DataAccess` only (no CSV fallback)
- `team_engine.py` → Removed CSV fallback in `analyze_venue_phases()`
- `api/main.py` → Removed `load_csv_or_pickle` monkey-patching and CSV retry fallback

**Verification:**
- Data integrity audit: CSV vs DuckDB → IDENTICAL (1,333,213 rows, 1,061,676 runs, 36,425 wickets)
- 17/17 API endpoints pass
- 6/6 engine function tests pass

---

### Phase 1a: CSV Graveyard Cleanup ⬜ READY
**Objective:** Delete dead CSV/pickle files from `/data`. They are build artifacts, not runtime dependencies.
**Time:** ~2 minutes
**Risk:** NONE (data is in DuckDB)

**Files to delete:**
| File | Size | Why it's dead |
| :--- | :--- | :--- |
| `FINAL_ODI_MASTER.csv` | 167 MB | Replaced by `balls` table in DuckDB |
| `FINAL_ODI_MASTER.pkl` | 174 MB | Pickle cache of above CSV |
| `MATCH_INFO.csv` | 229 KB | Merged into `matches` table |
| `MATCH_SQUADS.csv` | 2.2 MB | Replaced by `squads` table |
| `processed_player_stats.csv` | 1.2 MB | Replaced by `player_stats` table |
| `processed_phase_stats.csv` | 426 KB | Replaced by `phase_stats` table |
| `processed_phase_stats.pkl` | 485 KB | Pickle cache of above |
| `player_metadata.csv` | 45 KB | Replaced by `player_metadata` table |
| **TOTAL** | **~345 MB** | |

**Files to KEEP:**
- `odi.duckdb` (17MB) — THE database
- `json_source/` (2,513 JSON files) — Raw source data from Cricsheet

**Pipeline impact:**
- `scripts/update_data.py` still generates CSVs as intermediates during `json_converter.py → refinery_script.py → ingest_to_db.py`
- These CSVs are recreated every pipeline run, so deleting them now is safe
- Future improvement: modify pipeline to go `JSON → DuckDB` directly (eliminates intermediates entirely)

---

### Phase 2: Kill `raw_df` (Per-Query SQL) ✅ COMPLETE
**Objective:** Eliminate the 1.3M row `raw_df` DataFrame loaded at startup.
**Time:** ~1-2 hours
**Risk:** MEDIUM (engines depend on raw_df for filtering)

**Current problem:**
```python
# engine.py — loads ALL 1.3M balls into RAM
self.raw_df = dal.con.execute("SELECT * FROM balls").df()  # ~300MB RAM, ~3s
```

**Why it exists:** `PlayerEngine` and `PredictorEngine` were built to filter a pre-loaded DataFrame.
They do operations like:
```python
player_data = self.raw_df[self.raw_df['striker'] == player_name]
venue_data = self.raw_df[self.raw_df['venue'] == venue]
```

**The fix:** Replace these DataFrame filter patterns with DAL SQL queries:
```python
# BEFORE (RAM scan)
player_data = self.raw_df[self.raw_df['striker'] == player_name]

# AFTER (SQL push-down)
player_data = self.dal.get_balls(striker=player_name)
```

**Step-by-step:**
1. **Audit `PlayerEngine`**: Find every reference to `self.raw_df` and catalog the filter patterns
2. **Audit `PredictorEngine`**: Same audit
3. **Add missing DAL methods**: `get_balls()` already supports most filters. Add any missing ones.
4. **Refactor hot methods**: Replace DataFrame filters with DAL calls, one method at a time
5. **Remove `raw_df` from `engine.py`**: Once no engine references it, delete the load
6. **Verify**: Run all 17 API tests, compare outputs to pre-refactor baseline

**Expected gains:**
- Startup: ~5s → <1s (no 1.3M row load)
- RAM: ~350MB → ~50MB
- Per-query: Faster (DuckDB columnar scan vs Pandas full-table scan)

**Constraint:** `raw_df` is also passed to `PredictorEngine(raw_df, player_df)`. This constructor signature
must be updated to accept `dal` instead.

---

### Phase 3: Service Layer Extraction ✅ COMPLETE
**Objective:** Move business logic out of `api/main.py` into proper service classes.
**Time:** ~2-3 hours
**Risk:** LOW (pure refactor, no behavior change)

**Current problem:** `api/main.py` is 1,020 lines because it contains:

| Function | Lines | What it does | Where it should live |
| :--- | :--- | :--- | :--- |
| `_map_params()` | 225 | Parameter aliasing (team_a→home_team, etc.) | `core/services/param_mapper.py` |
| `_enrich_with_match_audit()` | 160 | Attaches match records to engine output | `core/services/enrichment.py` |
| `_build_compare_squads_table()` | 45 | Flattens squad comparison output | `core/services/serializers.py` |
| `_build_player_venue_stats_fallback()` | 85 | Computes venue batting stats from raw data | `core/services/player_service.py` |
| `_ensure_phase_total_runs()` | 17 | Normalizes phase stats | `core/services/team_service.py` |
| `execute_function()` (core) | ~120 | Engine dispatch + error handling | Stays in `api/main.py` |

**Step-by-step:**
1. **Create** `core/services/__init__.py`
2. **Extract** `_map_params` → `core/services/param_mapper.py`
3. **Extract** `_enrich_with_match_audit` → `core/services/enrichment.py`
4. **Extract** squad/player adapters → `core/services/player_service.py`
5. **Extract** phase stats normalization → `core/services/team_service.py`
6. **Slim down** `execute_function()` to: validate → map params → call service → return
7. **Verify**: All 17 API tests pass with identical output

**Expected result:** `api/main.py` drops from 1,020 → ~300 lines.

---

### Phase 4: API Controller Cleanup ✅ COMPLETE
**Objective:** Final polish on the API layer.
**Time:** ~1 hour
**Risk:** LOW
**Depends on:** Phase 3

**Tasks:**
1. **Pydantic request/response models**: Add strict validation schemas for each engine function
2. **Remove `sys.modules` hacking**: Clean up the engine resolution logic
3. **Standardize error responses**: All errors return consistent JSON
4. **API versioning**: Prepare for `/api/v2/` migration if needed
5. **Documentation**: Auto-generate OpenAPI docs from Pydantic models

---

## 🏗️ 4. Files Reference

### Core Runtime Files
| File | Role | Status |
| :--- | :--- | :--- |
| `engine.py` | Facade — initializes DAL + engines | ✅ v5.0 (DuckDB-only) |
| `core/data_access.py` | DAL — SQL queries → DataFrames | ✅ Active |
| `core/data_loader.py` | Factory for DataAccess + pipeline CSV helper | ✅ Cleaned |
| `core/exceptions.py` | DataIntegrityError | ✅ Stable |
| `api/main.py` | FastAPI controller | ⚠️ Bloated (1,020 lines) |
| `api/engine_pool.py` | Multi-format engine pool | ✅ Stable |
| `api/serializers.py` | Engine output → JSON | ✅ Stable |
| `api/models.py` | Pydantic models | ✅ Stable |

### Engine Files (DO NOT MODIFY unless Phase 2)
| File | Lines | Status |
| :--- | :--- | :--- |
| `formats/odi/engines/team_engine.py` | 826 | ✅ Stable |
| `formats/odi/engines/player_engine.py` | ~500 | ✅ database-driven (v5.1) |
| `formats/odi/engines/predictor_engine.py` | ~400 | ✅ database-driven (v5.1) |

### Data Pipeline (NOT part of runtime)
| File | Role |
| :--- | :--- |
| `scripts/update_data.py` | Master orchestrator |
| `formats/odi/utils/json_converter.py` | JSON → CSV |
| `formats/odi/utils/refinery_script.py` | CSV → Intelligence CSVs |
| `formats/odi/utils/ingest_to_db.py` | CSV → DuckDB |

### Database
| File | Size | Tables |
| :--- | :--- | :--- |
| `formats/odi/data/odi.duckdb` | 17 MB | balls (1.3M), matches (2.5K), player_stats (18.6K), phase_stats (5K), player_metadata (2K), squads (55K) |

---

## 📐 5. Rules of Engagement

1. **One Phase at a Time.** Complete current phase fully. Test. Verify. Then advance.
2. **No Engine Modifications** (except Phase 2). Engines are stable domain logic.
3. **Test Everything.** Before/after comparison for every phase. 17 API endpoints must pass.
4. **Update This Document.** Mark phases complete with dates after verification.
5. **Update AI_MEMORY.md.** Log session history after every phase.
