# PIPELINE.md — Three-Agent Assembly Line
**Project:** Cricket Algo-Trading Platform | **Version:** 4.0 | **Updated:** 2026-03-26
**Authoritative reference for the three-agent pipeline. CLAUDE.md governs when conflicts arise.**

---

## THE THREE AGENTS

| Agent | Model | Role | Owns |
|---|---|---|---|
| **Claude (Architect)** | claude-sonnet-4-6 | Plans, briefs, verifies | `workflow/` files — zero code execution |
| **Codex (Executor)** | configured model | Full-stack implementation | `api/` `core/` `formats/` `scripts/` `tests/` `frontend/` |
| **Gemini (Designer)** | gemini-3-flash | UI design + guide pages | Stitch designs + `frontend/app/docs/` only |

**Human touchpoints:** Bring idea → approve plan → approve design (when triggered) → receive result.
Everything else is automated.

**Stitch access:** Gemini owns Stitch. Gemini creates designs via `@davideast/stitch-mcp`, extracts screen HTML, reports back to Claude.
Codex receives the HTML reference in taskFile.md — Codex does not need Stitch API access.

---

## FLOW 1 — BACKEND-ONLY TASK

```
Human brings idea
    │
    ▼
Claude reads agents/workflow/handoff.md + relevant source files
Claude writes agents/workflow/plan.md ──► Human approves
    │
    ▼
Claude writes agents/workflow/taskFile.md  [Agent: Codex | Orchestration: SOLO]
Claude: pre-call snapshot of agents/workflow/report.md timestamp
Claude: invokes Codex via CLI (30 min timeout)
    │
    ▼
Codex executes ──► runs backend gates ──► commits ──► writes agents/workflow/report.md
    │
    ▼
Claude: post-call validation (3 steps — see ARCHITECT.md)
Claude: implementation review (reads every modified file vs ACs)
    │
    ├── PASS    ──► Claude updates agents/workflow/handoff.md ──► informs human ──► /clear
    ├── FAILED  ──► Claude flags exact failure ──► human decides
    ├── BLOCKED ──► Claude diagnoses ──► resolves or explains ──► human relays to Codex
    └── SILENT  ──► Claude checks git log ──► informs human ──► human confirms retry
```

---

## FLOW 2 — FRONTEND TASK WITH DESIGN

```
Human brings idea
    │
    ▼
Claude reads handoff + relevant frontend source + API schema for the feature
Claude writes agents/workflow/plan.md ──► Human approves
    │
    ▼
━━━━━━━━━━━━━  DESIGN PHASE — Gemini  ━━━━━━━━━━━━━
Claude extracts exact API response fields (no assumptions)
Claude writes agents/workflow/designBrief.md with schema + design tokens + constraints
Claude invokes Gemini via CLI
    │
    ▼
Gemini reads designBrief.md ──► creates Stitch-aligned designs ──► reports back
Claude + Human review design
    │
    ├── APPROVED ──► Gemini extracts Stitch screen HTML ──► reports to Claude ──► proceed to implementation
    └── REVISION ──► Claude updates designBrief.md ──► re-invoke Gemini
    │
    ▼
━━━━━━━━━━━━━  IMPLEMENTATION PHASE — Codex  ━━━━━━━━━━━━━
Claude writes agents/workflow/taskFile.md  [includes Stitch HTML from Gemini]
Claude: pre-call snapshot ──► invokes Codex via CLI
    │
    ▼
Codex implements exact design ──► runs frontend gates ──► commits ──► writes report
    │
    ▼
Claude: post-call validation + implementation review
    │
    ├── PASS    ──► Claude updates handoff.md ──► informs human ──► /clear
    └── FAILED  ──► Claude flags exact failure
```

---

## FLOW 3 — FULL-STACK TASK

Default sequence: Backend phase (Codex) → Design phase (Gemini, if UI changes) → Frontend phase (Codex).

```
Human brings idea
    │
    ▼
Claude writes plan.md (split: Phase A backend + optional Phase B design + Phase C frontend)
──► Human approves
    │
    ▼
━━━━━━━━  PHASE A — Codex (backend)  ━━━━━━━━
Claude writes taskFile.md  [Orchestration: MULTI-PHASE-A]
Claude invokes Codex ──► Codex executes ──► writes report
Claude validates Phase A. FAIL → STOP. Do NOT proceed.
    │
    ▼
━━━━━━━━  PHASE B — Gemini (design, if UI scope)  ━━━━━━━━
Claude writes designBrief.md with Phase A's new schema fields
Claude invokes Gemini ──► Gemini designs ──► Claude + Human approve
    │
    ▼
━━━━━━━━  PHASE C — Codex (frontend)  ━━━━━━━━
Claude writes taskFile.md  [Orchestration: MULTI-PHASE-C]
Claude invokes Codex ──► Codex implements exact design ──► writes report
Claude validates Phase C
    │
    ├── PASS    ──► Claude updates handoff.md ──► combined summary ──► /clear
    └── FAILED  ──► Claude flags and stops
```

