# 🧠 AI Context & Memory Log
**Last Updated:** 2026-02-06
**Current Phase:** Test Architecture Refactoring & Stability

## 📌 Current Architecture State
- **Core Engine:** `CricketAnalyzer` (v2.1) supports hot-reloading and cleaner logging.
- **Player Stats:** `PlayerEngine` (v5.3) features **Fast-Look Optimization** (Contextual Slicing).
    - **Speed Boost:** Reduced Squad Comparison latency from O(Players * Matches) to O(N) by creating focused dataframe subsets at the start of a comparison.
- **Testing:** Domain-Driven Test Structure implemented for `odi/analyze_venue_matchup`.
    - **Regression:** Automated Regression Suite (`run_venue_regression.py`) ensures stability of Venue Matchups.
    - **Fixtures:** Golden Master snapshots stored in `tests/odi/analyze_venue_matchup/fixtures/`.
- **Data:** `tools/process_player_stats.py` points to `FINAL_ODI_MASTER.csv`.

## 🚧 Active Tasks (The "To-Do" Stack)
- [x] Refactor Test Architecture (Domain-Driven Design)
- [x] Implement Venue Matchup Regression Suite
- [x] Enhance Player Profile (Milestones, Bowling Card)
- [x] Fix Player Form Inconsistency (Deterministic Sorting)
- [x] Implement Toss Bias Regression Suite
- [ ] Implement Phase Analysis Updates (Future)

## 🛑 Recent Decisions & Constraints (Why we did this)

## 🔄 Data Pipeline Architecture
This section details how raw data flows from source to the dashboard.

