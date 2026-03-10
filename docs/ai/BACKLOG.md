# BACKLOG.md
**Purpose:** Project planning board — all scheduled, in-review, and icebox tasks.
**Last Updated:** 2026-03-10
**Maintained by:** Human Architect
**Do NOT attach to AI agents** — use SESSION_STATE.md for agent context.

---

## HOW TO USE

- **IN REVIEW** — completed this sprint, pending final architect sign-off
- **BACKLOG** — scheduled, broken into subtasks, ready to action
- **ICEBOX** — future ideas, not scheduled, no subtasks yet

Task IDs are sequential. Never reuse an ID.
When a task moves to COMPLETE, log it in PROJECT_CONTEXT.md Section 10
and remove from this file.

---

## Tasks Status values:

- Open — not started
- In Progress — actively being worked
- Blocked — waiting on dependency
- Closed — YYYY-MM-DD — done

---

## IN REVIEW



## BACKLOG
## TASK-095 - Refine Venue Matchup Report styling and contrast
**Type:** frontend-modification
**Scope:** frontend
**Priority:** High
**Depends On:** TASK-094
**Created:** 2026-03-10
**Status:** CLOSED - 2026-03-10

### Description
Refine the "Venue Matchup / Fortress Report" screen with a dark theme polish pass to improve readability and aesthetics. Focus on team panel color coding, typography hierarchy, subordinated sample counts, de-emphasized accuracy notice, and improved table distinction.

### Acceptance Criteria
- AC-1: Home team panel has a visible blue left border or accent; Away team panel has a visible red left border or accent.
- AC-2: Typography hierarchy improved: section headers (e.g. BATTING 1ST) are more distinct from stat labels (e.g. Avg Score).
- AC-3: Sample counts in brackets (e.g. [3], [2]) are visually subordinate to the main value (muted color or smaller font).
- AC-4: Wins/Def/Chs badges in team panels are more readable (improved contrast or padding).
- AC-5: Accuracy Notice banner is de-emphasized (subtler border/background) but remains visible.
- AC-6: Match Audit table header row is visually distinct from data rows (e.g. different background/border).
- AC-7: Status column in Match Audit uses pill/badge styling for "Included"/"Excluded" labels.
- AC-8: Overall contrast ratios improved while retaining dark theme depth.
- AC-9: No logic or backend changes.
- AC-10: Post-task bouncer matches baseline.

### Files In Scope
- `frontend/components/renderers/VenueMatchupReport.tsx`
- `frontend/components/renderers/MatchAuditSection.tsx`

## TASK-094 - Fix venue matchup panel and match audit layout regressions
**Type:** frontend-bug-fix
**Scope:** frontend
**Priority:** High
**Depends On:** TASK-093
**Created:** 2026-03-10
**Status:** CLOSED - 2026-03-10

### Description
Three UI/layout bugs exist in the Venue Matchup / Fortress Report screen that
make the display unreadable in specific conditions. First, the Avg Fail Chase
value is truncated in both team panels and the bracketed sample count is cut
off due to container overflow. Second, the Sri Lanka chasing block has a large
visible empty gap above it caused by conditional renders leaving empty elements
when Highest Chased and Avg Succ. Chase are null/dash. Third, the Match Audit
table has no visual separation between the 1st Inn and Bat 2nd columns, making
row data unreadable.

### Acceptance Criteria
- AC-1: Avg Fail Chase displays in full in both team panels and the bracketed
  sample count is not truncated at supported viewport widths.
- AC-2: The home-team chasing block has no visible empty gap above it when
  Highest Chased and Avg Succ. Chase are null or "-".
- AC-3: The Match Audit table has clear visual separation between all columns,
  especially 1st Inn and Bat 2nd.
- AC-4: All other Venue Matchup screen elements render identically to before.
- AC-5: Post-task bouncer output matches or improves on baseline.

