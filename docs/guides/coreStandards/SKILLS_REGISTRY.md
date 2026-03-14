# Agentic Skills Registry
# Part of: coreStandards
# Load for: any task — required to reference correct gate paths
# Contains: all skill paths, wrong-path hard-stop rules, session startup requirement
# Source: ENGINEERING_STANDARDS_BACKEND.md Part 5 + ENGINEERING_STANDARDS_FRONTEND.md Part 5

---

## PART 5: AGENTIC SKILLS

### 5.1 Project-Local Skill Registry (Authoritative)

All agentic governance skills are internalized in the repository and MUST be referenced from project-local paths only. Global user-profile skill paths (`~/.codex/skills/`) are non-authoritative and MUST NOT be used.

Current project skills:

**Backend guide skills** (`core/gen_ai/skills/guides/backend/`):
- `core/gen_ai/skills/guides/backend/duckdb-lint-ops/`

**Backend validation skills** (`core/gen_ai/skills/validators/backend/`):
- `core/gen_ai/skills/validators/backend/boundary-sentinel/`
- `core/gen_ai/skills/validators/backend/event-state-linter/`
- `core/gen_ai/skills/validators/backend/executive-auditor/`
- `core/gen_ai/skills/validators/backend/manifest-contract-verifier/`
- `core/gen_ai/skills/validators/backend/paradigm-sentinel/`
- `core/gen_ai/skills/validators/backend/serialization-guard/`

**Frontend guide skills** (`core/gen_ai/skills/guides/frontend/`):
- `core/gen_ai/skills/guides/frontend/frontend-bug-fix-guide/`
- `core/gen_ai/skills/guides/frontend/frontend-modification-guide/`
- `core/gen_ai/skills/guides/frontend/frontend-new-component-guide/`

**Frontend validation skills** (`core/gen_ai/skills/validators/frontend/`):
- `core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/`
- `core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/`
- `core/gen_ai/skills/validators/frontend/frontend-type-sync-guard/`

**System skills** (`core/gen_ai/skills/.system/`):
- `core/gen_ai/skills/.system/skill-creator/`
- `core/gen_ai/skills/.system/skill-installer/`

When creating new skills, place them in the correct typed subdirectory:
- Backend guide skills: `core/gen_ai/skills/guides/backend/[skill-name]/`
- Backend validation skills: `core/gen_ai/skills/validators/backend/[skill-name]/`
- Frontend guide skills: `core/gen_ai/skills/guides/frontend/[skill-name]/`
- Frontend validation skills: `core/gen_ai/skills/validators/frontend/[skill-name]/`

---

### 5.3 Hard-Stop Condition

If any required skill gate fails, a stale or pre-restructure path is referenced (e.g. `core/gen_ai/skills/boundary-sentinel/` instead of `core/gen_ai/skills/validators/backend/boundary-sentinel/`), or gate results are missing from the task report, compliance status is `FAIL` regardless of bouncer output. The task is not complete.

---

### 5.4 Agent Context Requirement (Session Startup)

Every AI agent session that involves code changes MUST begin by loading the standards files specified in CLAUDE.md Step 2 and `docs/ai/SESSION_STATE.md`.

An agent that begins a task without loading the scoped standards files and session state has insufficient context. Any task started without this context MUST be restarted.

---

*Part of coreStandards — load for every task.*
*Full gate commands with exact paths are in GATE_SEQUENCE.md.*
*Authoritative source: ENGINEERING_STANDARDS_CORE.md*
