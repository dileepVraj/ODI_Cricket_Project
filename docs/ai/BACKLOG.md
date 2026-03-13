# BACKLOG.md
**Purpose:** Project planning board — all scheduled, in-review, and icebox tasks.
**Last Updated:** 2026-03-13
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
## TASK-120 - Add home_team_color and home_team_name to OVERALL row
**Type:** modification
**Scope:** backend
**Priority:** High
**Depends On:** TASK-117
**Created:** 2026-03-13
**Status:** CLOSED - 2026-03-13

### Description
Add home-team metadata to the aggregate matrix row only.

`core/interfaces/team_types.py` now adds additive optional
`home_team_color` and `home_team_name` support for `MatrixReportRow`,
and `core/services/report_builder.py` now emits those fields on the
aggregate OVERALL row using the existing `TEAM_COLORS` lookup chain
while leaving opponent rows unchanged.

### Acceptance Criteria
AC-1: `MatrixReportRow` includes `home_team_color: Optional[str]`.
AC-2: `MatrixReportRow` includes `home_team_name: Optional[str]`.
AC-3: OVERALL row uses
      `TEAM_COLORS.get(team_name) or TEAM_COLORS.get("Visitors", "gray")`.
AC-4: OVERALL row uses `home_team_name: team_name`.
AC-5: Opponent rows remain unchanged.
AC-6: Change is additive only - no existing fields removed or renamed.
AC-7: No `.iterrows()` / `.itertuples()` introduced.
AC-8: No `duckdb` import introduced.
AC-9: Stop-state-trace-confirm completed for `core/interfaces/team_types.py`.
AC-10: Gates 1/2/5/6 pass and bouncer matches baseline.

### Files In Scope
- `core/interfaces/team_types.py`
- `core/services/report_builder.py`
- READ ONLY - `config/shared/team_colors.py`
- READ ONLY - `core/calculators/team/venue_calculator.py`
- READ ONLY - `api/serializers.py`
- READ ONLY - `core/data_access.py`

## TASK-118 - MatrixTable + MatchAuditSection frontend fixes
**Type:** frontend-modification
**Scope:** frontend
**Priority:** High
**Depends On:** TASK-117
**Created:** 2026-03-13
**Status:** CLOSED - 2026-03-13

### Description
Fix the Home Dominance matrix renderer and Match Audit header colours.

`frontend/components/renderers/MatrixTable.tsx` now reads `form_data`
payload objects via `raw_results`, displays the column as `Last 5`,
renders all overall-record stat chips, highlights the overall label,
and injects opponent jersey colours from row-level `team_color`.
`frontend/components/renderers/MatchAuditSection.tsx` now applies
token-based per-column header colours for date/venue/team/status.

### Acceptance Criteria
AC-1: `form_data` no longer renders `[object Object]`.
AC-2: FormGuide maps `W/L/T/NR` to emoji display tokens.
AC-3: Matrix header displays `Last 5` for the form column.
AC-4: Overall record renders all stat chips with no slice limit.
AC-5: Overall Record label uses `--accent-primary`.
AC-6: Matrix opponent cells resolve `team_color` through runtime CSS vars.
AC-7: Match Audit team headers use `--accent-primary`; date/venue stay muted.
AC-8: No backend files modified.
AC-9: Gates F1/F2/F3/5/6 pass and bouncer matches baseline.

### Files In Scope
- `frontend/components/renderers/MatrixTable.tsx`
- `frontend/components/renderers/MatchAuditSection.tsx`
- READ ONLY - `frontend/lib/comparison-types.ts`
- READ ONLY - `frontend/components/renderers/VenueMatchupReport.tsx`
- READ ONLY - `frontend/components/renderers/CountryH2HReport.tsx`
- READ ONLY - `frontend/app/globals.css`
- READ ONLY - `docs/ai/SESSION_STATE.md`
- READ ONLY - `docs/guides/ENGINEERING_STANDARDS_FRONTEND.md`

## TASK-117 - Add team_color to MatrixReportRow in report_builder.py
**Type:** modification
**Scope:** backend
**Priority:** High
**Depends On:** TASK-116
**Created:** 2026-03-13
**Status:** CLOSED - 2026-03-13

### Description
Add opponent team jersey colours to matrix-table payload rows.

`core/interfaces/team_types.py` now adds an optional `team_color`
field to `MatrixReportRow`, and
`core/services/report_builder.py` now populates that field for each
opponent row via the standard `TEAM_COLORS` lookup chain while setting
the aggregate OVERALL row to `None`.

### Acceptance Criteria
AC-1: `MatrixReportRow` includes `team_color: Optional[str]`.
AC-2: `report_builder.py` imports `TEAM_COLORS`.
AC-3: Opponent rows use
      `TEAM_COLORS.get(opponent_name) or TEAM_COLORS.get("Visitors", "gray")`.
AC-4: OVERALL row uses `team_color: None`.
AC-5: Change is additive only - no existing fields removed or renamed.
AC-6: No `.iterrows()` / `.itertuples()` introduced.
AC-7: No `duckdb` import introduced.
AC-8: Stop-state-trace-confirm completed for `core/interfaces/team_types.py`.
AC-9: Gates 1/2/5/6 pass and bouncer matches baseline.

### Files In Scope
- `core/interfaces/team_types.py`
- `core/services/report_builder.py`
- READ ONLY - `config/shared/team_colors.py`
- READ ONLY - `core/calculators/team/matchup_calculator.py`
- READ ONLY - `core/calculators/team/venue_calculator.py`
- READ ONLY - `api/serializers.py`
- READ ONLY - `core/data_access.py`

