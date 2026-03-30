# EXECUTOR.md — Codex Full Operational Reference
**Version:** 4.0 | **Updated:** 2026-03-26
**Read by:** Codex (Executor) during task execution. Governs all backend and frontend tasks.

---

## BOOTSTRAP SEQUENCE

**E0 — Check taskFile**
```bash
cat agents/workflow/taskFile.md
```
Non-empty → stop all other steps. Execute the task. Do not proceed to E1.
Empty or missing → continue with E1.

**E1 — Soul**
Read `agents/souls/executor.md`. Ground every decision before touching code.

**E2 — Load scoped standards**

MANDATORY (every task):
- `docs/guides/coreStandards/MANDATES_1_TO_4.md`
- `docs/guides/coreStandards/SYSTEM_TOPOLOGY.md`
- `docs/guides/coreStandards/HIGH_IMPACT_REGISTRY.md`
- `docs/guides/coreStandards/GATE_SEQUENCE.md`
- `docs/guides/coreStandards/SKILLS_REGISTRY.md`

FOR ALL TASKS MODIFYING EXISTING CODE:
- `docs/guides/coreStandards/WORKFLOW_AND_LAWS.md`

FOR BACKEND TASKS:
- `docs/guides/backendStandards/PYTHON_STANDARDS.md`
- `docs/guides/backendStandards/MEMORY_AND_THREADING.md`

FOR FRONTEND TASKS:
- `docs/guides/frontendStandards/TACTICAL_EXECUTION.md`
- `docs/guides/frontendStandards/UI_IMPLEMENTATION.md`
- `docs/guides/frontendStandards/PERF_RESILIENCE_A11Y_TESTING.md`

CONDITIONAL:
- `docs/guides/backendStandards/KNOWN_PATTERNS_KIPS.md` — only when touching `formats/odi/engines/team_engine.py`
- `docs/guides/coreStandards/MANDATES_5_6_LIVE.md` — only when touching `core/live/` or `api/live/` [DORMANT — activates Phase 12]

**E3 — Run baseline bouncer**
```bash
python core/utils/compliance_bouncer.py --root .
```
Record output as before-snapshot. Hard stop if command cannot run.

**E4 — Classify the task**
Classify every file the task will touch using the layer role table in MANDATES_1_TO_4.md.
This determines which mandates apply. Do not skip this step.

---

## TASK EXECUTION PROTOCOL

### Phase 1 — Read and confirm scope
Read `agents/workflow/taskFile.md` in full.
Read every file listed in FILES IN SCOPE before writing any code.
If task scope is unclear or files are missing → write BLOCKED report immediately.

For calculator / engine / service tasks: read the VERIFICATION MATRIX section of the taskFile.
If the matrix is missing or has blank cells → write BLOCKED report immediately. Do not implement.
The matrix is your contract. You build exactly what it defines.

### Phase 2 — Implement
Follow TASK DESCRIPTION and ACCEPTANCE CRITERIA exactly.
For frontend tasks: use the embedded Stitch screen HTML in TASK PROMPT as your reference.
Implement the design exactly — no improvisation, no layout changes, no "improvements."

For calculator / engine / service tasks: implement each field exactly as the Verification Matrix defines it.
After implementing each function, trace every matrix row against your implementation — confirm the formula, the aggregation level, the denominator, and the concrete example produce the correct output.
If any row does not match → fix the implementation before moving on. Do not defer verification to Claude.

### Phase 3 — Run gates
Run all triggered gates in sequence. Fix failures before proceeding to the next gate.
A task is not complete until all triggered gates PASS.

**Backend gate triggers:**
| Gate | Triggers when |
|---|---|
| GATE 1 — boundary-sentinel | Any `core/` file modified |
| GATE 2 — duckdb-lint-ops | Any `calculators/` `engines/` `services/` modified |
| GATE 3 — manifest-contract-verifier | Any `manifest.py` or engine file modified |
| GATE 4 — serialization-guard | Any `api/serializers.py` or engine return type modified |
| GATE 5 — paradigm-sentinel | Always |
| GATE 6 — compliance_bouncer | Always — last |

**Frontend gate triggers:**
| Gate | Triggers when |
|---|---|
| GATE F1 — frontend-lint-sentinel | Any `.tsx` or `.ts` modified |
| GATE F2 — frontend-paradigm-sentinel | Always after F1 |
| GATE F3 — frontend-type-sync-guard | Always |

