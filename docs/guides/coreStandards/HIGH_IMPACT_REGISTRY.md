# High-Impact File Registry
# Part of: coreStandards
# Always load — required for all tasks
# The three registered files appear in almost every task's blast radius.
# Source: ENGINEERING_STANDARDS_BACKEND.md Part 6 (authoritative)

---

## PART 6: HIGH-IMPACT FILE REGISTRY

The following files carry disproportionate architectural risk. They are not frozen — legitimate refactoring will touch them. But any agent that modifies these files WITHOUT explicit instruction in the current task prompt has violated this standard.

---

### 6.1 The Rule

Before modifying any file in this registry, the agent MUST:

1. **Stop.** Do not make the change yet.
2. **State explicitly** which registered file it needs to modify and why.
3. **Produce an impact trace** — list every other file that imports from or depends on the file being modified.
4. **Wait for explicit confirmation** before proceeding.

If the current task prompt already contains an explicit instruction to modify a registered file (e.g. "update team_types.py"), no additional confirmation is needed — the instruction IS the permission.

Modifying a registered file without either:
- an explicit instruction in the task prompt, or
- a stop-state-trace-confirm sequence

is a hard architectural violation regardless of whether the bouncer passes.

---

### 6.2 The Registry

| File | Risk | Why |
|---|---|---|
| `core/data_access.py` | CRITICAL | Handles venue resolution, team hydration, and integrity validation. Every engine and service depends on it. A silent change here corrupts every downstream output. |
| `core/interfaces/team_types.py` | HIGH | Load-bearing type contract system. Adding new TypedDicts is safe. Removing or renaming existing types silently breaks engines, services, and serializers simultaneously with no immediate error. |
| `api/serializers.py` | HIGH | Small, complete, handles every known edge case. Changes here affect every API response. There is no routine reason to touch it. |

---

### 6.3 Files Removed From Registry

The following files were previously listed as Do-Not-Touch but have been removed because active refactoring requires them to be modifiable as normal workflow:

- `core/calculators/` — active refactoring area. Protected by the compliance bouncer and sentinel gates instead.
- `formats/odi/manifest.py` — touched constantly as a normal side effect of literal registration and feature additions. Protected by manifest-contract-verifier instead.
- `api/engine_pool.py` — too recently rebuilt to be considered stable. Re-evaluate for registry inclusion after Phase 12.

---

### 6.4 Registry Maintenance

This registry is a living document. After any major refactoring phase completes and a file is considered genuinely stable, it may be added to the registry. The criteria for addition are:

1. The file has not been modified in the last two phases.
2. All downstream consumers are typed and tested.
3. There is no known planned work that requires modifying it.

Files are added to the registry by explicit architect instruction only — never by agent decision.

---

*Part of coreStandards — load for every task.*
*Authoritative source: ENGINEERING_STANDARDS_CORE.md*
