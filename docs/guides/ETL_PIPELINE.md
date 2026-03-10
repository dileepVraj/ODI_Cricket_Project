# ODI Data ETL Pipeline

## 1. OVERVIEW

The Cricket Algo-Trading Platform relies on an analytical database (`odi.duckdb`) strictly generated ahead of time. The ETL pipeline is responsible for parsing raw JSON files (from Cricsheet), flattening them into CSV artifacts, pre-calculating analytical insights, and ultimately ingesting everything into an immutable, read-only DuckDB database using an atomic swap mechanism.

- **Data Sources:** Raw Cricsheet JSON match files (`formats/odi/data/json_source/*.json`)
- **Output Targets:** 
  - Several processed CSV files mapping out granular data (`FINAL_ODI_MASTER.csv`, `MATCH_INFO.csv`, `MATCH_SQUADS.csv`, `processed_phase_stats.csv`, `processed_player_batting_stats.csv`, `processed_player_bowling_stats.csv`, `processed_player_stats.csv`, `player_metadata.csv`)
  - A definitive DuckDB database file (`formats/odi/data/odi.duckdb`) which is the runtime Single Source of Truth for the API.

---

## 2. PIPELINE STAGES

The ETL is orchestrated by `scripts/maintenance/update_data.py`, consisting of 5 main stages:

### Stage 1: JSON Conversion
- **Purpose:** Flatten hierarchical Cricsheet JSON structures into tabular deliveries (ball-by-ball), match metadata, and playing squads.
- **Input:** Raw JSON files (`formats/odi/data/json_source/*.json`).
- **Output:** `FINAL_ODI_MASTER.csv`, `MATCH_INFO.csv`, and `MATCH_SQUADS.csv`.
- **Key Script:** `formats/odi/utils/json_converter.py`
- **Failure Modes / Edge Cases:** Corrupted JSON files, missing top-level keys, missing extraction targets (abandoned games with no deliveries). Employs strict failure modes to halt on bad JSON schemas.

### Stage 2: Intelligence Refinery
- **Purpose:** Transform the flattened ball-by-ball data into pre-aggregated player metrics (batting, bowling, combined) and phase-based match statistics (powerplay, middle, death overs).
- **Input:** `FINAL_ODI_MASTER.csv`
- **Output:** `processed_player_batting_stats.csv`, `processed_player_bowling_stats.csv`, `processed_player_stats.csv`, `processed_phase_stats.csv`, `player_metadata.csv`.
- **Key Script:** `formats/odi/utils/refinery_script.py`
- **Failure Modes / Edge Cases:** Heavy RAM consumption (loads entire ball-by-ball dataset via pandas), dependent on `over_num` existing, and `is_wicket` derivations being accurate.

### Stage 3: DuckDB Ingestion
- **Purpose:** Instantiate a temporary DuckDB database, load all generated CSVs into corresponding tables, perform structural integrity validations, hydrate missing teams for abandoned matches, and commit a zero-downtime atomic swap to replace the live database.
- **Input:** All CSV artifacts generated in Stages 1 and 2.
- **Output:** `formats/odi/data/odi.duckdb`
- **Key Script:** `formats/odi/utils/ingest_to_db.py`
- **Failure Modes / Edge Cases:** Atomic swap can fail if file locks exist. Schema validations ensure no incomplete `innings` calculations or mismatched `match_id` parity exists. Venue resolution failures threshold trigger a DataIntegrityError.

### Stage 4: Reconciliation Checks
- **Purpose:** Perform post-ingestion audits to guarantee database validity and venue resolution percentages.
- **Input:** `odi.duckdb` and source balls CSV.
- **Output:** Terminal output & optional JSON report.
- **Key Script:** `scripts/maintenance/etl_reconciliation_report.py`
- **Failure Modes / Edge Cases:** Fails if unresolved venue ratios breach configurable thresholds (e.g., > 25%).

