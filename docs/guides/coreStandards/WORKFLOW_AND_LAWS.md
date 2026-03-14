# Modification Protocol & Coding Laws
# Part of: coreStandards
# Load for: any task that modifies existing code
# Source: ENGINEERING_STANDARDS_BACKEND.md Part 3 (authoritative)

---

## THE MODIFICATION & WORKFLOW PROTOCOL

AI agents executing tasks MUST follow these exact workflows. Skipping a step is not permitted. If a step cannot be completed, the agent MUST stop and report — not proceed.

---

### Workflow A: Bug Fixes (The RCA Trace)

When diagnosing a bug, trace backwards through the layers. Do not mutate the engine until every upstream layer has been verified.

1. **Frontend:** Did Next.js send the correct request payload?
2. **API / Manifest:** Did Pydantic validate the input? Did the serializer strip or transform a field?
3. **Engine:** Is the mathematical calculation in the concrete engine correct?
4. **DAL:** Did the DAL construct the correct DuckDB query?
5. **ETL:** Is the data actually missing or corrupted in the source CSV or DuckDB table?

Do not mutate code at layer N until you have confirmed layer N+1 is correct.

---

### Workflow B: Adding New Features (Outside-In)

To implement a new analytical feature, follow this exact sequence. Steps MUST NOT be skipped or reordered.

1. **Define Contract:** Update `manifest.py` and `api/schemas/` to define the input and output shape. Nothing is built until the contract exists.
2. **Implement Logic:** Write the math in the Concrete Engine (`formats/{fmt}/engines/`). Ensure the implementation satisfies the ABC Interface in `core/interfaces/`.
3. **Truth Bridge:** Add a regression test that asserts the engine returns the exact structure promised by the Pydantic schema.
4. **UI Implementation:** Implement the Next.js visual component to consume the newly registered manifest endpoint.

---

### Workflow C: System Modifications (Safe Mutation)

- **Database Schema Changes:** MUST flow through ETL modifications (`json_converter.py` → `refinery_script.py`) followed by an Atomic Swap rebuild. Direct schema modifications to `odi.duckdb` are forbidden.
- **Mathematical Changes:** If an engine formula is intentionally altered, the resulting Truth Bridge test failures MUST be acknowledged and new "Golden Master" JSON outputs MUST be generated to baseline the new math.
- **API Response Changes:** Endpoint outputs MUST be additive. AI agents MUST NOT rename or remove existing JSON keys in serializers unless the Next.js frontend consuming those keys is simultaneously refactored in the same task.
- **Deletion Tasks:** When any function, endpoint, or class is deleted, the agent MUST search the entire codebase for all references to the deleted artefact and clean them up in the same task. A deletion is not complete until zero references remain in live code.

---

## THE 8 CODING LAWS

### The "Zero-Literal" Law (Source of Truth)

**Violation:** Hardcoding tactical windows, match limits, year thresholds, or fallback constants (e.g., `[:10]`, `year=2015`, `fallback=6`, `overs=50`).

**The Mandate:** No numeric or string literals related to business or cricket logic are permitted in any analytical file — regardless of its directory location. All constants MUST be defined in `manifest.py` and accessed via the injected `self.rules` or `format_rules` context.

**Audit Trigger:** Any integer or float found in an analytical method that is not `0` or `1` (used as counters or binary flags) is a Hard Fail.

---

### The "Derivative Literal" Law (No Math Hiding)

**The Cheat:** Using `100`, `/ 6`, or `0.5` because they seem like "standard math."

**The Law:** All numeric coefficients — even "obvious" ones like percentage divisors or sports-specific units — MUST be named constants in the manifest.

**Why:** If the format changes (e.g., a "100-ball" game), a `/ 6` for overs becomes a silent bug that produces wrong predictions without raising any error.

**Audit Trigger:** Any division by a raw integer or multiplication by a raw float in an analytical file is a Hard Fail.

---

### The "Visual Silence" Law (Presentation Purity)

