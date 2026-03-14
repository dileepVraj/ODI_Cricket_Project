# AGENTS.MD — Governing Law for AI Agents

**Version:** 3.0
**Last Updated:** 2026-03-14
**Status:** SUPREME DIRECTIVE — all prior versions superseded
**Core Directive:** "Assume data is dirty, boundaries are strict, and trust is zero."
**Project:** Cricket Algo-Trading Platform
**Project Root:** `C:\Cricket_Project_Stable\`

---

## PART 0: DUAL-AGENT WORKFLOW

This project uses two agents with distinct roles. Read this part first regardless of which agent you are.

---

### The Two Agents

**Claude** — Planning & Verification Agent
- Role: Think, plan, write task prompts, verify reports, maintain handoff context
- Does NOT execute implementation tasks (engines, calculators, API, components)
- CAN make small direct tweaks (see Small Tweak Rule below)
- Reads this file for PART 0 + PART 1 (Claude Bootstrap section)

**Codex** — Execution Agent
- Role: Implement tasks written by Claude, run gates, commit, write reports
- Reads this file in full — all parts apply
- Receives work exclusively via `workflow/taskFile.md`

---

### Workflow Files (all in `workflow/` directory)

| File | Written by | Purpose |
|---|---|---|
| `workflow/plan.md` | Claude | Plan for current idea — awaits human approval |
| `workflow/tasks.md` | Claude | Task breakdown after plan is approved |
| `workflow/taskFile.md` | Claude | Active task prompt for Codex — one task at a time |
| `workflow/taskFileTemplate.md` | Reference | Template Claude follows when writing taskFile.md |
| `workflow/report.md` | Codex | Task completion report — human presents to Claude for verification |
| `workflow/handoff.md` | Claude | ≤25 line context brief — human pastes at start of new session |

---

### The Workflow Cycle

```
1. IDEA
   Human brings idea (bug fix / feature / refactor / small task) to Claude.

2. PLAN
   Claude reads only the relevant files needed to understand the scope.
   Claude writes plan to workflow/plan.md.
   Human reviews — approves or iterates. No tasks are written until plan is approved.

3. TASK BREAKDOWN
   Claude writes workflow/tasks.md — splits plan into discrete tasks.
   Each task = one Codex session.

4. TASK WRITE
   Claude writes one task prompt into workflow/taskFile.md
   following workflow/taskFileTemplate.md exactly.
   Task prompt MUST include READ FIRST with exact standards file paths.

5. CODEX EXECUTES
   Human triggers Codex. Codex reads workflow/taskFile.md.
   Codex implements, runs gates, commits, writes workflow/report.md, prints terminal summary.

6. UNBLOCK (if needed)
   If Codex is blocked — human pastes the blocker to Claude.
   Claude diagnoses and provides a resolution path.
   Human relays resolution to Codex.

7. VERIFY
   Human presents workflow/report.md to Claude.
   Claude checks: gates passed, acceptance criteria met, no violations.
   If PASS → Claude gives green signal + overwrites workflow/handoff.md.
   If FAIL → Claude flags the issue — human decides next action.

8. NEXT TASK / CONTEXT RESET
   Human /clears Claude context.
   New session starts with: "Read workflow/handoff.md" to restore context.
   Repeat from step 1 or 4 for next task.