## TASK-116 - Remove hardcoded top_teams filter in report_builder.py
**Type:** bug-fix
**Scope:** backend
**Priority:** High
**Depends On:** NONE
**Created:** 2026-03-12
**Status:** CLOSED - 2026-03-12

### Description
The Home Dominance matrix, Away Performance matrix, and every other
caller of `ReportBuilder._generate_matrix_report()` previously
hardcoded a top-10 opponent list. Any opponent outside that list was
silently excluded from the matrix output even when valid filtered match
rows existed.

`core/services/report_builder.py` now derives opponents dynamically
from the filtered match data, keeps the row order alphabetic, and
computes the OVERALL row from that same dynamic opponent set.

### Acceptance Criteria
AC-1: The hardcoded `top_teams` list is removed from
      `_generate_matrix_report()`.
AC-2: Opponents are derived from `clean["opponent"].unique()`
      excluding `team_name`.
AC-3: Opponent rows are ordered consistently and documented inline.
AC-4: The OVERALL row remains first and aggregates the full dynamic
      opponent set.
AC-5: MatrixReportRow shape remains unchanged.
AC-6: No `.iterrows()` or `.itertuples()` introduced.
AC-7: No `duckdb` import introduced.
AC-8: Gates 1/2/5/6 pass and the bouncer matches baseline.
AC-9: All `_generate_matrix_report()` callers inherit the fix.

### Files In Scope
- `core/services/report_builder.py`
- READ ONLY - `core/calculators/team/matchup_calculator.py`
- READ ONLY - `core/interfaces/team_types.py`
- READ ONLY - `api/serializers.py`
- READ ONLY - `core/data_access.py`

## TASK-114 - Add analyze_global_h2h_structured backend method + manifest registration
**Type:** new-feature
**Scope:** backend
**Priority:** High
**Depends On:** TASK-107
**Created:** 2026-03-12
**Status:** CLOSED - 2026-03-12

### Description
Add a structured global H2H backend path alongside the legacy
comparison-table flow.

`core/calculators/team/matchup_calculator.py` now exposes
`_build_global_h2h_structured()` and
`calculate_global_h2h_structured_payload()`,
`formats/odi/engines/team_engine.py` now exposes
`analyze_global_h2h_structured()`, and
`formats/odi/manifest.py` now registers
`global_h2h_structured` with `output_type="global_h2h_report"`.
The existing `analyze_global_h2h()` method and
`comparison_table` manifest entry remain intact.

### Acceptance Criteria
AC-1: `_build_global_h2h_structured()` exists and returns a
      `VenueMatchupReport`-shaped payload.
AC-2: Both team stat blocks populate `team_color` via the
      `TEAM_COLORS` fallback chain.
AC-3: `analyze_global_h2h_structured()` exists in `team_engine.py`
      and returns `VenueMatchupReport`.
AC-4: Manifest entry `global_h2h_structured` is registered with
      `engine_method="analyze_global_h2h_structured"` and
      `output_type="global_h2h_report"`.
AC-5: No `duckdb` import added to the modified backend files.
AC-6: No `.iterrows()` or `.itertuples()` introduced.
AC-7: Gates 1/2/3/4/5/6 all pass.
AC-8: Summary payload includes matches, win_pct, tie_nr,
      last_5_home, last_5_away.
AC-9: `venue_avg` payload includes avg_1st, avg_2nd, avg_win_score.
AC-10: Existing `analyze_global_h2h()` behaviour remains unchanged.

### Files In Scope
- `core/calculators/team/matchup_calculator.py`
- `formats/odi/engines/team_engine.py`
- `formats/odi/manifest.py`
- READ ONLY - `core/calculators/team/venue_calculator.py`
- READ ONLY - `config/shared/team_colors.py`
- READ ONLY - `core/interfaces/team_types.py`
- READ ONLY - `api/serializers.py`
- READ ONLY - `core/data_access.py`

## TASK-113 - country_h2h structured team colors fix
**Type:** bug-fix
**Scope:** backend
**Priority:** High
**Depends On:** TASK-107
**Created:** 2026-03-12
**Status:** CLOSED - 2026-03-12

### Description
Fix missing team jersey colors in `CountryH2HReport`.

`_build_country_h2h_structured()` in
`core/calculators/team/matchup_calculator.py` hardcoded
`team_color: None` and `team_tone: None` for both team cards.
The structured payload now mirrors the `venue_calculator.py`
TEAM_COLORS lookup so the frontend can inject jersey colors
for both countries again.

### Acceptance Criteria
AC-1: `from config.shared.team_colors import TEAM_COLORS` is present
      in `matchup_calculator.py`.
AC-2: team_a `team_color` uses
      `TEAM_COLORS.get(home_team) or TEAM_COLORS.get("VISITOR_TEAM") or TEAM_COLORS.get("Visitors", "gray")`.
AC-3: team_b `team_color` uses
      `TEAM_COLORS.get(visitor_label) or TEAM_COLORS.get("VISITOR_TEAM") or TEAM_COLORS.get("Visitors", "gray")`.
AC-4: `team_tone` remains `None` for both teams.
AC-5: No other logic in `_build_country_h2h_structured()` changed.
AC-6: GATE 1 boundary-sentinel PASS.
AC-7: GATE 6 compliance bouncer PASS with zero new violations.

### Files In Scope
- `core/calculators/team/matchup_calculator.py`
- READ ONLY - `core/calculators/team/venue_calculator.py`
- READ ONLY - `config/shared/team_colors.py`

