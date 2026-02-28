# 📜 AI Architectural Manifesto (The Development Bible)
**Version:** 1.1  
**Status:** THE GOVERNING LAW  

This document is the **Single Source of Truth (SSOT)** for all engineering work in the Cricket Algo-Trader project. Every line of code generated or modified by an AI Agent must comply with these protocols. Failure to comply is a violation of the system architecture.

---

## 🛡️ 1. The Gatekeeper Protocol (MANDATORY)
Before beginning ANY task, the AI Agent is strictly required to execute this three-step sequence:

1.  **READ**: Retrieve and internalize this Manifesto and `docs/ai/AI_MEMORY.md` to establish the current sprint context and architectural constraints.
2.  **PLAN**: Draft a solution in the conversation using ONLY the approved patterns defined here. No "creative" deviations from the Hexagonal Architecture are permitted without explicit user approval.
3.  **AUDIT & SELF-CORRECT**: Before outputting code, run an internal audit:
    -   *"Did I hardcode a team color or use the config dictionary?"*
    -   *"Is there a single emoji or HTML tag in this headless engine?"*
    -   *"Am I using a loop where a vectorized SQL query should exist?"*

---

## 🏛️ 2. The Hexagonal Law (Stack Separation)
Technical debt is avoided by maintaining absolute "Air Gaps" between layers.

### **A. Logic Layer (Pure Math Zone)**
-   **Rule:** Engines (formats/{fmt}/engines/) and Calculators (core/calculators/) must be "Logic-Pure".
-   **Forbidden:** Importing any UI-specific module or hardcoding "Grease" (untyped objects).
-   **Requirement:** All logic must consume and return the explicit TypedDict contracts defined in core/interfaces/team_types.py.

### **B. Adapter Layer (The Manifest & API)**

- **Rule:** `formats/{fmt}/manifest.py` is the exclusive registry for all UI-facing keys, emojis, and display labels.
- **Requirement:** Any string literal used as a dictionary key or status label (e.g., 'Excluded', 'no_results') MUST be registered in the `SERVICE_LITERAL_REGISTRY` of the manifest.
- **Requirement:** The API (`api/main.py`) consumes raw data from engines and uses the Manifest-driven `report_formatter.py` to apply presentation logic.

### **C. Persistence Layer (DuckDB)**
-   **Rule:** `core/data_access.py` (The DAL) is the **exclusive** gateway to the database.
-   **Forbidden:** Direct `con.execute()` calls inside engine files. All SQL logic must be encapsulated in the DAL.

---

## 🛠️ 3. Feature Implementation Protocol
Follow this exact sequence to add any new analysis capability:

1.  **Manifest Entry**: Add the function to `formats/{fmt}/manifest.py`. This triggers the dynamic UI generation.
2.  **Param Mapping**: Update `ParamMapperService` to define how frontend context maps to your engine's arguments.
3.  **Engine Implementation**: Write the calculation logic in the appropriate engine. Use SQL-first logic (Vectorization).
4.  **Schema Definition**: Add the response model to `api/schemas/execute.py`.
5.  **Serializer**: Add a cleaner function in `api/serializers.py` to prepare the output for the `<DataTable />` or `<MatrixTable />` components.

---

## 🐞 4. Bug Fixing Protocol
Bugs must be treated as architectural failures, not one-off errors.

1.  **Diagnosis**: Run `scripts/tests/test_all_fns.py` to identify if the failure is across the entire manifest.
2.  **Truth Bridge**: If the bug is statistical, consult `formats/odi/tests/truth_bridge/`. Check if this is a `DATA_DRIFT` (acceptable) or `LOGIC_REGRESSION` (unacceptable).
3.  **Isolation**: Create a minimal reproduction script in `scripts/debug/`.
4.  **Root Cause Cleanup**: If the bug was caused by an anti-pattern (e.g., a missing `if b > 0`), update the **Anti-Patterns** section of this Manifesto to prevent recurrence.

---

## 🧹 5. Refactoring Standards
Refactoring is only permitted if it improves the "Hexagonal Air Gap."

1.  **Zero-Destruction**: You are FORBIDDEN from deleting existing helper functions or logic unless explicitly replacing them with superior, tested alternatives.
2.  **Backward Compatibility**: The existing API endpoints and manifest keys must remain functional. Use `deprecated` tags if necessary, but never break the "Match Pack" pipeline.
3.  **Atomic Updates**: If refactoring a core service (like the DAL), update it and its dependent engines in a single, verified transaction.

---

## 🚫 6. The "Sins" (Strict Anti-Patterns)
Any AI generating the following code will be considered "Hallucinating" or "Lazy":

-   **Hardcoding**: Never write `if team == "India"`. Use `PLAYER_ROLES` or `TEAM_COLORS` from the config.
-   **Lazy Placeholders**: Never output `// ... rest of code stays same`. Always output the full, valid function.
-   **Polluted Engines**: Putting `<b>Table</b>` or `🔥` inside an engine method.
-   **Linear Scans**: Iterating over multi-million row DataFrames with `.iterrows()`. Use vectorized SQL in the DAL.
-   **Alias Collapse Bug**: Resolving a venue alias set and then filtering by only the first matched label (`venue == first_match`). Venue filtering must use the full alias-derived mask.

---

## 🧬 7. Evolution & Governance
To append new laws to this Manifesto:
1.  State the **Context** (What happened?).
2.  Define the **New Protocol** (What is the law?).
3.  Update the **Version Number** at the top of this file.


## 📝 8. The Compliance Law

** Zero-Violation Policy:** Every delivery MUST pass `python core/utils/compliance-bouncer.py --root .` with zero hits for `ZERO_LITERAL`, `ANTI_GREASE`, or `VISUAL_SILENCE`.

** Physical Audit:** "Ghost Passes" (claiming success without physical file updates) are considered a total failure. The AI must verify that strings are physically written to the `SERVICE_LITERAL_REGISTRY` in the manifest.
---
**END OF MANIFESTO**
