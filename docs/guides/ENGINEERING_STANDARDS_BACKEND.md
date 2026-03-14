# Engineering Standards — Backend Agent Index
# Version: 3.0 (thin index — modular standards)
# Last Updated: 2026-03-14
# THIS FILE IS AN INDEX ONLY. Do not read it as a standards file.
# Read the individual module files listed below instead.
# Authoritative source: ENGINEERING_STANDARDS_CORE.md

---

## Standard Load Set for Backend Tasks

All paths below are relative to `docs/guides/`.

### MANDATORY (every backend task):
- `coreStandards/MANDATES_1_TO_4.md`
- `coreStandards/SYSTEM_TOPOLOGY.md`
- `coreStandards/HIGH_IMPACT_REGISTRY.md`
- `coreStandards/GATE_SEQUENCE.md`
- `coreStandards/SKILLS_REGISTRY.md`
- `coreStandards/WORKFLOW_AND_LAWS.md`
- `backendStandards/PYTHON_STANDARDS.md`
- `backendStandards/MEMORY_AND_THREADING.md`

### CONDITIONAL (load only when task requires):
- `backendStandards/KNOWN_PATTERNS_KIPS.md`
  → Load ONLY when task touches `formats/odi/engines/team_engine.py`
- `coreStandards/MANDATES_5_6_LIVE.md`
  → Load ONLY when task touches `core/live/` or `api/live/` [DORMANT — Phase 12]

### NEVER LOAD:
- `ENGINEERING_STANDARDS_CORE.md` — human architect file, not for agents
- `docs/ai/AI_MEMORY.md` — deprecated

---

## Quick Reference: What Each File Contains

| File | Contents |
|---|---|
| `coreStandards/MANDATES_1_TO_4.md` | Layer role classification + Mandates 1–4 (Functional Core, Hexagonal Purity, DOD, SRP) |
| `coreStandards/SYSTEM_TOPOLOGY.md` | Layer map + 6 Paradigms (Manifest-Driven UI, DAL Fortress, Strategy, ETL, Pre-Computed, Observer) |
| `coreStandards/HIGH_IMPACT_REGISTRY.md` | 3 registered files + stop-state-trace-confirm rule |
| `coreStandards/GATE_SEQUENCE.md` | Gates 1–6 + F1–F3 with full command syntax, compliance bouncer rules |
| `coreStandards/SKILLS_REGISTRY.md` | All skill paths, wrong-path hard-stop rules |
| `coreStandards/WORKFLOW_AND_LAWS.md` | Workflows A/B/C + 8 coding laws |
| `backendStandards/PYTHON_STANDARDS.md` | 8 Python rules (typing, vectorization, Pydantic, exceptions, etc.) |
| `backendStandards/MEMORY_AND_THREADING.md` | Memory management (6 rules) + thread-safety (4 rules) |
| `backendStandards/KNOWN_PATTERNS_KIPS.md` | KIP-001 + KIP-002 for team_engine.py only |
| `coreStandards/MANDATES_5_6_LIVE.md` | Mandates 5–6 (Live Layer / WebSocket) — DORMANT |
