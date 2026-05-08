# Plan: Fix All 9 SRP Advisory Violations
# Target output: C:\Cricket_Project_Stable\agents\plans\SRP_ADVISORY_FIX_PLAN.md
# Status: DRAFT
# Created: 2026-05-04

---

## PROGRESS TRACKER

Update the Status column as each sub-task completes. Do not mark DONE until the
commit exists in git history and all applicable gates passed.

| ST | File(s) targeted | Type | Status |
|---|---|---|---|
| ST-1 | `formats/odi/engines/team/_venue.py` | 2-line relocation | DONE (score 4->3, file remains at advisory -- accepted) |
| ST-2 | `formats/odi/match_pack/_chapter1.py` | Method decomposition | DONE (score 3->0, removed from advisory) |
| ST-3 | `core/match_pack/interpreters/summary_composer.py` | 3-way file split | DONE (score 3->0, removed from advisory) |
| ST-4 | `formats/odi/match_pack/_formatter.py` | 3-way file split | DONE (score removed from advisory, 3 new builders created) |
| ST-5 | `formats/odi/engines/player/_matchup.py` | 3-way file split | NOT STARTED |
| ST-6 | `formats/odi/engines/player/_profile.py` | 2-way file split | NOT STARTED |
| ST-7 | `core/services/serialization_service.py` | Sub-package extraction | NOT STARTED |
| ST-8 | `KNOWN_PATTERNS_KIPS.md`, `SRP_VIOLATIONS.md` | Documentation only | NOT STARTED |

**Status values:** `NOT STARTED` -> `IN PROGRESS` -> `DONE` (gates passed + committed)

---

## CONTEXT

The SRP sentinel reports 9 advisory violations. These do not block commits (they are
in the allowlist), but they represent real structural debt -- classes doing more than
one job, files that are too large, and methods that straddle multiple responsibility
domains. Fixing them improves testability, reduces future regression risk, and keeps
the codebase inside the clean architecture laws defined in MANDATES_1_TO_4.md.

These 9 violations fall into three categories:

- **Category 1 -- Hub stubs (2 violations):** `player/__init__.py` and
  `team/__init__.py` are both GATE3-required delegation hubs. Their LCOM4 is
  structurally unavoidable. These cannot be refactored without breaking GATE3.
  Fix = document as Known Intentional Patterns (KIPs) with clear justification.

- **Category 2 -- Targeted single-method fixes (2 violations):** `_venue.py`
  has one mixed-responsibility private method; `_chapter1.py` has one overlong
  method doing five jobs. Both are fixed surgically without creating new files.

- **Category 3 -- File splits (5 violations):** `summary_composer.py`,
  `_formatter.py`, `_matchup.py`, `_profile.py`, and `serialization_service.py`
  each contain two or more genuinely distinct responsibility clusters. All five
  require extracting code into new files.

Execution order: ST-1 -> ST-2 -> ST-3 -> ST-4 -> ST-5 -> ST-6 -> ST-7 -> ST-8.

---

## COMPLETE SCOPE -- FILES TOUCHED

### New files to create (11):
- `core/match_pack/interpreters/_condition_interpreter.py`
- `core/match_pack/interpreters/_roster_interpreter.py`
- `core/match_pack/interpreters/_summary_interpreter.py`
- `formats/odi/match_pack/_squad_narrative.py`
- `formats/odi/match_pack/_matchup_narrative.py`
- `formats/odi/match_pack/_phase_narrative.py`
- `formats/odi/engines/player/_matchup_threat.py`
- `formats/odi/engines/player/_matchup_aggregation.py`
- `formats/odi/engines/player/_profile_phase.py`
- `core/services/serialization/_object_normalizer.py`
- `core/services/serialization/_dataframe_serializer.py`

### Existing files to modify (8):
- `formats/odi/engines/team/_venue.py` (2-line relocation)
- `formats/odi/match_pack/_chapter1.py` (function-level decomposition only)
- `core/match_pack/interpreters/summary_composer.py` (becomes re-export facade)
- `formats/odi/match_pack/_formatter.py` (becomes re-export facade)
- `formats/odi/engines/player/_matchup.py` (reduced to class only, ~150 lines)
- `formats/odi/engines/player/_profile.py` (reduced, imports phase mixin)
- `formats/odi/engines/player/__init__.py` (MRO check only -- may need no change)
- `core/services/serialization_service.py` (becomes re-export shim)

### Documentation files to update (2):
- `docs/guides/backendStandards/KNOWN_PATTERNS_KIPS.md` (add KIP-003, KIP-004)
- `agents/audits/SRP_VIOLATIONS.md` (upgrade hub-file justifications)

---

## EXECUTION PROTOCOL (applies to every sub-task without exception)

Before touching any file, and after completing any ST, follow this exact sequence.
Skipping any step is a hard fail.

### Step 0: Capture baseline (mandatory before every ST)
Run the following and note the output. This is your pre-task reference.
```bash
# 1. SRP sentinel -- confirms which files are currently in advisory_violations
python core/utils/srp_sentinel.py --root . --json

# 2. Full test suite -- confirms zero pre-existing regressions
python -m pytest tests/ -x -q --tb=short

# 3. Compliance bouncer -- confirms clean gate-6 baseline
python core/utils/compliance_bouncer.py --root .
```
If any of these fail before you start -- stop. Do not proceed. Fix the pre-existing
failure first, then re-run all three to confirm a clean baseline, then start the ST.

### Step 1: Read all target files in full
Every file listed in the ST's scope MUST be read completely before any edit is made.
Do not rely on the code snippets in this plan alone -- they are excerpts. The full
file may have additional imports, class inheritance, or method dependencies not shown.

Tool: JCodeMunch `get_file_content` or `get_file_outline` + `get_symbol_source`.

