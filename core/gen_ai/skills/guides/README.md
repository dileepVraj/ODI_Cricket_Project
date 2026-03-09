# Guide Skills

Guide skills instruct the agent how to
perform a task correctly. They define
best practices, command patterns, and
execution sequences for specific operations.

## Skills
- duckdb-lint-ops � DuckDB query execution
  and DOD anti-pattern linting

---

## Frontend Guides

Frontend guide skills provide structured
checkpoint workflows for frontend tasks.
They enforce ENGINEERING_STANDARDS_FRONTEND.md
compliance, run the frontend gate sequence
(GATE F1, F2, F3, 5, 6), and produce
frontend-specific task reports.

### Skills

- frontend-bug-fix-guide — structured RCA
  trace, mandate checks, and gate sequence
  for diagnosing and fixing bugs in the
  Next.js frontend.
  Triggers: any frontend/ bug-fix task.
  Path: core/gen_ai/skills/guides/frontend/
        frontend-bug-fix-guide/SKILL.md
  Pass: all gates F1, F2, (F3 if types
        modified), 5, and 6 green.
  Fail: one or more gates report violations.

- frontend-modification-guide — delta
  discipline workflow for modifying existing
  components, styles, layouts, or API
  integration. Enforces CSS token compliance,
  manifest-driven rendering, and SRP.
  Triggers: any modification to frontend/
  files.
  Path: core/gen_ai/skills/guides/frontend/
        frontend-modification-guide/SKILL.md
  Pass: all gates F1, F2, (F3 if types
        modified), 5, and 6 green.
  Fail: one or more gates report violations.

- frontend-new-component-guide — component
  classification, directory placement,
  renderer lazy-loading checks, accessibility
  mandate, and TypeScript strict compliance
  for new React components.
  Triggers: creation of any new .tsx file
  under frontend/.
  Path: core/gen_ai/skills/guides/frontend/
        frontend-new-component-guide/SKILL.md
  Pass: all gates F1, F2, (F3 if types
        added), 5, and 6 green.
  Fail: one or more gates report violations.