### Files In Scope
- `frontend/components/renderers/VenueMatchupPanel.tsx`
- `frontend/components/renderers/MatchAuditSection.tsx`
- `frontend/styles/` (read-only inspection for existing styling patterns)

## TASK-093 - Fix venue matchup match audit status propagation
**Type:** bug-fix
**Scope:** backend
**Priority:** High
**Depends On:** TASK-092
**Created:** 2026-03-10
**Status:** CLOSED - 2026-03-10

### Description
The Match Audit table in the Venue Matchup / Fortress Report function displays
"Included" for matches that were correctly excluded from averages due to a short
2nd innings (< 45 overs, batting team not all-out, target not chased). Root cause
was diagnosed in the preceding task: EnrichmentService.enrich_with_match_audit()
in core/services/enrichment.py rebuilds audit rows from raw match_df using only
MATCH_IDS, discarding the computed status values from the calculator payload.
_build_audit_record() then defaults missing status to STATUS_OK and emits
"Included". The fix must pass the computed per-match status values from the
calculator payload into enrich_with_match_audit() so _build_audit_record()
receives the correct status for each match and emits the correct label.
Additionally, the preceding diagnosis task left doc updates incomplete and this
task must clean those up as part of its doc update step.

### Acceptance Criteria
- AC-1: enrich_with_match_audit() receives and uses the computed per-match
  status values from the calculator payload - it no longer rebuilds status
  from raw match_df alone.
- AC-2: _build_audit_record() receives the correct status value for the
  2018-10-23 match (status=4 / STATUS_SHORT_SECOND_DROP) and emits the
  correct exclusion label - not "Included".
- AC-3: Matches correctly included in averages continue to display "Included".
  No regression on status labels for valid included matches.
- AC-4: Data integrity is preserved - the excluded match remains excluded
  from all average calculations. Counts remain: SUMMARY_MATCHES=4,
  VALID_MATCHES=3, SHORT_SECOND_MATCHES=1.
- AC-5: All modified functions retain complete type annotations.
- AC-6: Post-task bouncer output matches or improves on baseline.
- AC-7: Doc cleanup complete - preceding diagnosis task BACKLOG entry
  is present and closed, SESSION_STATE reflects both the diagnosis task
  and this fix task as completed.

### Files In Scope
- `core/services/enrichment.py` - primary fix target
- READ ONLY - `core/data_access.py`
- READ ONLY - `core/interfaces/team_types.py`
- READ ONLY - `api/serializers.py`
- READ ONLY - `core/calculators/team/venue_calculator.py`
- READ ONLY - `core/services/match_filter_service.py`
- READ ONLY - `frontend/components/renderers/MatchAuditSection.tsx`

## TASK-092 - Diagnose venue matchup match audit status loss
**Type:** bug-fix
**Scope:** backend
**Priority:** High
**Depends On:** NONE
**Created:** 2026-03-10
**Status:** CLOSED - 2026-03-10

### Description
Diagnose why the Match Audit table in the Venue Matchup / Fortress Report path
shows "Included" for a match that the calculator correctly excludes from
averages. Confirm the affected match, verify the calculator-side status code and
summary counts, and isolate the exact handoff point where the status value is
lost before the audit rows are formatted for the frontend.

### Acceptance Criteria
- AC-1: Reproduce the incorrect Match Audit label for the excluded
  2018-10-23 Sri Lanka vs England match at Colombo.
- AC-2: Confirm the calculator path produces status=4
  (STATUS_SHORT_SECOND_DROP) for that match and preserves counts:
  SUMMARY_MATCHES=4, VALID_MATCHES=3, SHORT_SECOND_MATCHES=1.
- AC-3: Isolate the defect to `EnrichmentService.enrich_with_match_audit()`
  rebuilding audit rows from raw `match_df` via `MATCH_IDS`, which causes
  `_build_audit_record()` to default missing status to STATUS_OK.
- AC-4: Leave a fix-ready diagnosis without changing calculator, serializer,
  or frontend logic.

