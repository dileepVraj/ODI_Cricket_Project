# SRP Violation Audit & Refactor Plan — Backend Python Files
**Audit date:** 2026-03-30 | **Plan updated:** 2026-03-31
**Scope:** `core/`, `api/`, `formats/odi/`
**Total lines scanned:** ~18,244
**Audited by:** Claude (static analysis via Explore agent)

---

## Strategic Context

SRP violations are the **diagnostic lens**, not the goal. This document is the map for a full
backend structural refactor. Fixing the violations identified here also addresses:

- **Dead code** — methods that only exist because everything is bundled together
- **Import chain cleanup** — every file that imports from a god object breaks when it is split
- **Type system fragmentation** — `team_types.py` has 30+ TypedDicts because the domain was never separated
- **Test isolation** — you cannot unit-test `SchemaValidator` without a live DuckDB connection because it is fused into `DataAccess`
- **API layer bloat** — `api/main.py` does routing + validation + context assembly + engine resolution because there was no clean place to put those things
- **Frontend wiring clarity** — once `interpreter.py` is split, data shapes flowing to the frontend become predictable and bounded

The SRP gate (`GATE_SRP`) is wired and advisory. Baseline violations = 0 as of TASK-168.
This is the clean window for a structural refactor.

---

## GATE_SRP Allowlist — Known Registered Violations

> **These files are grandfathered.** `srp_sentinel.py` emits advisory warnings for them but does NOT
> block. Any file **not** in this list that exceeds SRP thresholds is a **hard block**.
>
> Remove a file from this list only when its refactor task is complete and verified green.

| File | Tier | Refactor task | Status |
|---|---|---|---|
| `formats/odi/engines/player_engine.py` | 1 | TASK-TBD | Pending |
| `core/calculators/team/venue_calculator.py` | 1 | TASK-TBD | Pending |
| `core/data_access.py` | 2 | TASK-TBD | Pending |
| `formats/odi/match_pack.py` | 2 | TASK-TBD | Pending |
| `api/main.py` | 3 | TASK-TBD | Pending |
| `core/services/squad_service.py` | 3 | TASK-175 | In Progress |
| `core/calculators/team/matchup_calculator.py` | 3 | TASK-TBD | Pending |
| `core/utils/compliance_bouncer.py` | 3 | TASK-TBD | Pending |
| `formats/odi/manifest.py` | 4 | TASK-TBD | Pending |
| `core/services/report_formatter.py` | 4 | TASK-TBD | Pending |
| `formats/odi/engines/team_engine.py` | 2 | TASK-TBD | Pending |
| `core/services/report_builder.py` | 3 | TASK-TBD | Pending |

---

## Refactor Work Order

Sequenced by **safest refactor first**, not blast radius. Foundation layers refactored last,
after everything above them is stable and tested.

### Three-Phase Completion Model

Every refactor task has three phases. A task is not architecturally complete until all three
are done. Phases 2+3 are often deferred until the caller is itself being restructured
(doing them earlier would mean touching the caller twice).

**Phase 1 — File decomposition (additive + trim)**
Create domain modules, copy code verbatim, replace god file with backward-compat shim/re-exports.
Import sites untouched. Gates pass. File removed from allowlist.

**Phase 2 — Import site migration**
Update every caller to import from the domain module directly instead of the shim.
One-line change per site. No logic changes.

**Phase 3 — Shim removal**
Delete the shim/re-export block once all import sites are migrated.
Circular dependencies (if any) resolved here.

**Exception — Task 1 (team_types):** Type imports are stable across structural refactors
(a type import survives when its caller file is later split). Phase 2+3 should be done as
a standalone task before Task 5 (player_engine.py) begins — see Task 1 below.

**Default rule for Tasks 2–15:** Phase 2+3 of each task is triggered by the Phase 1 of
its primary caller file (e.g. transformer/interpreter Phase 2+3 happen during Task 9,
squad_service Phase 2+3 happen during Task 5).

---

Each Phase 1 task must include:
1. Dead code scan — identify orphaned methods/functions before splitting
2. Import site audit — find every file importing from the target before touching it
3. Compliance bouncer pass (GATE 6)
4. GATE_SRP re-run — verify advisory count drops
5. Remove the file from the allowlist above once verified green