## TASK-112 - country-h2h-types.ts readStringOrNumber fix
**Type:** frontend-bug-fix
**Scope:** frontend
**Priority:** High
**Depends On:** TASK-109
**Created:** 2026-03-12
**Status:** CLOSED - 2026-03-12

### Description
Fix numeric field dropout in `frontend/lib/country-h2h-types.ts`.

The backend type contract for bat1/chase stat fields (`low_def`, `high`,
`low`, `avg_win`, `avg`, `succ`, `fail`) allows `int | str | None`. When the
backend returns a plain integer (for example `low_def = 271`), the frontend
parser silently drops it to `""` because `readString()` only accepts
`typeof === "string"`. The empty string then passes through `renderValue()`
in `CountryH2HReport.tsx` and displays as a dash.

### Acceptance Criteria
AC-1: `readStringOrNumber()` helper exists in `country-h2h-types.ts`.
AC-2: All bat1 stat fields use `readStringOrNumber()`.
AC-3: All chase stat fields use `readStringOrNumber()`.
AC-4: `readString()` remains for string-only fields.
AC-5: No `any`, final `unknown`, or bare `object` introduced.
AC-6: Gate F3 passes.
AC-7: Gate 6 bouncer PASS with zero new violations versus baseline.

### Files In Scope
- `frontend/lib/country-h2h-types.ts`
- READ ONLY - `frontend/components/renderers/CountryH2HReport.tsx`
- READ ONLY - `core/interfaces/team_types.py`

## TASK-111 - country_h2h opp_team regression fix
**Type:** bug-fix
**Scope:** backend
**Priority:** High
**Depends On:** TASK-107, TASK-108
**Created:** 2026-03-12
**Status:** CLOSED - 2026-03-12

### Description
Fix the `country_h2h` regression where `team_b` never reached the backend
because the manifest treated it as optional and the engine defaulted
`opp_team` to `"All"`, inflating host-country match counts and rendering
the visitor label as a placeholder.

### Acceptance Criteria
AC-1: `team_b` moved to `required_context` for `country_h2h`.
AC-2: `analyze_country_h2h()` requires `opp_team: str` with no default.
AC-3: `calculate_country_h2h_payload()` returns `{"payload": {}}`
      immediately if normalized `opp_scope == "All"`.
AC-4: `"VISITOR_TEAM"` does not appear in `matchup_calculator.py`.
AC-5: Gate 3 manifest-contract-verifier PASS.
AC-6: Gate 6 compliance bouncer PASS with zero new violations.

### Files In Scope
- `formats/odi/manifest.py`
- `formats/odi/engines/team_engine.py`
- `core/calculators/team/matchup_calculator.py`
- READ ONLY - `docs/ai/tasks/`

## TASK-110 - Task 4 - Create CountryH2HReport.tsx and register country_h2h_report
**Type:** frontend-new-component
**Scope:** frontend
**Priority:** High
**Depends On:** TASK-107, TASK-108, TASK-109
**Created:** 2026-03-12
**Status:** CLOSED - 2026-03-12

### Description
Create `frontend/components/renderers/CountryH2HReport.tsx` and register it
in `frontend/components/renderers/FunctionRenderer.tsx` under
`output_type="country_h2h_report"`.

The new renderer mirrors the Venue Matchup presentation structure:
3-column summary hero bar, optional form-guide strip, two team cards with
Batting 1st and Chasing sections, averages footer, and sparse-data notice.
Audit rendering remains owned by `FunctionRenderer` via `renderMatchAudit()`.

### Acceptance Criteria
AC-1: `frontend/components/renderers/CountryH2HReport.tsx` exists on disk.
AC-2: CountryH2HReport imports `CountryH2HData` and `getCountryH2HData`
      from `@/lib/country-h2h-types`.
AC-3: CountryH2HReport renders the same structure as VenueMatchupReport.
AC-4: `averagesTitle` defaults to `"COUNTRY AVERAGES"`.
AC-5: `MatchAuditSection` is not rendered inside CountryH2HReport.
AC-6: Team colors are injected via `useEffect` + CSS custom properties.
AC-7: team_a uses the home accent and team_b uses the away accent.
AC-8: `EmptyState` renders if `getCountryH2HData()` returns null.
AC-9: Zero `@keyframes` definitions in CountryH2HReport.tsx.
AC-10: Zero raw hex color values in CountryH2HReport.tsx.
AC-11: Zero illegal inline object/array props.
AC-12: Zero `any`, final `unknown`, or bare `object` in signatures.
AC-13: `FunctionRenderer.tsx` adds a `React.lazy()` import for CountryH2HReport.
AC-14: `FunctionRenderer.tsx` adds a `country_h2h_report` case mirroring
       `venue_matchup_report`.
AC-15: Existing `comparison_table`, `venue_matchup_report`, and `home_fortress`
       cases remain untouched.
AC-16: Gates F1, F2, F3, 5, and 6 all pass.

### Files In Scope
- `frontend/components/renderers/CountryH2HReport.tsx`
- `frontend/components/renderers/FunctionRenderer.tsx`
- READ ONLY - `frontend/components/renderers/VenueMatchupReport.tsx`
- READ ONLY - `frontend/components/renderers/FortressReport.tsx`
- READ ONLY - `frontend/components/renderers/MatchAuditSection.tsx`
- READ ONLY - `frontend/lib/country-h2h-types.ts`
- READ ONLY - `frontend/lib/venue-types.ts`
- READ ONLY - `frontend/lib/comparison-types.ts`

