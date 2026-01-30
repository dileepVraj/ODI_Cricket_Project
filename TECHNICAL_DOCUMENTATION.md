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
2.  Run the pipeline:
    ```bash
    python utils/json_converter.py
    ```
3.  Restart the dashboard kernel to load fresh stats.

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
**Role:** Calculates individual player stats, form, and matchups.
*   **`PlayerEngine`**:
    *   `analyze_player_profile()`: The master function for the Player Card. Orchestrates specific sub-calculations.
    *   `_get_stats()`: Calculates Batting/Bowling avg, SR, and **Form** (Last 5 matches). *Critically uses `squads_df` to detect DNB vs Absent.*
    *   `get_last_match_xi()`: Smart-fetches the latest Playing XI for pre-populating dropdowns.
    *   `render_pro_table()`: Generates the HTML for the "Detailed Stats" grid (Batting/Bowling summary).

#### `core/team_engine.py`
**Role:** Calculates team-level metrics and H2H logs.
*   **`TeamEngine`**:
    *   `analyze_head_to_head()`: Generates the "Win % Matrix" and recent match history between two teams.

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

---

## 5. 🧩 Key Design Patterns
1.  **Dependency Injection:** `engine.py` creates `raw_df` once and "injects" it into `PlayerEngine` and `TeamEngine`. Efficient memory usage.
2.  **Facade Pattern:** `CricketAnalyzer` hides the complexity of sub-engines from the UI (`interface.py`).
3.  **Defensive Coding:** "Nan-Safe" math (e.g., `avg = runs / outs if outs > 0 else runs`) prevents dashboard crashes on dirty data.
