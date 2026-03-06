# AUDIT-P02 - Player Engine Interface Contract Pre-Check

**Task ID:** TASK-026 / P02  
**Audit Series:** Player Engine - Phase 10  
**Date:** 2026-03-05  
**Depends on:** `docs/audits/player_engine/AUDIT-P01-structural-map.md`  
**Output File:** `docs/audits/player_engine/AUDIT-P02-interface-contract-precheck.md`

---

## 1. Read First Confirmation

Completed in order:
1. `docs/guides/ENGINEERING_STANDARDS_BACKEND.md` (Part 0: layer table + Mandate 1)
2. `docs/ai/SESSION_STATE.md`
3. `docs/audits/player_engine/AUDIT-P01-structural-map.md`
4. `core/interfaces/player_interface.py`
5. `formats/odi/engines/player_engine.py` (class definition + public method signatures)

---

## 2. Baseline Bouncer

```text
PASS: 100% compliance across 22 file(s).
```

P01 baseline match: YES.

---

## 3. Task Steps

### 3.1 ABC Contract Map

Abstract method: 1  
Name: get_active_squad  
Signature: def get_active_squad(self, team_name: str) -> List[str]:  
Return type: List[str]  
Docstring: Returns active squad members for a team.

Abstract method: 2  
Name: get_last_match_xi  
Signature: def get_last_match_xi(self, team_name: str) -> List[str]:  
Return type: List[str]  
Docstring: Returns the XI from the most recent match.

Abstract method: 3  
Name: get_squad_comparison_data  
Signature: def get_squad_comparison_data(self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None) -> SquadComparisonData:  
Return type: SquadComparisonData  
Docstring: Builds structured squad-comparison payload.

Abstract method: 4  
Name: compare_squads  
Signature: def compare_squads(self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None, recorder: Any = None) -> SquadComparisonData:  
Return type: SquadComparisonData  
Docstring: Compares two squads in a match context.

Abstract method: 5  
Name: analyze_squad_types  
Signature: def analyze_squad_types(self, team_name: str, players: List[str], opposition_bowlers: List[str], years: Optional[int] = None, recorder: Any = None, context_df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:  
Return type: List[Dict[str, Any]]  
Docstring: Analyzes batting archetypes against bowler styles.

Abstract method: 6  
Name: get_player_profile  
Signature: def get_player_profile(self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, years: int = 10) -> Optional[PlayerProfile]:  
Return type: Optional[PlayerProfile]  
Docstring: Fetches the complete 360-degree profile of a player.

Abstract method: 7  
Name: get_matchups  
Signature: def get_matchups(self, batter: str, bowlers: List[str], context_df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:  
Return type: List[Dict[str, Any]]  
Docstring: Returns Head-to-Head stats for a batter against a specific list of bowlers.

Abstract method: 8  
Name: analyze_player_profile  
Signature: def analyze_player_profile(self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, active_bowlers: Optional[List[str]] = None, years: int = 10) -> Optional[PlayerProfile]:  
Return type: Optional[PlayerProfile]  
Docstring: Context-aware player profile retrieval.

### 3.2 Engine Public Methods (from P01)

1. `def get_active_squad(self, team_name: str) -> List[str]`
2. `def get_last_match_xi(self, team_name: str, team_matches: Optional[pd.DataFrame] = None, match_balls_df: Optional[pd.DataFrame] = None) -> List[str]`
3. `def get_squad_comparison_data(self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None, context_df: Optional[pd.DataFrame] = None) -> SquadComparisonData`
4. `def compare_squads(self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None, recorder: Optional[TacticalRecorderPort] = None, context_df: Optional[pd.DataFrame] = None) -> SquadComparisonData`
5. `def analyze_squad_types(self, team_name: str, players: List[str], opposition_bowlers: List[str], years: Optional[int] = None, recorder: Optional[TacticalRecorderPort] = None, context_df: Optional[pd.DataFrame] = None) -> List[DisplayRecord]`
6. `def get_matchups(self, batter: str, bowlers: Optional[List[str]] = None, *, home_team: Optional[str] = None, opp_team: Optional[str] = None, home_xi: Optional[List[str]] = None, away_xi: Optional[List[str]] = None, context_df: Optional[pd.DataFrame] = None) -> List[DisplayRecord]`
7. `def get_player_profile(self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, years: Optional[int] = 10, raw_balls_df: Optional[pd.DataFrame] = None) -> Optional[PlayerProfile]`
8. `def analyze_player_profile(self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, active_bowlers: Optional[List[str]] = None, years: Optional[int] = 10, raw_balls_df: Optional[pd.DataFrame] = None) -> Optional[PlayerProfile]`

### 3.3 Contract Table

| Abstract Method | ABC Signature | Engine Signature | Status |
|---|---|---|---|
| get_active_squad | (self, team_name: str) -> List[str] | (self, team_name: str) -> List[str] | MATCH |
| get_last_match_xi | (self, team_name: str) -> List[str] | (self, team_name: str, team_matches: Optional[pd.DataFrame] = None, match_balls_df: Optional[pd.DataFrame] = None) -> List[str] | MISMATCH |
| get_squad_comparison_data | (self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None) -> SquadComparisonData | (self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None, context_df: Optional[pd.DataFrame] = None) -> SquadComparisonData | MISMATCH |
| compare_squads | (self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None, recorder: Any = None) -> SquadComparisonData | (self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None, recorder: Optional[TacticalRecorderPort] = None, context_df: Optional[pd.DataFrame] = None) -> SquadComparisonData | MISMATCH |
| analyze_squad_types | (self, team_name: str, players: List[str], opposition_bowlers: List[str], years: Optional[int] = None, recorder: Any = None, context_df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]] | (self, team_name: str, players: List[str], opposition_bowlers: List[str], years: Optional[int] = None, recorder: Optional[TacticalRecorderPort] = None, context_df: Optional[pd.DataFrame] = None) -> List[DisplayRecord] | MISMATCH |
| get_player_profile | (self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, years: int = 10) -> Optional[PlayerProfile] | (self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, years: Optional[int] = 10, raw_balls_df: Optional[pd.DataFrame] = None) -> Optional[PlayerProfile] | MISMATCH |
| get_matchups | (self, batter: str, bowlers: List[str], context_df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]] | (self, batter: str, bowlers: Optional[List[str]] = None, *, home_team: Optional[str] = None, opp_team: Optional[str] = None, home_xi: Optional[List[str]] = None, away_xi: Optional[List[str]] = None, context_df: Optional[pd.DataFrame] = None) -> List[DisplayRecord] | MISMATCH |
| analyze_player_profile | (self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, active_bowlers: Optional[List[str]] = None, years: int = 10) -> Optional[PlayerProfile] | (self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, active_bowlers: Optional[List[str]] = None, years: Optional[int] = 10, raw_balls_df: Optional[pd.DataFrame] = None) -> Optional[PlayerProfile] | MISMATCH |

