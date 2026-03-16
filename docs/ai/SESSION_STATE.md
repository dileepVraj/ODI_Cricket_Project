# Session State
**Last Updated:** 2026-03-16
**Current Phase:** Phase 10 — Engine Layer Refactoring + Frontend Remediation.
Frontend compliance sprint COMPLETE 2026-03-09 (TASK-058 through TASK-072).
Compliance remediation sprint COMPLETE 2026-03-10 (TASK-073 through TASK-087).
Team engine COMPLIANT 2026-03-05. Player engine COMPLIANT 2026-03-06.
Predictor engine COMPLIANT 2026-03-07.
Venue matchup match-audit diagnosis + fix COMPLETE 2026-03-10 (TASK-092 + TASK-093).
Venue matchup match-audit venue canonicalization COMPLETE 2026-03-10 (TASK-097).
Project cleanup COMPLETE 2026-03-10 (commit 4bba4a6).
Claude Code MCPs installed 2026-03-10 (6 servers).

---

## Active Sprint
None.

## In Progress
- Nothing currently in progress

## Last Completed

- TASK-136 - Add SquadComparisonCard renderer for squad_comparison output type - CLOSED 2026-03-16
  Added `frontend/components/renderers/SquadComparisonCard.tsx`, wired
  `squad_comparison` into `FunctionRenderer.tsx` and `SkeletonLoader.tsx`,
  and renders slim compare-squads payloads as squad metrics plus per-team
  player stats tables. Gates F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-135 - Slim compare_squads to squad-metrics only - CLOSED 2026-03-16
  `compare_squads` now returns the slim Tab 0 `SquadComparisonData`
  payload only, `api/main.py` no longer wraps it in the legacy
  GlobalCompareEnvelope serialization layer, and `formats/odi/manifest.py`
  now exposes `output_type="squad_comparison"`. Gates 1/2/3/4/5/6 PASS,
  bouncer PASS.

- TASK-134 - Consolidate squad player search to single combobox field - CLOSED 2026-03-16
  `PlayerSearch.tsx` now renders only the `AccessibleCombobox`, and
  `SquadBuilder.tsx` no longer stores a parallel `searchTerm` /
  `filteredPlayers` layer before passing player options into the squad
  picker. Gates F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-133 - Fix get_last_match_xi same-match XI supplementation - CLOSED 2026-03-16
  `PlayerEngine.get_last_match_xi()` now supplements short `is_playing_xi=True`
  squad results with remaining same-match team rows ordered by `player_order`,
  leaving the balls-data fallback untouched and preventing ghost-player XI
  padding. Gates 2/3/5/6 PASS, compare_squads truth-bridge PASS, bouncer PASS.

- TASK-132 - Fix loadSquad h2h XI initialisation and batting-order preservation - CLOSED 2026-03-16
  `PlayerEngine.get_last_match_xi()` now accepts `opponent`, filters squads and
  fallback match history to head-to-head matches, preserves `player_order` /
  first-appearance batting order, and the API/frontend load-squad plumbing now
  forwards the counterpart team through `get_players()` and `fetchPlayers()`.
  Gates 2/3/F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-131 - SRP refactor of PlayerProfileCard.tsx and _view dispatch - CLOSED 2026-03-15
  `PlayerProfileCard.tsx` now renders the profile-only path, shared intel display
  helpers live in `frontend/lib/player-intel.ts`, and `FunctionRenderer.tsx`
  dispatches `profile_card` payloads to `PlayerBattingIntel.tsx` or
  `PlayerBowlingIntel.tsx` when `_view` requests an intel mode.
  Gates F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-130 - Add Gate F2 rule 2.2A-R7 for internal _view dispatch in leaf renderers - CLOSED 2026-03-15
  `run_frontend_paradigm.py` now adds `VIEW_DISPATCH_PATTERN` and
  `check_view_dispatch_in_renderer()`, and Gate F2 now fails intentionally
  on `PlayerProfileCard.tsx` until TASK-131 moves `_view` routing into
  `FunctionRenderer.tsx`.
  Gate F2 FAIL (expected), Gates 5/6 PASS, bouncer PASS.