## TASK-109 - Task 3 - Create frontend/lib/country-h2h-types.ts
**Type:** frontend-new-component
**Scope:** frontend
**Priority:** High
**Depends On:** TASK-107, TASK-108
**Created:** 2026-03-12
**Status:** CLOSED - 2026-03-12

### Description
Create `frontend/lib/country-h2h-types.ts` as the frontend type contract
for the structured `country_h2h_report` payload. The file must define
`CountryH2HData` as a distinct type that mirrors the Venue Matchup
payload structure, plus `getCountryH2HData()` to parse that payload for
the renderer follow-up task.

### Acceptance Criteria
AC-1: `frontend/lib/country-h2h-types.ts` exists on disk.
AC-2: `CountryH2HData` mirrors `VenueMatchupData` structure.
AC-3: `CountryH2HData` includes the required `@schema` JSDoc tag.
AC-4: `getCountryH2HData()` exports the mirrored parser.
AC-5: Helper usage aligns with the established Venue Matchup parsing pattern.
AC-6: No `any`, final `unknown`, or bare `object` in type signatures.
AC-7: GATE F3 passes.
AC-8: Post-task compliance bouncer PASS with zero new violations.

### Files In Scope
- `frontend/lib/country-h2h-types.ts`
- READ ONLY - `frontend/lib/venue-types.ts`
- READ ONLY - `frontend/lib/fortress-types.ts`
- READ ONLY - `core/interfaces/team_types.py`

## TASK-108 - Task 2 - Wire analyze_country_h2h() and manifest to new payload
**Type:** modification
**Scope:** backend
**Priority:** High
**Depends On:** TASK-107
**Created:** 2026-03-12
**Status:** CLOSED - 2026-03-12

### Description
Wire `formats/odi/engines/team_engine.py` and
`formats/odi/manifest.py` to the structured country H2H payload
introduced by TASK-107. `analyze_country_h2h()` must consume
`{"payload": VenueMatchupReport}` instead of `{"rows": ...}`,
and the manifest must expose output_type `country_h2h_report`
for the frontend renderer follow-up tasks.

### Acceptance Criteria
AC-1: `analyze_country_h2h()` calls `payload.get("payload", {})`
      instead of `payload.get("rows", [])`.
AC-2: `analyze_country_h2h()` casts to `VenueMatchupReport`
      instead of `ComparisonReportRows`.
AC-3: `analyze_country_h2h()` return type annotation is updated
      to `VenueMatchupReport`.
AC-4: The `country_h2h` entry in `formats/odi/manifest.py` has
      output_type `country_h2h_report`.
AC-5: No other field in the `country_h2h` manifest entry changes.
AC-6: Gate 3 manifest-contract-verifier PASS.
AC-7: Post-task compliance bouncer PASS with zero new violations.

### Files In Scope
- `formats/odi/engines/team_engine.py`
- `formats/odi/manifest.py`
- READ ONLY - `core/calculators/team/matchup_calculator.py`
- READ ONLY - `core/interfaces/team_types.py`
- READ ONLY - `docs/ai/tasks/task1_h2h_payload_restructure_report.md`

## TASK-107 - Task 1 (revised) - Country H2H Payload Restructure
**Type:** modification
**Scope:** backend
**Priority:** High
**Depends On:** NONE
**Created:** 2026-03-12
**Status:** CLOSED - 2026-03-12

### Description
Extract `_build_country_h2h_structured()` in
`core/calculators/team/matchup_calculator.py` so
`calculate_country_h2h_payload()` can return a structured
`VenueMatchupReport`-compatible payload computed directly from
`clean_df`, without touching `ReportBuilder` or
`_comparison_rows()`.

### Acceptance Criteria
AC-1: `_build_country_h2h_structured()` exists in
      `matchup_calculator.py` with a fully typed signature and
      returns a `VenueMatchupReport`-compatible dict.
AC-2: All required aggregates are computed with vectorized
      Pandas or NumPy operations only.
AC-3: `calculate_country_h2h_payload()` returns
      `{"payload": ...}` and its return annotation is
      `VenueMatchupPayload`.
AC-4: `_comparison_rows()` and `core/services/report_builder.py`
      remain untouched.
AC-5: `ComparisonRowsPayload` remains in place.
AC-6: All triggered gates pass and post-task bouncer output
      matches baseline.

### Files In Scope
- `core/calculators/team/matchup_calculator.py`
- READ ONLY - `core/calculators/team/venue_calculator.py`
- READ ONLY - `core/services/report_builder.py`
- READ ONLY - `core/interfaces/team_types.py`
- READ ONLY - `docs/ai/tasks/task1_h2h_payload_restructure_report.md`

## TASK-106 - Extract fortress-types.ts, fix R6 violations, restore FortressReport formatting
**Type:** frontend-modification
**Scope:** frontend
**Priority:** High
**Depends On:** TASK-105
**Created:** 2026-03-11
**Status:** CLOSED - 2026-03-11

### Description
FortressReport.tsx contains payload extraction and type coercion
functions that belong in lib/, not in a renderer. TASK-105 hardened
GATE F2 to flag these as Rule 2.2A-R6 violations. This task fixes
the violation by extracting the offending functions into a new file
frontend/lib/fortress-types.ts, mirroring exactly how VenueMatchupReport
imports from lib/venue-types.ts.

FortressReport.tsx imports from the new lib file and is cleaned up.
After extraction, FortressReport.tsx will be well under 300 lines with
proper multi-line formatting fully restored.

### Acceptance Criteria
AC-1: `frontend/lib/fortress-types.ts` created, exports all types and
      functions listed in WHAT TO EXTRACT.
