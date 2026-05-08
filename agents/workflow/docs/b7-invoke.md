# B7 — Invoke Agents

## Pre-invocation checks

Re-read state.json immediately before writing — do not rely on session memory.
Read `agents/workflow/state.json` fresh from disk right now.
Confirm `active.task_id` is still null. If it is not null — HARD LOCK is active. Do not invoke.
This re-read is mandatory even if B1 confirmed idle earlier in the session.

## Write to state.json before every invocation (follow STATE.JSON WRITE PROTOCOL)

```json
"active": {
  "task_id": "TASK-XXX",
  "phase": "SOLO | MULTI-PHASE-A | MULTI-PHASE-C",
  "agent": "Codex | Gemini | Claude",
  "invoked_at": "<ISO timestamp>",
  "pre_call_commit": "<git log --oneline -1 hash>",
  "retry_count": 0
}
```

On retry (F2/F3/F7B): increment `retry_count` by 1 before re-invoking. Never reset it.
This persists the retry budget across session boundaries — F8 cannot silently reset the counter.

## Codex invocation

```powershell
codex exec -s danger-full-access --output-schema agents/workflow/report-schema.json -C "C:\Cricket_Project_Stable" "Read AGENTS.md. Then read agents/workflow/taskFile.md and execute the task."
```

Timeout: 2700000.

## Claude invocation (direct execution)

Claude executes the task directly in the current session.
No CLI command needed -- Claude reads AGENTS.md and taskFile.md and proceeds.
Claude also updates state.json after completion (Architect role).

## Gemini invocation

```bash
gemini -p "Read AGENTS.md. Then read agents/workflow/taskFile.md and execute the task." --yolo
```
