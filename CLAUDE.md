# AGENTS.MD — Governing Law for AI Agents

**Version:** 3.1
**Last Updated:** 2026-03-20
**Status:** SUPREME DIRECTIVE — all prior versions superseded
**Core Directive:** "Assume data is dirty, boundaries are strict, and trust is zero."
**Project:** Cricket Algo-Trading Platform
**Project Root:** `C:\Cricket_Project_Stable\`

---

## PART 0: TWO-AGENT WORKFLOW

This project uses two agents with distinct, non-overlapping roles. Read this part first regardless of which agent you are.

---

### The Two Agents

**Claude** — Planning, Verification & Frontend Execution Agent
- Role: Think, plan, write task prompts, verify backend reports, execute all frontend tasks directly, maintain handoff context
- Three modes of operation:
  1. **Architect** — reads files, writes plans, writes taskFile.md for Codex
  2. **Frontend Engineer** — implements frontend tasks directly (no CLI invocation needed)
  3. **Verifier** — reviews Codex reports and implementation quality
- Owns: `frontend/` (direct execution) + all `workflow/` files
- CAN make small direct tweaks to backend config/docs (see Small Tweak Rule below)
- Reads this file for PART 0 + PART 1 (Claude Bootstrap section)

**Codex** — Backend Execution Agent
- Role: Implement backend tasks written by Claude, run gates, commit, write reports
- Reads this file in full — all parts apply
- Receives work exclusively via `workflow/taskFile.md`
- Owns: `api/`, `core/`, `formats/`, `scripts/`, `tests/`

---

### Workflow Files (all in `workflow/` directory)

| File | Written by | Purpose |
|---|---|---|
| `workflow/plan.md` | Claude | Plan for current idea — awaits human approval |
| `workflow/tasks.md` | Claude | Task breakdown after plan is approved |
| `workflow/taskFile.md` | Claude | Active task prompt for Codex — one task at a time (frontend tasks executed directly by Claude, no taskFile needed) |
| `workflow/taskFileTemplate.md` | Reference | Template Claude follows when writing taskFile.md |
| `workflow/report.md` | Codex or Claude | Task completion report — Codex writes for backend tasks; Claude writes for frontend tasks |
| `workflow/handoff.md` | Claude | ≤25 line context brief — human pastes at start of new session |

---

### The Workflow Cycle

**Single-agent tasks (Scope: backend only):**
```
1. IDEA        → Human brings idea to Claude.
2. PLAN        → Claude reads relevant files, writes workflow/plan.md (DRAFT).
                  Human approves or iterates.
3. BREAKDOWN   → Claude writes workflow/tasks.md.
4. TASK WRITE  → Claude writes one task to workflow/taskFile.md. Sets Agent: Codex.
5. EXECUTE     → Claude invokes Codex via CLI (see CLI Orchestration Protocol).
                  Codex executes, commits, writes workflow/report.md.
6. UNBLOCK     → If Codex writes BLOCKED: Claude reads the blocker, diagnoses,
                  resolves directly (Small Tweak Rule) or explains to human.
                  Human relays resolution to Codex if needed.
7. REVIEW+VERIFY → Claude dispatches `backend-auditor` and `verify` agents in parallel.
                  backend-auditor: reads every modified file, audits all architectural
                  laws, coding standards, and hard prohibitions (CLAUDE.md Parts 2, 5, 8).
                  verify: reads workflow/report.md, checks acceptance criteria, validates
                  all report fields, cross-checks commit hashes in git log.
                  Both must return PASS before proceeding.
                  Either FAIL → Claude flags exact issue. Human decides next action.
9. RESET       → Human /clears Claude. New session: "Read workflow/handoff.md".
```

**Single-agent tasks (Scope: frontend only):**
```
1. IDEA        → Human brings idea to Claude.
2. PLAN        → Claude reads relevant frontend files, writes workflow/plan.md (DRAFT).
                  Human approves or iterates.
3. BREAKDOWN   → Claude writes workflow/tasks.md.
4. EXECUTE     → Claude executes the frontend task directly (no CLI invocation).
                  Claude implements the components, runs frontend gates (F1–F4),
                  commits the work, writes workflow/report.md.
