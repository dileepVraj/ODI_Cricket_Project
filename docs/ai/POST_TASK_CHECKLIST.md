# POST-TASK UPDATE CHECKLIST
**Purpose:** Files that MUST be updated
after every completed task or significant
progress. Human architect responsibility.
**Location:** docs/ai/POST_TASK_CHECKLIST.md
**Last Updated:** 2026-03-05

---

## ALWAYS UPDATE (every task)

- [ ] `docs/ai/SESSION_STATE.md`
      — Last Completed, In Progress,
        Active Task, Known Blockers

- [ ] `docs/ai/BACKLOG.md`
      — Task status, subtask checkboxes,
        close completed tasks

---

## UPDATE WHEN PHASE CHANGES

- [ ] `docs/ai/SESSION_STATE.md`
      — Current Phase field

- [ ] `docs/ai/PROJECT_CONTEXT.md`
      — Section 2: Current Project Phase

- [ ] `docs/ai/PROJECT_CONTEXT.md`
      — Section 8: Pending Work

---

## UPDATE WHEN TASK CLOSES

- [ ] `docs/ai/BACKLOG.md`
      — Status: Closed — YYYY-MM-DD

- [ ] `docs/ai/PROJECT_CONTEXT.md`
      — Section 10: Key Architectural
        Decisions — add decision row

---

## UPDATE WHEN ARCHITECT DECISION MADE

- [ ] `docs/ai/PROJECT_CONTEXT.md`
      — Section 10: Key Architectural
        Decisions — add decision row

- [ ] `docs/audits/[engine]/
        audit_05_final_report.md`
      — Section 7: Architect Decisions Log
        (audit tasks only)

---

## UPDATE WHEN VIOLATION FOUND AND FIXED

- [ ] `docs/audits/[engine]/
        audit_05_final_report.md`
      — Section 8: Refactor Readiness
        — mark resolved

- [ ] `docs/ai/BACKLOG.md`
      — Close refactor task

- [ ] `docs/ai/PROJECT_CONTEXT.md`
      — Section 10: log the fix

---

## UPDATE WHEN FALSE POSITIVE DOCUMENTED

- [ ] `docs/audits/[engine]/
        audit_05_final_report.md`
      — Section 4.3: False Positives

- [ ] `docs/ai/PROJECT_CONTEXT.md`
      — Section 10: log the decision

---

## UPDATE WHEN INTENTIONAL PATTERN (KIP)
## DOCUMENTED

- [ ] Inline comment added to source file
      — above the pattern

- [ ] `docs/guides/
        ENGINEERING_STANDARDS_BACKEND.md`
      — Part 7: Known Intentional Patterns

- [ ] `AGENTS.md`
      — Part 8: Hard Prohibitions

- [ ] `GEMINI.md`
      — Part 8: Hard Prohibitions

- [ ] `docs/audits/[engine]/
        audit_05_final_report.md`
      — Section 10: Architect Observations

---

## UPDATE WHEN NEW ENGINE AUDITED

- [ ] Create `docs/audits/[engine]/`
      directory

- [ ] Run AUDIT-01 through AUDIT-05
      — all outputs saved to that directory

- [ ] `docs/ai/BACKLOG.md`
      — TASK-010 subtasks updated

- [ ] `docs/ai/SESSION_STATE.md`
      — Last Completed updated

- [ ] `docs/ai/PROJECT_CONTEXT.md`
      — Section 10: log engine sign-off

---

## UPDATE WHEN NEW SKILL BUILT

- [ ] `docs/ai/PROJECT_CONTEXT.md`
      — Section 3.5: Skills Structure

- [ ] `docs/guides/
        ENGINEERING_STANDARDS_CORE.md`
      — Skills registry

- [ ] `docs/ai/BACKLOG.md`
      — Close skill build task

---

## UPDATE WHEN STANDARDS FILE CHANGES

- [ ] `docs/guides/
        ENGINEERING_STANDARDS_CORE.md`
      — Authoritative source — update first

- [ ] Propagate to affected scoped file:
      `ENGINEERING_STANDARDS_BACKEND.md`
      OR
      `ENGINEERING_STANDARDS_FRONTEND.md`

- [ ] `docs/ai/PROJECT_CONTEXT.md`
      — Section 3.1: Standards File
        Structure — update version

---

## NEVER UPDATE (agent-prohibited files)

These files are human-write-only.
Agents must never touch them.

- `docs/ai/SESSION_STATE.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/ai/BACKLOG.md`
- `docs/ai/POST_TASK_CHECKLIST.md`

---

*End of POST_TASK_CHECKLIST.md*
*Last Updated: 2026-03-05*
*Maintained by: Human Architect only*