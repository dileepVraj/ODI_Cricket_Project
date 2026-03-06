# AUDIT-P01 - Player Engine Structural Map

**Task ID:** TASK-026 / P01  
**Audit Series:** Player Engine - Phase 10  
**Date:** 2026-03-05  
**File Audited:** `formats/odi/engines/player_engine.py`  
**Output File:** `docs/audits/player_engine/AUDIT-P01-structural-map.md`

---

## 1. Read First Confirmation

Read in full before Step 2:
1. `docs/guides/ENGINEERING_STANDARDS_BACKEND.md`
2. `docs/ai/SESSION_STATE.md`
3. `formats/odi/engines/player_engine.py`
4. `core/interfaces/player_interface.py`

Active task in session state confirmed as `TASK-026 / P01`.

---

## 2. Baseline Bouncer

```text
PASS: 100% compliance across 22 file(s).
```

---

## 3. Task Steps

### 3.1 Layer Role Classification

- Primary job: `player_engine.py` computes player and squad analytics payloads from provided DataFrames and request context.
- Layer role: Domain Core (analytical calculation engine).
- Applicable mandates: Mandates 1, 2, 3, and 4 apply.

### 3.2 File Structure Map

- Total line count: 710
- Import block:
- Stdlib:
  - `from typing import Dict, List, Optional, Tuple`
  - `import logging`
  - `import re`
- Third-party:
  - `import pandas as pd`
  - `import numpy as np`
- Internal:
  - `from config.shared.venues import get_venue_aliases`
  - `from core.calculators import MatchupEngine`
  - `from core.exceptions import ConfigurationError`
  - `from core.services.report_builder import ReportBuilder`
  - `from core.services.report_formatter import ReportFormatter`
  - `from core.services.squad_service import SquadService`
  - `from core.interfaces.player_interface import BattingStats, BowlingStats, ContextStats, IPlayerEngine, PlayerProfile, SquadComparisonData`
  - `from core.interfaces.team_types import DataAccessPort, DisplayRecord, FormatRulesMap, ManifestFunctionDef, SquadComparisonPayload, TacticalRecorderPort`
- Class name(s): `PlayerEngine`
- Constructor signature:
  - `def __init__(self, player_df: pd.DataFrame, meta_df: pd.DataFrame, squads_df: Optional[pd.DataFrame] = None, dal: Optional[DataAccessPort] = None, format_rules: Optional[FormatRulesMap] = None) -> None`
- Number of public methods: 8
- Number of private methods (prefixed `_`): 15
- Number of dunder methods: 1 (`__init__`)
- Number of property methods: 0
- Module-level constants/variables outside class: `logger`

### 3.3 Function-by-Function Map

Function: __init__
Type: dunder
Signature: def __init__(self, player_df: pd.DataFrame, meta_df: pd.DataFrame, squads_df: Optional[pd.DataFrame] = None, dal: Optional[DataAccessPort] = None, format_rules: Optional[FormatRulesMap] = None) -> None
Lines: 38-63
Line count: 26
Description: Initializes engine rules, dependent services, and source DataFrames, and normalizes `squads_df.match_id` when squad data is present.
Calls: _require_tactical_thresholds, _require_style_map, _require_player_roles, _require_default_player_role, _require_default_years_window, _require_engine_defaults
Data in: `player_df` DataFrame, `meta_df` DataFrame, optional `squads_df` DataFrame, optional DAL port, optional format rules map
Data out: `None`

Function: _require_nonempty_dict_rule
Type: private
Signature: def _require_nonempty_dict_rule(self, key: str) -> ManifestFunctionDef
Lines: 65-72
Line count: 8
Description: Fetches a required rule by key and raises a configuration error when the value is missing or not a non-empty dict.
Calls: NONE
Data in: `key` string
Data out: manifest rule dict (`ManifestFunctionDef`)

