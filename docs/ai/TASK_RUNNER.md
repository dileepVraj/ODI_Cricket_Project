# TASK_RUNNER.md — Autonomous Task Execution Loop
# Location: docs/ai/TASK_RUNNER.md
# Version: 1.0
# Last Updated: 2026-03-10
# Purpose: Autonomous end-to-end task execution from taskFile.md input
#          to committed output with full doc updates and task report.
#          This file is the entry point for all agent task execution.
#
# HOW TO INVOKE:
#   "Read docs/ai/TASK_RUNNER.md and execute the task in taskFile.md"
#
# FAILURE BEHAVIOUR:
#   On any STOP condition — restore from snapshot (Phase 3), report BLOCKED.
#   Never leave docs/ai/ files in a partial update state.

---

## PHASE 1 — INGEST TASK

### 1.1 Read taskFile.md
```bash
cat taskFile.md
```

Extract and record:
- Task description
- Task type (from TASK METADATA block)
- Scope (backend / frontend / both / tooling)
- Files in scope
- Acceptance criteria
- Constraints
- Full task prompt

If taskFile.md is missing or empty:
```
CRITICAL BLOCKER: taskFile.md missing or empty.
Cannot begin execution. Halting.
```
Stop. Do not proceed.

### 1.2 Read SESSION_STATE.md
```bash
cat docs/ai/SESSION_STATE.md
```

Extract:
- Current phase
- Active task (must be None — if not, stop and report conflict)
- Queue (confirm task is not already in progress)
- Pre-task dirty file notice
- Gate state snapshot

If SESSION_STATE.md is missing:
```
CRITICAL BLOCKER: docs/ai/SESSION_STATE.md missing.
Halting.
```
Stop. Do not proceed.

### 1.3 Confirm no active task conflict
If SESSION_STATE.md shows an active task that is NOT None:
```
CONFLICT DETECTED: SESSION_STATE.md shows active task {task}.
Cannot begin new task until active task is resolved.
Halting. Architect review required.
```
Stop. Do not proceed.

---

## PHASE 2 — ASSIGN TASK ID AND CREATE BACKLOG ENTRY

### 2.1 Scan BACKLOG.md for highest task ID
```bash
grep -o "TASK-[0-9]*" docs/ai/BACKLOG.md | sort -t- -k2 -n | tail -1
```

Record result as `{LAST_ID}`.
New task ID = `{LAST_ID + 1}` formatted as `TASK-{NNN}` (zero-padded to 3 digits).

Example: If last ID is TASK-089, new ID is TASK-090.

### 2.2 Write BACKLOG entry
Add the following block to `docs/ai/BACKLOG.md` under the appropriate
priority section (High / Medium / Low from taskFile.md metadata):

```markdown
## TASK-{ID} — {one-line description from task description}

**Type:** {task type}
**Scope:** {scope}
**Priority:** {priority}
**Depends On:** {depends on or NONE}
**Created:** {YYYY-MM-DD}
**Status:** IN PROGRESS

### Description
{task description from taskFile.md}

### Acceptance Criteria
{acceptance criteria from taskFile.md}

### Files In Scope
{files in scope from taskFile.md}
```

Verify write:
```bash
grep -n "TASK-{ID}" docs/ai/BACKLOG.md
```
Expected: Entry present with Status: IN PROGRESS.

### 2.3 Update SESSION_STATE.md — Active Task
In `docs/ai/SESSION_STATE.md`, update:
```
## Active Task
TASK-{ID} — {one-line description} — IN PROGRESS
```

Verify:
```bash
grep -n "Active Task" docs/ai/SESSION_STATE.md
```
Expected: Shows TASK-{ID} as active.

---

## PHASE 3 — SNAPSHOT (ROLLBACK SAFETY)

Before touching any source file, snapshot the current state of all docs:

