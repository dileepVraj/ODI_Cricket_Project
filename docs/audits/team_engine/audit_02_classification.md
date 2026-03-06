# AUDIT-02 - Layer Classification
**Audit Series:** Team Engine Compliance Audit
**File Audited:** `formats/odi/engines/team_engine.py`
**Date:** 2026-03-05
**Agent:** Codex (GPT-5)

---

## Section 1 - File Structure Observation

### Imports
- `from __future__ import annotations`
- `from types import MappingProxyType`
- `from typing import Optional, Union, cast`
- `import pandas as pd`
- `from core.calculators.team.matchup_calculator import calculate_away_performance_payload, calculate_continent_performance_payload, calculate_country_h2h_payload, calculate_global_h2h_payload, calculate_global_performance_payload, calculate_home_dominance_payload, calculate_team_form_payload`
- `from core.calculators.team.venue_calculator import calculate_home_fortress_payload, calculate_venue_bias_payload, calculate_venue_matchup_payload, calculate_venue_phases_payload`
- `from core.exceptions import ConfigurationError`
- `from core.interfaces.team_interface import ITeamEngine`
- `from core.interfaces.team_types import ComparisonReportRows, DataAccessPort, FormatConfig, MatrixReportRows, RecorderPort, SportConstants, TacticalThresholds, TeamFormRows, TeamMatchContext, VenueBiasReport, VenueMatchupReport, VenuePhasesReport`
- `from core.services.venue_service import VenueService`
- `from formats.odi.config.settings import ODI_COUNTRY_PREFIX_MAP`

### Classes
- `TeamEngine(ITeamEngine)`

### Methods Per Class
- `__init__(self, match_df: Optional[pd.DataFrame] = None, phase_df: Optional[pd.DataFrame] = None, dal: Optional[DataAccessPort] = None, format_rules: Optional[FormatConfig] = None) -> None`
- `_compute_reference_date(match_frame: pd.DataFrame) -> pd.Timestamp`
- `_require_match_context(self, match_context: Optional[TeamMatchContext]) -> TeamMatchContext`
- `_context_df(match_context: TeamMatchContext, key: str) -> pd.DataFrame`
- `_context_reference_date(self, match_context: TeamMatchContext) -> pd.Timestamp`
- `_require_format_config(self) -> FormatConfig`
- `_require_positive_int(self, raw_value: Union[int, str, float, None], config_key: str) -> int`
- `_min_balls_for_completed_innings(self) -> int`
- `_default_years_window(self) -> int`
- `_resolved_years(self, years_value: int) -> int`
- `_phase_rules(self) -> dict[str, list[int]]`
- `_require_tactical_thresholds(self, match_context: TeamMatchContext) -> TacticalThresholds`
- `_threshold(self, match_context: TeamMatchContext, key: str) -> int`
- `_require_sport_constants(self) -> SportConstants`
- `_sport_constant(self, key: str) -> int`
- `_resolved_team_form_limit(self, match_context: TeamMatchContext, limit_value: int) -> int`
- `analyze_home_fortress(self, stadium_name: str, home_team: str, opp_team: str = "All", years_back: int = 0, recorder: Optional[RecorderPort] = None, match_context: Optional[TeamMatchContext] = None) -> ComparisonReportRows`
- `analyze_venue_matchup_structured(self, stadium_name: str, home_team: str, opp_team: str, years_back: int = 0, match_context: Optional[TeamMatchContext] = None) -> VenueMatchupReport`
- `analyze_venue_phases(self, stadium_id: str, home_team: Optional[str] = None, away_team: Optional[str] = None, years: int = 0, recorder: Optional[RecorderPort] = None, match_context: Optional[TeamMatchContext] = None) -> VenuePhasesReport`
- `analyze_venue_bias(self, stadium_name: str, years_back: int = 0, recorder: Optional[RecorderPort] = None, match_context: Optional[TeamMatchContext] = None) -> Optional[VenueBiasReport]`
- `analyze_global_h2h(self, home_team: str, opp_team: str, years_back: int = 0, match_context: Optional[TeamMatchContext] = None) -> ComparisonReportRows`
- `analyze_country_h2h(self, home_team: str, opp_team: str = "All", country_name: Optional[str] = None, years_back: int = 0, recorder: Optional[RecorderPort] = None, match_context: Optional[TeamMatchContext] = None) -> ComparisonReportRows`
- `analyze_home_dominance(self, home_team: str, years_back: int = 0, recorder: Optional[RecorderPort] = None, match_context: Optional[TeamMatchContext] = None) -> MatrixReportRows`
- `analyze_away_performance(self, team_name: str, years_back: int = 0, recorder: Optional[RecorderPort] = None, match_context: Optional[TeamMatchContext] = None) -> MatrixReportRows`
- `analyze_global_performance(self, team_name: str, years_back: int = 0, match_context: Optional[TeamMatchContext] = None) -> MatrixReportRows`
- `analyze_continent_performance(self, team_name: str, continent: str, opp_team: str = "All", years_back: int = 0, match_context: Optional[TeamMatchContext] = None) -> MatrixReportRows | ComparisonReportRows`
- `analyze_team_form(self, team_name: str, opp_team: str = "All", continent: str = "All", limit: int = 0, recorder: Optional[RecorderPort] = None, match_context: Optional[TeamMatchContext] = None) -> TeamFormRows`

