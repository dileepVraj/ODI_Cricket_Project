# 🏏 Cricket Algo-Trader - System Architecture & Developer Guide

## 1. Executive Summary
**Project Name:** Cricket Algo-Trader
**Purpose:** A high-frequency analytics dashboard for cricket traders. It bypasses standard "averages" to find edge cases (e.g., "Left-Arm Pace vs Top Order at Wankhede") using granular ball-by-ball data.
**Core Philosophy:** "Context over Content." A player's average means nothing without context (Venue, Opponent, Current Form).

---

## 2. High-Level Architecture (The Stack)

The application follows a **Model-View-Controller (MVC)** hybrid pattern tailored for Jupyter environments.

### 🏗️ The 3-Layer Stack
1.  **Data Layer (The Foundation)**
    * **Raw Source:** `formats/odi/data/json_source/*.json`.
    * **Ingestion Engine:** `formats/odi/utils/json_converter.py`.
    * **Refinery Engine:** `formats/odi/utils/refinery_script.py`.
    * **Primary Storage:** `formats/odi/data/odi.duckdb` (DuckDB Runtime authority).
    * **CSV Fallback:** `FINAL_ODI_MASTER.csv`, `processed_player_stats.csv` (used for one-time DB ingestion).

2.  **Logic Layer (The Brains)**
    * **`core/team_engine.py`**: Factory → `get_team_engine("odi")` dynamically loads format-specific TeamEngine.
    * **`core/player_engine.py`**: Factory → `get_player_engine("odi")` dynamically loads format-specific PlayerEngine.
    * **`core/predictor.py`**: Factory → `get_predictor_engine("odi")` dynamically loads format-specific PredictorEngine.
    * **`core/data_access.py`**: Central DAL providing format-agnostic query toolbox.
    * **`core/data_loader.py`**: DRY CSV/Pickle caching (shared by facade).
    * **`core/base_engine.py`**: Shared safe-math utilities (`_safe_divide`, `_safe_float`).
    * **`engine.py`**: The Facade v3.0. Format-aware, uses `config/format_registry.py` for dynamic engine loading. Supports both `CricketAnalyzer(filepath)` and `CricketAnalyzer(format_type="odi")`.
    * **`core/transformer.py`**: Data Cleaner. Converts raw engine structures into types for reports.
    * **`core/interpreter.py`**: Context Layer. Adds momentum weights and narratives.
    * **`config/format_registry.py`**: Format Hub v2.0. Central registry for engines, manifests, configs.

2b. **Report Generation Layer (`formats/odi/`)**
    * **`match_pack.py`**: The "Combat Manual" orchestrator. Builds a 4-chapter JSON report (Macro Context → Battlefield → Tactical Engine → Player Intelligence) by calling engines silently and piping data through the Transformer → Interpreter pipeline.

4.  **Verification Layer (The Quality Guard - `formats/odi/tests/truth_bridge/`)**
    * **Truth Bridge**: Advanced auto-diagnosis system that distinguishes between `DATA_DRIFT` and `LOGIC_REGRESSION`.
    * **Ground Truth**: JSON-based snapshots used to detect unintended shifts in engine logic.

3.  **Presentation Layer (The Face)**
    * **`interface.py`**: The UI Builder. Uses `ipywidgets` to render Tabs:
        * **Squad Comparison:** (The "Virtual Dugout")
        * **Phase Analysis:** (Run Rate charts per 10 overs)
        * **Venue Analysis:** (Toss Bias & Par Scores)
    * **`dashboard.ipynb`**: The Entry Point. Initializes the system and displays the Cockpit.

---

## 3. Data Pipeline & Process Flow

### 🔄 How Data Moves
1.  **Ingestion:**
    * Run `formats/odi/utils/json_converter.py`.
    * It reads thousands of JSON files (ignored by Git) and merges them into `FINAL_ODI_MASTER.csv`.
    * *Result:* A single 100MB+ file containing every ball bowled in history.

2.  **Refinement:**
    * Run `formats/odi/utils/refinery_script.py`.
    * It cleans the Master CSV (fixes names, handles "DNB").
    * It generates specialized views: `processed_phase_stats.csv` (Run rates per 10 overs).
    * Rebuild DuckDB (runtime DB): `python formats/odi/utils/ingest_to_db.py`.

3.  **Execution:**
    * User opens `dashboard.ipynb`.
    * `engine.CricketAnalyzer` initializes in **Pure DB Mode**.
    * It opens a connection to DuckDB via `core/data_access.py`.
    * **RAM Efficiency:** DataFrames are *not* hydrated globally (~78% RAM savings).
    * Sub-engines execute high-speed SQL aggregations for specific queries.
    * `interface.TraderCockpit` builds the UI and connects buttons to Engine functions.

---

## 4. Directory Structure Map