AC-2: `FortressReport.tsx` imports from `@/lib/fortress-types`.
AC-3: `FortressReport.tsx` contains zero functions that accept `unknown`
      as first/sole parameter.
AC-4: `FortressReport.tsx` raw line count is under 300 with proper
      multi-line JSX formatting fully restored.
AC-5: GATE F2 runs clean with zero violations across the full frontend tree.
AC-6: `FortressReport.tsx` behaviour is unchanged.
AC-7: `frontend/lib/fortress-types.ts` has no React imports.
AC-8: GATE F3 triggered and passed after creating the new `lib/` file.
AC-9: Post-task compliance bouncer PASS, violation count matches baseline.

### Files In Scope
- `frontend/lib/fortress-types.ts`
- `frontend/components/renderers/FortressReport.tsx`
- READ ONLY - `frontend/lib/venue-types.ts`
- READ ONLY - `frontend/lib/comparison-types.ts`

## TASK-105 - Add payload extractor detection rule R6 to frontend-paradigm-sentinel
**Type:** validator-fix
**Scope:** tooling
**Priority:** High
**Depends On:** TASK-104
**Created:** 2026-03-11
**Status:** CLOSED - 2026-03-11

### Description
frontend-paradigm-sentinel had no rule detecting payload extraction
functions inside renderer files. This allowed FortressReport.tsx to
embed raw API payload parsing and type coercion helpers that belong in
`lib/`, not in renderer components.

The new rule targets functions in `components/renderers/` whose sole or
first parameter is typed `unknown` and whose return type is a non-display
domain type. Display-safe helpers remain exempt.

### Acceptance Criteria
AC-1: `check_payload_extractor_in_renderer()` exists in
      `run_frontend_paradigm.py` and is called from `scan_file()`.
AC-2: All 7 audited FortressReport payload extractors are flagged.
AC-3: All 8 audited legitimate helpers remain exempt.
AC-4: Full-tree GATE F2 produces violations only on FortressReport.tsx.
AC-5: `SKILL.md` includes Rule 2.2A-R6 in the checks table.
AC-6: Post-task compliance bouncer PASS matches baseline.

### Files In Scope
- `core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/scripts/run_frontend_paradigm.py`
- `core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/SKILL.md`

## TASK-104 - Inject team jersey colours for all audit table teams in FortressReport
**Type:** bug-fix
**Scope:** both
**Priority:** High
**Depends On:** TASK-103
**Created:** 2026-03-11
**Status:** CLOSED - 2026-03-11

### Description
Team names in the Fortress Report match audit table render without jersey
colours. In VenueMatchup this works because the two team card colours are
injected as CSS vars. In Fortress the audit table shows many visiting teams
(England, India, Bangladesh, Australia etc.) and none of their CSS vars are
injected.

Fix: add a team_colors dict to HomeFortressReport payload containing
{team_name: hex_color} for every unique team appearing in clean_df.
The frontend useEffect in FortressReport.tsx iterates this dict and
injects a CSS var for each team, making MatchAuditSection colour
resolution work identically to VenueMatchup.

### Acceptance Criteria
AC-1: HomeFortressReport TypedDict in team_types.py has:
      team_colors: dict[str, str]
      stop-state-trace-confirm performed and recorded.
AC-2: calculate_home_fortress_structured_payload() populates team_colors:
      all unique team names from clean_df["team_bat_1"] and
      clean_df["team_bat_2"] combined, looked up via TEAM_COLORS.get().
      Teams with no entry in TEAM_COLORS are omitted.
AC-3: team_colors is added to the HomeFortressReport dict in the
      calculator alongside the other top-level keys.
AC-4: FortressReport.tsx useEffect injects CSS vars for
      all entries in team_colors and cleans them up on unmount.
AC-5: All team names in the match audit table render with jersey
      colours matching VenueMatchup.
AC-6: No domain logic added to the frontend component.
AC-7: GATE F3 triggered only if lib/types.ts is modified.
AC-8: Post-task compliance bouncer PASS, violation count matches baseline.

### Files In Scope
- `core/interfaces/team_types.py`
- `core/calculators/team/venue_calculator.py`
- `frontend/components/renderers/FortressReport.tsx`
- READ ONLY - `config/shared/team_colors.py`
- READ ONLY - `frontend/components/renderers/VenueMatchupReport.tsx`

## TASK-103 - Use Visitors sentinel for aggregate visitor batting stats in fortress calculator
**Type:** bug-fix
**Scope:** backend
**Priority:** High
**Depends On:** TASK-102
**Created:** 2026-03-11
**Status:** CLOSED - 2026-03-11

### Description
Visitor batting/chasing stats in the Fortress Report were rendering as dashes
when `opp_team == "All"` because the structured payload path was not routing
aggregate visitors through the existing `"Visitors"` sentinel branch in
`calculate_team_metrics()`.

### Acceptance Criteria
AC-1: When `opp_team == "All"`, visitor batting/chasing stats are populated
      with real values instead of dashes.
AC-2: Visitor wins/defended/chased counts remain unchanged from TASK-102.
AC-3: Visitor display name remains `VISITORS` in the report.
AC-4: `_team_intel()` receives `"Visitors"` as the sentinel string.
AC-5: `home_team_ref` is added only to a `visitor_df` copy.
AC-6: Specific-opponent behaviour remains unchanged.
AC-7: No other source files are modified.
AC-8: Post-task compliance bouncer PASS, matching the baseline.

### Files In Scope
- `core/calculators/team/venue_calculator.py`
- READ ONLY - `core/calculators/performance.py`

