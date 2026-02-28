# Test Ideas Tracker

Purpose:
- Track important test ideas that are agreed but not yet implemented.
- Prevent critical regression checks from being forgotten.

## Pending

### 1) Regression: no-result first-innings must still count for batting-1 metrics

- Status: Pending
- Priority: High
- Added: 2026-02-19
- Owner: Team

Scope:
- Protect stats when a match has only innings 1 in source data (innings 2 missing or null).
- Example reference match: `1239536` (Sri Lanka vs England, 2021-07-04, no result, Sri Lanka 166 all out).

Why this matters:
- If this is mishandled, valid first-innings contributions are dropped from batting-1 averages.
- That causes visible user-facing discrepancies (`249 [11]` vs `257 [10]` type drift).

Proposed tests:
1. DAL normalization test
   - File target: `tests/test_data_access_integrity.py`
   - Assert `get_matches(match_ids=["1239536"])` returns:
     - `team_bat_2 == "England"`
     - `score_inn1 == 166`
     - `score_inn2 is null`
     - `balls_inn2 == 0`
     - `wickets_inn2 == 0`

2. Engine behavior regression test
   - File target: `formats/odi/tests/truth_bridge/global_h2h/test_runner.py` or dedicated pytest in `tests/`
   - Assert `analyze_global_h2h("Sri Lanka", "England", years_back=10)` includes:
     - `Average 1st Innings` for Sri Lanka as `249 [11]`
     - `Lowest 1st Innings` for Sri Lanka as `166`

3. Integrity guard test
   - File target: `tests/test_data_access_integrity.py`
   - Assert DataAccess integrity validator fails if innings-2 is missing while winner is not no-result/abandoned.

Acceptance criteria:
- All three tests pass in CI.
- Future refactors cannot drop valid innings-1 data from no-result interrupted matches.

## Implemented

- None yet.