```text
/
|-- dashboard.ipynb          # MAIN ENTRY POINT
|-- engine.py                # Facade v3.0 (Format-Aware Controller)
|-- interface.py             # UI Code (Tabs: Squads, Phase, Venue)
|-- pyproject.toml           # Python packaging
|-- requirements.txt         # Pinned dependencies
|-- .env.example             # Environment config template
|
|-- config/
|   |-- format_registry.py   # Format Hub v2.0 (factories, manifests, configs)
|   |-- settings.py          # Global defaults (overridden per-format)
|   `-- shared/
|       |-- team_colors.py   # TEAM_COLORS (Source of Truth)
|       |-- venues.py        # VENUE_MAP + aliases
|       `-- themes.py        # UI theme constants
|
|-- core/                    # Format-Agnostic Layer
|   |-- team_engine.py       # Factory → get_team_engine("odi")
|   |-- player_engine.py     # Factory → get_player_engine("odi")
|   |-- predictor.py         # Factory → get_predictor_engine("odi")
|   |-- data_access.py       # DuckDB DAL (parameterized SQL)
|   |-- data_loader.py       # CSV/Pickle cache (DRY)
|   |-- base_engine.py       # Shared safe-math utilities
|   |-- transformer.py       # Data Cleaner (Raw → Typed Dicts)
|   |-- interpreter.py       # Intelligence Layer (Context, Narratives)
|   |-- exceptions.py        # Custom error hierarchy
|   `-- interfaces/          # Protocol contracts (ITeamEngine)
|
|-- formats/
|   `-- odi/
|       |-- __init__.py          # Exports: TeamEngine, PlayerEngine, PredictorEngine, FORMAT_CONFIG
|       |-- manifest.py          # UI capability declaration
|       |-- predictor.py         # ODI prediction model
|       |-- match_pack.py        # Combat Manual Orchestrator (4-Chapter JSON)
|       |-- config/              # ODI settings, rankings, players
|       |   |-- players.py
|       |   |-- rankings.py
|       |   `-- settings.py
|       |-- engines/             # ODI TeamEngine, PlayerEngine
|       |-- data/                # ODI datasets + DuckDB runtime
|       |-- reports/             # ODI match pack outputs
|       |-- tests/               # Truth Bridge + Regression suites
|       |-- utils/               # Ingestion + refinery scripts
|       |-- tools/               # Maintenance tools
|       `-- scripts/             # Maintenance scripts
|
|-- scripts/
|   `-- update_data.py           # Master Pipeline Orchestrator (4-stage)
|
|-- tests/                       # Cross-format integration tests
|
`-- docs/                        # Architecture, guides, reports, AI context
```
------

## 5. Data Intelligence Pipeline (The "Refinery")

The project uses a **Hybrid Architecture** to balance Speed vs. Scale.

### 🔄 The Flow: JSON -> CSV -> DuckDB
1.  **Raw Ingestion (Source)**
    *   **Input:** Thousands of JSON files from Cricsheet.
    *   **Process:** `formats/odi/utils/json_converter.py` flattens these into a single Master CSV.
    *   **Artifact:** `formats/odi/data/FINAL_ODI_MASTER.csv`.

2.  **Refinery (Enrichment)**
    *   **Process:** `formats/odi/utils/refinery_script.py`.
    *   **Logic:**
        *   Standardizes Venue Names using `VENUE_MAP`.
        *   Calculates "Phase Stats" (Powerplay, Middle, Death) for every match.
        *   Computes "Form" badges (Last 5 matches).
    *   **Artifact:** `formats/odi/data/processed_player_stats.csv`.

3.  **Analytical Engine (The Consumer)**
    *   **Live Dashboard:** Uses `CricketAnalyzer` (In-Memory Pandas) for < 50ms response times on vectorized queries.
    *   **Deep Research:** Uses `odi.duckdb` (OLAP Database) for complex SQL queries across millions of balls.

### ❓ Why Verification Matters Here?
Because we support **Hot Reloading**, any bug in the Refinery (e.g., a bad Venue Map) immediately corrupts the Dashboard. The **Verification Suite (Stage 4)** prevents bad data from ever reaching the UI.

---

## 6. Future Plans & Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 6 | ✅ DONE | Headless Refactor (Engines decoupled from UI) |
| Phase 7 | ✅ DONE | Truth Bridge (Auto-diagnosing regression tests) |
| Phase 8 | ✅ DONE | Automated Data Pipeline (`scripts/update_data.py`) |
| Phase 9 | ✅ DONE | Codebase Audit & Format-Agnostic Refactor |
| Phase 10 | 🔜 NEXT | FastAPI + Next.js Frontend (9 sub-phases) |
| Phase 11 | 📋 PLANNED | Multi-Format Support (T20I, IPL modules) |
| Phase 12 | 📋 PLANNED | Backtesting Rig (Simulate betting strategies on historical data) |
| Phase 13 | 📋 PLANNED | Live Data Integration (Real-time match feed) |


