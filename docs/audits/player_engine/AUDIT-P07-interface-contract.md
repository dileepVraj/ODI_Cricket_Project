# AUDIT-P07 - Player Engine Interface Contract Deep Dive

**Task ID:** TASK-026 / P07  
**Audit Series:** Player Engine - Phase 10  
**Date:** 2026-03-05  
**Output File:** `docs/audits/player_engine/AUDIT-P07-interface-contract.md`

---

## 1. Baseline Bouncer

```text
PASS: 100% compliance across 22 file(s).
```

P01 baseline match: YES.

---

## 2. Step 3.1 - P02 Mismatch Flag Investigations

Method: `get_last_match_xi`  
P02 flag: `P02-FLAG-01`  
Signature delta: ABC exposes only `team_name`; engine adds optional `team_matches` and `match_balls_df`.  
Direction: IMPROVEMENT  
Honours ABC intent: PARTIALLY  
Evidence: Body returns recent XI from `self.squads_df` first, then fallback reconstruction from injected match/ball context when available.  
Recommended action: UPDATE_ABC

Method: `get_squad_comparison_data`  
P02 flag: `P02-FLAG-02`  
Signature delta: Engine adds optional `context_df` input absent in ABC.  
Direction: IMPROVEMENT  
Honours ABC intent: YES  
Evidence: Body still builds the same `SquadComparisonData` contract while allowing caller-supplied context scoping.  
Recommended action: UPDATE_ABC

Method: `compare_squads`  
P02 flag: `P02-FLAG-03`  
Signature delta: Engine tightens `recorder` from `Any` to `Optional[TacticalRecorderPort]` and adds optional `context_df`.  
Direction: IMPROVEMENT  
Honours ABC intent: YES  
Evidence: Body delegates to `get_squad_comparison_data` and preserves the same return contract.  
Recommended action: UPDATE_ABC

Method: `analyze_squad_types`  
P02 flag: `P02-FLAG-04`  
Signature delta: Engine replaces `recorder: Any` with `Optional[TacticalRecorderPort]` and return type `List[Dict[str, Any]]` with `List[DisplayRecord]`.  
Direction: IMPROVEMENT  
Honours ABC intent: YES  
Evidence: Body computes tactical breakdown and returns display records from formatter output, matching tactical-table intent.  
Recommended action: UPDATE_ABC

Method: `get_player_profile`  
P02 flag: `P02-FLAG-05`  
Signature delta: Engine uses `years: Optional[int]` and adds optional `raw_balls_df`.  
Direction: IMPROVEMENT  
Honours ABC intent: YES  
Evidence: Body still returns `Optional[PlayerProfile]` and enriches batting milestones only when raw balls are injected.  
Recommended action: UPDATE_ABC

Method: `get_matchups`  
P02 flag: `P02-FLAG-06`  
Signature delta: Engine makes `bowlers` optional, adds keyword-only team/XI context inputs, and returns `List[DisplayRecord]` instead of `List[Dict[str, Any]]`.  
Direction: IMPROVEMENT  
Honours ABC intent: PARTIALLY  
Evidence: Body supports both explicit bowler lists and inferred-bowler computation, but introduces keyword-only invocation shape not represented by ABC.  
Recommended action: UPDATE_ABC

Method: `analyze_player_profile`  
P02 flag: `P02-FLAG-07`  
Signature delta: Engine uses `years: Optional[int]` and adds optional `raw_balls_df`.  
Direction: IMPROVEMENT  
Honours ABC intent: YES  
Evidence: Body preserves gate-and-delegate behavior and still returns `Optional[PlayerProfile]`.  
Recommended action: UPDATE_ABC

---

## 3. Step 3.2 - DUAL_DATA_PATH Investigations (from P03)

Method: `get_last_match_xi`  
Path 1 (no injection): Uses constructor-injected `self.squads_df` to read latest match XI.  
Path 2 (with injection): Uses injected `team_matches` and `match_balls_df` as fallback path to reconstruct XI.  
Path 1 is Mandate 1 clean: YES  
Paths computationally equivalent: PARTIALLY  
Pattern assessment: NEEDS_ARCHITECT_DECISION

Method: `get_squad_comparison_data`  
Path 1 (no injection): Creates empty `squad_context_df` and continues pipeline with empty base context.  
Path 2 (with injection): Uses injected `context_df` as analysis base after date filtering.  
Path 1 is Mandate 1 clean: YES  
Paths computationally equivalent: NO  
Pattern assessment: NEEDS_ARCHITECT_DECISION

Method: `analyze_squad_types`  
Path 1 (no injection): Returns `[]` immediately when `context_df` is absent.  
Path 2 (with injection): Runs full tactical analysis pipeline on injected context.  
Path 1 is Mandate 1 clean: YES  
Paths computationally equivalent: NO  
Pattern assessment: NEEDS_ARCHITECT_DECISION

Method: `get_matchups`  
Path 1 (no injection): Returns `[]` immediately when `context_df` is absent.  
Path 2 (with injection): Runs grouped matchup aggregation from injected context.  
Path 1 is Mandate 1 clean: YES  
Paths computationally equivalent: NO  
Pattern assessment: NEEDS_ARCHITECT_DECISION

Method: `get_player_profile`  
Path 1 (no injection): Uses constructor-injected `self.player_df`; raw-ball milestones remain default when `raw_balls_df` absent.  
Path 2 (with injection): Uses injected `raw_balls_df` to compute batting milestones within lookback window.  
Path 1 is Mandate 1 clean: YES  
Paths computationally equivalent: PARTIALLY  
Pattern assessment: NEEDS_ARCHITECT_DECISION

