# 📘 The Dugout - Technical Documentation

## 1. 🏗️ High-Level Architecture
**The Dugout** is a high-performance cricket analytics dashboard designed for pro-traders and analysts. It operates on a **Local-First** architecture to ensure zero latency and full data sovereignty.

### System Data Flow
```mermaid
graph TD
    A[JSON Source Data] -->|utils/json_converter.py| B(Master CSV Database)
    B --> C[CricketAnalyzer Engine]
    C -->|Sub-Engines| D[PlayerEngine & TeamEngine]
    D --> E[Interface Layer (ipywidgets)]
    E --> F[User Dashboard (app.py)]
    D -.->|Verification| G[🌉 Truth Bridge]
    G -.->|Validation| B
```

---

## 2. 💻 Tech Stack

### High-Level (User Facing)
*   **Platform:** Python 3.10+
*   **Environment:** Jupyter Notebook / Voila (for standalone web-app feel)
*   **Interface:** `ipywidgets` (Interactive Controls) + `HTML/CSS` (Custom Reporting Tables)

### Low-Level (Core Processing)
*   **Data Processing:** `pandas` (Vectorized operations for speed)
*   **Performance:** `numpy` (Numerical compute), Pre-computed CSV indexes
*   **Verification:** `pytest` (Standard Bridge Tests) + JSON Snapshot Compare
*   **Utilities:** `glob`, `os`, `json` (Standard library for file IO)

---

## 3. 🚀 Usage Guide

### A. Running the Dashboard
1.  **Launch Jupyter:** `jupyter notebook`
2.  **Open App:** Navigate to `dashboard.ipynb`
3.  **Run All:** Click "Cell" -> "Run All"
4.  **Voila Mode (Optional):** Click the "Voila" button for a clean, code-free UI.

### B. Updating Data
When new match logs (JSON) arrive:
1.  Place `.json` files in `data/json_source/`.
2.  Run the pipeline: `python utils/json_converter.py`
3.  **Audit Configuration**: Run `python scripts/find_missing_players.py` to ensure new players are mapped in `config/teams.py`.
4.  Restart the dashboard kernel.

### C. Quality Control (Truth Bridge)
Before trusting engine results after a code change:
1.  Navigate to `tests/odi/truth_bridge/`.
2.  Run a specific validator, e.g., `python tests/odi/truth_bridge/analyze_venue_matchup/test_runner.py`.
3.  Verify the `report.json` shows `PASS` (or `DATA_DRIFT` for fresh data).

---

## 4. 📂 Codebase Reference (File-by-File)

### 🧱 Core Architecture

#### `engine.py`
**Role:** The "Facade" / Main Controller.
*   **`CricketAnalyzer`**: The singleton class that initializes the app.
    *   `load_data()`: Loads `FINAL_ODI_MASTER.csv` and `MATCH_INFO.csv`.
    *   `_create_match_summary()`: Aggregates ball-by-ball data into match-level results.
    *   `reload_database()`: Allows hot-reloading of data without restarting the kernel.

#### `interface.py`
**Role:** The "Frontend" / View Layer.
*   **`TraderCockpit`**: The main UI class.
    *   `__init__`: Sets up the widget layout (Header, Control Panel, Output Area).
    *   `_setup_tabs()`: Creates the "Team Analysis", "Player Analysis", and "Phase Analysis" tabs.
    *   `on_generate_click()`: The Event Handler. Collects inputs → Calls Engine → Updates Output.

### 🧠 Logic Engines (`core/`)

#### `core/player_engine.py` (The Heavy Lifter)
*   **`PlayerEngine`**:
    *   `analyze_player_profile()`: Master orchestration for the Player Card.
    *   `analyze_squad_types()`: **[TACTICAL]** Generates the "Threat Matrix" (Batter vs. Opposition Bowling Types).
    *   `_get_stats()`: Context-aware stats (DNB logic via `MATCH_SQUADS.csv`).
    *   `_calculate_squad_metrics()`: Aggregated team stats (Caps, Runs, Wickets).

#### `core/team_engine.py`
*   **`TeamEngine`**:
    *   `analyze_head_to_head()`: Win % Matrix and recent history.
    *   `analyze_home_fortress()`: **[SMART FILTER]** Calculates home dominance. Excludes "Easy Chases" (< 200) from general averages to prevent Batting Power deflation.
    *   `analyze_continent_performance()`: Regional dominance analysis.

### 🛠️ Utilities (`utils/`)

#### `utils/json_converter.py`
**Role:** The "Ingestion Engine".
*   **`process_matches()`**:
    1.  Reads raw JSONs.
    2.  Extracts Squads -> `MATCH_SQUADS.csv`.
    3.  Extracts Info -> `MATCH_INFO.csv`.
    4.  Flattens Ball-by-Ball -> `FINAL_ODI_MASTER.csv`.

#### `utils/refinery_script.py` (Deprecated/Merged)
*   *Note: Phase Stats logic previously here is now largely integrated or used for ad-hoc "Phase Analysis" csv generation.*

### 💾 Data Layer (`data/`)
*   **`FINAL_ODI_MASTER.csv`**: Every ball bowled (1M+ rows). Source of truth for stats.
*   **`MATCH_SQUADS.csv`**: Who was in the Playing XI (Critical for DNB logic).
*   **`MATCH_INFO.csv`**: Meta-data (Winner, Venue, Dates) for fast lookups.
*   **`player_metadata.csv`**: Unique list of players mapped to their primary teams.

### 💾 Tactical Configuration (`config/`)
*   **`config/teams.py`**: The "Source of Truth" for tactical analysis.
    *   **10-Year Coverage**: All international players since 2014 are mapped.
    *   **Historical Legends**: 200+ pre-2014 legends mapped to support career-long tactical visibility.
    *   **Maintenance**: Guided by `find_missing_players.py` and `check_bowler_coverage.py`.

---

## 5. ⚡ Performance & Caching (The Fast-Load Path)

To handle 1M+ rows efficiently, the engine implements a **Self-Healing Pickle Cache**:

1.  **Detection**: On startup, `CricketAnalyzer` checks for a `.pkl` file matching the database name (e.g., `FINAL_ODI_MASTER.pkl`).
2.  **Validation**: It compares the `mtime` (modified time) of the CSV vs. the Pickle.
3.  **The Fast Path**: If the Pickle is newer, it loads via `pd.read_pickle()` (**~80% faster** than CSV).
4.  **The Slow Path (Auto-Rebuild)**: If the CSV is newer (user updated the data), the engine performs a "Slow Load", cleans the data, and **automatically regenerates** the Pickle file for the next session.

---

## 6. 🧩 Key Design Patterns
1.  **Dependency Injection:** `engine.py` creates `raw_df` once and "injects" it into `PlayerEngine` and `TeamEngine`. Efficient memory usage.
2.  **Facade Pattern:** `CricketAnalyzer` hides the complexity of sub-engines from the UI (`interface.py`).
3.  **Defensive Coding:** "Nan-Safe" math (e.g., `avg = runs / outs if outs > 0 else runs`) prevents dashboard crashes on dirty data.
