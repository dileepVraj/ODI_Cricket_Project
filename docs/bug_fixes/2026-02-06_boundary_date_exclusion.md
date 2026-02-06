# Bug Fix: Boundary Date Exclusion (2026-02-06)

## 🚨 Problem Statement
Analysis functions using `pd.Timestamp.now() - pd.DateOffset(years=X)` for lookback filtering were inconsistently excluding matches that occurred exactly on the boundary date (e.g., exactly 10 years ago today).

### Root Cause
- `pd.Timestamp.now()` includes a high-precision time component (e.g., `2026-02-06 10:21:49`).
- Most cricket data is recorded at "zero time" (`2016-02-06 00:00:00`).
- Because `2016-02-06 00:00:00` is mathematically **less than** `2016-02-06 10:21:49`, the match was erroneously categorized as being "older" than the lookup window and filtered out.

## 🛠️ Implementation Fix
The fix involved normalizing the "Current Time" to daily precision (midnight) before calculating the lookback cutoff.

### Logic Change
**Old Logic:**
```python
cutoff = pd.Timestamp.now() - pd.DateOffset(years=10)
# Result: 2016-02-06 10:21:49 -> 00:00 match is EXCLUDED
```

**New Logic:**
```python
cutoff = pd.Timestamp.now().floor('D') - pd.DateOffset(years=10)
# Result: 2016-02-06 00:00:00 -> 00:00 match is INCLUDED
```

### Affected Files
1.  `core/team_engine.py`: Updated 9 analysis methods.
2.  `core/player_engine.py`: Updated 9 instances (milestones/aggregations).
3.  `core/predictor.py`: Updated score prediction window logic.

## ✅ Verification
- **Targeted Test**: `tests/odi/verify_boundary_fix.py` confirmed that Feb 6, 2016 matches are now included when run on Feb 6, 2026.
- **Regression Suite**: Ran `run_continent_regression.py`. Mismatches detected for 4 regions (Asia, Africa, Oceania) were manually verified as the "Hidden" matches being correctly recovered. Updated Golden Master to reflect the new accurate counts.
