# AUDIT-P08 - Player Engine: Stale Types + Group B Caller Investigation

**Task ID:** TASK-026 / P08  
**Audit Series:** Player Engine - Phase 10  
**Date:** 2026-03-05  
**Output file:** `docs/audits/player_engine/AUDIT-P08-stale-types.md`

---

## 1. Baseline Bouncer

```text
PASS: 100% compliance across 22 file(s).
```

P01 baseline match: YES.

---

## 2. SWEEP A - Stale Types

### Step A1 - Type Inventory

Type name: `BattingStats`  
Defined in: `core/interfaces/player_interface.py`  
Used in engine as: INTERNAL_ONLY

Type name: `BowlingStats`  
Defined in: `core/interfaces/player_interface.py`  
Used in engine as: INTERNAL_ONLY

Type name: `ContextStats`  
Defined in: `core/interfaces/player_interface.py`  
Used in engine as: INTERNAL_ONLY

Type name: `PlayerProfile`  
Defined in: `core/interfaces/player_interface.py`  
Used in engine as: BOTH

Type name: `MatchupStats`  
Defined in: `core/interfaces/player_interface.py`  
Used in engine as: INTERNAL_ONLY

Type name: `SquadMetrics`  
Defined in: `core/interfaces/player_interface.py`  
Used in engine as: INTERNAL_ONLY

Type name: `TacticalMatrixRow`  
Defined in: `core/interfaces/player_interface.py`  
Used in engine as: INTERNAL_ONLY

Type name: `SquadComparisonData`  
Defined in: `core/interfaces/player_interface.py`  
Used in engine as: BOTH

Type name: `SquadComparisonPayload`  
Defined in: `core/interfaces/team_types.py`  
Used in engine as: RETURN_TYPE

### Step A2 - Cross-reference Against Engine Usage

Type name: `BattingStats`  
Referenced in engine: YES

Type name: `BowlingStats`  
Referenced in engine: YES

Type name: `ContextStats`  
Referenced in engine: YES

Type name: `PlayerProfile`  
Referenced in engine: YES

Type name: `MatchupStats`  
Referenced in engine: NO  
If NO - stale confirmed: YES  
If NO - last known use: Legacy typed matchup contract superseded by `get_matchups` returning `List[DisplayRecord]`.

Type name: `SquadMetrics`  
Referenced in engine: NO  
If NO - stale confirmed: NO  
If NO - last known use: Still actively used inside `SquadComparisonData` dataclass fields in `player_interface.py`.

Type name: `TacticalMatrixRow`  
Referenced in engine: NO  
If NO - stale confirmed: YES  
If NO - last known use: Legacy tactical row contract superseded by `analyze_squad_types` returning `List[DisplayRecord]`.

Type name: `SquadComparisonData`  
Referenced in engine: YES

Type name: `SquadComparisonPayload`  
Referenced in engine: YES

### Step A3 - Stale Type Flags

[P08-FLAG-01] STALE_TYPE - `MatchupStats`:
              imported/defined in `core/interfaces/player_interface.py` but zero references
              in engine signatures or bodies.
              Carry to: P10 violation summary

[P08-FLAG-02] STALE_TYPE - `TacticalMatrixRow`:
              imported/defined in `core/interfaces/player_interface.py` but zero references
              in engine signatures or bodies.
              Carry to: P10 violation summary

---

## 3. SWEEP B - Group B Caller Investigation

Caller files scanned (from required grep plus Group B caller sweep):
- `api/context_builder.py`
- `api/engine_pool.py`
- `api/main.py`
- `formats/odi/__init__.py`
- `formats/odi/player_engine.py`
- `formats/odi/match_pack.py`
- `formats/odi/manifest.py`
- `formats/odi/engines/player_engine.py`
- `tests/verify_headless_player.py`
- `scripts/debug/inspect_sigs.py`
- `formats/odi/renderers/player_renderer.py`
- `formats/odi/tests/truth_bridge/compare_squads/test_runner.py`
- `core/services/param_mapper.py`
- `formats/odi/tests/truth_bridge/player_stats_validation/test_runner.py`
- `core/data_access.py`
- `core/player_engine.py`
- `core/interfaces/team_types.py`
- `core/match_pack/transformer.py`
- `core/interfaces/player_interface.py`

### Step B1 - Call Sites

Method: `analyze_squad_types`  
File: `formats/odi/engines/player_engine.py`  
Line: 300  
Call signature: `self.analyze_squad_types(team_a_name, team_a_players, team_b_players, years_back, context_df=squad_context_df,)`  
context_df passed: YES

Method: `analyze_squad_types`  
File: `formats/odi/engines/player_engine.py`  
Line: 307  
Call signature: `self.analyze_squad_types(team_b_name, team_b_players, team_a_players, years_back, context_df=squad_context_df,)`  
context_df passed: YES

Method: `analyze_squad_types`  
File: `formats/odi/engines/player_engine.py`  
Line: 569  
Call signature: `self.analyze_squad_types(team_a_name, team_a_players, team_b_players, years_back, context_df=squad_context_df)`  
context_df passed: YES

