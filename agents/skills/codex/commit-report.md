# SKILL: commit-report
# Agent: Codex
# When: After REVIEWER returns PASS verdict, before task is marked complete
# Purpose: Structured commit + JSON report that Claude reads programmatically

---

## STEPS

### Step 1 — Confirm Reviewer verdict
Read the REVIEWER subagent's JSON verdict.
If verdict is not "PASS" → do not commit. Fix the failures. Re-invoke REVIEWER.
If verdict is "PASS" → proceed.

### Step 2 — Run assertion one final time
```bash
python agents/workflow/assertion.py
```
Capture raw output. If ASSERTION FAILED → do not commit. Something changed after review.

### Step 3 — Run triggered gates
Run every gate listed in `pre_call_state.json` under `gates_triggered`.
Fix failures before proceeding. Do not skip.

Compare post-task bouncer violation count against `baseline_violations` in pre_call_state.json.
New violations introduced → FAIL. Fix before committing.

### Step 4 — Commit
```bash
git add <every file in scope.json allowed_files that was modified>
git commit -m "[TASK-XXX]: <one line description>"
```
Capture commit hash. If commit fails (hook rejection) → fix the hook violation, retry once.

### Step 5 — Delete assertion script
```bash
# Delete throwaway assertion — task complete
rm agents/workflow/assertion.py
```
If no assertion existed (frontend/infra task) → skip.

### Step 6 — Write JSON report
Write to `agents/workflow/reports/TASK-XXX.json` (NOT report.md — JSON only):
```json
{
  "task_id": "TASK-XXX",
  "date": "YYYY-MM-DD",
  "agent": "Codex",
  "status": "COMPLETE",
  "commit": "<real hash — not NONE>",
  "baseline_violations": <N>,
  "post_task_violations": <N>,
  "violations_delta": 0,
  "gates": [
    {"gate_id": "GATE1",  "triggered": false, "status": "SKIPPED",  "violations": []},
    {"gate_id": "GATE2",  "triggered": true,  "status": "PASS",     "violations": []},
    {"gate_id": "GATE3",  "triggered": true,  "status": "PASS",     "violations": []},
    {"gate_id": "GATE5",  "triggered": true,  "status": "PASS",     "violations": []},
    {"gate_id": "GATE6",  "triggered": true,  "status": "PASS",     "violations": []},
    {"gate_id": "GATEF1", "triggered": true,  "status": "PASS",     "violations": []},
    {"gate_id": "GATEF2", "triggered": true,  "status": "PASS",     "violations": []},
    {"gate_id": "GATEF3", "triggered": true,  "status": "PASS",     "violations": []}
  ],
  "reviewer_verdict": { <embed full REVIEWER JSON here> },
  "assertion_output": "<raw terminal output>",
  "files_modified": ["path/file1", "path/file2"],
  "scope_violations": [],
  "blockers_hit": [],
  "taskfile_cleared": true
}
```

### Step 7 — Clear workflow files
```bash
# Clear taskFile — task is done
echo "" > agents/workflow/taskFile.md
# Clear scope contract
rm agents/workflow/scope.json
# Clear pre-call state
rm agents/workflow/pre_call_state.json
```

### Step 8 — Print terminal summary
```
[TASK-XXX] STATUS: COMPLETE
Commit: <hash>
Reviewer: PASS
Report: agents/workflow/reports/TASK-XXX.json
```

---

## BLOCKED variant
If the task cannot complete (F4 — BLOCKED):
Write `agents/workflow/reports/TASK-XXX-blocked.json`:
```json
{
  "task_id": "TASK-XXX",
  "agent": "Codex",
  "status": "BLOCKED",
  "commit": null,
  "blocker": "<exact question — one sentence>",
  "blocker_context": "<what was tried, what was found>",
  "files_modified_so_far": []
}
```
Do NOT clear taskFile.md when BLOCKED — Claude needs it to resolve the question.
Do NOT clear scope.json or pre_call_state.json when BLOCKED.
Print: `[TASK-XXX] STATUS: BLOCKED — <one line>`
