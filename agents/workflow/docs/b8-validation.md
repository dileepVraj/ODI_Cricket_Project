# B8 — Post-Call Validation

## Step 1 — Silent failure check
Read `agents/workflow/state.json` active.pre_call_commit. Compare against `git log --oneline -1`.
No new commit + no updated report → F1 (silent failure). Follow spec.md F1 protocol.

## Step 2 — Validate report
Read `agents/workflow/reports/TASK-XXX.json`.
Validate against `agents/workflow/report-schema.json`.
Schema invalid → treat as F1.

## Step 3 — Green signal check (ALL must be true)
- `status`: COMPLETE
- All triggered gates: `"status": "PASS"`
- `reviewer.verdict`: PASS
- `reviewer.assertion.match`: true (or null for non-calculator tasks)
- `reviewer.assertion.pre_impl_output`: non-empty and does NOT contain "ASSERTION PASSED"
  (for calculator/engine/service tasks — proves assertion was red before implementation)
- `taskfile_cleared`: true
- `commit` exists in `git log --oneline -5`
- `violations_delta` ≤ 0

Any condition false → identify failure mode from spec.md Section 2. Do not give green signal.

## Step 4 — Logic audit (Claude's primary QA responsibility)
The Reviewer subagent verified structure and coverage. Claude verifies correctness.
These are different jobs. Do both, in order.

For calculator / engine / service tasks:
  Read the Verification Matrix in taskFile.md (or the archived plan if taskFile is cleared).
  For EVERY row: trace the formula against the actual code.
  - Find the exact line(s) where this field is computed.
  - Confirm the formula in code matches the formula in the matrix.
  - Confirm the denominator, aggregation level, and empty-data result match.
  If any row cannot be confirmed: flag as logic mismatch. Do not give green signal.

For all tasks:
  Read every file in `files_modified`.
  For each AC: find the specific code that satisfies it and confirm the logic is correct,
  not just that the code exists (the Reviewer already checked existence).
  "The field is returned" is not enough — confirm it is computed correctly.

## Step 5 — Green signal
Update `agents/workflow/state.json`:
```json
{
  "last_completed_task": "TASK-XXX",
  "last_commit": "<commit hash>",
  "gate_baseline_violations": <post_task_violations>,
  "active": { "task_id": null, "phase": null, "agent": null, "invoked_at": null, "pre_call_commit": null, "retry_count": 0 },
  "next": "ready"
}
```
Inform human. Human /clears.