## TASK-102 - Fix visitor stats, visitor label, and match audit in HomeFortress calculator
**Type:** bug-fix
**Scope:** backend
**Priority:** High
**Depends On:** TASK-101
**Created:** 2026-03-11
**Status:** CLOSED - 2026-03-11

### Description
Three bugs in calculate_home_fortress_structured_payload() in
core/calculators/team/venue_calculator.py:

1. Visitor stats are empty when opp_team == "All"; the visitor side should
   aggregate all non-home winners as a combined visitor pool.
2. Visitor label currently shows "All"; it must display "VISITORS".
3. No match audit renders because the structured payload omits the MATCH_IDS
   key that enrichment uses to inject match_audit.

### Acceptance Criteria
AC-1: When opp_team == "All", visitor card name is "VISITORS" (not "All").
AC-2: When opp_team == "All", visitor wins/defended/chased are computed
      from summary_df (non-home-team winners) and are not zeroed out.
AC-3: When opp_team == "All", visitor batting/chasing stat rows may remain
      None/dash, but wins/defended/chased counts are correct.
AC-4: When opp_team is a specific team, _team_intel() behaviour is unchanged.
AC-5: The HomeFortressReport dict includes a MATCH_IDS key built from
      clean_df["match_id"].
AC-6: Match audit renders through enrichment after Execute Analysis.
AC-7: No changes to enrichment.py, team_engine.py, manifest.py,
      api/serializers.py, or any frontend file.
AC-8: If HomeFortressReport TypedDict required MATCH_IDS, stop-state-trace-confirm
      was performed and recorded.
AC-9: All new code uses vectorized Pandas operations.
AC-10: Post-task compliance bouncer PASS, violation count matches baseline.

### Files In Scope
- `core/calculators/team/venue_calculator.py`
- `core/interfaces/team_types.py` (only if MATCH_IDS must be added)
- READ ONLY - `core/services/enrichment.py`
- READ ONLY - `core/interfaces/team_types.py`

## TASK-101 - Hardcode opp_team=All in analyze_home_fortress_structured, retire old manifest entry
**Type:** bug-fix
**Scope:** backend
**Priority:** High
**Depends On:** TASK-100A
**Created:** 2026-03-11
**Status:** CLOSED - 2026-03-11

### Description
analyze_home_fortress_structured() currently accepts opp_team as a
parameter. The manifest entry for home_fortress_structured does not
include opp_team in required_context, so the API layer never passes it,
causing a missing positional argument error at runtime.

The intended behaviour of the Fortress Report is home team vs ALL teams
at the venue - opp_team is always "All" regardless of what the user has
selected in the away team dropdown. opp_team must be removed from the
method signature entirely and hardcoded to "All" inside the method body.

Additionally, the old home_fortress manifest entry (key: "home_fortress",
engine_method: "analyze_home_fortress", output_type: "comparison_table")
must be retired - it is superseded by home_fortress_structured. Leaving
both active causes two "Fortress Report" tabs to appear in the UI.

### Acceptance Criteria
AC-1: analyze_home_fortress_structured() in team_engine.py has NO
      opp_team parameter in its signature.
AC-2: Inside analyze_home_fortress_structured(), opp_team is set to
      the string "All" before being passed to
      calculate_home_fortress_structured_payload() via the context dict.
AC-3: The method still accepts: stadium_name, home_team, years_back,
      match_context - unchanged from TASK-100A minus opp_team.
AC-4: The old manifest entry with key "home_fortress" and
      engine_method "analyze_home_fortress" is removed.
AC-5: The manifest entry with engine_method "analyze_home_fortress_structured"
      has key "home_fortress" (renamed from "home_fortress_structured").
AC-6: Only one "Fortress Report" entry exists in the manifest after the fix.
AC-7: KIP-001 and KIP-002 untouched.
AC-8: Post-task compliance bouncer PASS, violation count matches baseline.

### Files In Scope
- `formats/odi/engines/team_engine.py`
- `formats/odi/manifest.py`
- READ ONLY - `formats/odi/engines/team_engine.py`
- READ ONLY - `formats/odi/manifest.py`

## TASK-100B - Create FortressReport.tsx and register home_fortress case in FunctionRenderer
**Type:** frontend-new-component
**Scope:** frontend
**Priority:** High
**Depends On:** TASK-100A
**Created:** 2026-03-11
**Status:** CLOSED - 2026-03-11

### Description
TASK-100A added analyze_home_fortress_structured() and registered
output_type "home_fortress" in the manifest. This task creates the
frontend renderer for that output type.

Create frontend/components/renderers/FortressReport.tsx from scratch
using the VenueMatchup presentation system (glass panels, tone-mapped
team cards, StatBadge pills, SectionHeader/DataRow rows, FooterItem
venue averages, low-sample warning banner). Register it in
FunctionRenderer.tsx under case "home_fortress". No backend files,
no API contract, no types.ts, no manifest changes.

### Acceptance Criteria
AC-1: FortressReport.tsx created at
      frontend/components/renderers/FortressReport.tsx.
AC-2: FunctionRenderer.tsx adds the FortressReport lazy import and the
      home_fortress switch case.
