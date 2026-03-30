# AI_MEMORY.md

## Current Architecture State
- **Designer Pipeline:** Gemini (Designer) is operational, focusing on Stitch designs and guide pages.
- **Frontend:** Next.js application in `frontend/` directory.

## Active Tasks
- [x] Retrieve Venue Bias Card redesign from Stitch (ID: 12d88059b3694bbb85fbca6de1ec63b7)
- [x] Capture screenshot of the design for reference (`screenshots/VenueBiasCard-Stitch.png`)
- [x] Redesign VenueBiasCard for Mumbai Wankhede (ID: 6c63bf3b89ab4bd0ac94df8011786239)
- [ ] Implement VenueBiasCard.tsx (Codex - Executor)
- [ ] Verify implementation (Claude - Architect)

## Session History
### 2026-03-26 (VenueBiasCard Redesign - Mumbai)
- **Gemini (Designer):** Redesigned the `VenueBiasCard` in Stitch (Project `11862759278153505832`).
- **Fixes:** Removed blue for data, elevated Confidence Interval, aligned grids, added Score Banding and Toss Recovery modules.
- **Report:** Detailed design decisions written to `agents/workflow/report.md`.
### 2026-03-26 (VenueBiasCard Redesign - Eden)
- **Task:** VenueBiasCard Redesign.
- **Action:**
    - Read `GEMINI.md` and `agents/workflow/designBrief.md` (Mode: design).
    - Audited `frontend/lib/types.ts` for `VenueBiasData` schema consistency.
    - Redesigned `VenueBiasCard` in Stitch (Project: `6709284778558203039`) using Eden Gardens sample data.
    - Implemented 6-zone layout: Hero Split (Zone 1), Metadata (Zone 2), Score Grid (Zone 3), Bias Trend (Zone 4), Toss Intel (Zone 5), and Reliability Logic.
    - Adhered to "Quant-Grade Terminal" standards: Dark theme (#0F172A), sharp corners (4px), Inter/JetBrains Mono font pairing, Cyan/Purple/Green semantic colors.
    - Generated new Stitch screen: `projects/6709284778558203039/screens/095d24d4d9224cd28573ab5e4205b602`.
    - Updated `agents/workflow/report.md` and cleared `designBrief.md`.
- **Files Modified:**
    - `agents/workflow/report.md`
    - `agents/workflow/designBrief.md`
    - `AI_MEMORY.md`
