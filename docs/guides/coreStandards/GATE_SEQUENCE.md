# Gate Sequence & Compliance Rules
# Part of: coreStandards
# Always load — required for every task completion
# Contains: Gates 1–6 (backend) + Gates F1–F3 (frontend) with full command syntax
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
This is GATE 6 in the gate sequence below. Gates 1–5 must pass before GATE 6 is reached.

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
Pass condition: zero cross-layer import violations, zero `self.dal` usage outside DAL, zero `duckdb.connect()` outside `core/data_access.py`.

---

**GATE 2 — duckdb-lint-ops (DOD lint only)**
Trigger: any modification to `calculators/`, `engines/`, or `services/`.
```powershell
python core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py --root .
```
Pass condition: zero `.iterrows()` / `.itertuples()` violations.

---

**GATE 3 — manifest-contract-verifier**
Trigger: any modification to `manifest.py` or any engine file in `formats/`.
```powershell
python core/gen_ai/skills/validators/backend/manifest-contract-verifier/scripts/run_verifier.py --root . --manifest formats/odi/manifest.py
```
Pass condition: all `engine_class` / `engine_method` contracts verified, all `required_context` fields map to valid engine parameters.

---

**GATE 4 — serialization-guard**
Trigger: any modification to `api/serializers.py` or engine return types.
```powershell
python core/gen_ai/skills/validators/backend/serialization-guard/scripts/run_lint.py --root . --paths api/serializers.py --max-record-rows 500
```
Pass condition: zero memory bombs, zero high-latency recursive serialization patterns.

---

**GATE F1 — frontend-lint-sentinel**
Trigger: any modification to `frontend/` files.
Path: `core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/`
```powershell
python core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/scripts/run_frontend_lint.py --root .
```
Pass condition: zero violations across all 12 lint checks (raw fetch, type safety, CSS tokens, icon library, accessibility, test framework).

---

**GATE F2 — frontend-paradigm-sentinel**
Trigger: always — after GATE F1 passes (frontend tasks only).
Path: `core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/`
```powershell
python core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/scripts/run_frontend_paradigm.py --root .
```
Pass condition: zero architectural paradigm violations (domain logic, SRP, placement contract, external state libs).

---

**GATE F3 — frontend-type-sync-guard**
Trigger: any modification to `lib/types.ts` or backend schema types.
Path: `core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/`
```powershell
python core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/scripts/run_type_sync.py --root .
```
Pass condition: zero `@schema` JSDoc violations.

---

**GATE 5 — paradigm-sentinel (meta-gate)**
Trigger: always — runs after all primary gates pass.
Follow instructions in:
`core/gen_ai/skills/validators/backend/paradigm-sentinel/SKILL.md`
Pass condition: zero violations across all paradigm checks including boundary scan, DAL bypass probe, and bouncer gate.

---

**GATE 6 — compliance_bouncer (final gate)**
Trigger: always — last step before every commit.
```powershell
python core/utils/compliance_bouncer.py --root .
```
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
| Backend engine/calculator/service | GATE 1 (if core/ touched), GATE 2, GATE 3 (if manifest/engine), GATE 4 (if serializer), GATE 5, GATE 6 |
| Frontend component | GATE F1, GATE F2, GATE F3 (if lib/types.ts), GATE 5, GATE 6 |
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
