# CURRENT_ARCHITECTURE.md - System Audit & Overhaul Map

This document provides a comprehensive map of the current state of the Cricket Algo-Trader codebase as of February 2026.

## 1. Directory Tree

```text
c:\Cricket_Project_Stable
├── api/                        # FastAPI Application Layer
│   ├── schemas/                # Pydantic Request/Response Models
│   ├── services/               # API-specific business logic
│   ├── engine_pool.py          # Singleton Engine Management
│   ├── main.py                 # REST Entry Point (Manifest-Driven)
│   └── serializers.py          # Adapter for JSON-safe engine outputs
├── config/                     # System Configuration
│   ├── shared/                 # Team colors, venue mappings, aliases
│   └── format_registry.py      # Registry linking format keys to modules
├── core/                       # Agnostic Business Logic & Data Layer
│   ├── interfaces/             # Engine Abstract Base Classes
│   ├── match_pack/             # JSON Report Generation Logic
│   ├── services/               # Param Mapping, Enrichment, Fallbacks
│   ├── base_engine.py          # Shared Engine Utilities
│   ├── data_access.py          # DuckDB DAL (Single Source of Truth)
│   ├── data_loader.py          # Registry-aware Data Factory
│   └── exceptions.py           # Domain-specific Errors
├── data_templates/             # Ingestion & ETL Schema Templates
├── docs/                       # Project Documentation & AI Memory
├── formats/                    # Format-Specific Implementations
│   └── odi/                    # Men's ODI Implementation
│       ├── config/             # Role definitions, styles, rankings
│       ├── engines/            # HEAVY LOGIC: team_engine, player_engine
│       ├── manifest.py         # UI Manifest (Architecture Driver)
│       ├── match_pack.py       # Analyst Report Orchestrator
│       └── predictor.py        # Score Projection Logic
├── frontend/                   # Next.js / TypeScript Frontend
├── scripts/                    # Maintenance & Pipeline Scripts
├── engine.py                   # Root Facade (CricketAnalyzer)
└── AI_MEMORY.md                # Living Project Context
```

## 2. File Responsibility Matrix

| File Path | Core Responsibility | Coupling/Dependency |
| :--- | :--- | :--- |
| `api/main.py` | Universal REST router. Dispatches requests to engines based on the `manifest.py` function keys. | Coupled to `engine_pool.py` and `core/services/param_mapper.py`. |
| `api/engine_pool.py` | Singleton pattern for initializing and caching format-specific `CricketAnalyzer` instances. | Relies on `config/format_registry.py` for format discovery. |
| `core/data_access.py` | High-performance DuckDB Data Access Layer (DAL). The ONLY module allowed to run SQL. | Hardcoded to DuckDB schema; coupled to `config/shared/venues.py` for alias expansion. |
| `engine.py` | The Root Facade (`CricketAnalyzer`). Coordinates data loading and delegating to sub-engines. | Hardcoded to assume `team_engine`, `player_engine`, and `predictor_engine` attributes exist. |
| `core/services/param_mapper.py` | Maps unified API context (Venue ID, Teams) to internal engine method arguments. | Deeply coupled to the structure of the `manifest.py`. |
| `formats/odi/engines/team_engine.py` | Calculates team-level stats (Fortress, H2H, Venue Bias). Contains 1,500+ lines of analysis. | Coupled to ODI-specific thresholds and `ITeamEngine` interface. |
| `formats/odi/engines/player_engine.py` | Calculates squad-level comparisons, tactical matrices, and player profiles. | Coupled to `BOWLER_STYLES` and `PLAYER_ROLES` in `formats/odi/config/`. |
| `formats/odi/manifest.py` | The "Metadata as Truth" file. Defines what categories, tabs, and filters appear in the UI. | Standardized schema; interpreted by `api/main.py` and Frontend. |
| `api/serializers.py` | Adapter layer. Converts DataFrames and Dataclasses into JSON-safe dictionaries. | Highly generic; no external coupling. |

## 3. The 'Heavy Logic' Identification (Targets for Overhaul)

The following logic is currently isolated in the `formats/odi/` directory but should be moved to `core/` to make the system truly format-agnostic:

*   **Smart Filter Logic (`team_engine.py -> apply_smart_filters`)**: Decision logic for excluding short/abandoned matches based on balls bowled. Move to `core/services/match_filter_service.py` with configurable thresholds per format.
*   **Vectorized Performance Metrics (`team_engine.py -> _calculate_team_stats`)**: Pure pandas/numpy transformations for calculating win/loss averages and scores. Move to a generic `core/calculators/team_metrics.py`.
*   **Archetype Analysis (`player_engine.py -> analyze_squad_types`)**: The logic that computes batter strike-rates vs bowling types. Move to `core/calculators/matchup_engine.py`.
*   **Squad Aggregate Metrics (`player_engine.py -> _calculate_squad_metrics`)**: Summation of career runs, wickets, and caps for a list of players. Move to `core/services/squad_service.py`.

## 4. Unnecessary / Redundant Code

1.  **`legacy/interface.py`**: A 33KB Streamlit/CLI relic. Obsolete now that the Next.js API-driven frontend is operational.
2.  **`engine.py` Proxy Methods**: Methods like `CricketAnalyzer.analyze_home_fortress` are redundant wrappers now that `api/main.py` resolves methods dynamically via the manifest.
3.  **Duplicate `context_linter.py`**: Present in both the root directory and `scripts/maintenance/`. The root version should be deleted.
4.  **In-Memory Venue Standardizer (`engine.py -> _smart_standardize_venues`)**: This logic is partially duplicated in `core/data_access.py` and `config/shared/venues.py`. Standardized venue IDs (DuckDB Level) should replace fuzzy name matching in the engine.
