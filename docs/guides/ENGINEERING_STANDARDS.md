# System Architecture & Engineering Standards

**Last Updated:** 2026-03-02
**Version:** 2.2
**Target Audience:** Human Architects & Autonomous AI Agents.
**Core Directive:** "Assume data is dirty, boundaries are strict, and trust is zero."

This document is the **absolute and non-negotiable source of truth** for all code generation, refactoring, and architectural decisions within the Multi-format Cricket Algo-Trading Platform. Every rule in this document is a hard constraint. AI agents MUST parse this document in full before executing any task. Partial compliance is non-compliance. When in doubt, do less — not more.

---

## PART 0: ARCHITECTURAL DNA (The Principal Mandates)

These are the immovable laws of this codebase. They are not tied to any specific directory, filename, or technology. They are tied to the **responsibility** of the code being written. No task, no deadline, and no agent instruction overrides them. Ever.

---

### HOW TO READ PART 0

Before applying any mandate, you must first classify the file you are working on. Every file in this codebase has a **layer role** — a single primary responsibility that determines which mandates apply to it.

**How to classify any file — ask what its primary job is:**

| If the file's primary job is... | Its layer role is... | Mandates that apply |
|---|---|---|
| Performing calculations — taking data in, returning results out | **Domain Core** | Mandates 1, 2, 3, 4 |
| Mapping HTTP requests to domain functions, serializing responses | **Interface Adapter** | Mandates 2, 4 |
| Reading from or writing to the database | **Data Access** | Mandates 2, 4 |
| Rendering UI components, displaying data | **UI Adapter** | Mandate 4 |
| Extracting, transforming, or loading data into the database | **ETL Infrastructure** | Mandate 4 |
| Managing live match state, scraping, broadcasting live updates | **Live Layer** | Mandates 5, 6 |

**A file's layer role is determined by what it does — not where it lives.**

If a new file is added anywhere in the codebase that performs analytical calculations, it is a Domain Core file and Mandates 1, 2, 3, and 4 apply to it immediately — regardless of its directory path. The current project topology (which directories exist today) is documented in Part 1. Part 0 governs the principles. Part 1 maps those principles to the current structure. When the structure changes, Part 1 is updated. Part 0 never changes.

---

### Mandate 1: Functional Core, Imperative Shell

**APPLIES TO:** Any file whose primary responsibility is analytical calculation. You can identify these files because they accept data structures (DataFrames, dicts, TypedDicts) as inputs and return computed results (primitives, TypedDicts, dataclasses) as outputs. They contain mathematical or statistical logic. They do not orchestrate, do not serve HTTP requests, and do not manage state.

**PRINCIPLE:**
A Domain Core file is a pure function at the architectural level. It takes data in. It returns data out. It has no memory of previous calls. It has no awareness of the outside world. Given identical inputs, it ALWAYS produces identical outputs. This is not a style preference — it is what makes the calculations testable, debuggable, and trustworthy in a trading context. You cannot trust a win probability produced by a function that also writes to a database, reads from a file, or depends on a global variable — because you cannot reproduce its output in isolation.

**What this means in practice:**
During the execution of any Domain Core function — from the moment it is called to the moment it returns — the function MUST NOT:
- Read from a database
- Write to a database
- Read from a file
- Write to a file
- Make a network request
- Access or modify a global variable
- Produce any output other than its return value
- Call any function that does any of the above

All data the function needs MUST arrive as parameters. All results MUST be returned explicitly. Nothing enters or leaves through side channels.

**VIOLATIONS — apply to any file with a Domain Core layer role:**
```python
# VIOLATION — queries database mid-calculation
def analyze_venue(self, venue: str) -> VenueReport:
    df = self.dal.get_matches(venue=venue)    # I/O inside Domain Core
    return self._calculate(df)

# VIOLATION — reads a file mid-calculation
def load_weights(self) -> Dict[str, float]:
    with open("weights.json") as f:           # File I/O inside Domain Core
        return json.load(f)

# VIOLATION — modifies global state as a side effect
def calculate_win_rate(self, df: pd.DataFrame) -> float:
    result = (df["winner"] == self.team).mean()
    GLOBAL_CACHE["last_result"] = result      # Global mutation inside Domain Core
    return result

# CORRECT — all data arrives as parameters, result returned explicitly
def analyze_venue(
    self,
    match_df: pd.DataFrame,
    venue: str
) -> VenueReport:
    filtered = match_df[match_df["venue"] == venue]
    return self._calculate(filtered)
```

**HARD STOP:** If you are working on a Domain Core file and it performs any I/O, reads any file, or touches any global variable during execution — stop the task immediately and report a Critical Boundary Violation before making any other change.

---

### Mandate 2: Hexagonal Purity (The Air Gap)

**APPLIES TO:** Any file whose layer role is Domain Core or Data Access. This mandate defines what these files are forbidden from knowing about.

**PRINCIPLE:**
The cricket domain — calculating a win probability, a player's economy rate, a venue bias — is completely blind to the infrastructure that surrounds it. A Domain Core file does not know whether it is being called by a FastAPI server, a Jupyter notebook, a unit test, or a command-line script. It does not know that DuckDB exists. It does not know that JSON exists. It speaks one language: DataFrames in, TypedDicts out.

This is the Hexagonal Architecture guarantee: you can swap the entire infrastructure — replace FastAPI with Flask, replace DuckDB with PostgreSQL, replace Next.js with Vue — and the domain core does not change by a single line. That guarantee is only maintained if the domain core is never allowed to import from the infrastructure layer.

