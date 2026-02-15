# 🏗️ Cricket Algo-Trader — Application Architecture

## 1. Executive Summary

**Project:** Cricket Algo-Trader ("The Dugout")
**Purpose:** A high-frequency analytics dashboard for professional cricket traders. It bypasses raw averages to uncover contextual edge cases (e.g., "Left-Arm Pace vs Top Order at Wankhede") using granular ball-by-ball data.
**Core Philosophy:** *"Context over Content."* A player's batting average alone is meaningless — it only becomes actionable when filtered by venue, opponent, recent form, and match phase.

---

## 2. High-Level Architecture

The application follows a **4-Layer MVC Hybrid** pattern tailored for Jupyter environments, with an additional Verification Layer for data integrity.

```mermaid
graph TD
    subgraph "📁 Data Layer"
        SRC["JSON Source<br/>(Cricsheet)"]
        ING["Ingestion Engine<br/>(formats/odi/utils/json_converter.py)"]
        DB["DuckDB Runtime DB<br/>(odi.duckdb)"]
        CSV["Master CSV<br/>(FINAL_ODI_MASTER.csv)"]
        SRC -->|"Flatten JSON"| ING
        ING -->|"Load"| DB
        ING -->|"Backup"| CSV
    end

    subgraph "🧠 Logic Layer (core/)"
        FACADE["CricketAnalyzer<br/>(engine.py — Facade)"]
        DAL["Data Access Layer<br/>(data_access.py)"]
        TE["TeamEngine<br/>(team_engine.py)"]
        PE["PlayerEngine<br/>(player_engine.py)"]
        FACADE -->|"Context Manager"| DAL
        DAL -->|"Direct SQL Query"| TE
        DAL -->|"Direct SQL Query"| PE
    end

    subgraph "🖥️ Presentation Layer"
        UI["TraderCockpit<br/>(interface.py)"]
        NB["Dashboard<br/>(dashboard.ipynb)"]
        NB -->|"Initializes"| FACADE
        FACADE -->|"Returns Data"| UI
    end

    subgraph "📊 Report Layer"
        GEN["MatchPackGenerator<br/>(formats/odi/match_pack.py)"]
        TRANS["Transformer<br/>(transformer.py)"]
        INTERP["Interpreter<br/>(interpreter.py)"]
        JSON_OUT["Match Pack JSON"]
        FACADE -->|"Engine Calls"| GEN
        GEN -->|"Raw Data"| TRANS
        TRANS -->|"Clean Data"| INTERP
        INTERP -->|"+ Narrative"| JSON_OUT
    end

    DB -->|"Query"| DAL

    style SRC fill:#1a1a2e,stroke:#0f3460,color:#e94560
    style FACADE fill:#16213e,stroke:#0f3460,color:#e94560
    style UI fill:#0f3460,stroke:#533483,color:#e94560
    style GEN fill:#533483,stroke:#0f3460,color:#e94560
    style TB fill:#2c003e,stroke:#0f3460,color:#e94560
```

---

## 3. Layer-by-Layer Breakdown

### 3.1 Data Layer (The Foundation)

| File | Role | Key Details |
|:-----|:-----|:------------|
| `formats/odi/data/json_source/*.json` | Raw Source | Cricsheet ball-by-ball JSON files |
| `formats/odi/utils/json_converter.py` | Ingestion Engine | Flattens JSONs → 3 CSVs |
| `formats/odi/data/FINAL_ODI_MASTER.csv` | **Source of Truth** | Every ball bowled (1M+ rows, ~100MB+) |
| `formats/odi/data/MATCH_SQUADS.csv` | Context Data | Playing XI per match (enables DNB detection) |
| `formats/odi/data/MATCH_INFO.csv` | Metadata | Winner, Venue, Toss, Dates |
| `formats/odi/data/player_metadata.csv` | Player Index | Player → Primary Team mapping |
| `formats/odi/data/odi.duckdb` | Runtime DB | Tables: `balls`, `matches`, `player_stats`, `phase_stats`, `player_metadata`, `squads` |
| `config/shared/team_colors.py` | Static Config | Team colors (`TEAM_COLORS`) |
| `formats/odi/config/players.py` | Static Config | Bowler styles + player roles |
| `formats/odi/config/rankings.py` | Static Config | ODI rankings (`ODI_RANKINGS`) |
| `config/shared/venues.py` | Venue Normalization | `VENUE_MAP` aliases ("M. Chinnaswamy" → "IND_BANGALORE") |

