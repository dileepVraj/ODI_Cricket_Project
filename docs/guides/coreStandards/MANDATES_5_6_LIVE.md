# Architectural Mandates 5–6 (Live Layer)
# Part of: coreStandards
# DORMANT — do not load unless task touches core/live/ or api/live/
# core/live/ does not exist yet in Phase 10. These mandates activate in Phase 12.
# Source: ENGINEERING_STANDARDS_BACKEND.md Part 0 (authoritative)

---

## Mandate 5: Event-Driven State (The Live Bridge)

**APPLIES TO:** Any file that participates in the live match pipeline — the scraper, the live state singleton, the WebSocket broadcaster, and any calculation triggered by a live match event. This mandate also applies to any historical analysis code that might be tempted to read live state, or any live code that might be tempted to query DuckDB.

**PRINCIPLE:**
Live match state and historical match data are fundamentally different things and MUST be treated differently. Historical data lives in DuckDB — it is immutable, pre-loaded at startup, and queried analytically. Live match state lives in RAM — it is mutable, updated every 10 seconds by the scraper, and accessed by all connected clients simultaneously.

These two worlds MUST NEVER be mixed. A live calculation MUST NOT query DuckDB. A historical query MUST NOT read from the live singleton. The boundary between these two worlds is absolute.

**The in-memory contract:**
The `LiveMatchState` Pydantic model is the single source of truth for all live calculations. It is always current. It is always in RAM. Any calculation that needs the current score, the current over, or the current win probability reads from this singleton — never from DuckDB.

**Why DuckDB must never be queried during a live event:**
DuckDB is a file-based analytical database. A read from DuckDB involves disk I/O, query parsing, and result serialization. On the Ryzen 5 3500U this takes 50–500 milliseconds. A WebSocket broadcast needs to complete in under 100ms to feel instantaneous to the user. DuckDB reads inside the live pipeline violate both the latency requirement and Mandate 1 simultaneously.

**VIOLATIONS — apply to any file with a Live Layer role:**
```python
# VIOLATION — DuckDB query inside a live calculation
def calculate_live_win_probability(
    self, state: LiveMatchState
) -> float:
    recent = self.dal.get_matches(           # DuckDB inside live path
        team=state.batting_team, limit=5
    )
    ...

# VIOLATION — writing live state without acquiring a lock first
def update_score(self, new_score: int) -> None:
    self.state.current_score = new_score    # Race condition — no lock

# CORRECT — live calculation uses only pre-loaded historical data
# and the in-memory state object — never DuckDB at runtime
def calculate_live_win_probability(
    self,
    state: LiveMatchState,
    historical_win_rate: float             # pre-computed at startup
) -> float:
    chase_factor = state.required_rr / state.current_rr
    return min(historical_win_rate * chase_factor, 1.0)

# CORRECT — singleton write protected by a lock
def update_score(self, new_score: int) -> None:
    with self._state_lock:                  # lock acquired before write
        self.state.current_score = new_score
```

**HARD STOP:** Any DuckDB query, file read, or network call found inside any function that executes during a live scrape cycle or WebSocket broadcast is a Critical Architecture Violation.

---

## Mandate 6: WebSocket-First Real-Time Communication

**APPLIES TO:** Any file that pushes data from the backend to the frontend in response to a live event, and any frontend file that receives or requests live data. This mandate governs the communication protocol between the live backend layer and the frontend during a match session.

**PRINCIPLE:**
HTTP is a request-response protocol — the client asks, the server answers. This model is fundamentally wrong for live match data where the server has new information before the client asks for it. Making the frontend poll via repeated HTTP requests is architecturally backwards, wastes resources, and adds unnecessary latency between a score update and the frontend reflecting it.

WebSocket is a persistent, bidirectional connection. The server pushes data the moment it has it. The frontend receives it instantly. No polling. No repeated round trips. One connection per client session, held open for the duration of the match.

**The communication contract — strictly one-directional:**
```
Scraper updates singleton (every 10 seconds)
    → acquires threading.Lock()
    → writes delta fields to LiveMatchState
    → releases lock
    → WebSocket broadcaster sends DELTA ONLY to all connected clients
    → frontend WebSocket hook receives push event
    → React state merges delta
    → UI re-renders affected components only
```

**What "delta-only" means:**
The broadcaster MUST send only the fields that changed — not the entire state object. If only the score changed, only the score field is broadcast. This keeps payloads minimal, reduces re-render cost, and prevents unnecessary state churn in the React component tree.

**VIOLATIONS — apply to any file in the Live Layer or UI Adapter:**
```javascript
// VIOLATION — polling via repeated HTTP calls (frontend)
setInterval(() => {
    fetch('/execute/get_live_score')
        .then(r => r.json())
        .then(setScore)
}, 3000)   // This is forbidden. Use WebSocket.

// VIOLATION — Server-Sent Events instead of WebSocket (backend)
async def live_feed(request: Request):
    async def event_stream():
        while True:
            yield f"data: {score}\n\n"    # SSE — forbidden for live data
    return EventSourceResponse(event_stream())
```
```javascript
// CORRECT — persistent WebSocket connection (frontend)
const ws = new WebSocket('ws://localhost:8000/live/match')
ws.onmessage = (event) => {
    const delta = JSON.parse(event.data)
    setState(prev => ({ ...prev, ...delta }))    // merge delta only
}
```

**HARD STOP:** Any polling implementation, any `setInterval` or `setTimeout` calling an HTTP endpoint for live data, or any Server-Sent Events implementation used for live updates is a Critical Architecture Violation.

---

*Part of coreStandards — DORMANT until Phase 12.*
*Load only when task touches core/live/ or api/live/.*
*Authoritative source: ENGINEERING_STANDARDS_CORE.md*
