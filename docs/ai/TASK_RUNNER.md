# TASK_RUNNER.md — Autonomous Task Execution Loop
# Location: docs/ai/TASK_RUNNER.md
# Version: 2.0
# Last Updated: 2026-03-14
# Purpose: Autonomous end-to-end task execution from workflow/taskFile.md input
#          to committed output with full doc updates, report.md write, and terminal summary.
#          This file is the entry point for all Codex task execution.
#
# HOW TO INVOKE:
#   "Read docs/ai/TASK_RUNNER.md and execute the task in workflow/taskFile.md"
#
# FAILURE BEHAVIOUR:
#   On any STOP condition — restore from snapshot (Phase 3), report BLOCKED.
#   Write BLOCKED report to workflow/report.md. Print status to terminal.
#   Never leave docs/ai/ files in a partial update state.

---

## PHASE 1 — INGEST TASK

### 1.1 Read workflow/taskFile.md
```bash
cat workflow/taskFile.md
```

Extract and record:
- Task description
- Task type (from TASK METADATA block)
- Scope (backend / frontend / both / tooling)
- Files in scope
- Acceptance criteria
- Constraints
- Full task prompt

If workflow/taskFile.md is missing or empty:
```
CRITICAL BLOCKER: workflow/taskFile.md missing or empty.
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
Then write BLOCKED report to `workflow/report.md` and print status to terminal.

---

## PHASE 4 — BOOTSTRAP

### 4.1 Load context-loader skill
```
Invoke: core/gen_ai/skills/guides/backend/context-loader/context-loader.md
```
Do not proceed until output shows: `CONTEXT LOADED — {scope} task`

### 4.2 Load scoped standards files

Load ONLY the files listed for the task scope. All paths are relative to `docs/guides/`.

**MANDATORY (every task):**
- `coreStandards/MANDATES_1_TO_4.md`
- `coreStandards/SYSTEM_TOPOLOGY.md`
- `coreStandards/HIGH_IMPACT_REGISTRY.md`
- `coreStandards/GATE_SEQUENCE.md`
- `coreStandards/SKILLS_REGISTRY.md`
- `coreStandards/WORKFLOW_AND_LAWS.md`

**FOR BACKEND TASKS (add to mandatory):**
- `backendStandards/PYTHON_STANDARDS.md`
- `backendStandards/MEMORY_AND_THREADING.md`

**FOR FRONTEND TASKS (add to mandatory):**
- `frontendStandards/TACTICAL_EXECUTION.md`
- `frontendStandards/UI_IMPLEMENTATION.md`
- `frontendStandards/PERF_RESILIENCE_A11Y_TESTING.md`

**CONDITIONAL (load only when task explicitly requires):**
- `backendStandards/KNOWN_PATTERNS_KIPS.md` → only when task touches `formats/odi/engines/team_engine.py`
- `coreStandards/MANDATES_5_6_LIVE.md` → only when task touches `core/live/` or `api/live/` [DORMANT]

### 4.3 Run baseline bouncer
```bash
python core/utils/compliance_bouncer.py --root .
```
Record output as **baseline**.
If FAIL: trigger rollback. Write BLOCKED report to `workflow/report.md`. Print status. Stop.

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

Execute the full task prompt from `workflow/taskFile.md`.

Follow the loaded guide skill checkpoints in sequence.
Follow all rules from CLAUDE.md Parts 2–8.
Follow all filesystem integrity rules (CLAUDE.md Part 5, Rules 1–7).

**During execution, enforce these invariants:**

- Run gate sequence as each file is modified (per TASK_PROTOCOL.md Section 3)
- On any gate FAIL: stop on that file — fix before continuing to next file
- On any CRITICAL DEVIATION: trigger rollback, write BLOCKED report, stop
- On any registered file touch without explicit instruction: trigger rollback, stop
- Never write to docs/ai/ during Phase 5 — that is Phase 7 only
- Never run banned git commands (CLAUDE.md Part 5, Rule 2)
- Scope all git status calls to task directory (CLAUDE.md Part 5, Rule 3)

**Verify acceptance criteria as you go:**
Check each acceptance criterion from `workflow/taskFile.md` as it is satisfied.
Record: "AC-{N}: SATISFIED / NOT YET SATISFIED"

---

## PHASE 6 — VERIFICATION

### 6.1 Acceptance criteria check
For each criterion in `workflow/taskFile.md`:
```
AC-1: {criterion text} — SATISFIED / FAILED
AC-2: {criterion text} — SATISFIED / FAILED
...
```
If any criterion is FAILED: trigger rollback. Write BLOCKED report. Stop.

### 6.2 Disk verify all modified files
For every source file modified in Phase 5:
```bash
wc -l {filepath}
grep -c "{key_marker}" {filepath}
```
If any verify fails: trigger rollback. Write BLOCKED report. Stop.

### 6.3 Post-task bouncer
```bash
python core/utils/compliance_bouncer.py --root .
```
Expected: PASS — matches or improves on baseline.
If FAIL: trigger rollback. Write BLOCKED report. Stop.

### 6.4 Run all triggered gates
Run every gate triggered by the files modified in Phase 5.
Gate trigger conditions per TASK_PROTOCOL.md Section 3.

Record each gate result:
```
GATE {N} ({name}): TRIGGERED — PASS / FAIL
```
If any gate FAIL: trigger rollback. Write BLOCKED report. Stop.

---

## PHASE 7 — POST-TASK DOC UPDATES

### 7.1 Update BACKLOG.md
Mark TASK-{ID} as CLOSED.

### 7.2 Update SESSION_STATE.md
Set Last Completed to TASK-{ID} and today's date.
Set Active Task back to None.

### 7.3 Update PROJECT_CONTEXT.md — Section 4 Rolling Window
In `docs/ai/PROJECT_CONTEXT.md`, update Section 4 (RECENT ARCHITECTURAL DECISIONS):
1. Prepend one new entry at position 1 describing the key architectural change made.
2. Renumber all entries (1–5).
3. **Delete any entry beyond position 5.** The list MUST contain exactly 5 items after this update.
   Format: `N. **TASK-XXX:** [one-line architectural decision summary]`

Verify:
```bash
grep -c "^\d\." docs/ai/PROJECT_CONTEXT.md
```
Expected: exactly 5 numbered entries in Section 4.

### 7.4 Commits
```bash
# Commit 1 — task work
git add [every source file modified in Phase 5]
git commit -m "TASK-XXX: [one line description]"