### Files In Scope
- `core/services/enrichment.py` - READ ONLY for diagnosis
- READ ONLY - `core/calculators/team/venue_calculator.py`
- READ ONLY - `core/services/match_filter_service.py`
- READ ONLY - `frontend/components/renderers/MatchAuditSection.tsx`

## TASK-091 - Restore venue matchup score-extreme layer ownership
**Type:** refactor
**Scope:** backend
**Priority:** High
**Depends On:** TASK-090
**Created:** 2026-03-10
**Status:** CLOSED - 2026-03-10

### Description
TASK-090 introduced a layer violation in `core/calculators/team/venue_calculator.py`
by coercing high/low score extremes to strings inside the calculator. This task
restores `high_1st`, `low_1st`, and `high_chased` to raw `int | None` values in
the calculator and moves the required display coercion into `api/serializers.py`
so the frontend keeps the correct user-visible values without a Visual Silence
violation in Domain Core.

### Acceptance Criteria
- AC-1: `_normalize_text_metric()` is removed from the three affected calculator
  fields.
- AC-2: `high_1st`, `low_1st`, and `high_chased` return `int | None` from the
  calculator.
- AC-3: String coercion for those three fields is handled in `api/serializers.py`.
- AC-4: The frontend still receives correctly formatted High/Low and Highest
  Chased values.
- AC-5: All modified functions retain complete type annotations.
- AC-6: Post-task bouncer output matches or improves on baseline.

### Files In Scope
- `core/calculators/team/venue_calculator.py`
- `api/serializers.py`
- READ ONLY - `core/interfaces/team_types.py`
- READ ONLY - `core/data_access.py`

## TASK-090 - Venue Matchup null High/Low and Highest Chased metrics
**Type:** bug-fix
**Scope:** backend
**Priority:** High
**Depends On:** NONE
**Created:** 2026-03-10
**Status:** CLOSED - 2026-03-10

### Description
The Venue Matchup function (Venue Intelligence section) is returning null/None
for two metrics: "High / Low" score in the Batting First block, and "Highest
Chased" in the Chasing block. Both fields render as "-" in the frontend despite
valid match data existing for the queried combination. All other metrics in the
same function return correct values. The reference (ipywidgets) app returns
correct values for the same inputs. Agent must diagnose the root cause
independently, fix it, and confirm no regression on surrounding metrics.

### Acceptance Criteria
- AC-1: "High / Low" in the Batting First block returns correct max and min
  innings scores for a valid team/venue/years query.
- AC-2: "Highest Chased" in the Chasing block returns the correct max
  successfully chased score for the queried team at the queried venue.
- AC-3: All other Venue Matchup metrics that were returning correct values
  before this fix continue to return identical values (no regression).
- AC-4: Fix uses vectorized Pandas/NumPy operations only - no row-level
  iteration introduced.
- AC-5: All modified functions retain complete type annotations.
- AC-6: Post-task bouncer output matches or improves on baseline.

### Files In Scope
- `formats/odi/engines/venue_engine.py` (or equivalent venue matchup engine)
- `core/calculators/<venue_calculator>.py` (whichever calculator computes
  high_score, low_score, highest_chased - follow the call chain)
- READ ONLY - `core/data_access.py`
- READ ONLY - `core/interfaces/team_types.py`
- READ ONLY - `api/serializers.py`
- READ ONLY - `formats/odi/manifest.py`



### [TASK-012] Token optimisation — section-aware context loading
**Status:** Open
**Priority:** Low
**Scope:** AI Tooling
**Blocked by:** Needs 1 week monitoring first (from 2026-03-03)
**Why:** Both agents burning tokens loading full standards files.
Read Discipline added as quick fix — monitor before building section-splitting.
**Subtasks:**
- [ ] Monitor agent sessions for 1 week — note any file re-reads
- [ ] Decide: is section-splitting needed after monitoring?
- [ ] If yes — design section file structure for BACKEND standards
- [ ] If yes — design section file structure for FRONTEND standards
- [ ] Update context-loader.md with section-aware attach logic
- [ ] Test with Codex and Gemini — verify token reduction


