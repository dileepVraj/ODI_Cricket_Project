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

| Scope | Attach |
|---|---|
| `backend` | `docs/guides/ENGINEERING_STANDARDS_BACKEND.md`, `docs/ai/SESSION_STATE.md` |
| `frontend` | `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md`, `docs/ai/SESSION_STATE.md` |
| `architecture` | `docs/guides/ENGINEERING_STANDARDS_BACKEND.md`, `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md`, `docs/ai/SESSION_STATE.md`, `docs/guides/TECHNICAL_AUDIT_REPORT.md` |

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
