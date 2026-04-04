# Gate Sequence & Compliance Rules
# Part of: coreStandards
# Always load — required for every task completion
# Contains: Gates 1–6 (backend) + Gates F1–F4 (frontend) with full command syntax
# Source: ENGINEERING_STANDARDS_BACKEND.md Part 4 + ENGINEERING_STANDARDS_FRONTEND.md Part 4.3

---

## PHASE 12 COMPLIANCE GATE

No code is complete without passing every applicable gate in this section. These are not suggestions. They are deployment blockers.

---

### 4.1 Mandatory Gatekeeper

From this phase onward, **no code may be committed** unless `core/utils/compliance_bouncer.py` returns:

```
PASS: 100% compliance
```
This is GATE 6 in the gate sequence below. Gates 1–5P must pass before GATE 6 is reached.

Blocking command:
```powershell
python core/utils/compliance_bouncer.py --root .
```

A single violation is sufficient to block the commit. Fix the violation. Re-run the bouncer. Only then proceed.

**What the bouncer enforces (10 rules):**
- `ZERO_LITERAL` — hardcoded literals not declared in manifest registries
- `ANTI_ANY` — `Any` or `object` in type signatures
- `MISSING_RETURN_TYPE` — missing return annotations on functions
- `IO_AIR_GAP` — file or OS I/O inside engine execute paths
- `PRESENTATION_PURITY` — UI strings in service layer (formatters are exempt)
- `DOD_VIOLATION` — scalar loops (`.iterrows()` / `.itertuples()` forbidden)
- `BOUNDARY_VIOLATION` — infrastructure imports in Domain Core files
- `CONSTITUTIONAL_VISUAL_SILENCE` — visual tokens inside `core/`
- `CONSTITUTIONAL_TYPED_TRUTH` — deprecated or legacy imports in engines and calculators
- `CONSTITUTIONAL_ANTI_GREASE` — `Dict[str, Any]` or `object` in signatures

---

### 4.2 Git Commit Enforcement (Local)

The repository includes `.githooks/pre-commit` to enforce the compliance gate at commit time.

Enable once per clone:
```powershell
git config core.hooksPath .githooks
```

This hook MUST be enabled. Commits made without the hook active are non-compliant regardless of bouncer output.

---

### 4.3 Sentinel Order of Execution

Validation skills are mandatory gates — not optional. Every code-modifying task MUST pass all applicable gates in the order below before it is considered complete. Skipping any gate is a HARD FAIL.

Skills are divided into two types:
- **Guide skills** — instruct the agent how to perform a task correctly.
- **Validation skills** — verify the work done is architecturally correct.

Only validation skills appear in this gate sequence.

---

**GATE 1 — boundary-sentinel**
Trigger: any modification to `core/` files.
```powershell
python core/gen_ai/skills/validators/backend/boundary-sentinel/scripts/run_sentinel.py --root . --paths core/
```
Optional JSON output: append `--json` to emit structured `{"gate":"...","status":"PASS|FAIL","violations":[...],"violation_count":N}`.
Pass condition: zero cross-layer import violations, zero `self.dal` usage outside DAL, zero `duckdb.connect()` outside `core/data_access.py`.

---

**GATE-C — contract-regression**
Trigger: any modification to `core/calculators/`, `core/services/`, or `formats/*/engines/`.
```bash
python -m pytest tests/contracts/ -x -q --tb=short
```
Pass condition: all existing contract tests pass. Zero regressions in previously verified calculator/engine/service functions.

If GATE-C fails:
- Failure means this task changed the output of a function that had a verified contract.
- If the change is intentional (contract update): the contract file MUST be in FILES IN SCOPE
  and MUST be updated to reflect the new expected output before commit.
- If the change is unintentional: the implementation has introduced a regression. Fix it.

If `tests/contracts/` is empty or does not exist → SKIPPED (no contracts yet).

---

**GATE 2 — duckdb-lint-ops (DOD lint only)**
Trigger: any modification to `calculators/`, `engines/`, or `services/`.
```powershell
python core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py --root .
```
Optional JSON output: append `--json` to emit structured `{"gate":"...","status":"PASS|FAIL","violations":[...],"violation_count":N}`.
Pass condition: zero `.iterrows()` / `.itertuples()` violations.

---

