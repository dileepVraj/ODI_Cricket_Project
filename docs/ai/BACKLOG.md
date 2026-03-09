# BACKLOG.md
**Purpose:** Project planning board — all scheduled, in-review, and icebox tasks.
**Last Updated:** 2026-03-09
**Maintained by:** Human Architect
**Do NOT attach to AI agents** — use SESSION_STATE.md for agent context.

---

## HOW TO USE

- **IN REVIEW** — completed this sprint, pending final architect sign-off
- **BACKLOG** — scheduled, broken into subtasks, ready to action
- **ICEBOX** — future ideas, not scheduled, no subtasks yet

Task IDs are sequential. Never reuse an ID.
When a task moves to COMPLETE, log it in PROJECT_CONTEXT.md Section 10
and remove from this file.

---

## Tasks Status values:

- Open — not started
- In Progress — actively being worked
- Blocked — waiting on dependency
- Closed — YYYY-MM-DD — done

---

## IN REVIEW



## BACKLOG



### [TASK-012] Token optimisation — section-aware context loading
**Status:** Open
**Priority:** Low
**Scope:** AI Tooling
**Blocked by:** Needs 1 week monitoring first (from 2026-03-03)
**Why:** Both agents burning tokens loading full standards files.
Read Discipline added as quick fix — monitor before building section-splitting.
**Subtasks:**
- [ ] Monitor agent sessions for 1 week — note any file re-reads
- [ ] Decide: is section-splitting needed after monitoring?
- [ ] If yes — design section file structure for BACKEND standards
- [ ] If yes — design section file structure for FRONTEND standards
- [ ] Update context-loader.md with section-aware attach logic
- [ ] Test with Codex and Gemini — verify token reduction

---

## Execution Order



## ICEBOX
Future ideas — not scheduled. No subtasks. No commitment.

- Phase 12 planning — live layer. NOT started.
  Do not action until architect gives explicit go-ahead.
- Format expansion — extend strategy loaders beyond ODI to T20I and other formats.
- match_pack/ expansion — add more report types as engine functions grow.
- Pre-commit hook audit — verify .githooks/pre-commit cannot be bypassed.

### [ICE-001] MCP Integration
**Status:** Icebox
**Why parked:** No actionable work until Phase 12 live layer is scoped.
Engine refactoring must complete first.
**Potential value:**
- Expose DuckDB data layer to agents via MCP server
- Wrap compliance bouncer as an invokable MCP tool
- Live match feed exposure in Phase 12 without custom connectors
**Revisit trigger:** Phase 12 scoping begins

### [ICE-002] Extract engine dispatcher from api/main.py
**Status:** Icebox
**Why parked:** Dispatch logic will change during TASK-010 engine refactoring.
Extracting before refactor means doing it twice.
**Revisit trigger:** TASK-010 complete

### [ICE-003] Extract error handler from api/main.py
**Status:** Icebox
**Why parked:** Low priority, not blocking anything.
**Revisit trigger:** TASK-018 and TASK-010 complete

### [ICE-004] Enhance context-loader to output correct guide skill path based on task type
**Status:** Icebox
**Why parked:** Guide skills just built — context-loader enhancement is a quality-of-life
improvement, not a blocker. TASK-010 takes priority.
**What it does:**
- Reads task type from SESSION_STATE.md Active Task section
- Outputs the correct guide skill path alongside the standards file attach list
**Revisit trigger:** After TASK-010 engine refactoring completes

### [ICE-005] Numba AOT Warm-Up Standard
**Status:** Icebox
**Why parked:** Phase 12 (live layer) has not started. No Monte Carlo simulation
code exists in the codebase. No Numba dependency. When this standard was
previously included as Mandate 7 in ENGINEERING_STANDARDS_BACKEND.md v2.2,
it was actively harmful — agents interpreted its presence as permission to
start building Phase 12 infrastructure. It was deliberately removed on 2026-03-03.
**Revisit trigger:** Phase 12 scoping begins AND Monte Carlo simulation is designed.

---

*End of BACKLOG.md — Last Updated 2026-03-09*
*For current session state, see docs/ai/SESSION_STATE.md*
*For permanent project knowledge, see docs/ai/PROJECT_CONTEXT.md*