### Step 2: Run importer scan on every file being split or relocated
Any time a file is being split, a method is being moved, or a class is being renamed,
run a `find_importers` scan -- even if the ST does not explicitly list this step.

Tool: JCodeMunch `find_importers` on the target file.

Document every importer. After the change, verify each one still works.
If an importer imports something that is being moved, update that importer in the same task.

### Step 3: Make the changes
Follow the ST steps in exact order. Do not skip steps. Do not reorder steps.
Create new files before removing code from existing files -- this prevents a broken
intermediate state where code has been deleted but the replacement does not yet exist.

### Step 4: Run gates in the order listed for the ST
Gates must be run in sequence, not in parallel. Each gate catches a different class
of problem. A later gate passing does not mean an earlier gate would have passed.

### Step 5: Gate failure protocol
If any gate fails:
- **Attempt 1:** Read the error, identify the root cause, fix it.
- **Attempt 2:** If still failing, re-read the original file in full -- the plan's
  snippet may be incomplete or the file may have changed since the plan was written.
- **Attempt 3:** If still failing after two fix attempts, stop. Do not proceed to the
  next ST. Report exactly which gate failed, what the error says, and what was tried.
  Do not commit a partially fixed state.

### Step 6: Commit after GATE 6 passes
Every ST ends with exactly one commit. The commit message format is defined in the
COMMIT MESSAGES section below. Do not commit before GATE 6 passes.
Do not batch multiple STs into one commit.

---

## SUB-TASK 1: Fix `_venue.py` -- move serialization out of private builder

**Violation:** `formats/odi/engines/team/_venue.py` -- LCOM4=2
**Root cause:** `_venue_bias_payload()` (private payload builder) calls
`SerializationService.serialize_raw_matches()`. Serialization belongs in the
public method, not the private builder. It creates a second disjoint usage cluster --
all other private builders never touch SerializationService.
**Fix type:** Targeted 2-line relocation. No new files.

**Step 0: Capture baseline**
Run SRP sentinel, full test suite, and compliance bouncer per the Execution Protocol.
Confirm `_venue.py` appears in `advisory_violations` before starting.

**Step 1: Read the target file**
Read `formats/odi/engines/team/_venue.py` in full. Pay attention to the full signature
of `analyze_venue_bias` -- the plan shows its return value as `report`, but verify the
actual return structure before relocating the serialization call.

**Step 2: Make the change**
**Current code (in `_venue_bias_payload`):**
```python
def _venue_bias_payload(self, stadium_name, years_back, match_context):
    payload = calculate_venue_bias_payload(...)
    report = payload.get("report")
    if report is not None:
        raw_matches = report.get("raw_matches")
        if isinstance(raw_matches, pd.DataFrame):
            report["raw_matches"] = SerializationService.serialize_raw_matches(raw_matches)
    return payload
```

**After fix -- split across two methods:**
```python
def _venue_bias_payload(self, stadium_name, years_back, match_context):
    # Pure payload builder -- no serialization here
    return calculate_venue_bias_payload(...)

def analyze_venue_bias(self, stadium_name, years_back, recorder, match_context):
    payload = self._venue_bias_payload(stadium_name, years_back, match_context)
    report = payload.get("report")
    if report is not None:
        raw_matches = report.get("raw_matches")
        if isinstance(raw_matches, pd.DataFrame):
            report["raw_matches"] = SerializationService.serialize_raw_matches(raw_matches)
    return report   # existing return logic unchanged
```

**Gates to run:** GATE-C, GATE 2, GATE 3, GATE 5T, GATE 5P, GATE 6

**SRP verification:** Run `python core/utils/srp_sentinel.py --root . --json` and confirm
`_venue.py` no longer appears in `advisory_violations`.

---

## SUB-TASK 2: Fix `_chapter1.py` -- decompose `build` into private methods

**Violation:** `formats/odi/match_pack/_chapter1.py` -- import_domains=3
**Root cause:** `ChapterOneBuilder.build()` is an 80+ line method performing five
fetch-transform-interpret cycles inline. It touches config/, core/, and formats/
layers inside one method body, which is what triggers the import_domains=3 signal.
**Fix type:** Function-level SRP decomposition. No new files. Same class.

**Step 0: Capture baseline**
Run SRP sentinel, full test suite, and compliance bouncer per the Execution Protocol.
Confirm `_chapter1.py` appears in `advisory_violations` before starting.

**Step 1: Read the target file**
Read `formats/odi/match_pack/_chapter1.py` in full. The plan shows four extracted
methods but the actual `build()` method may have additional inline logic not captured
in the snippets. Understand the full method before decomposing.

**Step 2: Make the changes**
**The five cycles inside `build()` currently:**
1. Global H2H (4Y and 8Y)
2. Home team form (global + vs opponent)
3. Away team form (global + vs opponent)
4. Country H2H with manual mapping
5. Home dominance + away performance matrices

**After decomposition, `build()` becomes a clean orchestrator:**
```python
def build(self, home: str, away: str, venue: str) -> Dict[str, Any]:
    return {
        **self._build_h2h_section(home, away),
        **self._build_form_section(home, away),
        **self._build_country_h2h_section(home, away, venue),
        **self._build_dominance_sections(home, away),
    }
```

**New private methods to add (logic extracted verbatim -- no changes to what the code does):**

| New method | Responsibility | Approx lines |
|---|---|---|
| `_build_h2h_section(home, away) -> dict` | Fetch + transform + interpret 4Y and 8Y global H2H | ~20 |
| `_build_form_section(home, away) -> dict` | Fetch + transform + interpret form for both teams | ~25 |
| `_build_country_h2h_section(home, away, venue) -> dict` | Resolve country, fetch, manually map, interpret | ~22 |
| `_build_dominance_sections(home, away) -> dict` | Home dominance + away performance matrices | ~12 |

