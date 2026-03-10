# POST_TASK_CHECKLIST.md — Agent-Executable
# Location: docs/ai/POST_TASK_CHECKLIST.md
# Version: 3.0
# Last Updated: 2026-03-10
# Purpose: Machine-executable checklist. Run in sequence after every task.
#          Every item has a concrete command or action. No ambiguity.
#          Called by TASK_RUNNER.md Phase 7. Do not skip items.

---

## PHASE 7 — POST-TASK DOC UPDATES

Execute every applicable section below in order.
Determine applicability from the task type and scope recorded in Phase 1.

---

### STEP 7.1 — ALWAYS: Close task in BACKLOG.md

**Trigger:** Every task.

Action: In `docs/ai/BACKLOG.md`, find the task entry created in Phase 2.
Update status line from:
```
Status: IN PROGRESS
```
to:
```
Status: CLOSED — {YYYY-MM-DD}
```

Verify:
```bash
grep -n "TASK-{ID}" docs/ai/BACKLOG.md
```
Expected: Status line shows CLOSED with today's date.
If not found: STOP — report BLOCKED. Do not continue.

---

### STEP 7.2 — ALWAYS: Update SESSION_STATE.md

**Trigger:** Every task.

Action: In `docs/ai/SESSION_STATE.md`:

1. Move task from **In Progress** to **Last Completed** block.
   Format:
   ```
   - TASK-{ID} — {one-line description} — CLOSED {YYYY-MM-DD}
     {2-3 line summary of what changed, what was fixed, gate results}
   ```

2. Update **Active Task** to `None.`

3. Update **Queue** — remove completed task, promote next task.

4. Update **Gate State Snapshot** if any gate result changed.

5. Update **Last Updated** date at top of file.

Verify:
```bash
grep -n "TASK-{ID}" docs/ai/SESSION_STATE.md
grep -n "Last Updated" docs/ai/SESSION_STATE.md
```
Expected: Task appears in Last Completed. Date is today.

---

### STEP 7.3 — ALWAYS: Update PROJECT_CONTEXT.md

**Trigger:** Every task that changes code, gates, or architecture.

Action: In `docs/ai/PROJECT_CONTEXT.md`, update **Section 10: Key Architectural Decisions**.
Add one row:

```
| {description of decision/change} | {what was decided} | {reason} | {YYYY-MM-DD} |
```

If task closed a sprint or phase — also update:
- Section 2: Current Project Phase
- Section 8: Pending Work

Verify:
```bash
grep -n "{TASK-ID or key term}" docs/ai/PROJECT_CONTEXT.md
```
Expected: New row present in Section 10.

---

### STEP 7.4 — IF GATE F1 CHANGED: Update Rule Inventory in SESSION_STATE.md

**Trigger:** Task added, removed, or modified a Gate F1 check.

Action: In `docs/ai/SESSION_STATE.md`, update the **Rule Inventory** table.
Add new row:
```
| {rule-id} | {function_name} | TASK-{ID} |
```

Verify:
```bash
grep -n "{function_name}" docs/ai/SESSION_STATE.md
```
Expected: New row present in Rule Inventory table.

---

### STEP 7.5 — IF NEW SKILL BUILT: Update PROJECT_CONTEXT.md + ENGINEERING_STANDARDS_CORE.md

**Trigger:** Task created a new skill SKILL.md under `core/gen_ai/skills/`.

Actions:
1. `docs/ai/PROJECT_CONTEXT.md` — Section 3.5: Skills Structure — add skill entry
2. `docs/guides/ENGINEERING_STANDARDS_CORE.md` — Skills registry — add skill row
3. `docs/ai/BACKLOG.md` — Close skill build task (Step 7.1 covers this)

Verify:
```bash
grep -n "{skill_name}" docs/ai/PROJECT_CONTEXT.md
grep -n "{skill_name}" docs/guides/ENGINEERING_STANDARDS_CORE.md
```
Expected: Skill present in both files.

---

### STEP 7.6 — IF STANDARDS FILE CHANGED: Propagate to scoped files

**Trigger:** Task modified `ENGINEERING_STANDARDS_CORE.md`.

Actions (in order):
1. Confirm change is in `ENGINEERING_STANDARDS_CORE.md` first
2. Propagate to `ENGINEERING_STANDARDS_BACKEND.md` if backend scope
3. Propagate to `ENGINEERING_STANDARDS_FRONTEND.md` if frontend scope
4. Update version number in affected files

Verify:
```bash
grep -n "Version" docs/guides/ENGINEERING_STANDARDS_BACKEND.md
grep -n "Version" docs/guides/ENGINEERING_STANDARDS_FRONTEND.md
```
Expected: Version updated in affected file(s).

