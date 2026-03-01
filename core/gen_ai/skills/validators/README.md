# Validation Skills

Validation skills verify that work done is
architecturally correct. They are mandatory
gates in the sentinel order defined in
docs/guides/ENGINEERING_STANDARDS.md
section 4.3.

## Gate Sequence
1. boundary-sentinel (GATE 1)
2. duckdb-lint-ops (GATE 2) — lives in guides/
3. manifest-contract-verifier (GATE 3)
4. serialization-guard (GATE 4)
5. paradigm-sentinel (GATE 5)
6. compliance-bouncer (GATE 6) — lives in
   core/utils/

## Skills
- boundary-sentinel — hexagonal boundary
  enforcement
- manifest-contract-verifier — manifest-to-
  engine contract verification
- event-state-linter — async pattern
  enforcement (dormant until Phase 12)
- serialization-guard — serialization memory
  and latency enforcement
- executive-auditor — bouncer gate enforcer
- paradigm-sentinel — meta-gate, runs all
  primary checks