**Violation:** Any analytical file returning UI-friendly strings like `"DNB"`, `"N/A"`, `"-"`, `"Bat Form"`, `"their last 5"`, or any human-readable label.

**The Mandate:** Domain Core files are Visual-Deaf. They process and return Raw Primitive Data (`float`, `int`, `bool`, `None`) or Domain Objects (TypedDicts, dataclasses). Human-readable labelling, placeholder logic, and narrative string assembly are strictly reserved for the `ReportFormatter` and the frontend.

**Audit Trigger:** Any string literal containing non-technical, human-readable descriptors found in a Domain Core return value is a Hard Fail.

---

### The "Anti-Grease" Law (Typed Truth)

**Violation:** Using `Any`, bare `Dict`, `**kwargs`, or `object` to pass data between layers.

**The Mandate:** The use of `Any` is officially deprecated and forbidden in all method signatures in Domain Core files. All complex data structures MUST be defined as `pydantic.BaseModel` or `TypedDict`. Every function MUST have a return type hint. `None` returns MUST be explicitly marked as `-> None`.

**The Object-is-Any Extension:** Replacing `Any` with `object` or `Dict[str, object]` to pass the linter while keeping data blind is equally forbidden. `object` is `Any` in a tuxedo.

**Audit Trigger:** A grep for `: Any`, `: object`, or `-> Dict[str, object]` in any Domain Core file is a Hard Fail.

---

### The "I/O Air-Gap" Law (Execute-Path Purity)

**Violation:** Calling `os.path`, `open()`, `pd.read_csv()`, `duckdb.query()`, or any file-system or network operation inside an execute path.

**The Mandate:** The execute path MUST be Purely Computational. All data MUST be pre-loaded at startup and injected as DataFrames. No file or database access is permitted once the server has started serving requests.

**Audit Trigger:** Any file-system or database-driver import found in a Domain Core file is a Hard Fail.

---

### The "Pure Primitive" Mandate

**The Cheat:** Returning `f"{team_id}_stats"` or `team_name + " Form"` from an engine or service.

**The Law:** Domain Core files may only return primitives (`int`, `float`, `bool`) or `None` as scalar values. Any string concatenation involving domain data inside a Domain Core file is a Presentation Leak.

**Why:** Strings are for humans. Data is for systems. Mixing them in the domain core makes the output untestable, unlocalizable, and format-dependent.

---

### The "Stale Test" Law (Truth Bridge Integrity)

**Violation:** A test file asserting the behaviour of a function, endpoint, or schema that no longer exists in the codebase.

**The Mandate:** When any endpoint, function, or API schema is removed or renamed, its corresponding test MUST be removed or updated in the same task.

**Workflow:** When removing any function or endpoint, the agent MUST search the entire `tests/` directory for references to that artefact before marking the removal task complete. Any matching test MUST be either rewritten or explicitly disabled:
```python
# TEST DISABLED — [function name] removed — pending [Phase X] rebuild
# See [file path] for rebuild requirements.
```

**Audit Trigger:** Any test file containing a call to a function, class, or URL that does not exist in the current codebase is a Hard Fail.

---

### The "Skeleton Prohibition" Law (Extended Crash Early, Crash Loud)

**Violation:** Any function whose body is `pass`, `return {}`, `return []`, `return 0`, or `return None` when those returns represent unimplemented logic rather than a legitimate empty result.

**The Mandate:** Unimplemented functions MUST raise `NotImplementedError` with a descriptive message.
```python
# VIOLATION
def run_simulation(self):
    pass

# CORRECT
def run_simulation(self) -> SimulationResult:
    raise NotImplementedError(
        "run_simulation() is pending Phase 12 rebuild. "
        "See core/backtester.py for rebuild requirements."
    )
```

**Audit Trigger:** Any non-trivial method body consisting solely of `pass` or a bare default return in a Domain Core file is a Hard Fail.

---

*Part of coreStandards — load for any task that modifies existing code.*
*Authoritative source: ENGINEERING_STANDARDS_CORE.md*