### Stage 5: Verification (Truth Bridge)
- **Purpose:** Run comprehensive truth bridge tests to ensure the loaded data produces expected engine calculation outcomes (verifying logic over the newly hydrated data).
- **Input:** The test suites and `odi.duckdb`.
- **Output:** Test Pass/Fail artifacts.
- **Key Script:** `formats/odi/tests/truth_bridge/run_all.py`

---

## 3. DUCKDB SCHEMA

All tables resident in the `odi.duckdb` runtime database alongside known/inferred columns (mostly strings/integers, floats for metrics):

- **balls**
  - **Columns:** `match_id`, `start_date`, `venue`, `batting_team`, `bowling_team`, `innings`, `over_num`, `ball_rank`, `ball`, `striker`, `non_striker`, `bowler`, `runs_off_bat`, `extras`, `wides`, `noballs`, `wicket_type`, `player_dismissed`, `winner`.
  - **Constraints:** Canonical identity enforced by uniqueness on (`match_id`, `innings`, `over_num`, `ball_rank`).

- **matches**
  - **Columns:** `match_id`, `start_date`, `venue`, `venue_id`, `team_bat_1`, `team_bat_2`, `winner`, `year`, `season`, `score_inn1`, `score_inn2`, `balls_inn1`, `balls_inn2`, `wickets_inn1`, `wickets_inn2`, `toss_winner`, `toss_decision`, `city`, `match_type`, `gender`, `competition`, `event_name`, `event_match_number`, `outcome_result`, `outcome_method`, `outcome_by_runs`, `outcome_by_wickets`, `neutral_venue`.
  - **Constraints:** Ensures missing innings 2 variables are populated as `0` if match had no result, or otherwise verified to exist if the match had a declared result.

- **player_stats** (Combined Role Metrics)
  - **Columns:** `player`, `team`, `opponent`, `innings`, `runs`, `balls`, `dismissals`, `role`, `context`.

- **player_batting_stats**
  - **Columns:** Same base fields + `dots`, `fours`, `sixes`, `strike_rate`, `average`.

- **player_bowling_stats**
  - **Columns:** Same base fields + `legal_balls`, `dots`, `fours`, `sixes`, `economy`, `strike_rate`, `average`.

- **phase_stats**
  - **Columns:** Pivot table generated fields depending on defined phases (e.g., `team`, `innings`, `{phase}_runs`, `{phase}_wkts`, `{phase}_balls`, etc).

- **squads**
  - **Columns:** `match_id`, `date`, `team`, `player`, `player_order`, `is_playing_xi`, `player_status`, `source`.

- **player_metadata**
  - **Columns:** `player`, `team`.

---

## 4. DATA FLOW DIAGRAM

```text
                           ┌─────────────────────────────┐
                           │    Raw JSON (Cricsheet)     │
                           └──────────────┬──────────────┘
                                          │
                                   [STAGE 1] JSON Conversion
                                          │
                  ┌───────────────────────┼───────────────────────┐
                  ▼                       ▼                       ▼
    [FINAL_ODI_MASTER.csv]        [MATCH_INFO.csv]         [MATCH_SQUADS.csv]
                  │                       │                       │
         [STAGE 2] Refinery               │                       │
                  │                       │                       │
     ┌────────────┼────────────┐          │                       │
     ▼            ▼            ▼          │                       │
[player_stats*] [phase_stats.csv] [player_metadata]               │
     │            │            │          │                       │
     └────────────┴────────────┴──────────┴───────────────────────┘
                                          │
                                 [STAGE 3] DB Ingestion
                                          │
                           ┌──────────────▼──────────────┐
                           │        [odi.duckdb.tmp]     │
                           │   (Integrity validations)   │
                           └──────────────┬──────────────┘
                                          │
                                 [Atomic File Swap]
                                          │
                           ┌──────────────▼──────────────┐
                           │          odi.duckdb         │
                           │(Immutable Single Source DB) │
                           └──────────────┬──────────────┘
                                          │
                               [STAGE 4 & 5] Audits
                                          │
                           ┌──────────────▼──────────────┐
                           │      FastAPI / DAL Layer    │
                           │         (Read-Only)         │
                           └──────────────▼──────────────┘
                                          │
                                 [gen_ai Skill Layer]
                             (data_templates/prompts/ → 
                              core/gen_ai/skills/ → 
                              LLM narrative generation)
                                          │
                           ┌──────────────▼──────────────┐
                           │     API Response Output     │
                           └─────────────────────────────┘
```

