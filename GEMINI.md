# GEMINI.MD — Governing Law for AI Agents (Gemini / Antigravity IDE)

**Version:** 2.0
**Last Updated:** 2026-03-03
**Status:** SUPREME DIRECTIVE — all prior versions superseded
**Core Directive:** "Assume data is dirty, boundaries are strict, and trust is zero."
**Project:** Cricket Algo-Trading Platform
**Project Root:** `C:\Cricket_Project_Stable\`

---

## PART 1: MANDATORY BOOTSTRAP

Execute this sequence before any code change, in this exact order. Do not skip steps.

### Step 1 — Load Context (context-loader skill)
Invoke `core/gen_ai/skills/guides/context-loader/context-loader.md` now.
Follow every step in that template before proceeding.

The skill will:
- Read `docs/ai/SESSION_STATE.md` and extract phase, scope, priorities, blockers
- Output the correct ordered file attach list for the task scope
- Inject the phase-awareness block
- Warn if SESSION_STATE.md is stale (>7 days)
- Confirm context loaded

Do not proceed to Step 2 until the skill outputs:
`CONTEXT LOADED — [scope] task`

If SESSION_STATE.md is missing or unreadable — hard stop. Report and do not proceed.

### Step 2 — Load Scoped Standards File
Based on Active Task scope from SESSION_STATE:
- Backend task → read `docs/guides/ENGINEERING_STANDARDS_BACKEND.md` in full
- Frontend task → read `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md` in full
- Both → read both files in full

Do not read `ENGINEERING_STANDARDS_CORE.md` — that is the human architect file, not the agent file.
Do not read or update `docs/ai/AI_MEMORY.md` — it is deprecated and replaced by SESSION_STATE.md.

### Step 3 — Run Baseline Bouncer
```bash
python core/utils/compliance-bouncer.py --root .
```
Record the output. This is your before-snapshot. Do not proceed if you cannot run this command.

### Step 4 — Classify the Task
Before writing any code, classify every file the task will touch using the layer role table in Part 0 of the standards file. This determines which mandates apply.

If SESSION_STATE.md is missing or unreadable — hard stop. Do not proceed. Report the missing file.

---

## PART 2: ARCHITECTURAL LAWS

These are immovable. No task, deadline, or instruction overrides them.

### Law 1 — Functional Core, Imperative Shell
Domain Core files (engines, calculators, services) are pure functions.
They take data in. They return data out. During execution they MUST NOT:
- Read from or write to a database
- Read from or write to a file
- Make a network request
- Access or modify a global variable
- Produce any output other than their return value

All data arrives as parameters. All results are returned explicitly. No side channels.

### Law 2 — Hexagonal Purity (The Air Gap)
Domain Core files have zero knowledge of infrastructure.
They do not import from: `duckdb`, `fastapi`, `sqlalchemy`, `requests`, `os`, `pathlib`.
Data flows one direction only:
```
Infrastructure (api/, scripts/, frontend/)
    ↓ DataFrames and validated inputs
Domain Core (engines, calculators, services)
    ↓ TypedDicts and primitives