## 🛑 STRICT CODING STANDARDS (Zero-Destruction Policy)

1.  **NO LAZY PLACEHOLDERS:** Never use comments like `// ... rest of code remains the same` or `// ... existing logic`. You MUST rewrite the full file or function explicitly if you are outputting code.
2.  **PRESERVE & EXTEND:** When refactoring, you are forbidden from deleting existing helper functions, imports, or logic unless explicitly asked to remove them.
3.  **ATOMIC UPDATES:** If you are modifying a single function, output *only* that function. Do not print the whole file unless asked.
4.  **SAFETY CHECK:** Before outputting a full file rewrite, internally verify that you have included every single previous method (e.g., `tactical_matrix`, `matchups`, `get_stats`).

## 🛑 ADVANCED AI PROTOCOLS (The "Senior Dev" Standards)

### 1. The "Source of Truth" Rule (No Hardcoding)
* **Trigger:** Whenever styling a team or defining a player's role.
* **Rule:** You are FORBIDDEN from hardcoding Hex codes (e.g., `#0088ff`) or Role strings (e.g., `Right Arm Fast`).
* **Action:** You MUST import and use the dictionaries from:
    * `config.shared.team_colors` for `TEAM_COLORS`
    * `formats.odi.config.players` for `PLAYER_ROLES` and `BOWLER_STYLES`
    * Use `TEAM_COLORS['India']`, not `'blue'`.
    * Use `PLAYER_ROLES.get(player)`, not manual `if/else` checks.
    * *Reason:* Changing a color or role map should update the whole app instantly.

### 2. The "Defensive Data" Rule (Anti-Crash)
* **Trigger:** Whenever performing calculations (Division, Indexing) or loading CSVs.
* **Rule:** Assume Data is Dirty. Never divide without checking for Zero (`if balls > 0`). Never access a DataFrame column without checking `if col in df.columns`.
* **Action:**
    * Replace `avg = runs / outs` with `avg = runs / outs if outs > 0 else runs`.
    * Handle `NaN` values gracefully (display as `-` or `0`, do not let the UI throw an error).
    * *Reason:* Cricket data often has "Did Not Bat" (DNB) or 0-ball innings which crash standard math.

### 3. The "Widget Performance" Rule (No Infinite Loading)
* **Trigger:** When initializing `TraderCockpit` or creating Dropdowns in `interface.py`.
* **Rule:** **NO HEAVY COMPUTATION IN `__init__`**.
* **Action:**
    * Heavy sorting or filtering must happen in the `engine.py` (Controller), not the UI thread.
    * Use `df['col'].unique()` instead of `list(set(df['col']))` for speed.
    * *Reason:* Calculating stats for 5,000 players inside a UI render block causes the "Infinite Loading" bug.

### 4. The "Context Integrity" Rule (No Fake Stats)
* **Trigger:** When a user asks for "Kohli's Stats".
* **Rule:** Context is King. Averages are meaningless without filters.
* **Action:**
    * ALWAYS check the `years` filter (e.g., "Last 2 Years" vs "All Time").
    * ALWAYS check the `venue` filter.
    * If a player has < 3 innings in a specific condition, you MUST flag it (e.g., "Small Sample Size" or hide the Badge).
    * *Reason:* Showing an Average of 100 because a player hit 1 run in 1 not-out inning is misleading trading advice.

### 5. The "Visual Hierarchy" Rule
* **Trigger:** When creating HTML tables or charts.
* **Rule:** Information Density must be high but readable.
* **Action:**
    * **Numbers:** Right-Align all numerical data.
    * **Text:** Left-Align names and roles.
    * **Badges:** Must always use the 4-Tier Color Codes (Green/Teal/Orange/Red).
    * **Contrast:** Never put dark text on a dark background (e.g., Black text on India Blue background).

### 6. The "Living Memory" Protocol
* **File:** `docs/ai/AI_MEMORY.md`
* **Trigger:** At the end of ANY significant code refactor or bug fix.
* **Rule:** You MUST update `docs/ai/AI_MEMORY.md`.
* **Action:**
    1.  Mark completed tasks as `[x]` in the "Active Tasks" list.
    2.  Add a bullet point to "Session History" explaining what files you changed.
    3.  If you changed the architecture (e.g., added a new function), update "Current Architecture State."
    4.  **Anti-Patterns (New):** If a bug was caused by a specific mistake (e.g., assuming a column exists), you MUST log it in the "Anti-Patterns & Lessons Learned" section.
    5.  *Crucial:* This allows future sessions to know what you did and **what to avoid**. Do not skip this.