---

### Task 0 — Gate Hardening (do first, before any refactor)

**What:** Upgrade `srp_sentinel.py` to hard-block on net-new files exceeding thresholds.
Advisory-only for files registered in the allowlist above.

**Why:** Without this, a new god object can be introduced tomorrow and the gate only warns.
The allowlist ensures existing known violations are tracked, not silently ignored.

**Files:** `core/utils/srp_sentinel.py`, `core/utils/paradigm_sentinel.py`, `GATE_SEQUENCE.md`

---

### Task 1 — `core/interfaces/team_types.py`
**Lines:** 695 | **Risk:** Zero (pure type reorganization, no runtime logic)

30+ TypedDicts spanning team analysis, venue, player, and serialization domains.

**Split into:**
| New file | Domain |
|---|---|
| `core/interfaces/team_types.py` | Team analysis TypedDicts only |
| `core/interfaces/venue_types.py` | Venue analysis TypedDicts |
| `core/interfaces/player_types.py` | Player analysis TypedDicts |
| `core/interfaces/serialization_types.py` | Serialization / output TypedDicts |

**Phase 1 — COMPLETE** — TASK-169a (`49c4243`) created domain files, TASK-169b trims
team_types and wires re-exports. team_types.py removed from allowlist.

**Phase 2 — Pending (TASK-TBD) — Migrate 16 import sites**

Each of the 16 import sites currently does:
```python
from core.interfaces.team_types import SomeType
```
Each must be updated to import from the domain file that owns that type:
```python
from core.interfaces.venue_types   import VenueData, VenuePhaseData, ...
from core.interfaces.player_types  import PlayerFormRow, PlayerProfile, ...
from core.interfaces.team_types    import TeamRecord, ...          # team-only types
from core.interfaces.serialization_types import SerializedPayload, ...
```
Before starting: run `grep -r "from core.interfaces.team_types import" . --include="*.py"`
to enumerate every import site and map each name to its domain file.

Known import sites (verify against HEAD before task):
`formats/odi/engines/player_engine.py`, `formats/odi/engines/team_engine.py`,
`formats/odi/match_pack.py`, `core/services/squad_service.py`,
`core/services/report_builder.py`, `core/services/report_formatter.py`,
`core/calculators/team/venue_calculator.py`, `core/calculators/team/matchup_calculator.py`,
plus ~8 additional files identified in TASK-169 import audit.

**When to run:** Before Task 5 (player_engine.py Phase 1). Type imports are stable
across structural refactors so this can be a standalone task at any point before Task 5.

**Phase 3 — Pending (TASK-TBD) — Remove re-exports, resolve SN-001**

Once all 16 import sites are migrated:
1. Remove the 69-name re-export block from the bottom of `core/interfaces/team_types.py`
2. Remove wildcard `# noqa: F403` imports from `core/interfaces/__init__.py`
3. Verify `venue_types.py` and `player_types.py` no longer need to import from `team_types.py`
   (if they do, move the shared type to a new `core/interfaces/shared_types.py`)
4. Confirm SN-001 (circular import) is resolved — remove from state.json standing_notices

**Phase 3 may be combined with Phase 2 into a single task** if the circular dep analysis
is straightforward. Run in the same task only if the import graph is clean after Phase 2.

---

### Task 2 — `core/match_pack/transformer.py`
**Lines:** 536 | **Risk:** Low (no external DB, pure transforms)

**Responsibilities mixed:** H2H slim/full transforms, venue bias transforms, team form
transforms, dominance matrix transforms, squad comparison transforms, player stats
transforms, HTML/emoji stripping, string parsing utilities.

**Split into:**
| New module | Responsibility |
|---|---|
| `core/match_pack/transformers/h2h_transformer.py` | H2H slim/full transforms |
| `core/match_pack/transformers/venue_transformer.py` | Venue bias transforms |
| `core/match_pack/transformers/team_transformer.py` | Team form + dominance matrix |
| `core/match_pack/transformers/player_transformer.py` | Player stats transforms |
| `core/match_pack/transformers/string_utils.py` | HTML/emoji stripping, string parsing |

**Status: COMPLETE** â€” TASK-172b (`66264c3`) replaced `transformer.py`
with a backward-compat re-export shim and removed it from the allowlist.