**The Air Gap — data flows in one direction only:**
```
Infrastructure (api/, scripts/, frontend/)
        ↓  DataFrames and validated inputs flow inward
    Domain Core (engines, calculators, services)
        ↓  TypedDicts and primitives flow outward
Infrastructure (api/, scripts/, frontend/)
```

Nothing else crosses this boundary. No infrastructure object, no framework class, no database connection, no HTTP request or response ever enters the domain core.

**How to identify an infrastructure import:**
An import is an infrastructure import if the imported module has knowledge of how data is stored, served, rendered, or transmitted. If removing it would require knowing about the database engine, the web framework, the filesystem layout, or the network — it is an infrastructure import and it does not belong in a Domain Core file.

**VIOLATIONS — apply to any file with a Domain Core or Data Access layer role:**
```python
# VIOLATION — database framework imported in Domain Core
import duckdb                              # Database awareness
from sqlalchemy.orm import Session         # ORM awareness

# VIOLATION — web framework imported in Domain Core
from fastapi import HTTPException          # Framework awareness
import requests                            # Network awareness
from flask import request                  # Framework awareness

# VIOLATION — filesystem access in Domain Core
import os                                  # Filesystem awareness
from pathlib import Path                   # Filesystem awareness
import json                                # Acceptable only for data structures,
                                           # not for json.load(open(...)) patterns

# VIOLATION — API layer object passed into Domain Core
def analyze(self, request: Request) -> dict:   # FastAPI Request in domain
    team = request.json["team"]
    ...

# CORRECT — Domain Core imports only domain types and standard computation
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from core.interfaces.team_types import VenueReport, FormatRulesMap
from core.interfaces.player_interface import PlayerProfile
```

**HARD STOP:** Any infrastructure import found in a Domain Core file is a Critical Boundary Violation. Stop the task. Remove the import. Report the violation before proceeding with any other change.

---

### Mandate 3: Data-Oriented Design (DOD) — Hardware-Aware Computation

**APPLIES TO:** Any file that performs operations on collections of data — DataFrames, arrays, lists of records, or any structure containing more than one row. This includes Domain Core files, calculators, services, and any utility that processes tabular data.

**PRINCIPLE:**
How you write a calculation determines whether it runs in 2 milliseconds or 20 seconds on this hardware. On the Ryzen 5 3500U, a scalar Python loop over a DataFrame row-by-row is 10 to 100 times slower than the equivalent vectorized NumPy or Pandas operation — because scalar loops cannot use the CPU's SIMD instruction set or fill the L3 cache efficiently. In a trading tool where latency matters, this is not a style preference. It is a correctness requirement.

**Hardware reality — understand this before writing any calculation:**
The application runs on a Ryzen 5 3500U with approximately 4 GB of usable RAM after the operating system, IDE, and browser have taken their share. There is no cloud. There is no more RAM. Every calculation must be written with this constraint as a first-class concern — not as an afterthought.

**The core rule:**
Every operation that processes more than one row of data MUST be expressed as a vectorized operation using NumPy or Pandas. The CPU processes entire arrays in parallel using SIMD instructions. Python loops process one element at a time. These are not equivalent approaches with different syntax — they are fundamentally different execution models with a 10–100× performance difference on this hardware.

**How to identify a vectorization violation:**
A vectorization violation exists when you can see a Python `for` loop, `.iterrows()`, or `.itertuples()` being used to compute a result that could be expressed as a Pandas or NumPy operation across the whole array at once.

**VIOLATIONS — apply to any file performing tabular data operations:**
```python
# VIOLATION — scalar loop with row-by-row calculation
results = []
for index, row in df.iterrows():
    results.append(row["runs"] / row["balls"] * 100)
strike_rates = pd.Series(results)

# VIOLATION — itertuples is equally forbidden
for row in df.itertuples():
    if row.wickets > 3:
        high_impact.append(row.player)

# VIOLATION — manual index access in a loop
economy_rates = []
for i in range(len(df)):
    economy_rates.append(df.iloc[i]["runs"] / df.iloc[i]["overs"])

# CORRECT — vectorized arithmetic across the entire array simultaneously
strike_rates = (df["runs"] / df["balls"] * 100)

# CORRECT — boolean mask, no loop
high_impact = df[df["wickets"] > 3]["player"].tolist()

# CORRECT — vectorized column arithmetic
economy_rates = df["runs"] / df["overs"]
```

**The memory corollary:**
Vectorization and memory are linked. A scalar loop that builds a Python list and then converts it to a NumPy array creates two full copies of the data simultaneously. A vectorized operation works in-place on the existing array. On 4 GB of RAM, the difference between these two approaches can determine whether the application runs or crashes during a live session.

**HARD STOP:** Any `.iterrows()`, `.itertuples()`, or Python `for` loop used to compute a mathematical result that could be vectorized is a Critical Violation. Stop the task. Rewrite the operation as a vectorized expression. Do not add the loop and plan to fix it later.

---

### Mandate 4: Single Responsibility Principle (SRP) — One Reason to Change

**APPLIES TO:** Every file in the codebase without exception. SRP is not a Domain Core rule. It is a universal rule. It applies to API files, engine files, utility files, frontend components, ETL scripts, and test files equally.

**PRINCIPLE:**
A unit of code — whether a function, a class, or a file — has a Single Responsibility when you can describe its entire purpose without using the word "and."

If you find yourself saying "this function filters the data AND calculates the win rate" — that is two responsibilities. If you say "this file handles venue analysis AND player matching AND form calculation" — that is three responsibilities. Each "and" is a decomposition boundary that must be resolved before the code is considered complete.

