# Memory & Resource Audit — Cricket Algo-Trader
**Date:** 2026-02-27 | **Auditor:** Antigravity AI | **Hardware:** AMD Ryzen 5 3500U · 16 GB RAM · 4 GB usable budget

---

> **BUDGET HARD CEILING: 4,096 MB**
> Windows 11 + IDE + browser consume ~10 GB before the app starts.

---

## SECTION 1: CURRENT MEMORY BASELINE

### 1.1 Startup Memory Map

At startup, `api/main.py` [line 147–156] fires `initialize_pool()` from `api/engine_pool.py` [line 33]. This instantiates one `CricketAnalyzer` object per loaded format. Currently only `odi` has a manifest, so **one analyzer is built and held for the entire server lifetime**.

The call chain:
```
api/main.py [L153]  →  engine_pool.initialize_pool()  →  CricketAnalyzer(format_type="odi", ...)
```

The `CricketAnalyzer` object (imported via `from engine import CricketAnalyzer` — `api/engine_pool.py` [L44]) loads and holds the following for the entire session:

| Object | Source | Where Held | Lifetime |
|---|---|---|---|
| `analyzer.match_df` | DuckDB `matches` table, full `SELECT *` | Session singleton in `_engine_pool["odi"]` | **Forever (session)** |
| `analyzer.phase_df` | DuckDB `phase_stats` table, full `SELECT *` | Session singleton | **Forever (session)** |
| `analyzer.player_df` | DuckDB `player_stats` table, full `SELECT *` | Session singleton | **Forever (session)** |
| `analyzer.meta_df` | DuckDB `player_metadata` table, full `SELECT *` | Session singleton | **Forever (session)** |
| `analyzer.squads_df` | DuckDB `squads` table, full `SELECT *` | Session singleton | **Forever (session)** |
| `analyzer.dal` | `DataAccess` object with open `duckdb.connect()` | Session singleton | **Forever (session)** |
| `analyzer.team_engine` | `TeamEngine` instance | Session singleton | **Forever (session)** |
| `analyzer.player_engine` | `PlayerEngine` instance + `self.player_df`, `self.meta_df`, `self.squads_df` | Session singleton | **Forever (session)** |
| `analyzer.predictor_engine` | `PredictorEngine` instance + `self.player_df` | Session singleton | **Forever (session)** |
| DuckDB connection | `duckdb.connect(db_path, read_only=True)` — `core/data_access.py` [L29] | `self.con` inside `DataAccess` | **Forever (session)** |

> **⚠️ CRITICAL INTEGRITY WARNING:** The `CricketAnalyzer` class was deleted from the root in the junk cleanup. The pool still tries `from engine import CricketAnalyzer` at `api/engine_pool.py` [L44]. This import either resolves to an `engine.py` somewhere on the Python path (not found in the scan) or the pool silently fails the `odi` format at runtime. **This is the single highest-priority code integrity risk found in this audit and must be verified at runtime.**

#### Estimated Startup Memory (ODI format only)

| Component | Estimate Basis | Est. MB |
|---|---|---|
| Python interpreter + FastAPI + Uvicorn + all imports | Typical | ~150 MB |
| DuckDB engine (in-process) | Library overhead | ~30 MB |
| `odi.duckdb` file = 18.7 MB on disk | DuckDB buffers aggressively; expect 2–4× | ~60–75 MB |
| `analyzer.match_df` (~4,600 matches × ~30 cols) | int64/float64/object mix | ~15–25 MB |
| `analyzer.phase_df` (`processed_phase_stats.csv` = 504 KB on disk) | CSV → Pandas 3–4× overhead | ~2–4 MB |
| `analyzer.player_df` (`processed_player_stats.csv` = 1.15 MB on disk) | CSV → Pandas overhead | ~4–8 MB |
| `analyzer.meta_df` (`player_metadata.csv` = 46 KB on disk) | Negligible | <1 MB |
| `analyzer.squads_df` (`MATCH_SQUADS.csv` = 4.0 MB on disk) | Pandas 3–4× overhead | ~12–16 MB |
| `PlayerEngine` + `PredictorEngine` self.player_df/meta_df/squads_df | Same objects passed by reference | 0 MB (shared) |
| Next.js dev mode (separate process) | Typical Next.js 16 dev server | ~200–400 MB |
| **TOTAL STARTUP ESTIMATE** | | **~480–710 MB** |

