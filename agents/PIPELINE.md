# PIPELINE.md -- Universal Agent Pipeline
**Project:** Cricket Algo-Trading Platform | **Version:** 5.0 | **Updated:** 2026-04-19
**CLAUDE.md governs when conflicts arise.**

---

## THE THREE AGENTS

| Agent | Model | Capabilities |
|---|---|---|
| **Claude** | claude-sonnet-4-6 | Plans, executes directly, verifies, and updates state |
| **Codex** | configured model | Executes any task -- backend, frontend, design |
| **Gemini** | gemini-3-flash | Executes any task -- backend, frontend, design |

**All three agents share the same execution standard: `AGENTS.md`.**
Any agent can execute any task. Any agent can continue work left unfinished by another.

**Human touchpoints:** Bring idea -> approve plan -> receive result.

---

## STANDARD FLOW -- Any Task

```
Human brings idea
    |
    v
Claude reads source files + state
Claude writes agents/workflow/taskFile.md
Claude: pre-call snapshot
    |
    v
Claude OR Codex OR Gemini reads AGENTS.md + taskFile.md
Executes task (backend, frontend, design, or full-stack)
Runs triggered gates -- commits -- writes report to reports/TASK-XXX.json
    |
    v
Claude validates report
    |
    +-- PASS    --> Claude updates state.json + handoff.md --> informs human
    +-- BLOCKED --> Claude diagnoses --> any agent continues (see Continuation Flow)
    +-- SILENT  --> Claude checks git log --> informs human
```

---

## CONTINUATION FLOW -- Any Agent Picks Up Blocked Work

When an agent is blocked, any other agent (or the same agent) can continue:

```
Agent A writes BLOCKED report to agents/workflow/reports/TASK-XXX-blocked.json
taskFile.md is NOT cleared when blocked
    |
    v
Agent B (any agent) reads:
  1. agents/workflow/taskFile.md                        <- original task spec
  2. agents/workflow/reports/TASK-XXX-blocked.json      <- what was tried + the blocker
  3. git diff HEAD                                       <- uncommitted changes from Agent A
  4. git log --oneline -5                                <- commits already made by Agent A
    |
    v
Agent B resolves the blocker and completes remaining work
Runs all triggered gates -- commits remaining changes -- writes COMPLETE report
    |
    v
Claude validates as normal
```

**Key rule:** The taskFile is the universal work order. It is never cleared until a COMPLETE
report is written. Any executor who reads the taskFile + blocked report can continue the work.

---

## DESIGN IN THE NEW MODEL

Design is a task type, not a separate phase or a separate agent's job.
When a task requires new UI screens:

1. **Claude embeds design context directly in the taskFile:**
   - Describe the screens to build and the trading decision they serve
   - List the exact API schema fields to display (extract from source, no assumptions)
   - Include Vantage design token reference and existing component patterns to match
   - State whether human approval of the design is needed before implementation begins

2. **The executor (any agent with Stitch MCP) creates the design and implements it:**
   - Uses Stitch to create and iterate on designs
   - Extracts screen HTML from Stitch
   - Implements the frontend code from the approved design
   - Runs frontend gates (F1, F2, F3) as normal

3. **If human design approval is required before writing code:**
   - The taskFile states: "DESIGN APPROVAL REQUIRED -- produce design output first, then wait"
   - The executor creates the design and writes a design-only report
   - Claude and human review -- on approval, the executor continues with implementation

No separate designBrief.md file is needed. Design context lives in the taskFile.

---

## WHO TO INVOKE

All three agents share the same execution standard and can handle any task.

**Claude (direct execution in this conversation):**
Claude reads AGENTS.md and taskFile.md and executes the task directly in the session.
No CLI command needed.

**Codex (CLI invocation):**
```powershell
codex exec -s danger-full-access --output-schema agents/workflow/report-schema.json -C "C:\Cricket_Project_Stable" "Read AGENTS.md. Then read agents/workflow/taskFile.md and execute the task."
```
Timeout: **1800000ms**. Always set this on the Bash tool call.

**Gemini (CLI invocation):**
```bash
gemini -p "Read AGENTS.md. Then read agents/workflow/taskFile.md and execute the task." --yolo
```

---

## WORKFLOW FILES REFERENCE

| File | Written by | When |
|---|---|---|
| `agents/workflow/taskFile.md` | Claude | One task at a time -- any executor reads and executes it |
| `agents/workflow/reports/TASK-XXX.json` | Any executor | On completion |
| `agents/workflow/reports/TASK-XXX-blocked.json` | Any executor | When blocked -- taskFile is NOT cleared |
| `agents/workflow/handoff.md` | Claude | After green signal on a verified report |
| `agents/workflow/state.json` | Claude only | After verified completion -- not during execution |

---

## GATE REFERENCE

**Backend gates (all executors, backend tasks):**
| Gate | Trigger |
|---|---|
| GATE 1 -- boundary-sentinel | Any `core/` file modified |
| GATE 2 -- duckdb-lint-ops | Any `calculators/` `engines/` `services/` file modified |
| GATE 3 -- manifest-contract-verifier | Any `manifest.py` or engine file modified |
| GATE 4 -- serialization-guard | Any `api/serializers.py` or engine return type modified |
| GATE 5 -- paradigm-sentinel | Always |
| GATE 6 -- compliance_bouncer | Always -- last |

**Frontend gates (all executors, frontend tasks):**
| Gate | Trigger |
|---|---|
| GATE F1 -- frontend-lint-sentinel | Any `.tsx` or `.ts` modified |
| GATE F2 -- frontend-paradigm-sentinel | Always after F1 |
| GATE F3 -- frontend-type-sync-guard | Always |

---

## TROUBLESHOOTING

| Symptom | Likely cause | Action |
|---|---|---|
| CLI returns instantly | Agent not on PATH | `codex --version` or `gemini --version` |
| Report not written | Silent failure | Run git log -- follow Silent Failure Protocol in CLAUDE.md |
| BLOCKED in report | Scope unclear or file missing | Read blocker question, Claude resolves, any agent continues |
| Gate FAIL | Standard violated | Read gate output, locate specific rule violation |
| Agent A blocked, Agent B continuing | Normal continuation | Agent B reads taskFile + blocked report + git diff |

*Governing law: CLAUDE.md + AGENTS.md. This file is the pipeline reference.*