- TASK-129 - Add Bowling Intel to player profile screen - CLOSED 2026-03-15
  `PlayerProfile` and `PlayerProfileSchema` now expose `phase_bowling`
  and `last_10_bowling`, `analyze_player_profile()` now derives
  venue-aware bowling phases from the same ground-filtered raw balls
  path, and `PlayerProfileCard.tsx` now renders a dedicated
  `Bowling Intel` panel.
  Gates 1/2/3/F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-128 - Make player profile phase_runs venue-aware - CLOSED 2026-03-15
  `PlayerProfile` and `PlayerProfileSchema` no longer expose
  `phase_runs_raw`, and `analyze_player_profile()` now derives
  `phase_runs` from the same ground-filtered `raw_bat_ground` path
  already used by `vs_bowling_style`.
  Gates 1/2/5/6 PASS, bouncer PASS.

- TASK-127 - Player Profile screen redesign - CLOSED 2026-03-15
  `player_profile` now exposes venue/year extra inputs plus
  dual `Profile` / `Batting Intel` execute buttons, with
  `_view`-enriched frontend rendering in `CategoryScreen.tsx`,
  `ExtraInputCombobox.tsx`, and `PlayerProfileCard.tsx`.
  Gates 3/F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-125 - Add Batting Intel toggle panel to PlayerProfileCard - CLOSED 2026-03-15
  `PlayerProfileCard.tsx` now adds a closed-by-default Batting Intel panel
  with last-10 score chips, phase-runs breakdown, and bowling-style tables
  plus CSS comparison bars. Gates F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-124 - Enhance analyze_player_profile with phase runs, vs-style breakdown, last_10_runs - CLOSED 2026-03-15
  `PlayerEngine.analyze_player_profile()` now adds `phase_runs`,
  `vs_bowling_style`, `phase_runs_raw`, and numeric `last_10_runs`
  payload fields, with country pre-filtering handled in
  `api/context_builder.py` and ground filtering handled in-engine.
  Gates 1/2/3/5/6 PASS, bouncer PASS.

- TASK-123 - Continent Performance matrix payload unification - CLOSED 2026-03-15
  `calculate_continent_performance_payload()` now preserves the existing
  opponent/continent mask logic while always returning `_matrix_rows(...)`,
  removing the flat comparison-table branch that broke the `matrix_table`
  contract whenever `opp_team` was a specific team. Gates 1/2/5/6 PASS,
  bouncer PASS.

- TASK-122 - Continent Performance optional context passthrough + Last 5 limit - CLOSED 2026-03-15
  `buildExecuteParams()` now forwards manifest-defined optional context values
  when they are non-empty and not `All`, `CategoryScreen.tsx` now passes
  `activeFn.optional_context`, and `ReportBuilder._build_form_data_payload()`
  now limits `raw_results` and derived counts to the five most recent matches.
  `MatrixTable.tsx` also removes an unused width helper and redundant top-level
  blank lines to restore frontend paradigm compliance. Gates 1/2/F1/F2/F3/5/6
  PASS, bouncer PASS.

- TASK-121 - Strict Decisions refactor — decisions = wins + losses in matrix report - CLOSED 2026-03-15
  `ReportBuilder._generate_matrix_report()` now defines per-opponent and
  OVERALL decisions explicitly as wins plus losses, derives Tie/NR from
  that count, and keeps silent local dirty-data diagnostics without
  changing the MatrixReportRow output contract. Gates 1/2/5/6 PASS,
  bouncer PASS.

- TASK-119R - MatrixTable column alignment, home team colour, chip label fix (retry) - CLOSED 2026-03-13
  `MatrixTable.tsx` now applies fixed table layout plus explicit width
  classes across every matrix header and cell, and hides OVERALL-only
  home-team metadata from visible columns.
  The existing CSS-variable effect now also injects `overallRow`
  `home_team_name` / `home_team_color`, and overall stat-chip labels
  use `--accent-primary`. Gates F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-120 - Add home_team_color and home_team_name to OVERALL row - CLOSED 2026-03-13
  `MatrixReportRow` now includes additive optional `home_team_color`
  and `home_team_name` keys, and `ReportBuilder._generate_matrix_report()`
  now emits them only on the aggregate OVERALL row via `TEAM_COLORS`.
  Gates 1/2/5/6 PASS, bouncer PASS.