AC-3: Root wrapper uses the required max-w-5xl animate-fade-in layout.
AC-4: Summary bar renders Matches, Home Win %, and Tied/NR in a glass panel.
AC-5: Home team card follows the VenueMatchup tone + heading treatment.
AC-6: Visitor card always renders, including zero-filled All-opponent payloads.
AC-7: Batting 1st and Chasing sections use SectionHeader/DataRow with bracket splits.
AC-8: Venue averages footer uses the shared footer presentation pattern.
AC-9: Low-sample warnings render the sparse-data notice banner when present.
AC-10: team_color CSS vars are injected via useEffect and cleaned up on unmount.
AC-11: toneClasses() is copied verbatim from VenueMatchupReport.tsx.
AC-12: DataRow bracket annotation renderer is copied verbatim.
AC-13: No hardcoded hex values are introduced.
AC-14: No inline styles are used except the team heading style.
AC-15: No new CSS variable names are introduced.
AC-16: EmptyState fallback exists for unrecognisable payloads.
AC-17: match_audit is not rendered inside FortressReport.tsx.
AC-18: GATE F3 remains skipped because lib/types.ts is untouched.
AC-19: Post-task bouncer matches the baseline PASS.

### Files In Scope
- frontend/components/renderers/FortressReport.tsx
- frontend/components/renderers/FunctionRenderer.tsx

## TASK-100A - Add HomeFortressReport structured payload and register home_fortress output type
**Type:** backend - new-feature
**Scope:** backend
**Priority:** High
**Depends On:** TASK-099
**Created:** 2026-03-11
**Status:** CLOSED - 2026-03-11

### Description
Add a parallel structured Home Fortress path so the calculator and engine can
return typed venue context instead of only flat comparison rows. The new path
must add `HomeFortressReport`, build a structured payload from the existing
fortress filter pipeline, expose `analyze_home_fortress_structured()`, and
register a new `home_fortress` manifest output type without changing the
existing flat fortress method.

### Acceptance Criteria
AC-1: `core/interfaces/team_types.py` exports `HomeFortressReport`.
AC-2: `HomeFortressReport` mirrors the venue-matchup structure with
      summary/home/visitor/venue_avg/low_sample_warnings.
AC-3: `HomeFortressStructuredPayload` is added to venue_calculator.
AC-4: `calculate_home_fortress_structured_payload()` uses the existing
      fortress filter pipeline and returns `{"payload": {}}` on empty data.
AC-5: `analyze_home_fortress_structured()` mirrors the structured
      venue-matchup engine signature and return cast pattern.
AC-6: `formats/odi/manifest.py` registers a new `home_fortress` output type
      and a separate function entry pointing at the structured engine method.
AC-7: Existing flat fortress methods remain unchanged.
AC-8: All new functions have complete type hints with no `Any`/`object`.
AC-9: KIP-001 and KIP-002 in `team_engine.py` remain untouched.
AC-10: Post-task compliance bouncer matches the baseline PASS.

### Files In Scope
- `core/interfaces/team_types.py`
- `core/calculators/team/venue_calculator.py`
- `formats/odi/engines/team_engine.py`
- `formats/odi/manifest.py`

## TASK-099 - Tighten Match Audit cell contrast, widths, and status labels
**Type:** frontend-modification
**Scope:** frontend
**Priority:** High
**Depends On:** TASK-098
**Created:** 2026-03-11
**Status:** CLOSED - 2026-03-11

### Description
Two issues remain in the Match Audit table of the Venue Matchup / Fortress
Report screen after TASK-098. First, the white text outline applied to team
name headings in TASK-098 was not applied to the team name spans inside the
BAT 1ST and BAT 2ND cells - Sri Lanka's blue jersey colour bleeds into the
dark background making it unreadable. Second, column spacing between VENUE,
WINNER, BAT 1ST, BAT 2ND, and STATUS is too wide causing a horizontal
scrollbar - all columns must fit within the viewport with minimal gaps. The
STATUS column pill labels are also too verbose for the available space and
must be shortened to compact icon-based labels that still communicate the
excluded innings.

### Acceptance Criteria
AC-1: Team name spans inside BAT 1ST and BAT 2ND cells have the same
      thin white text outline/shadow applied as the panel headings -
      no jersey colour bleeds into the dark background.

AC-2: All Match Audit columns - DATE, VENUE, WINNER, BAT 1ST, BAT 2ND,
      STATUS - fit within the viewport width with no horizontal scrollbar.

AC-3: Column gaps between all adjacent columns are minimal and consistent
      - approximately 0.5rem or equivalent tight spacing.

AC-4: STATUS column uses compact pill labels:
      - Included       -> ✅ (green pill)
      - Excluded Short 2nd innings -> 2nd ⛔ (amber/red pill)
      - Excluded Short 1st innings -> 1st ⛔ (amber/red pill)
      Any other excluded reason -> ⛔ with shortest meaningful label.

AC-5: All columns remain readable - no text truncation on DATE, VENUE,
      WINNER, or score values in BAT 1ST and BAT 2ND.

AC-6: No regression - all data values, jersey colours on team names,
      and existing pill styling remain correct.

AC-7: Post-task bouncer output matches or improves on baseline.

### Files In Scope
- frontend/components/renderers/MatchAuditSection.tsx

## TASK-098 - Tighten Venue Matchup Report panel styling and merge innings display columns
**Type:** frontend-modification
**Scope:** frontend
**Priority:** High
**Depends On:** TASK-096
**Created:** 2026-03-11
**Status:** CLOSED - 2026-03-11

### Description
The Venue Matchup / Fortress Report screen has several remaining visual issues
after the TASK-096 polish pass. The team panel boxes have excessively rounded
corners and are too large - they should use subtle corners matching the old
reference application. Metric result values are rendered in a different font
size and weight to their labels - they must match exactly. Team name headings
need a thin white text outline/border so jersey colours that are close to the
dark background remain legible. The Match Audit table is restructured: the
separate 1ST INN and 2ND INN columns are removed and their scores are merged
into the BAT 1ST and BAT 2ND columns respectively, formatted as
"TeamName Score (Overs)" in a single cell. This is a frontend-only display
change - the API payload is not modified.

