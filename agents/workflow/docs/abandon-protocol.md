# Abandon Protocol

**Triggered by:** explicit human command only — e.g. "abandon TASK-168", "drop this task", "cancel it".
Never triggered by Claude's own judgment.

## Steps

1. Read current `agents/workflow/state.json` active block.
2. Write updated state.json:
   - Append to `abandoned_tasks` array:
     ```json
     { "task_id": "TASK-XXX", "abandoned_at": "<ISO timestamp>", "reason": "<human's stated reason or 'no reason given'>" }
     ```
   - Null out active:
     ```json
     "active": { "task_id": null, "phase": null, "agent": null, "invoked_at": null, "pre_call_commit": null, "retry_count": 0 }
     ```
   - Set `"next": "ready"`
3. Inform human: "TASK-XXX recorded as abandoned. Lock released."
4. Proceed to B2 for next request.

**Note:** Abandon is a resolution, not an erasure. The task_id and reason are preserved in
`abandoned_tasks` so the audit trail survives. A task abandoned twice with the same root cause
is a signal the spec needs fixing, not just retrying.