- TASK-118 - MatrixTable + MatchAuditSection frontend fixes - CLOSED 2026-03-13
  `MatrixTable.tsx` now renders `form_data.raw_results` as emoji-based
  `Last 5`, removes the overall stat-chip slice limit, and injects
  row-level `team_color` CSS variables for opponent cells.
  `MatchAuditSection.tsx` now colours team-name headers with
  `--accent-primary` while keeping date/venue muted and status secondary.
  Gates F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-117 - Add team_color to MatrixReportRow in report_builder.py - CLOSED 2026-03-13
  `MatrixReportRow` now includes an additive optional `team_color` field,
  and `ReportBuilder._generate_matrix_report()` now emits opponent-row team
  colours via `TEAM_COLORS` while setting the aggregate OVERALL row to `None`.
  Gates 1/2/5/6 PASS, bouncer PASS.

- TASK-116 - Remove hardcoded top_teams filter in report_builder.py - CLOSED 2026-03-12
  `ReportBuilder._generate_matrix_report()` now derives its opponent rows
  from `clean["opponent"].unique()` instead of a hardcoded top-10 list,
  and the OVERALL row aggregates that same dynamic opponent set.
  Gates 1/2/5/6 PASS, bouncer PASS.

- TASK-115 - GlobalH2HReport frontend renderer + FunctionRenderer registration - CLOSED 2026-03-12
  Added `frontend/lib/global-h2h-types.ts`,
  `frontend/components/renderers/GlobalH2HReport.tsx`, and the
  `global_h2h_report` dispatcher path in `FunctionRenderer.tsx`.
  Committed alongside TASK-115: pre-existing branding changes from the
  prior session task chain — app name changed from
  `CricketAlgo | Trading` to `Vantage | Strategic Algo Exchange`,
  FormatSelector sidebar name/subtitle updated, default UI font moved to
  Cascadia Code, Vantage shield icon replaced
  `frontend/app/icon.png` and `frontend/public/icon.png`, and
  `frontend/app/layout.tsx` metadata title updated. Gates F1/F2/F3/5/6
  PASS, bouncer PASS.

- TASK-114 - Add analyze_global_h2h_structured backend method + manifest registration - CLOSED 2026-03-12
  Added `calculate_global_h2h_structured_payload()` plus
  `_build_global_h2h_structured()` in `matchup_calculator.py`,
  `analyze_global_h2h_structured()` in `team_engine.py`, and a new
  `global_h2h_structured` manifest entry with
  `output_type=\"global_h2h_report\"`. Gates 1/2/3/4/5/6 PASS,
  bouncer PASS.

- TASK-113 - country_h2h structured team colors fix - CLOSED 2026-03-12
  `core/calculators/team/matchup_calculator.py` now imports `TEAM_COLORS`
  and populates both Country H2H team-card `team_color` fields with the same
  fallback chain used by `venue_calculator.py`. Gates 1/2/4/5/6 PASS, bouncer PASS.

- TASK-112 - country-h2h-types.ts readStringOrNumber fix - CLOSED 2026-03-12
  `country-h2h-types.ts` now preserves numeric country-H2H bat1/chase values
  by coercing strings or numbers to string during parsing instead of dropping
  ints to `""`. Gates F1/F2/F3/5/6 PASS and bouncer PASS.

- TASK-111 - country_h2h opp_team regression fix - CLOSED 2026-03-12
  `country_h2h` now requires `team_b` in the manifest, and
  `analyze_country_h2h()` no longer defaults `opp_team` to `"All"`.
  The calculator now exits early on stale `"All"` requests and removes the
  `VISITOR_TEAM` placeholder. Gates 1/2/3/4/5/6 PASS, bouncer PASS.

- TASK-110 - Task 4 - CountryH2HReport renderer + FunctionRenderer wiring - CLOSED 2026-03-12
  Added `frontend/components/renderers/CountryH2HReport.tsx` and registered
  `country_h2h_report` in `FunctionRenderer.tsx`, mirroring the Venue Matchup
  layout while keeping match audit rendering in the dispatcher. Gates F1/F2/F3/5/6
  PASS and bouncer PASS.

- TASK-109 - Task 3 - Create frontend/lib/country-h2h-types.ts - CLOSED 2026-03-12
  Added `frontend/lib/country-h2h-types.ts` with a distinct
  `CountryH2HData` contract and a parser that mirrors the Venue Matchup
  adapter pattern. Gates F1/F2/F3/5/6 PASS and bouncer PASS.