---



## Execution Order



## ICEBOX
Future ideas — not scheduled. No subtasks. No commitment.

- Phase 12 planning — live layer. NOT started.
  Do not action until architect gives explicit go-ahead.
- Format expansion — extend strategy loaders beyond ODI to T20I and other formats.
- match_pack/ expansion — add more report types as engine functions grow.
- Pre-commit hook audit — verify .githooks/pre-commit cannot be bypassed.

### [ICE-001] MCP Integration
**Status:** Icebox
**Why parked:** No actionable work until Phase 12 live layer is scoped.
Engine refactoring must complete first.
**Potential value:**
- Expose DuckDB data layer to agents via MCP server
- Wrap compliance bouncer as an invokable MCP tool
- Live match feed exposure in Phase 12 without custom connectors
**Revisit trigger:** Phase 12 scoping begins

### [ICE-002] Extract engine dispatcher from api/main.py
**Status:** Icebox
**Why parked:** Dispatch logic will change during TASK-010 engine refactoring.
Extracting before refactor means doing it twice.
**Revisit trigger:** TASK-010 complete

### [ICE-003] Extract error handler from api/main.py
**Status:** Icebox
**Why parked:** Low priority, not blocking anything.
**Revisit trigger:** TASK-018 and TASK-010 complete

### [ICE-004] Enhance context-loader to output correct guide skill path based on task type
**Status:** Icebox
**Why parked:** Guide skills just built — context-loader enhancement is a quality-of-life
improvement, not a blocker. TASK-010 takes priority.
**What it does:**
- Reads task type from SESSION_STATE.md Active Task section
- Outputs the correct guide skill path alongside the standards file attach list
**Revisit trigger:** After TASK-010 engine refactoring completes

### [ICE-005] Numba AOT Warm-Up Standard
**Status:** Icebox
**Why parked:** Phase 12 (live layer) has not started. No Monte Carlo simulation
code exists in the codebase. No Numba dependency. When this standard was
previously included as Mandate 7 in ENGINEERING_STANDARDS_BACKEND.md v2.2,
it was actively harmful — agents interpreted its presence as permission to
start building Phase 12 infrastructure. It was deliberately removed on 2026-03-03.
**Revisit trigger:** Phase 12 scoping begins AND Monte Carlo simulation is designed.

### [TASK-077] Create frontend test suite (Vitest + React Testing Library)
**Status:** Open â€” 2026-03-09
**Priority:** Tier 1 â€” Hard Fail (full sprint)
**Type:** frontend-new-component
**Audit ref:** Rule 2.2F-R2 (zero test files exist)
**Files (new):**
- `frontend/lib/executeHelpers.test.ts`
- `frontend/components/renderers/FunctionRenderer.test.tsx`
- `frontend/lib/api.test.ts`
- `frontend/lib/context.test.tsx`
**Description:**
No `.test.tsx` or `.test.ts` files exist anywhere under `frontend/`. Systemic Hard Fail
for Rule 2.2F-R2. Required coverage completely absent:
1. `resolveSquadBuilderConfig()`, `isExtraInputFieldConfig()`, `extractEnrichedData()` â€” all branches
2. `FunctionRenderer.tsx` â€” one test per output_type (11 registered: report, comparison_table,
   matrix_table, form_table, table, phase_analysis, venue_matchup_report, prediction_card,
   profile_card, matchup_table, download_json)
