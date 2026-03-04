---
name: executive-auditor
description: Mandatory post-modification governance gate. Trigger after any code change to run Phase 12 compliance checks, enforce HARD_FAIL on any violation, and block 'Task Complete' status until the compliance bouncer returns 100% PASS.
---

# Executive Auditor

Run this skill after any code modification.

## Required Sequence

1. Read Phase 12 section from `docs/guides/ENGINEERING_STANDARDS.md`.
2. Execute:

```powershell
python core/utils/compliance_bouncer.py --root .
```

3. Parse violations and enforce decision:
- If violations > 0: output `HARD_FAIL`.
- Immediately provide a line-numbered remediation plan using the bouncer evidence (`file:line:col`).
- Explicitly forbid stating "Task Complete".

4. Only when violations == 0:
- Report `PASS_100`.
- Permit completion status.
- Auto-sync `docs/ai/AI_MEMORY.md` with:
  - `Status: Phase 11.2 (Purification) - 100% Green.`
  - `Audit Log: Reduced compliance-bouncer violations from 1832 to 0.`
  - `Performance Impact: Blocking I/O removed from critical path.`
  - `Constraint Integrity: pre-commit hooks active and enforced.`

## Run Helper

```powershell
python "core/gen_ai/skills/executive-auditor/scripts/run_audit.py" --root .
```