5. SELF-AUDIT  → Claude runs the frontend self-audit checklist (see Claude Bootstrap)
                  before marking the task complete.
6. VERIFY      → Claude reviews its own report against acceptance criteria.
                  PASS → green signal + update handoff.md + inform human.
                  FAIL → Claude flags the issue and resolves before completing.
7. RESET       → Human /clears Claude. New session: "Read workflow/handoff.md".
```

**Multi-agent tasks (Scope: both backend + frontend) — Two-Phase Mode:**
```
DEFAULT SEQUENCE: Codex (backend) first → Claude (frontend) second.
Reason: frontend needs the API contracts and TypeScript types that Codex defines.

1. IDEA        → Human brings idea to Claude.
2. PLAN        → Claude writes plan.md. Human approves.
3. BREAKDOWN   → Claude splits into Phase A (backend/Codex) + Phase B (frontend/Claude).
4. ORCHESTRATE → Claude runs the full two-phase sequence:

   PHASE A — Codex (backend):
   a. Claude writes Phase A task to workflow/taskFile.md.
   b. Claude invokes Codex via CLI (see CLI Commands below).
   c. Claude dispatches `backend-auditor` and `verify` agents in parallel for Phase A.
      backend-auditor audits all modified files against laws, standards, prohibitions.
      verify checks acceptance criteria and validates all report fields.
   d. Both agents must return PASS to clear Phase A.
   e. If PHASE A FAILS → stop. Inform human with exact failure. Do not proceed to Phase B.

   PHASE B — Claude (frontend):
   f. Claude executes the frontend task directly (no CLI invocation).
   g. Claude implements components, runs self-audit checklist, runs gates F1–F4, commits.
   h. Claude writes workflow/report.md for Phase B.
   i. Claude reviews its own Phase B implementation against acceptance criteria.
   j. If PHASE B FAILS → flag the issue. Phase A work is already committed.