```bash
cp docs/ai/BACKLOG.md docs/ai/BACKLOG.md.snap
cp docs/ai/SESSION_STATE.md docs/ai/SESSION_STATE.md.snap
cp docs/ai/PROJECT_CONTEXT.md docs/ai/PROJECT_CONTEXT.md.snap
```

Record: "Snapshot taken — rollback available if task fails."

**Rollback trigger conditions:**
- Any gate FAIL that cannot be fixed within task scope
- Bouncer FAIL post-task
- Any CRITICAL DEVIATION from filesystem integrity rules
- Agent cannot complete acceptance criteria

**Rollback procedure:**
```bash
cp docs/ai/BACKLOG.md.snap docs/ai/BACKLOG.md
cp docs/ai/SESSION_STATE.md.snap docs/ai/SESSION_STATE.md
cp docs/ai/PROJECT_CONTEXT.md.snap docs/ai/PROJECT_CONTEXT.md
rm docs/ai/*.snap
```
Then report BLOCKED with exact failure reason.

---

## PHASE 4 — BOOTSTRAP (standard CLAUDE.md sequence)

### 4.1 Load context-loader skill
```
Invoke: core/gen_ai/skills/guides/backend/context-loader/context-loader.md
```
Do not proceed until output shows: `CONTEXT LOADED — {scope} task`

### 4.2 Load scoped standards file
- Backend scope → read `docs/guides/ENGINEERING_STANDARDS_BACKEND.md` in full
- Frontend scope → read `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md` in full
- Both → read both in full

### 4.3 Run baseline bouncer
```bash
python core/utils/compliance_bouncer.py --root .
```
Record output as **baseline**.
If FAIL: trigger rollback. Report BLOCKED. Stop.

### 4.4 Load TASK_PROTOCOL.md
```bash
cat docs/ai/TASK_PROTOCOL.md
```
Classify task type from Section 1.
Determine guide skill load order from Section 2.
Determine gate sequence from Section 3.

### 4.5 Load guide skill
Load the guide skill identified in Step 4.4.
Do not begin task execution until guide skill is loaded.

---

## PHASE 5 — EXECUTE TASK

Execute the full task prompt from taskFile.md.

Follow the loaded guide skill checkpoints in sequence.
Follow all rules from CLAUDE.md Parts 2–5.
Follow all filesystem integrity rules (CLAUDE.md Part 5, Rules 1–7).

**During execution, enforce these invariants:**

- Run gate sequence as each file is modified (per TASK_PROTOCOL.md Section 3)
- On any gate FAIL: stop on that file — fix before continuing to next file
- On any CRITICAL DEVIATION: trigger rollback, report BLOCKED, stop
- On any registered file touch without explicit instruction: trigger rollback, stop
- Never write to docs/ai/ during Phase 5 — that is Phase 7 only
- Never run banned git commands (CLAUDE.md Part 5, Rule 2)
- Scope all git status calls to task directory (CLAUDE.md Part 5, Rule 3)

**Verify acceptance criteria as you go:**
Check each acceptance criterion from taskFile.md as it is satisfied.
Record: "AC-{N}: SATISFIED / NOT YET SATISFIED"

---

## PHASE 6 — VERIFICATION

### 6.1 Acceptance criteria check
For each criterion in taskFile.md:
```
AC-1: {criterion text} — SATISFIED / FAILED
AC-2: {criterion text} — SATISFIED / FAILED
...
```
If any criterion is FAILED: trigger rollback. Report BLOCKED. Stop.

### 6.2 Disk verify all modified files
For every source file modified in Phase 5:
```bash
wc -l {filepath}
grep -c "{key_marker}" {filepath}
```
If any verify fails: trigger rollback. Report BLOCKED. Stop.

### 6.3 Post-task bouncer
```bash
python core/utils/compliance_bouncer.py --root .
```
Expected: PASS — matches or improves on baseline.
If FAIL: trigger rollback. Report BLOCKED. Stop.