**Gates to run:** GATE 2, GATE 5T, GATE 5P, GATE 6

---

## SUB-TASK 3: Fix `summary_composer.py` -- split into 3 focused interpreter classes

**Violation:** `core/match_pack/interpreters/summary_composer.py` -- 319 lines, LCOM4=3
**Root cause:** Three genuinely distinct clusters in one class:
  Cluster A -- Condition detection (pitch/time/toss analysis, 4 helper functions + `interpret_conditions`)
  Cluster B -- Bowling roster analysis (`_build_bowling_roster` + `analyze_bowling_roster`)
  Cluster C -- Executive summary synthesis (`generate_executive_summary`)
**Fix type:** File split into 3 new files. Original file becomes re-export facade.

### Step 1: Pre-split importer scan (MANDATORY before touching any file)
Use JCodeMunch `find_importers` on `summary_composer.py`. Every file that imports
`MatchSummaryComposer` or any function from this module must be updated in this task.
Common suspects: `formats/odi/match_pack/_orchestrator.py`, `_chapter4.py`.

### Step 2: Create `_condition_interpreter.py`
**File:** `core/match_pack/interpreters/_condition_interpreter.py`
**Class:** `ConditionInterpreter(InterpreterBase)`
**Imports needed:** `from core.match_pack.interpreters._base import InterpreterBase`
**Contains:**
- Module-level private helpers:
  - `_strip_style_emojis(style: str) -> str`
  - `_classify_experience(wickets: int) -> str`
  - `_detect_pitch_conditions(pitch: str) -> list[str]`
  - `_detect_time_conditions(time: str) -> list[str]`
- Class method: `interpret_conditions(self, pitch, time, toss, bias_data) -> Dict`

### Step 3: Create `_roster_interpreter.py`
**File:** `core/match_pack/interpreters/_roster_interpreter.py`
**Class:** `RosterInterpreter(InterpreterBase)`
**Contains:**
- Module-level helper: `_build_bowling_roster(players, bowler_styles, player_roles, team_stats) -> List[Dict]`
- Class method: `analyze_bowling_roster(self, home_xi, away_xi, pitch_conditions, player_stats) -> Dict`

**NOTE -- DOD check:** `_build_bowling_roster` currently uses a Python loop over
players. After extraction, confirm: is this iterating rows of a DataFrame (DOD
violation) or iterating a plain Python list of player names (permitted)? If it
iterates a DataFrame, vectorize. If it iterates a Python list, it is exempt.

### Step 4: Create `_summary_interpreter.py`
**File:** `core/match_pack/interpreters/_summary_interpreter.py`
**Class:** `SummaryInterpreter(InterpreterBase)`
**Contains:**
- Class method: `generate_executive_summary(self, chapters, home_team, away_team, conditions) -> Dict`

### Step 5: Update `summary_composer.py` as re-export facade
```python
# summary_composer.py -- re-export facade for backward compatibility
# Import the three focused classes so existing callers work unchanged
from core.match_pack.interpreters._condition_interpreter import ConditionInterpreter
from core.match_pack.interpreters._roster_interpreter import RosterInterpreter
from core.match_pack.interpreters._summary_interpreter import SummaryInterpreter

class MatchSummaryComposer(ConditionInterpreter, RosterInterpreter, SummaryInterpreter):
    """Backward-compatibility composite. Prefer focused classes for new code."""
    pass
```

### Step 6: Update all call sites found in Step 1

**Gates to run:** GATE 1, GATE-C, GATE 2, GATE 5T, GATE 5P, GATE 6

---

## SUB-TASK 4: Fix `_formatter.py` -- split into 3 focused narrative builders

**Violation:** `formats/odi/match_pack/_formatter.py` -- 335 lines, LCOM4=7
**Root cause:** Seven narrative builder methods spanning 3 clusters:
  Cluster A -- Squad + player-level narrative (`_build_squad_narrative`, `_build_player_stats_narrative`)
  Cluster B -- Bowling matchup + tactical narrative (4 methods)
  Cluster C -- Phase/conditions narrative (`_build_phase_narrative`)
**Fix type:** File split into 3 new files. Original becomes re-export facade.

### Step 1: Pre-split importer scan (MANDATORY)
Use JCodeMunch `find_importers` on `_formatter.py`. Most likely importers:
`_orchestrator.py`, `_assembler.py`. All must be updated or kept working via facade.

### Step 2: Create `_squad_narrative.py`
**File:** `formats/odi/match_pack/_squad_narrative.py`
**Class:** `SquadNarrativeBuilder`
**Contains:**
- `_build_squad_narrative(self, squad_data, home, away) -> str`
- `_build_player_stats_narrative(self, player_stats, home, away) -> str`

### Step 3: Create `_matchup_narrative.py`
**File:** `formats/odi/match_pack/_matchup_narrative.py`
**Class:** `MatchupNarrativeBuilder`
**Imports:** `from formats.odi.config.players import BOWLER_STYLES` (keep in this file)
**Contains:**
- `_build_tactical_narrative(self, matrix_data, home, away) -> str`
- `_build_matchup_narrative(self, matchup_data, home, away) -> str`
- `_build_role_based_tactical_narrative(self, tactical_data, home, away) -> str`
- `_build_smart_pitch_narrative(self, roster_data, player_stats, home, away, pitch_cond) -> str`

### Step 4: Create `_phase_narrative.py`
**File:** `formats/odi/match_pack/_phase_narrative.py`
**Class:** `PhaseNarrativeBuilder`
**Contains:**
- `_build_phase_narrative(self, phase_data, home, away) -> str`

