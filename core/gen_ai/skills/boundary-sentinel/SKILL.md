---
name: boundary-sentinel
description: Trigger this skill whenever code is modified or created in the core/ directory to ensure zero database (DAL) or API coupling.
---

# Boundary Sentinel

Use this skill to enforce Hexagonal Architecture and DDD boundaries inside `core/`.

## Scope

- Single responsibility: detect cross-layer import violations and Core side-effect leakage.
- Do not perform unrelated refactors, formatting-only changes, or business-logic rewrites.
- Zero-context assumption: scan each target file independently of prior chat history.

## Zero-Context AST Checks

For every file under `core/`, run these independent checks:

1. Import block scan (top-level imports only):
- Flag `import api...`
- Flag `from api... import ...`
- Flag `import frontend...`
- Flag `from frontend... import ...`

2. Class-body side-effect scan:
- Flag any `self.dal` usage (attribute read, assignment, or call chain)
- Flag any raw `duckdb.connect(...)` call

3. Report:
- Print `Pass` when no violations are found
- Print `Fail` and `file:line:col` with rule id and message for each violation

## Command

```powershell
python "core/gen_ai/skills/boundary-sentinel/scripts/run_sentinel.py" --root "." --paths core/
```

## Test (Expected Pass)

```powershell
python "core/gen_ai/skills/boundary-sentinel/scripts/run_sentinel.py" --root "." --paths core/calculators/performance.py
```

Expected output:

```text
Pass
```