- TASK-108 - Task 2 - Country H2H Engine + Manifest Wiring - CLOSED 2026-03-12
  `analyze_country_h2h()` now reads the structured `payload` key and
  returns `VenueMatchupReport`, while the `country_h2h` manifest entry
  now emits `output_type="country_h2h_report"`. Gates 2/3/4/5/6 PASS,
  bouncer PASS, and frontend renderer follow-up remains deferred.

- TASK-107 - Task 1 (revised) - Country H2H Payload Restructure - CLOSED 2026-03-12
  `calculate_country_h2h_payload()` now returns a structured
  `VenueMatchupReport`-compatible payload built directly from `clean_df`
  in `matchup_calculator.py`. Gates 1/2/4/5/6 PASS, Gate 3 SKIPPED,
  bouncer PASS, and the TeamEngine consumer update remains deferred to Task 2.

- TASK-106 - Extract fortress-types.ts, fix R6 violations, restore FortressReport formatting - CLOSED 2026-03-11
  FortressReport payload types and extraction helpers now live in
  `frontend/lib/fortress-types.ts`, and the renderer imports the adapter
  instead of coercing unknown payloads inline. Gates F1/F2/F3/5/6 PASS,
  bouncer PASS, FortressReport now 294 lines with zero R6 violations.

- TASK-105 - Add payload extractor detection rule R6 to frontend-paradigm-sentinel - CLOSED 2026-03-11
  Frontend paradigm sentinel now flags renderer-local payload extraction
  helpers whose first input is `unknown` and whose typed return is a domain
  object, while exempting display-safe helpers. GATE F2 now FAILS on the
  seven FortressReport extractors only (resolved by TASK-106),
  and bouncer PASS remains unchanged.

- TASK-104 - Inject team jersey colours for all audit table teams in FortressReport - CLOSED 2026-03-11
  Home Fortress structured payload now emits a typed `team_colors` map built
  from unique audit-table teams, and FortressReport injects runtime CSS vars
  for every entry so Match Audit team names resolve jersey colours. Gates
  1/2/3/4/F1/F2/5/6 PASS, GATE F3 SKIPPED, bouncer PASS.

- TASK-103 - Use Visitors sentinel for aggregate visitor batting stats in fortress calculator - CLOSED 2026-03-11
  Home Fortress structured payload now passes aggregate visitors through the
  existing `"Visitors"` metrics branch via a `visitor_df` copy with
  `home_team_ref`, while preserving VISITORS display text and TASK-102 counts.
  Gates 1/2/3/4/5/6 PASS, bouncer PASS.

- TASK-102 - Fix visitor stats, visitor label, and match audit in HomeFortress calculator - CLOSED 2026-03-11
  Home Fortress structured payload now labels the aggregate away side as
  VISITORS, computes all-visitor wins/defended/chased from summary_df when
  opp_team is "All", and emits MATCH_IDS so enrichment injects match_audit.
  Gates 1/2/3/4/5/6 PASS, bouncer PASS.

- TASK-101 - Hardcode opp_team=All in analyze_home_fortress_structured, retire old manifest entry - CLOSED 2026-03-11
  `analyze_home_fortress_structured()` now hardcodes `opp_team="All"` and no
  longer requires the API to pass an away-team value. The legacy flat fortress
  manifest entry was removed, leaving one structured Fortress Report tab. Gates
  1/2/3/4/5/6 PASS, bouncer PASS.

- TASK-100B - Create FortressReport.tsx and register home_fortress case in FunctionRenderer - CLOSED 2026-03-11
  Added `FortressReport.tsx` and registered the `home_fortress` renderer path in
  `FunctionRenderer.tsx`, reusing the Venue Matchup glass-panel card system and
  runtime team-colour CSS variables for the structured fortress payload. Gates
  F1/F2/5/6 PASS, GATE F3 SKIPPED per task scope, bouncer PASS.

- TASK-100A - Add HomeFortressReport structured payload and register home_fortress output type - CLOSED 2026-03-11
  Added `HomeFortressReport`, a structured fortress calculator payload, and
  `analyze_home_fortress_structured()` so fortress analysis can return typed
  venue context alongside the legacy flat comparison-table path. Gates
  1/2/3/4/5/6 PASS, bouncer PASS.

- TASK-099 - Tighten Match Audit cell contrast, widths, and status labels - CLOSED 2026-03-11
  Match Audit team-name spans now reuse the existing token-based heading
  outline, status badges render compact icon labels, and column widths/padding
  were tightened to remove the horizontal scroll regression. Gates F1/F2/F3/5/6
  PASS, bouncer PASS.

