# Bug Fix: Batting Average Integrity (Non-Striker Run-Outs) (2026-02-06)

## 🚨 Problem Statement
The batting average calculation was erroneously assigning "Outs" to the player identified as the `striker` on any ball where a wicket fell.

### Root Cause
- In `player_engine.py` and `refinery_script.py`, the logic used `df.groupby('striker')['wicket_type'].count()`.
- If a **non-striker** was run out, the ball is still recorded under the `striker`'s name in the database.
- Result: The striker was charged with an "out" they didn't commit, and the non-striker (who actually got out) was given a "not out" credit.

## 🛠️ Implementation Fix
Switched the dismissal attribution from `striker` name to the explicit `player_dismissed` column.

### Logic Change
**New Logic (Batting):**
1. Runs/Balls are still grouped by `striker`.
2. **Dismissals** are now calculated by grouping the dataset by the `player_dismissed` column.
3. The two datasets are merged.

**New Logic (H2H Matchups):**
In `_display_batter_vs_bowlers`, the suppression logic now specifically checks:
```python
'player_dismissed': lambda x: (x == batter).sum()
```
This ensures a bowler only gets credit in the H2H table if they actually got THAT specific batter out.

## ✅ Verification
- Rebuilt the intelligence layer using `python utils/refinery_script.py`.
- Verified that the `KeyError: 'batting_team'` was resolved by aligning with the `team_bat_1/2` schema.
- Mathematical integrity confirmed: Batters are no longer penalized for their partner's run-outs.
