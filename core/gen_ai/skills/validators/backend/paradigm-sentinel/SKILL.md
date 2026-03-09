---
name: paradigm-sentinel
description: Mandatory post-skill governance sweep. Trigger after any other skill executes, or after any code-modifying task, to detect paradigm violations hidden behind local skill passes.
---

# Paradigm Sentinel

Run this skill as the final check after every other skill.

## Mission

Prevent false confidence where one linter passes while fundamental architecture is violated elsewhere.

## Required Post-Skill Checks

1. Run boundary scan on `core/`:

```powershell
python "core/gen_ai/skills/validators/backend/boundary-sentinel/scripts/run_sentinel.py" --root "." --paths core/
```

2. Run Compliance Bouncer gate:

```powershell
python core/utils/compliance_bouncer.py --root .
```

3. Probe for hidden DAL bypass patterns:
- Global DAL singletons outside `core/data_access.py`
- Any `duckdb.connect(...)` outside DAL and ETL scripts
- `import api...` or `import frontend...` inside `core/`
- Hardcoded tactical literals inside `engines/` or `services/`

Suggested scan:

```powershell
if (Get-Command rg -ErrorAction SilentlyContinue) {
  rg -n "global\s+dal|duckdb\.connect\(|self\.dal|import\s+api|from\s+api|import\s+frontend|from\s+frontend" core formats -S
} else {
  Select-String -Path "core\**\*.py","formats\**\*.py" -Pattern "global\s+dal|duckdb\.connect\(|self\.dal|import\s+api|from\s+api|import\s+frontend|from\s+frontend"
}
```

## Exit Contract

- `PASS`: No violations from any step.
- `FAIL`: Any violation in any step blocks commit readiness.

When failing, print a compact matrix with file:line:col evidence and the broken paradigm.