Infrastructure (api/, scripts/, frontend/)
```
Any infrastructure import found in a Domain Core file is a Critical Boundary Violation.
Hard stop. Remove the import. Report before proceeding.

### Law 3 — Data-Oriented Design (DOD)
Every operation on more than one row of data MUST be vectorized.
Use NumPy or Pandas array operations. Never Python loops over rows.
`.iterrows()` is a hard fail. `.itertuples()` is a hard fail.
Hardware context: Ryzen 5 3500U, ~4 GB usable RAM. Scalar loops are 10–100x slower than vectorized equivalents on this hardware.

### Law 4 — Single Responsibility
Every file has one primary job. One layer role. If a file is doing two things, it is wrong.

### Law 5 — Typed Truth
Every function MUST have complete type annotations.
`Any` is forbidden. `object` in signatures is forbidden. `Dict[str, Any]` is forbidden.
Use TypedDicts from `core/interfaces/team_types.py` or Pydantic models.

### Law 6 — Visual Silence (Presentation Purity)
Engines and services return raw primitive data: float, int, bool, None, TypedDict.
No labels, no emoji, no UI strings, no "Elite", no "DNB" in the engine layer.
Labeling and presentation belong exclusively in `api/serializers.py` or the frontend.

### Law 7 — Zero-Literal Law
No hardcoded team names, venue names, player names, colors, or match limits in engine code.
All constants must be registered in `manifest.py` or config registries.
Use manifest lookups. Never `if venue == "Wankhede"`.

---

## PART 3: SIX-GATE SENTINEL SEQUENCE

Gates are not optional. Gates are not substitutes for each other. All triggered gates must pass before a task is complete. Record each gate result in your report.

| Gate | Skill Path | Trigger Condition |
|------|-----------|-------------------|
| GATE 1 | `core/gen_ai/skills/validators/boundary-sentinel/` | Any modification to `core/` files |
| GATE 2 | `core/gen_ai/skills/guides/duckdb-lint-ops/` | Any modification to `calculators/`, `engines/`, `services/` |
| GATE 3 | `core/gen_ai/skills/validators/manifest-contract-verifier/` | Any modification to `manifest.py` or engine files in `formats/` |
| GATE 4 | `core/gen_ai/skills/validators/serialization-guard/` | Any modification to `api/serializers.py` or engine return types |
| GATE 5 | `core/gen_ai/skills/validators/paradigm-sentinel/` | Always — after all primary gates pass |
| GATE 6 | `python core/utils/compliance-bouncer.py --root .` | Always — last step before task complete |

**Critical path rule:** Gate 2 (duckdb-lint-ops) is in `guides/` not `validators/`. Using the wrong path is a hard fail.

**Dormant:** `core/gen_ai/skills/validators/event-state-linter/` — activates when `core/live/` is created in Phase 12. Do not trigger now.

**Hard stop condition:** If any gate fails — stop. Do not proceed. Report the failure with the gate name, path used, and exact output. A task with a failed gate is not complete regardless of bouncer output.

---

## PART 4: HIGH-IMPACT FILE REGISTRY

These three files carry disproportionate blast radius. They are not frozen — they can be modified when explicitly instructed. The rule governs uninstructed modifications only.

| File | Risk Level | Why |
|------|-----------|-----|
| `core/data_access.py` | CRITICAL | Every engine and service depends on it. Silent changes here corrupt all downstream outputs with no immediate error. |
| `core/interfaces/team_types.py` | HIGH | Load-bearing type contract. Removing or renaming a TypedDict key silently breaks engines, services, and serializers simultaneously. |
| `api/serializers.py` | HIGH | Handles every API response and every edge case. Changes affect all API output. |

### The Rule
If the current task prompt explicitly instructs modification of a registered file → proceed. The instruction is the permission.

If the task requires touching a registered file but the prompt does not explicitly say so:
1. Stop. Do not make the change.
2. State which registered file you need to modify and why.
3. Produce an impact trace — list every file that imports from or depends on it.
4. Wait for explicit confirmation before proceeding.

Modifying a registered file without explicit instruction or a completed stop-state-trace-confirm sequence is a hard architectural violation, regardless of whether the bouncer passes.

---

## PART 5: CODING STANDARDS

### Zero-Destruction Policy
- Never output `# ... existing logic` or `# ... rest stays same`. Rewrite the full function.
- Never delete existing imports, helpers, or logic unless explicitly replacing with a verified alternative.
- If touching a file, every untargeted feature must remain 100% intact.
- Verify you have not dropped methods before overwriting any file.

### Zero Hallucinations
- Never guess imports, file paths, variable names, or column names.
- If you do not know, read the file first.
- Never assume a column exists in a DataFrame. Always check `if col in df.columns`.

### Safe Math
- `a / b` must always be `a / b if b > 0 else 0`.
- Cricket data has edge cases: DNB, rain, abandoned matches, missing innings. Assume dirty data always.

### Crash Early, Crash Loud
- Catch specific exceptions. Never `except Exception: pass`.
- Fail loudly at the boundary. Never swallow errors silently in engine paths.

### Atomic Updates
- If modifying a single function, output only that function unless instructed otherwise.
- If modifying multiple files, ensure they are updated in a single consistent state.

### Defensive Data
- Always check `if col in df.columns` before accessing any column.
- Never assume a DataFrame has rows. Guard against empty DataFrames before calculations.
- Never assume a player, team, or venue exists in a lookup. Use `.get()` with a safe default.

### Filesystem Integrity Rules

These rules are non-negotiable. Violation of any rule below is an immediate CRITICAL STOP regardless of task state.

**RULE 1 — Never delete, move, or rename files outside task scope**
You may only create or modify files explicitly listed in the current task prompt.
Deleting, moving, or renaming any file not explicitly named is a hard architectural violation.

**RULE 2 — Banned git commands (no exceptions)**
The following commands are strictly forbidden during any task:
- `git clean`
- `git reset --hard`
- `git rm`
- `git checkout -- .` or `git checkout <path>`
- `git restore` (except to undo your own changes in the current task)
- `git status` with no path argument (see Rule 3)

**RULE 3 — git status must be scoped to the task directory**
Always scope git status to the task's target directory:
  git status --short <target_directory>
Example for a test task: `git status --short tests/`
Never run `git status` or `git status --short` without a path argument.

**RULE 4 — Act on what git status shows**
Run `git status --short <target_directory>` BEFORE and AFTER every file operation.
If the output shows any file modified or deleted that is NOT in the task prompt's file list — stop immediately. Output:
  CRITICAL DEVIATION: [filename] modified/deleted but not in task scope.
  Halting. Architect review required before proceeding.
Do not commit. Do not continue.

