---
name: duckdb-lint-ops
description: Query local DuckDB files safely in read-only mode and run Data-Oriented Design lint checks for pandas anti-patterns. Use when users ask for SQL inspection, schema checks, data profiling, or linting for iterrows/itertuples/manual DataFrame loops.
---

# DuckDB Lint Ops

Use this skill for quant-terminal data inspection and lint safety.

## Defaults

- Default DuckDB path: `formats/odi/data/odi.duckdb`
- Additional format DBs follow the same pattern: `formats/{fmt}/data/{fmt}.duckdb`

## Scripts

- `scripts/query_duckdb.py`
  - Safe query runner with `read_only=True`
  - Accepts SQL text or SQL file

- `scripts/run_lint.py`
  - Scans Python files for Data-Oriented Design anti-patterns:
    - `iterrows()`
    - `itertuples()`
    - manual Python `for` loops over DataFrame-like objects

## Typical Usage

1. Query default ODI database:

```powershell
python "core/gen_ai/skills/duckdb-lint-ops/scripts/query_duckdb.py" --sql "SELECT COUNT(*) AS n FROM matches"
```

2. Additional format DBs follow the same pattern: `formats/{fmt}/data/{fmt}.duckdb`

3. Run DOD linter on repository:

```powershell
python "core/gen_ai/skills/duckdb-lint-ops/scripts/run_lint.py" --root "."
```

## Execution Rules

- Never open DuckDB in write mode from this skill.
- Treat lint violations as hard errors for quant math code.
- Prefer vectorized pandas/NumPy operations over row-wise iteration.