### 7. The "Bug Post-Mortem" Rule
* **Trigger:** Whenever identifying and fixing a logic or data-integrity bug.
* **Rule:** You MUST create a formal documentation file in `docs/bug_fixes/`.
* **Action:**
    * Create a file: `docs/bug_fixes/YYYY-MM-DD_short_description.md`.
    * Include: **Problem Statement**, **Root Cause**, **Implementation Fix**, and **Verification Results**.
    * *Reason:* Ensures that subtle bugs (like date boundary issues) are understood by future agents and developers to prevent re-introduction.

---

## 🧪 8. The Truth Bridge Testing Protocol (Enhanced)

Our testing uses the **Truth Bridge**, a non-destructive verification system that compares "Engine Logic" against "Golden Master" snapshots.

### A. Core Workflow (V2.5)
1.  **SEED MODE**: Run `SEED_MODE="1" python run_all.py` to capture a baseline of current engine outputs.
    *   *Constraint:* Only run this when you are 100% sure the current logic is correct.
2.  **REFACTOR**: Make your code changes.
3.  **VALIDATE**: Run `python formats/odi/tests/truth_bridge/run_all.py`.
    *   **PASS**: Engine matches baseline exactly.
    *   **DATA_DRIFT**: Results changed because new matches were added (Expected).
    *   **LOGIC_REGRESSION**: Results changed despite Match IDs being identical (Critical Bug).

### B. Verification Suites
| Suite | Scope | Responsibility |
| :--- | :--- | :--- |
| `compare_squads` | **Tactical Parity** | Ensures "Batter vs Bowler" matchups and Run Costs are stable. |
| `predictor_validation` | **Algorithm Integrity** | Verifies that Win Probability logic hasn't drifted. |
| `player_stats` | **Micro-Stats** | Checks if Kohli's Average/SR are consistent with filtering logic. |
| `team_form` | **Macro-Trends** | Validates "Last 5 Matches" sequence generation. |

### C. Auto-Diagnosis
If a test fails, the runner will analyze the failure:
*   **"LOGIC REGRESSION"**: Same match IDs, different numbers -> **YOU BROKE THE MATH.**
*   **"DATA DRIFT"**: New match IDs found -> **SAFE TO UPDATE BASELINE.**

---

---

## 🔄 7. Operational Workflows & Data Maintenance

This section dictates how the AI Agent and Developer should handle data updates to ensure the dashboard reflects the latest matches.

### 🛑 Protocol A: The "Fresh Data" Cycle (Full Update)
**Trigger Command:** "Update the database", "Process new data", or "Refuel the engine."

#### Phase 1: Manual Preparation (User Responsibility)
* **Step 1:** Download the latest `odis_json.zip` from [Cricsheet.org](https://cricsheet.org/downloads/).
* **Step 2:** Extract the contents into: `formats/odi/data/json_source/`.
    * *Rule:* Overwrite all existing files to ensure corrected scorecards are updated.
    * *Verification:* Ensure `formats/odi/data/json_source/` contains `.json` files (not a subfolder).

#### Phase 2: Ingestion (The Converter)
* **Script:** `formats/odi/utils/json_converter.py`
* **Execution:** `python formats/odi/utils/json_converter.py`
* **Purpose:** Flattens thousands of raw JSON files into a single Master CSV.
* **Output:** `formats/odi/data/FINAL_ODI_MASTER.csv`
* **AI Check:** Verify that `FINAL_ODI_MASTER.csv` exists and is >100MB.

#### Phase 3: Refinement (The Refinery)
* **Script:** `formats/odi/utils/refinery_script.py`
* **Execution:** `python formats/odi/utils/refinery_script.py`
* **Purpose:**
    1.  Cleans Venue Names (using `config/shared/venues.py`).
    2.  Calculates "Phase Stats" (Powerplay/Middle/Death).
    3.  Computes "Form" (Last 5 Matches) and 4-Tier Badges.
* **Output:** * `formats/odi/data/processed_player_stats.csv`
    * `formats/odi/data/processed_phase_stats.csv`

#### Phase 4: Hot Reload (The Restart)
* **Action:** The Dashboard (`dashboard.ipynb`) loads data *into memory* only on startup.
* **Requirement:** The user **MUST** Restart the Jupyter Kernel or re-run the `dashboard.ipynb` initialization cell to see the new data.
* **AI Response:** After running scripts, explicitly tell the user: *"Update complete. Please restart your dashboard kernel now."*

---

### 🛠️ Troubleshooting Data Issues
* **Issue:** "Infinite Loading" on Dashboard startup.
    * *Cause:* `processed_player_stats.csv` might be corrupted or empty.
    * *Fix:* Re-run **Phase 3 (Refinery)**.
* **Issue:** "KeyError: 'batter'" during Ingestion.
    * *Cause:* Old/Corrupt JSON format in `json_source`.
    * *Fix:* Delete all files in `formats/odi/data/json_source/` and re-extract the fresh ZIP.