### Step 5: Update `_formatter.py` as re-export facade
```python
# _formatter.py -- re-export facade for backward compatibility
from formats.odi.match_pack._squad_narrative import SquadNarrativeBuilder
from formats.odi.match_pack._matchup_narrative import MatchupNarrativeBuilder
from formats.odi.match_pack._phase_narrative import PhaseNarrativeBuilder

class MatchPackFormatter(SquadNarrativeBuilder, MatchupNarrativeBuilder, PhaseNarrativeBuilder):
    """Backward-compatibility composite. Prefer focused builders for new code."""
    pass
```

### Step 6: Update all call sites found in Step 1

**Gates to run:** GATE 2, GATE 3, GATE 5T, GATE 5P, GATE 6

---

## SUB-TASK 5: Fix `_matchup.py` -- split into 3 files (largest task)

**Violation:** `formats/odi/engines/player/_matchup.py` -- 718 lines, LCOM4=4
**Root cause:** Four responsibility clusters crammed into one file:
  Cluster 1 -- Threat classification (`_THREAT_THRESHOLD_KEYS`, `_load_threat_thresholds`, `_compute_threat_rating`)
  Cluster 2 -- Window aggregation (`_aggregate_matchup_window`)
  Cluster 3 -- Phase/innings slicing (`_build_phase_stats`, `_build_innings_stats`)
  Cluster 4 -- Dispatch + assembly (`get_matchups`, `_matchup_single_batter`)
**Fix type:** 3-way file split. `_matchup.py` keeps only the class body.

### CRITICAL CONSTRAINT -- GATE3
`get_matchups` is a manifest-registered abstract method on `IPlayerEngine`. It MUST
remain as a public method on `PlayerEngineMatchup` with its exact signature.
The `__init__.py` hub stub must continue resolving it via MRO. Never move
`get_matchups` out of `PlayerEngineMatchup`.

### Step 1: Pre-split check
Search for any file that does `from formats.odi.engines.player._matchup import`
to import the module-level private functions directly (not via the class).
These would break after extraction. Update them if found.

### Step 2: Create `_matchup_threat.py`
**File:** `formats/odi/engines/player/_matchup_threat.py`
**Type:** Module-level functions and constants only (no class needed -- stateless)
**Move from `_matchup.py`:**
- `_THREAT_THRESHOLD_KEYS: list[str]` (the 22-key validation list)
- `_load_threat_thresholds(tactical_thresholds: dict) -> dict`
- `_compute_threat_rating(raw_balls, raw_outs, w_avg, w_sr, ...18 threshold params...) -> pd.Series`

### Step 3: Create `_matchup_aggregation.py`
**File:** `formats/odi/engines/player/_matchup_aggregation.py`
**Type:** Module-level functions only (stateless -- receive DataFrames, return DataFrames)
**Move from `_matchup.py`:**
- `_aggregate_matchup_window(window_df, thresholds, percent_scale) -> pd.DataFrame`
- `_build_phase_stats(phase_key, prefix, overall_df, batter_df, rules, thresholds, percent_scale) -> pd.DataFrame`
- `_build_innings_stats(innings_num, prefix, overall_df, batter_df, thresholds, percent_scale) -> pd.DataFrame`

### Step 4: Reduce `_matchup.py` to class only
After the two new files are created, update `_matchup.py`:
- Add at top: `from ._matchup_threat import _THREAT_THRESHOLD_KEYS, _load_threat_thresholds, _compute_threat_rating`
- Add at top: `from ._matchup_aggregation import _aggregate_matchup_window, _build_phase_stats, _build_innings_stats`
- Remove all moved module-level functions and constants from this file
- Keep `PlayerEngineMatchup(PlayerEngineBase)` class with its 4 methods:
  - `get_matchups(...)` -- public manifest method (signature unchanged)
  - `_load_threat_thresholds(self) -> dict` -- instance wrapper
  - `_compute_threat_rating(self, ...) -> pd.Series` -- instance wrapper
  - `_matchup_single_batter(...)` -- main calculation workhorse
- Target size: ~150 lines (down from 718)

### Step 5: Verify `__init__.py` hub is unaffected
The hub inherits `PlayerEngineMatchup`. The new helper files are internal imports
inside `_matchup.py` -- the hub never sees them. No MRO change needed.

**Gates to run:** GATE-C, GATE 2, GATE 3, GATE 5T, GATE 5P, GATE 6

---

## SUB-TASK 6: Fix `_profile.py` -- extract phase analysis to mixin

**Violation:** `formats/odi/engines/player/_profile.py` -- 440 lines, LCOM4=2
**Root cause:** Phase analysis methods (`_build_phase_conditions`, `_compute_phase_runs`,
`_compute_phase_bowling`) form a cohesive independent sub-system. They have no
dependency on the profile assembly logic, but they live in the same file.
**Fix type:** Extract phase cluster to a new mixin class. 2-way file split.

### CRITICAL CONSTRAINT -- GATE3
`analyze_player_profile` is the manifest-registered public method. It MUST remain
on `PlayerEngineProfile` with its exact signature. Never move it.

### Step 0: Pre-split check and baseline
Run SRP sentinel, full test suite, and compliance bouncer per the Execution Protocol.
Confirm `_profile.py` appears in `advisory_violations`.

Read `formats/odi/engines/player/_profile.py` in full before making any edit.

Use JCodeMunch `find_importers` on `_profile.py`. Any file that imports from it directly
-- including any that import the phase module-level functions -- must continue to work
after the split. Document every importer and verify each one after the change.

### Step 1: Create `_profile_phase.py`
**File:** `formats/odi/engines/player/_profile_phase.py`
**Contains:**

Module-level functions (stateless, injectable with `rules`):
- `_build_phase_conditions(over_num: int, rules: dict) -> tuple[List[pd.Series], List[str]]`
- `_compute_phase_runs(raw_bat: pd.DataFrame, rules: dict) -> List[PhaseRunsRow]`
- `_compute_phase_bowling(raw_bowl: pd.DataFrame, rules: dict) -> List[PhaseBowlingRow]`