**HARD RULE: No phase starts before the previous phase is verified PASS.**

---

## FLOW 4 — FUNCTION GUIDE (Human-triggered)

Gemini both designs AND implements guide pages. Codex is not involved.

```
Human triggers guide for a feature
    │
    ▼
Claude writes agents/workflow/designBrief.md
  - Feature summary and "why" narrative
  - API schema fields the guide will explain
  - Existing guide page structure (if any) for consistency
  - Acceptance criteria
Claude invokes Gemini via CLI
    │
    ▼
Gemini reads designBrief.md
Gemini designs guide structure ──► Claude + Human approve
Gemini implements directly in frontend/app/docs/
Gemini runs frontend gates (F1, F2, F3)
Gemini writes agents/workflow/report.md
    │
    ▼
Claude: implementation review + report validation
    │
    ├── PASS    ──► Claude updates handoff.md ──► informs human ──► /clear
    └── FAILED  ──► Claude flags exact failure ──► Gemini fixes
```

---

## WHEN GEMINI ACTIVATES

| Trigger | Flow |
|---|---|
| New page or major UI overhaul | Flow 2 or Flow 3 Phase B |
| Function guide page | Flow 4 |
| Design-scope: new data visualisation, new renderer layout | Flow 2 |

**Gemini does NOT activate for:** bug fixes, small component tweaks, data display adjustments, backend tasks.

---

## CLI COMMANDS

**Invoke Codex (backend + frontend tasks):**
```powershell
codex exec -s danger-full-access --output-schema agents/workflow/report-schema.json -C "C:\Cricket_Project_Stable" "Read AGENTS.md. Then read agents/workflow/taskFile.md and execute the task."
```
Timeout: **1800000ms**. Always set this on the Bash tool call.

**Invoke Gemini (design + guide tasks):**
```bash
gemini -p "Read GEMINI.md. Then read agents/workflow/designBrief.md and execute." --yolo
```

---

## WORKFLOW FILES REFERENCE

| File | Written by | When | Max size |
|---|---|---|---|
| `agents/workflow/plan.md` | Claude | After human brings idea — DRAFT until approved | — |
| `agents/workflow/taskFile.md` | Claude | One task at a time — Codex only | — |
| `agents/workflow/designBrief.md` | Claude | When design or guide phase needed — Gemini only | — |
| `agents/workflow/report.md` | Codex or Gemini | On completion or block — overwritten per phase | — |
| `agents/workflow/handoff.md` | Claude | After green signal on verified report | 25 lines |
| `agents/workflow/tasks.md` | Claude | Task breakdown for multi-phase work | — |

---

## GATE REFERENCE

**Codex (backend) gates:**
| Gate | Trigger |
|---|---|
| GATE 1 — boundary-sentinel | Any `core/` file modified |
| GATE 2 — duckdb-lint-ops | Any `calculators/` `engines/` `services/` file modified |
| GATE 3 — manifest-contract-verifier | Any `manifest.py` or engine file modified |
| GATE 4 — serialization-guard | Any `api/serializers.py` or engine return type modified |
| GATE 5 — paradigm-sentinel | Always |
| GATE 6 — compliance_bouncer | Always — last |

**Codex (frontend) gates:**
| Gate | Trigger |
|---|---|
| GATE F1 — frontend-lint-sentinel | Any `.tsx` or `.ts` modified |
| GATE F2 — frontend-paradigm-sentinel | Always after F1 |
| GATE F3 — frontend-type-sync-guard | Always |

**Gemini (guide implementation) gates:** F1, F2, F3 — same as Codex frontend.

---

## TROUBLESHOOTING

| Symptom | Likely cause | Action |
|---|---|---|
| CLI returns instantly | Agent not on PATH | `codex --version` or `gemini --version` |
| report.md not updated | Silent failure | Run git log — follow Silent Failure Protocol in ARCHITECT.md |
| BLOCKED in report | Scope unclear in taskFile | Read blocker question, Claude resolves or relays to human |
| Gate FAIL | Standard violated | Read gate output, locate specific rule violation |
| Phase C fails after Phase A passed | Phase A introduced breaking API change | Check Phase A commits, Claude adapts taskFile |

*Governing law: CLAUDE.md + GEMINI.md + AGENTS.md. This file is the pipeline reference.*
