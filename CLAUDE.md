# CLAUDE.md — Architect v5.0
**Project:** Cricket Algo-Trading Platform | **Root:** `C:\Cricket_Project_Stable\`
**Pipeline spec:** `agents/redesign/spec.md` | **Failure modes:** spec.md Section 2

---

## HARD RULE — COMMUNICATION STYLE (non-negotiable, every session)

The human is non-technical and learning. **Always explain everything in plain, everyday language.**
- No jargon. No technical terms unless unavoidable.
- If a technical term must be used, explain it in one simple sentence right after.
- Think: "explain it to a friend who has never touched a computer."
- This applies to ALL responses — explanations, status updates, errors, everything.
- This rule cannot be overridden by any other instruction in this file.

---

## BOOTSTRAP — every session, in order

**B0 — Read session notes**
```bash
cat agents/sessions/$(ls agents/sessions/ | sort | tail -1)
```
Read the most recent session file from agents/sessions/. Look for the "Next session"
or "Next:" lines to understand what was planned for this session.

**B0a — Pre-read workflow files (mandatory — prevents Write tool hard-block)**
Immediately after reading session notes, read these files every session, no exceptions:
```
agents/workflow/taskFile.md
agents/workflow/state.json      ← (also read in B1, but read here too)
```
The Write tool hard-blocks with an error if a file has not been Read in the same session.
`taskFile.md` is written in B5 — if it is not pre-read here, B5 will fail, trigger a
retry loop, and consume 2× tokens. Pre-reading at bootstrap costs nothing and prevents
this every time. This applies even if the file is empty or does not exist yet — attempt
the read anyway (an error is acceptable; the Write tool only checks that a Read was attempted).

**B1 — Read state**
```bash
cat agents/workflow/state.json
```

**Before reading — schema check:**
- If state.json is missing, empty, or unparseable → read `agents/workflow/state.json.bak`
- If bak also unreadable → inform human: "state.json is unreadable and no backup exists.
  Run `git log --oneline -5` to reconstruct last known state manually. Do not proceed."
- Never silently assume clean state if the file cannot be parsed.
- If file is readable: verify `schema_version == 1`. If wrong or missing → treat as unreadable, go to recovery path above.

**After parsing:**
- `active.task_id` is null → idle, ready for new task
- `active.task_id` not null → **HARD LOCK**. A task is in progress and was not resolved.

**HARD LOCK — what this means:**

BLOCKED (do not do any of these until the lock is released):
- Write taskFile.md
- Invoke Codex or Gemini
- Edit any file in `core/` `api/` `formats/` `frontend/`

ALLOWED while locked:
- Read the existing report (`agents/workflow/reports/<task_id>*.json`)
- Read code files for diagnosis only
- Edit workflow files to resolve a blockage (Small Tweak Rule still applies)
- Present findings and options to the human

**Lock releases via two paths only:**
1. Full B8 post-call validation completes and Step 5 green signal is written to state.json
2. Human explicitly abandons the task → ABANDON PROTOCOL (below)

Until one of these two paths completes, the lock does not lift. "Just move on" is not a path.

**B2 — Classify request**
- New feature / overhaul → B3 (brainstorm) then B4 (plan)
- Bug fix / clear spec → B5 (taskFile) directly
- Frontend with design scope → B6 (designBrief) then B5
- Function guide → B6 (Gemini implements)
- Verify only → B8

**B3 — Brainstorm** *(new features / overhauls only)*
Invoke `core/gen_ai/skills/.system/brainstorm-intake/SKILL.md`. Mandatory for any task
touching a new calculator, engine, endpoint, or major UI overhaul. Not skippable.

**B4 — Plan**
Read relevant source files. Write `agents/workflow/plan.md`. Wait for human approval.
For frontend tasks with design scope: proceed to B6 after approval.

**B5 — TaskFile**
Write `agents/workflow/taskFile.md` per `agents/workflow/taskFileTemplate.md`.
For calculator/engine/service tasks: Verification Matrix must be fully filled before
writing the taskFile. Blank cells = task not ready. Do not assign.

For calculator/engine/service tasks — write assertion script BEFORE taskFile:
  Claude writes `agents/workflow/assertion.py` directly (Write tool — same as writing
  taskFile.md or state.json). This is a Claude action, not a shell command, not Codex.

  Source: the Verification Matrix concrete example column only.
  Do not consult the codebase. Do not read the function being implemented.
  The assertion must encode what the matrix says, not what the code will do.

  Translation: one row → one assert block:
  ```python
  # THROWAWAY — delete after task complete. Written by Claude, run by Codex.
  # Task: <TASK-ID> | Field: <field_name>
  # Matrix row: <concrete input> → <expected output>
  from <module> import <function>
  result = <function>(<concrete_input>)
  assert result["<field>"] == <expected_value>, f"ASSERTION FAILED: expected <expected_value>, got {result['<field>']}"
  print("ASSERTION PASSED:", result)
  ```

  Write the taskFile only after assertion.py is saved.
  Codex does not rewrite assertion.py — if it is missing, Codex blocks.

Confirm with human before invoking.

**B6 — DesignBrief for Gemini**
Write `agents/workflow/designBrief.md`. Must include:
- Feature context and trading significance
- Exact API schema fields (extracted from source — no assumptions)
- Design token reference (globals.css variables)
- Existing component patterns to match
- Mode: design OR guide
Invoke Gemini. Review with human. On approval → extract Stitch HTML for B5 (design mode)
or proceed to B8 (guide mode).

**B7 — Invoke agents**

*Re-read state.json immediately before writing — do not rely on session memory:*
Read `agents/workflow/state.json` fresh from disk right now.
Confirm `active.task_id` is still null. If it is not null — HARD LOCK is active. Do not invoke.
This re-read is mandatory even if B1 confirmed idle earlier in the session.

*Write to state.json before every invocation (follow STATE.JSON WRITE PROTOCOL below):*
```json
"active": {
  "task_id": "TASK-XXX",
  "phase": "SOLO | MULTI-PHASE-A | MULTI-PHASE-C",
  "agent": "Codex | Gemini",
  "invoked_at": "<ISO timestamp>",
  "pre_call_commit": "<git log --oneline -1 hash>",
  "retry_count": 0
}
```
On retry (F2/F3/F7B): increment `retry_count` by 1 before re-invoking. Never reset it.
This persists the retry budget across session boundaries — F8 cannot silently reset the counter.

*Codex:*
```powershell
codex exec -s danger-full-access --output-schema agents/workflow/report-schema.json -C "C:\Cricket_Project_Stable" "Read AGENTS.md. Then read agents/workflow/taskFile.md and execute the task."
```
Timeout: 1800000ms.

*Gemini:*
```bash
gemini -p "Read GEMINI.md. Then read agents/workflow/designBrief.md and execute." --yolo
```

**B8 — Post-call validation**

Step 1 — Silent failure check:
Read `agents/workflow/state.json` active.pre_call_commit. Compare against `git log --oneline -1`.
No new commit + no updated report → F1 (silent failure). Follow spec.md F1 protocol.

Step 2 — Validate report:
Read `agents/workflow/reports/TASK-XXX.json`.
Validate against `agents/workflow/report-schema.json`.
Schema invalid → treat as F1.

Step 3 — Green signal check (ALL must be true):
- `status`: COMPLETE
- All triggered gates: `"status": "PASS"`
- `reviewer.verdict`: PASS
- `reviewer.assertion.match`: true (or null for non-calculator tasks)
- `reviewer.assertion.pre_impl_output`: non-empty and does NOT contain "ASSERTION PASSED"
  (for calculator/engine/service tasks — proves assertion was red before implementation)
- `taskfile_cleared`: true
- `commit` exists in `git log --oneline -5`
- `violations_delta` ≤ 0

Any condition false → identify failure mode from spec.md Section 2. Do not give green signal.

Step 4 — Logic audit (Claude's primary QA responsibility):
The Reviewer subagent verified structure and coverage. Claude verifies correctness.
These are different jobs. Do both, in order.

For calculator / engine / service tasks:
  Read the Verification Matrix in taskFile.md (or the archived plan if taskFile is cleared).
  For EVERY row: trace the formula against the actual code.
  - Find the exact line(s) where this field is computed.
  - Confirm the formula in code matches the formula in the matrix.
  - Confirm the denominator, aggregation level, and empty-data result match.
  If any row cannot be confirmed: flag as logic mismatch. Do not give green signal.

For all tasks:
  Read every file in `files_modified`.
  For each AC: find the specific code that satisfies it and confirm the logic is correct,
  not just that the code exists (the Reviewer already checked existence).
  "The field is returned" is not enough — confirm it is computed correctly.

Step 5 — Green signal:
Update `agents/workflow/state.json`:
```json
{
  "last_completed_task": "TASK-XXX",
  "last_commit": "<commit hash>",
  "gate_baseline_violations": <post_task_violations>,
  "active": { "task_id": null, "phase": null, "agent": null, "invoked_at": null, "pre_call_commit": null, "retry_count": 0 },
  "next": "ready"
}
```
Inform human. Human /clears.

---

## SMALL TWEAK RULE (Claude direct edits)

Claude may edit files directly when ALL true:
- Fix is in `agents/workflow/` files (taskFile, designBrief, scope.json, state.json, plan.md)
  OR pure config/doc files (CLAUDE.md, AGENTS.md, GEMINI.md, soul files)
- NEVER inside `core/` `api/` `formats/` `frontend/` — regardless of how small
- No gate validation needed

This rule resolves F4 (BLOCKED) when the blocker is a workflow file clarification.
For code-level blockers: relay to human. Human answers. Claude updates taskFile. Re-invoke.

---

## ABANDON PROTOCOL

**Triggered by:** explicit human command only — e.g. "abandon TASK-168", "drop this task", "cancel it".
Never triggered by Claude's own judgment.

**Steps:**
1. Read current `agents/workflow/state.json` active block.
2. Write updated state.json:
   - Append to `abandoned_tasks` array:
     ```json
     { "task_id": "TASK-XXX", "abandoned_at": "<ISO timestamp>", "reason": "<human's stated reason or 'no reason given'>" }
     ```
   - Null out active:
     ```json
     "active": { "task_id": null, "phase": null, "agent": null, "invoked_at": null, "pre_call_commit": null, "retry_count": 0 }
     ```
   - Set `"next": "ready"`
3. Inform human: "TASK-XXX recorded as abandoned. Lock released."
4. Proceed to B2 for next request.

**Note:** Abandon is a resolution, not an erasure. The task_id and reason are preserved in
`abandoned_tasks` so the audit trail survives. A task abandoned twice with the same root cause
is a signal the spec needs fixing, not just retrying.

---

## STATE.JSON WRITE PROTOCOL

Every write to `agents/workflow/state.json` — whether active block, green signal, or abandon —
must follow this sequence. No exceptions.

**Step 1 — Backup current state:**
Before writing anything, copy the current contents of state.json to `state.json.bak`:
Read state.json → write identical contents to `agents/workflow/state.json.bak`.
If state.json does not exist yet (first run) → skip backup, proceed to write.

**Step 2 — Write new state:**
Write the updated state.json with the full file contents (not a partial patch).
Always include all fields. Never write a partial JSON object.

**Step 3 — Verify write:**
Read state.json back immediately after writing.
Confirm it parses as valid JSON and `schema_version` is present.
If verification fails → restore from state.json.bak and inform human.

---

## MULTI-PHASE SEQUENCING

Default: Backend (Codex) → Design (Gemini, if needed) → Frontend (Codex).
HARD RULE: No phase starts before previous phase is verified green.

Phase A report: `agents/workflow/reports/TASK-XXX-phase-A.json`
Phase C report: `agents/workflow/reports/TASK-XXX-phase-C.json`

---

## STANDARDS REFERENCE TABLE

**Pipeline & Architecture**
| Topic | File |
|---|---|
| Full pipeline spec (all decisions, all sessions) | `agents/redesign/spec.md` |
| Pipeline guarantees (G1–G10) | `agents/redesign/spec.md` Section 1 |
| Failure modes + escalation paths (F1–F8) | `agents/redesign/spec.md` Section 2 |
| Agent capabilities + MCP servers | `agents/redesign/spec.md` Section 0 |
| Verification & gate layer | `agents/redesign/spec.md` Section 4 |
| State + handoff mechanism | `agents/redesign/spec.md` Section 5 |
| Session journal (decisions made per session) | `agents/redesign/journal.md` |

**Workflow Files**
| Topic | File |
|---|---|
| TaskFile template | `agents/workflow/taskFileTemplate.md` |
| Session state (replaces handoff.md) | `agents/workflow/state.json` |
| Report JSON schema | `agents/workflow/report-schema.json` |
| Completed task reports | `agents/workflow/reports/` |
| DesignBrief template | `agents/workflow/designBrief.md` |

**Codex Skills**
| Topic | File |
|---|---|
| Pre-task setup (baseline, scope, assertion) | `agents/skills/codex/pre-task.md` |
| Reviewer subagent (independent AC check) | `agents/skills/codex/reviewer.md` |
| Commit + structured report | `agents/skills/codex/commit-report.md` |
| Scope enforcement pre-commit hook | `agents/skills/codex/scope-guard.md` |

**Gemini Skills**
| Topic | File |
|---|---|
| Full-codebase consistency audit | `agents/skills/gemini/consistency-audit.md` |
| Persist approved design decisions | `agents/skills/gemini/save-design-decisions.md` |
| Guide page quality check | `agents/skills/gemini/guide-quality.md` |

**Core Standards (load per task scope)**
| Topic | File |
|---|---|
| Architectural Laws (Mandates 1–4) | `docs/guides/coreStandards/MANDATES_1_TO_4.md` |
| Gate sequence scripts + paths | `docs/guides/coreStandards/GATE_SEQUENCE.md` |
| High-impact file registry | `docs/guides/coreStandards/HIGH_IMPACT_REGISTRY.md` |
| System topology (layer map) | `docs/guides/coreStandards/SYSTEM_TOPOLOGY.md` |
| Workflow laws + Definition of Done | `docs/guides/coreStandards/WORKFLOW_AND_LAWS.md` |
| Skills registry (gate script paths) | `docs/guides/coreStandards/SKILLS_REGISTRY.md` |

**Backend Standards**
| Topic | File |
|---|---|
| Python standards + hard prohibitions | `docs/guides/backendStandards/PYTHON_STANDARDS.md` |
| Memory & threading rules | `docs/guides/backendStandards/MEMORY_AND_THREADING.md` |
| Known patterns (KIPs) | `docs/guides/backendStandards/KNOWN_PATTERNS_KIPS.md` |

**Frontend Standards**
| Topic | File |
|---|---|
| Frontend execution protocol | `docs/guides/frontendStandards/TACTICAL_EXECUTION.md` |
| UI implementation standards | `docs/guides/frontendStandards/UI_IMPLEMENTATION.md` |
| Perf / accessibility / testing | `docs/guides/frontendStandards/PERF_RESILIENCE_A11Y_TESTING.md` |

**Agent Souls (read when grounding a decision)**
| Topic | File |
|---|---|
| Architect soul | `agents/souls/architect.md` |
| Executor soul | `agents/souls/executor.md` |
| Designer soul | `agents/souls/designer.md` |
