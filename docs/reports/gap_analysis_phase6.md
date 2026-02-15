# 📉 Gap Analysis: Phase 6 (The "Roast")

**Date:** 2026-02-14
**Standard:** [ENGINEERING_STANDARDS.md](../guides/ENGINEERING_STANDARDS.md)

---

## 🛑 Executive Summary
The application is a **Data Science Prototype**, not an **Engineering Product**.
While the *logic* is sound (Symbolic), the *implementation* (Neuro) is fragile, coupled, and untestable.

**Rating:** `D+` (Functional but Fragile)

---

## 🔍 Detailed Violations

### 1. The "Headless" Violation (Severity: Critical)
*   **Standard:** Engines returns `Dict` or `Dataclass`. UI is separate.
*   **Reality:** `Core` engines are infected with `IPython.display`.
*   **Evidence:**
    *   `core/team_engine.py`: Contains `display(HTML("<div..."))`.
    *   `core/player_engine.py`: Returns `None` but prints HTML tables as side-effects.
*   **Impact:** We cannot build a Web App, Mobile App, or REST API without rewriting 100% of the logic.

### 2. The "Typed Truth" Violation (Severity: High)
*   **Standard:** Strict Type Hints (`def foo(x: int) -> int`).
*   **Reality:** Dynamic Typing (`def foo(x)`).
*   **Evidence:** `TeamEngine._apply_smart_filters(self, df)` -> What is `df`? A DataFrame? A Dict? A List? We guess.
*   **Impact:** Future agents (Gemini 2.0) will hallucinate inputs because the signature provides no contract.

### 3. The "Crash Early" Violation (Severity: Medium)
*   **Standard:** No bare `try...except`.
*   **Reality:** Broad exception swallowing.
*   **Evidence:** `core/team_engine.py:30`: `except Exception: max_date = None`.
*   **Impact:** If the date format changes, the engine silently defaults to `None` instead of alerting us, leading to "Empty Graphs" with no error logs.

---

## 🛠️ Remediation Plan (Phase 6)

1.  **Define Protocols:** Create `core/interfaces/` (Started).
2.  **Extract Logic:** Move HTML generation to `formats/odi/renderers/`.
3.  **Enforce Types:** Add type hints to every function we refactor.

---

> "We are building a Porsche engine, but right now it's welded to a tractor chassis."