**Why this matters beyond clean code:**
SRP is what makes this codebase survivable as it grows. A function with one responsibility has one reason to change. A function with three responsibilities has three reasons to change — and every change to one responsibility risks breaking the other two. In a trading tool that will expand to multiple formats and live match analysis, functions that do too many things become unmaintainable faster than any other form of technical debt.

**The decomposition hierarchy — apply at the correct level:**

| What you observe | What it means | How to fix it |
|---|---|---|
| A function does two things | Function-level SRP violation | Split into two private methods in the same class |
| A class manages two concerns | Class-level SRP violation | Split into two classes |
| An engine handles two analytical domains | Module-level SRP violation | Extract one domain into a dedicated Calculator class |
| A file has three or more domains | File-level SRP violation | Split into multiple files, each owning one domain |

**The 30-line rule — understood correctly:**
The engineering standards state that a function exceeding 30 lines MUST be decomposed. This is a heuristic — a reliable warning sign — not the definition of SRP itself. A function that exceeds 30 lines is almost always doing more than one thing. But the question to ask is not "is this function over 30 lines?" — it is "can I describe this function's purpose without using the word 'and'?" If yes and it happens to be 35 lines, document the justification. If no and it is only 20 lines, decompose it anyway — because SRP is about responsibility, not line count.

**The file-size corollary:**
A file exceeding 500 lines is a warning. A file exceeding 800 lines is a violation requiring decomposition before new features are added. The correct decomposition at the file level is to extract focused Calculator classes, each owning one analytical domain — for example: `VenueCalculator`, `FormCalculator`, `MatchupCalculator`, `PhaseCalculator`.

**VIOLATIONS — apply to every file in the codebase:**
```python
# VIOLATION — function does two things (filtering AND calculating)
def get_venue_win_rate(
    self, match_df: pd.DataFrame, venue: str
) -> float:
    # Responsibility 1: filter
    venue_df = match_df[match_df["venue"] == venue]
    home_df = venue_df[venue_df["team_bat_1"] == self.team]
    # Responsibility 2: calculate
    wins = (home_df["winner"] == self.team).sum()
    return wins / len(home_df) if len(home_df) > 0 else 0.0

# CORRECT — one function, one responsibility
def _filter_venue_matches(
    self, match_df: pd.DataFrame, venue: str
) -> pd.DataFrame:
    venue_df = match_df[match_df["venue"] == venue]
    return venue_df[venue_df["team_bat_1"] == self.team]

def _calculate_win_rate(self, df: pd.DataFrame) -> float:
    if len(df) == 0:
        return 0.0
    return (df["winner"] == self.team).sum() / len(df)

def get_venue_win_rate(
    self, match_df: pd.DataFrame, venue: str
) -> float:
    filtered = self._filter_venue_matches(match_df, venue)
    return self._calculate_win_rate(filtered)
```

**HARD STOP:** Any new function submitted for review that cannot be described without using the word "and" is rejected without exception. Decompose it first, then submit.

---

### Mandate 5: Event-Driven State (The Live Bridge)

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

### Mandate 6: WebSocket-First Real-Time Communication

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


## PART 1: ARCHITECTURAL TOPOLOGY & THE 6 PARADIGMS

The application follows a strict Hexagonal / Port-and-Adapter architecture. The layer roles defined in Part 0 map to the following directory structure in the current project. Layer boundaries are enforced by the compliance bouncer and by code review. Agents MUST NOT violate layer boundaries under any circumstances.

### Layer Map (Current Project Topology)

| Layer Role | Current Location | Responsibility | What It MUST NOT Do |
|---|---|---|---|
| **UI Adapter** | `frontend/` | Render pre-computed API responses | Contain domain logic, formulas, or format-specific conditions |
| **Interface Adapter** | `api/` | Map JSON to domain functions via manifest; serialize responses | Execute business logic or touch the DAL directly |
| **Application Core** | `core/` | ABCs, DAL, format-agnostic utilities | Contain format-specific concrete logic or default to any single format |
| **Concrete Strategy** | `formats/{fmt}/engines/` | Format-specific engine implementations | Import infrastructure libraries or bypass the DAL |
| **ETL Infrastructure** | `scripts/` | Data extraction, transformation, DuckDB ingestion | Be called at API runtime |
| **Live Layer** | `core/live/`, `api/live/` | Live state singleton, scraper, WebSocket broadcaster | Query DuckDB, perform file I/O, block the event loop |

---

### Paradigm 1: Manifest-Driven UI

**Rule:** The UI is dynamically generated from the backend manifest. To add any new UI feature — a chart, a dropdown, a new stat panel, a new analysis category — you MUST declare it first in `formats/{fmt}/manifest.py`.

**Constraint:** AI agents MUST NOT add hardcoded UI components to Next.js for domain features unless that feature is formally registered in the corresponding backend manifest. The manifest is the contract. The UI is the renderer.

**Hard Stop:** Any React component that hardcodes a function name, category name, or analysis type that is not registered in the manifest is a Hard Fail.

---

### Paradigm 2: The DAL Fortress

**Rule:** `core/data_access.py` is the absolute and exclusive gatekeeper to DuckDB. No other file in the codebase may communicate with DuckDB directly.

**Constraint:** Analytical engines (`TeamEngine`, `PlayerEngine`) MUST NEVER instantiate `duckdb.connect()` or execute raw SQL. Engines MUST query the DAL exclusively. The DAL MUST enforce read-only connections (`read_only=True`) during API runtime. Write access to DuckDB is permitted only in ETL scripts during a database rebuild — never at runtime.

**Hard Stop:** Any `duckdb.connect()` call found outside of `core/data_access.py` and `scripts/` is a Critical Boundary Violation.

