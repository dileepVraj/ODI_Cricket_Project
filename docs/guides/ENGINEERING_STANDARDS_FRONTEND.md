# Engineering Standards — Frontend Agent Index
# Version: 3.0 (thin index — modular standards)
# Last Updated: 2026-03-14
# THIS FILE IS AN INDEX ONLY. Do not read it as a standards file.
# Read the individual module files listed below instead.
# Authoritative source: ENGINEERING_STANDARDS_CORE.md

---

## Standard Load Set for Frontend Tasks

All paths below are relative to `docs/guides/`.

### MANDATORY (every frontend task):
- `coreStandards/MANDATES_1_TO_4.md`
- `coreStandards/SYSTEM_TOPOLOGY.md`
- `coreStandards/HIGH_IMPACT_REGISTRY.md`
- `coreStandards/GATE_SEQUENCE.md`
- `coreStandards/SKILLS_REGISTRY.md`
- `coreStandards/WORKFLOW_AND_LAWS.md`
- `frontendStandards/TACTICAL_EXECUTION.md`
- `frontendStandards/UI_IMPLEMENTATION.md`
- `frontendStandards/PERF_RESILIENCE_A11Y_TESTING.md`

### CONDITIONAL (load only when task requires):
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
| `frontendStandards/TACTICAL_EXECUTION.md` | 15 tactical execution rules (API wrapper, Tailwind, state, TypeScript, etc.) |
| `frontendStandards/UI_IMPLEMENTATION.md` | 10 UI rules (CSS tokens, badge system, icons, fonts, renderer pattern, etc.) |
| `frontendStandards/PERF_RESILIENCE_A11Y_TESTING.md` | Performance (3) + Resilience (3) + Accessibility (3) + Testing (4) rules |
| `coreStandards/MANDATES_5_6_LIVE.md` | Mandates 5–6 (Live Layer / WebSocket) — DORMANT |