Function: _require_tactical_thresholds
Type: private
Signature: def _require_tactical_thresholds(self) -> Dict[str, int]
Lines: 74-84
Line count: 11
Description: Loads tactical thresholds from rules and converts each threshold value to an integer map.
Calls: _require_nonempty_dict_rule
Data in: none
Data out: `Dict[str, int]`

Function: _require_style_map
Type: private
Signature: def _require_style_map(self) -> Dict[str, str]
Lines: 86-88
Line count: 3
Description: Loads the style mapping rule and normalizes all keys and values to strings.
Calls: _require_nonempty_dict_rule
Data in: none
Data out: `Dict[str, str]`

Function: _require_player_roles
Type: private
Signature: def _require_player_roles(self) -> Dict[str, str]
Lines: 90-92
Line count: 3
Description: Loads the player role mapping rule and normalizes all keys and values to strings.
Calls: _require_nonempty_dict_rule
Data in: none
Data out: `Dict[str, str]`

Function: _require_default_player_role
Type: private
Signature: def _require_default_player_role(self) -> str
Lines: 94-101
Line count: 8
Description: Retrieves and validates the configured default player role string.
Calls: NONE
Data in: none
Data out: default role string

Function: _require_default_years_window
Type: private
Signature: def _require_default_years_window(self) -> int
Lines: 103-118
Line count: 16
Description: Retrieves, validates, and returns the default lookback years window as a positive integer.
Calls: NONE
Data in: none
Data out: positive integer years window

Function: _require_engine_defaults
Type: private
Signature: def _require_engine_defaults(self) -> Dict[str, int]
Lines: 120-130
Line count: 11
Description: Loads engine default settings and converts each configured default value to an integer map.
Calls: _require_nonempty_dict_rule
Data in: none
Data out: `Dict[str, int]`

Function: _get_player_role
Type: private
Signature: def _get_player_role(self, player_name: str) -> str
Lines: 132-134
Line count: 3
Description: Returns the configured role for a player name or falls back to the default role.
Calls: NONE
Data in: `player_name` string
Data out: role string

Function: _compute_reference_date
Type: private
Signature: def _compute_reference_date(self) -> pd.Timestamp
Lines: 136-146
Line count: 11
Description: Resolves a reference date from rules when valid, otherwise uses the current day floor timestamp.
Calls: NONE
Data in: none
Data out: pandas `Timestamp`

Function: _get_reference_date
Type: private
Signature: def _get_reference_date(self) -> pd.Timestamp
Lines: 148-151
Line count: 4
Description: Returns a cached reference date and computes it once if not already cached.
Calls: _compute_reference_date
Data in: none
Data out: pandas `Timestamp`

Function: _get_years_back
Type: private
Signature: def _get_years_back(self, years: Optional[int]) -> int
Lines: 153-162
Line count: 10
Description: Converts an optional years input into a validated positive integer lookback window.
Calls: NONE
Data in: optional integer-like `years`
Data out: positive integer years window

Function: _get_tactical_threshold
Type: private
Signature: def _get_tactical_threshold(self, key: str) -> int
Lines: 164-175
Line count: 12
Description: Returns a specific tactical threshold by key as an integer after key and value validation.
Calls: NONE
Data in: threshold `key` string
Data out: integer threshold value

Function: _get_engine_default
Type: private
Signature: def _get_engine_default(self, key: str) -> int
Lines: 177-188
Line count: 12
Description: Returns a specific engine default setting by key as an integer after key and value validation.
Calls: NONE
Data in: default-setting `key` string
Data out: integer default value

Function: get_active_squad
Type: public
Signature: def get_active_squad(self, team_name: str) -> List[str]
Lines: 191-197
Line count: 7
Description: Filters metadata rows for a team and returns a sorted unique player list for that team.
Calls: NONE
Data in: `team_name` string and `self.meta_df` DataFrame
Data out: `List[str]` of player names