### Acceptance Criteria
- AC-1: Panel border-radius is reduced to match the subtle corner style of
  the reference ipywidgets application - not heavily rounded.
- AC-2: Panel internal padding and sizing is reduced so metrics fit snugly
  with consistent, compact spacing - no excessive whitespace inside the panel.
- AC-3: Metric result values use the exact same font family and font size
  as their row labels. No bold. No size difference between label and value.
- AC-4: Team name headings (SRI LANKA, ENGLAND) have a thin white
  text outline or border so jersey colours that are close to the
  dark theme background remain clearly visible.
- AC-5: Match Audit table has no separate 1ST INN or 2ND INN columns.
- AC-6: BAT 1ST column displays team name and innings score combined in
  one cell - format: "TeamName Score (Overs)"
  e.g. "England 357/3 (50.0)". Team name rendered in jersey colour.
- AC-7: BAT 2ND column displays team name and innings score combined in
  one cell - same format as BAT 1ST.
  e.g. "Sri Lanka 304/10 (46.4)". Team name rendered in jersey colour.
- AC-8: Match Audit table columns are evenly spaced and readable after
  the restructure - no jammed columns, no truncation.
- AC-9: All data values (scores, overs, team names, status) remain
  correct - no data regression from the display restructure.
- AC-10: Post-task bouncer output matches or improves on baseline.

### Files In Scope
- `frontend/components/renderers/VenueMatchupReport.tsx`
- `frontend/components/renderers/MatchAuditSection.tsx`

## TASK-097 - Canonicalize venue IDs in match audit enrichment
**Type:** bug-fix
**Scope:** backend
**Priority:** High
**Depends On:** TASK-093
**Created:** 2026-03-10
**Status:** CLOSED - 2026-03-10

### Description
The Match Audit table in the Venue Matchup / Fortress Report screen displays
raw inconsistent venue name strings (e.g. "R Premadasa Stadium, Colombo" and
"R.Premadasa Stadium, Khettarama" for the same physical ground). A diagnosis
task confirmed the fix belongs in core/services/enrichment.py, specifically
where _build_audit_record() constructs the venue field. The DAL already
returns canonical venue_id alongside the raw venue string. The fix must update
enrichment.py to prefer the DAL-provided venue_id when building audit rows,
falling back to resolving the raw venue string via config/shared/venues.py only
when venue_id is absent. The serializer, frontend, and DAL must not be touched.

### Acceptance Criteria
- AC-1: _build_audit_record() in enrichment.py prefers the DAL-provided
  venue_id field when constructing the venue field in audit rows.
- AC-2: When venue_id is absent from the DAL row, the enrichment service
  falls back to resolving the raw venue string via venues.py to obtain the
  canonical ID.
- AC-3: When neither venue_id nor a resolvable raw venue string is available,
  the raw venue string is used as-is; no crash, no empty field.
- AC-4: All Match Audit rows for the same physical ground display the same
  canonical venue identifier regardless of what raw string variant the DAL
  row carries.
- AC-5: No other enrichment.py logic is altered; only the venue field
  construction in _build_audit_record() changes.
- AC-6: All modified functions retain complete type annotations.
- AC-7: Post-task bouncer output matches or improves on baseline.
- AC-8: Doc cleanup for the preceding diagnosis task is complete.

### Files In Scope
- `core/services/enrichment.py`
- READ ONLY - `config/shared/venues.py`
- READ ONLY - `core/data_access.py`
- READ ONLY - `api/serializers.py`
- READ ONLY - `core/interfaces/team_types.py`

## TASK-096 - Venue Matchup Report jersey colours and layout refinements
**Type:** frontend-modification
**Scope:** frontend
**Priority:** High
**Depends On:** TASK-095
**Created:** 2026-03-10
**Status:** CLOSED - 2026-03-10

### Description
Following the TASK-095 visual polish pass, the Venue Matchup / Fortress Report
screen still needs jersey-colour team headings, softer metric values, clearer
panel spacing, a more visible accuracy notice, and better Match Audit table
separation without changing any data or backend behaviour.

### Acceptance Criteria
- AC-1: Team name headings in both panel headers use jersey colours from `config/shared/team_colors.py`.
- AC-2: Team names in the Match Audit table Winner, Bat 1st, and Bat 2nd columns use jersey colours from `config/shared/team_colors.py`.
- AC-3: Team panels have at least 16px horizontal margin from screen edges.
- AC-4: Panel rounded corners do not clip right-edge metric values.
- AC-5: Metric result values are visually softer while remaining distinct from labels.
- AC-6: Accuracy Notice banner uses a subtle but visible informational colour.
- AC-7: Match Audit table columns are clearly separated with no jammed adjacent values.
- AC-8: Avg Fail Chase displays fully in both panels without truncation.
- AC-9: Data, labels, values, and behaviour remain unchanged.
- AC-10: Post-task bouncer output matches or improves on baseline.

### Files In Scope
- `frontend/components/renderers/VenueMatchupReport.tsx`
- `frontend/components/renderers/MatchAuditSection.tsx`
- `frontend/components/ui/AccuracyNotice.tsx`
- `config/shared/team_colors.py` (read only)

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

*End of BACKLOG.md - Last Updated 2026-03-13*
*For current session state, see docs/ai/SESSION_STATE.md*
*For permanent project knowledge, see docs/ai/PROJECT_CONTEXT.md*
