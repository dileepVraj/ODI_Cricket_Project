# 🧠 AI Context & Memory Log
**Last Updated:** 2026-02-06
**Current Phase:** Test Architecture Refactoring & Stability

## 📌 Current Architecture State
- **Core Engine:** `CricketAnalyzer` (v2.1) supports hot-reloading and cleaner logging.
- **Micro/Macro Logic:** 
    - `TeamEngine` handles macro analytics (H2H, Fortress). Core functions like `analyze_home_fortress` are polymorphic.
    - `PlayerEngine` (v5.3) features **Fast-Look Optimization** (Contextual Slicing) and DNB logic via `MATCH_SQUADS.csv`.
- **Predictor:** `PredictorEngine` (v4.0) uses Venue Par, Batting Potential, and Bowling Threat with Tail-Ender Risk logic.
- **The Soul:** **"Context over Content"** - Every metric is weighted by Venue, Opponent, and Form (Last X years).
- **Testing:** Domain-Driven Test Structure implemented for `odi/truth_bridge` with self-diagnosis (DATA_DRIFT vs LOGIC_REGRESSION).
- **Performance:** **Self-Healing Pickle Cache** (v3.0) implemented in `engine.py`. Automatically converts CSV to Pickle for an 80% load-time reduction.

### 🏏 Player Role Methodology (Cortex v2.5)
*   **Bowler**: Primary contributor; bats 8-11.
*   **Batter**: Primary contributor; bowls < 5% of games.
*   **Bowl AR**: Significant batting (bats 7-8) but primary role is bowling.
*   **Bat AR**: Top 6 batter who bowls regularly (> 20% of games).
*   **Verification Proof**: `scripts/find_missing_players.py` cross-references the full 10-year dataset against `config/teams.py`.

## 🚧 Active Tasks (The "To-Do" Stack)
- [x] Implement Venue Matchup Truth Bridge (240/240 Green)
- [x] Integrate Smart Self-Diagnosis (Data Drift vs Logic Bug)
- [x] Implement Check Fortress Truth Bridge (Key-Discovery Mode)
- [x] Implement Global H2H Truth Bridge (Schema Loyalty Mode)
- [x] Implement Host Country H2H (Country Stats) Truth Bridge
- [x] Implement `analyze_global_performance` Truth Bridge (Key-Discovery Mode)
- [x] **[NEW]** Implement- [x] `analyze_team_form` Truth Bridge (100% Pass)
- [x] `compare_squads` Truth Bridge (100% Pass - 188 metrics verified across 3 layers)
- [x] **EPIC:** Expanded `config/teams.py` to cover 10 years of historical data. Added 200+ bowling styles and 400+ player roles across all major and minor ODI nations.
- [x] Consolidated Sri Lanka data: Removed duplicate sections and resolved missing styles (e.g., Kusal Mendis).
- [x] Verified configuration integrity with `find_missing_players.py` (Zero gaps for SL).
- [x] `analyze_continent_performance` Truth Bridge (100% Pass - 44 regional matrices verified)
- [x] **Auto-Diagnosis Audit (v2.5)**: Verified `MATCH_IDS` integration across all 12 Truth Bridge suites. Confirmed `LOGIC` vs `DRIFT` detection is 100% effective.
- [x] Implement Localized Regression Guides for all Bridge Suites
- [x] **[2026-02-10]** Expanded `config/teams.py` with 200+ historical legends to restore career-long tactical visibility (All-Time Parity).
- [x] **[2026-02-10]** Synchronized project documentation (`TECHNICAL_DOCUMENTATION.md` & `DEV_GUIDE.md`) with 4-layer architecture.
- [x] **[2026-02-10]** Implemented **Match Pack Generator** (The Combat Manual) with standalone `Interpreter` class for intersectional tactical logic.
- [x] **[2026-02-10]** Integrated Match Context Inputs (Time, Toss, Pitch) into the Dashboard for real-time condition weighting.
- [x] **[2026-02-10]** Deployed all tactical expansions and truth bridge updates to GitHub `origin/main`.
- [x] **[2026-02-11]** Transitioned Team and Player form metrics from "Last 5" to **"Last 10"** baseline. Verified UI stability and documentation sync.
- [x] **[2026-02-11]** Codebase Deep Dive & Bug Fixes: Removed duplicate `TeamEngine` init in `engine.py` (line 119) and duplicate `_apply_smart_filters` in `team_engine.py` `analyze_home_fortress` (line 567).
- [x] **[2026-02-11]** Match Pack Generator v3.0: Created 3-file pipeline — `core/transformer.py` (5 transform functions), `core/interpreter.py` (9 interpretation methods + rating rules), `reports/match_pack_generator.py` (orchestrator with `_silent_call` to preserve UI). 6/6 unit tests pass.
- [x] **[2026-02-11]** Match Pack v3.1 Post-Review: Fixed 4 bugs (dominance key mismatch, 50% narrative, trend logic, incomplete phase data). Added 7 quality improvements (section_description, reasoning, timeline, stripped _match_ids, slim H2H, chapter descriptions). Fixed `team_engine.py` phase return packet (4→12 fields). 24/24 tests pass.
- [x] **[2026-02-11]** Match Pack v3.2 Post-Review: 5 fixes — (1) Added `caveat_2nd_innings_death` to phase analysis, (2) Renamed `h_`/`a_` keys to `home_team_`/`away_team_` in global_habits, (3) Added section descriptions + auto-narratives for squad_comparison/tactical_matrix/matchups, (4) Smart pitch suitability narrative using venue wickets instead of bowler count, (5) Added player stats section (batting/bowling form + venue metrics) via `_get_stats` in payload + `transform_player_stats`. 46/46 tests pass.

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
- **Regression Protocol**: Adopted "Golden Master" testing for complex analytics outputs (Venue Matchups) instead of manual unit assertions, to catch unintended data changes.
- **[2026-02-09] Recent Form Suite**: Implemented `tests/odi/truth_bridge/recent_form/`. Verified sequence-based form (`summary_code`) for 9 teams across 6 continents.
- **Compliance**: STRICTLY following `DEV_GUIDE.md` and `GEMINI.md`.