### Phase 4 — Frontend Self-Audit (frontend tasks only — all 16 must pass)
1. TOKENS — CSS variables only, no raw hex/rgba
2. ARBITRARY TAILWIND — No `[property:value]` syntax in `.tsx`/`.ts`
3. FONT DISCIPLINE — Numeric data: `.font-data`/JetBrains Mono. UI text: Inter
4. NO DOMAIN LOGIC — No cricket arithmetic in React components
5. URL STATE — Filters in URL search params, not Context
6. ROUTER — Next.js `router.push()` or `<Link>` only
7. API WRAPPER — All fetch via `lib/api.ts`, no bare `fetch()`
8. ERROR BOUNDARIES — Every renderer output wrapped; shell is outside boundary
9. ARIA — Icon-only buttons: `aria-label`. Result container: `aria-live="polite"`
10. LAZY LOADING — Renderer components in `FunctionRenderer.tsx` use `React.lazy()`
11. PLACEMENT — Components in correct directory (`layout/` `renderers/` `inputs/` `common/`)
12. TYPESCRIPT — No `any`. API shapes typed in `lib/types.ts` with `@schema` JSDoc
13. OUT-OF-SCOPE — No files outside `frontend/` modified
14. GATES — F1, F2, F3 all PASS
15. VISUAL ACCEPTANCE — Playwright screenshot taken, compared to Stitch spec
16. SRP — Run `wc -l` on every touched file in `frontend/components/`. >300 lines → full SRP analysis before committing.

### Phase 5 — Commit
```bash
git add [every file modified in task steps]
git commit -m "[task-id]: [one line description]"
```
One commit per task. No doc-update second commit — those files no longer exist.

### Phase 6 — Write report and clear taskFile
Write report to `agents/workflow/report.md`.
Do NOT write report until the commit has a real hash.
Clear `agents/workflow/taskFile.md` — write empty string.
Print to terminal: `[TASK-ID] [STATUS: COMPLETE / BLOCKED]`

---

## TASK CLASSIFICATION TABLE

| Task Type | Gate sequence | Standards loaded |
|---|---|---|
| bug-fix (backend) | 1,2,3,4,5,6 | Backend + core |
| modification (backend) | 1,2,3,4,5,6 | Backend + core |
| new-feature (backend) | 1,2,3,4,5,6 | Backend + core + KIPs if engine |
| refactor (backend) | 5,6 | Backend + core |
| frontend-bug-fix | F1,F2,F3 | Frontend |
| frontend-modification | F1,F2,F3 | Frontend |
| frontend-new-component | F1,F2,F3 | Frontend |
| full-stack | 1-6 then F1-F3 | Backend + Frontend |
| validator-fix | 6 | Core only |
| infra/hook | 6 | Core only |

---

## REPORT FORMAT

Write exactly this format to `agents/workflow/report.md`. No prose. No omissions.

```
TASK REPORT
===========
Task: [one-line description]
Date: [YYYY-MM-DD]
Agent: Codex

Baseline Bouncer: [PASS/FAIL — N violations]
Post-Task Bouncer: [PASS/FAIL — N violations — matches baseline: YES/NO]

Gates Triggered:
- GATE 1 (boundary-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 2 (duckdb-lint-ops): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 3 (manifest-contract-verifier): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 4 (serialization-guard): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE F1 (frontend-lint-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE F2 (frontend-paradigm-sentinel): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE F3 (frontend-type-sync-guard): [TRIGGERED/SKIPPED] — [PASS/FAIL]
- GATE 5 (paradigm-sentinel): TRIGGERED — [PASS/FAIL]
- GATE 6 (compliance_bouncer): TRIGGERED — [PASS/FAIL]

Files Modified: [list]
Registered Files Touched: [list or NONE]
Blockers Hit: [list or NONE]

Acceptance Criteria:
- AC-1: [criterion text] — SATISFIED/FAILED
- AC-2: [criterion text] — SATISFIED/FAILED

Disk Verify:
- [filepath]: [line count] lines — key markers present YES/NO

Verification Matrix: [N/A — not a calculator/engine task | VERIFIED — all N rows confirmed | BLOCKED — row [X] did not match]

Rollback Used: YES/NO
agents/workflow/taskFile.md Cleared: YES — must be YES before COMPLETE

Commit: [hash] — must be a real hash, not NONE

Status: [COMPLETE / BLOCKED — reason]
```

---

## MCP SERVERS AVAILABLE

| Server | Purpose |
|---|---|
| `filesystem` | Read/write `C:\Cricket_Project_Stable` |
| `context7` | Up-to-date library docs |
| `playwright` | Visual acceptance screenshots |
| `sequential-thinking` | Structured multi-step reasoning |
| `jcodemunch` | Code exploration and symbol search across the codebase |
| `duckdb` | Query `formats/odi/data/odi.duckdb` directly |
| `cricket` | Live cricket domain context during implementation |
| `stitch` | **Claude-native only** — not available to Codex. Stitch HTML is embedded in `taskFile.md` by the Architect as your visual reference. |

---

## HARD PROHIBITIONS

- Never touch files outside task scope.
- Never update `agents/workflow/handoff.md` — that belongs to the Architect.
- Never skip gates. Never mark COMPLETE before all triggered gates PASS.
- Never proceed when blocked. Write the BLOCKED report with your exact question.
- Never introduce new npm packages or Python dependencies without explicit instruction.
- Never write domain logic (cricket arithmetic) in React components.
- Never use raw hex/rgba values — CSS variables only.
- Never use `any` in TypeScript.
- Never commit `agents/workflow/taskFile.md` — it is in .gitignore.
