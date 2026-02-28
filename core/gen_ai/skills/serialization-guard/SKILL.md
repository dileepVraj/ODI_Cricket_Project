---
name: serialization-guard
description: Trigger this skill when modifying api/serializers.py or engine return types to ensure the data-to-JSON path is optimized for low-latency quant trading.
---

# Serialization Guard

Use this skill to enforce memory-safe, low-latency serialization on API response paths.

## Scope

- Single responsibility: detect serializer memory bombs and slow Python-loop serialization patterns.
- Zero-context assumption: perform a fresh AST scan of target serialization files each run.

## AST Rules

1. Flag DataFrame memory bombs:
- Any `.to_dict(orient="records")` call is only a violation when there is no explicit row count guard before it.
- A row count guard (for example `if len(df) > 1000: raise`) before the call makes it compliant.
- Default safety threshold: 500 rows.

2. Enforce fast serialization path:
- If records serialization is used, require `orjson` or vectorized DataFrame `.to_json(...)` usage.

3. Flag recursive high-latency patterns:
- Recursive list comprehensions in serializer hot paths (for example `[serialize_engine_output(row) for row in records]`).

4. Enforce vectorized NumPy casting:
- Flag element-wise loops/list-comprehensions over NumPy arrays in serialization logic.

## Command

```powershell
python "core/gen_ai/skills/serialization-guard/scripts/run_lint.py" --root "." --paths api/serializers.py --max-record-rows 500
```

## Test

```powershell
python "core/gen_ai/skills/serialization-guard/scripts/run_lint.py" --root "." --paths api/serializers.py --max-record-rows 500
```

Expected: `Fail`, including a `High Latency Risk` finding for the recursive list comprehension.