**Data Update Workflow:**
1. Download latest `odis_json.zip` from Cricsheet.org
2. Extract into `formats/odi/data/json_source/`
3. Run `python formats/odi/utils/json_converter.py` (shim: `python utils/json_converter.py`)
4. Run `python formats/odi/utils/ingest_to_db.py` (rebuilds DuckDB)
5. Restart dashboard kernel (data loads into memory on startup)


**Performance: Self-Healing Pickle Cache**
On startup, `CricketAnalyzer` checks if a `.pkl` cache is newer than the CSV. If yes → fast-loads from pickle (~80% faster). If no → rebuilds the pickle automatically.

---

### 3.2 Logic Layer — The Brains

#### `engine.py` — The Facade (Controller v3.0)

The central orchestrator. Implements the **Facade Pattern** with **format-aware initialization**.

**Two Init Modes:**
- **Legacy:** `CricketAnalyzer("formats/odi/data/FINAL_ODI_MASTER.csv")` → auto-detects format from path
- **Modern:** `CricketAnalyzer(format_type="odi")` → explicit format selection

**Key Responsibilities:**
- Format detection and registry-based engine loading via `get_format_engines()`.
- DRY data loading via `core.data_loader.load_csv_or_pickle()`.
- Proper logging via `logging` module (no `print()` statements).
- Passthrough for all sub-engine analysis methods.

#### `core/team_engine.py` — Factory

Format-agnostic factory. `get_team_engine("odi")` dynamically loads `formats.odi.engines.team_engine.TeamEngine`.

The ODI implementation (`formats/odi/engines/team_engine.py`) handles:

| Function | Purpose |
|:---------|:--------|
| `analyze_head_to_head` | Win % matrix with breakdown (Bat 1st/2nd wins) |
| `analyze_home_fortress` | Home dominance with Smart Filters (excludes easy chases < 200) |
| `analyze_venue_phases` | Phase-by-phase scoring (PP/Middle/Death, 1st & 2nd innings) |
| `analyze_venue_bias` | Toss impact analysis (Bat 1st vs Field 1st win rates) |
| `analyze_home_dominance` | Home performance matrix vs all opponents |
| `analyze_away_performance` | Away win rates across all host countries |
| `analyze_team_form` | Recent form sequence (last 10 matches) |

#### `core/player_engine.py` — Factory

Format-agnostic factory. `get_player_engine("odi")` dynamically loads `formats.odi.engines.player_engine.PlayerEngine`.

The ODI implementation (`formats/odi/engines/player_engine.py`) handles:

| Function | Purpose |
|:---------|:--------|
| `compare_squads` | Full XI comparison: experience, form, matchups |
| `analyze_squad_types` | Tactical Matrix: batter avg vs each bowling type |
| `_get_stats` | Per-player: batting/bowling form, venue history, vs opponent |
| `_display_batter_vs_bowlers` | Batter vs specific bowler H2H (bunny detection) |
| `_generate_comparison_payload` | Structured data export for regression tests & reports |
| `analyze_player_profile` | Individual player deep-dive card |

#### `core/predictor.py` — Factory

Format-agnostic factory. `get_predictor_engine("odi")` loads `formats.odi.predictor.PredictorEngine`.
Weighted factor model combining venue bias, form, H2H, and conditions.

#### `config/format_registry.py` — Format Hub (v2.0)

Central registry for all cricket formats.

| Function | Purpose |
|:---------|:--------|
| `get_format_engines(fmt)` | Returns dict of engine classes for a format |
| `get_format_manifest(fmt)` | Loads the format's UI manifest |
| `get_format_config(fmt)` | Loads format-specific settings |
| `get_available_formats()` | Lists all registered formats |

---

### 3.3 Presentation Layer — The Face

#### `interface.py` — TraderCockpit

The main UI built with `ipywidgets` + custom HTML/CSS.

**Tabs:**
- **Team Analysis** — H2H, Fortress, Dominance matrices
- **Player Analysis** — Player cards, squad comparison
- **Phase Analysis** — Run rate charts per 10-over phase
- **Venue Analysis** — Toss bias, par scores

**Key Design Rules:**
- No heavy computation in `__init__` (Widget Performance Rule)
- All styling from `config/shared/team_colors.py` and `formats/odi/config/players.py` (Source of Truth Rule)
- 4-Tier badge system: Green (Elite) / Teal (Good) / Orange (Average) / Red (Poor)

#### `dashboard.ipynb` — Entry Point

Initializes `CricketAnalyzer` → creates `TraderCockpit` → displays UI.

---