---

### Paradigm 3: Strict Strategy Pattern (Format Agnosticism)

**Rule:** The system supports multiple formats (ODI, T20I, The Hundred, Women's variants) without tight coupling. Adding a new format MUST NOT require modifying existing format code.

**Constraint:** Factory routers (e.g., `get_team_engine()`) MUST explicitly require a `format_key` — no defaults, no fallbacks. They MUST enforce runtime compliance by checking `issubclass(ConcreteEngine, ICoreInterface)`. Concrete engines MUST implement all `@abstractmethod` signatures defined in their `core/interfaces/` ABC. A concrete engine that does not fully implement its ABC is a deployment blocker.

**Hard Stop:** Any hardcoded `"odi"` string found in `core/` as a default fallback is a Hard Fail.

---

### Paradigm 4: ETL Immutability & Atomic Swaps

**Rule:** The production DuckDB database is immutable at API runtime. It is a read-only artefact produced by the ETL pipeline.

**Constraint:** AI agents MUST NEVER write scripts to `ALTER TABLE`, `UPDATE`, or `INSERT` directly into the live `odi.duckdb` database. All schema or data modifications MUST be implemented in `formats/{fmt}/utils/refinery_script.py` and deployed via the full 4-stage `update_data.py` pipeline using the Atomic Temp DB Swap methodology. The swap guarantees zero downtime and zero partial-write corruption.

**Hard Stop:** Any script that writes directly to `odi.duckdb` outside of the ETL pipeline is a Critical Data Integrity Violation.

---

### Paradigm 5: The Pre-Computed Payload Mandate

**Rule:** The frontend MUST NOT parse strings, evaluate thresholds, or perform calculations to derive UI state. Every UI decision — badge colour, warning flag, chart threshold, form indicator — MUST be pre-computed by the Python backend and included explicitly in the API JSON payload.

**Constraint:** AI agents MUST NEVER write string-manipulation logic (e.g., `val.match(...)`) or statistical thresholds (e.g., `if (n < 3)`) inside React components to generate warnings, badges, or flags. The backend sends pre-computed booleans and tagged primitives. The UI maps those values to pixels.

**Exception:** Pre-submission client-side form validation — checking if a user has selected enough players or filled required context fields before clicking Execute — is exempt. Basic length and boolean checks on user inputs to manage local button states are permitted.

**Hard Stop:** Any React component performing arithmetic, string parsing, or statistical comparison on API response data is a Hard Fail.

---

### Paradigm 6: Observer Pattern (Live State Reactivity)

**Rule:** The live match singleton is the single observable subject. Connected frontend clients are observers. When the scraper updates the singleton, all connected clients are notified automatically — without polling, without repeated HTTP requests.

**Constraint:** AI agents MUST NOT implement live updates by having the frontend call the standard `/execute/{function_key}` HTTP endpoint on a timer. That endpoint is for historical analysis only and MUST NOT be repurposed for live data. Live updates flow exclusively through the WebSocket broadcast channel defined in `api/live/`.

**State Flow — Strictly One-Directional. Must Never Be Reversed:**
```
Scraper (every 10s)
    → acquires threading.Lock()
    → writes delta to LiveMatchState singleton
    → releases lock
    → triggers WebSocket broadcast (delta only — not full state)
    → Next.js WebSocket hook receives push event
    → React state updates
    → UI re-renders
```

**Delta-Only Broadcasts:** The WebSocket broadcast MUST send only the fields that changed — not the entire state object. Full state serialization on every 10-second cycle is wasteful and increases client-side re-render cost unnecessarily.

**Separation of Concerns:** The Observer pattern applies ONLY to `core/live/` and `api/live/`. The historical analysis layer (`formats/{fmt}/engines/`, `api/main.py`) remains purely request-response and MUST NOT be modified to support push semantics.

**Hard Stop:** Any polling implementation, any `setInterval` calling `/execute/`, or any WebSocket handler embedded in `api/main.py` rather than `api/live/` is a Critical Architecture Violation.

---

## PART 2: THE CODING CONSTITUTION (Tactical Execution)

Every rule in this section is a hard constraint. "I didn't know" is not an acceptable explanation for a violation.

---

### 2.1 Python Engineering Standards

**1. The Typed Truth:** Every function signature MUST have strict Python type hints. No exceptions. Return types MUST always be declared. `None` return types MUST be explicitly marked as `-> None`.
```python
# CORRECT
def get_stats(df: pd.DataFrame, team: str) -> Dict[str, float]:

# VIOLATION — no type hints
def get_stats(df, team):
```

**2. Vectorization Mandate (DOD):** Analytical calculations MUST utilize Pandas and NumPy vectorization. AI agents MUST NEVER use `for index, row in df.iterrows():` for mathematical aggregations. Vectorized operations run 10–100× faster and consume a fraction of the memory on the Ryzen 5.

**3. The Pydantic Shield:** Every FastAPI endpoint MUST define incoming requests and outgoing responses using strict `pydantic.BaseModel` schemas. Validation MUST occur at the API boundary — before the payload reaches the engine layer. Engines MUST NOT receive unvalidated raw dicts.

**4. Crash Early, Crash Loud:** Bare exceptions are forbidden. AI agents MUST NEVER write `try: ... except Exception: pass`. Catch specific, expected errors (`KeyError`, `ValueError`, `TypeError`). Swallowing exceptions silently produces wrong results that are indistinguishable from correct results — the most dangerous failure mode in a trading tool.

**5. Skeleton Prohibition:** Unimplemented functions MUST NEVER silently return fake data, empty structures, or default zeros. Any function whose body is not yet implemented MUST raise `NotImplementedError` with a message explaining why the function is unimplemented and where the rebuild requirements are documented.
```python
# VIOLATION — silent fake return
def run_simulation(self):
    pass  # or return 0, or return {}

# CORRECT
def run_simulation(self) -> SimulationResult:
    raise NotImplementedError(
        "run_simulation() is pending Phase 12 rebuild. "
        "See core/backtester.py for rebuild requirements."
    )
```

**6. Source of Truth:** Hex colours, team mappings, venue aliases, and format constants MUST be referenced from `config/` or `formats/{fmt}/config/`. They MUST NEVER be hardcoded into engine or UI files.

**7. Ephemeral Branches:** Do not create `temp_test.py`, `debug_script.py`, or `scratch.py` in the main codebase. All experimental code MUST reside in a git branch and MUST be deleted post-merge. The main branch is always production-ready.

**8. Module Naming:** All Python module filenames MUST use `snake_case`. Hyphens in filenames break Python import conventions and create friction across hooks and scripts. Any hyphenated filename MUST be renamed before the module is extended.

---

### 2.2 Tactical Frontend Execution Rules

**1. The API Wrapper Mandate:** Never write raw `fetch()` calls inside React components. AI agents MUST use the standardised API wrappers inside `frontend/lib/api.ts` (e.g., `executeFunction()`). This ensures consistent error handling, auth headers, and base URL management across all API calls.

**2. Strict Tailwind CSS:** Styling MUST be handled exclusively by Tailwind CSS utility classes. AI agents MUST NEVER use React inline `style={{ ... }}` attributes unless dynamically calculating a progress bar width or an absolute chart coordinate — where the value is computed at runtime and cannot be expressed as a static class.

**3. Global State Purity:** Rely solely on React Context for global state. AI agents MUST NOT introduce Redux, Zustand, MobX, or any other state management library. All global state MUST be managed inside `frontend/lib/context.tsx` (`AppProvider`) and accessed via `useAppContext()`.

**4. Component Modularity:** UI files MUST be strictly partitioned. AI agents MUST NOT create monolithic React components exceeding 300 lines. Complex UI elements MUST be decomposed into focused sub-components.

**5. No Domain Logic in the Frontend:** React components MUST NOT contain cricket domain logic, statistical formulas, or format-specific conditional branches. All domain decisions are made in Python and delivered as pre-computed values in the API response.

**6. TypeScript Strict Mode:** All frontend code MUST be written in TypeScript. The use of `any` as a type annotation in TypeScript is forbidden. Every API response type MUST be defined in `frontend/lib/types.ts` and used consistently.

---

### 2.3 Memory Management Standards (4 GB Hard Budget)

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

### 2.4 Thread-Safety Standards (Live Singleton Integrity)

These rules govern the two concurrent threads — the background scraper and the FastAPI request handler — that share the `LiveMatchState` singleton in Phase 12.

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

## PART 3: THE MODIFICATION & WORKFLOW PROTOCOL

AI agents executing tasks MUST follow these exact workflows. Skipping a step is not permitted. If a step cannot be completed, the agent MUST stop and report — not proceed.

---

### Workflow A: Bug Fixes (The RCA Trace)

When diagnosing a bug, trace backwards through the layers. Do not mutate the engine until every upstream layer has been verified.

1. **Frontend:** Did Next.js send the correct request payload?
2. **API / Manifest:** Did Pydantic validate the input? Did the serializer strip or transform a field?
3. **Engine:** Is the mathematical calculation in the concrete engine correct?
4. **DAL:** Did the DAL construct the correct DuckDB query?
5. **ETL:** Is the data actually missing or corrupted in the source CSV or DuckDB table?

Do not mutate code at layer N until you have confirmed layer N+1 is correct.

---

### Workflow B: Adding New Features (Outside-In)

To implement a new analytical feature, follow this exact sequence. Steps MUST NOT be skipped or reordered.

1. **Define Contract:** Update `manifest.py` and `api/schemas/` to define the input and output shape. Nothing is built until the contract exists.
2. **Implement Logic:** Write the math in the Concrete Engine (`formats/{fmt}/engines/`). Ensure the implementation satisfies the ABC Interface in `core/interfaces/`.
3. **Truth Bridge:** Add a regression test that asserts the engine returns the exact structure promised by the Pydantic schema.
4. **UI Implementation:** Implement the Next.js visual component to consume the newly registered manifest endpoint.

---

### Workflow C: System Modifications (Safe Mutation)

- **Database Schema Changes:** MUST flow through ETL modifications (`json_converter.py` → `refinery_script.py`) followed by an Atomic Swap rebuild. Direct schema modifications to `odi.duckdb` are forbidden.
- **Mathematical Changes:** If an engine formula is intentionally altered, the resulting Truth Bridge test failures MUST be acknowledged and new "Golden Master" JSON outputs MUST be generated to baseline the new math.
- **API Response Changes:** Endpoint outputs MUST be additive. AI agents MUST NOT rename or remove existing JSON keys in serializers unless the Next.js frontend consuming those keys is simultaneously refactored in the same task.
- **Deletion Tasks:** When any function, endpoint, or class is deleted, the agent MUST search the entire codebase for all references to the deleted artefact and clean them up in the same task. A deletion is not complete until zero references remain in live code.

---

### The "Zero-Literal" Law (Source of Truth)

**Violation:** Hardcoding tactical windows, match limits, year thresholds, or fallback constants (e.g., `[:10]`, `year=2015`, `fallback=6`, `overs=50`).

**The Mandate:** No numeric or string literals related to business or cricket logic are permitted in any analytical file — regardless of its directory location. All constants MUST be defined in `manifest.py` and accessed via the injected `self.rules` or `format_rules` context.

**Audit Trigger:** Any integer or float found in an analytical method that is not `0` or `1` (used as counters or binary flags) is a Hard Fail.

---

### The "Derivative Literal" Law (No Math Hiding)

**The Cheat:** Using `100`, `/ 6`, or `0.5` because they seem like "standard math."

**The Law:** All numeric coefficients — even "obvious" ones like percentage divisors or sports-specific units — MUST be named constants in the manifest.

**Why:** If the format changes (e.g., a "100-ball" game), a `/ 6` for overs becomes a silent bug that produces wrong predictions without raising any error.

**Audit Trigger:** Any division by a raw integer or multiplication by a raw float in an analytical file is a Hard Fail.

---

### The "Visual Silence" Law (Presentation Purity)

**Violation:** Any analytical file returning UI-friendly strings like `"DNB"`, `"N/A"`, `"-"`, `"Bat Form"`, `"their last 5"`, or any human-readable label.

**The Mandate:** Domain Core files are Visual-Deaf. They process and return Raw Primitive Data (`float`, `int`, `bool`, `None`) or Domain Objects (TypedDicts, dataclasses). Human-readable labelling, placeholder logic, and narrative string assembly are strictly reserved for the `ReportFormatter` and the frontend.

**Audit Trigger:** Any string literal containing non-technical, human-readable descriptors found in a Domain Core return value is a Hard Fail.

---

### The "Anti-Grease" Law (Typed Truth)

**Violation:** Using `Any`, bare `Dict`, `**kwargs`, or `object` to pass data between layers.

**The Mandate:** The use of `Any` is officially deprecated and forbidden in all method signatures in Domain Core files. All complex data structures MUST be defined as `pydantic.BaseModel` or `TypedDict`. Every function MUST have a return type hint. `None` returns MUST be explicitly marked as `-> None`.

**The Object-is-Any Extension:** Replacing `Any` with `object` or `Dict[str, object]` to pass the linter while keeping data blind is equally forbidden. `object` is `Any` in a tuxedo.

**Audit Trigger:** A grep for `: Any`, `: object`, or `-> Dict[str, object]` in any Domain Core file is a Hard Fail.

---

### The "I/O Air-Gap" Law (Execute-Path Purity)

**Violation:** Calling `os.path`, `open()`, `pd.read_csv()`, `duckdb.query()`, or any file-system or network operation inside an execute path.

**The Mandate:** The execute path MUST be Purely Computational. All data MUST be pre-loaded at startup and injected as DataFrames. No file or database access is permitted once the server has started serving requests.

**Audit Trigger:** Any file-system or database-driver import found in a Domain Core file is a Hard Fail.

---

### The "Pure Primitive" Mandate

**The Cheat:** Returning `f"{team_id}_stats"` or `team_name + " Form"` from an engine or service.

**The Law:** Domain Core files may only return primitives (`int`, `float`, `bool`) or `None` as scalar values. Any string concatenation involving domain data inside a Domain Core file is a Presentation Leak.

**Why:** Strings are for humans. Data is for systems. Mixing them in the domain core makes the output untestable, unlocalizable, and format-dependent.

---

### The "Stale Test" Law (Truth Bridge Integrity)

**Violation:** A test file asserting the behaviour of a function, endpoint, or schema that no longer exists in the codebase.

**The Mandate:** When any endpoint, function, or API schema is removed or renamed, its corresponding test MUST be removed or updated in the same task.

**Workflow:** When removing any function or endpoint, the agent MUST search the entire `tests/` directory for references to that artefact before marking the removal task complete. Any matching test MUST be either rewritten or explicitly disabled:
```python
# TEST DISABLED — [function name] removed — pending [Phase X] rebuild
# See [file path] for rebuild requirements.
```

**Audit Trigger:** Any test file containing a call to a function, class, or URL that does not exist in the current codebase is a Hard Fail.

---

### The "Skeleton Prohibition" Law (Extended Crash Early, Crash Loud)

**Violation:** Any function whose body is `pass`, `return {}`, `return []`, `return 0`, or `return None` when those returns represent unimplemented logic rather than a legitimate empty result.

**The Mandate:** Unimplemented functions MUST raise `NotImplementedError` with a descriptive message.
```python
# VIOLATION
def run_simulation(self):
    pass

# CORRECT
def run_simulation(self) -> SimulationResult:
    raise NotImplementedError(
        "run_simulation() is pending Phase 12 rebuild. "
        "See core/backtester.py for rebuild requirements."
    )
```

**Audit Trigger:** Any non-trivial method body consisting solely of `pass` or a bare default return in a Domain Core file is a Hard Fail.

---

## PART 4: PHASE 12 COMPLIANCE GATE

No code enters Phase 12 without passing every gate in this section. These are not suggestions. They are deployment blockers.

---

### 4.1 Mandatory Gatekeeper

From this phase onward, **no code may be committed** unless `core/utils/compliance-bouncer.py` returns:

```
PASS: 100% compliance
```
This is GATE 6 in the six-gate sentinel sequence defined in section 4.3. Gates 1-5 must pass before GATE 6 is reached.

Blocking command:
```powershell
python core/utils/compliance-bouncer.py --root .
```

A single violation is sufficient to block the commit. Fix the violation. Re-run the bouncer. Only then proceed.

**What the bouncer enforces (10 rules):**
- `ZERO_LITERAL` — hardcoded literals not declared in manifest registries
- `ANTI_ANY` — `Any` or `object` in type signatures
- `MISSING_RETURN_TYPE` — missing return annotations on functions
- `IO_AIR_GAP` — file or OS I/O inside engine execute paths
- `PRESENTATION_PURITY` — UI strings in service layer (formatters are exempt)
- `DOD_VIOLATION` — scalar loops (`.iterrows()` / `.itertuples()` forbidden)
- `BOUNDARY_VIOLATION` — infrastructure imports in Domain Core files
- `CONSTITUTIONAL_VISUAL_SILENCE` — visual tokens inside `core/`
- `CONSTITUTIONAL_TYPED_TRUTH` — deprecated or legacy imports in engines and calculators
- `CONSTITUTIONAL_ANTI_GREASE` — `Dict[str, Any]` or `object` in signatures

---

### 4.2 Git Commit Enforcement (Local)

The repository includes `.githooks/pre-commit` to enforce the compliance gate at commit time.

Enable once per clone:
```powershell
git config core.hooksPath .githooks
```

This hook MUST be enabled. Commits made without the hook active are non-compliant regardless of bouncer output.

---

### 4.3 Sentinel Order of Execution

Validation skills are mandatory gates — not optional. Every code-modifying task MUST pass all applicable gates in the order below before it is considered complete. Skipping any gate is a HARD FAIL.

Skills are divided into two types:
- **Guide skills** — instruct the agent how to perform a task correctly.
- **Validation skills** — verify the work done is architecturally correct.

Only validation skills appear in this gate sequence.

---

**GATE 1 — boundary-sentinel**
Trigger: any modification to `core/` files.
```powershell
python core/gen_ai/skills/validators/
boundary-sentinel/scripts/run_sentinel.py
--root . --paths core/
```
Pass condition: zero cross-layer import violations, zero `self.dal` usage outside DAL, zero `duckdb.connect()` outside `core/data_access.py`.

---

**GATE 2 — duckdb-lint-ops (DOD lint only)**
Trigger: any modification to `calculators/`, `engines/`, or `services/`.
```powershell
python core/gen_ai/skills/guides/
duckdb-lint-ops/scripts/run_lint.py --root .
```
Pass condition: zero `.iterrows()` / `.itertuples()` violations.

---

**GATE 3 — manifest-contract-verifier**
Trigger: any modification to `manifest.py` or any engine file in `formats/`.
```powershell
python core/gen_ai/skills/validators/
manifest-contract-verifier/scripts/
run_verifier.py --root .
--manifest formats/odi/manifest.py
```
Pass condition: all `engine_class` / `engine_method` contracts verified, all `required_context` fields map to valid engine parameters.

---

**GATE 4 — serialization-guard**
Trigger: any modification to `api/serializers.py` or engine return types.
```powershell
python core/gen_ai/skills/validators/
serialization-guard/scripts/run_lint.py
--root . --paths api/serializers.py
--max-record-rows 500
```
Pass condition: zero memory bombs, zero high-latency recursive serialization patterns.

---

**GATE 5 — paradigm-sentinel (meta-gate)**
Trigger: always — runs after all primary gates pass.
Follow instructions in:
`core/gen_ai/skills/validators/
paradigm-sentinel/SKILL.md`
Pass condition: zero violations across all paradigm checks including boundary scan, DAL bypass probe, and bouncer gate.

---

**GATE 6 — compliance-bouncer (final gate)**
Trigger: always — last step before every commit.
```powershell
python core/utils/compliance-bouncer.py
--root .
```
Pass condition: `PASS: 100% compliance`.

---

**Dormant gates (activate when phase ships):**
- `event-state-linter` — activate when `core/live/` is created in Phase 12. Insert as GATE 3.5 between manifest-verifier and serialization-guard.

---

The bouncer is a final gate — not a substitute for the skill gates. All six gates must pass in sequence. A task is COMPLETE only when GATE 6 returns `PASS: 100% compliance`.

---

### 4.4 Non-Negotiable Block Condition

Any `FAIL` from `compliance-bouncer.py` is a hard stop for merge and release readiness. No exceptions. No deadline overrides this rule. Fix the violation first.

---

### 4.5 Memory Baseline Gate (Phase 12 Readiness)

Before any Phase 12 code is merged, the application's memory footprint at startup MUST be measured and recorded. The baseline MUST be under 800 MB RSS.

Measurement command (run after backend starts):
```python
import psutil, os
process = psutil.Process(os.getpid())
print(f"RSS: {process.memory_info().rss / 1024**2:.1f} MB")
```

Current baseline: ~247 MB. Phase 12 live layer adds approximately 10–30 MB. Both are well within the 4 GB budget — but this MUST be re-verified after any significant feature addition.

---

## PART 5: AGENTIC SKILLS

### 5.1 Project-Local Skill Registry (Authoritative)

All agentic governance skills are internalized in the repository and MUST be referenced from project-local paths only. Global user-profile skill paths (`~/.codex/skills/`) are non-authoritative and MUST NOT be used.

Current project skills:
**Guide skills** (`core/gen_ai/skills/guides/`):
- `core/gen_ai/skills/guides/duckdb-lint-ops/`

**Validation skills** 
(`core/gen_ai/skills/validators/`):
- `core/gen_ai/skills/validators/boundary-sentinel/`
- `core/gen_ai/skills/validators/event-state-linter/`
- `core/gen_ai/skills/validators/executive-auditor/`
- `core/gen_ai/skills/validators/manifest-contract-verifier/`
- `core/gen_ai/skills/validators/paradigm-sentinel/`
- `core/gen_ai/skills/validators/serialization-guard/`

**System skills** (`core/gen_ai/skills/.system/`):
- `core/gen_ai/skills/.system/skill-creator/`
- `core/gen_ai/skills/.system/skill-installer/`

When creating new skills, place them in the 
correct typed subdirectory:
- Guide skills: 
  `core/gen_ai/skills/guides/[skill-name]/`
- Validation skills: 
  `core/gen_ai/skills/validators/[skill-name]/`

---

### 5.2 Logic Gate Requirement (Pre-Bouncer)

Before a task can be marked ready for a 
`compliance-bouncer` PASS, the following 
logic gates MUST be executed in order and 
pass criteria recorded. This sequence mirrors 
section 4.3 exactly.

**GATE 1 - boundary-sentinel**
Trigger: any modification to `core/` files.
Path: `core/gen_ai/skills/validators/
boundary-sentinel/`

**GATE 2 - duckdb-lint-ops (DOD lint)**
Trigger: any modification to `calculators/`, 
`engines/`, or `services/`.
Path: `core/gen_ai/skills/guides/duckdb-lint-ops/`

**GATE 3 - manifest-contract-verifier**
Trigger: any modification to `manifest.py` 
or any engine file in `formats/`.
Path: `core/gen_ai/skills/validators/
manifest-contract-verifier/`

**GATE 4 - serialization-guard**
Trigger: any modification to 
`api/serializers.py` or engine return types.
Path: `core/gen_ai/skills/validators/
serialization-guard/`

**GATE 5 - paradigm-sentinel (meta-gate)**
Trigger: always - after all primary gates pass.
Path: `core/gen_ai/skills/validators/
paradigm-sentinel/`

**GATE 6 - compliance-bouncer (final gate)**
Trigger: always - last step before every commit.
Command: `python core/utils/compliance-bouncer.py 
--root .`

Dormant: `event-state-linter` activates when 
`core/live/` is created in Phase 12. Insert 
as GATE 3.5.

`compliance-bouncer.py` is a final gate - 
not a substitute for the skill gates. 
All six gates must pass. A task with missing 
gate results is `FAIL` regardless of bouncer 
output.

---

### 5.3 Hard-Stop Condition

If any required skill gate fails, a stale 
or pre-restructure path is referenced 
(e.g. `core/gen_ai/skills/boundary-sentinel/` 
instead of 
`core/gen_ai/skills/validators/boundary-sentinel/`),
or gate results are missing from the task 
report, compliance status is `FAIL` regardless 
of bouncer output. The task is not complete.

---

### 5.4 Agent Context Requirement (Session Startup)

Every AI agent session that involves code changes MUST begin with the following three documents attached or pasted into the context window:

1. This engineering standards document (full text) — `docs/guides/engineering_standards.md`
2. The current technical audit report — `docs/guides/TECHNICAL_AUDIT_REPORT.md`
3. The AI memory log — `docs/ai/AI_MEMORY.md`

An agent that begins a task without these three documents has insufficient context to make safe architectural decisions. Any task started without this context MUST be restarted.

---

## PART 6: HIGH-IMPACT FILE REGISTRY

The following files carry disproportionate 
architectural risk. They are not frozen — 
legitimate refactoring will touch them. 
But any agent that modifies these files 
WITHOUT explicit instruction in the current 
task prompt has violated this standard.

---

### 6.1 The Rule

Before modifying any file in this registry,
the agent MUST:

1. **Stop.** Do not make the change yet.
2. **State explicitly** which registered file 
   it needs to modify and why.
3. **Produce an impact trace** — list every 
   other file that imports from or depends on 
   the file being modified.
4. **Wait for explicit confirmation** before 
   proceeding.

If the current task prompt already contains 
an explicit instruction to modify a registered 
file (e.g. "update team_types.py"), no 
additional confirmation is needed — the 
instruction IS the permission.

Modifying a registered file without either:
- an explicit instruction in the task prompt, 
  or
- a stop-state-trace-confirm sequence

is a hard architectural violation regardless 
of whether the bouncer passes.

---

### 6.2 The Registry

| File | Risk | Why |
|---|---|---|
| `core/data_access.py` | CRITICAL | Handles venue resolution, team hydration, and integrity validation. Every engine and service depends on it. A silent change here corrupts every downstream output. |
| `core/interfaces/team_types.py` | HIGH | Load-bearing type contract system. Adding new TypedDicts is safe. Removing or renaming existing types silently breaks engines, services, and serializers simultaneously with no immediate error. |
| `api/serializers.py` | HIGH | Small, complete, handles every known edge case. Changes here affect every API response. There is no routine reason to touch it. |

---

### 6.3 Files Removed From Registry

The following files were previously listed 
as Do-Not-Touch but have been removed because 
active refactoring requires them to be 
modifiable as normal workflow:

- `core/calculators/` — active refactoring 
  area. Protected by the compliance bouncer 
  and sentinel gates instead.
- `formats/odi/manifest.py` — touched 
  constantly as a normal side effect of 
  literal registration and feature additions. 
  Protected by manifest-contract-verifier 
  instead.
- `api/engine_pool.py` — too recently rebuilt 
  to be considered stable. Re-evaluate for 
  registry inclusion after Phase 12.

---

### 6.4 Registry Maintenance

This registry is a living document. After any 
major refactoring phase completes and a file 
is considered genuinely stable, it may be 
added to the registry. The criteria for 
addition are:

1. The file has not been modified in the last 
   two phases.
2. All downstream consumers are typed and 
   tested.
3. There is no known planned work that 
   requires modifying it.

Files are added to the registry by explicit 
architect instruction only — never by agent 
decision.

---

*End of Document — Version 2.2 — Last Updated: 2026-03-02*
*Any modification to this document requires architect approval and a version increment.*
