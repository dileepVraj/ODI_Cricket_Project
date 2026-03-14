# Context Loader Prompt Template

Use this template when `context-loader` is invoked.

## 1. Read session state

Read `docs/ai/SESSION_STATE.md` and extract:
- Current phase
- Active task scope
- Priority queue top item
- Known blockers
- Last Updated date

## 2. Build ordered attach list from scope

Input:
- `task_scope`: `backend` | `frontend` | `architecture`

Attach rules:

All paths below are relative to `docs/guides/`.

| Scope | Mandatory | Conditional |
|---|---|---|
| `backend` | `coreStandards/MANDATES_1_TO_4.md`, `coreStandards/SYSTEM_TOPOLOGY.md`, `coreStandards/HIGH_IMPACT_REGISTRY.md`, `coreStandards/GATE_SEQUENCE.md`, `coreStandards/SKILLS_REGISTRY.md`, `coreStandards/WORKFLOW_AND_LAWS.md`, `backendStandards/PYTHON_STANDARDS.md`, `backendStandards/MEMORY_AND_THREADING.md`, `docs/ai/SESSION_STATE.md` | `backendStandards/KNOWN_PATTERNS_KIPS.md` — load only if task touches `formats/odi/engines/team_engine.py` |
| `frontend` | `coreStandards/MANDATES_1_TO_4.md`, `coreStandards/SYSTEM_TOPOLOGY.md`, `coreStandards/HIGH_IMPACT_REGISTRY.md`, `coreStandards/GATE_SEQUENCE.md`, `coreStandards/SKILLS_REGISTRY.md`, `coreStandards/WORKFLOW_AND_LAWS.md`, `frontendStandards/TACTICAL_EXECUTION.md`, `frontendStandards/UI_IMPLEMENTATION.md`, `frontendStandards/PERF_RESILIENCE_A11Y_TESTING.md`, `docs/ai/SESSION_STATE.md` | — |
| `architecture` | all backend mandatory files + all frontend mandatory files + `docs/guides/TECHNICAL_AUDIT_REPORT.md` | — |

Return files in the exact order shown above.

## 3. Inject phase-awareness block

Emit this block in agent context:

```text
CURRENT PHASE: [value from SESSION_STATE]
ACTIVE TASK: [value from SESSION_STATE]
DO NOT: start Phase 12 work (live layer / Numba AOT)
DO NOT: touch core/data_access.py, core/interfaces/team_types.py,
        api/serializers.py without stop-state-trace-confirm
```

## 4. Apply stale-state warning check

Compare `Last Updated` from `SESSION_STATE.md` against today's date.
If age is greater than 7 days, output:

```text
WARNING: SESSION_STATE.md is stale ([date]).
Verify priorities with architect before proceeding.
```

## 5. Confirm context loaded

Output:

```text
CONTEXT LOADED - [scope] task
Files attached: [list]
Phase: [phase]
Ready to proceed.
```

## 6. Read Discipline

Once a file has been read and values extracted, do NOT re-read it.
Work from extracted values only for the remainder of the task.

Extract once. Reference the extraction.

Violations:
- Reading SESSION_STATE.md more than once per session
- Reading standards files more than once per session
- Re-opening any file to "verify" something already extracted