---

### STEP 7.7 — IF KIP DOCUMENTED: Update all KIP registries

**Trigger:** Task documented a new Known Intentional Pattern (KIP).

Actions:
1. Inline comment added to source file above the pattern — confirm present
2. `docs/guides/ENGINEERING_STANDARDS_BACKEND.md` — Part 7: KIPs — add entry
3. `AGENTS.md` — Part 8: Hard Prohibitions — add prohibition
4. `GEMINI.md` — Part 8: Hard Prohibitions — add prohibition

Verify:
```bash
grep -n "KIP-" docs/guides/ENGINEERING_STANDARDS_BACKEND.md
grep -n "KIP-" AGENTS.md
```
Expected: New KIP present in both files.

---

### STEP 7.8 — IF PHASE CHANGED: Update phase fields

**Trigger:** Task completed a phase transition.

Actions:
1. `docs/ai/SESSION_STATE.md` — Current Phase field — update
2. `docs/ai/PROJECT_CONTEXT.md` — Section 2: Current Project Phase — update
3. `docs/ai/PROJECT_CONTEXT.md` — Section 8: Pending Work — update

Verify:
```bash
grep -n "Current Phase" docs/ai/SESSION_STATE.md
grep -n "Current Phase" docs/ai/PROJECT_CONTEXT.md
```
Expected: Both files show updated phase.

---

### STEP 7.9 — IF NEW ENGINE AUDITED: Create audit directory and update docs

**Trigger:** Task completed a full engine audit.

Actions:
1. Confirm `docs/audits/{engine}/` directory exists with AUDIT-01 through AUDIT-05
2. `docs/ai/SESSION_STATE.md` — Last Completed — add engine sign-off entry
3. `docs/ai/PROJECT_CONTEXT.md` — Section 10 — log engine sign-off

Verify:
```bash
ls docs/audits/{engine}/
```
Expected: All 5 audit files present.

---

### STEP 7.10 — ALWAYS: Disk verify all modified docs

**Trigger:** Every task — after all doc updates above.

For every file modified in Steps 7.1–7.9, run:
```bash
wc -l {filepath}
grep -c "{key_marker}" {filepath}
```

Expected: Non-zero line count. Key markers present.
If any verify fails: STOP — report BLOCKED.

---

### STEP 7.11 — ALWAYS: Final bouncer

**Trigger:** Every task — after all doc updates.

```bash
python core/utils/compliance_bouncer.py --root .
```

Expected: PASS — 0 violations — matches baseline.
If FAIL: STOP — do not commit — report BLOCKED with exact output.

---

### STEP 7.12 — ALWAYS: Two-commit sequence

**Trigger:** Every task — after bouncer PASS.

**Commit 1 — Task work:**
```bash
git add {all task source files}
git commit -m "TASK-{ID}: {one-line description}"
```

**Commit 2 — Doc updates:**
```bash
git add docs/ai/BACKLOG.md docs/ai/SESSION_STATE.md docs/ai/PROJECT_CONTEXT.md
git add {any other docs modified in Steps 7.1–7.9}
git commit -m "docs: TASK-{ID} post-task doc updates"
```

Verify both commits landed:
```bash
git log --oneline -3
```
Expected: Two new commits visible. No `--no-verify` used.

---

### STEP 7.13 — ALWAYS: Produce task report

**Trigger:** Every task — final step.

Produce report in the exact format defined in CLAUDE.md Part 7.
Add to report:

```
Doc Updates:
- BACKLOG.md: CLOSED TASK-{ID} — YES/NO
- SESSION_STATE.md: Last Completed updated — YES/NO
- PROJECT_CONTEXT.md: Section 10 updated — YES/NO
- Additional docs updated: {list or NONE}
Commit 1 (task work): {hash}
Commit 2 (doc updates): {hash}
```

A task is NOT complete until this report is produced with both commit hashes.

---

## NEVER DO (hard prohibitions — agent)

- Do not run `git commit --no-verify`
- Do not skip Step 7.11 (final bouncer)
- Do not skip Step 7.12 (two-commit sequence)
- Do not modify any file in `docs/ai/` beyond what is explicitly listed
  in Steps 7.1–7.9 for the current task type
- Do not update `docs/ai/AI_MEMORY.md` — it is deprecated
- Do not mark task COMPLETE without producing Step 7.13 report

---

*End of POST_TASK_CHECKLIST.md*
*Version: 3.0*
*Last Updated: 2026-03-10*
*Maintained by: TASK_RUNNER.md (agent-executable) + Human Architect*