---

## 5. KEY FILES REFERENCE

- **`scripts/maintenance/update_data.py`** (Entry Point)
  Master CLI orchestrator. Accepts flags mapped to skipping stages (e.g. `--skip-conversion`).

- **`formats/odi/utils/json_converter.py`**
  Handles traversing the JSON AST. Translates varying structures (like older vs modern Cricsheet shapes) into continuous dimensional tables. Calculates hierarchical deliveries. 

- **`formats/odi/utils/refinery_script.py`**
  Loads master CSV into memory to apply domain models, generating derived analytics: bowler economies, dot probabilities, dimensional group-by aggregations (phase analysis). 

- **`formats/odi/utils/ingest_to_db.py`**
  Reads flat files utilizing `read_csv_auto`. Implements canonical key backfills (e.g. `over_num` / `ball_rank` bridges) if missing. Performs the final file integrity constraints before executing an OS-level atomic replace on `odi.duckdb`.

- **`scripts/maintenance/etl_reconciliation_report.py`**
  Performs data assurance comparisons between the generated SQL tables and intermediate CSVs.

- **`core/data_access.py`** (Consumer)
  Runtime interface that relies heavily on DuckDB ingestion correctness. It operates under read-only mode to fetch insights.
  > ⚠️ Registered high-risk boundary file (CLAUDE.md). 
  > Do not modify without architect approval and a 
  > completed impact trace.

---

## 6. KNOWN ISSUES AND EDGE CASES

- **Dirty Data (DNB, abandoned matches):** Handled defensively throughout. For instance, matches missing one team due to premature rain abandonment have their participants inferred by scanning ball arrays. Innings-2 variables are purposefully nulled rather than zeroed when a match is officially a "No Result" or "Abandoned" to prevent miscalculating metrics like run rates.
- **Large Memory Fingerprint in Refinery:** Stage 2 executes pandas abstractions over the entire `FINAL_ODI_MASTER.csv` simultaneously. This puts the ETL process dangerously close to local Ryzen 5 3500U hardware memory ceilings (~4 GB limits). 
- **Deterministic Venue Resolution:** Venue strings are messy. The pipeline depends on `config.shared.venues.resolve_venue_id`. If the ratio of unresolved venues exceeds a defined parameter (`max_unresolved_venue_ratio`, default 5-25%), DB ingestion crashes loudly.
- **Atomic File Swaps on Windows:** `os.replace` relies on system behavior for file locks. If a local script has a lingering connection open to `odi.duckdb`, Stage 3 can crash from an `OSError` file-in-use.

---

## 7. PHASE 12 READINESS NOTES

- **Delta Updates:** Currently, pipeline ingestion requires a *full rebuild* of the DuckDB instance whenever new baseline data is fetched. Moving to Phase 12 (Live Data Stream), this architecture must be re-evaluated to either support asynchronous batch incrementation without breaking atomic swaps, or isolating live state firmly away from the DuckDB file in singletons.
- **Real-Time Data Mutability:** As the database is configured to act strictly as a historical archive ("read-only"), the ETL mechanisms should not be repurposed to ingest live websocket streams. The live layer needs fully distinct memory-first architectures (e.g. pure python objects with threading locks) rather than writing to DB, to avoid failing Mandate 5 (Event-Driven State).