### 3.4 Report Layer — The Combat Manual

The Match Pack pipeline generates AI-consumable JSON reports for pre-match analysis.

```
Engine Call (silent) → Transformer (clean data) → Interpreter (narrative + context) → JSON
```

#### `formats/odi/match_pack.py` — The Orchestrator

Chains engine calls through the transformer and interpreter pipeline. Uses `_silent_call()` to suppress engine stdout/UI output while capturing return values.

**Report Structure (4 Chapters):**
1. **Macro Context** — Global H2H, team form, dominance matrices
2. **Battlefield** — Fortress check, venue H2H, toss bias
3. **Tactical Engine** — Phase analysis, condition weights
4. **Player Intelligence** — Squad comparison, tactical matrix, matchups, player stats, bowling roster

#### `core/transformer.py` — The Data Cleaner

Converts raw engine output (HTML strings, emoji-decorated dicts, flat `[{Metric, Value}]` lists) into clean structured JSON.

| Function | Input → Output |
|:---------|:---------------|
| `transform_h2h_slim` | `[{Metric, Value}]` → wins/losses only (no averages) |
| `transform_h2h_report` | `[{Metric, Value}]` → full H2H with batting averages |
| `transform_venue_bias` | Flat dict → structured toss/decision analysis |
| `transform_team_form` | Form dict → summary stats (no match details) |
| `transform_dominance_matrix` | Matrix rows → aggregated win/loss stats |
| `transform_squad_comparison` | Nested payload → clean squad/matrix/matchup data |
| `transform_player_stats` | `_get_stats` dict → batting/bowling/venue objects |

#### `core/interpreter.py` — The Intelligence Layer

Adds narrative context, trend detection, and contextual tags to transformed data.

| Function | What It Adds |
|:---------|:-------------|
| `interpret_h2h` | Dominance narrative, trend analysis, context tags |
| `interpret_form` | Momentum assessment, win quality, trend reasoning |
| `interpret_fortress` | Fortress strength rating (0-100) |
| `interpret_toss_bias` | Toss decision alignment with match context |
| `interpret_dominance` | Home/Away strength classification |
| `interpret_conditions` | Pitch/Time/Toss condition weights |
| `analyze_bowling_roster` | Bowling composition vs pitch suitability |
| `generate_executive_summary` | Cross-chapter tactical summary |

---

### 3.5 Verification Layer — Truth Bridge

A non-destructive verification system that auto-diagnoses test failures.

**Core Workflow:**
1. **SEED**: Capture baseline engine outputs as JSON snapshots
2. **REFACTOR**: Make code changes
3. **VALIDATE**: Compare current output vs baseline
   - **PASS** — Output matches exactly
   - **DATA_DRIFT** — Results changed because new matches were added (expected)
   - **LOGIC_REGRESSION** — Results changed despite identical Match IDs (critical bug)

**Auto-Diagnosis:** Every engine function returns `MATCH_IDS` in its payload. The Truth Bridge compares file modification timestamps and match ID sets to distinguish drift from regression.

**Suites:**

| Suite | Coverage |
|:------|:---------|
| `analyze_venue_matchup` | Toss bias, ground par stats (240 benchmarks) |
| `check_fortress` | Home dominance, smart chasing filters |
| `compare_squads` | Batter vs bowler tactical parity |
| `global_performance` | Team win/loss metrics |
| `recent_form` | Sequence-based form for 9 teams across 6 continents |
| `analyze_phases` | Phase scoring patterns (~500 permutations) |

---

## 4. Directory Structure