5. COMPLETE    → Both phases PASS: Claude updates handoff.md, reports full summary to human.
6. RESET       → Human /clears Claude. New session: "Read workflow/handoff.md".
```

---

### CLI Orchestration Protocol

Applies to backend tasks only. Claude invokes Codex via PowerShell CLI.
Frontend tasks are executed directly by Claude — no CLI invocation needed.
Human does not manually trigger agent sessions.

**Sequencing Rule (multi-phase tasks):**
Default order is defined in The Workflow Cycle above (Codex first, Claude second).
- EXCEPTION: Claude (frontend) first → Codex (backend) second, ONLY IF:
  - Frontend change is entirely on an existing, stable API (no new endpoints, no type changes)
  - Backend change is independent (e.g. engine optimisation that does not affect any API contract)
  - Claude explicitly states the justification when writing the plan.

**CLI Commands:**

Frontend tasks — Claude executes directly. No CLI invocation. No taskFile needed.

Invoke Codex (backend tasks — single-agent or Phase A):
```powershell
codex exec --full-auto -C "C:\Cricket_Project_Stable" "Read CLAUDE.md. Then read workflow/taskFile.md and execute the backend task."
```

The `Orchestration` field in taskFile.md tells Codex whether this is SOLO or MULTI-PHASE-A.

**Bash timeout:** Always set timeout to 1800000ms (30 minutes) when invoking agent CLIs.
The default 2-minute timeout will kill the agent mid-task.

**Pre-call snapshot — MANDATORY before every CLI invocation:**
Before calling the CLI, Claude MUST capture the current state of report.md:
```bash
# Record last-modified timestamp before invoking agent
stat -c "%Y %n" workflow/report.md 2>/dev/null || echo "report.md does not exist"
```
Store this snapshot. It is the baseline for post-call validation.

**Post-call report validation — MANDATORY after every CLI invocation:**
After the CLI call returns, Claude MUST run this check sequence:

Step 1 — Did report.md change?
```bash
stat -c "%Y %n" workflow/report.md 2>/dev/null || echo "report.md missing"
```
Compare to pre-call snapshot.
- If unchanged or missing → SILENT FAILURE (see Silent Failure Protocol below)
- If changed → proceed to Step 2

Step 2 — Read and validate report.md content:
```bash
cat workflow/report.md
```
Check:
- `Agent:` field matches the agent that was invoked
- `Status:` is present (COMPLETE or BLOCKED)
- Both commit hashes are real (not NONE) — only required for COMPLETE
- `workflow/taskFile.md Cleared: YES` — only required for COMPLETE

Step 3 — Check git log regardless of report status:
```bash
git log --oneline -3
```
Cross-reference commit hashes in report against actual git log.
If report claims commits exist but git log shows none since pre-call → SILENT FAILURE.

**Claude's verification steps after post-call validation:**
0. PARALLEL AUDIT (always first — before acting on the report):
   Dispatch `backend-auditor` and `verify` agents simultaneously.
   - backend-auditor receives: list of files from "Files Modified" in report.md + task ID.
     It audits every file against all architectural laws, coding standards, hard prohibitions.
   - verify receives: workflow/report.md + task acceptance criteria.
     It checks report fields, acceptance criteria, and cross-checks commit hashes in git log.
   Wait for both to complete. Both must return PASS before proceeding to step 1.
   Either returns FAIL → flag the exact violation. Do not proceed.
1. All gates PASS, commit hashes real, taskFile cleared, no scope violations → PASS
2. Any gate FAIL or constraint violation → task FAILED — inform human with exact details
3. Status: BLOCKED → read blocker, diagnose, inform human (see Unblock section)
4. Silent Failure detected → Silent Failure Protocol (see below)

**Report preservation:**
After verifying Phase A, Claude saves the key Phase A data (task ID, commit hash, gate results)
to a brief internal note before Phase B overwrites `workflow/report.md`.
On completion, Claude presents a combined summary of both phases to the human.

**Unblock during CLI orchestration:**
If Codex writes `Status: BLOCKED` in its report:
- Claude reads the blocker question
- Claude resolves it directly (Small Tweak Rule) OR explains the resolution to the human
- Human relays resolution to Codex for continuation
- Claude does NOT automatically re-invoke the CLI until the blocker is resolved and human confirms
Frontend tasks cannot be BLOCKED in this sense — Claude resolves its own blockers directly.

**Silent Failure Protocol:**
A silent failure occurs when the CLI returns but report.md was not written or not updated.
This means the agent crashed, drifted, or was killed before completing.

On detecting a silent failure, Claude MUST:

1. Run git log to establish what actually happened:
```bash
git log --oneline -5
git status --short frontend/   # or api/ depending on agent
```

2. Inform the human with this exact summary:
   - Which agent was invoked and what task
   - That report.md was not written (silent failure)
   - What git log shows (commits made or not)
   - Recommended action (one of the three below)

3. Recommended actions based on git log:
   - Commits exist, no report → agent completed work but drifted on reporting.
     Safe to re-invoke with instruction: "The task work is done (commit: [hash]).
     Write the report to workflow/report.md only. Do not redo the implementation."
   - No commits, no report → agent failed before making any changes.
     Safe to re-invoke normally — no state was changed.
   - Partial commits exist → do NOT re-invoke automatically.
     Human must review what was committed before deciding next action.

4. Claude does NOT re-invoke the CLI automatically on a silent failure.
   Human must explicitly confirm before Claude retries.

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
- Each task must be independently executable in one session (by Codex for backend, by Claude directly for frontend)
- If a task touches both backend and frontend — split into two tasks (Phase A backend, Phase B frontend)
- Order tasks so dependencies are respected (no task requires output from a future task)

**4. taskFile.md discipline — applies to Codex (backend) tasks only.**
Frontend tasks are executed directly by Claude — no taskFile needed for frontend.
When writing `workflow/taskFile.md` for Codex, follow `workflow/taskFileTemplate.md` exactly.
Set the `Agent` field: `Codex`.
Every task prompt MUST include a `READ FIRST` section listing the exact standards files
Codex must load. Use the table below to select files:

| Task scope | Agent | Standards files to include in READ FIRST |
|---|---|---|
| Backend engine/calculator/service | Codex | MANDATES_1_TO_4, SYSTEM_TOPOLOGY, HIGH_IMPACT_REGISTRY, GATE_SEQUENCE, SKILLS_REGISTRY, WORKFLOW_AND_LAWS, PYTHON_STANDARDS, MEMORY_AND_THREADING |
| team_engine.py modification | Codex | All backend files above + KNOWN_PATTERNS_KIPS |
| Frontend component | Claude (direct) | Claude reads TACTICAL_EXECUTION, UI_IMPLEMENTATION, PERF_RESILIENCE_A11Y_TESTING before executing |
| Both backend + frontend | Phase A → Codex taskFile | Phase B → Claude executes directly |

All backend paths are relative to `docs/guides/`. Example: `docs/guides/coreStandards/MANDATES_1_TO_4.md`
Frontend standards paths: `docs/guides/frontendStandards/TACTICAL_EXECUTION.md` etc.

**5. Report verification.**
First: perform the implementation review defined in Step C5 (read every modified file, verify against acceptance criteria before touching the report).

Then check the report fields:
- All triggered gates are PASS (Codex: gates 1–6; Claude frontend: gates F1–F4)
- All acceptance criteria SATISFIED
- Bouncer post-task matches or improves baseline
- Both commit hashes are real (not NONE)
- PROJECT_CONTEXT.md Section 4 has exactly 5 entries
- workflow/taskFile.md cleared — YES (Codex tasks only; frontend tasks have no taskFile to clear)
- For Claude frontend reports: `Out-of-Scope Files Touched` must be NONE (any other value is a violation)
If all checks pass → give green signal → overwrite `workflow/handoff.md`.

**6. handoff.md rules.**
- Overwrite `workflow/handoff.md` only after giving green signal on a verified report
- Maximum 25 lines of content
- Cover: last task completed, what was achieved, current phase, next task in queue, any known blockers
- Write in plain text — no markdown headers, no bullet nesting

**7. Small Tweak Rule.**
Claude may execute small backend/config changes directly (without writing a taskFile for Codex) when ALL of these are true:
- Touches ≤ 3 files
- Does NOT touch engine, calculator, or service files in `formats/` or `core/`
- Does NOT touch any registered file (`core/data_access.py`, `core/interfaces/team_types.py`, `api/serializers.py`)
- Does NOT require gate validation (no bouncer run needed)
- Examples: config edits, template updates, doc fixes

If any condition above is NOT met → write a task for Codex instead.

**Note:** Frontend work is NOT governed by the Small Tweak Rule. All frontend work — regardless of size — is executed directly by Claude as the Frontend Engineer (no taskFile, no CLI). The Small Tweak Rule only applies to backend/config files.

---

## PART 1: MANDATORY BOOTSTRAP

**→ If you are Claude: follow the Claude Bootstrap below.**
**→ If you are Codex: skip to the Codex Bootstrap section.**

---

### Claude Bootstrap

Execute at the start of every Claude session, in order.

**Step C0 — Load Soul**
Read `.claude/SOUL.md` now. This is the mission grounding document for Project Vantage.
It defines why this project exists, who the operator is, and the standard every decision must meet.
Do this before reading handoff or state. Let the mission anchor the session.

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
- Backend task write → go to Task Write (Step C4)
- Frontend task execute → go to Frontend Execute (Step C4F)
- Report verification (Codex) → go to Verify (Step C5)
- Frontend self-verify → go to Step C5F
- Blocker resolution → diagnose and provide resolution path
- Small tweak (backend/config only) → check Small Tweak Rule (Part 0), execute if eligible

**Step C3 — Plan**
Read the relevant source files for the idea.
Write plan to `workflow/plan.md`. Mark status: DRAFT.
Present plan to human. Wait for approval. Do not proceed to Step C4 without approval.

**Step C4 — Task Write (backend tasks → Codex)**
If tasks.md not yet written: write `workflow/tasks.md` with task breakdown.
Write one task prompt to `workflow/taskFile.md` following `workflow/taskFileTemplate.md`.
Include READ FIRST with exact standards file paths (see table in Part 0 Rule 4).
Confirm with human before handing off to Codex.

**Step C4F — Frontend Execute (Claude executes directly)**
Read the relevant frontend source files before writing any code.
Load the three frontend standards files before starting:
- `docs/guides/frontendStandards/TACTICAL_EXECUTION.md`
- `docs/guides/frontendStandards/UI_IMPLEMENTATION.md`
- `docs/guides/frontendStandards/PERF_RESILIENCE_A11Y_TESTING.md`
Implement the frontend task directly. Follow all standards as if you were Codex.
On completion, run the Frontend Self-Audit Checklist (see Step C5F).
Commit work and write `workflow/report.md` in the Part 7 format (Agent: Claude).

**Step C5 — Review Implementation + Verify Report (Codex tasks)**
Dispatch `backend-auditor` and `verify` agents in parallel. Do not read files yourself first.

  backend-auditor — pass it:
    - List of files from "Files Modified" in workflow/report.md
    - Task ID
    It will read every modified file and audit against all architectural laws (Part 2),
    coding standards (Part 5), hard prohibitions (Part 8), KIP patterns, and registered
    file rules (Part 4). Returns violations with exact file:line references.

  verify — pass it:
    - workflow/report.md
    - Task acceptance criteria (from workflow/taskFile.md or tasks.md)
    It will check acceptance criteria, validate all report fields per Part 0 Rule 5,
    and cross-check commit hashes against git log.

Wait for both agents to return results. Then:
  Both PASS → print: "GREEN SIGNAL — TASK-XXX complete. Proceed to next task."
              Overwrite `workflow/handoff.md` with current context (≤25 lines).
  Either FAILS → list the specific failures from the agent report. Do not give green signal.

**Step C5F — Frontend Self-Audit Checklist (Claude frontend tasks)**
Before marking any frontend task complete, Claude MUST run this checklist:
1. TOKENS — No raw hex, no raw rgba(). All colours use CSS variables from globals.css.
2. ARBITRARY TAILWIND — No `[property:value]` syntax anywhere in any .tsx/.ts file.
3. FONT DISCIPLINE — All numeric data uses `.font-data` / JetBrains Mono. All UI text uses Inter.
4. NO DOMAIN LOGIC — No arithmetic or comparison on cricket data in any React component.
5. URL STATE — All filter values (team, venue, innings) stored in URL search params, not Context.
6. ROUTER — All navigation uses Next.js router.push() or <Link>. No window.history, no hash nav.
7. API WRAPPER — All fetch calls go through lib/api.ts. No bare fetch() in components.
8. ERROR BOUNDARIES — Every renderer output wrapped in Error Boundary. Shell is outside boundary.
9. ARIA — Every icon-only button has aria-label. Result container has aria-live="polite".
10. LAZY LOADING — Renderer components in FunctionRenderer.tsx use React.lazy().
11. PLACEMENT — Components in correct directory (layout/ renderers/ inputs/ common/).
12. TYPESCRIPT — No `any`. All API shapes typed in lib/types.ts with @schema JSDoc.
13. OUT-OF-SCOPE — No files outside frontend/ modified (except doc updates explicitly required).
14. GATES — F1 (lint-sentinel), F2 (paradigm-sentinel), F3 (type-sync-guard), F4 (visual-acceptance) all PASS.
15. VISUAL ACCEPTANCE (F4) — Start the dev server, navigate to every route touched by the task, and screenshot the result. Compare each screenshot side-by-side against the Stitch spec or design reference. Every layout property that the spec defines (grid columns, card borders, spacing, icon rendering, tag pills, hover states) must be visually confirmed in the running browser before this check passes. A passing build or passing TypeScript is not a substitute. If anything does not match the spec → fix it before writing report.md.

All 15 checks MUST PASS before writing workflow/report.md.

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

**Rationale:** Prior incidents with unscoped file deletion and docs/ai/ modification. Treat any violation as a critical incident.

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
Agent: [Codex / Claude]

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
- GATE F4 (visual-acceptance): [TRIGGERED/SKIPPED — frontend scope only] — [PASS/FAIL] — routes checked: [list]
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

*End of AGENTS.md — Version 3.1 — 2026-03-20*
*Source of truth for current project state: docs/ai/SESSION_STATE.md*
*Workflow files: workflow/ directory*
*Standards: docs/guides/coreStandards/ | docs/guides/backendStandards/ | docs/guides/frontendStandards/*
