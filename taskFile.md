# TASK FILE
# =========
# Location: C:\Cricket_Project_Stable\taskFile.md

---

## TASK METADATA
```
Task ID       : AUTO — assigned by agent from BACKLOG.md highest ID + 1
Task Type     : bug-fix
Scope         : backend
Priority      : High
Phase 12 Risk : NO
Depends On    : NONE
```

---

## TASK DESCRIPTION
```
The Venue Matchup function (Venue Intelligence section) is returning null/None
for two metrics: "High / Low" score in the Batting First block, and "Highest
Chased" in the Chasing block. Both fields render as "-" in the frontend despite
valid match data existing for the queried combination. All other metrics in the
same function return correct values. The reference (ipywidgets) app returns
correct values for the same inputs. Agent must diagnose the root cause
independently, fix it, and confirm no regression on surrounding metrics.
```

---

## FILES IN SCOPE
```
Identify exact paths via filesystem inspection at task start:

- formats/odi/engines/venue_engine.py  (or equivalent venue matchup engine)
- core/calculators/<venue_calculator>.py  (whichever calculator computes
  high_score, low_score, highest_chased — follow the call chain)

READ ONLY — do not modify without stop-state-trace-confirm:
- core/data_access.py

READ ONLY — do not modify in this task:
- core/interfaces/team_types.py
- api/serializers.py
- formats/odi/manifest.py

Agent must NOT touch any file not listed above.
```

---

## ACCEPTANCE CRITERIA
```
AC-1: "High / Low" in the Batting First block returns correct max and min
      innings scores for a valid team/venue/years query.

AC-2: "Highest Chased" in the Chasing block returns the correct max
      successfully chased score for the queried team at the queried venue.

AC-3: All other Venue Matchup metrics that were returning correct values
      before this fix continue to return identical values (no regression).

AC-4: Fix uses vectorized Pandas/NumPy operations only — no row-level
      iteration introduced.

AC-5: All modified functions retain complete type annotations.

AC-6: Post-task bouncer output matches or improves on baseline.
```

---

## CONSTRAINTS
```
- Do NOT modify core/data_access.py without a stop-state-trace-confirm sequence.
- Do NOT modify core/interfaces/team_types.py or api/serializers.py — out of
  scope for this task.
- No hardcoded team names, venue names, or score thresholds in engine or
  calculator logic.
- No Phase 12 references of any kind.
- Assume dirty data on all column accesses — check column existence before use.
- Empty subsets must return None explicitly — never 0, never NaN.
- Do NOT modify or remove the constructor discard pattern
  `_ = (match_df, phase_df, dal)` in formats/odi/engines/team_engine.py line 26.
- Do NOT add a duplicate definition of `_context_match_df` to team_engine.py.
```

---

## TASK PROMPT
```
READ FIRST
----------
1. Read CLAUDE.md (AGENTS.md) in full.
2. Read docs/guides/ENGINEERING_STANDARDS_BACKEND.md in full.
3. Read docs/ai/SESSION_STATE.md — extract current phase, scope, and blockers.
4. Invoke core/gen_ai/skills/guides/backend/context-loader/context-loader.md
   and confirm: CONTEXT LOADED — backend task.

BASELINE BOUNCER
----------------
Run: python core/utils/compliance_bouncer.py --root .
Record full output as your before-snapshot. Hard stop if this cannot be run.

TASK STEPS
----------
Step 1 — Locate the venue matchup engine and follow the call chain to the
         calculator(s) responsible for computing high_score, low_score, and
         highest_chased. Read every file in the chain before writing any code.

Step 2 — Diagnose the root cause independently. Trace the full filter and
         aggregation logic for the two failing fields. State your diagnosis
         clearly before making any code change.

Step 3 — Apply the fix. Change only what is necessary to resolve the bug.
         Do not refactor surrounding logic unless it is directly causing the
         failure.

Step 4 — Verify AC-1 through AC-6 one by one before submitting the report.

VERIFICATION
------------
Check each AC individually. Mark SATISFIED or FAILED. Do not mark the task
COMPLETE if any AC is FAILED — stop and report the blocker instead.

CONSTRAINTS
-----------
- core/data_access.py: READ ONLY unless impact trace produced and confirmed.
- core/interfaces/team_types.py: READ ONLY — no modification permitted.
- api/serializers.py: READ ONLY — no modification permitted.
- No Phase 12 references.
- No hardcoded names or thresholds.
- No .iterrows() or .itertuples().
- No Dict[str, Any] in any type signature.
- Do NOT modify or remove `_ = (match_df, phase_df, dal)` in team_engine.py line 26.
- Do NOT add a duplicate `_context_match_df` definition to team_engine.py.
```

---

## EXPECTED REPORT FORMAT

Agent must produce this exact report on task completion or block.
No prose summaries. No alternative layouts. No omissions.
```
TASK REPORT
===========
Task: [one-line description]
Date: [YYYY-MM-DD]
Agent: [Claude / Gemini / Codex]

Baseline Bouncer: [PASS/FAIL — N violations]
Post-Task Bouncer: [PASS/FAIL — N violations — matches baseline: YES/NO]

Gates Triggered:
- GATE 1 (boundary-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 2 (duckdb-lint-ops): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 3 (manifest-contract-verifier): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 4 (serialization-guard): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE F1 (frontend-lint-sentinel): SKIPPED — frontend scope only
- GATE F2 (frontend-paradigm-sentinel): SKIPPED — frontend scope only
- GATE F3 (frontend-type-sync-guard): SKIPPED — frontend scope only
- GATE 5 (paradigm-sentinel): TRIGGERED — [PASS/FAIL]
- GATE 6 (compliance_bouncer): TRIGGERED — [PASS/FAIL]

Root Cause: [one line — agent's own diagnosis]
Files Modified: [list]
Registered Files Touched: [list or NONE]
Stop-State-Trace-Confirm Used: [YES/NO — which file]
Blockers Hit: [list or NONE]
Phase 12 References Added: [YES — VIOLATION / NO — confirmed]
AI_MEMORY.md Updated: [NO — confirmed]

Acceptance Criteria:
- AC-1: High/Low score returns correct values — SATISFIED/FAILED
- AC-2: Highest Chased returns correct values — SATISFIED/FAILED
- AC-3: No regression on other Venue Matchup metrics — SATISFIED/FAILED
- AC-4: Vectorized operations only — SATISFIED/FAILED
- AC-5: Type annotations complete on modified functions — SATISFIED/FAILED
- AC-6: Post-task bouncer matches baseline — SATISFIED/FAILED

Doc Updates:
- BACKLOG.md        : TASK-{ID} CLOSED — YES/NO
- SESSION_STATE.md  : Last Completed updated — YES/NO
- PROJECT_CONTEXT.md: Section 10 updated — YES/NO
- Additional docs   : [list or NONE]

Disk Verify:
- [filepath]: [line count] lines — key markers present YES/NO

Rollback Used: YES/NO
taskFile.md Cleared: YES/NO

Commit 1 (task work)  : [hash]
Commit 2 (doc updates): [hash]

Status: [COMPLETE / BLOCKED — reason]
```

*Do not commit taskFile.md to git. Add to .gitignore if not already present.*