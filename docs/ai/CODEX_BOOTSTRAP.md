# CODEX_BOOTSTRAP.md — Codex Agent Full Reference
**Version:** 3.3 | **Project:** Cricket Algo-Trading Platform | **Root:** `C:\Cricket_Project_Stable\`
**Core Directive:** "Assume data is dirty, boundaries are strict, and trust is zero."

---

## CODEX BOOTSTRAP — Execute in order before any code change

**Step 0 — Check for workflow/taskFile.md**
```bash
cat workflow/taskFile.md
```
If it exists and is non-empty:
- Stop all other bootstrap steps
- Read `docs/ai/TASK_RUNNER.md`
- Execute the task in `workflow/taskFile.md`
- Do not proceed with Steps 1–4 below

If empty or missing → continue with Step 1.

**Step 1 — Load Context (context-loader skill)**
Invoke `core/gen_ai/skills/guides/backend/context-loader/context-loader.md`.
Follow every step. Do not proceed until it outputs: `CONTEXT LOADED — [scope] task`
If SESSION_STATE.md is missing or unreadable — hard stop. Report and do not proceed.

**Step 2 — Load Scoped Standards Files**

MANDATORY (every task):
- `docs/guides/coreStandards/MANDATES_1_TO_4.md`
- `docs/guides/coreStandards/SYSTEM_TOPOLOGY.md`
- `docs/guides/coreStandards/HIGH_IMPACT_REGISTRY.md`
- `docs/guides/coreStandards/GATE_SEQUENCE.md`
- `docs/guides/coreStandards/SKILLS_REGISTRY.md`

FOR ALL TASKS MODIFYING EXISTING CODE (add):
- `docs/guides/coreStandards/WORKFLOW_AND_LAWS.md`

FOR BACKEND TASKS (add):
- `docs/guides/backendStandards/PYTHON_STANDARDS.md`
- `docs/guides/backendStandards/MEMORY_AND_THREADING.md`

CONDITIONAL:
- `docs/guides/backendStandards/KNOWN_PATTERNS_KIPS.md` — only when task touches `formats/odi/engines/team_engine.py`
- `docs/guides/coreStandards/MANDATES_5_6_LIVE.md` — only when task touches `core/live/` or `api/live/` [DORMANT]

Do NOT read `ENGINEERING_STANDARDS_CORE.md` (human architect file).
Do NOT read or update `docs/ai/AI_MEMORY.md` (deprecated).

**Step 3 — Run Baseline Bouncer**
```bash
python core/utils/compliance_bouncer.py --root .
```
Record output as before-snapshot. Hard stop if command cannot run.

**Step 4 — Classify the Task**
Before writing any code, classify every file the task will touch using the layer role table in
`docs/guides/coreStandards/MANDATES_1_TO_4.md`. This determines which mandates apply.

---

## ARCHITECTURAL LAWS — Immovable. No task or deadline overrides them.

**Law 1 — Functional Core, Imperative Shell**
Domain Core files (engines, calculators, services) are pure functions. During execution they MUST NOT:
read/write database, read/write files, make network requests, access/modify globals, produce side-channel output.
All data arrives as parameters. All results returned explicitly.

**Law 2 — Hexagonal Purity (The Air Gap)**
Domain Core files have zero knowledge of infrastructure.
Forbidden imports in Domain Core: `duckdb`, `fastapi`, `sqlalchemy`, `requests`, `os`, `pathlib`.
Data flows one direction only:
```
Infrastructure (api/, scripts/, frontend/)
    ↓ DataFrames and validated inputs
Domain Core (engines, calculators, services)
    ↓ TypedDicts and primitives
