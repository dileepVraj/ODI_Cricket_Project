# Memory Management & Thread-Safety Standards
# Part of: backendStandards
# Load 2.3 for: any engine/calculator/service task with DataFrames
# Load 2.4 for: Phase 12 tasks involving LiveMatchState singleton (currently DORMANT)
# Source: ENGINEERING_STANDARDS_BACKEND.md Parts 2.3 + 2.4 (authoritative)

---

## 2.3 Memory Management Standards (4 GB Hard Budget)

These rules exist because the application has exactly 4 GB of usable RAM. Violating them does not produce a code review comment — it produces a crash during a live match session.

**1. DuckDB Filters on Disk — Not Pandas in RAM:** Every DAL method MUST push all known filters (player, team, venue, year range) into the SQL `WHERE` clause. Loading a full table into a Pandas DataFrame and filtering in Python is forbidden when a filtered DuckDB query would return a fraction of the rows.
```python
# VIOLATION — loads entire balls table (~300–600 MB in RAM)
balls_df = self.dal.get_balls(years_back=5)

# CORRECT — loads only the relevant players' data (~5–30 MB)
balls_df = self.dal.get_balls(players=squad_players, years_back=5)
```

**2. No Unnecessary DataFrame Copies:** AI agents MUST NOT call `.copy()` on a DataFrame unless mutation of the original would cause a correctness bug. Use filtered views (`df[mask]`) instead of copies. Every `.copy()` call doubles the memory of that DataFrame temporarily.

**3. dtype Downcasting at the DAL Boundary:** Integer columns that will never exceed 32-bit range (runs, balls, wickets, overs, years) MUST be cast to `int32`. Float columns for cricket statistics MUST be cast to `float32`. This halves the memory footprint of every pre-loaded DataFrame. Downcasting is enforced at load time in `core/data_access.py` — not in the engines.

**4. Pre-Allocated Simulation Arrays:** Before any iterative simulation (e.g., Monte Carlo), allocate the result array once and fill in-place. Never build a Python list inside a loop and convert to NumPy at the end — this creates two full copies of the data simultaneously.
```python
# VIOLATION — creates two full copies simultaneously
results = []
for i in range(10_000):
    results.append(simulate_one())
output = np.array(results)

# CORRECT — single allocation, in-place fill
output = np.empty(10_000, dtype=np.float32)
for i in range(10_000):
    output[i] = simulate_one()
```

**5. No Unbounded Accumulators:** Global variables, caches, or in-memory lists that grow with each request and have no eviction policy are forbidden. Any in-memory accumulator MUST define a maximum size and an explicit eviction or rotation strategy.

**6. Production Build for Live Sessions:** The Next.js frontend MUST be run in production build mode during live trading sessions. Dev mode consumes an additional 150–400 MB that is not available in the 4 GB budget.
```powershell
# CORRECT for live sessions
npm run build && npm run start

# FORBIDDEN during live sessions
npm run dev
```

**Hard Stop:** Any `.copy()` call on a session-level DataFrame, any full table load where a filtered query is possible, or any list-then-convert simulation pattern is a Hard Fail.

---

## 2.4 Thread-Safety Standards (Live Singleton Integrity)

These rules govern the two concurrent threads — the background scraper and the FastAPI request handler — that share the `LiveMatchState` singleton in Phase 12.

**Note: Section 2.4 is currently DORMANT.** `core/live/` does not exist yet in Phase 10. These rules apply when Phase 12 live layer work begins.

**1. All Singleton Writes and Reads MUST Use a Lock:** The `LiveMatchState` singleton MUST be protected by a single `threading.Lock()` stored as a class-level attribute. Any thread that writes to or reads from the singleton MUST acquire this lock first.

**2. Context Manager Pattern is Mandatory:** Lock acquisition MUST use Python's context manager (`with self._state_lock:`). Manual `acquire()` / `release()` calls are forbidden — they introduce deadlock risk if an exception fires between the two calls.

**3. Lock Duration Must Be Minimal:** The lock MUST be held only during the atomic state update — never during network I/O, never during calculations, never during WebSocket broadcasting.

**4. Scraper MUST Be a Daemon Thread:** The scraper thread MUST be initialised with `daemon=True` so it does not prevent application shutdown.

**Correct Pattern:**
```python
# WRITE (scraper thread) — lock held only during the state mutation
with self._state_lock:
    self.state.current_score = new_score
    self.state.current_over = new_over
    self.state.win_probability = new_probability

# READ (API thread) — lock held only during the snapshot read
with self._state_lock:
    snapshot = dataclasses.replace(self.state)
return snapshot
```

**Hard Stop:** Any write to or read from a session-level singleton from within a threaded context without a `threading.Lock()` is a Critical Thread-Safety Violation.

---

*Part of backendStandards — load for backend tasks involving DataFrames (2.3) or live singleton (2.4).*
*Authoritative source: ENGINEERING_STANDARDS_CORE.md*