- TASK-098 - Tighten Venue Matchup Report panel styling and merge innings display columns - CLOSED 2026-03-11
  Venue matchup team cards now use subtler corners, tighter padding, uniform
  metric typography, and token-based heading outlines for jersey-colour contrast.
  Match Audit now merges innings scores into Bat 1st/Bat 2nd cells without
  changing the backend payload. Gates F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-097 - Canonicalize venue IDs in match audit enrichment - CLOSED 2026-03-10
  Match Audit venue rows now prefer DAL-provided `venue_id` and fall back to
  `resolve_venue_id(raw venue)` before using raw text. Gates 1/2/5/6 PASS,
  bouncer PASS.

- TASK-096 - Venue Matchup Report jersey colours and layout refinements - CLOSED 2026-03-10
  Venue matchup team headers now use config-sourced jersey colours via the
  existing `team_color` payload, and Match Audit team-name cells resolve the
  same colours through runtime CSS variables. Panel spacing, metric readability,
  accuracy notice visibility, and audit-table column sizing were tightened.
  Gates F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-095 - Refine Venue Matchup Report styling and contrast - CLOSED 2026-03-10
  Applied dark theme polish pass with home/away color coding (blue/red),
  improved typography hierarchy, subordinated sample counts in brackets ([n]),
  and pill/badge styling for Match Audit status column. Accuracy Notice 
  banner de-emphasized. Gates F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-094 - Fix venue matchup panel and match audit layout regressions - CLOSED 2026-03-10
  Venue matchup stat rows now wrap long chase values and use tighter section spacing,
  removing the visible empty gap when chase placeholders render. Match Audit table
  now adds clear column dividers. Gates F1/F2/F3/5/6 PASS, bouncer PASS.

- TASK-093 - Fix venue matchup match audit status propagation - CLOSED 2026-03-10
  Enrichment now status-tags MATCH_IDS audit rows with the canonical smart-filter
  service before formatting, so excluded fortress matches keep their calculator
  status labels. Gates 1/2/5/6 PASS, bouncer PASS.

- TASK-092 - Diagnose venue matchup match audit status loss - CLOSED 2026-03-10
  Root cause confirmed: enrichment rebuilt fortress audit rows from raw `match_df`
  and defaulted missing status to Included. Confirmed 2018-10-23 carried
  STATUS_SHORT_SECOND_DROP with counts 4/3/1 before formatting.

- TASK-091 - Restore venue matchup score-extreme layer ownership - CLOSED 2026-03-10
  Venue matchup calculator now returns raw int score extremes again for
  high_1st, low_1st, and high_chased. Serializer now stringifies only those
  three fields, preserving frontend rendering. Gates 1/2/4/5/6 PASS, bouncer PASS.

- TASK-090 - Venue Matchup null High/Low and Highest Chased metrics - CLOSED 2026-03-10
  Structured venue matchup payload now normalizes scalar score extremes to
  string values in the backend payload contract. Sample query verified against
  raw calculator output. Gates 1/2/3/5/6 PASS, bouncer PASS.

- Project cleanup — COMPLETE 2026-03-10
  ~18.5MB removed: stale ETL backup, test outputs, orphaned scripts,
  dead audit docs, dev artifacts, renderers dead code.
  Bouncer PASS. Commit: 4bba4a6.

- Claude Code MCP setup — COMPLETE 2026-03-10
  6 MCPs installed: github, filesystem, sequential-thinking,
  context7, playwright, duckdb.
  All connected, zero warnings. .mcp.json at project root.
  DuckDB path: C:\Cricket_Project_Stable\formats\odi\data\odi.duckdb

- TASK-086 + TASK-087 — Undefined CSS token fixes — CLOSED 2026-03-10
  --format-selector-height added to globals.css.
  --warning → --tier-caution, --success → --tier-elite,
  --danger → --tier-danger in phase-analysis components.

- TASK-085 — Gate F1: check_undefined_css_tokens() — CLOSED 2026-03-10
  Found 4 real violations on first run. Gate F1 now 19 checks.

- TASK-081 + TASK-082 + TASK-083 — Gate F1 improvements — CLOSED 2026-03-09
  check_suspense_fallback_class(), check_usememo_primitive_wrap(),
  aria-busy extension in check_live_region_announcements().