---

### 1.2 DataFrame Inventory

All DataFrames pre-loaded and held in RAM as session singletons:

#### DF-1: `analyzer.match_df`
- **Confirmed used at:** `api/main.py` [L695], `core/services/enrichment.py` [L31]
- **Data:** Full `matches` table from DuckDB (`SELECT * FROM matches`). All ODI match summaries.
- **Dtypes:** `object` (team names, venue, winner), `float64` (scores), `int64` (ball counts), `datetime64` (start_date).
- **Full table or filtered?** Full table — no filter pushed.
- **Lifetime:** Session singleton, held forever.
- **Estimated row count:** ~4,600 matches.
- **Estimated RAM:** ~15–25 MB (confirm with Section 5.2 script).
- **`.copy()` usage:** `team_engine.py` [L45] calls `frame.copy()` on every single TeamEngine method call.

#### DF-2: `analyzer.phase_df`
- **Data:** Phase stats (powerplay/mid/death run & wicket aggregates per match+innings).
- **Dtypes:** Mix of `float64` (averages) and `int64/object` (match_id, phase labels).
- **On-disk size:** `processed_phase_stats.csv` = 504 KB.
- **Est. RAM:** ~2–4 MB.

#### DF-3: `analyzer.player_df` (also held in `PredictorEngine.player_df` and `PlayerEngine.player_df`)
- **File / Line:** `PredictorEngine.__init__` [`predictor.py` L36], `PlayerEngine.__init__` [`player_engine.py` L50].
- **Data:** Aggregated player career stats cross-indexed by context, opponent, venue, role.
- **On-disk:** `processed_player_stats.csv` = 1.15 MB.
- **Est. RAM:** ~4–8 MB.
- **Note:** Passed by reference to both engine instances — RAM cost is 1× (not duplicated).

#### DF-4: `analyzer.meta_df`
- **File / Line:** `PlayerEngine.__init__` [`player_engine.py` L33].
- **Data:** Player metadata (team affiliations, roles).
- **Est. RAM:** < 1 MB. Negligible.

#### DF-5: `analyzer.squads_df`
- **File / Line:** `PlayerEngine.__init__` [`player_engine.py` L52–55].
- **Data:** Match squad rosters with `is_playing_xi` flags.
- **On-disk:** `MATCH_SQUADS.csv` = 4.0 MB.
- **Est. RAM:** ~12–16 MB.

#### DF-6: Per-Request `context_df` (Balls DataFrame)
- **File / Line:** `api/main.py` [L664]: `context_df = dal.get_balls(players=clean_players)`.
- **Data:** Ball-by-ball records for players in the current request. **Filter is correctly pushed into SQL.**
- **Lifetime:** Local variable. Released after request completes.
- **Peak estimate (Squad Comparison, 22 players, 5 years):** 500,000–1,000,000 rows × ~20 columns. **~50–200 MB peak.**

#### DF-7: `balls_df` in `predict_score()` — 🔴 CRITICAL RISK
- **File / Line:** `formats/odi/predictor.py` [L118]: `balls_df = self.dal.get_balls(years_back=years)`.
- **Data:** **The ENTIRE balls table, filtered only by `years_back`. No team, no player, no venue filter applied at query time.**
- **The source CSV (`FINAL_ODI_MASTER.csv`) is 181 MB on disk.**
- **Est. Pandas RAM:** A 181 MB CSV typically produces a **300–600 MB DataFrame** due to Python `object` column overhead (team names, player names, wicket types, etc.).
- **This is the single most dangerous memory operation in the codebase.**

---

### 1.3 DuckDB Query Pattern Analysis

#### ✅ GOOD — Filter properly pushed into SQL (DuckDB filters on disk)