Method: `analyze_squad_types`  
File: `formats/odi/engines/player_engine.py`  
Line: 572  
Call signature: `self.analyze_squad_types(team_b_name, team_b_players, team_a_players, years_back, context_df=squad_context_df)`  
context_df passed: YES

Method: `analyze_squad_types`  
File: `api/main.py`  
Line: 391  
Call signature: `result = method(**call_params)`  
context_df passed: N/A

Method: `get_matchups`  
File: `formats/odi/engines/player_engine.py`  
Line: 316  
Call signature: `self.get_matchups(p, team_b_players, context_df=squad_context_df)`  
context_df passed: YES

Method: `get_matchups`  
File: `formats/odi/engines/player_engine.py`  
Line: 317  
Call signature: `self.get_matchups(p, team_a_players, context_df=squad_context_df)`  
context_df passed: YES

Method: `get_matchups`  
File: `formats/odi/engines/player_engine.py`  
Line: 578  
Call signature: `self.get_matchups(p, team_b_players, context_df=squad_context_df)`  
context_df passed: YES

Method: `get_matchups`  
File: `formats/odi/engines/player_engine.py`  
Line: 583  
Call signature: `self.get_matchups(p, team_a_players, context_df=squad_context_df)`  
context_df passed: YES

Method: `get_matchups`  
File: `api/main.py`  
Line: 391  
Call signature: `result = method(**call_params)`  
context_df passed: N/A

Method: `get_squad_comparison_data`  
File: `formats/odi/engines/player_engine.py`  
Line: 349  
Call signature: `self.get_squad_comparison_data(team_a_name, team_a_players, team_b_name, team_b_players, venue_id, years, context_df=context_df,)`  
context_df passed: YES

Method: `get_squad_comparison_data`  
File: `api/main.py`  
Line: 391  
Call signature: `result = method(**call_params)`  
context_df passed: N/A

Dynamic dispatch evidence for all three methods:
- `formats/odi/manifest.py` lines 360 and 370 register `engine_method` for `analyze_squad_types` and `get_matchups`; line 350 routes `compare_squads` which calls `get_squad_comparison_data` internally.
- `api/context_builder.py` lines 182-200 inject `context_df` for `get_squad_comparison_data`/`compare_squads`, `analyze_squad_types`, and `get_matchups` before `method(**call_params)`.

No external direct call sites were found in `api/`, `core/`, `formats/`, `scripts/`, or `tests/` outside engine-internal calls and dynamic API dispatch.

### Step B2 - Per-method Caller Verdict

Method: `analyze_squad_types`  
Total call sites found: 5  
Call sites passing context_df: 4  
Call sites omitting context_df: 0  
Files with omitted calls: NONE  
Verdict: SAFE_TO_REQUIRE

Method: `get_matchups`  
Total call sites found: 5  
Call sites passing context_df: 4  
Call sites omitting context_df: 0  
Files with omitted calls: NONE  
Verdict: SAFE_TO_REQUIRE

Method: `get_squad_comparison_data`  
Total call sites found: 2  
Call sites passing context_df: 1  
Call sites omitting context_df: 0  
Files with omitted calls: NONE  
Verdict: SAFE_TO_REQUIRE

---

## 4. SWEEP C - Consolidation

### 4.1 Stale Types Summary

| Type Name | Defined In | Stale | Flag |
|---|---|---|---|
| BattingStats | core/interfaces/player_interface.py | NO | - |
| BowlingStats | core/interfaces/player_interface.py | NO | - |
| ContextStats | core/interfaces/player_interface.py | NO | - |
| PlayerProfile | core/interfaces/player_interface.py | NO | - |
| MatchupStats | core/interfaces/player_interface.py | YES | P08-FLAG-01 |
| SquadMetrics | core/interfaces/player_interface.py | NO | - |
| TacticalMatrixRow | core/interfaces/player_interface.py | YES | P08-FLAG-02 |
| SquadComparisonData | core/interfaces/player_interface.py | NO | - |
| SquadComparisonPayload | core/interfaces/team_types.py | NO | - |

### 4.2 Group B Caller Summary

| Method | Call Sites | context_df Always Passed | Verdict |
|---|---:|---|---|
| analyze_squad_types | 5 | YES | SAFE_TO_REQUIRE |
| get_matchups | 5 | YES | SAFE_TO_REQUIRE |
| get_squad_comparison_data | 2 | YES | SAFE_TO_REQUIRE |

### 4.3 Combined Flag List

[P08-FLAG-01] STALE_TYPE - `MatchupStats` (carry to P10)  
[P08-FLAG-02] STALE_TYPE - `TacticalMatrixRow` (carry to P10)

Group B caller findings carry to P10 as architectural note (no compliance flags).

---

## 5. Verification

- [x] Every type in the inventory has a referenced/stale verdict.
- [x] Every discovered call site is documented individually with file/line/signature/context_df status.
- [x] No external direct call sites outside engine itself were found; dynamic API dispatch sites were documented explicitly.
- [x] Group B verdicts use only allowed values.
- [x] No fix recommendations included.
- [x] Bouncer output confirms match with P01 baseline.
