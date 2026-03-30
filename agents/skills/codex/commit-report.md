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

### Step 3 — Compute violations delta
Gates already ran and passed in Phase 4. Do not re-run them.
Run compliance_bouncer only, to get the final post-task violation count:
```bash
python core/utils/compliance_bouncer.py --root .
```
Compare result against `baseline_violations` in pre_call_state.json.
If post-task count > baseline → FAIL. New violations were introduced. Fix before committing.

### Step 4 — Persist assertion as contract test
For calculator/engine/service tasks — move BEFORE committing:
```bash
# Derive module name from the import line in assertion.py
# e.g. "from core.calculators.team.win_rate import ..." → core_calculators_team_win_rate.py
mkdir -p tests/contracts
mv agents/workflow/assertion.py tests/contracts/<module_name>.py
```
How to derive the filename: read the `from <module> import` line in assertion.py.
Convert the module path to underscores: `core.calculators.team.win_rate` → `core_calculators_team_win_rate.py`.

If a contract file for this module already exists:
- New field added to module → append the new assert block to the existing file.
- Existing field contract changed intentionally → update the relevant assert block.
- Do NOT create a duplicate file. One file per module.

If no assertion existed (frontend/infra task) → skip this step.

### Step 5 — Commit
Stage all modified scope files AND the contract file (if applicable) together:
```bash
git add <every file in scope.json allowed_files that was modified>
git add tests/contracts/<module_name>.py   # if calculator/engine/service task
git commit -m "[TASK-XXX]: <one line description>"
```
Capture commit hash. If commit fails (hook rejection) → fix the hook violation, retry once.
Contract files are always permitted by the scope-guard (tests/contracts/* exemption).

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
    {"gate_id": "GATE1",     "triggered": false, "status": "SKIPPED",  "violations": []},
    {"gate_id": "GATE-C",    "triggered": false, "status": "SKIPPED",  "violations": []},
    {"gate_id": "GATE2",     "triggered": true,  "status": "PASS",     "violations": []},
    {"gate_id": "GATE3",     "triggered": true,  "status": "PASS",     "violations": []},
    {"gate_id": "GATE4",     "triggered": false, "status": "SKIPPED",  "violations": []},
    {"gate_id": "GATE5S",    "triggered": true,  "status": "PASS",     "violations": []},
    {"gate_id": "GATE5T",    "triggered": true,  "status": "PASS",     "violations": []},
    {"gate_id": "GATEF1",    "triggered": false, "status": "SKIPPED",  "violations": []},
    {"gate_id": "SRP-CHECK", "triggered": false, "status": "SKIPPED",  "violations": []},
    {"gate_id": "GATEF2",    "triggered": false, "status": "SKIPPED",  "violations": []},
    {"gate_id": "GATEF3",    "triggered": false, "status": "SKIPPED",  "violations": []},
    {"gate_id": "GATE5P",    "triggered": true,  "status": "PASS",     "violations": []},
    {"gate_id": "GATE6",     "triggered": true,  "status": "PASS",     "violations": []}
  ],
  "reviewer": {
    "verdict": "PASS",
    "acs": [
      {"id": "AC-1", "status": "SATISFIED", "reason": "<specific code that satisfies it>"},
      {"id": "AC-2", "status": "SATISFIED", "reason": "<specific code that satisfies it>"}
    ],
    "assertion": {
      "ran": true,
      "expected": "<value from matrix>",
      "actual": "<value from output>",
      "match": true,
      "pre_impl_output": "<raw terminal output from BEFORE implementation — must show failure>",
      "raw_output": "<raw terminal output from AFTER implementation — must show ASSERTION PASSED>"
    },
    "scope_clean": true,
    "out_of_scope_files": [],
    "issues": []
  },
  "acs": [
    {"id": "AC-1", "status": "SATISFIED", "reason": "<specific code>"},
    {"id": "AC-2", "status": "SATISFIED", "reason": "<specific code>"}
  ],
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

Stash any partial implementation changes to keep the working directory clean for the next invocation:
```bash
git stash push -m "TASK-XXX blocked partial — <one line blocker summary>"
```
This preserves the work without leaving dirty state. Claude may inspect the stash for context when resolving the blocker.

Print: `[TASK-XXX] STATUS: BLOCKED — <one line>`