### 6.4 Run all triggered gates
Run every gate triggered by the files modified in Phase 5.
Gate trigger conditions per TASK_PROTOCOL.md Section 3.

Record each gate result:
```
GATE {N} ({name}): TRIGGERED — PASS / FAIL
```
If any gate FAIL: trigger rollback. Report BLOCKED. Stop.

---

## PHASE 7 — POST-TASK DOC UPDATES

Execute `docs/ai/POST_TASK_CHECKLIST.md` in full.

Steps 7.1 through 7.13 in order.
Determine applicable steps from task type and scope.
Steps 7.1, 7.2, 7.3, 7.10, 7.11, 7.12, 7.13 are ALWAYS required.

On completion of Step 7.12 (two-commit sequence):
```bash
rm docs/ai/BACKLOG.md.snap
rm docs/ai/SESSION_STATE.md.snap
rm docs/ai/PROJECT_CONTEXT.md.snap
```
Snapshots are deleted only after successful commit. Never before.

**Clear taskFile.md:**
```bash
echo "" > taskFile.md
```
Verify:
```bash
cat taskFile.md
```
Expected: Empty or single blank line.

---

## PHASE 8 — TASK REPORT

Produce report in CLAUDE.md Part 7 format.

Append the following doc update block to the standard report:

```
Doc Updates:
- BACKLOG.md        : TASK-{ID} CLOSED — YES/NO
- SESSION_STATE.md  : Last Completed updated — YES/NO
- PROJECT_CONTEXT.md: Section 10 updated — YES/NO
- Additional docs   : {list or NONE}

Acceptance Criteria:
- AC-1: {text} — SATISFIED/FAILED
- AC-2: {text} — SATISFIED/FAILED

Rollback Used: YES/NO
Snapshots Cleaned: YES/NO

Commit 1 (task work)  : {hash}
Commit 2 (doc updates): {hash}
```

---

## HARD STOPS — IMMEDIATE ROLLBACK + REPORT BLOCKED

These conditions trigger immediate rollback with no exception:

| Condition | Action |
|-----------|--------|
| SESSION_STATE.md shows active task at Phase 1 | Stop before Phase 2 — no rollback needed |
| taskFile.md missing or empty | Stop before Phase 2 — no rollback needed |
| Baseline bouncer FAIL | Rollback Phase 3 snapshot. Report BLOCKED. |
| Any gate FAIL during execution | Rollback Phase 3 snapshot. Report BLOCKED. |
| Post-task bouncer FAIL | Rollback Phase 3 snapshot. Report BLOCKED. |
| CRITICAL DEVIATION (wrong file modified) | Rollback Phase 3 snapshot. Report BLOCKED. |
| Registered file touched without instruction | Rollback Phase 3 snapshot. Report BLOCKED. |
| Any acceptance criterion FAILED | Rollback Phase 3 snapshot. Report BLOCKED. |
| docs/ai/ write outside POST_TASK_CHECKLIST steps | Rollback Phase 3 snapshot. Report BLOCKED. |

---

## QUICK REFERENCE

```
TASK_RUNNER EXECUTION ORDER
════════════════════════════
Phase 1  → Read taskFile.md + SESSION_STATE.md
Phase 2  → Assign TASK-ID + write BACKLOG entry
Phase 3  → Snapshot docs (rollback safety)
Phase 4  → Bootstrap (context-loader + standards + baseline bouncer + TASK_PROTOCOL)
Phase 5  → Execute task (guide skill + gates)
Phase 6  → Verification (AC check + disk verify + post bouncer + gates)
Phase 7  → POST_TASK_CHECKLIST (Steps 7.1–7.13)
Phase 8  → Task report
```

---

*End of TASK_RUNNER.md*
*Version: 1.0*
*Last Updated: 2026-03-10*
*Invocation: "Read docs/ai/TASK_RUNNER.md and execute the task in taskFile.md"*