**GATE 3 — manifest-contract-verifier**
Trigger: any modification to `manifest.py` or any engine file in `formats/`.
```powershell
python core/gen_ai/skills/validators/backend/manifest-contract-verifier/scripts/run_verifier.py --root . --manifest formats/odi/manifest.py
```
Optional JSON output: append `--json` to emit structured `{"gate":"...","status":"PASS|FAIL","violations":[...],"violation_count":N}`.
Pass condition: all `engine_class` / `engine_method` contracts verified, all `required_context` fields map to valid engine parameters.

---

**GATE 4 — serialization-guard**
Trigger: any modification to `api/serializers.py` or engine return types.
```powershell
python core/gen_ai/skills/validators/backend/serialization-guard/scripts/run_lint.py --root . --paths api/serializers.py --max-record-rows 500
```
Optional JSON output: append `--json` to emit structured `{"gate":"...","status":"PASS|FAIL","violations":[...],"violation_count":N}`.
Pass condition: zero memory bombs, zero high-latency recursive serialization patterns.

---

**GATE 5S — semgrep-security (REMOVED)**
Removed from hook and workflow. Rationale: internal-only platform, no public exposure,
no PII, no financial transactions on the app side. semgrep CLI also crashes on Windows
due to a charmap encoding bug in `--config=auto` rule download.

---

**GATE 5T — python-type-check**
Trigger: any Python file modified.
```powershell
python core/utils/python_type_check.py --root .
```
Optional JSON output: append `--json` to emit structured output.
Pass condition: violations_delta ≤ 0 vs `mypy_baseline_violations` in state.json.

**Known issue:** `core/gen_ai/` contains two files named `run_lint.py`, which causes mypy
to abort with a duplicate module error before checking anything — so the script currently
reports 0 violations silently. This is a script bug. True baseline (core/ excluding gen_ai)
is **145 errors** as of TASK-177a. Tracked in state.json as `mypy_baseline_violations`.

**Correct manual command** (use this if the script output looks wrong):
```bash
python -m mypy core/ --ignore-missing-imports --no-error-summary --exclude core/gen_ai
```
delta = (current count) - 145. Must be ≤ 0.

**Fix pending:** `core/utils/python_type_check.py` needs `--exclude core/gen_ai` added to
the mypy subprocess call. Schedule as an infra task before the next SRP split.

---

**GATE F1 — frontend-lint-sentinel**
Trigger: any modification to `frontend/` files.
Path: `core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/`
```powershell
python core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/scripts/run_frontend_lint.py --root .
```
Optional JSON output: append `--json` to emit structured `{"gate":"...","status":"PASS|FAIL","violations":[...],"violation_count":N}`.
Pass condition: zero violations across all 12 lint checks (raw fetch, type safety, CSS tokens, icon library, accessibility, test framework).

---

**SRP-CHECK — component line-count guard**
Trigger: any modification to `frontend/components/*.tsx` files.
Enforced by: `.githooks/pre-commit` SRP CHECK section.
Pass condition: no component file exceeds 300 lines. 300 lines is a signal to decompose, not a target.
Failure requires structural SRP analysis — not line-shuffling. Apply the "describe without and" test to each resulting file.
Note: SRP-CHECK is in the hook but has no standalone script. It does not emit JSON gate output. Report it as `{"gate_id": "SRP-CHECK", "triggered": true, "status": "PASS", "violations": []}` after confirming component line counts.

---

**GATE F2 — frontend-paradigm-sentinel**
Trigger: always — after GATE F1 passes (frontend tasks only).
Path: `core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/`
```powershell
python core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/scripts/run_frontend_paradigm.py --root .
```
Optional JSON output: append `--json` to emit structured `{"gate":"...","status":"PASS|FAIL","violations":[...],"violation_count":N}`.
Pass condition: zero architectural paradigm violations (domain logic, SRP, placement contract, external state libs).

---

**GATE F3 — frontend-type-sync-guard**
Trigger: any modification to `lib/types.ts` or backend schema types.
Path: `core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/`
```powershell
python core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/scripts/run_type_sync.py --root .
```
Optional JSON output: append `--json` to emit structured `{"gate":"...","status":"PASS|FAIL","violations":[...],"violation_count":N}`.
Pass condition: zero `@schema` JSDoc violations.

---