Engine public methods without ABC counterpart:

| Engine Public Method | Status |
|---|---|
| NONE | NONE |

### 3.4 Contract Summary

- Total abstract methods in ABC: 8
- MATCH: 1
- MISMATCH: 7 (`get_last_match_xi`, `get_squad_comparison_data`, `compare_squads`, `analyze_squad_types`, `get_player_profile`, `get_matchups`, `analyze_player_profile`)
- MISSING: 0 (NONE)
- EXTRA engine methods not in ABC: 0 (NONE)
- Contract status: HAS GAPS

### 3.5 Flags for P07

- [P02-FLAG-01] MISMATCH - `get_last_match_xi`: ABC expects `(team_name)` only, engine adds `team_matches` and `match_balls_df` - carry to P07
- [P02-FLAG-02] MISMATCH - `get_squad_comparison_data`: ABC has no `context_df`, engine adds `context_df: Optional[pd.DataFrame]` - carry to P07
- [P02-FLAG-03] MISMATCH - `compare_squads`: ABC expects `recorder: Any`, engine has `recorder: Optional[TacticalRecorderPort]` and extra `context_df` - carry to P07
- [P02-FLAG-04] MISMATCH - `analyze_squad_types`: ABC return `List[Dict[str, Any]]` with `recorder: Any`; engine return `List[DisplayRecord]` with `recorder: Optional[TacticalRecorderPort]` - carry to P07
- [P02-FLAG-05] MISMATCH - `get_player_profile`: ABC expects `years: int = 10`, engine has `years: Optional[int] = 10` and extra `raw_balls_df` - carry to P07
- [P02-FLAG-06] MISMATCH - `get_matchups`: ABC expects `bowlers: List[str]` and return `List[Dict[str, Any]]`; engine uses optional bowlers, extra keyword-only params, and returns `List[DisplayRecord]` - carry to P07
- [P02-FLAG-07] MISMATCH - `analyze_player_profile`: ABC expects `years: int = 10`, engine has `years: Optional[int] = 10` and extra `raw_balls_df` - carry to P07

---

## 4. Verification

- [x] Every abstract method from the ABC appears in Step 3.3 (8/8).
- [x] Every public method from P01 appears in Step 3.3 or EXTRA table.
- [x] No fix recommendations are included.
- [x] No Part 0 compliance verdicts are included.
- [x] Bouncer output confirms match with P01 baseline.