---

### Task 3 — `core/match_pack/interpreter.py`
**Lines:** 883 | **Risk:** Low-medium (no external DB, narrative only)

**Responsibilities mixed:**
- H2H interpretation with dominance tagging
- Venue bias narrative generation
- Team form interpretation
- Dominance matrix interpretation
- Squad comparison context tagging
- Player stats interpretation
- Executive summary generation
- Narrative composition and context tagging
- Condition weight assignment
- Format-specific ranking integration
- Player role and bowling style interpretation
- Data enrichment with context metadata

**Split into:**
| New class | Responsibility |
|---|---|
| `H2HInterpreter` | H2H interpretation, dominance tagging |
| `VenueInterpreter` | Venue bias narratives |
| `TeamInterpreter` | Team form, dominance matrix |
| `PlayerInterpreter` | Player stats, role/style interpretation |
| `MatchSummaryComposer` | Executive summary generation, context tagging |

**Frontend wiring note:** Changes to `PlayerInterpreter` and `MatchSummaryComposer` data shapes
will affect API response structure. Verify frontend component expectations before and after.

**Status: COMPLETE** — TASK-174a (`1d63a82`) created domain files,
TASK-174b trims interpreter and wires shim. interpreter.py removed from allowlist.

---

### Task 4 — `core/services/squad_service.py`
**Lines:** 607 | **Risk:** Medium (service layer, well-bounded, but many call sites)

**Responsibilities mixed:**
- Config/rule access helpers (`_get_tactical_threshold`, `_default_player_role`)
- Data normalization utilities (`_normalize_players`, `_normalize_base_df`)
- Shared rounding utilities (`_round_one_decimal`, `_round_two_decimals`)
- Empty data scaffolding (`_empty_player_records`)
- Squad-level metrics aggregation (`_calculate_squad_metrics`)
- Player-level bulk stats building (`_build_bulk_player_stats`)
- Bulk metrics entry point (`get_bulk_metrics`)

**Split into:**
| New class | Responsibility |
|---|---|
| `SquadServiceBase` | Config/rule access, normalization, rounding, empty scaffolding |
| `SquadMetricsCalculator` | Squad-level metrics aggregation |
| `PlayerStatsBuilder` | Player-level bulk stats building |
| `SquadService (hub)` | Composite via MRO, owns `get_bulk_metrics` |

---

### Task 5 — `formats/odi/engines/player_engine.py`
**Lines:** 1,612 | **Risk:** Medium-high (import audit mandatory before starting)

**Responsibilities mixed:**
- Player squad fetching and caching
- Batting and bowling statistics calculation
- Squad comparison analysis
- Tactical matrix generation
- Player matchup analysis (batter vs bowler)
- Player profile generation
- Form sequence analysis
- Playing XI extraction from recent matches
- Player role classification
- Bowling style mapping
- Venue-specific player stats
- International ranking lookups

**Split into:**
| New class | Responsibility |
|---|---|
| `PlayerFetcher` | Squad fetch, cache, playing XI extraction |
| `PlayerCalculator` | Batting / bowling stats, form sequences |
| `PlayerComparator` | Squad comparison, matchup analysis (batter vs bowler) |
| `PlayerProfiler` | Profile generation, role classification, bowling style mapping |
| `PlayerVenueAnalyzer` | Venue-specific stats, ranking lookups |

---

### Task 6 — `core/calculators/team/venue_calculator.py`
**Lines:** 961 | **Risk:** Medium (42 free functions, no encapsulation — easy to parallelise tests against splits)

**Responsibilities mixed:**
- Venue bias analysis (batting vs chasing win rates)
- Home fortress calculations (team dominance at home)
- Venue matchup analysis (team performance at specific ground)
- Venue phase breakdowns (powerplay, middle, death per venue)
- Score distribution analysis at venues
- Toss intelligence (venue-specific toss impact)
- Score extremes and banding calculations
- Team performance metrics aggregation
- Phase-based scenario comparisons
- Report building and formatting
- Team color mapping