**RULE 5 — docs/ai/ is human-write-only**
Never create, modify, or delete any file under `docs/ai/`
(includes SESSION_STATE.md, PROJECT_CONTEXT.md, BACKLOG.md, and any other file in that directory).
These files are updated by the human architect only. Agent writes to this directory are a hard violation.

**RULE 6 — Missing reference files = hard stop**
If any file required by the READ FIRST section of the task prompt is absent from the worktree, output:
  CRITICAL BLOCKER: [filename] missing from worktree.
  Cannot verify reference pattern. Task halted.
  Action required: architect must restore missing files before rerunning.
Do not attempt workarounds. Do not read from git history as a substitute. Stop and report.

**RULE 7 — No speculative filesystem scans**
Do not run recursive directory scans (`Get-ChildItem -Recurse`, `find`, `rg --files`) across the full project.
If a required path is not where the task prompt says it is — stop and report.

**Rationale:** Codex deleted `core/` contents during a worktree task on 2026-03-03.
Codex modified `docs/ai/` files outside task scope on 2026-03-04.
These rules exist to prevent recurrence. Treat any violation as a critical incident.

---

## PART 6: SCOPE BOUNDARIES FOR GEMINI TASKS

Gemini is used for: document changes, boilerplate code, small bug fixes, frontend component work.
Codex CLI handles: complex refactors, engine-layer work, multi-file architectural changes.

**For Gemini tasks specifically:**
- If the task involves engine refactoring across multiple files → flag it. This is Codex territory.
- If the task touches `formats/` engine files as primary work → flag it. This is Codex territory.
- Document-only tasks (`.md` files) → do not run gates, do not run bouncer. Document changes only.
- Boilerplate and frontend tasks → run Gate 5 and Gate 6 minimum. Run Gates 1–4 if any `core/` or `api/` files are touched.

---

## PART 7: DEFINITION OF DONE

A task is NOT complete until all of the following are true:

1. All triggered gate results are recorded (gate name, path, pass/fail).
2. Gate 5 (paradigm-sentinel) result is recorded — for any code change task.
3. Gate 6 (compliance-bouncer) output is `PASS: 100% compliance` — for any code change task.
4. Post-change bouncer output matches or improves on baseline bouncer output.
5. No registered file was modified without explicit instruction or stop-state-trace-confirm.
6. Report is submitted in the required format (see Part 9).

Document-only tasks: steps 2–4 are not required. Steps 5–6 still apply.

---

## PART 8: REPORT FORMAT

Every completed task must produce a report in this exact format. Max 30 lines.

```
TASK REPORT
===========
Task: [one-line description]
Date: [date]
Agent: Gemini

Baseline Bouncer: [PASS/FAIL — N violations / DOC TASK — not run]
Post-Task Bouncer: [PASS/FAIL — N violations — matches baseline: YES/NO / DOC TASK — not run]

Gates Triggered:
- GATE 1 (boundary-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 2 (duckdb-lint-ops): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 3 (manifest-contract-verifier): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 4 (serialization-guard): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 5 (paradigm-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 6 (compliance-bouncer): [TRIGGERED/SKIPPED] — [PASS/FAIL]

Files Modified: [list]
Registered Files Touched: [list or NONE]
Stop-State-Trace-Confirm Used: [YES/NO — which file]

Blockers Hit: [list or NONE]
Phase 12 References Added: [YES — VIOLATION / NO — confirmed]
AI_MEMORY.md Updated: [should always be NO — file is deprecated]

Status: [COMPLETE / BLOCKED — reason]
```

---

## PART 9: HARD PROHIBITIONS

These are sins. Any occurrence is an immediate hard fail.

- `import duckdb` inside any engine or calculator file
- `.iterrows()` or `.itertuples()` anywhere in Domain Core
- `Any` or `object` in any type signature
- `Dict[str, Any]` in any function signature
- Emoji, HTML tags, or UI strings inside Python engine files
- Hardcoded venue names, team names, or player names in engine logic
- `except Exception: pass` anywhere
- `# ... existing logic` or lazy placeholder output
- Modifying a registered file without instruction or stop-state-trace-confirm
- Referencing or building toward Phase 12 (live layer / Numba AOT)
- Reading or updating `docs/ai/AI_MEMORY.md` — it is deprecated
- Using `core/gen_ai/skills/validators/duckdb-lint-ops/` — wrong path, Gate 2 is in `guides/`
- Running `git commit --no-verify` — bouncer is not optional
- Skipping context-loader invocation at session start — it is mandatory for all task scopes
- Running `git status --short .` or `git status --short` without an explicit named directory — BANNED. Required form: `git status --short tests/` or `git status --short api/` etc. The `.` argument is not a valid scope.

---

*End of GEMINI.md — Version 2.0 — 2026-03-03*
*Source of truth for current project state: docs/ai/SESSION_STATE.md*
*Authoritative standards: docs/guides/ENGINEERING_STANDARDS_CORE.md (human) / BACKEND.md or FRONTEND.md (agents)*