```text
/
|-- dashboard.ipynb              # ENTRY POINT
|-- engine.py                    # Facade v3.0 (Format-Aware Controller)
|-- interface.py                 # UI (TraderCockpit)
|-- pyproject.toml               # Python packaging
|-- requirements.txt             # Pinned dependencies
|-- .env.example                 # Environment config template
|
|-- config/
|   |-- format_registry.py       # Format Hub v2.0 (factories, manifests, configs)
|   |-- settings.py              # Global defaults (overridden per-format)
|   `-- shared/
|       |-- team_colors.py       # TEAM_COLORS (Source of Truth)
|       |-- venues.py            # VENUE_MAP + aliases
|       `-- themes.py            # UI theme constants
|
|-- core/                        # Format-Agnostic Layer
|   |-- team_engine.py           # Factory → get_team_engine("odi")
|   |-- player_engine.py         # Factory → get_player_engine("odi")
|   |-- predictor.py             # Factory → get_predictor_engine("odi")
|   |-- data_access.py           # DuckDB DAL (parameterized SQL)
|   |-- data_loader.py           # CSV/Pickle cache (DRY)
|   |-- base_engine.py           # Shared safe-math utilities
|   |-- transformer.py           # Data Cleaner (Engine → JSON)
|   |-- interpreter.py           # Intelligence Layer (Narrative + Tags)
|   |-- exceptions.py            # Custom error hierarchy
|   `-- interfaces/              # Protocol contracts (ITeamEngine)
|
|-- formats/
|   `-- odi/
|       |-- __init__.py          # Exports: TeamEngine, PlayerEngine, PredictorEngine, FORMAT_CONFIG
|       |-- manifest.py          # UI capability declaration
|       |-- predictor.py         # ODI prediction model
|       |-- match_pack.py        # Combat Manual Orchestrator
|       |-- config/              # ODI settings, rankings, players
|       |-- engines/             # ODI TeamEngine, PlayerEngine
|       |-- data/                # ODI datasets + DuckDB runtime
|       |-- reports/             # ODI match pack outputs
|       |-- tests/               # Truth Bridge + Regression suites
|       |-- utils/               # Ingestion + refinery scripts
|       |-- tools/               # Maintenance tools
|       `-- scripts/             # Maintenance scripts
|
|-- scripts/
|   `-- update_data.py           # Master Pipeline Orchestrator
|
|-- tests/                       # Cross-format integration tests
|
`-- docs/                        # Architecture, guides, reports, AI context
```

---

## 5. Key Design Patterns

| Pattern | Where | Why |
|:--------|:------|:----|
| **Facade** | `engine.py` → `CricketAnalyzer` | Hides sub-engine complexity from UI |
| **Factory** | `core/*.py` → `get_team_engine(fmt)` | Format-agnostic dynamic loading via registry |
| **Dependency Injection** | `engine.py` creates `raw_df` once → injects into sub-engines | Single DataFrame in memory |
| **Silent Call** | `formats/odi/match_pack.py` → `_silent_call()` | Engine methods generate data silently; generator captures return values |
| **Self-Healing Cache** | `core/data_loader.py` → Pickle auto-rebuild | ~80% faster startup when data hasn't changed |
| **Defensive Coding** | All engines + `core/base_engine.py` | NaN-safe math via `_safe_divide()`, `_safe_float()` |
| **Source of Truth** | `config/shared/team_colors.py` + `formats/odi/config/players.py` | All colors, roles, styles centralized — never hardcoded |
| **Truth Bridge** | `formats/odi/tests/truth_bridge/` | Auto-diagnoses DATA_DRIFT vs LOGIC_REGRESSION |
| **Format Registry** | `config/format_registry.py` | Central hub for format engines, manifests, configs |

---

## 6. Data Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant NB as dashboard.ipynb
    participant F as CricketAnalyzer (Facade)
    participant TE as TeamEngine
    participant PE as PlayerEngine
    participant UI as TraderCockpit

    U->>NB: Opens Dashboard
    NB->>F: CricketAnalyzer(filepath)
    F->>F: load_data() → CSV/Pickle → DataFrame
    F->>TE: TeamEngine(raw_df, match_df)
    F->>PE: PlayerEngine(raw_df, player_df, meta_df)
    NB->>UI: TraderCockpit(analyzer)
    UI->>U: Renders Dashboard

    U->>UI: Selects "India vs England, Wankhede"
    UI->>F: analyze_home_fortress(venue, home, opp, years)
    F->>TE: Delegates to TeamEngine
    TE->>TE: Filter by venue/team → Compute stats
    TE->>F: Returns structured dict + MATCH_IDS
    F->>UI: Returns data
    UI->>U: Renders HTML Table with badges
```

---

## 7. Match Pack Pipeline

```mermaid
sequenceDiagram
    participant MPG as MatchPackGenerator
    participant F as CricketAnalyzer
    participant T as Transformer
    participant I as Interpreter
    participant OUT as JSON File

    MPG->>F: _silent_call(analyze_global_h2h, ...)
    F-->>MPG: Raw engine output (HTML/dicts)
    MPG->>T: transform_h2h_slim(raw_data)
    T-->>MPG: Clean structured dict
    MPG->>I: interpret_h2h(clean_data)
    I-->>MPG: Data + Narrative + Context Tags
    MPG->>MPG: Assemble all chapters
    MPG->>MPG: _strip_internal_keys() (remove _match_ids)
    MPG->>OUT: Write JSON (MatchPack_*.json)
```
