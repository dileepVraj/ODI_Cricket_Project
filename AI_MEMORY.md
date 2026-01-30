# 🧠 AI Context & Memory Log
**Last Updated:** 2026-01-30
**Current Phase:** Player Profile Enhancement & Bug Fixing

## 📌 Current Architecture State
- **Core Engine:** `CricketAnalyzer` (v2.1) supports hot-reloading and cleaner logging.
- **Player Stats:** `PlayerEngine` now handles Batting vs Bowling contexts cleanly using a Dual-Card UI (Opponent + Venue).
- **Data:** `process_player_stats.py` points to `FINAL_ODI_MASTER.csv` (Zip logic deprecated). `processed_player_stats.csv` contains `at_venue` stats.

## 🚧 Active Tasks (The "To-Do" Stack)
- [x] Enhance Player Profile (Milestones, Bowling Card)
- [x] Debug Venue Stats (GD Phillips @ Indore)
- [ ] Implement Phase Analysis Updates (Next Session)
- [x] Fix Player Form Inconsistency (Deterministic Sorting)

## 🛑 Recent Decisions & Constraints (Why we did this)
- **Compliance:** STRICTLY following `DEV_GUIDE.md` and `GEMINI.md`. No hardcoded colors/strings.
- **Data Integrity:** Re-processed `processed_player_stats.csv` from Master CSV because the Backup Zip was missing/corrupt.
- **UI UX:** Introduced "All Time" label dynamically in Profile when years > 40.
- **Performance:** Removed redundant redundant H2H/Venue logic blocks to fix syntax errors and improve speed.

## 📝 Session History (Reverse Chronological)
- **[2026-01-30] Debugged Venue Stats:** FIXED `process_player_stats.py` to point to correct Master CSV. Verified GD Phillips stats at Indore (111 Runs).
- **[2026-01-30] Enhanced Player Profile:** Updated `core/player_engine.py` to show Batting Milestones (100s/50s) & Bowling Stats (Wkts/Econ). Added Dual-Card View (Opponent + Venue side-by-side).
- **[2026-01-30] Fixed Data Discrepancy:** Resolved RG Sharma double-counting bug by enforcing Role-based filtering in Career Summary.
- **[2026-01-30] Data Pipeline:** Executed "Fresh Data Protocol" (Ingestion & Refinement).
- **[2026-01-30] Bug Fix:** Patched `utils/refinery_script.py` to calculate `is_wicket` column, preventing a crash during Phase 3.
- **[2026-01-30] Bug Fix (Critical):** Resolved "Player Batting Form" inconsistency (DNB vs Score) by implementing deterministic sorting (`Date + MatchID`) and optimized retrieval in `core/player_engine.py`.
- **[2026-01-30] Logic Enhancement:** Fixed "Phantom DNB" issue for active squad players (e.g., JC Buttler) by integrating `MATCH_SQUADS.csv` into `engine.py` and `core/player_engine.py`. This allows perfect distinction between "Did Not Bat" (in squad) and "Absent" (not in squad).
- **[2026-01-30] Ad-Hoc Analysis:** Verified 5-Wicket Haul counts for current squads (SL: 7, ENG: 3) using a custom script, confirming data accuracy for players like PWH de Silva (4) and AU Rashid (2).
- **[2026-01-30] UI Polish:** Fixed invisible slider text in Dark Mode by injecting dynamic CSS for `.widget-readout` in `interface.py`.