| Method | File:Line | Filter Pushed? | Notes |
|---|---|---|---|
| `get_matches()` | `data_access.py` [L383–427] | YES | team/venue/years/country WHERE clause |
| `get_balls()` | `data_access.py` [L430–494] | YES | match_ids, venue, team, player, innings, phase, years WHERE clause |
| `get_venue_summary()` | `data_access.py` [L497–520] | YES | aggregated in SQL |
| `get_h2h_summary()` | `data_access.py` [L522–556] | YES | aggregated in SQL |
| `get_player_career_summary()` | `data_access.py` [L558–585] | YES | full aggregation in SQL |
| `get_venue_phase_stats()` | `data_access.py` [L587–614] | YES | double aggregation in SQL |
| `get_player_vs_style()` | `data_access.py` [L616–632] | YES | filtered by striker + bowler list |
| `get_team_form()` | `data_access.py` [L634–654] | YES | filtered with LIMIT |
| `get_player_stats_batch()` | `data_access.py` [L671–723] | YES | player list filter in SQL |

#### ❌ BAD — Full table loads (no filter)

| Method | File:Line | Problem | Severity |
|---|---|---|---|
| `get_player_stats()` | `data_access.py` [L352–355] | `SELECT * FROM player_stats` — no filter | **MEDIUM** |
| `get_player_batting_stats()` | `data_access.py` [L357–360] | `SELECT * FROM player_batting_stats` — no filter | **MEDIUM** |
| `get_player_bowling_stats()` | `data_access.py` [L362–365] | `SELECT * FROM player_bowling_stats` — no filter | **MEDIUM** |
| `get_phase_stats()` | `data_access.py` [L367–370] | `SELECT * FROM phase_stats` — no filter | **LOW** (small table) |
| `get_player_metadata()` | `data_access.py` [L372–375] | `SELECT * FROM player_metadata` — no filter | **LOW** (< 1 MB) |
| `get_squads()` | `data_access.py` [L377–380] | `SELECT * FROM squads` — no filter | **MEDIUM** |
| **`get_balls(years_back=years)`** | **`predictor.py` [L118]** | **No player/team/venue filter. Loads ENTIRE balls table.** | **🔴 CRITICAL** |

> **The DuckDB DAL architecture (Section 1.3 "GOOD" group) is well-designed.** The one critical exception is `predictor.py` [L118] which bypasses the entire filter-push strategy.

---

## SECTION 2: MEMORY RISK ANALYSIS

### 2.1 DataFrame dtype Audit

Based on column names, CSV sizes, and standard Pandas inference behaviour. **Cannot determine exact dtypes without runtime measurement** — use Section 5.2 to confirm.

| DataFrame | Expected Dominant Dtypes | Optimization Opportunity | Est. Saving |
|---|---|---|---|
| `match_df` | `object`, `float64`, `datetime64` | `balls_inn1/2`, `wickets_inn1/2`, `score_inn1/2` → `int32` | ~4–10 MB |
| `phase_df` | `float64`, `object` | `pp_runs`, `mid_runs`, `dth_runs`, `pp_wkts` etc. → `float32` | ~1–2 MB |
| `player_df` | `object`, `float64` | `runs`, `balls`, `innings`, `dismissals` → `int32` | ~2–4 MB |
| `context_df` (per-request) | `object` (dominant), `float64` | `runs_off_bat`, `extras`, `wides`, `noballs` → `int16`; `innings` → `int8` | **10–40 MB per large request** |
| `balls_df` in predictor | Same as context_df, full table | Anything helps; root fix is to not load the full table | **300–600 MB if load made unavoidable** |

**Rule:** Casting `float64` → `float32` or `int64` → `int32` saves **exactly 4 bytes per value per row**.

---

### 2.2 DataFrame Copy Audit

Every `.copy()` call that creates a temporary in-memory duplicate:

| Location | File:Line | Necessary? | Memory Cost |
|---|---|---|---|
| `_normalize_match_innings_fields()` | `data_access.py` [L234] | YES — modifies columns in-place | Transient ~15–25 MB spike |
| `_hydrate_missing_match_teams()` | `data_access.py` [L311–312] | YES — writes back to DataFrame | Transient spike |
| **`_context_df()` in TeamEngine** | **`team_engine.py` [L45]** | **NO — called on every TeamEngine method. Copies match_df and phase_df on every API call.** | **~15–25 MB wasted per team analysis request** |
| `squad_context_df = context_df.copy()` | `player_engine.py` [L257] | Partially necessary | ~1× context_df = 50–200 MB spike |
| `squad_context_df = context_df.copy()` | `player_engine.py` [L541] | Same pattern, separate code path | ~1× context_df spike |
| `context_df = context_df.copy()` | `api/main.py` [L673] | YES — needed for date coercion | ~1× context_df spike |
| `bat_window = balls_df[...].copy()` | `predictor.py` [L208] | YES — adds `is_out` column | 2nd copy of already-massive balls_df |
| `bowl_window = balls_df[...].copy()` | `predictor.py` [L235] | YES — groupby agg | 3rd copy during prediction |
| `work_df = df.copy()` | `match_filter_service.py` [L33] | YES — adds status column | ~1× match_df |
| `phase_df = ball_df.copy()` | `phase_engine.py` [L119] | YES — pivot operation | Transient |

