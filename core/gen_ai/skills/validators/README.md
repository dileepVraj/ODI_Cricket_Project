# Validation Skills

Validation skills verify that work done is
architecturally correct. They are mandatory
gates in the sentinel order defined in
docs/guides/ENGINEERING_STANDARDS.md
section 4.3.

## Gate Sequence
1. boundary-sentinel (GATE 1)
2. duckdb-lint-ops (GATE 2) � lives in guides/
3. manifest-contract-verifier (GATE 3)
4. serialization-guard (GATE 4)
5. paradigm-sentinel (GATE 5)
6. compliance-bouncer (GATE 6) � lives in
   core/utils/

## Skills
- boundary-sentinel � hexagonal boundary
  enforcement
- manifest-contract-verifier � manifest-to-
  engine contract verification
- event-state-linter � async pattern
  enforcement (dormant until Phase 12)
- serialization-guard � serialization memory
  and latency enforcement
- executive-auditor � bouncer gate enforcer
- paradigm-sentinel � meta-gate, runs all
  primary checks

---

## Frontend Gate Sequence

Frontend gates run after all applicable
backend gates pass. They are triggered
by any modification to frontend/ files.

F1. frontend-lint-sentinel (GATE F1)
    Triggers on any .tsx or .ts modification
    under frontend/.
F2. frontend-paradigm-sentinel (GATE F2)
    Always — after GATE F1 passes.
F3. frontend-type-sync-guard (GATE F3)
    Triggers when lib/types.ts or any
    backend Pydantic schema file is modified.
5.  paradigm-sentinel (GATE 5) — always.
6.  compliance-bouncer (GATE 6) — always.

## Frontend Validators

Frontend validator skills enforce compliance
with ENGINEERING_STANDARDS_FRONTEND.md via
automated scanning of tsx/ts files.

### Skills

- frontend-lint-sentinel (GATE F1) — scans
  all .tsx/.ts files under frontend/ for
  12 common rule violations covering raw
  fetch calls, type safety, CSS tokens,
  icon libraries, accessibility, format
  hardcoding, and test framework compliance.
  Triggers: any .tsx or .ts modification
  under frontend/.
  Invoke: python core/gen_ai/skills/
    validators/frontend/frontend-lint-sentinel
    /scripts/run_frontend_lint.py --root .
  Pass: zero violations reported.
  Fail: violations listed as
    [RULE X.XX-RN] description
    file:line:col

- frontend-paradigm-sentinel (GATE F2) —
  deep architectural scan for structural
  violations: domain logic in components,
  SRP breaches, wrong directory placement,
  external state library imports, renderer
  error-swallowing, and component size over
  300 lines.
  Triggers: always after GATE F1 passes.
  Invoke: python core/gen_ai/skills/
    validators/frontend/frontend-paradigm-
    sentinel/scripts/run_frontend_paradigm.py
    --root .
  Pass: zero violations reported.
  Fail: violations listed as
    [RULE X.XX-RN] description
    file:line:col

- frontend-type-sync-guard (GATE F3) —
  validates that all TypeScript interfaces
  in lib/types.ts that map to backend API
  schemas carry @schema JSDoc tags. Prevents
  silent drift between backend Pydantic
  models and frontend TypeScript interfaces.
  Triggers: modification to lib/types.ts or
  any backend Pydantic schema file.
  Invoke: python core/gen_ai/skills/
    validators/frontend/frontend-type-sync-
    guard/scripts/run_type_sync.py --root .
  Pass: zero violations reported.
  Fail: interfaces missing @schema JSDoc
    listed as
    [RULE 2.2D-R3] Interface 'X' missing
    @schema JSDoc
    file:line:col