**Split into:**
| New module / class | Responsibility |
|---|---|
| `VenueBiasCalculator` | Batting vs chasing win rates, score distributions |
| `HomeFortressCalculator` | Team dominance at home, home win rates |
| `VenueMatchupCalculator` | Team performance at specific ground |
| `VenuePhaseAnalyzer` | Powerplay / middle / death breakdowns per venue |
| `VenueTossAnalyzer` | Toss impact, toss-win correlation |
| `VenueReportBuilder` | Report assembly, team color mapping |

---

### Task 7 — `core/calculators/team/matchup_calculator.py`
**Lines:** 624 | **Risk:** Medium (25+ free functions, no encapsulation)

**Responsibilities mixed:** Batting vs bowling matchup scoring, wicket pressure, matchup
ranking, player-specific matchup building, phase-specific analysis, averaging, matrix
assembly, sample filtering.

**Split into:**
| New class | Responsibility |
|---|---|
| `MatchupScorer` | Batting vs bowling scoring, wicket pressure |
| `MatchupRanker` | Ranking, averaging, sample filtering |
| `MatchupMatrixBuilder` | Phase-specific analysis, matrix assembly |

---

### Task 8 — `core/data_access.py`
**Lines:** 750 | **Risk:** High (foundation layer — bugs here corrupt everything above)

Do this **after** Tasks 1–7 are stable. The concepts proven in those splits
(`SchemaValidator`, `QueryBuilder`) will have analogues here.

**Responsibilities mixed:**
- DuckDB connection management
- Schema validation
- Match integrity checks
- Venue alias resolution and filtering
- Innings field normalization
- Missing team hydration from balls data
- Match queries (complex venue/team/time filters)
- Ball-by-ball queries
- Player career summaries
- Venue-phase stats aggregation
- H2H summary stats
- Player vs bowling style analysis
- Team form extraction
- Batch player stats retrieval
- Database statistics

**Split into:**
| New class | Responsibility |
|---|---|
| `SchemaValidator` | Schema validation, match integrity checks |
| `QueryBuilder` | Query construction for matches, balls, players |
| `DataNormalizer` | Venue alias resolution, innings normalization, team hydration |
| `DataAccess` (slimmed) | Connection management only, delegates to above |

---

### Task 9 — `formats/odi/match_pack.py`
**Lines:** 856 | **Risk:** High (entry point for every match pack generation)

Refactor after all engine and service dependencies are clean.

**Responsibilities mixed:**
- Match pack orchestration (chapters 1–4 generation)
- Engine call coordination across 15+ different analyses
- Data transformation (calling transformer)
- Data interpretation (calling interpreter)
- Silent execution and stdout suppression
- Report assembly and structure management
- File I/O for report persistence
- Executive summary generation
- Match pack JSON generation
- Internal key stripping
- Data structure flattening

**Split into:**
| New class | Responsibility |
|---|---|
| `MatchPackOrchestrator` | Chapter sequencing, engine call coordination only |
| `MatchPackAssembler` | Report assembly, key stripping, flattening |
| `MatchPackPersister` | File I/O, JSON generation |

---

### Task 10 — `api/main.py`
**Lines:** 588 | **Risk:** High (every API request passes through here)

**Prerequisite:** Smoke test baseline covering at least 3–4 endpoints and verifying
response shapes. Do not refactor without this baseline.

**Responsibilities mixed:**
- API endpoint definitions (10+ routes)
- Format discovery and validation
- Context data assembly (teams, venues, players, regions, countries)
- Manifest retrieval and caching
- Generic function execution and orchestration
- Parameter validation and injection
- Engine resolution and instantiation
- Error handling and HTTP responses
- Backward compatibility routing
- Request preprocessing

**Split into:**
| New module | Responsibility |
|---|---|
| `ContextBuilder` | Teams, venues, players, regions, countries assembly |
| `EngineResolver` | Engine resolution and instantiation |
| `RequestValidator` | Parameter validation and injection |
| `LegacyRouter` | Backward compatibility routing |
| `main.py` (slimmed) | Route registration only |

---

### Task 11 — `formats/odi/manifest.py`
**Lines:** 865 | **Risk:** Low (30+ function definitions, no runtime logic)

All ODI function definitions in a single file. Adding one function means editing the
entire manifest. Should be split by category before new features are added.

