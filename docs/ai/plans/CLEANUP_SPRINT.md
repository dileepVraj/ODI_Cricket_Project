# 🏗️ Cleanup Sprint: Engineering Standards Alignment

## 🎯 Goal
Align the ODI format implementation with the **Gold Standard** defined in `docs/guides/ENGINEERING_STANDARDS.md`. No more "Amateur Hour" code.

---

## 🛠️ Phase 1: Headless Engine Refactor
**Objective:** Decouple Logic from UI. Engines should return data, not `<div>` tags.

- [x] **PlayerEngine Refactor:**
    - [x] Add strict type hints to all function signatures.
    - [x] Remove `display()` and `HTML()` from `analyze_player_profile`.
    - [x] Ensure `get_player_profile` returns a strictly typed `PlayerProfile` dataclass.
- [x] **TeamEngine Refactor:**
    - [x] Add strict type hints to all function signatures.
    - [x] Remove all UI logic. Move any residual HTML generation to `formats/odi/renderers/team_renderer.py`.
    - [x] Return `Dict` or `DataFrame` for all analysis methods.

## 🧪 Phase 2: The "Trustless" Expansion
**Objective:** Protect ROI with automated truth verification.

- [x] **Verification Suite:**
    - [x] Expand the Truth Bridge to cover `Player Stats` and `Team Form`.
    - [x] Generate "Golden Master" JSON snapshots for top 10 players and teams.
    - [x] Integrate verification into the `scripts/update_data.py` pipeline (fails ingestion if logic regresses).

## 📈 Phase 3: ROI-Driven Documentation
**Objective:** Document the "Edge".

- [x] **Backtesting Rig (Skeleton):**
    - [x] Create `core/backtester.py` to simulate betting strategies.
    - [x] Document the Hypothesis for the "Dot Ball %" and "Phase Dominance" metrics (Created `docs/hypotheses/ROI_METRICS.md`).

---

## 🚦 Execution Order
1. **Type Hints & PlayerEngine Cleanup** (High Impact, Low Risk) - [x] Done.
2. **TeamEngine Decoupling** (Complexity: High) - [x] Done.
3. **Truth Bridge Expansion** (Safety Net) - Next.
