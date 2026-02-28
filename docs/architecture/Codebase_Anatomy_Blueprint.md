# Codebase Anatomy and Architecture Blueprint

This document provides a comprehensive architectural map of the Multi-format Cricket Algo-Trading Platform.

## 1. Global Directory Structure & Tech Stack Summary

### Global Directory Structure
```text
c:\Cricket_Project_Stable\
├── api/                  # FastAPI Application Layer (v2.0 Manifest-Driven)
│   ├── schemas/          # Pydantic validation schemas
│   ├── main.py           # FastAPI entry point & generic execute endpoint
│   ├── engine_pool.py    # Global format/engine pool manager
│   └── serializers.py    # Standardizes complex Engine data for JSON
├── config/               # Shared project configurations & mappings (Venues, Teams)
├── core/                 # Central Business Logic and Data Access
│   ├── interfaces/       # Abstract Base Classes (ABCs)
│   ├── data_access.py    # DuckDB Data Access Layer (DAL)
│   ├── team_engine.py    # Core Team statistical math execution
│   └── player_engine.py  # Core Player analysis & profile math
├── docs/                 # Intelligent Documentation & Handover guides
├── formats/              # Dynamically Loaded Formats (e.g., odi, t20)
│   └── odi/
│       ├── data/         # SQLite/DuckDB localized files
│       ├── engines/      # Format-specific engine implementations
│       ├── scripts/      # Format-tied ETL scripts
│       └── manifest.py   # The Truth Source for UI/UX (Manifest-Driven UI)
├── frontend/             # Next.js 16 Web Application
│   ├── app/              # App Router (page.tsx, layout.tsx, etc.)
│   ├── components/       # UI Components (Sidebar, Inputs, Formats)
│   └── lib/              # API Fetch wrappers and React Context Providers
└── scripts/              # Global orchestrators (ETL, Reconciliation, Truth Bridge)
    └── maintenance/      # update_data.py, memory_manager.py, etc.
```

### Tech Stack Summary
*   **Frontend Layer:** Next.js 16, React 19, Tailwind CSS (v4) / PostCSS, React Context API (`AppProvider`), and Lucide React.
*   **Backend Layer:** FastAPI, Uvicorn (ASGI server), Pydantic (data parsing/validation).
*   **Data / Database Layer:** DuckDB (In-memory/File-based vector database), Pandas, and NumPy for data computation and ETL transforms.

---

## 2. The Database Schema (DuckDB)

The Data Layer is powered by a locally hosted **DuckDB** instance (`formats/odi/data/odi.duckdb`), optimized for vectorized analytics. 

### Core Tables
*   `matches`: Stores high-level match summaries. Includes columns: `match_id`, `start_date`, `venue`, `team_bat_1`, `team_bat_2`, `winner`, `score_inn1`, `score_inn2`.
*   `balls`: Granular ball-by-ball facts. Includes columns: `match_id`, `innings`, `striker`, `bowler`, `runs_off_bat`, `extras`, `wicket_type`, `phase`, `batting_team`, `bowling_team`.
*   `player_stats`: High-level aggregated career statistics for batsmen/bowlers.
*   `player_batting_stats`: Vectorized aggregations specific to batting facts (total runs, strike rates, etc.).
*   `player_bowling_stats`: Vectorized aggregations specific to bowling facts (economy, wickets, etc.).
*   `phase_stats`: Ball data pre-grouped into strategic phases (e.g., Powerplay 1-10, Death Overs 41-50).
*   `squads`: Rosters connecting players to their national or franchise teams.
*   `player_metadata`: Player roles and physical attributes (e.g., "Right-Hand Bat").
*   `match_info`: Meta descriptions of conditions, toss outcomes, and umpires.

**Relationships:** `balls.match_id` references `matches.match_id`, acting as the primary dimension for temporal and venue-based joins. Most queries use Python string manipulation to parameterize SQL queries generated against these structured tabular schemas.

---

## 3. The Data Pipeline (ETL)

The ETL pipeline operates as a master "Intelligence Pipeline" automated via `scripts/maintenance/update_data.py`.

### Pipeline Flow
1. **Extraction (JSON to CSV):** Orchestrated by `formats.odi.utils.json_converter.run_json_conversion()`. Raw Cricsheet JSON files are parsed into flat CSV staging sheets.
2. **Transformation (Intelligence Refinery):** Orchestrated by `formats.odi.utils.refinery_script.rebuild_intelligence_layer()`. Derives phase data, fills missing values, canonicalizes names, and enriches data via Pandas manipulation.
3. **Ingestion (DuckDB):** Handled by `formats.odi.utils.ingest_to_db.run_db_ingestion()`. Translates the refined CSV artifacts into optimized DuckDB binary tables.
4. **Reconciliation & Validation:** Handled by `scripts/maintenance/etl_reconciliation_report.py`. Ensures database integrity contract checks post-ingestion (e.g., verifying `matches` count matches `balls` distinct IDs).