- TASK-079 — Tokenize box-shadow values — CLOSED 2026-03-09
  --shadow-sidebar and --shadow-card-deep added to globals.css.

- TASK-080 — Fix FormatSelector icon color literal — CLOSED 2026-03-09

- TASK-073/074/075/076/078 — Frontend compliance fixes — CLOSED 2026-03-09
  SkeletonLoader, FunctionRenderer, page.tsx, CategoryScreen, border-radius tokens.

## Active Task
None.

## Queue (in order)
1. Antigravity MCP config — next session
2. TASK-084 — Gate F1: Add check_required_test_files()
   DEPENDS ON: ICE-002 (TASK-077) un-iced first
3. TASK-012 — Token optimisation (parked — monitor first, from 2026-03-03)

## Icebox
- ICE-001 — MCP Integration (broader) — revisit Phase 12 scoping
- ICE-002 — TASK-077 — Frontend test suite (Vitest + RTL)
  Parked: 2026-03-09. TASK-084 depends on this.
- ICE-003 — Pylance/Python MCP — revisit Phase 12

## Architect Decision Required
None outstanding.

## Pre-Task Dirty File Notice (standing)
The following files have pre-existing uncommitted changes unrelated to
any active task. Agents must NOT block on their presence in git status:
  frontend/lib/api.ts — @schema tag additions, pre-existing

## Gate State Snapshot (2026-03-11)
- GATE 1  (boundary-sentinel):           PASS
- GATE 2  (duckdb-lint-ops):             PASS - 0 violations
- GATE 3  (manifest-contract-verifier):  PASS
- GATE 4  (serialization-guard):         PASS
- GATE F1 (frontend-lint-sentinel):   PASS — 0 violations (19 checks)
- GATE F2 (frontend-paradigm-sentinel): PASS — 0 violations
- GATE F3 (frontend-type-sync-guard):  PASS — 0 violations
- GATE 5  (paradigm-sentinel):         PASS
- GATE 6  (compliance-bouncer):        PASS — 0 violations (22 files)
- Pre-commit hook:                     PASS — all gates active, exit 0

## Rule Inventory — frontend-lint-sentinel (Gate F1)
| Rule | Function | Added |
|---|---|---|
| 2.2A-R1 | check_raw_fetch | pre-sprint |
| 2.2A-R6 | check_any_unknown | TASK-066 |
| 2.2A-R13 | check_hardcoded_format_strings | pre-sprint |
| 2.2A-R14 | check_polling_execute | TASK-072 |
| 2.2B-R1 | check_raw_hex_colors | pre-sprint |
| 2.2B-R1 | check_undefined_css_tokens | TASK-085 |
| 2.2B-R4 | check_non_lucide_icons | pre-sprint |
| 2.2B-R5 | check_inline_font_family | TASK-068 |
| 2.2B-R6 | check_component_keyframes | pre-sprint |
| 2.2C-R1 | check_eager_renderer_imports | pre-sprint |
| 2.2C-R1 | check_suspense_fallback_class | TASK-081 |
| 2.2C-R2 | check_usememo_primitive_wrap | TASK-082 |
| 2.2C-R3 | check_inline_object_array_props | TASK-071 |
| 2.2D-R3 | check_schema_jsdoc | pre-sprint |
| 2.2E-R1 | check_aria_label_buttons | pre-sprint |
| 2.2E-R2 | check_onclick_non_interactive | TASK-070 |
| 2.2E-R3 | check_live_region_announcements | TASK-070 |
| 2.2E-R3 | check_loading_aria_live (extended) | TASK-083 |
| 2.2F-R1 | check_non_vitest_imports | pre-sprint |

## Rule Inventory — frontend-paradigm-sentinel (Gate F2)
| Rule | Function | Added |
|---|---|---|
| 2.2A-R3 | check_external_state | pre-sprint |
| 2.2A-R4 | check_file_size | pre-sprint |
| 2.2A-R5 | check_domain_arithmetic | pre-sprint |
| 2.2A-R6 | check_payload_extractor_in_renderer | TASK-105 |
| 2.2A-R7 | check_view_dispatch_in_renderer | TASK-130 |
| 2.2B-R7 | check_renderer_placement | pre-sprint |
| 2.2D-R2 | check_silent_catch_in_renderer | pre-sprint |