```

---

### Claude's Planning Rules

**1. Read only what you need.**
Before writing a plan, read only the files relevant to the idea:
- Always read: `docs/ai/SESSION_STATE.md`, `workflow/handoff.md`
- Read relevant source files based on what the idea touches
- Do NOT scan the full codebase speculatively

**2. plan.md discipline.**
- Write the plan to `workflow/plan.md`
- Mark it DRAFT until human approves
- Do not write `workflow/tasks.md` until human explicitly approves the plan
- If plan is revised, overwrite `workflow/plan.md` — do not append

**3. tasks.md discipline.**
- After plan approval, split into the minimum number of tasks needed
- Each task must be independently executable by Codex in one session
- Order tasks so dependencies are respected (no task requires output from a future task)

**4. taskFile.md discipline — the most important rule.**
When writing `workflow/taskFile.md`, follow `workflow/taskFileTemplate.md` exactly.
Every task prompt MUST include a `READ FIRST` section listing the exact standards files
Codex must load. Use the table below to select files:

| Task scope | Standards files to include in READ FIRST |
|---|---|
| Backend engine/calculator/service | MANDATES_1_TO_4, SYSTEM_TOPOLOGY, HIGH_IMPACT_REGISTRY, GATE_SEQUENCE, SKILLS_REGISTRY, WORKFLOW_AND_LAWS, PYTHON_STANDARDS, MEMORY_AND_THREADING |
| team_engine.py modification | All backend files above + KNOWN_PATTERNS_KIPS |
| Frontend component | MANDATES_1_TO_4, SYSTEM_TOPOLOGY, HIGH_IMPACT_REGISTRY, GATE_SEQUENCE, SKILLS_REGISTRY, WORKFLOW_AND_LAWS, TACTICAL_EXECUTION, UI_IMPLEMENTATION, PERF_RESILIENCE_A11Y_TESTING |
| Both backend + frontend | All backend files + all frontend files |

All paths are relative to `docs/guides/`. Example full path: `docs/guides/coreStandards/MANDATES_1_TO_4.md`

**5. Report verification.**
When human presents `workflow/report.md`, check:
- All triggered gates are PASS
- All acceptance criteria SATISFIED
- Bouncer post-task matches or improves baseline
- Both commit hashes are real (not NONE)
- PROJECT_CONTEXT.md Section 4 has exactly 5 entries
- workflow/taskFile.md cleared — YES
If all checks pass → give green signal → overwrite `workflow/handoff.md`.

**6. handoff.md rules.**
- Overwrite `workflow/handoff.md` only after giving green signal on a verified report
- Maximum 25 lines of content
- Cover: last task completed, what was achieved, current phase, next task in queue, any known blockers
- Write in plain text — no markdown headers, no bullet nesting

**7. Small Tweak Rule.**
Claude may execute small changes directly (without writing a taskFile for Codex) when ALL of these are true:
- Touches ≤ 3 files
- Does NOT touch engine, calculator, or service files in `formats/` or `core/`
- Does NOT touch any registered file (`core/data_access.py`, `core/interfaces/team_types.py`, `api/serializers.py`)
- Does NOT require gate validation (no bouncer run needed)
- Examples: config edits, template updates, doc fixes, small frontend style tweaks

If any condition above is NOT met → write a task for Codex instead.

---

## PART 1: MANDATORY BOOTSTRAP

**→ If you are Claude: follow the Claude Bootstrap below.**
**→ If you are Codex: skip to the Codex Bootstrap section.**

---

### Claude Bootstrap

Execute at the start of every Claude session, in order.

**Step C1 — Restore context**
```bash
cat workflow/handoff.md
cat docs/ai/SESSION_STATE.md
```
Extract: current phase, last completed task, next task in queue, active blockers.
If handoff.md is empty — ask human what we're working on before proceeding.

**Step C2 — Understand the request**
Identify which workflow step the human is asking for:
- New idea → go to Plan (Step C3)
- Plan revision → update workflow/plan.md
- Task write → go to Task Write (Step C4)
- Report verification → go to Verify (Step C5)
- Blocker resolution → diagnose and provide resolution path
- Small tweak → check Small Tweak Rule (Part 0), execute if eligible

**Step C3 — Plan**
Read the relevant source files for the idea.
Write plan to `workflow/plan.md`. Mark status: DRAFT.
Present plan to human. Wait for approval. Do not proceed to Step C4 without approval.

**Step C4 — Task Write**
If tasks.md not yet written: write `workflow/tasks.md` with task breakdown.
Write one task prompt to `workflow/taskFile.md` following `workflow/taskFileTemplate.md`.
Include READ FIRST with exact standards file paths (see table in Part 0 Rule 4).
Confirm with human before handing off to Codex.

**Step C5 — Verify Report**
Read `workflow/report.md`.
Check all items listed in Part 0 Rule 5.
If all pass → print: "GREEN SIGNAL — TASK-XXX complete. Proceed to next task."
Then overwrite `workflow/handoff.md` with current context (≤25 lines).
If any check fails → list the specific failures. Do not give green signal.

---

### Codex Bootstrap

Execute this sequence before any code change, in this exact order. Do not skip steps.

**Step 0 — Check for workflow/taskFile.md**
Before any other step, check if `workflow/taskFile.md` exists and is non-empty.
```bash
cat workflow/taskFile.md
```

If it exists and is non-empty:
- Stop all other bootstrap steps
- Read `docs/ai/TASK_RUNNER.md`
- Execute the task in `workflow/taskFile.md`
- Do not proceed with Steps 1–4 below — TASK_RUNNER handles everything

If it does not exist or is empty:
- Continue with Step 1 below as normal

**Step 1 — Load Context (context-loader skill)**
Invoke `core/gen_ai/skills/guides/backend/context-loader/context-loader.md` now.
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

**Step 2 — Load Scoped Standards Files**

Load ONLY the files listed for your task type. All paths are relative to `docs/guides/`.
Do NOT load files not listed for your task type.

**MANDATORY (every task):**
- `coreStandards/MANDATES_1_TO_4.md`
- `coreStandards/SYSTEM_TOPOLOGY.md`
- `coreStandards/HIGH_IMPACT_REGISTRY.md`
- `coreStandards/GATE_SEQUENCE.md`
- `coreStandards/SKILLS_REGISTRY.md`

**FOR ALL TASKS MODIFYING EXISTING CODE (add to mandatory):**
- `coreStandards/WORKFLOW_AND_LAWS.md`

**FOR BACKEND TASKS (add to mandatory):**
- `backendStandards/PYTHON_STANDARDS.md`
- `backendStandards/MEMORY_AND_THREADING.md`

**FOR FRONTEND TASKS (add to mandatory):**
- `frontendStandards/TACTICAL_EXECUTION.md`
- `frontendStandards/UI_IMPLEMENTATION.md`
- `frontendStandards/PERF_RESILIENCE_A11Y_TESTING.md`

**CONDITIONAL (load only when explicitly required by task):**
- `backendStandards/KNOWN_PATTERNS_KIPS.md` → only when task touches `formats/odi/engines/team_engine.py`
- `coreStandards/MANDATES_5_6_LIVE.md` → only when task touches `core/live/` or `api/live/` [DORMANT]

Do not read `ENGINEERING_STANDARDS_CORE.md` — that is the human architect file, not the agent file.
Do not read or update `docs/ai/AI_MEMORY.md` — it is deprecated and replaced by SESSION_STATE.md.

**Step 3 — Run Baseline Bouncer**
```bash
python core/utils/compliance_bouncer.py --root .
```
Record the output. This is your before-snapshot. Do not proceed if you cannot run this command.

**Step 4 — Classify the Task**
Before writing any code, classify every file the task will touch using the layer role table in
`docs/guides/coreStandards/MANDATES_1_TO_4.md`. This determines which mandates apply.

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
| GATE 1 | `core/gen_ai/skills/validators/backend/boundary-sentinel/` | Any modification to `core/` files |
| GATE 2 | `core/gen_ai/skills/guides/backend/duckdb-lint-ops/` | Any modification to `calculators/`, `engines/`, `services/` |
| GATE 3 | `core/gen_ai/skills/validators/backend/manifest-contract-verifier/` | Any modification to `manifest.py` or engine files in `formats/` |
| GATE 4 | `core/gen_ai/skills/validators/backend/serialization-guard/` | Any modification to `api/serializers.py` or engine return types |
| GATE 5 | `core/gen_ai/skills/validators/backend/paradigm-sentinel/` | Always — after all primary gates pass |
| GATE 6 | `python core/utils/compliance_bouncer.py --root .` | Always — last step before task complete |

**Critical path rule:** Gate 2 (duckdb-lint-ops) is in `guides/` not `validators/`. Using the wrong path is a hard fail.

**Dormant:** `core/gen_ai/skills/validators/backend/event-state-linter/` — activates when `core/live/` is created in Phase 12. Do not trigger now.

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

**RULE 5 — docs/ai/ is human-write-only by default**
Never create, modify, or delete any file under `docs/ai/`
(includes SESSION_STATE.md, PROJECT_CONTEXT.md, BACKLOG.md, and any
other file in that directory) unless the current task prompt contains
an explicit instruction from the human architect to do so.

The instruction must name the specific file and the specific change
permitted. When explicit permission is given, make only the change
instructed — do not update any other file in docs/ai/ beyond what
was explicitly named.

If the task prompt does not contain explicit permission for a specific
docs/ai/ file — treat it as human-write-only. Agent writes to this
directory without explicit instruction are a hard architectural
violation regardless of bouncer output.

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

## PART 6: DEFINITION OF DONE

A task is NOT complete until all of the following are true:

1. All triggered gate results are recorded (gate name, path, pass/fail).
2. Gate 5 (paradigm-sentinel) result is recorded.
3. Gate 6 (compliance_bouncer) output is `PASS: 100% compliance`.
4. Post-change bouncer output matches or improves on baseline bouncer output.
5. No registered file was modified without explicit instruction or stop-state-trace-confirm.
6. Report written to `workflow/report.md` in the required format (see Part 7).
7. PROJECT_CONTEXT.md Section 4 contains exactly 5 entries (rolling window enforced).
8. Terminal summary printed with task status and report location.

A passing bouncer with missing gate results is a FAIL. All gates must be present.

---

## PART 7: REPORT FORMAT

Every completed task MUST produce a report written to `workflow/report.md` in EXACTLY this format.
No prose summaries, no alternative layouts, no "what changed" sections. Deviation is a hard fail.

```
TASK REPORT
===========
Task: [one-line description]
Date: [date]
Agent: Codex