### Method Responsibilities (one line each)
- `__init__` - Stores immutable format configuration for engine execution.
- `_compute_reference_date` - Resolves a reference date from `start_date` column or current day fallback.
- `_require_match_context` - Validates that `match_context` exists and is dict-like.
- `_context_df` - Pulls a DataFrame from context by key and returns a defensive copy.
- `_context_reference_date` - Resolves and validates the effective reference date from context.
- `_require_format_config` - Returns mutable dict view of engine format config.
- `_require_positive_int` - Normalizes and validates positive integer config values.
- `_min_balls_for_completed_innings` - Reads and validates innings completeness threshold from config.
- `_default_years_window` - Reads and validates default years window from config.
- `_resolved_years` - Applies default years window when caller provides non-positive years.
- `_phase_rules` - Normalizes phase range rules from config into `dict[str, list[int]]`.
- `_require_tactical_thresholds` - Merges base and context tactical thresholds and normalizes values.
- `_threshold` - Fetches one required tactical threshold by key with validation.
- `_require_sport_constants` - Loads and validates required sport constants from config.
- `_sport_constant` - Fetches one required sport constant by key.
- `_resolved_team_form_limit` - Applies default form window limit when input limit is non-positive.
- `analyze_home_fortress` - Builds calculator input for home-fortress analysis and returns rows.
- `analyze_venue_matchup_structured` - Builds venue-matchup input and returns structured matchup report.
- `analyze_venue_phases` - Builds phase-analysis input bundle and returns phase report.
- `analyze_venue_bias` - Builds venue-bias input and returns optional bias report.
- `analyze_global_h2h` - Builds global head-to-head input and returns comparison rows.
- `analyze_country_h2h` - Builds country-filtered head-to-head input and returns rows.
- `analyze_home_dominance` - Builds home-dominance input and returns matrix rows.
- `analyze_away_performance` - Builds away-performance input and returns matrix rows.
- `analyze_global_performance` - Builds global-performance input and returns matrix rows.
- `analyze_continent_performance` - Builds continent-performance input and returns rows.
- `analyze_team_form` - Builds team-form input and returns form rows.

---

## Section 2 - Layer Classification

### Classification Table Evaluation
- Performs calculations taking data in and returning results out: **YES** - methods accept context/config/team parameters, call calculator functions with DataFrames, and return typed report rows/objects.
- Maps HTTP requests to domain functions: **NO** - no FastAPI/Flask/request/response imports or routing functions.
- Reads from or writes to a database: **NO** - no `duckdb`, SQL, or DAL I/O calls in method bodies.
- Renders UI components or displays data: **NO** - no frontend/UI rendering code.
- Extracts/transforms/loads data into a database: **NO** - no ETL write/load operations.
- Manages live match state/scraping/broadcasting: **NO** - no live-state singleton, scraper, websocket, or broadcaster logic.

### Result
**Primary Job:** Orchestrate team analysis computation by validating context/config, preparing calculator payloads, and returning typed analytical results.
**Layer Role:** Domain Core
**Applicable Mandates:** Mandate 1, Mandate 2, Mandate 3, Mandate 4
**Derived Laws In Scope:** Zero-Literal Law, Derivative Literal Law, Visual Silence Law, Anti-Grease Law, I/O Air-Gap Law

---

## Section 3 - Classification Conflicts

NO CLASSIFICATION CONFLICT confirmed.

---

## Section 4 - Mandate Scope Summary

This table drives AUDIT-03.
Every row marked IN SCOPE must be fully
audited in the next task.

| Mandate / Law               | In Scope |
|-----------------------------|----------|
| Mandate 1 - Functional Core | YES |
| Mandate 2 - Hexagonal Purity| YES |
| Mandate 3 - DOD             | YES |
| Mandate 4 - SRP             | YES |
| Zero-Literal Law            | YES |
| Derivative Literal Law      | YES |
| Visual Silence Law          | YES |
| Anti-Grease Law             | YES |
| I/O Air-Gap Law             | YES |

---

## Status
**AUDIT-02:** COMPLETE
**Classification:** Domain Core
**Conflicts Found:** NO
**Next Task:** AUDIT-03 - Mandate Compliance Audit
