# Standards Reference Index

## Pipeline & Architecture
| Topic | File |
|---|---|
| Full pipeline spec (all decisions, all sessions) | `agents/redesign/spec.md` |
| Pipeline guarantees (G1–G10) | `agents/redesign/spec.md` Section 1 |
| Failure modes + escalation paths (F1–F8) | `agents/redesign/spec.md` Section 2 |
| Agent capabilities + MCP servers | `agents/redesign/spec.md` Section 0 |
| Verification & gate layer | `agents/redesign/spec.md` Section 4 |
| State + handoff mechanism | `agents/redesign/spec.md` Section 5 |
| Session journal (decisions made per session) | `agents/redesign/journal.md` |

## Workflow Files
| Topic | File |
|---|---|
| TaskFile template | `agents/workflow/taskFileTemplate.md` |
| Session state | `agents/workflow/state.json` |
| Report JSON schema | `agents/workflow/report-schema.json` |
| Completed task reports | `agents/workflow/reports/` |
| DesignBrief template | `agents/workflow/designBrief.md` |

## Codex Skills
| Topic | File |
|---|---|
| Pre-task setup (baseline, scope, assertion) | `agents/skills/codex/pre-task.md` |
| Reviewer subagent (independent AC check) | `agents/skills/codex/reviewer.md` |
| Commit + structured report | `agents/skills/codex/commit-report.md` |
| Scope enforcement pre-commit hook | `agents/skills/codex/scope-guard.md` |

## Gemini Skills
| Topic | File |
|---|---|
| Full-codebase consistency audit | `agents/skills/gemini/consistency-audit.md` |
| Persist approved design decisions | `agents/skills/gemini/save-design-decisions.md` |
| Guide page quality check | `agents/skills/gemini/guide-quality.md` |

## Core Standards (load per task scope)
| Topic | File |
|---|---|
| Architectural Laws (Mandates 1–4) | `docs/guides/coreStandards/MANDATES_1_TO_4.md` |
| Gate sequence scripts + paths | `docs/guides/coreStandards/GATE_SEQUENCE.md` |
| High-impact file registry | `docs/guides/coreStandards/HIGH_IMPACT_REGISTRY.md` |
| System topology (layer map) | `docs/guides/coreStandards/SYSTEM_TOPOLOGY.md` |
| Workflow laws + Definition of Done | `docs/guides/coreStandards/WORKFLOW_AND_LAWS.md` |
| Skills registry (gate script paths) | `docs/guides/coreStandards/SKILLS_REGISTRY.md` |

## Backend Standards
| Topic | File |
|---|---|
| Python standards + hard prohibitions | `docs/guides/backendStandards/PYTHON_STANDARDS.md` |
| Memory & threading rules | `docs/guides/backendStandards/MEMORY_AND_THREADING.md` |
| Known patterns (KIPs) | `docs/guides/backendStandards/KNOWN_PATTERNS_KIPS.md` |

## Frontend Standards
| Topic | File |
|---|---|
| Frontend execution protocol | `docs/guides/frontendStandards/TACTICAL_EXECUTION.md` |
| UI implementation standards | `docs/guides/frontendStandards/UI_IMPLEMENTATION.md` |
| Perf / accessibility / testing | `docs/guides/frontendStandards/PERF_RESILIENCE_A11Y_TESTING.md` |

## Agent Souls (read when grounding a decision)
| Topic | File |
|---|---|
| Architect soul | `agents/souls/architect.md` |
| Executor soul | `agents/souls/executor.md` |
| Designer soul | `agents/souls/designer.md` |
