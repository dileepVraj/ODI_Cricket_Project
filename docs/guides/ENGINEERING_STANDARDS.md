# 🏗️ Engineering Standards: The "Gold Standard"
**Last Updated:** 2026-02-15 (Post-Audit)

> "We assume the data is dirty, the market is efficient, and manual processes will fail."

---

## ✅ Current Achievement Status

| Standard | Status | Evidence |
|----------|--------|----------|
| Headless Engines | ✅ ACHIEVED | TeamEngine, PlayerEngine, PredictorEngine — pure data output |
| Format-Agnostic Core | ✅ ACHIEVED | Factory pattern in `core/`, format registry v2.0 |
| Crash Early, Crash Loud | ✅ ACHIEVED | Zero bare `except: pass` remaining |
| Type Hints | ✅ ACHIEVED | All public engine methods typed |
| Vectorization | ✅ ACHIEVED | No `iterrows` loops in engines |
| Source of Truth | ✅ ACHIEVED | `TEAM_COLORS`, `PLAYER_ROLES` centralized |
| Living Documentation | ⚠️ IN PROGRESS | Core docs updated, auto-update rules added |
| API-First | 🔜 NEXT | FastAPI wrapper planned (Phase 1) |
| Automated Pipeline | ✅ ACHIEVED | `scripts/update_data.py` — 4-stage flow |
| Truth Bridge | ✅ ACHIEVED | 12 regression suites, auto-diagnosis |

---

## 🏆 The Principles

### 1. ROI-Driven Development (RDD)
*   **Philosophy:** Code is a Liability. Features are Bets.
*   **Rule:** Every major feature must have a **Hypothesis** and a **Backtest**.
    *   *Bad:* "Added a new chart for dot ball percentage."
    *   *Good:* "Added Dot Ball analysis. Backtest shows it improves 'Under 250 Runs' prediction accuracy by 4%."

### 2. The "Trustless" Architecture
*   **Philosophy:** Trust nothing. Verify everything.
*   **Rule:** The **Truth Bridge** is not a suggestion. It is a gatekeeper.
    *   Data Ingestion must fail if column distributions shift.
    *   Logic updates must fail if they break historical "Golden Masters" without a signed-off reason.
    *   Engine functions MUST return `MATCH_IDS` for auto-diagnosis.

### 3. API-First (Headless)
*   **Philosophy:** Data is the product. The Dashboard is just one view.
*   **Rule:** Engines NEVER return UI (HTML/Plots).
    *   `analyze_venue_bias()` → Returns `Dict[str, Any]`.
    *   Renderers (`TeamHTMLRenderer`) take data, produce UI. Separate concerns.

### 4. Format-Agnostic Core
*   **Philosophy:** Adding a new cricket format should NEVER require modifying `core/`.
*   **Rule:**
    *   `core/*.py` files are factories — they load implementations dynamically.
    *   Format-specific code lives in `formats/{fmt}/`.
    *   `config/format_registry.py` is the single registry for all formats.
    *   `engine.py` uses the registry, never hardcodes format imports.

### 5. Living Documentation
*   **Philosophy:** If it's not in the docs, it doesn't exist.
*   **Rule:**
    *   `AI_MEMORY.md` is updated at the end of every significant task.
    *   Core docs are kept current (see Auto-Update Protocol below).
    *   A feature is NOT DONE until a `REGRESSION_GUIDE.md` exists.

---

## 📜 The Coding Constitution (Tactical Rules)

### 1. The "Typed Truth" (Type Hints)
*   **Rule:** Every function signature MUST have Type Hints.
*   **Why:** We are building a financial engine. `x + y` could be `10 + 20` (30) or `"10" + "20"` ("1020").
*   **Standard:**
    ```python
    # BAD
    def get_stats(data, team): ...

    # GOOD
    def get_stats(data: pd.DataFrame, team: str) -> Dict[str, float]: ...
    ```

### 2. S.O.L.I.D. in Data Science
*   **Rule:** A function calculates Stats OR Renders HTML. Never both.
*   **Standard:**
    *   `core/` logic returns `dataclasses` or `dicts`.
    *   Renderers use `jinja2` or `ipywidgets` to display those dicts.

### 3. Vectorization Mandate (Performance)
*   **Rule:** NEVER iterate over DataFrame rows with `for index, row in df.iterrows():`.
*   **Exception:** Complex string parsing where Regex is impossible (rare).
*   **Standard:**
    ```python
    # BAD
    for i in df.index: df.at[i, 'runs'] = df.at[i, 'runs'] * 2

    # GOOD
    df['runs'] = df['runs'] * 2
    ```

### 4. Crash Early, Crash Loud (Error Handling)
*   **Rule:** Do not wrap large blocks in broad `try: ... except Exception: pass`.
*   **Standard:** Catch specific errors (`KeyError`, `ValueError`). If a critical calculation fails, raise a custom `DataIntegrityError`.
*   **Status:** ✅ Zero bare `except: pass` remaining as of 2026-02-15 audit.

### 5. The "Golden Master" Test
*   **Rule:** For any complex output, keep a JSON snapshot ("Golden Master") of the correct output.
*   **Why:** Unit tests check if code runs. Golden Masters check if the *answer* is still right.

### 6. The "Leaf Blower" Policy (Cleanup)
*   **Rule:** Any temporary script (`debug_*.py`, `temp_*.py`, `*_CORRUPTED.py`) must be deleted immediately.
*   **Status:** ✅ All ghost files deleted as of 2026-02-15 audit.

### 7. Source of Truth (No Hardcoding)
*   **Rule:** NEVER hardcode hex colors, player roles, or format-specific constants.
*   **Standard:**
    *   Colors: `TEAM_COLORS.get('India', 'blue')` from `config/shared/team_colors.py`
    *   Roles: `PLAYER_ROLES.get(player)` from `formats/odi/config/players.py`
    *   Settings: Format-specific configs in `formats/{fmt}/config/settings.py`

### 8. Defensive Data (Anti-Crash)
*   **Rule:** Assume data is dirty. Never divide without checking for zero.
*   **Standard:**
    ```python
    # BAD
    avg = runs / outs

    # GOOD
    avg = runs / outs if outs > 0 else runs
    ```
*   Also: check `if col in df.columns` before accessing.

---

## 🚀 The Roadmap to "Industry Top Notch"

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 6 | ✅ DONE | Headless Refactor (Engines decoupled from UI) |
| Phase 7 | ✅ DONE | Truth Bridge (Auto-diagnosing regression tests) |
| Phase 8 | ✅ DONE | Automated Data Pipeline |
| Phase 9 | ✅ DONE | Codebase Audit & Format-Agnostic Refactor |
| Phase 10 | 🔜 NEXT | FastAPI + Next.js Frontend (9 sub-phases) |
| Phase 11 | 📋 PLANNED | Multi-Format Support (T20I, IPL) |
| Phase 12 | 📋 PLANNED | Backtesting Rig (Simulate betting strategies) |