Infrastructure (api/, scripts/, frontend/)
```
Any infrastructure import in Domain Core = Critical Boundary Violation. Hard stop.

**Law 3 — Data-Oriented Design (DOD)**
Every operation on more than one row MUST be vectorized. NumPy or Pandas array operations only.
`.iterrows()` is a hard fail. `.itertuples()` is a hard fail.
Hardware: Ryzen 5 3500U, ~4 GB usable RAM. Scalar loops are 10–100x slower.

**Law 4 — Single Responsibility**
Every file has one primary job. One layer role.

**Law 5 — Typed Truth**
Every function MUST have complete type annotations.
`Any` is forbidden. `object` in signatures is forbidden. `Dict[str, Any]` is forbidden.
Use TypedDicts from `core/interfaces/team_types.py` or Pydantic models.

**Law 6 — Visual Silence (Presentation Purity)**
Engines and services return raw primitives: float, int, bool, None, TypedDict.
No labels, no emoji, no UI strings in the engine layer.
Labeling belongs exclusively in `api/serializers.py` or the frontend.

**Law 7 — Zero-Literal Law**
No hardcoded team names, venue names, player names, colors, or match limits in engine code.
All constants registered in `manifest.py` or config registries. Never `if venue == "Wankhede"`.

---

## SIX-GATE SENTINEL SEQUENCE — All triggered gates must pass. None are optional.

| Gate | Skill Path | Trigger Condition |
|------|-----------|-------------------|
| GATE 1 | `core/gen_ai/skills/validators/backend/boundary-sentinel/` | Any modification to `core/` files |
| GATE 2 | `core/gen_ai/skills/guides/backend/duckdb-lint-ops/` | Any modification to `calculators/`, `engines/`, `services/` |
| GATE 3 | `core/gen_ai/skills/validators/backend/manifest-contract-verifier/` | Any modification to `manifest.py` or engine files in `formats/` |
| GATE 4 | `core/gen_ai/skills/validators/backend/serialization-guard/` | Any modification to `api/serializers.py` or engine return types |
| GATE 5 | `core/gen_ai/skills/validators/backend/paradigm-sentinel/` | Always — after all primary gates pass |
| GATE 6 | `python core/utils/compliance_bouncer.py --root .` | Always — last step before task complete |

Critical path rule: Gate 2 (duckdb-lint-ops) is in `guides/` not `validators/`. Wrong path = hard fail.
Dormant: `core/gen_ai/skills/validators/backend/event-state-linter/` — activates when `core/live/` is created in Phase 12.

Hard stop condition: Any gate fails → stop. Report gate name, path used, exact output. Failed gate = incomplete task.

---

## HIGH-IMPACT FILE REGISTRY

| File | Risk Level | Why |
|------|-----------|-----|
| `core/data_access.py` | CRITICAL | Every engine and service depends on it. Silent changes corrupt all downstream outputs. |
| `core/interfaces/team_types.py` | HIGH | Load-bearing type contract. Removing/renaming a TypedDict key breaks engines, services, serializers simultaneously. |
| `api/serializers.py` | HIGH | Handles every API response and edge case. Changes affect all API output. |

**The Rule:** If the task prompt explicitly instructs modification → proceed.
If the task requires touching a registered file but the prompt does not say so:
1. Stop. State which file and why.
2. Produce an impact trace — list every file that imports from or depends on it.
3. Wait for explicit confirmation before proceeding.

---

## CODING STANDARDS

**Zero-Destruction Policy**
- Never output `# ... existing logic` or `# ... rest stays same`. Rewrite the full function.
- Never delete existing imports, helpers, or logic unless explicitly replacing with a verified alternative.
- Every untargeted feature must remain 100% intact.

**Zero Hallucinations**
- Never guess imports, file paths, variable names, or column names.
- If you do not know, read the file first.
- Never assume a column exists in a DataFrame. Always check `if col in df.columns`.

**Safe Math**
- `a / b` must always be `a / b if b > 0 else 0`.
- Cricket data has edge cases: DNB, rain, abandoned matches, missing innings. Assume dirty data always.

**Crash Early, Crash Loud**
- Catch specific exceptions. Never `except Exception: pass`.
- Fail loudly at the boundary. Never swallow errors silently in engine paths.

**Atomic Updates**
- Modifying a single function: output only that function unless instructed otherwise.
- Modifying multiple files: ensure they are updated in a single consistent state.

**Filesystem Integrity Rules**

RULE 1 — Never delete, move, or rename files outside task scope.

RULE 2 — Banned git commands (no exceptions):
`git clean`, `git reset --hard`, `git rm`, `git checkout -- .`, `git checkout <path>`,
`git restore` (except to undo your own changes), `git status` with no path argument.

RULE 3 — git status must be scoped:
```bash
git status --short <target_directory>
```
Never run `git status` or `git status --short .` without an explicit named directory.

RULE 4 — Act on what git status shows. If any file modified/deleted not in task scope → CRITICAL DEVIATION. Stop immediately.

RULE 5 — `docs/ai/` is human-write-only by default. Never create/modify/delete any file under `docs/ai/`
unless the task prompt contains explicit instruction naming the specific file and change permitted.

RULE 6 — Missing reference files = hard stop. Output CRITICAL BLOCKER and halt.

RULE 7 — No speculative filesystem scans across the full project.

---

## DEFINITION OF DONE — Task is NOT complete until all are true:

1. All triggered gate results recorded (gate name, path, pass/fail).
2. Gate 5 (paradigm-sentinel) result recorded.
3. Gate 6 (compliance_bouncer) output is `PASS: 100% compliance`.
4. Post-change bouncer matches or improves baseline.
5. No registered file modified without explicit instruction or stop-state-trace-confirm.
6. Report written to `workflow/report.md` in required format (see below).
7. PROJECT_CONTEXT.md Section 4 contains exactly 5 entries (rolling window enforced).
8. Terminal summary printed with task status and report location.

---

## REPORT FORMAT — Write to workflow/report.md exactly as shown. No deviations.

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

## HARD PROHIBITIONS — Any occurrence is an immediate hard fail.

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
- Reading or updating `docs/ai/AI_MEMORY.md` — deprecated
- Using `core/gen_ai/skills/validators/backend/duckdb-lint-ops/` — wrong path, Gate 2 is in `guides/backend/`
- Running `git commit --no-verify` — bouncer is not optional
- Skipping context-loader invocation at session start
- Running `git status --short .` — banned. Must name explicit directory.
- Report written to terminal only — must be written to `workflow/report.md`
- Report format deviating from the template above

**KIP-001:** Do NOT modify or remove the constructor discard pattern
`_ = (match_df, phase_df, dal)` in `formats/odi/engines/team_engine.py` line 26.
Intentional stateless design. See `docs/guides/backendStandards/KNOWN_PATTERNS_KIPS.md`.

**KIP-002:** Do NOT add a duplicate definition of `_context_match_df` to the upper section
of `formats/odi/engines/team_engine.py`. Method is defined in the lower section of the same file.
See `docs/guides/backendStandards/KNOWN_PATTERNS_KIPS.md`.