**Libraries Used:** 
*   **Pandas & NumPy:** In-memory transformation, cleaning, and CSV generation.
*   **DuckDB:** Rapid table ingestion operations (`duckdb.connect(db_path)`).

---

## 4. The Backend Layer (FastAPI & Core Engines)

The Backend acts as a headless algorithmic engine utilizing a "Trustless Architecture" mapping to Next.js.

### FastAPI Entry Point
*   **Location:** `api/main.py`
*   **Design Pattern:** Format-agnostic Manifest Driver.
*   All frontend invocations target a single dynamic POST endpoint: 
    `POST /api/v1/{format_type}/execute/{function_key}`

### Data Access Layer (DAL)
*   **Location:** `core/data_access.py`
*   **Connection Mechanism:** Maintains a read-only DuckDB instance pool: `self.con = duckdb.connect(db_path, read_only=True)`. It executes highly-tailored SQL aggregates using vectorized grouping (`SELECT SUM(...) FROM balls WHERE striker IN (...)`) and returns standardized **Pandas DataFrames** downstream to the engines.

### Core Engines
*   **`core/team_engine.py`**: Executes aggregations for franchise/national teams. Uses methods like `compare_squads` and `analyze_venue_bias` relying directly on Pandas outputs from the DAL.
*   **`core/player_engine.py`**: Analyzes player performance trajectories (e.g., executing `analyze_player_profile`). Employs pre-computed stats vs linear scans when grouping matches or slicing across venues.
*   **`core/predictor.py`**: Acts as a pseudo ML-heuristic node for predictive outputs utilizing historical aggregates.

### Backend Libraries 
*   **Routing:** FastAPI & Uvicorn.
*   **Data Validation:** Pydantic models in `api/schemas` (`ExecuteRequest`, `ExecuteResponse`) to validate incoming API context payloads.
*   **Serialization:** `api/serializers.py` enforces JSON-compliant data structures (converting complex Numpy/Pandas scalars, domain Dataclasses, or NaN constants into standard JSON primitives for the UI).

---

## 5. The Frontend Layer (Next.js)

The interactive dashboard adheres precisely to a Phase-Sequential roadmap (React 19 / Next.js 16).

### Directory Construction
*   **`app/page.tsx`:** Standard Next.js server/client component acting as the global application shell. Houses the 3-Layer split (FormatSelector, ContextBar, and dynamic CategoryScreen/Sidebar).
*   **`app/layout.tsx`:** Base HTML, global font handling, and CSS injectors.
*   **`components/`:** Cleanly partitioned modular parts (e.g., `layout/Sidebar.tsx`, `renderers/FunctionRenderer.tsx`).

### Global State Management
Instead of Redux or Zustand, the state rests purely on **React Context** combined with standard React Hooks (`useState`, `useEffect`).
*   **Provider:** `AppProvider` (exported from `frontend/lib/context.tsx`).
*   **Usage:** Captures universally required variables globally (`manifest`, `activeFormat`, `contextValues`) using `useAppContext()`. 

### "Manifest-Driven UI"
The UI constructs itself via a master configuration file from the Python backend (`formats/{fmt}/manifest.py`).
1.  Frontend sends a `GET /api/v1/odi/manifest` request on initialization.
2.  The response contains categories, tabs, parameters (Context Bar fields like "🏟️ Venue" vs "🌍 Region"), and Output Renderers (Table formats vs charts).
3.  `app/page.tsx` parses this exact JSON structure to dynamically render Sidebar groupings, active tabs, and validation logic without hardcoding format-specific conditional renders.

### Frontend Libraries
*   **Styling:** Tailwind CSS (v4) with vanilla PostCSS (`@tailwindcss/postcss`). Custom thematic colors and variable injections defined in `globals.css` (e.g., glass-card variants).
*   **Icons:** Lucide-React.
*   **Data Fetching/Requests:** Utilizes standard browser native `fetch()` heavily abstracted inside `frontend/lib/api.ts` (e.g., `executeFunction()` wrapper).

---

## 6. The API Contract

Frontend and Backend communication strictly adheres to JSON-Pydantic validated agreements via the generic `execute` route schema.

### Example Interaction

**Frontend Request:**
```http
POST /api/v1/odi/execute/venue_bias
Content-Type: application/json

{
  "params": {
    "venue_id": "v_20281",
    "years": 5,
    "team_a": "Australia",
    "team_b": "India"
  }
}
```

**Backend JSON Response (Data Encapsulation):**
```json
{
  "function_key": "venue_bias",
  "output_type": "report",
  "data": {
     "bat_first_win_percent": 65.5,
     "avg_first_innings_score": 284,
     "pace_vs_spin_ratio": 1.4,
     "matches_analyzed": 10
  },
  "metadata": {
     "engine_class": "TeamEngine",
     "engine_method": "analyze_venue_bias",
     "format": "odi"
  }
}
```

This ensures extreme scalability—any new engine methods added to the backend implicitly populate to the Frontend by merely updating the `manifest.py` and output type parser.