> **The `_context_df()` pattern in `team_engine.py` [L45] is the most structurally wasteful.** Every TeamEngine method (`analyze_home_fortress`, `analyze_venue_bias`, `analyze_global_h2h`, `analyze_team_form`, etc.) calls `self._context_df(ctx, "match_df")` which does `frame.copy()`. A 15–25 MB copy is created and discarded on every single team analysis API request.

---

### 2.3 Monte Carlo / Simulation Memory Audit

**NOT PRESENT in current codebase.** The word `simulate` returns zero results across all Python files. `core/backtester.py` (1,960 bytes) is a thin stub with no iterative logic.

`PredictorEngine.predict_score()` at `predictor.py` [L102–367] uses **deterministic arithmetic** (weighted averages, not probabilistic sampling) — no loop-based array building.

**Phase 12 memory implication:** If Phase 12 adds live win probability recalculation on each 10-second scrape event using the current `predict_score()` architecture, it will fire `self.dal.get_balls(years_back=years)` [`predictor.py` L118] repeatedly — loading the full balls table into RAM every 10 seconds. Without garbage collection guarantee between calls, this is an **unbounded recurring memory spike**.

---

### 2.4 Memory Leak Risk

| Risk | File:Line | Description | Severity |
|---|---|---|---|
| **Full balls table in `predict_score()`** | `predictor.py` [L118] | `balls_df` is released after function returns (no leak), but the 300–600 MB spike on every call is dangerous for Phase 12's repeating invocations | 🔴 CRITICAL |
| **`_engine_pool` dict accumulates per format** | `engine_pool.py` [L27] | Grows if additional formats are loaded. Currently 1 format. No eviction. | LOW (controlled) |
| **Session DataFrames never freed** | `engine_pool.py` [L70], `player_engine.py` [L50] | `match_df`, `player_df`, etc. held for server lifetime by design. Not a leak but inflates baseline. | DESIGN (intentional) |
| **`io.StringIO()` per request** | `api/main.py` [L437] | Each request allocates a buffer. Released after request. | NEGLIGIBLE |
| **`results` list in `get_player_vs_style()` loop** | `data_access.py` [L617–632] | Local list of DFs, then `pd.concat`. Released. | NEGLIGIBLE |

---

### 2.5 Next.js Memory Profile

| Setting | File:Line | RAM |
|---|---|---|
| **Current: `npm run dev`** | `frontend/package.json` [L6] | **~250–450 MB** (HMR + source maps + instrumentation) |
| **Production: `npm run build && npm start`** | `frontend/package.json` [L7–8] | **~100–180 MB** (minified, no HMR) |
| **Estimated saving by switching: ~150–300 MB** | | |

**The frontend is currently configured to run in dev mode.** It should be switched to production mode for any session where you are doing analysis rather than UI development.

---

## SECTION 3: PHASE 12 READINESS

### 3.1 Current Headroom Estimate

| Scenario | RAM |
|---|---|
| Baseline (startup, dev mode frontend) | ~730–1,160 MB |
| Peak (during `predict_score()` call) | ~1,100–1,835 MB |
| 4 GB hard budget | 4,096 MB |
| **Available headroom (conservative peak)** | **~2,261 MB** |
| **Available headroom (optimistic peak)** | **~3,006 MB** |

---

### 3.2 Phase 12 Memory Requirements

