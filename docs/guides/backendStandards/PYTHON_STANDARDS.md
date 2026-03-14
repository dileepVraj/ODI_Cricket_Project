# Python Engineering Standards
# Part of: backendStandards
# Load for: any backend task (engine, calculator, service, DAL, API)
# Source: ENGINEERING_STANDARDS_BACKEND.md Part 2.1 (authoritative)

---

## 2.1 Python Engineering Standards

Every rule in this section is a hard constraint.

**1. The Typed Truth:** Every function signature MUST have strict Python type hints. No exceptions. Return types MUST always be declared. `None` return types MUST be explicitly marked as `-> None`.
```python
# CORRECT
def get_stats(df: pd.DataFrame, team: str) -> Dict[str, float]:

# VIOLATION — no type hints
def get_stats(df, team):
```

**2. Vectorization Mandate (DOD):** Analytical calculations MUST utilize Pandas and NumPy vectorization. AI agents MUST NEVER use `for index, row in df.iterrows():` for mathematical aggregations. Vectorized operations run 10–100× faster and consume a fraction of the memory on the Ryzen 5.

**3. The Pydantic Shield:** Every FastAPI endpoint MUST define incoming requests and outgoing responses using strict `pydantic.BaseModel` schemas. Validation MUST occur at the API boundary — before the payload reaches the engine layer. Engines MUST NOT receive unvalidated raw dicts.

**4. Crash Early, Crash Loud:** Bare exceptions are forbidden. AI agents MUST NEVER write `try: ... except Exception: pass`. Catch specific, expected errors (`KeyError`, `ValueError`, `TypeError`). Swallowing exceptions silently produces wrong results that are indistinguishable from correct results — the most dangerous failure mode in a trading tool.

**5. Skeleton Prohibition:** Unimplemented functions MUST NEVER silently return fake data, empty structures, or default zeros. Any function whose body is not yet implemented MUST raise `NotImplementedError` with a message explaining why the function is unimplemented and where the rebuild requirements are documented.
```python
# VIOLATION — silent fake return
def run_simulation(self):
    pass  # or return 0, or return {}

# CORRECT
def run_simulation(self) -> SimulationResult:
    raise NotImplementedError(
        "run_simulation() is pending Phase 12 rebuild. "
        "See core/backtester.py for rebuild requirements."
    )
```

**6. Source of Truth:** Hex colours, team mappings, venue aliases, and format constants MUST be referenced from `config/` or `formats/{fmt}/config/`. They MUST NEVER be hardcoded into engine or UI files.

**7. Ephemeral Branches:** Do not create `temp_test.py`, `debug_script.py`, or `scratch.py` in the main codebase. All experimental code MUST reside in a git branch and MUST be deleted post-merge. The main branch is always production-ready.

**8. Module Naming:** All Python module filenames MUST use `snake_case`. Hyphens in filenames break Python import conventions and create friction across hooks and scripts. Any hyphenated filename MUST be renamed before the module is extended.

---

*Part of backendStandards — load for every backend task.*
*Authoritative source: ENGINEERING_STANDARDS_CORE.md*