---

## 4. Step 3.3 - ABC Violations (ABC_FIX Items)

Method: `compare_squads`  
ABC violation: `recorder: Any = None`  
Engine equivalent: `recorder: Optional[TacticalRecorderPort] = None`  
Fix required: YES - update ABC to match engine's typed version

Method: `analyze_squad_types`  
ABC violation: `recorder: Any = None`  
Engine equivalent: `recorder: Optional[TacticalRecorderPort] = None`  
Fix required: YES - update ABC to match engine's typed version

Method: `analyze_squad_types`  
ABC violation: `-> List[Dict[str, Any]]`  
Engine equivalent: `-> List[DisplayRecord]`  
Fix required: YES - update ABC to match engine's typed version

Method: `get_matchups`  
ABC violation: `-> List[Dict[str, Any]]`  
Engine equivalent: `-> List[DisplayRecord]`  
Fix required: YES - update ABC to match engine's typed version

---

## 5. Step 3.4 - EXTRA Engine Methods

CONFIRMED - no EXTRA methods.

---

## 6. Step 3.5 - Recommendation Blocks

ABC RECOMMENDATION BLOCK
========================
Action required: YES

[ABC-REC-01] UPDATE_ABC - `get_last_match_xi`:
             Update signature to: `def get_last_match_xi(self, team_name: str, team_matches: Optional[pd.DataFrame] = None, match_balls_df: Optional[pd.DataFrame] = None) -> List[str]`
             Reason: Engine contract supports explicit fallback context not represented in ABC.

[ABC-REC-02] UPDATE_ABC - `get_squad_comparison_data`:
             Update signature to: `def get_squad_comparison_data(self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: Optional[int] = None, context_df: Optional[pd.DataFrame] = None) -> SquadComparisonData`
             Reason: Engine supports injected context windowing used by downstream calculations.

[ABC-REC-03] FIX_ANY - `compare_squads`:
             Replace `recorder: Any = None` with `recorder: Optional[TacticalRecorderPort] = None` and add `context_df: Optional[pd.DataFrame] = None`
             Reason: Mandate 4 violation in ABC itself and missing engine capability.

[ABC-REC-04] FIX_ANY - `analyze_squad_types`:
             Replace `recorder: Any = None` with `recorder: Optional[TacticalRecorderPort] = None`
             Reason: Mandate 4 violation in ABC itself.

[ABC-REC-05] FIX_ANY - `analyze_squad_types`:
             Replace return `List[Dict[str, Any]]` with `List[DisplayRecord]`
             Reason: Mandate 4 violation in ABC itself and engine uses stronger typed return.

[ABC-REC-06] UPDATE_ABC - `get_player_profile`:
             Update signature to: `def get_player_profile(self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, years: Optional[int] = 10, raw_balls_df: Optional[pd.DataFrame] = None) -> Optional[PlayerProfile]`
             Reason: Engine allows optional years coercion and optional raw-ball enrichment path.

[ABC-REC-07] FIX_ANY - `get_matchups`:
             Replace return `List[Dict[str, Any]]` with `List[DisplayRecord]` and update signature to `def get_matchups(self, batter: str, bowlers: Optional[List[str]] = None, *, home_team: Optional[str] = None, opp_team: Optional[str] = None, home_xi: Optional[List[str]] = None, away_xi: Optional[List[str]] = None, context_df: Optional[pd.DataFrame] = None) -> List[DisplayRecord]`
             Reason: Mandate 4 violation in ABC itself and ABC must reflect engine invocation shape.

[ABC-REC-08] UPDATE_ABC - `analyze_player_profile`:
             Update signature to: `def analyze_player_profile(self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, active_bowlers: Optional[List[str]] = None, years: Optional[int] = 10, raw_balls_df: Optional[pd.DataFrame] = None) -> Optional[PlayerProfile]`
             Reason: Engine adds optional raw-ball context and optional-years alignment.

DUAL_DATA_PATH RECOMMENDATION BLOCK
===================================
Pattern verdict: ARCHITECT_DECISION_REQUIRED

Decision needed:
- Whether dual-path APIs should remain as a supported contract pattern (constructor-backed/default path plus injected-context path), or be collapsed into one mandatory context path.

Viable option 1:
- STANDARDISE dual-path contract across `get_last_match_xi`, `get_squad_comparison_data`, `analyze_squad_types`, `get_matchups`, `get_player_profile`.
- Define explicit expected behavior for no-injection path (`[]`, empty metrics, or constructor-data fallback) and encode this in ABC signatures/docstrings.

Viable option 2:
- REMOVE dual-path behavior for context-driven methods by requiring explicit injected DataFrames for execution paths that currently short-circuit or degrade without context.
- Keep only deterministic single-source behavior per method in ABC and engine.

KIP CANDIDATES
==============
NONE.

---

## 7. Verification

- [x] All 7 P02 flags have completed Step 3.1 entries.
- [x] All 5 DUAL_DATA_PATH flags from P03 have completed Step 3.2 entries.
- [x] ABC violations are in separate Step 3.3 block.
- [x] Step 3.5 includes explicit verdicts for ABC fixes and DUAL_DATA_PATH pattern.
- [x] ARCHITECT_DECISION_REQUIRED includes two explicit options.
- [x] Bouncer output matches P01 baseline.