### 1. Source Layer (`data/json_source/`)
- **Format:** [Cricsheet](https://cricsheet.org/) JSON (Overs-based structure).
- **Action:** Drop new match `.json` files here to update the database.

### 2. Ingestion Engine (`utils/json_converter.py`)
**Command:** `python utils/json_converter.py`
- **Steps:**
    1.  **Iterate:** Scans all `.json` files in source directory.
    2.  **Extract:** Splits data into 3 contexts: Match Info, Playing Squads, Ball-by-Ball.
    3.  **Normalize:** Flattens nested JSON (`innings -> overs -> deliveries`) into tabular rows.
    4.  **Standardize:** Renames raw keys to Schema Standard (e.g., `batter` -> `striker`).
    5.  **Calculate:** Derives `ball` decimal (0.1, 0.2) from over/delivery counts.

### 3. Storage Layer (`data/`)
| File | Role | Key Schema Notes |
| :--- | :--- | :--- |
| `FINAL_ODI_MASTER.csv` | **Source of Truth**. Ball-by-ball database. | `balls_innX` (Plural), `team_bat_1` (Not 'batting_team'). |
| `MATCH_SQUADS.csv` | **Context**. Validates "Did Not Bat". | Used by `PlayerEngine` to differentiate DNB vs Absent. |
| `MATCH_INFO.csv` | **Metadata**. Search Index. | Contains Winner, Toss, and Venue details. |

### 4. Application Layer (`engine.py`)
- **Loading:** `CricketAnalyzer` loads `FINAL_ODI_MASTER.csv` into memory (`self.match_df`).
- **Refining:** `TeamEngine._apply_smart_filters` applies logic (e.g., removing rain-curtailed matches < 45 overs).

- **Testing Strategy:** Moved from flat `tests/` structure to specific domain folders (`tests/odi/analyze_venue_matchup/`) to improve maintainability and cohesion.
- **Regression Protocol:** Adopted "Golden Master" testing for complex analytics outputs (Venue Matchups) instead of manual unit assertions, to catch unintended data changes.
- **Compliance:** STRICTLY following `DEV_GUIDE.md` and `GEMINI.md`.

## 🛠️ Data Processing & Schema Standards
- **Column Standardization:**
    - `ball_innX` -> `balls_innX` (Plural enforced).
    - `batting_team` -> `team_bat_1` (Engine naming convention).
    - `bowling_team` -> `team_bat_2` (Engine naming convention).
- **Engine Robustness (v2.3):**
    - **Fuzzy Column Matching:** `TeamEngine` defends against header drift.
    - **Cleaner Injection:** Test Runners now use `CricketAnalyzer` (Facade pattern) instead of raw CSV loading to ensure the Test Environment mirrors Production exactly (including Venue Standardization).

## 🧱 Anti-Patterns & Lessons Learned (The "Do Not Repeat" Log)

### 1. Test Environment Discrepancy
- **Mistake:** The initial `toss_bias` regression test loaded `pd.read_csv('FINAL_ODI_MASTER.csv')` directly.
- **Consequence:** The App (Production) uses `CricketAnalyzer` which cleans venue names (e.g., "M. Chinnaswamy" -> "IND_BANGALORE"). The Test (Raw CSV) used raw names. This led to "Insufficient Data" in tests while the App worked fine.
- **Fix:** **ALWAYS** instantiate `CricketAnalyzer` in test generators/runners. Never load raw CSVs in tests unless testing the loader itself.

### 2. Schema Assumption Blindness
- **Mistake:** Assumed `batting_team` existed in `FINAL_ODI_MASTER.csv` because legacy code referenced it.
- **Reality:** The column was actually `team_bat_1` (an internal standard). Detailed schema verification (`df.columns`) should happen *before* writing logic.
- **Fix:** Check `AI_MEMORY.md` -> Storage Layer or run `df.columns` before assuming.

### 5. Missing Columns in Master Data
- **Mistake:** Assumed `bowling_team` existed in `FINAL_ODI_MASTER.csv`. Code relied on it for H2H stats.
- **Reality:** Only `bowler` and `team_bat_1`/`team_bat_2` existed.
- **Fix:** Implemented self-healing logic in `CricketAnalyzer.load_data` (`engine.py`) to derive `batting_team` and `bowling_team` from match metadata if missing. Always prioritize robust data loading.

### 3. Hardcoded Test Coverage
- **Mistake:** Hardcoded a "Top 10" country list in test data generators.
- **Consequence:** Missed edge cases (Zimbabwe, Ireland) and required manual updates when venues changed.
- **Fix:** Use **Dynamic Imports** from `venues.py` (`VENUE_MAP`) to generate test cases. If it's in the App, it's in the Test.

### 4. Definition of Done Violation
- **Mistake:** Built regression suites (Toss, Phase) without creating documentation (`REGRESSION_GUIDE.md`), leading to obscure knowledge.
- **Fix:** A Feature is **NOT DONE** until a `REGRESSION_GUIDE.md` exists in its test folder. This is a gating criteria for task completion.

### 6. Date Boundary Exclusion
- **Mistake:** Using `pd.Timestamp.now()` directly for lookback cutoffs (e.g., `cutoff = now - 10 years`).
- **Consequence:** Matches on the *same day* years ago are excluded because the current time (e.g., 10 AM) is later than the match start time (usually 00:00 in data).
- **Fix:** **ALWAYS** use `pd.Timestamp.now().floor('D')` when filtering by date to include the full boundary day.

## 📝 Session History (Reverse Chronological)
- **[2026-02-06] Batting Average Integrity Fix:** Refactored dismissal logic to attribute "Outs" based on `player_dismissed` rather than `striker`. This fixes accuracy for non-striker run-outs.
    - **Fix:** Switched to merge-based aggregation in `refinery_script.py` and explicit name matching in `player_engine.py`.
- **[2026-02-06] Boundary Date Fix:** Fixed a project-wide bug where matches on the exact boundary date (e.g., exactly 10 years ago) were excluded due to `pd.Timestamp.now()` time components.
    - **Fix:** Applied `.floor('D')` to all current-time cutoffs in `team_engine.py`, `player_engine.py`, and `predictor.py`.
    - **Regression:** Updated Golden Master for `analyze_continent_performance` to include recovered matches for Australia, NZ, England, and South Africa.
- **[2026-02-03] Phase Analysis Master Suite:** Implemented `tests/odi/analyze_phases/` with maximal coverage:
    - **"N-vs-N" Strategy:** Updated generator to loop through *every* opponent for *every* venue (Host vs World), creating ~500 permutations.
    - **Engine Refactor:** Updated `TeamEngine.analyze_venue_phases` to return a comprehensive data packet (Venue Baseline, Home/Away Specifics, Global Habits, Risk Flags) instead of just printing HTML.
    - **Metric Integrity:** Validated Powerplay/Death stats, Wickets, and Strategic Alerts across the entire dataset.
- **[2026-02-03] Toss Bias Coverage:** Expanded `analyze_toss_bias` regression coverage to 100% of defined venues (Dynamic loading from `venues.py`).
- **[2026-02-03] Engine Stability:** Fixed critical `KeyError: 'batting_team'` in `interface.py` by making column lookup robust (`batting_team` OR `team_bat_1` + `innings` logic).
- **[2026-02-03] Test Architecture Fix:** Audited all regression suites. Verified only `toss_bias` was bypassing the Facade. Corrected `generate_test_data.py` and `run_toss_bias_regression.py` to use `CricketAnalyzer`. 
- **[2026-02-04] Recent Form Regression Suite:** Implemented `tests/odi/analyze_recent_form/` (Level 3 coverage).
    - **Engine Update:** Refactored `TeamEngine.analyze_team_form` to return structured data (`{summary_code, matches}`) for testability.
    - **Coverage:** Top Teams vs Global, Key Rivals (e.g., INDvPAK), and Continent-Specific form.
    - **Validation:** Verified Sequence Logic and Match Sort Order across all scenarios.
    - **Refactor (User Req):** Simplified scope to Global + All Continents (iterated). Removed "vs Opponent" checks and Match Details from Golden Master to focus purely on Form Sequence.
    - **Standardization:** Aligned output format with `analyze_venue_matchup` suite.
        - **Workflow:** `generate_latest_results` -> `compare_results` -> `test_report.json`.
        - **Artifacts:** `recent_form_latest_results.json` and `recent_form_test_report.json` are now standard outputs.
    - **Back-Correction:** Retroactively standardized `analyze_phases` suite to follow the same 3-file protocol (Generate/Compare/Report).
- **[2026-02-04] Governance Update:** Created `.cursorrules` (System Prompt Injection) to enforce "Read First" behavior. Updated `GEMINI.md` with strict "Definition of Done" & "Zero Deletion" policies.
- **[2026-02-03] Documentation Clean-up:** Retroactively created `REGRESSION_GUIDE.md` for Toss, Phase, and Continent suites.
- **[2026-02-02] GitHub Push:** Pushed latest changes (Continent Regression, Logic Fix, UI Polish) to `origin/main`.
- **[2026-02-02] Emoji Fix:** Updated `TeamEngine` to display Handshake (🤝) for explicit Ties OR 'No Result' matches with equal scores (e.g., BAN vs WI).
- **[2026-02-02] UI Refinement:** Optimized match audit table with `table-sm` and text wrapping to fit screens perfectly without horizontal scrolling.
- **[2026-02-02] Logic Fix:** Removed blanket exclusion of 'No Result' matches in `TeamEngine`. Now relying on `is_short` (<45 overs) logic to filter rain games. This recovered 7 valid matches in the regression suite (e.g., BAN vs WI Tie).
- **[2026-02-02] UI Enhancement:** Added horizontal scrollbar (`overflow-x: auto`) to `TeamEngine._display_audit` to fix cut-off tables in Jupyter.
- **[2026-02-02] Continent Performance Suite:** Implemented `tests/odi/analyze_continent_performance/`. Covers Global and Regional Performance Matrices.
- **[2026-02-01] Documentation:** Added detailed docstrings to `core/team_engine.py` and `core/player_engine.py` covering all public API methods and internal helpers.
- **[2026-01-31] Away Performance Suite:** Implemented `tests/odi/analyze_away_performance/`. Verified text-based form guide and Matrix Logic for all major teams.
- **[2026-02-04] Compare SQUADS Suite (Level 4):**
  - **Refactor:** Decoupled `player_engine.compare_squads` into data-generator (`_generate_comparison_payload`) and UI-renderer.
  - **Regression:** Implemented `tests/odi/compare_squads/` with 3-Layer Verification (Squad Experience, Tactical Matrix, H2H Matchups).
  - **Fix:** Fixed critical `KeyError: 'bowling_team'` in `engine.py` by implementing self-healing column derivation.
  - **Focus:** Excluded bulky ProStats to maintain a lightweight, focused baseline (200KB vs MBs).
  - **🔥 Performance Optimization:** Implemented "Fast-Look" refactor. Reduced comparison time by ~80% by passing a `context_df` (subset of rows for the 22 players) through the analytical pipeline, eliminating redundant linear scans of the main 200MB dataframe. Verified via regression suite (100% Match).
