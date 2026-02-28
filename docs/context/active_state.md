# 🧠 Active State Context
**Last Updated:** 2026-02-15 (Post-Audit)
**Status:** Active | Format-Agnostic Core | **Frontend Build Ready**

## 🚨 CURRENT PRIORITY: Frontend Development
**Roadmap:** [`docs/plans/FRONTEND_ROADMAP.md`](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/docs/plans/FRONTEND_ROADMAP.md)
**Design Spec:** [`docs/design/UI_SPEC.md`](file:///c:/Users/khaisar%20jaha/OneDrive/Desktop/Cricket_Project_Stable/docs/design/UI_SPEC.md) (V5 — Manifest-Driven)
**Architecture:** Manifest-driven, dynamic UI. Each format declares capabilities via `manifest.py`.
**Rule:** Follow phases sequentially. Check roadmap status tracker before starting any frontend work.

## 📌 Current Architecture State (Post-Audit v3.0)

### Core Layer (`core/`)
- **Format-Agnostic Factories:** `core/team_engine.py`, `core/player_engine.py`, `core/predictor.py` are now factories that dynamically load format-specific engines via `config/format_registry.py`.
- **No shims, no circular imports, no IPython dependencies in core.**
- **BaseEngine:** `core/base_engine.py` provides shared safe-math utilities (`_safe_divide`, `_safe_float`, `_format_pct`).

### Facade (`engine.py`)
- **CricketAnalyzer v3.0** — Format-aware facade.
- **Two init modes:**
    - Legacy: `CricketAnalyzer("formats/odi/data/FINAL_ODI_MASTER.csv")` (auto-detects format)
    - Modern: `CricketAnalyzer(format_type="odi")`
- Uses `logger` (not `print()`), `core.data_loader` for DRY caching, `get_format_engines()` for dynamic engine loading.

### Format Engines (`formats/odi/engines/`)
- **TeamEngine** (v6.1) — Headless, Typed, Vectorized. Handles macro analytics (H2H, Fortress, Phases, Form).
- **PlayerEngine** (v5.5) — Headless, Typed. Fast-Look Optimization, DNB detection, Role-Aligned Schema.
- **PredictorEngine** (v4.0) — Venue Par, Batting Potential, Bowling Threat with Tail-Ender Risk.

### Format Registry (`config/format_registry.py` v2.0)
- Central hub for format management.
- Functions: `get_format_engines()`, `get_format_manifest()`, `get_format_config()`, `get_available_formats()`.
- Registered formats: ODI, T20I, WODI, WT20I, IPL (only ODI has implementations).

### Data Access
- **DuckDB-backed DAL** (`core/data_access.py`) — Parameterized SQL, schema verification.
- **Self-Healing Pickle Cache** via `core/data_loader.py`.
- **Performance:** Pure DB Mode — selective queries, no global DataFrame hydration.

### Packaging & Config
- `pyproject.toml` — Proper Python packaging with optional dependency groups.
- `.env.example` — Environment configuration template.
- `.gitignore` — Comprehensive, covers all formats and data files.
- `requirements.txt` — Pinned deps (DuckDB 1.2.1), grouped by purpose.

## 🏏 Player Role Methodology (Cortex v2.5)
*   **Bowler**: Primary contributor; bats 8-11.
*   **Batter**: Primary contributor; bowls < 5% of games.
*   **Bowl AR**: Significant batting (bats 7-8) but primary role is bowling.
*   **Bat AR**: Top 6 batter who bowls regularly (> 20% of games).
*   **Verification Proof**: `formats/odi/scripts/find_missing_players.py` cross-references the full 10-year dataset against `formats/odi/config/players.py`.

## 🔄 Data Pipeline Architecture

### 1. Source Layer (`formats/odi/data/json_source/`)
- **Format:** [Cricsheet](https://cricsheet.org/) JSON (Overs-based structure).
- **Action:** Drop new match `.json` files here to update the database.

### 2. Ingestion Engine (`formats/odi/utils/json_converter.py`)
**Command:** `python formats/odi/utils/json_converter.py`
- Iterates `.json` files → Extracts 3 contexts → Normalizes → Standardizes → Outputs CSVs.

### 3. Automated Pipeline (`scripts/update_data.py`)
**Command:** `python scripts/update_data.py`
- **Stage 1:** JSON → CSV (Ingestion)
- **Stage 2:** CSV → Refined CSVs (Refinery)
- **Stage 3:** CSVs → DuckDB (Database Rebuild)
- **Stage 4:** Truth Bridge Verification (auto-fail on regression)

### 4. Storage Layer

| File | Role |
| :--- | :--- |
| `FINAL_ODI_MASTER.csv` | **Source of Truth**. Ball-by-ball (1M+ rows). |
| `MATCH_SQUADS.csv` | Playing XI per match (DNB detection). |
| `MATCH_INFO.csv` | Metadata (Winner, Toss, Venue). |
| `odi.duckdb` | Runtime DB. Tables: `balls`, `matches`, `player_stats`, `phase_stats`, `squads`. |

## 🛑 Coding Standards & Constraints
- **STRICTLY following:** `docs/guides/ENGINEERING_STANDARDS.md` and `docs/ai/GEMINI.md`.
- **Test Parity Rule:** NEVER use `pd.read_csv()` in tests. ALWAYS use `CricketAnalyzer(filepath)`.
- **Fingerprint Mandate:** Engine functions MUST return `MATCH_IDS` for Truth Bridge.
- **Source of Truth Rule:** Colors from `TEAM_COLORS`, Roles from `PLAYER_ROLES`. No hardcoding.
- **Defensive Data Rule:** Safe division, NaN handling, column existence checks.
- **Crash Early, Crash Loud:** Specific exceptions only. Zero bare `except: pass`.
- **Constrained PowerShell Rule:** If `npm` fails because `npm.ps1` is blocked, run frontend commands with `npm.cmd ...` (or `cmd /c npm ...`). This fallback is allowed for any agent in constrained shells.

## Host Country H2H Behavioral Contract
- Canonical user manual: `docs/application_detailed_user_manual.md`.
- `country_h2h` defaults `country_name` to home-team country when empty.
- `team_b` is optional and supports `All` for home-vs-all analysis in host country scope.
- Host-country filtering uses `venue_id` prefixes plus raw `venue` alias resolution when `venue_id` is null.
- Output contract is list-shaped for `comparison_table`: data returns `List[Dict]`, no-data returns `[]` (never `{}`).

## 🧱 Anti-Patterns & Lessons Learned

### 1. Test Environment Discrepancy
- **Mistake:** Loading raw CSV in tests instead of using `CricketAnalyzer`.
- **Fix:** ALWAYS use the Facade in tests. It applies venue standardization that raw CSV misses.

### 2. Schema Assumption Blindness
- **Mistake:** Assumed `batting_team` column existed; actually `team_bat_1`.
- **Fix:** Check `df.columns` before writing logic. Self-healing derivation in facade.

### 3. Date Boundary Exclusion
- **Mistake:** Using `pd.Timestamp.now()` for lookback cutoffs.
- **Fix:** Use `pd.Timestamp.now().floor('D')` to include full boundary day.

### 4. Hardcoded Hex Colors
- **Mistake:** Using `#1f77b4` directly in Python code.
- **Fix:** Use `TEAM_COLORS.get('India', 'blue')`. Single Source of Truth.

### 5. Shadow Shadowing (Backward-Compat Shims)
- **Mistake:** Shims in `core/` that re-imported from `formats/odi/`, shadowing local classes.
- **Fix:** Replaced with factory pattern. `get_team_engine("odi")` dynamically loads the correct class. All shims removed.

### 6. Bare except:pass (Silent Failures)
- **Mistake:** 7 locations with `except: pass` that swallowed all errors silently.
- **Fix:** All replaced with specific exception types (`KeyError`, `ValueError`, `TypeError`, `OSError`). Zero bare excepts remain.

### 7. IPython in Core (API Crash)
- **Mistake:** `core/predictor.py` imported IPython at module level → crashes in non-Jupyter environments.
- **Fix:** Core is now fully API-safe. IPython only in `interface.py` (the UI file).

### 8. Ghost Files (Dead Code)
- **Mistake:** `core/player_engine_CORRUPTED.py` (70KB) and `core/player_engine_TEMP.py` (70KB) in production.
- **Fix:** Deleted. Git is the version history.

### 9. Missing `__init__.py` in Subpackages (Import Blindness)
- **Mistake**: Large subdirectories like `core/interfaces` or `formats/odi/renderers` were missing `__init__.py`, causing IDEs/linters to fail importing their contents.
- **Fix**: Every directory intended to be part of a Python package MUST contain an `__init__.py` file. Added missing files to `core/interfaces/` and `formats/odi/renderers/`.

### 10. React Side-Effect in State Updater (Router Update Error)
- **Mistake**: Calling `window.history.pushState` (or any Next.js Router action) inside a `useState` functional updater (`setX(prev => { ... side-effect ... })`).
- **Consequence**: "Cannot update a component (`Router`) while rendering a different component (`AppProvider`)". Functional updaters must be pure.
- **Fix**: Move side-effects (like URL synchronization) to a `useEffect` that monitors the state changes. This ensures the side-effect runs *after* the render phase is complete.
### 11. API Parameter Mapping Drift (Unexpected Argument Error)
- **Mistake**: The generic `execute` endpoint was mapping the global `years` context to `years_back` for all methods by default.
- **Consequence**: `PlayerEngine.get_matchups` and `MatchPackGenerator.generate_pack` crashed with `TypeError: ... got an unexpected keyword argument 'years_back'`.
- **Fix**: Updated `ParamMapperService` in `core/services/param_mapper.py` to explicitly exclude `years`/`years_back` for methods that don't accept temporal parameters.
- **Rule**: When adding a new engine method, verify its signature against the `ParamMapperService` logic to ensure only valid arguments are passed.