Baseline Bouncer: [PASS/FAIL — N violations]
Post-Task Bouncer: [PASS/FAIL — N violations — matches baseline: YES/NO]

Gates Triggered:
- GATE 1 (boundary-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 2 (duckdb-lint-ops): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 3 (manifest-contract-verifier): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 4 (serialization-guard): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE F1 (frontend-lint-sentinel): [TRIGGERED/SKIPPED — frontend scope only] — [PASS/FAIL]
- GATE F2 (frontend-paradigm-sentinel): [TRIGGERED/SKIPPED — frontend scope only] — [PASS/FAIL]
- GATE F3 (frontend-type-sync-guard): [TRIGGERED/SKIPPED — frontend scope only] — [PASS/FAIL]
- GATE 5 (paradigm-sentinel): TRIGGERED — [PASS/FAIL]
- GATE 6 (compliance_bouncer): TRIGGERED — [PASS/FAIL]

Files Modified: [list]
Registered Files Touched: [list or NONE]
Stop-State-Trace-Confirm Used: [YES/NO — which file]

Blockers Hit: [list or NONE]
Phase 12 References Added: [YES — VIOLATION / NO — confirmed]
AI_MEMORY.md Updated: [should always be NO — file is deprecated]

Doc Updates:
- BACKLOG.md              : TASK-{ID} CLOSED — YES/NO
- SESSION_STATE.md        : Last Completed updated — YES/NO
- PROJECT_CONTEXT.md Sec4 : Rolling window enforced (exactly 5 entries) — YES/NO

workflow/taskFile.md Cleared: YES — must be YES before COMPLETE

Commit 1 (task work)  : [hash] — must be a real hash, not NONE
Commit 2 (doc updates): [hash] — must be a real hash, not NONE

Status: [COMPLETE / BLOCKED — reason]
```

---

## PART 8: HARD PROHIBITIONS

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
- Using `core/gen_ai/skills/validators/backend/duckdb-lint-ops/` — wrong path, Gate 2 is in `guides/backend/`
- Running `git commit --no-verify` — bouncer is not optional
- Skipping context-loader invocation at session start — it is mandatory for all task scopes
- Running `git status --short .` or `git status --short` without an explicit named directory — BANNED. Required form: `git status --short tests/` or `git status --short api/` etc. The `.` argument is not a valid scope.
- Submitting a task report in any format other than the template defined in Part 7 — report format is mandatory, not a suggestion
- Writing report output to terminal only — report MUST be written to `workflow/report.md`
- Do NOT modify or remove the constructor
  discard pattern
  `_ = (match_df, phase_df, dal)`
  in `formats/odi/engines/team_engine.py`
  line 26 — intentional stateless design.
  See docs/guides/backendStandards/KNOWN_PATTERNS_KIPS.md KIP-001.

- Do NOT add a duplicate definition of
  `_context_match_df` to the upper section
  of `formats/odi/engines/team_engine.py`
  — method is defined in the lower section
  of the same file.
  See docs/guides/backendStandards/KNOWN_PATTERNS_KIPS.md KIP-002.

---

*End of AGENTS.md — Version 3.0 — 2026-03-14*
*Source of truth for current project state: docs/ai/SESSION_STATE.md*
*Workflow files: workflow/ directory*
*Standards: docs/guides/coreStandards/ | docs/guides/backendStandards/ | docs/guides/frontendStandards/*
