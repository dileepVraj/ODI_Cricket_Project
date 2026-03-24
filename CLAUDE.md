# CLAUDE.md — Agent Bootstrap v3.3
**Project:** Cricket Algo-Trading Platform | **Root:** `C:\Cricket_Project_Stable\`
**Core Directive:** "Assume data is dirty, boundaries are strict, and trust is zero."

> **If you are Codex:** Read `docs/ai/CODEX_BOOTSTRAP.md` now. That file contains your full bootstrap, all architectural laws, gates, coding standards, report format, and hard prohibitions. Do not proceed without it.

---

## TWO-AGENT ROLES

**Claude** — Planning, Verification & Frontend Execution
Owns `frontend/` (executes directly) + all `workflow/` files. Writes plans, task prompts, and handoff. Invokes Codex for backend tasks via CLI.

**Codex** — Backend Execution
Owns `api/`, `core/`, `formats/`, `scripts/`, `tests/`. Receives work via `workflow/taskFile.md` only.

Workflow files: `workflow/plan.md` | `workflow/tasks.md` | `workflow/taskFile.md` | `workflow/report.md` | `workflow/handoff.md`

---

## WORKFLOW CYCLES

**Frontend only:** IDEA → [Brainstorm] → PLAN → EXECUTE (Claude direct) → VERIFY (C5) → RESET
**Backend only:** IDEA → [Brainstorm] → PLAN → TASK WRITE (C4) → CLI invoke Codex → VERIFY (C5) → RESET
**Full-stack:** Backend phase (Codex) first → Frontend phase (Claude direct) second — default order.

Brainstorm required for new features/pages/overhauls. Skip for bug fixes, minor tweaks, clear specs.
Skill: `core/gen_ai/skills/.system/brainstorm-intake/SKILL.md`

**Invoke Codex (backend tasks only):**
```powershell
codex exec --full-auto -C "C:\Cricket_Project_Stable" "Read CLAUDE.md. Then read workflow/taskFile.md and execute the backend task."
```
Timeout: 1800000ms. Full CLI protocol (pre/post snapshot, silent failure): `docs/ai/CLI_ORCHESTRATION.md`

**Small Tweak Rule** — Claude may edit backend/config directly when ALL true:
<=3 files, not engine/calculator/service, not a registered file (`core/data_access.py`, `core/interfaces/team_types.py`, `api/serializers.py`), no gate validation needed.
Frontend is never governed by this rule — Claude always executes frontend directly.

---

## CLAUDE BOOTSTRAP — run in order every session

**C0** Read `.claude/SOUL.md` first. Mission grounding before everything else.
**C1** `cat workflow/handoff.md` then `cat docs/ai/SESSION_STATE.md`. If handoff empty → ask human.
**C2** Identify request type:
  - New feature / overhaul → C2B then C3
  - Bug fix / tweak / clear spec → C3 directly
  - Backend task write → C4 | Frontend execute → C4F | Verify → C5 | Broken → systematic-debugging skill
**C2B** Invoke `core/gen_ai/skills/.system/brainstorm-intake/SKILL.md`. Confirm spec before writing plan.
**C3** Read relevant files. Write `workflow/plan.md` (DRAFT). Wait for human approval before C4.
**C4** Write `workflow/tasks.md` if needed. Write `workflow/taskFile.md` per `workflow/taskFileTemplate.md`. Include READ FIRST with standards paths. Confirm before invoking Codex.
**C4F** Load frontend standards below. Read relevant source files. Implement directly. Run C5F checklist. Commit. Write `workflow/report.md`. Then dispatch C5.
**C5** Dispatch `verification-agent`: `core/gen_ai/skills/.system/verification-agent/SKILL.md`
  Pass: task ID, scope, files modified, acceptance criteria.
  PASS → update `workflow/handoff.md`. FAIL → fix + re-dispatch (max 3 rounds).

**Frontend standards (load before every C4F):**
- `docs/guides/frontendStandards/TACTICAL_EXECUTION.md`
- `docs/guides/frontendStandards/UI_IMPLEMENTATION.md`
- `docs/guides/frontendStandards/PERF_RESILIENCE_A11Y_TESTING.md`

**C5F — Frontend Self-Audit (all 16 must pass before writing report.md):**
1. TOKENS — CSS variables only, no raw hex/rgba
2. ARBITRARY TAILWIND — No `[property:value]` syntax in any .tsx/.ts
3. FONT DISCIPLINE — Numeric data: `.font-data`/JetBrains Mono. UI text: Inter
4. NO DOMAIN LOGIC — No cricket arithmetic in React components
5. URL STATE — Filters in URL search params, not Context
6. ROUTER — Next.js router.push() or `<Link>` only
7. API WRAPPER — All fetch via `lib/api.ts`, no bare fetch()
8. ERROR BOUNDARIES — Every renderer output wrapped; shell is outside boundary
9. ARIA — Icon-only buttons: aria-label. Result container: aria-live="polite"
10. LAZY LOADING — Renderer components in FunctionRenderer.tsx use React.lazy()
11. PLACEMENT — Components in correct directory (layout/ renderers/ inputs/ common/)
12. TYPESCRIPT — No `any`. API shapes typed in lib/types.ts with @schema JSDoc
13. OUT-OF-SCOPE — No files outside `frontend/` modified (except explicit doc updates)
14. GATES — F1 lint, F2 paradigm, F3 type-sync, F4 visual-acceptance all PASS
15. VISUAL ACCEPTANCE — Dev server running, every touched route screenshotted, compared to spec
16. SRP — Run `wc -l` on every file you touched in `frontend/components/`. If any file exceeds 300 lines, STOP and perform a full SRP analysis before committing: (a) list every distinct responsibility the file holds, (b) extract each into a dedicated file with a clean prop interface, (c) apply the "describe without and" test to every resulting file. Merely moving lines to stay under 300 is a Hard Fail — the split must be structurally justified.

---

## STANDARDS REFERENCE TABLE

| Topic | File |
|---|---|
| Architectural Laws (Laws 1-7) | `docs/guides/coreStandards/MANDATES_1_TO_4.md` |
| Gate Sequence (Gates 1-6, F1-F4) | `docs/guides/coreStandards/GATE_SEQUENCE.md` |
| High-Impact File Registry | `docs/guides/coreStandards/HIGH_IMPACT_REGISTRY.md` |
| System Topology | `docs/guides/coreStandards/SYSTEM_TOPOLOGY.md` |
| Workflow Laws + Definition of Done | `docs/guides/coreStandards/WORKFLOW_AND_LAWS.md` |
| Python Standards + Hard Prohibitions | `docs/guides/backendStandards/PYTHON_STANDARDS.md` |
| Memory & Threading | `docs/guides/backendStandards/MEMORY_AND_THREADING.md` |
| Known Patterns (KIPs) | `docs/guides/backendStandards/KNOWN_PATTERNS_KIPS.md` |
| Report Format + taskFile Template | `workflow/taskFileTemplate.md` |
| CLI Orchestration Protocol | `docs/ai/CLI_ORCHESTRATION.md` |
| Codex Full Bootstrap | `docs/ai/CODEX_BOOTSTRAP.md` |

*Source of truth: `docs/ai/SESSION_STATE.md` | Workflow: `workflow/` | Standards: `docs/guides/`*
