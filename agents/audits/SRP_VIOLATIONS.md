# SRP Violations Allowlist
# Read by core/utils/srp_sentinel.py -- _load_allowlist()
# Format: each file path must appear in a table row as | `path/to/file.py` | ... |
# Paths are POSIX-style relative to the project root.
# Files listed here are treated as advisory (not blocking) by GATE_SRP.

All entries below are pre-existing structural debt, not regressions.
Scheduled for refactor in a future phase when the relevant engine layer is rebuilt.

| File | Score | Rule | Justification |
|---|---|---|---|
| `core/match_pack/interpreters/summary_composer.py` | 3 | SRP_WARNING | Scheduled refactor -- 319 lines, LCOM4=3, multi-domain call sites |
| `core/services/serialization_service.py` | 3 | SRP_WARNING | Scheduled refactor -- LCOM4=8, large class covering multiple output shapes |
| `formats/odi/engines/player/__init__.py` | 3 | SRP_WARNING | Scheduled refactor -- LCOM4=4, aggregation hub for player sub-engines |
| `formats/odi/engines/player/_matchup.py` | 3 | SRP_WARNING | Scheduled refactor -- 718 lines, LCOM4=4, matchup computation is dense |
| `formats/odi/engines/player/_profile.py` | 4 | SRP_WARNING | Scheduled refactor -- 440 lines, LCOM4=2, profile assembly across career/form/venue |
| `formats/odi/engines/team/__init__.py` | 3 | SRP_WARNING | Scheduled refactor -- LCOM4=11, team engine coordinator |
| `formats/odi/engines/team/_venue.py` | 4 | SRP_WARNING | Scheduled refactor -- LCOM4=2, venue analysis combines multiple calculation domains |
| `formats/odi/match_pack/_chapter1.py` | 3 | SRP_WARNING | Scheduled refactor -- 3 import domains, chapter assembly touches data and presentation |
| `formats/odi/match_pack/_formatter.py` | 3 | SRP_WARNING | Scheduled refactor -- 335 lines, LCOM4=7, formats multiple output types |