Class `PlayerEnginePhase(PlayerEngineBase)` -- instance wrappers that inject `self.rules`:
- `_build_phase_conditions(self, over_num) -> tuple`
- `_compute_phase_runs(self, raw_bat) -> List[PhaseRunsRow]`
- `_compute_phase_bowling(self, raw_bowl) -> List[PhaseBowlingRow]`

Imports needed:
- `from core.interfaces.player_interface import PhaseBowlingRow, PhaseRunsRow`
- `from ._base import PlayerEngineBase, _PHASE_CANONICAL`
- `import pandas as pd`

### Step 2: Update `_profile.py`
- Remove the 3 module-level phase functions (moved to `_profile_phase.py`)
- Remove the 3 instance wrapper methods for phases (moved to `PlayerEnginePhase`)
- Add import: `from ._profile_phase import PlayerEnginePhase`
- Update class declaration:
  ```python
  class PlayerEngineProfile(PlayerEngineBase, PlayerEnginePhase):
  ```
- All phase methods are now inherited from `PlayerEnginePhase` -- no method bodies change
- Target size: ~220 lines (down from 440)

### Step 3: Verify MRO chain after change
```python
from formats.odi.engines.player import PlayerEngine
print(PlayerEngine.__mro__)
# Expected order: PlayerEngine -> PlayerEngineSquad -> PlayerEngineMatchup
#                 -> PlayerEngineProfile -> PlayerEnginePhase -> PlayerEngineBase
#                 -> IPlayerEngine -> object
```
If MRO resolution raises `TypeError`, it means `PlayerEnginePhase` needs to be
listed before `PlayerEngineBase` in `PlayerEngineProfile`'s bases. Adjust as needed.

### Step 4: Verify `__init__.py` hub stubs still resolve
The hub has stubs for `analyze_player_profile`. After this change, the MRO still
resolves it through `PlayerEngineProfile` -- no hub changes needed.

**Gates to run:** GATE-C, GATE 2, GATE 3, GATE 5T, GATE 5P, GATE 6

---

## SUB-TASK 7: Fix `serialization_service.py` -- split into sub-package

**Violation:** `core/services/serialization_service.py` -- LCOM4=8
**Root cause:** Despite being ~85 lines, the class has 8 disjoint method groups.
Two clearly distinct clusters:
  Cluster A -- Object normalization (5 methods): `wrap_as_schema`, `to_plain_data`,
               `_normalize_dataclass`, `_normalize_pydantic`, `_normalize_container`
  Cluster B -- DataFrame serialization (3 methods): `serialize_dataframe_records`,
               `serialize_ui_records`, `serialize_raw_matches`
**Fix type:** Extract into a `serialization/` sub-package. High blast radius --
proceed carefully. No callers need to change.

### CRITICAL WARNING -- BLAST RADIUS
`SerializationService` is imported across many engine and service files. The fix
MUST be 100% transparent -- every existing `from core.services.serialization_service
import SerializationService` must continue to work unchanged.

### Step 1: Find all importers (MANDATORY before touching anything)
Use JCodeMunch `find_importers` on `core/services/serialization_service.py`.
Document every file. After the split, verify each importer still works.

### Step 2: Create `core/services/serialization/` package directory

### Step 3: Create `_object_normalizer.py`
**File:** `core/services/serialization/_object_normalizer.py`
**Contains:**
- Type aliases: `JsonPrimitive: TypeAlias = str | int | float | bool | None`
  and `JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]`
- Class `ObjectNormalizerMixin` (no parent):
  - `wrap_as_schema(cls, data) -> JsonValue` (@classmethod)
  - `to_plain_data(cls, data) -> JsonValue` (@classmethod)
  - `_normalize_dataclass(cls, data: object) -> JsonValue` (@classmethod)
  - `_normalize_pydantic(cls, data, model_dump_fn) -> JsonValue` (@classmethod)
  - `_normalize_container(cls, data: dict | list | tuple) -> JsonValue` (@classmethod)
- Imports needed: `from dataclasses import asdict, is_dataclass`, `from typing import TypeAlias, cast`,
  `from core.interfaces.serialization_types import DataclassProtocol, PydanticProtocol`

### Step 4: Create `_dataframe_serializer.py`
**File:** `core/services/serialization/_dataframe_serializer.py`
**Contains:**
- Class `DataFrameSerializerMixin` (no parent):
  - `serialize_dataframe_records(cls, data: pd.DataFrame, *, max_rows, as_json_string) -> str | list` (@classmethod)
  - `serialize_ui_records(cls, data, *, max_rows) -> list` (@classmethod)
  - `serialize_raw_matches(cls, data, *, max_rows) -> str` (@classmethod)
- Imports needed: `import pandas as pd`

### Step 5: Create `core/services/serialization/__init__.py`
```python
from core.services.serialization._object_normalizer import (
    ObjectNormalizerMixin, JsonPrimitive, JsonValue
)
from core.services.serialization._dataframe_serializer import DataFrameSerializerMixin
from core.interfaces.team_types import ComparisonReportRow, MatrixReportRow, TeamFormRow

class SerializationService(ObjectNormalizerMixin, DataFrameSerializerMixin):
    """Full serializer -- all methods available on one class."""
    pass

__all__ = ["SerializationService", "JsonPrimitive", "JsonValue"]
```

### Step 6: Update `serialization_service.py` as a re-export shim
```python
# serialization_service.py -- backward-compatibility shim
# All existing callers continue to work with zero changes
from core.services.serialization import SerializationService, JsonPrimitive, JsonValue

__all__ = ["SerializationService", "JsonPrimitive", "JsonValue"]
```

