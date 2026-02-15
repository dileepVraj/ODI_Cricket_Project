# 🎯 Implementation Plan: Performance & Purity Refactor (v6.1)

This plan outlines the "Brutal Refactor" to bring the `TeamEngine` up to the standards defined in `ENGINEERING_STANDARDS.md`.

## 🛡️ Objectives
1.  **Vectorization Mandate**: Eliminate `apply()` and `iterrows()` in `TeamEngine`.
2.  **Architectural Purity**: Remove all UI imports (`IPython.display`) from the engine.
3.  **Typed Truth**: Add full type hints to all internal helper methods.

## 📝 Roadmap

### Phase 1: Engine Vectorization
- [ ] Refactor `_generate_matrix_report` to use `np.where` instead of `apply(axis=1)`.
- [ ] Refactor `_get_form_guide` to use vectorized mapping and `np.select`.
- [ ] Verify that performance improves (especially on larger datasets).

### Phase 2: Headless Purity
- [ ] Remove `from IPython.display import display, HTML` from `TeamEngine`.
- [ ] Delete legacy `_display_report` and `_display_audit` methods.
- [ ] Ensure all public methods return strictly typed JSON/Dicts or DataFrames.

### Phase 3: Typed Truth (Internal)
- [ ] Add type hints to `_get_avg_with_count`.
- [ ] Add type hints to `_get_form_guide`.
- [ ] Add type hints to `_calculate_team_stats`.
- [ ] Add type hints to `_generate_matrix_report`.

### Phase 4: Verification & Memory
- [ ] Run Truth Bridge tests to ensure no logic regression.
- [ ] Update `docs/ai/AI_MEMORY.md` with the "Brutal Refactor" status.

---
**Status**: 🚀 Starting Phase 1
**Owner**: AI Assistant (Senior Dev Mode)