Function: get_last_match_xi
Type: public
Signature: def get_last_match_xi(self, team_name: str, team_matches: Optional[pd.DataFrame] = None, match_balls_df: Optional[pd.DataFrame] = None) -> List[str]
Lines: 199-246
Line count: 48
Description: Returns the most recent XI for a team by preferring `squads_df` and falling back to recent match/ball context backscan logic.
Calls: _get_engine_default
Data in: `team_name`, optional `team_matches` DataFrame, optional `match_balls_df` DataFrame
Data out: `List[str]` of player names

Function: get_squad_comparison_data
Type: public
Signature: def get_squad_comparison_data(self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None, context_df: Optional[pd.DataFrame] = None) -> SquadComparisonData
Lines: 248-332
Line count: 85
Description: Builds the full structured squad comparison dataclass by combining filtered context metrics, tactical matrices, and matchup tables for both teams.
Calls: _get_years_back, _get_reference_date, analyze_squad_types, get_matchups
Data in: team names, squad player lists, venue id, optional years, optional context DataFrame
Data out: `SquadComparisonData` dataclass containing team metrics, player tables, matrices, and matchup dicts

Function: compare_squads
Type: public
Signature: def compare_squads(self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None, recorder: Optional[TacticalRecorderPort] = None, context_df: Optional[pd.DataFrame] = None) -> SquadComparisonData
Lines: 334-357
Line count: 24
Description: Provides a wrapper entrypoint that delegates squad comparison execution to `get_squad_comparison_data`.
Calls: get_squad_comparison_data
Data in: team names, squad player lists, venue id, optional years, optional recorder, optional context DataFrame
Data out: `SquadComparisonData`

Function: analyze_squad_types
Type: public
Signature: def analyze_squad_types(self, team_name: str, players: List[str], opposition_bowlers: List[str], years: Optional[int] = None, recorder: Optional[TacticalRecorderPort] = None, context_df: Optional[pd.DataFrame] = None) -> List[DisplayRecord]
Lines: 360-432
Line count: 73
Description: Produces tactical matrix rows for a squad against opposition bowlers within a lookback window and optionally records threshold-based tactical alerts.
Calls: _get_years_back, _get_reference_date, _get_tactical_threshold
Data in: team name, player list, opposition bowler list, optional years, optional recorder, optional context DataFrame
Data out: `List[DisplayRecord]` table rows

Function: get_matchups
Type: public
Signature: def get_matchups(self, batter: str, bowlers: Optional[List[str]] = None, *, home_team: Optional[str] = None, opp_team: Optional[str] = None, home_xi: Optional[List[str]] = None, away_xi: Optional[List[str]] = None, context_df: Optional[pd.DataFrame] = None) -> List[DisplayRecord]
Lines: 437-530
Line count: 94
Description: Computes batter-versus-bowler matchup aggregates and derived indicators (including bunny flags, average, and strike rate) from context ball data.
Calls: _get_tactical_threshold
Data in: batter name, optional bowler list, optional team/XI context, optional context DataFrame
Data out: `List[DisplayRecord]` matchup records

Function: _generate_comparison_payload
Type: private
Signature: def _generate_comparison_payload(self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None, context_df: Optional[pd.DataFrame] = None) -> SquadComparisonPayload
Lines: 532-597
Line count: 66
Description: Builds a regression payload for squad comparison by collecting both squads' metrics, tactical matrices, and matchup dictionaries.
Calls: _get_years_back, _get_reference_date, analyze_squad_types, get_matchups
Data in: team names, squad player lists, venue id, optional years, optional context DataFrame
Data out: `SquadComparisonPayload`

Function: _get_batting_milestones
Type: private
Signature: def _get_batting_milestones(self, df: pd.DataFrame) -> Tuple[int, int, int]
Lines: 599-605
Line count: 7
Description: Aggregates per-match runs to return counts of centuries, fifties, and highest score.
Calls: NONE
Data in: batting ball-level DataFrame
Data out: tuple `(centuries, fifties, highest_score)` as integers