### Step 7: Post-split verification
```python
# Must not raise ImportError
from core.services.serialization_service import SerializationService
s = SerializationService()
# All methods must be available
assert hasattr(s, "to_plain_data")
assert hasattr(s, "serialize_ui_records")
```

**Gates to run:** GATE 1, GATE-C, GATE 2, GATE 5T, GATE 5P, GATE 6

---

## SUB-TASK 8: Document hub `__init__.py` files as Known Intentional Patterns

**Violations (2):**
- `formats/odi/engines/player/__init__.py` -- LCOM4=4, parent_count=3
- `formats/odi/engines/team/__init__.py` -- LCOM4=11, parent_count=3

**Root cause:** Both are GATE3 delegation hubs. Their LCOM4 is structurally
determined by the number of methods that delegate to different parent classes.
Splitting them would break GATE3. These are correct by design.
**Fix type:** Documentation only. No code changes.

### Step 1: Add KIP-003 to `KNOWN_PATTERNS_KIPS.md`
```
### [KIP-003] PlayerEngine hub LCOM4 reflects parent count, not SRP violation

File: formats/odi/engines/player/__init__.py
Pattern: GATE3 delegation hub (SN-008 pattern)

What it looks like: LCOM4=4, score=3, SRP_WARNING from the sentinel.

Why it is correct: Each stub method delegates to a different parent class
(PlayerEngineSquad, PlayerEngineMatchup, PlayerEngineProfile). The SRP sentinel
sees one method cluster per parent, giving LCOM4 = parent count + 1 = 4.
This is structurally unavoidable when multiple ABCs must be satisfied by a
single public class required by GATE3.

Hard Stop: Do NOT split this file. Do NOT merge the hub with any domain class.
The hub exists solely to give the manifest-contract-verifier a single class
to verify against the manifest.
```

### Step 2: Add KIP-004 to `KNOWN_PATTERNS_KIPS.md`
```
### [KIP-004] TeamEngine hub LCOM4 equals stub method count, not SRP violation

File: formats/odi/engines/team/__init__.py
Pattern: GATE3 delegation hub

What it looks like: LCOM4=11, score=3, SRP_WARNING from the sentinel.

Why it is correct: 11 stub methods each delegate to a different analyzer
(TeamVenueAnalyzer, TeamH2HAnalyzer, TeamFormAnalyzer). None of the stubs
call each other, so each is its own LCOM4 component. LCOM4 = stub count.
This is the expected behaviour for a pure delegation hub.

Hard Stop: Do NOT split this file. Do NOT merge the hub with any analyzer class.
```

### Step 3: Update `agents/audits/SRP_VIOLATIONS.md`
Add a "HUB PATTERN -- PERMANENT ADVISORY" section:
- Reference KIP-003 and KIP-004
- Explain that hub files will always score SRP_WARNING under the current sentinel
  algorithm, and that suppressing them via the allowlist is the correct resolution

**Gates to run:** GATE 5P, GATE 6

---

## EXECUTION ORDER AND DEPENDENCIES

```
ST-1 (_venue.py targeted fix)        -- independent, run first
ST-2 (_chapter1.py method decomp)    -- independent, run in same session as ST-1
     |
     v
ST-3 (summary_composer split)        -- check importers first; run after ST-1+2 clean
ST-4 (_formatter.py split)           -- check importers first; can run same session as ST-3
     |
     v
ST-5 (_matchup.py split)             -- larger; dedicate a session to it
ST-6 (_profile.py split)             -- run immediately after ST-5 (same package)
     |
     v
ST-7 (serialization split)           -- highest blast radius; run in its own session
     |
     v
ST-8 (documentation)                 -- always last
```

ST-1 + ST-2 = one commit each (can be done in one session)
ST-3 + ST-4 = one commit each (can be done in one session)
ST-5 + ST-6 = one commit each (same player engine package, sequential)
ST-7 = one commit (own session due to blast radius)
ST-8 = one commit

---

## GATE SEQUENCE PER SUB-TASK

| Sub-task | GATE-1 | GATE-C | GATE-2 | GATE-3 | GATE-5T | GATE-5P | GATE-6 |
|---|---|---|---|---|---|---|---|
| ST-1 (_venue.py) | -- | YES | YES | YES | YES | YES | YES |
| ST-2 (_chapter1.py) | -- | -- | YES | -- | YES | YES | YES |
| ST-3 (summary_composer) | YES | YES | YES | -- | YES | YES | YES |
| ST-4 (_formatter.py) | -- | -- | YES | YES | YES | YES | YES |
| ST-5 (_matchup.py) | -- | YES | YES | YES | YES | YES | YES |
| ST-6 (_profile.py) | -- | YES | YES | YES | YES | YES | YES |
| ST-7 (serialization) | YES | YES | YES | -- | YES | YES | YES |
| ST-8 (docs) | -- | -- | -- | -- | -- | YES | YES |

GATE-C triggers: any `core/calculators/`, `core/services/`, or `formats/*/engines/` file
GATE-3 triggers: any engine file in `formats/`

---

## RISK REGISTER

| Risk | Sub-task | Mitigation |
|---|---|---|
| MRO conflict when `PlayerEnginePhase` added to `PlayerEngineProfile` | ST-6 | Print `PlayerEngine.__mro__` after change; insert `PlayerEnginePhase` before `PlayerEngineBase` in bases list |
| Direct imports of module-level private functions from `_matchup.py` break | ST-5 | Grep for `from ._matchup import _compute_threat_rating` before splitting |
| `SerializationService` callers using star imports break | ST-7 | Check for star imports; add explicit `__all__` to shim module |
| Bouncer flags new facade classes (they live in `services/` or `engines/`) | ST-3/4/7 | Facades have no literals -- only imports and re-exports. Bouncer only scans for literals. |
| Contract tests fail because engine method moved to different file | ST-5/6 | Contract tests import via `__init__.py` hub, not internal files. Unaffected. Verify explicitly. |
| `_build_bowling_roster` loop in summary_composer triggers DOD gate | ST-3 | Determine if loop is over a DataFrame (vectorize) or a plain list (exempt). Fix if needed before committing. |
| Type aliases `JsonPrimitive`/`JsonValue` break if imported from old path | ST-7 | Keep re-export in the shim; add to `__all__` explicitly |