**GATE F4 — next-devtools-check** *(dormant)*
Trigger: frontend tasks — but currently always SKIPPED.
Status: dormant until next-devtools MCP is configured.
Do NOT include in `gates_triggered` in pre_call_state.json — it will never produce a real result.
When activated: `python core/utils/next_devtools_check.py --root .`
Pass condition: zero new runtime errors vs pre-task baseline (requires dev server).
Activation: add to `.githooks/pre-commit` GATE F4 dormant section and remove the comment block.

---

**GATE 5P — paradigm-sentinel (meta-gate)**
Trigger: always — runs after all primary gates pass.
```powershell
python core/utils/paradigm_sentinel.py --root .
```
Optional JSON output: append `--json` to emit structured output.
Pass condition: zero combined violations from GATE 1, GATE 6, and blocking GATE_SRP findings.
Note: the hook calls `paradigm_sentinel.py`, not `run_sentinel.py`. Do not confuse with GATE 1.

---

**GATE_SRP — srp-sentinel (two-tier)**
Trigger: always — runs inside GATE5P after GATE1 and GATE6.
Status: PASS when every violation is allowlisted. FAIL when any non-allowlisted file exceeds SRP thresholds.
```powershell
python core/utils/srp_sentinel.py --root . --json
```
Optional: restrict scope with `--paths core/api/formats/odi/engines/`.
JSON output keys:
- `blocking_violations` — hard-blocking findings
- `advisory_violations` — allowlisted findings
- `violations` — compatibility alias for `blocking_violations`
Findings appear in GATE5P JSON output under "srp_advisory" key, and blocking SRP
violations are folded into GATE5P's combined violation list.

Signals checked (three independent static analysis signals):
  Signal A: class method count > 20 or file function count > 20          (+1)
  Signal B: file line count > 400                                         (+1)
  Signal C: LCOM4 > 1 — class methods split into disjoint groups         (+2, weighted)
  Signal D: verb clusters >= 3 — methods span 3+ responsibility verbs    (+1)
  Signal E: import domains >= 3 — file imports from 3+ project layers    (+1)

Scoring: score >= 3 → SRP_WARNING | score >= 5 → SRP_FLAG

Note: SRP findings indicate scheduled refactor debt, not deployment blockers.
Known violations registry: agents/audits/SRP_VIOLATIONS.md

---

**GATE 6 — compliance_bouncer (final gate)**
Trigger: always — last step before every commit.
```powershell
python core/utils/compliance_bouncer.py --root .
```
Optional JSON output: append `--json` to emit structured `{"gate":"...","status":"PASS|FAIL","violations":[...],"violation_count":N}`.
Pass condition: `PASS: 100% compliance`.

---

**Dormant gates (activate when phase ships):**
- `event-state-linter` — activate when `core/live/` is created in Phase 12. Insert as GATE 3.5 between manifest-verifier and serialization-guard.

---

The bouncer is a final gate — not a substitute for the skill gates. All applicable gates must pass in sequence. A task is COMPLETE only when GATE 6 returns `PASS: 100% compliance`.

---

### Gate Applicability by Task Type

| Task type | Gates required |
|---|---|
| Backend engine/calculator/service | GATE-C (if calculators/services/engines touched), GATE 1 (if core/ touched), GATE 2, GATE 3 (if manifest/engine), GATE 4 (if serializer), GATE 5S, GATE 5T, GATE 5P, GATE 6 |
| Frontend component | GATE F1, SRP-CHECK (if components/*.tsx), GATE F2, GATE F3 (if lib/types.ts), GATE 5P, GATE 6 |
| Full-stack task | All applicable backend gates + all applicable frontend gates |

---

### 4.4 Non-Negotiable Block Condition

Any `FAIL` from `compliance_bouncer.py` is a hard stop for merge and release readiness. No exceptions. No deadline overrides this rule. Fix the violation first.

---

### 4.5 Memory Baseline Gate (Phase 12 Readiness)

Before any Phase 12 code is merged, the application's memory footprint at startup MUST be measured and recorded. The baseline MUST be under 800 MB RSS.

Measurement command (run after backend starts):
```python
import psutil, os
process = psutil.Process(os.getpid())
print(f"RSS: {process.memory_info().rss / 1024**2:.1f} MB")
```

Current baseline: ~247 MB. Phase 12 live layer adds approximately 10–30 MB. Both are well within the 4 GB budget — but this MUST be re-verified after any significant feature addition.

---

*Part of coreStandards — load for every task.*
*Authoritative source: ENGINEERING_STANDARDS_CORE.md*
