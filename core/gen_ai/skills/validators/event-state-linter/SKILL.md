---
name: event-state-linter
description: Trigger this skill when building 'Service' layers or Scrapers to ensure zero synchronous blocking of the FastAPI event loop.
---

# Event State Linter

Use this skill to enforce non-blocking async patterns in high-frequency or live-feed modules.

## Scope

- Single responsibility: detect synchronous blocking calls and async starvation risks.
- Zero-context assumption: parse target file(s) fresh using AST.

## AST Rules

1. Flag blocking sync calls:
- `time.sleep(...)`
- `requests.get(...)` (and other `requests.*` network calls)
- `duckdb.connect(...)` synchronous DB connection

2. Enforce state model contract:
- Classes named with `State` must inherit `pydantic.BaseModel`

3. Enforce async I/O discipline:
- Functions performing I/O-like calls must be `async def`
- I/O calls in `async def` must be wrapped with `await`

4. Prevent event-loop starvation:
- Flag `while True` loops that do not contain `await asyncio.sleep(...)`

5. Output:
- `Pass` when no violations
- `Fail` with `file:line:col`, rule id, and code line

## Command

```powershell
python "core/gen_ai/skills/event-state-linter/scripts/run_lint.py" --root "." --paths core/live api/live
```

Default scan target: `core/live/` and `api/live/` (Phase 12 directories — will be created during Phase 12 build).
If these directories do not exist yet, the linter will report nothing to scan — this is expected pre-Phase 12.

## Test (Expected Fail)

```powershell
python "core/gen_ai/skills/event-state-linter/scripts/run_lint.py" --root "." --paths "core/gen_ai/skills/event-state-linter/references/mock_live_scraper_fail.py"
```

Expected output starts with:

```text
Fail:
```