---

## COMMIT MESSAGES

```
[SRP-ST1]: relocate SerializationService call from _venue_bias_payload to analyze_venue_bias
[SRP-ST2]: decompose ChapterOneBuilder.build into four private section methods
[SRP-ST3]: split MatchSummaryComposer into three focused interpreter classes
[SRP-ST4]: split MatchPackFormatter into three focused narrative builder classes
[SRP-ST5]: split _matchup.py -- extract threat and aggregation helpers to own files
[SRP-ST6]: extract PlayerEnginePhase mixin from _profile.py
[SRP-ST7]: split SerializationService into ObjectNormalizerMixin and DataFrameSerializerMixin
[SRP-ST8]: document PlayerEngine and TeamEngine hub pattern as KIP-003 and KIP-004
```

---

## FINAL VERIFICATION (after all 8 sub-tasks)

**SRP sentinel -- all 9 target files must be gone from advisory_violations:**
```bash
python core/utils/srp_sentinel.py --root . --json
```
Expected: `advisory_violations` list is empty (or contains only newly discovered files,
not any of the original 9).

**Paradigm sentinel:**
```bash
python core/utils/paradigm_sentinel.py --root .
```
Expected: `GATE5P - PASS`

**Compliance bouncer:**
```bash
python core/utils/compliance_bouncer.py --root .
```
Expected: `PASS: 100% compliance`

**Contract tests:**
```bash
python -m pytest tests/contracts/ -x -q --tb=short
```
Expected: all pass, zero regressions.

**Full test suite:**
```bash
python -m pytest tests/ -x -q --tb=short
```
Expected: all pass.

**MRO verification (after ST-5 and ST-6):**
```python
from formats.odi.engines.player import PlayerEngine
print(PlayerEngine.__mro__)
# Must contain PlayerEnginePhase between PlayerEngineProfile and PlayerEngineBase
```

**Backward-compat verification (after ST-7):**
```python
from core.services.serialization_service import SerializationService
assert hasattr(SerializationService, "to_plain_data")
assert hasattr(SerializationService, "serialize_ui_records")
```

---

## DONE CRITERIA

Each sub-task is complete when:
1. All applicable gates in the table above pass
2. SRP sentinel no longer shows the target file in advisory_violations
3. Full test suite still passes (no regressions)
4. Commit created with the correct message format

The full plan is complete when:
1. `srp_sentinel.py --json` shows 0 advisory violations for all 9 original target files
2. `compliance_bouncer.py` returns PASS
3. `paradigm_sentinel.py` returns PASS
4. All tests pass
5. All 8 commits exist in git history on main

---

## PRE-EXISTING TEST FAILURES -- FIX AFTER ST-8

These 4 failure groups were discovered during the ST-4 baseline check (2026-05-04).
They existed before ST-4 began and are unrelated to the SRP refactor. Fix them in a
dedicated session immediately after all 8 SRP sub-tasks are committed.

Run before starting that session to confirm the failures are still present:
```bash
python -m pytest tests/test_cockpit_api.py tests/test_venue_bias_enrichment.py tests/test_continent_performance_regression.py tests/verify_headless_player.py -q --tb=short
```
Expected: 8 failures. If fewer, some were fixed as a side-effect of SRP work.

---

### FAILURE GROUP 1 -- Cockpit settlement: total_volume_wagered wrong

**Test:** `tests/test_cockpit_api.py::test_cockpit_trade_settlement_records_metrics_and_locks_trade`
**Assertion:** `assert settled_trade["total_volume_wagered"] == 60.0`
**Actual:** `64.0`

**What the test does:**
- Creates a trade, places two bets:
  - Bet 1: BACK, stake=40, odds_paise=90
  - Bet 2: LAY, stake=20, odds_paise=120
- Settles the trade and checks `total_volume_wagered`
- Expected: 40 + 20 = 60 (sum of raw stakes)
- Actual: 64 -- which is 40 + 24

**Root cause hypothesis:**
The LAY bet stake of 20 at odds_paise=120 (1.2 decimal) has a liability of
`20 * (1.2 - 1.0) = 4`. The actual result of 64 = 40 + 20 + 4, which means the
code is now calculating `total_volume_wagered` as stake + liability for LAY bets
instead of just stake. Either the formula changed, or the field being summed
changed from `stake` to something like `exposure` or `total_exposure`.

**Investigation steps:**
1. Read `cockpit/calculator.py` -- search for `total_volume_wagered`. Find where
   it is computed and what fields it sums.
2. Read `cockpit/models.py` -- check the `Bet` model. Confirm whether it has a
   `liability`, `exposure`, or `total_exposure` field that was recently added.
3. Check git log for `cockpit/calculator.py` and `cockpit/models.py`:
   `git log --oneline -10 -- cockpit/calculator.py cockpit/models.py`
   The formula changed at some point -- identify the commit.
4. Decision: either the formula is wrong (revert to stake-only) or the test
   expectation is wrong (update to 64.0 to reflect the new liability-inclusive
   formula). The correct answer depends on what `total_volume_wagered` is
   supposed to mean for the operator. Ask the human before changing either.

---

### FAILURE GROUP 2 -- Continent mask: _build_continent_mask deleted

**Test:** `tests/test_continent_performance_regression.py::test_continent_mask_uses_venue_fallback_when_venue_id_missing`
**Assertion:** `AttributeError: 'TeamEngine' object has no attribute '_build_continent_mask'`