| Phase 12 Addition | Estimated RAM | Notes |
|---|---|---|
| Background scraper thread (10s cadence) | ~5–15 MB | Thread stack + scrape payload string |
| Live match state singleton (Pydantic model) | ~1–5 MB | Single match worth of structured data |
| WebSocket connections (1 user, asyncio) | ~1–5 MB | Asyncio coroutines + buffers |
| **Win probability on each scraper update — FIXED** | ~0 MB extra (request-scoped) | If predictor uses player-filtered query |
| **Win probability on each scraper update — UNFIXED** | **+300–600 MB every 10 seconds** | Full balls table repeatedly loaded |
| **Phase 12 TOTAL (safe implementation)** | **~10–30 MB** | Predictor must be fixed first |
| **Phase 12 TOTAL (current implementation)** | **+300–600 MB recurring** | Memory crash risk over time |

---

### 3.3 Blocking Issues Before Phase 12

| # | Issue | File:Line | Risk If Unresolved |
|---|---|---|---|
| **🔴 BLOCKER 1** | `get_balls(years_back=years)` loads entire balls table with no player/venue filter | `predictor.py` [L118] | Every 10-second Phase 12 scraper update triggers a 300–600 MB RAM spike. OOM crash over time. |
| **🔴 BLOCKER 2** | `from engine import CricketAnalyzer` references a potentially deleted module | `engine_pool.py` [L44] | If broken, no format loads at all. Phase 12 cannot start. Must verify `engine.py` exists. |
| **⚠️ NON-BLOCKER 3** | `_context_df()` copies `match_df` on every team analysis request | `team_engine.py` [L45] | 15–25 MB wasted per request. Not critical at 1-user load but wastes memory. |

---

## SECTION 4: PRIORITIZED MEMORY OPTIMIZATION PLAN

### PRIORITY 1 — CRITICAL (Fix Before Phase 12)

- **Fix `predictor.py` full table load** — Expected RAM saving: **300–600 MB per prediction call**
  - [`predictor.py` Line 118]
  - Change: `balls_df = self.dal.get_balls(years_back=years)`
  - To: `balls_df = self.dal.get_balls(players=list(set(batting_players + bowling_players)), years_back=years)`

- **Verify `CricketAnalyzer` Facade (`engine.py`) exists** — Existential risk, no savings estimate
  - [`api/engine_pool.py` Line 44]

- **Switch Next.js to production mode** — Expected RAM saving: **~150–300 MB**
  - [`frontend/package.json` Line 6]
  - Use `npm run build && npm start` instead of `npm run dev` for any analysis session

---

### PRIORITY 2 — HIGH (Fix Before Adding New Features)

- **Eliminate `_context_df()` copy in TeamEngine** — Expected saving: **15–25 MB per team API request**
  - [`team_engine.py` Line 45]
  - Either pass frame directly without copy, or copy only when mutation is confirmed necessary

- **Downcast `match_df` numeric columns at startup** — Expected saving: **~4–10 MB**
  - Inside `CricketAnalyzer.__init__` / engine Facade
  - `balls_inn1`, `balls_inn2`, `wickets_inn1`, `wickets_inn2` → `int32`
  - `score_inn1`, `score_inn2` → `int32`

- **Downcast `context_df` numeric columns after `get_balls()`** — Expected saving: **10–40 MB per large request**
  - [`api/main.py` Lines 664–680]
  - `runs_off_bat`, `extras`, `wides`, `noballs` → `int16`; `innings` → `int8`

---

### PRIORITY 3 — MEDIUM (Fix During Normal Development)

- **Remove redundant `context_df.copy()` in `get_squad_comparison_data()` and `_generate_comparison_payload()`** — Expected saving: **50–200 MB peak reduction for squad comparison**
  - [`player_engine.py` Lines 257, 541]

- **Replace full-table startup loads with lazy/on-demand loading** — Reduces startup latency, not steady-state RAM
  - [`data_access.py` Lines 352–380] — `get_player_stats()`, `get_squads()`, etc.

- **Downcast `player_df` numeric columns at startup** — Expected saving: **2–4 MB**
  - `runs`, `balls`, `innings`, `dismissals` → `int32`

---

## SECTION 5: MEASUREMENT INSTRUCTIONS

### 5.1 Startup Memory Measurement

Run this **after** starting the FastAPI backend to see the true baseline:

