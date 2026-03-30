# SKILL: pre-task
# Agent: Codex
# When: Run at the start of every task, before any implementation
# Purpose: Establish clean baseline, write scope contract, load standards

---

## STEPS (run in order, do not skip)

### Step 0 — Resume from stash (if applicable)
If this task was previously BLOCKED and a stash exists from that invocation, pop it now:
```bash
git stash list | grep "TASK-XXX blocked partial"
```
If a matching stash entry exists → `git stash pop` before proceeding.
- If `git stash pop` succeeds → proceed normally. The prior partial work is restored.
- If `git stash pop` fails with conflicts → BLOCKED immediately. Do not proceed.
  Write BLOCKED report with blocker: "Stash pop conflict — prior blocked work cannot be
  cleanly restored. Conflicting files: [list from git status]. Human must resolve manually."
  Do NOT attempt to resolve the conflict. Do NOT drop the stash.
If no stash exists → proceed normally. This is a fresh start.

### Step 1 — Run baseline bouncer
```bash
python core/utils/compliance_bouncer.py --root .
```
Record violation count. If the command cannot run → BLOCKED immediately.
Write the count to `agents/workflow/pre_call_state.json`:
```json
{
  "baseline_violations": <N>,
  "last_commit": "<hash from git log --oneline -1>",
  "timestamp": "<ISO timestamp>"
}
```

### Step 2 — Write scope contract
Read `agents/workflow/taskFile.md`. Extract every file listed under FILES IN SCOPE.
Write `agents/workflow/scope.json`:
```json
{
  "task_id": "<TASK-XXX>",
  "allowed_files": ["path/to/file1", "path/to/file2"]
}
```
This file is read by the scope-guard pre-commit hook.
Do not proceed if taskFile.md is empty or missing FILES IN SCOPE.

### Step 3 — Load standards
Read every file listed under READ FIRST in the TASK PROMPT section of taskFile.md.
Do not skip any listed file. A missing standards file is not a blocker — note it and proceed.

### Step 4 — Classify task
Using the layer role table in MANDATES_1_TO_4.md, classify every file the task will touch.
This determines which gates trigger. Write classification to the pre_call_state.json:
```json
{
  "baseline_violations": <N>,
  "last_commit": "<hash>",
  "timestamp": "<ISO>",
  "layers_touched": ["calculator", "frontend", "manifest"],
  "gates_triggered": ["GATE1", "GATE-C", "GATE2", "GATE3", "GATE4", "GATE5S", "GATE5T", "GATEF1", "SRP-CHECK", "GATEF2", "GATEF3", "GATE5P", "GATE6"]
}
```

### Step 5 — Run pre-written assertion to capture red state (calculator/engine/service tasks only)
If the task touches `core/calculators/`, `core/services/`, or `formats/*/engines/`:
`agents/workflow/assertion.py` was written by Claude before this task was assigned.
Do NOT rewrite or modify it. It encodes the Verification Matrix — not your implementation plan.

Run it now, before writing any implementation code:
```bash
python agents/workflow/assertion.py
```
This will fail — the function does not exist yet. That is correct and required.
Capture the full terminal output. This is the RED STATE.
Save it — it must be embedded in the report as `assertion.pre_impl_output`.

If assertion.py does not exist → BLOCKED immediately. Do not implement.
If assertion.py runs and PASSES before any implementation → BLOCKED.
  A passing assertion before implementation means the assertion is testing nothing new.
  Report this as a blocker with context: "assertion passed pre-impl — possible stale function".

---

pre-task complete. Proceed to implementation.
