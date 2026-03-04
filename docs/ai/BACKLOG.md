# BACKLOG.md
**Purpose:** Project planning board — all scheduled, in-review, and icebox tasks.
**Last Updated:** 2026-03-04
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

- Nothing as of now.

---

## BACKLOG

### [TASK-008] Filesystem Integrity Rules
**Status:** Closed — 2026-03-04
**Priority:** High
**Scope:** AI Tooling
**Blocked by:** Nothing
**Why:** Codex deleted core/ contents during worktree task on 2026-03-03.
Hard rules prevent repeat.
**Subtasks:**
- [X] Add Filesystem Integrity Rules block to AGENTS.md Part 5
- [X] Add Filesystem Integrity Rules block to GEMINI.md Part 5
- [X] Verify both files committed clean
- [X] Update PROJECT_CONTEXT.md Section 5.2 to reflect rules added

**Rules added (copied into both files):**
- MUST NOT delete, move, or rename any file not explicitly listed in task prompt
- MUST NOT run: git clean, git reset --hard, git rm, git checkout -- .
- If any required reference file is missing from worktree — hard stop.
  Output: CRITICAL BLOCKER: [file] missing. Task halted. Do not improvise.
- MUST NOT run recursive filesystem scans to locate missing files
- Run git status on target directory BEFORE and AFTER every file operation
- If unexpected deletions appear in git status — stop immediately.
  Report as CRITICAL DEVIATION before any further action.

---

### [TASK-009] Core/ file audit — delete confirmed dead files
**Status:** Closed — 2026-03-04
**Priority:** High
**Scope:** Backend housekeeping
**Blocked by:** Nothing — confirmed safe to delete
**Why:** backtester.py and base_engine.py confirmed dead scaffolding.
No imports found anywhere. Confirmed via grep on 2026-03-03.
**Note:** Both files were never git-tracked. Already absent from disk.
No commit required — git had no record of them.
**Subtasks:**
- [X] Remove-Item core/backtester.py
- [X] Remove-Item core/base_engine.py
- [X] Run compliance bouncer — confirm still passes
- [X] Commit: chore: remove confirmed dead scaffold files

---

### [TASK-010] Engine refactoring
**Status:** Open
**Priority:** Critical
**Scope:** Backend
**Blocked by:** TASK-014, TASK-015, TASK-016, TASK-017, TASK-018, TASK-019 — pre-engine housekeeping must complete first
**Why:** Primary active work. Engine files in formats/ need refactoring
to meet Phase 11.3 compliance standards.
**Subtasks:**
- [ ] Run tree formats/ /F /A — map full engine file structure
- [ ] Run compliance bouncer on formats/ — identify violations per file
- [ ] Triage violations by severity — list per engine file
- [ ] Refactor engine files one at a time (never batch)
- [ ] Per engine: run full six-gate sentinel sequence
- [ ] Per engine: bouncer must pass before moving to next file
- [ ] Final bouncer pass across full codebase
- [ ] Update TECHNICAL_AUDIT_REPORT.md on completion

---

### [TASK-011] Update TECHNICAL_AUDIT_REPORT.md
**Status:** Blocked
**Priority:** Medium
**Scope:** Documentation
**Blocked by:** TASK-010 must complete first — audit reflects engine state
**Why:** Stale since 2026-02-27, predates Phase 11.3 completion
and engine refactoring.
**Subtasks:**
- [ ] Review current report sections
- [ ] Update phase status to reflect Phase 11.3 complete
- [ ] Update engine compliance status after TASK-010
- [ ] Increment version to v3.2.0
- [ ] Update audit date

---

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

### [TASK-013] Create CLAUDE.md
**Status:** Blocked
**Priority:** Low
**Scope:** AI Tooling
**Blocked by:** Claude CLI pro subscription not yet activated
**Why:** Claude CLI requires its own agent config file at project root.
**Subtasks:**
- [ ] Activate Claude CLI pro subscription
- [ ] Copy AGENTS.md to CLAUDE.md at project root
- [ ] Verify all paths and references are correct
- [ ] Commit: feat: add CLAUDE.md for Claude CLI
- [ ] Update PROJECT_CONTEXT.md Section 5

---

### [TASK-014] Fix stale test — test_api_integration.py
**Status:** Closed - 2026-03-04
**Priority:** High
**Scope:** Backend housekeeping
**Blocked by:** Nothing
**Why:** /predict endpoint no longer exists. Passing test testing a dead endpoint
is active misinformation — violates Stale Test Law. Do this first.
**Estimate:** 30 mins
**Subtasks:**
- [x] Locate all /predict references in tests/test_api_integration.py
- [x] Disable or rewrite each with correct comment explaining why
- [x] Run compliance bouncer — confirm still passes
- [x] Commit: fix(tests): disable stale predict endpoint test [TASK-014]

---

