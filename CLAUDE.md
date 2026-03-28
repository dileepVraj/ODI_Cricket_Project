# CLAUDE.md — Architect v5.0
**Project:** Cricket Algo-Trading Platform | **Root:** `C:\Cricket_Project_Stable\`
**Pipeline spec:** `agents/redesign/spec.md` | **Failure modes:** spec.md Section 2

---

## BOOTSTRAP — every session, in order

**B1 — Read state**
```bash
cat agents/workflow/state.json
```
- `active.task_id` is null → idle, ready for new task
- `active.task_id` not null → task was in progress. Read `agents/workflow/reports/<task_id>*.json`.
  Compare `active.pre_call_commit` against `git log --oneline -1`.
  Determine: COMPLETE / BLOCKED / SILENT FAILURE. Follow spec.md Section 2.

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

*Write to state.json before every invocation:*
```json
"active": {
  "task_id": "TASK-XXX",
  "phase": "SOLO | MULTI-PHASE-A | MULTI-PHASE-C",
  "agent": "Codex | Gemini",
  "invoked_at": "<ISO timestamp>",
  "pre_call_commit": "<git log --oneline -1 hash>"
}
```

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
- `taskfile_cleared`: true
- `commit` exists in `git log --oneline -5`
- `violations_delta` ≤ 0

Any condition false → identify failure mode from spec.md Section 2. Do not give green signal.

Step 4 — Implementation spot-check:
Read every file in `files_modified`. Verify implementation matches task intent.
For calculator tasks: trace one field from the Verification Matrix against the actual code.
This is a spot-check — primary QA was the Reviewer subagent.

Step 5 — Green signal:
Update `agents/workflow/state.json`:
```json
{
  "last_completed_task": "TASK-XXX",
  "last_commit": "<commit hash>",
  "gate_baseline_violations": <post_task_violations>,
  "active": { "task_id": null, "phase": null, "agent": null, "invoked_at": null, "pre_call_commit": null },
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
