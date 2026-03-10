Execute the following cleanup tasks. Delete only the files and directories 
listed below — nothing else. Do not modify any source code files.

After every deletion, run:
  git status --short C:\Cricket_Project_Stable
to confirm only listed files are affected.

FILES AND DIRECTORIES TO DELETE:

1. formats/odi/data/odi.duckdb.prev
2. formats/odi/reports/ — entire directory
3. scripts/fn_results.json
4. scripts/fn_status.txt
5. scripts/signatures.json
6. scripts/linter_report.txt
7. utils/test_recorder.py
8. .gemini/refactor_script.py
9. scripts/maintenance/focus_manager.py
10. scripts/maintenance/memory_manager.py
11. scripts/debug/check_predictor.py
12. scripts/debug/inspect_sigs.py
13. formats/odi/tools/list_india_matches.py
14. temp_pytest/ — entire directory
15. dev/ — entire directory
16. tests/output.txt
17. data_templates/manual_log copy.json
18. formats/odi/renderers/ — entire directory
19. docs/audits/team_engine/ — entire directory
20. docs/audits/player_engine/ — entire directory
21. context_linter.py
22. context_indexer.py
23. Any stale truth_bridge subdirs that are empty

DO NOT TOUCH:
- formats/odi/player_engine.py (strategy loader — must stay)
- formats/odi/team_engine.py (strategy loader — must stay)
- docs/ai/ — human-write-only, do not touch
- frontend/node_modules/
- .git/
- Any file not explicitly listed above

After all deletions, run:
  python core/utils/compliance_bouncer.py --root .

Expected: PASS — 0 violations.

Then commit:
  git add -A
  git commit -m "chore: project cleanup — remove stale artifacts, orphaned scripts, dead audit docs"

Report format:
  Files deleted: {list}
  Files skipped/not found: {list}
  Bouncer: PASS/FAIL
  Commit hash: {hash}