Function: get_player_profile
Type: public
Signature: def get_player_profile(self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, years: Optional[int] = 10, raw_balls_df: Optional[pd.DataFrame] = None) -> Optional[PlayerProfile]
Lines: 607-686
Line count: 80
Description: Assembles a player's profile dataclass with career batting, optional bowling summary, and optional opposition/venue batting context slices.
Calls: _get_years_back, _get_reference_date, _get_batting_milestones, _get_player_role
Data in: player name, optional opposition, optional venue id, optional years, optional raw balls DataFrame
Data out: `PlayerProfile` dataclass or `None`

Function: analyze_player_profile
Type: public
Signature: def analyze_player_profile(self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, active_bowlers: Optional[List[str]] = None, years: Optional[int] = 10, raw_balls_df: Optional[pd.DataFrame] = None) -> Optional[PlayerProfile]
Lines: 688-710
Line count: 23
Description: Validates player presence and delegates context-aware profile retrieval to `get_player_profile`.
Calls: get_player_profile
Data in: player name, optional opposition, optional venue id, optional active bowler list, optional years, optional raw balls DataFrame
Data out: `PlayerProfile` dataclass or `None`

### 3.4 Call Graph

Public method call graph:

`get_active_squad()` [entry point]

`get_last_match_xi()`
  -> `_get_engine_default()`

`get_squad_comparison_data()`
  -> `_get_years_back()`
  -> `_get_reference_date()`
  -> `analyze_squad_types()`
      -> `_get_years_back()`
      -> `_get_reference_date()`
      -> `_get_tactical_threshold()`
  -> `get_matchups()`
      -> `_get_tactical_threshold()`

`compare_squads()`
  -> `get_squad_comparison_data()`

`analyze_squad_types()`
  -> `_get_years_back()`
  -> `_get_reference_date()`
  -> `_get_tactical_threshold()`

`get_matchups()`
  -> `_get_tactical_threshold()`

`get_player_profile()`
  -> `_get_years_back()`
  -> `_get_reference_date()`
  -> `_get_batting_milestones()`
  -> `_get_player_role()`

`analyze_player_profile()`
  -> `get_player_profile()`

Internal method call status:

`__init__()`
  -> `_require_tactical_thresholds()`
  -> `_require_style_map()`
  -> `_require_player_roles()`
  -> `_require_default_player_role()`
  -> `_require_default_years_window()`
  -> `_require_engine_defaults()`

`_require_tactical_thresholds()` -> `_require_nonempty_dict_rule()`
`_require_style_map()` -> `_require_nonempty_dict_rule()`
`_require_player_roles()` -> `_require_nonempty_dict_rule()`
`_require_engine_defaults()` -> `_require_nonempty_dict_rule()`
`_get_reference_date()` -> `_compute_reference_date()`
`_generate_comparison_payload()`
  -> `_get_years_back()`
  -> `_get_reference_date()`
  -> `analyze_squad_types()`
  -> `get_matchups()`

`_generate_comparison_payload()` [unused - not called internally by other methods in this file]

### 3.5 Surface-Level Observations

- File size is 710 lines.
- The module defines one class (`PlayerEngine`) and one module-level variable (`logger`).
- Method count is 24 total: 8 public, 15 private, and 1 dunder.
- Constructor stores three DataFrame attributes (`player_df`, `meta_df`, `squads_df`) and initializes two helper services (`SquadService`, `MatchupEngine`).
- Rule validation and normalization are front-loaded in constructor helper methods before analytics methods run.
- Squad-comparison output is exposed via dataclass return (`SquadComparisonData`) and also has a private regression payload builder (`_generate_comparison_payload`).
- `compare_squads()` is a thin delegator to `get_squad_comparison_data()`.
- `analyze_player_profile()` is a thin delegator to `get_player_profile()` after a player existence check.
- `get_matchups()` supports inferred bowler lists when explicit bowlers are not provided.
- No property methods are defined in this class.

---

## 4. Verification

- [x] Every method in the file has a corresponding entry in Step 3.3.
- [x] No compliance judgements appear in Steps 3.2-3.5.
- [x] Call graph in Step 3.4 accounts for all methods listed in Step 3.3.
- [x] Baseline bouncer output in Step 2 is pasted verbatim.