## 🛠️ Data Processing & Schema Standards
- **Column Standardization:**
    - `ball_innX` -> `balls_innX` (Plural enforced).
    - `batting_team` -> `team_bat_1` (Engine naming convention).
    - `bowling_team` -> `team_bat_2` (Engine naming convention).
- **Engine Robustness (v2.3):**
    - **Fuzzy Column Matching:** `TeamEngine` defends against header drift.
    - **Cleaner Injection:** Test Runners now use `CricketAnalyzer` (Facade pattern) instead of raw CSV loading to ensure the Test Environment mirrors Production exactly (including Venue Standardization).

### C. The "Test Parity" Rule
*   **Rule:** Test Environments must mirror Production Logic.
*   **Implementation:** 
    *   **NEVER** use `pd.read_csv()` in regression tests.
    *   **ALWAYS** use `CricketAnalyzer(filepath)` (The Facade) to load data.

### D. The "Fingerprint Mandate" (Truth Bridge)
*   **Trigger:** When migrating ANY function to Truth Bridge.
*   **Rule:** The Engine function **MUST** return `MATCH_IDS` in its output payload.
*   **Why:** `TruthBridgeBase` relies on this key for Auto-Diagnosis (Drift vs Logic Regression).
*   **Action:** If the legacy function lacks it, **YOU MUST REFACTOR THE ENGINE** to include it before writing the test runner. No exceptions.

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
- **[2026-02-09] Truth Bridge Expansion (Phase 2):** Migration of core macro-analytics functions to the Truth Bridge system.
    - **Suites Migrated:** `check_fortress`, `analyze_country_h2h`, `analyze_global_h2h`, `home_dominance`, and `away_performance`.
    - **Strategy:** Implemented **"Key-Discovery Mode"** for legacy fixtures.
    - **Innovation:** Developed **Matrix Fingerprinting** (v2.5) logic for `_generate_matrix_report` to support automated diagnostics in row-per-opponent reports.
    - **Documentation:** Unified localized `REGRESSION_GUIDE.md` files for all migrated suites.
    - **Pivot:** Switched from `analyze_player_profile` to **`analyze_toss_bias`** upon request.
    - **Legacy Compatibility:** Refactored `TeamEngine.analyze_venue_bias` to strictly return the Schema defined in `analyze_toss_bias_expected_results.json` while keeping modern "BOWL FIRST" terminology.
    - **Fix:** Fixed `VENUE_MAP` iteration bug by implementing a `_group_venues_by_country` helper in the test runner.
    - **Phase Analysis:** Migrated `analyze_venue_phases` to Truth Bridge. Implemented complex nested schema reconstruction in `test_runner.py` to match `analyze_phases_latest_results.json`. Validated identical data points.
    - **Auto-Diagnosis:** Upgraded `analyze_venue_bias` and `analyze_venue_phases` engines to return `MATCH_IDS` metadata. Regenerated ground truth with fingerprints to enable Data Drift detection.
- **[2026-02-09] Deep Soul Dive**: Conducted comprehensive research into every layer (Ingestion, Logic, UI). Confirmed polymorphism in `analyze_venue_matchup` and standardized the "Context over Content" philosophy across all engines.
- **[2026-02-06] Truth Bridge Milestone (Phase 1):** Completed the `analyze_venue_matchup` verification suite.
    - **Standardization:** Migrated to a **10-year lookback** standard across all bencharks.
    - **Intelligence:** Implemented **Auto-Diagnostic** runner. It compares `data/FINAL_ODI_MASTER.pkl` modification time against `ground_truth.json` to prove if a failure is due to data updates or code regressions.
    - **Verification:** User manually verified 240+ Statsguru benchmarks. Suite is currently **100% PASSING**.
    - **Reporting:** Standardized `report.json` with granular mapping (Home vs Visitor Wins).
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
- **[2026-02-11] Transition to Last 10 Form Metrics:**
    - **Engine Update:** Updated `TeamEngine.analyze_team_form` and `PlayerEngine._get_stats` to compute trends over the last 10 matches (~2-3 bilateral series).
    - **UI Optimization:** Implemented CSS guardrails (nowrap, reduced font-size) in `PlayerEngine.render_pro_table` to prevent doubled string density from cluttering the XI comparison dashboard.
    - **Sync:** Updated `interface.py` to trigger 10-match lookbacks. Consistent "Last 10" labels applied to legends and documentation.
