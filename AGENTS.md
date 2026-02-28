# 🤖 AGENTS.MD: THE GOVERNING LAW FOR AI AGENTS

**Version:** 1.0  
**Status:** THE SUPREME DIRECTIVE  
**Core Mandate:** "Assume data is dirty, boundaries are strict, and trust is zero."

This document is the **Single Source of Truth (SSOT)** and mandatory operational manual for all AI Agents working on the Cricket Algo-Trader codebase. Every interaction and code modification MUST comply with these rules.

---

## 🛡️ 1. THE GATEKEEPER PROTOCOL (MANDATORY BOOTSTRAP)
Before outputting any code or making any changes, you MUST follow this sequence:

1.  **READ & ESTABLISH CONTEXT**: 
    -   Read `docs/guides/ENGINEERING_STANDARDS.md` to internalize the architecture.
    -   Consult the `AI_ARCHITECTURAL_MANIFESTO.md` for governing laws.
2.  **PLAN**: Draft your solution. Ensure it respects the **Hexagonal Air Gap**.
3.  **INTERNAL AUDIT**: Run a mental checklist:
    -   *"Am I using `config/` for colors/roles instead of hardcoding?"*
    -   *"Is this engine function deterministic and functional (Data-In, Data-Out)?"*
    -   *"Am I using vectorization (Pandas/NumPy) or a slow loop?"*

---

## 🛑 2. STRICT CODING STANDARDS (ZERO-DESTRUCTION)

1.  **NO LAZY PLACEHOLDERS:** Never output `// ... existing logic` or `// ... rest of code stays same`. You MUST rewrite the full function or file.
2.  **PRESERVE & EXTEND:** Never delete existing imports, helper functions, or logic unless explicitly replacing them with superior, tested alternatives.
3.  **ATOMIC UPDATES:** If modifying a single function, output *only* that function. If modifying multiple files, ensure they are updated in a single, consistent state.
4.  **ZERO HALLUCINATIONS:** NEVER guess imports, file paths, or variable names. If you don't know, **READ THE FILE**.

---

## 🏛️ 3. ARCHITECTURAL LAWS

### 3.1 The Hexagonal Law (Stack Separation)
Technical debt is avoided by maintaining absolute "Air Gaps" between layers.
-   **Engine Layer (`formats/{fmt}/engines/`):** Pure math. No I/O, no database calls, no UI strings, no emojis.
-   **API Layer (`api/`):** The only bridge. Handles serialization (adding emojis/labels) via `api/serializers.py`.
-   **DAL Layer (`core/data_access.py`):** The EXCLUSIVE gateway to DuckDB. No `con.execute()` in engines.

### 3.2 Functional Core, Imperative Shell
-   **Core:** Math engines MUST be deterministic. They take data and return data.
-   **Shell:** `api/` and `scripts/` handle the "dirty" work of I/O and state.

### 3.3 Manifest-Driven UI
-   The UI is 100% driven by `formats/{fmt}/manifest.py`.
-   To add a feature, register it in the manifest FIRST.
-   **Rule:** Never hardcode UI components in React for specific domain features.

---

## 🎓 4. ENGINEERING STANDARDS (TACTICAL)

### 4.1 Python Standards
-   **Typed Truth:** Every function MUST have strict Type Hints. `Any` is forbidden (Use `TypedDict` or `Pydantic`).
-   **Vectorization (DOD):** Zero Scalar Loops. Use Pandas/NumPy. `.iterrows()` is a failure.
-   **Crash Early, Crash Loud:** Catch specific exceptions. Never use `except Exception: pass`.
-   **Safe Math:** `a / b` must be `a / b if b > 0 else 0`. Assume dirty data.

### 4.2 Visual Silence (Presentation Purity)
-   Engines return **Raw Primitive Data** (float, int, bool, None).
-   Labeling (e.g., `"DNB"`, `"Elite"`) and placeholders are reserved for the **api/serializers.py** or **Frontend**.

### 4.3 Source of Truth (Zero-Literal Law)
-   Hardcoding team names, colors, or match limits is FORBIDDEN.
-   Use `TEAM_COLORS['India']` and `PLAYER_ROLES.get(player)`.
-   All constants must be in `manifest.py` or `config/`.

---

## 🛠️ 5. SKILL COMPLIANCE & GOVERNANCE
Agents must operate within the verified "Agentic Skills" framework:
1.  **boundary-sentinel**: Enforce layer separation (Engine vs API vs DAL).
2.  **duckdb-lint-ops**: Prevent raw SQL in engines and enforce DAL usage.
3.  **manifest-contract-verifier**: Ensure engine outputs match the `manifest.py` contract.
4.  **event-state-linter**: Ensure "Live Match" updates are in-memory only.
5.  **serialization-guard**: Prevent DataFrames from leaking directly to the frontend without cleanup.

---

## 🧪 6. TESTING & VALIDATION
-   **Golden Masters:** Use JSON snapshots from `formats/{fmt}/tests/truth_bridge/` for verification.
-   **No Hardcoding Teams:** Tests must cover all teams/venues dynamically.
-   **Truth Bridge:** If math changes, failures MUST be audited for `LOGIC_REGRESSION` vs `DATA_DRIFT`.

---

## ✅ 7. DEFINITION OF DONE (HANDOVER PROTOCOL)

A task is not complete until:
1.  **Logic Verification:** Green tests pass, and math is manually verified.
2.  **Documentation Update:** Update the relevant `.md` files if architecture/contracts changed.
3.  **Memory Sync:** **UPDATE `docs/ai/AI_MEMORY.md`** with a timestamped log of your changes.
4.  **Compliance:** Run `python core/utils/compliance-bouncer.py --root .`. Zero violations allowed.

---

## 🚫 6. THE "SINS" (STRICT ANTI-PATTERNS)
-   **Polluted Engines:** Emojis (🔥) or HTML tags in Python engine files.
-   **Hardcoded Logic:** `if venue == "Wankhede"`.
-   **Data Access Violations:** `import duckdb` inside an engine.
-   **Lazy Handover:** Skipping the `AI_MEMORY.md` update.

---
**GOVERNANCE:** Failure to follow these rules will result in immediate rejection of the contribution. Any deviation must be explicitly justified and approved by the Human Architect.