3. `lib/api.ts` â€” error code paths: 422, 5xx, network failure
4. `lib/context.tsx` â€” format switch clears contextValues, manifest load sets years default
**Implementation order:**
1. `executeHelpers.test.ts` â€” type guards + helper branches
2. `FunctionRenderer.test.tsx` â€” 11 routing tests
3. `api.test.ts` â€” error code paths
4. `context.test.tsx` â€” format switch + years default
**Acceptance Criteria:**
- All 4 test files exist under `frontend/`
- Vitest + RTL only â€” no Jest/Mocha/Enzyme (Rule 2.2F-R1)
- Tests assert behaviour, not CSS class presence or implementation detail
- No hardcoded format keys "odi"/"t20i" in any test file (Rule 2.2F-R4)
- All 11 output_type routing paths covered
- All error code paths (422, 5xx, network) covered
- Gate F1 PASS, Bouncer PASS
**Guide:** `core/gen_ai/skills/guides/frontend/frontend-new-component-guide/SKILL.md`
**Gates:** F1, F2, F3, Gate 5, Gate 6
**Note:** TASK-084 (check_required_test_files gate) depends on this task being CLOSED first.

### [TASK-084] Gate F1: Add check_required_test_files()
**Status:** Open â€” 2026-03-09
**Priority:** Tier 3 â€” Gate improvement
**Type:** validator-fix
**Audit ref:** Gate coverage gap â€” Rule 2.2F-R2
**Files:**
- `core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/scripts/run_frontend_lint.py`
**Description:**
No gate verifies that required test files exist. The missing test suite (TASK-077) was
invisible to all gates. Add `check_required_test_files()` that verifies the following
test files exist under `frontend/`:
- `frontend/lib/executeHelpers.test.ts`
- `frontend/components/renderers/FunctionRenderer.test.tsx`
- `frontend/lib/api.test.ts`
- `frontend/lib/context.test.tsx`
**DEPENDS ON:** TASK-077 must be CLOSED before this task is executed.
Running this gate before the test files exist will immediately Hard Fail.
**Acceptance Criteria:**
- `check_required_test_files()` added to run_frontend_lint.py
- Absence of any required test file â†’ Hard Fail
- Gate F1 PASS â€” 0 violations (only run after TASK-077 CLOSED)
- Bouncer PASS
**Guide:** N/A â€” validator-fix, no guide skill required
**Gates:** Gate F1 (self-test), Gate 5, Gate 6

---

## TASK-086 — Add --format-selector-height token to globals.css and fix FormatSelector reference
**Status:** Open — 2026-03-09
**Priority:** Tier 1 — Hard Fail (gate violation)
**Type:** frontend-modification
**Audit ref:** Rule 2.2B-R1 — undefined CSS token --format-selector-height
**Files:**
- `frontend/app/globals.css`
- `frontend/components/layout/FormatSelector.tsx`

**Description:**
`var(--format-selector-height)` referenced in FormatSelector.tsx:12 but not defined
in globals.css. Add the token to globals.css alongside existing layout dimension tokens
(`--sidebar-width`, `--topbar-height`, `--context-bar-height`), then confirm the
reference in FormatSelector.tsx resolves correctly.

**Acceptance Criteria:**
- `--format-selector-height` defined in globals.css layout dimensions section
- FormatSelector.tsx:12 reference resolves to defined token
- Gate F1 PASS, Bouncer PASS

**Guide:** `core/gen_ai/skills/guides/frontend/frontend-modification-guide/SKILL.md`
**Gates:** F1, F2, F3, Gate 5, Gate 6

Add **GitHub** (@modelcontextprotocol/server-github) MCP server

## TASK-088 — Refinery memory optimisation
Chunked pandas or DuckDB-native aggregations in refinery_script.py
Priority: Medium — pre-Phase 12 requirement

## TASK-089 — ETL atomic swap connection guard
Add open-connection check before os.replace in ingest_to_db.py
Priority: High — will cause crashes when API runs continuously in Phase 12


---

*End of BACKLOG.md — Last Updated 2026-03-10*
*For current session state, see docs/ai/SESSION_STATE.md*
*For permanent project knowledge, see docs/ai/PROJECT_CONTEXT.md*