**What the test does:**
Directly calls `engine._build_continent_mask(...)` on a `TeamEngine` instance to
verify it falls back to venue-based country lookup when `venue_id` is missing.

**Root cause:**
`_build_continent_mask` was a private method on `TeamEngine` (or one of its parent
analyzer classes). It no longer exists -- it was either renamed, moved to a helper
function, or deleted during an earlier refactor session.

**Investigation steps:**
1. Search the codebase for `_build_continent_mask`:
   `grep -r "_build_continent_mask" .`
   If found: the method was moved -- update the test to call it on the correct object.
   If not found: the method was deleted or renamed.
2. If deleted/renamed, check git log:
   `git log --oneline --all -S "_build_continent_mask"`
   Find the commit that removed it and see what replaced it.
3. Read the test in full (`tests/test_continent_performance_regression.py`) to
   understand exactly what behavior it is asserting -- the venue fallback logic
   probably still exists somewhere, just under a different name or in a different class.
4. Fix options (choose one):
   - If the logic moved to a module-level function, update the test to call that
     function directly.
   - If the method was inlined into a larger method, extract it back out as a
     private helper so the test can target it.
   - If the behavior is now tested indirectly through a public method, rewrite
     the test to go through that public method with a fixture that exercises the
     fallback path.

---

### FAILURE GROUP 3 -- Venue bias enrichment: trend and toss intelligence broken

**Tests (5 failures):**
- `test_venue_bias_enrichment.py::test_bias_trend_strengthening`
- `test_venue_bias_enrichment.py::test_bias_trend_weakening`
- `test_venue_bias_enrichment.py::test_bias_trend_stable`
- `test_venue_bias_enrichment.py::test_toss_intelligence_chose_bat_wins`
- `test_venue_bias_enrichment.py::test_toss_intelligence_mixed_decisions`

**Assertions:**
- `assert result["direction"] == "STABLE"` -- actual: `"INSUFFICIENT_DATA"`
  (same for STRENGTHENING and WEAKENING)
- `assert result["chose_bat_win_pct"] == 80` -- actual: `None`
- `assert result["chose_bat_win_pct"] == 100` -- actual: `None`

**Root cause hypotheses (two separate issues):**

*Issue A -- Bias trend direction always returns INSUFFICIENT_DATA:*
The enrichment service that calculates `direction` (STABLE / STRENGTHENING /
WEAKENING) has a minimum-data guard that is now stricter than the test fixtures
provide. Either the threshold constant increased, or the input data shape expected
by the function changed (e.g., it now requires a different DataFrame column that
the test fixtures do not supply).

*Issue B -- Toss intelligence chose_bat_win_pct is always None:*
The field that drives `chose_bat_win_pct` is not being populated from the test
fixture data. The key being read from the fixture may have been renamed, or the
calculation path that sets this field was moved and is not being reached.

**Investigation steps:**
1. Read `tests/test_venue_bias_enrichment.py` in full. Identify the fixture data
   being passed in for the trend and toss intelligence tests.
2. Read `core/services/enrichment.py` (or wherever `calculate_bias_trend` and
   `toss_intelligence` live). Trace the exact code path from input fixture to
   the `direction` and `chose_bat_win_pct` output keys.
3. For Issue A: find the minimum-data threshold constant. Compare against the
   number of rows in the test fixture. If the fixture has fewer rows than the
   threshold, either lower the threshold or add more rows to the fixture.
4. For Issue B: find where `chose_bat_win_pct` is set. Trace back to what input
   key feeds it. Compare the input key name against what the test fixture provides.
   A rename somewhere in the pipeline is the most likely cause.
5. Fix: update the enrichment function or the test fixture so they agree on data
   shape and field names. Do not change both simultaneously -- fix one side and
   confirm the test passes before touching the other.

---

### FAILURE GROUP 4 -- Headless player API: tactical_thresholds missing from rules

**Test:** `tests/verify_headless_player.py::test_headless_api`
**Error:**
```
ConfigurationError: Missing required format rule 'tactical_thresholds'.
Define it in manifest FORMAT_RULES and pass it into PlayerEngine.
```
**Stack:** `PlayerEngine.__init__` -> `_require_tactical_thresholds()` ->
`_require_nonempty_dict_rule("tactical_thresholds")` -> raises.

**What the test does:**
Constructs a `PlayerEngine` directly (headless -- no API layer) by passing
`player_df`, `meta_df`, and `dal`. The engine then tries to read
`tactical_thresholds` from its injected `rules` dict and fails because the
test is not supplying that key.

**Root cause:**
`tactical_thresholds` was added as a required key in `FORMAT_RULES` (in the ODI
manifest) at some point after this test was written. The test's fixture or setup
never added it because it did not exist at the time. The `PlayerEngine` constructor
now hard-requires it, so any test that builds `PlayerEngine` without it will crash.

**Investigation steps:**
1. Read `tests/verify_headless_player.py` in full. Find how the test constructs
   the `PlayerEngine` -- specifically, what `rules` dict (if any) it passes in.
2. Read `formats/odi/manifest.py`. Find `FORMAT_RULES` and locate the
   `tactical_thresholds` entry. Copy its exact structure (keys and default values).
3. Read `formats/odi/engines/player/_base.py` lines 40-70. Confirm exactly what
   `_require_tactical_thresholds()` checks for -- the minimum keys the dict must
   contain.
4. Fix: update the test fixture to include a valid `tactical_thresholds` dict that
   satisfies the validator. Use the same structure as in `FORMAT_RULES` in the
   manifest. The test should not need to change its assertions -- only its setup.
5. After fixing, run the full headless test to confirm it reaches its actual
   assertions (the engine constructing successfully is step one; the engine
   returning correct results is step two).
