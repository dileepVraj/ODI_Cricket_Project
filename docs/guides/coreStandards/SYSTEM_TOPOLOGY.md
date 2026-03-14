# System Topology & Paradigms
# Part of: coreStandards
# Always load alongside MANDATES_1_TO_4.md — these two files are a functional unit.
# MANDATES_1_TO_4.md defines the principles. This file maps them to the current directory structure.
# Source: ENGINEERING_STANDARDS_BACKEND.md Part 1 (authoritative)

---

## PART 1: SYSTEM TOPOLOGY & PARADIGMS

The application follows a strict Hexagonal / Port-and-Adapter architecture. The layer roles defined in MANDATES_1_TO_4.md map to the following directory structure in the current project. Layer boundaries are enforced by the compliance bouncer and by code review. Agents MUST NOT violate layer boundaries under any circumstances.

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

*Part of coreStandards — always load alongside MANDATES_1_TO_4.md.*
*Authoritative source: ENGINEERING_STANDARDS_CORE.md*