```python
# Save as measure_startup.py and run: python measure_startup.py
import psutil

for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
    try:
        if 'uvicorn' in ' '.join(proc.cmdline()):
            mem = proc.memory_info()
            print(f"[BACKEND] PID: {proc.pid}")
            print(f"  RSS (Resident Set): {mem.rss / 1024**2:.1f} MB")
            print(f"  VMS (Virtual):      {mem.vms / 1024**2:.1f} MB")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
    try:
        cmdline = ' '.join(proc.cmdline())
        if 'next' in cmdline and ('dev' in cmdline or 'start' in cmdline):
            mem = proc.memory_info()
            print(f"\n[FRONTEND] PID: {proc.pid}")
            print(f"  RSS: {mem.rss / 1024**2:.1f} MB")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
```

---

### 5.2 Per-DataFrame Measurement

Add this block temporarily inside `CricketAnalyzer.__init__` (or the engine Facade) immediately after each DataFrame is assigned:

```python
# TEMPORARY — remove after audit
def _df_ram(df, name):
    mb = df.memory_usage(deep=True).sum() / 1024**2
    print(f"[RAM AUDIT] {name}: {len(df):,} rows × {len(df.columns)} cols = {mb:.2f} MB")
    print(f"  dtypes: {dict(df.dtypes.value_counts())}")

_df_ram(self.match_df,   "match_df")
_df_ram(self.phase_df,   "phase_df")
_df_ram(self.player_df,  "player_df")
_df_ram(self.meta_df,    "meta_df")
_df_ram(self.squads_df,  "squads_df")
```

---

### 5.3 Peak Memory During `predict_score()`

Wrap the `predict_score()` body in `predictor.py` with this context manager (temporary):

```python
# Add to imports at top of predictor.py (temporary):
import tracemalloc

# At the START of predict_score():
tracemalloc.start()

# At the END of predict_score(), before `return {`:
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"[RAM AUDIT] predict_score() — current: {current/1024**2:.1f} MB, peak: {peak/1024**2:.1f} MB")
```

Then trigger one prediction via the frontend and read the server console.

---

### 5.4 System-Wide Available RAM Check (PowerShell)

Run this in PowerShell **before** starting the application on any given day:

```powershell
$os   = Get-CimInstance Win32_OperatingSystem
$total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$avail = [math]::Round($os.FreePhysicalMemory     / 1MB, 2)
$used  = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 2)

Write-Host "Total RAM:           $total GB"
Write-Host "Used by OS+procs:    $used GB"
Write-Host "Available NOW:       $avail GB"
Write-Host "Budget headroom:     $('{0:F2}' -f ($avail - 4)) GB spare above 4 GB floor"
```

---

## FINAL SUMMARY

### Q1: How much RAM is this application currently using at peak?

**Estimated 1,100–1,835 MB at peak.** Breakdown:

| Layer | Est. MB |
|---|---|
| Python backend + all pre-loaded DataFrames | ~480–710 |
| Next.js frontend (dev mode) | ~250–450 |
| DuckDB process overhead | ~60–75 |
| `predict_score()` full balls table spike | +300–600 |
| **Peak total** | **~1,100–1,835** |

This is **27–45% of the 4 GB budget** — comfortably within limits. **Run the Section 5.2 measurement script to replace these estimates with ground truth.**

---

### Q2: Do we have enough headroom to safely build Phase 12?

**Yes — but only after fixing `predictor.py` [L118] first.**

Phase 12 itself (scraper thread + Pydantic singleton + WebSocket) adds only ~10–30 MB — trivial. The danger is that Phase 12's 10-second scrape cycle will call `predict_score()` repeatedly. If unfixed, each call loads the full 181 MB CSV worth of data into a 300–600 MB Pandas DataFrame, creating a recurring RAM spike every 10 seconds. Without guaranteed GC between calls, memory will ratchet upward and eventually exceed the 4 GB ceiling.

**Fix the predictor → Phase 12 is safe. Build Phase 12 without fixing it → crash risk.**

---

### Q3: What is the single most impactful memory change we can make right now?

**Refactor `formats/odi/predictor.py` [Line 118].**

```python
# CURRENT (BAD) — loads the ENTIRE balls table (~300–600 MB in RAM):
balls_df = self.dal.get_balls(years_back=years)

# FIX — loads only the ~22 relevant players' data (~5–30 MB in RAM):
all_players = list(set(batting_players + bowling_players))
balls_df = self.dal.get_balls(players=all_players, years_back=years)
```

This single-line change eliminates the largest avoidable memory cost in the entire application and unblocks Phase 12 development.