### [TASK-015] Introduce python-dotenv — move hardcoded config to .env
**Status:** Closed - 2026-03-04
**Priority:** High
**Scope:** Backend housekeeping
**Blocked by:** Nothing
**Why:** Hardcoded CORS origin and database paths in api/main.py — not portable,
not production-safe. Single most impactful housekeeping change.
**Estimate:** Half day
**Subtasks:**
- [ x] Add python-dotenv to requirements.txt and pyproject.toml
- [ x] Create .env file at project root with CORS origin and DB paths
- [ x] Add .env to .gitignore
- [ x] Create .env.example with placeholder values — commit this, not .env
- [ x] Update api/main.py to load config via dotenv
- [ x] Run compliance bouncer — confirm still passes
- [ x] Commit: feat(config): introduce python-dotenv, move hardcoded config to .env [TASK-015]

---

### [TASK-016] Align requirements.txt and pyproject.toml
**Status:** Closed - 2026-03-04
**Priority:** High
**Scope:** Backend housekeeping
**Blocked by:** Nothing
**Why:** FastAPI version discrepancy between the two files — silent time bomb
on fresh installs and CI.
**Estimate:** 15 mins
**Subtasks:**
- [ x] Compare FastAPI version in requirements.txt vs pyproject.toml
- [ x] Align both to the same pinned version currently running
- [ x] Check for any other version discrepancies while in there
- [ x] Commit: chore(deps): align requirements.txt and pyproject.toml versions [TASK-016]

---

### [TASK-017] Extract context_builder.py from api/main.py
**Status:** Open
**Priority:** High
**Scope:** Backend refactor
**Blocked by:** TASK-015 — dotenv changes touch main.py, do that first
**Why:** Context injection logic inline in main.py (~120 lines that don't belong there).
Extraction improves testability and reduces agent collision risk during TASK-010.
**Estimate:** Half day
**Subtasks:**
- [ ] Identify all context building logic in api/main.py
- [ ] Create core/services/context_builder.py with extracted logic — fully typed
- [ ] Update api/main.py to call context_builder
- [ ] Run compliance bouncer — confirm still passes
- [ ] Commit: refactor(services): extract context_builder from main.py [TASK-017]

---

### [TASK-018] Extract startup/lifespan DB loading from api/main.py
**Status:** Open
**Priority:** High
**Scope:** Backend refactor
**Blocked by:** TASK-017 — do in same sweep while main.py is open
**Why:** Inline DB loading logic in main.py causes agents to accidentally touch
data loading when working on routing. Clean separation protects TASK-010.
**Estimate:** 2 hours
**Subtasks:**
- [ ] Identify lifespan/startup DB loading logic in api/main.py
- [ ] Create core/services/startup.py with extracted logic — fully typed
- [ ] Update api/main.py lifespan to delegate to startup.py
- [ ] Run compliance bouncer — confirm still passes
- [ ] Commit: refactor(services): extract DB startup logic into startup.py [TASK-018]

---

### [TASK-019] Rename compliance-bouncer.py to compliance_bouncer.py
**Status:** Open
**Priority:** Medium
**Scope:** Backend housekeeping
**Blocked by:** TASK-017, TASK-018 — do last, after main.py churn settles
**Why:** Hyphen violates Module Naming standard. Causes ergonomic friction
everywhere it is referenced. Must be done atomically — many files reference it.
**Estimate:** 1 hour
**Subtasks:**
- [ ] Rename core/utils/compliance-bouncer.py → core/utils/compliance_bouncer.py
- [ ] Update .githooks/pre-commit
- [ ] Update AGENTS.md and GEMINI.md
- [ ] Update ENGINEERING_STANDARDS_BACKEND.md, ENGINEERING_STANDARDS_CORE.md, ENGINEERING_STANDARDS_FRONTEND.md
- [ ] Update PROJECT_CONTEXT.md — all references
- [ ] Update SESSION_STATE.md
- [ ] Run renamed bouncer — confirm still passes
- [ ] Commit: chore(utils): rename compliance-bouncer.py to compliance_bouncer.py [TASK-019]

---

## Execution Order (pre-engine housekeeping)

```
TASK-014 → TASK-015 → TASK-016 → TASK-017 → TASK-018 → TASK-019 → TASK-010
```

---

## ICEBOX
Future ideas — not scheduled. No subtasks. No commitment.

- Frontend compliance debt — 5 items in PROJECT_CONTEXT.md Section 7.1.
  Action after engine queue clears.
- Phase 12 planning — live layer / Numba AOT. NOT started.
  Do not action until architect gives explicit go-ahead.
- Format expansion — extend strategy loaders beyond ODI to T20I and other formats.
- match_pack/ expansion — add more report types as engine functions grow.
- Pre-commit hook audit — verify .githooks/pre-commit cannot be bypassed.
- Automate Gates 1–5 as runnable Python scripts — currently prompt-based skills
  relying on agent honesty. Automation makes them trustworthy and agent-independent.
  Reference: validators/boundary-sentinel, duckdb-lint-ops, manifest-contract-verifier,
  serialization-guard, paradigm-sentinel.

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

---

*End of BACKLOG.md — Last Updated 2026-03-04*
*For current session state, see docs/ai/SESSION_STATE.md*
*For permanent project knowledge, see docs/ai/PROJECT_CONTEXT.md*