# Commit 2 — doc updates
git add docs/ai/BACKLOG.md docs/ai/SESSION_STATE.md docs/ai/PROJECT_CONTEXT.md
git commit -m "docs: TASK-XXX post-task doc updates"
```

Record both commit hashes. A task with Status: COMPLETE but NONE commits is invalid.

### 7.5 Clear workflow/taskFile.md
```bash
echo "" > workflow/taskFile.md
```
Verify:
```bash
cat workflow/taskFile.md
```
Expected: Empty or single blank line.

### 7.6 Write report to workflow/report.md
Overwrite `workflow/report.md` with the full task report using the format defined
in `workflow/taskFileTemplate.md` EXPECTED REPORT FORMAT section.

Both commit hashes MUST be real hashes — not NONE — before writing COMPLETE status.

### 7.7 Print terminal summary
After writing report.md, print to terminal:
```
TASK-{ID} [STATUS: COMPLETE / BLOCKED]
Report written to workflow/report.md
{One line: what was done, or why blocked}
```

Delete snapshots after successful completion:
```bash
rm docs/ai/BACKLOG.md.snap
rm docs/ai/SESSION_STATE.md.snap
rm docs/ai/PROJECT_CONTEXT.md.snap
```

---

## HARD STOPS — IMMEDIATE ROLLBACK + WRITE BLOCKED REPORT

These conditions trigger immediate rollback with no exception:

| Condition | Action |
|-----------|--------|
| SESSION_STATE.md shows active task at Phase 1 | Stop before Phase 2 — no rollback needed |
| workflow/taskFile.md missing or empty | Stop before Phase 2 — no rollback needed |
| Baseline bouncer FAIL | Rollback Phase 3 snapshot. Write BLOCKED report. |
| Any gate FAIL during execution | Rollback Phase 3 snapshot. Write BLOCKED report. |
| Post-task bouncer FAIL | Rollback Phase 3 snapshot. Write BLOCKED report. |
| CRITICAL DEVIATION (wrong file modified) | Rollback Phase 3 snapshot. Write BLOCKED report. |
| Registered file touched without instruction | Rollback Phase 3 snapshot. Write BLOCKED report. |
| Any acceptance criterion FAILED | Rollback Phase 3 snapshot. Write BLOCKED report. |
| docs/ai/ write outside Phase 7 steps | Rollback Phase 3 snapshot. Write BLOCKED report. |

---

## QUICK REFERENCE

```
TASK_RUNNER EXECUTION ORDER
════════════════════════════
Phase 1  → Read workflow/taskFile.md + SESSION_STATE.md
Phase 2  → Assign TASK-ID + write BACKLOG entry
Phase 3  → Snapshot docs (rollback safety)
Phase 4  → Bootstrap (context-loader + standards + baseline bouncer + TASK_PROTOCOL)
Phase 5  → Execute task (guide skill + gates)
Phase 6  → Verification (AC check + disk verify + post bouncer + gates)
Phase 7  → Doc updates + commits + write workflow/report.md + print terminal summary
```

---

*End of TASK_RUNNER.md*
*Version: 2.0*
*Last Updated: 2026-03-14*
*Invocation: "Read docs/ai/TASK_RUNNER.md and execute the task in workflow/taskFile.md"*