**Split into:**
| New module | Domain |
|---|---|
| `formats/odi/manifests/h2h_manifest.py` | H2H functions |
| `formats/odi/manifests/venue_manifest.py` | Venue functions |
| `formats/odi/manifests/team_manifest.py` | Team functions |
| `formats/odi/manifests/player_manifest.py` | Player functions |

---

### Task 12 — `formats/odi/engines/team_engine.py`
**Lines:** 463 | **Methods:** 29 | **LCOM4:** 11 | **Risk:** Medium
**Gate score:** 5 (SRP_FLAG) — missed in original audit, caught by GATE_SRP on first run

**Responsibilities mixed:**
- Home fortress, venue matchup, venue phases, venue bias analysis
- Global H2H, country H2H, home dominance, away/global/continent performance
- Team form analysis
- Private helper factories (`_require_*`, `_resolved_*`, `_context_*` — 15+ methods)

**Split into:**
| New class | Responsibility |
|---|---|
| `TeamVenueAnalyzer` | Home fortress, venue matchup, venue phases, venue bias |
| `TeamH2HAnalyzer` | Global H2H, country H2H, home/away/global/continent performance |
| `TeamFormAnalyzer` | Team form analysis |

---

### Task 13 — `core/services/report_builder.py`
**Lines:** 430 | **Methods:** 6 | **LCOM4:** 6 | **Risk:** Low-medium
**Gate score:** 3 (SRP_WARNING) — missed in original audit, caught by GATE_SRP on first run

6 methods, 6 disjoint LCOM4 groups — every method operates on completely independent state.
Report data building, form data assembly, matrix generation, player stats indexing, and team
form record building have no shared attributes.

**Split into:** `ReportDataBuilder`, `FormDataAssembler`, `MatrixReportGenerator`.

---

### Task 14 — `core/services/report_formatter.py`
**Lines:** 399 | **Risk:** Low (20+ static methods, clear seams)

**Split into:** `StatusFormatter`, `ToneAssigner`, `DisplayFormatter`.

---

### Task 15 — `core/utils/compliance_bouncer.py`
**Lines:** 752 | **Risk:** Low (gate utility, lower priority)

Five distinct validation tools in one module. A failure in one validation domain can
mask failures in another.

**Note:** Refactor last — this is a gate utility. Any change to it requires re-running
the full gate sequence to confirm nothing regressed.

---

## Additional Findings (Beyond SRP)

### Dead Code Risk
Every god object refactor will orphan helpers that were only called internally. Before
splitting any file, run a dead code scan on that file's methods/functions and remove
anything with zero callers outside the file.

### Import Chain Blast
These files are all import targets. Splitting them breaks imports across `formats/`, `api/`,
and `core/`. Each task must begin with: `grep -r "from <module> import" . --include="*.py"`
to enumerate every import site before touching the file.

### Frontend Wiring Risk
`interpreter.py` splits (`PlayerInterpreter`, `MatchSummaryComposer`) and `match_pack.py`
splits (`MatchPackOrchestrator`) change internal data shapes that eventually land in API
responses. For each of these, verify frontend component expectations before and after.

### `formats/odi/manifest.py` — Multiplier Risk
Tier 4 in the original audit, but this is actually the highest future multiplier. Every
new ODI function adds to it. Split by category (Task 11) before adding new features.

---

## Clean Examples (What Good Looks Like)

| File | Lines | Why it's clean |
|---|---|---|
| `core/calculators/player_math.py` | 120 | Two vectorized functions, one concern |
| `core/calculators/performance.py` | 89 | One function, one concern |
| `core/services/serialization_service.py` | 87 | One class, pure transformation |
| `core/data_loader.py` | 89 | Factory pattern, single responsibility |

---

## Gate Coverage

**Current state:** `GATE_SRP` is advisory for all files. Always exits 0. Never blocks.

**After Task 0:** `GATE_SRP` hard-blocks on net-new files exceeding thresholds.
Advisory-only for files registered in the allowlist above. This prevents the problem
from growing while the refactor happens.

**Progress tracking:** As each refactor task completes, remove the file from the allowlist
table above and update its status. GATE_SRP advisory count should decrease with each task.

---

*Verify line counts and method counts against current HEAD before scheduling each task.*
*Allowlist is authoritative — do not add files to it without a matching audit entry above.*
