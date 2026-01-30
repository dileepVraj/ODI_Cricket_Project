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
    * **Raw Source:** `data/json_source/*.json` (Cricsheet Ball-by-Ball data).
    * **Ingestion Engine:** `json_converter.py` (Flattens JSONs into a Master CSV).
    * **Refinery Engine:** `refinery_script.py` (Calculates advanced metrics like Phase Stats, Player Metadata).
    * **Storage:** `data/FINAL_ODI_MASTER.csv`, `processed_player_stats.csv`.

2.  **Logic Layer (The Brains - `core/`)**
    * **`player_engine.py`**: Micro-analysis. Handles individual player form, matchups, and archetypes.
    * **`team_engine.py`**: Macro-analysis. Handles Team Fortresses, Venue Bias, and **Phase Analysis** (Powerplay/Death Run Rates).
    * **`predictor.py`**: Predictive modeling. Uses weighted factors to forecast match scores.

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
    * Run `json_converter.py`.
    * It reads thousands of JSON files (ignored by Git) and merges them into `FINAL_ODI_MASTER.csv`.
    * *Result:* A single 100MB+ file containing every ball bowled in history.

2.  **Refinement:**
    * Run `refinery_script.py`.
    * It cleans the Master CSV (fixes names, handles "DNB").
    * It generates specialized views: `processed_phase_stats.csv` (Run rates per 10 overs).

3.  **Execution:**
    * User opens `dashboard.ipynb`.
    * `engine.CricketAnalyzer` loads the CSVs into memory (Pandas DataFrames).
    * `interface.TraderCockpit` builds the UI and connects buttons to Engine functions.

---

## 4. Directory Structure Map

```text
/
├── dashboard.ipynb          # MAIN ENTRY POINT
├── interface.py             # UI Code (Tabs: Squads, Phase, Venue)
├── engine.py                # Controller (Connects UI to Core)
├── settings.py              # Global Settings (Paths, Debug Flags)
├── venues.py                # Venue Name Normalization Logic
│
├── config/
│   ├── teams.py             # STATIC DATA (Colors, Roles, Squads)
│
├── core/
│   ├── player_engine.py     # Micro-Stats (Player vs Player)
│   ├── team_engine.py       # Macro-Stats (Phase Analysis, Fortresses)
│   ├── predictor.py         # Algo-Prediction Model
│
├── data/
│   ├── FINAL_ODI_MASTER.csv # The Big Data (Ignored by Git LFS)
│   ├── processed_*.csv      # Refined faster datasets
│   └── json_source/         # Raw downloads (Ignored)
│
└── utils/
    ├── json_converter.py    # ETL Script 1
    └── refinery_script.py   # ETL Script 2

------

6. Future Plans & Roadmap
Live Data Integration: Connect a scraper to feed live match data into engine.py for in-play signals.

T20 Support: Clone the logic to handle T20Is (requires new teams_t20.py config).

Fantasy Connector: Export "Dream Team" probabilities based on the Tactical Matrix.

Sentiment Analysis: (Long Term) Scrape Twitter/News for "Player Morale" flags


## 🛑 STRICT CODING STANDARDS (Zero-Destruction Policy)

1.  **NO LAZY PLACEHOLDERS:** Never use comments like `// ... rest of code remains the same` or `// ... existing logic`. You MUST rewrite the full file or function explicitly if you are outputting code.
2.  **PRESERVE & EXTEND:** When refactoring, you are forbidden from deleting existing helper functions, imports, or logic unless explicitly asked to remove them.
3.  **ATOMIC UPDATES:** If you are modifying a single function, output *only* that function. Do not print the whole file unless asked.
4.  **SAFETY CHECK:** Before outputting a full file rewrite, internally verify that you have included every single previous method (e.g., `tactical_matrix`, `matchups`, `get_stats`).

## 🛑 ADVANCED AI PROTOCOLS (The "Senior Dev" Standards)

### 1. The "Source of Truth" Rule (No Hardcoding)
* **Trigger:** Whenever styling a team or defining a player's role.
* **Rule:** You are FORBIDDEN from hardcoding Hex codes (e.g., `#0088ff`) or Role strings (e.g., `Right Arm Fast`).
* **Action:** You MUST import and use the dictionaries from `config.teams`:
    * Use `TEAM_COLORS['India']`, not `'blue'`.
    * Use `PLAYER_ROLES.get(player)`, not manual `if/else` checks.
    * *Reason:* Changing a color in `config/` should update the whole app instantly.

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
* **File:** `AI_MEMORY.md`
* **Trigger:** At the end of ANY significant code refactor or bug fix.
* **Rule:** You MUST update `AI_MEMORY.md`.
* **Action:**
    1.  Mark completed tasks as `[x]` in the "Active Tasks" list.
    2.  Add a bullet point to "Session History" explaining what files you changed.
    3.  If you changed the architecture (e.g., added a new function), update "Current Architecture State."
    4.  *Crucial:* This allows future sessions to know what you did. Do not skip this.


## 🔄 7. Operational Workflows & Data Maintenance

This section dictates how the AI Agent and Developer should handle data updates to ensure the dashboard reflects the latest matches.

### 🛑 Protocol A: The "Fresh Data" Cycle (Full Update)
**Trigger Command:** "Update the database", "Process new data", or "Refuel the engine."

#### Phase 1: Manual Preparation (User Responsibility)
* **Step 1:** Download the latest `odis_json.zip` from [Cricsheet.org](https://cricsheet.org/downloads/).
* **Step 2:** Extract the contents into: `data/json_source/`.
    * *Rule:* Overwrite all existing files to ensure corrected scorecards are updated.
    * *Verification:* Ensure `data/json_source/` contains `.json` files (not a subfolder).

#### Phase 2: Ingestion (The Converter)
* **Script:** `utils/json_converter.py`
* **Execution:** `python utils/json_converter.py`
* **Purpose:** Flattens thousands of raw JSON files into a single Master CSV.
* **Output:** `data/FINAL_ODI_MASTER.csv`
* **AI Check:** Verify that `FINAL_ODI_MASTER.csv` exists and is >100MB.

#### Phase 3: Refinement (The Refinery)
* **Script:** `utils/refinery_script.py`
* **Execution:** `python utils/refinery_script.py`
* **Purpose:**
    1.  Cleans Venue Names (using `venues.py`).
    2.  Calculates "Phase Stats" (Powerplay/Middle/Death).
    3.  Computes "Form" (Last 5 Matches) and 4-Tier Badges.
* **Output:** * `data/processed_player_stats.csv`
    * `data/processed_phase_stats.csv`

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
    * *Fix:* Delete all files in `data/json_source/` and re-extract the fresh ZIP.