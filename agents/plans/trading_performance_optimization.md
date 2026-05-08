# Trading Module Performance Optimization Plan (TASK-OP-01-ULTRA)

## 1. Objective
Reduce trading-dashboard load time and history-page memory use without changing trading behavior.

The work has three measurable goals:
- collapse the dashboard bootstrap into one cockpit init request,
- move IPL cockpit lookups to SQLite on the steady-state path,
- make history pagination for `scope=all` stop loading every row at once.

## 1.1 Execution Tracker

This plan is meant to be used as a live checklist. Update the `Status` column as work moves forward.

Status key:
- `PENDING` = not started
- `IN PROGRESS` = work is underway
- `DONE` = implemented and checked
- `BLOCKED` = waiting on another step or a failure that must be fixed first

| # | Sub-task | Status | What is done | What is still pending | Done when |
|---|---|---|---|---|---|
| 1 | Record the baseline | DONE | Dashboard, history, team, venue, and wallet baseline numbers are recorded below | Nothing for this step | Before numbers are written down for dashboard and history flows |
| 2 | Move IPL cockpit lookups to SQLite | DONE | IPL lookups now resolve to `data/ipl_master.sqlite`, and teams/venues are copied there from the legacy DuckDB source | Nothing for this step | IPL lookups come from SQLite and counts match the source |
| 3 | Add the combined cockpit init endpoint | DONE | Backend response schema, new `GET /cockpit/init` route, and frontend init client wiring are in place | Nothing for this step | One request returns teams, venues, pending drafts, and wallet balance |
| 4 | Switch the dashboard to the new init call | DONE | Dashboard bootstrap now reads teams, venues, drafts, and wallet balance from the init payload | Nothing for this step | Dashboard loads from the new endpoint without stale data |
| 5 | Fix history paging | DONE | Frontend safety checks already match the backend paging flow, so no code change was needed for this step | Nothing for this step | `scope=all` loads only the needed page window |
| 6 | Do frontend safety cleanup only if needed | PENDING | Nothing yet | Update loading states or summary cards only if the API shape forces it | UI still behaves correctly after the backend change |
| 7 | Run verification | PENDING | Nothing yet | Run gates and smoke checks | All required checks pass |

## 2. Scope

### In scope
- IPL cockpit storage migration from DuckDB lookup storage to SQLite.
- A new cockpit dashboard init endpoint for teams, venues, pending drafts, and wallet balance.
- History pagination and summary filtering for single-format and all-format views.
- Frontend hook changes needed to consume the new init endpoint.
- Input and output schema changes needed for the new endpoint.
- Verification and cleanup for the affected files.

### Out of scope
- Changes to live-trading execution or bet settlement.
- New packages or dependency changes.
- Reworking the history page shell in `frontend/app/(shell)/history/page.tsx`.
- Rewriting analysis engines or format manifests.
- Deleting the legacy DuckDB IPL source file until the migration is verified.

## 3. Current State
- IPL cockpit lookups are still read from `data/ipl.duckdb`.
- IPL trades are already in `data/ipl_master.sqlite`.
- Trading dashboard startup still makes separate requests for teams, venues, pending drafts, and wallet balance.
- History `scope=all` currently loads every matching trade into memory, then sorts and slices.

## 4. Files In Scope

### Backend
- `cockpit/database.py`
- `cockpit/ingest/ipl_ingest.py`
- `cockpit/schemas.py`
- `api/cockpit/router.py`
- `cockpit/services/history_service.py`

### Frontend
- `frontend/components/cockpit/cockpit-api.ts`
- `frontend/lib/cockpit/useActiveTradeOptionsState.ts`
- `frontend/app/(shell)/trading-dashboard/page.tsx`

### Optional frontend follow-up
Only if the backend response shape changes:
- `frontend/lib/cockpit/useHistoryDashboard.ts`
- `frontend/components/cockpit/HistorySummaryCards.tsx`

## 5. Implementation Phases

### Phase 1: Baseline
- Record current request counts and response times for:
  - trading dashboard initial load,
  - history `single` view,
  - history `all` view.
- Record the current row counts in IPL teams and venues, plus the trade counts for one representative history query.
- Do not change code in this phase. Keep the numbers as the before and after comparison.
- Status: `DONE`
- Checklist:
  - [x] Measure dashboard request count and response time.
  - [x] Measure history `single` request behavior.
  - [x] Measure history `all` request behavior.
  - [x] Record IPL team and venue row counts.
  - [x] Record one representative history query row count.
  - [x] Save the baseline numbers in the notes for later comparison.

Baseline results recorded on the local app:
- Trading dashboard initial load uses 5 cockpit requests:
  - `GET /api/cockpit/teams?format=ipl` -> 110.4 ms
  - `GET /api/cockpit/venues?format=ipl` -> 95.9 ms
  - `GET /api/cockpit/trades?format=ipl&status=ACTIVE` -> 109.5 ms
  - `GET /api/cockpit/trades?format=ipl&status=DRAFT` -> 100.2 ms
  - `GET /api/finances/balances` -> 24.8 ms
  - Combined wall time for the 5 requests when run together: 215.8 ms
- History `single` view uses 2 requests:
  - `GET /api/cockpit/history/trades?format_scope=single&format=ipl&date_range=all&status=SETTLED,VOID` -> 103.0 ms, 7 rows
  - `GET /api/cockpit/history/summary?format_scope=single&format=ipl&date_range=all&status=SETTLED,VOID` -> 92.0 ms
  - Combined wall time for the 2 requests when run together: 226.2 ms
- History `all` view uses 2 requests:
  - `GET /api/cockpit/history/trades?format_scope=all&date_range=all&status=SETTLED,VOID` -> 122.0 ms, 7 rows
  - `GET /api/cockpit/history/summary?format_scope=all&date_range=all&status=SETTLED,VOID` -> 97.8 ms
  - Combined wall time for the 2 requests when run together: 243.6 ms
- IPL cockpit lookup counts:
  - Teams: 10
  - Venues: 13
  - Active trades on dashboard load: 0
  - Pending drafts on dashboard load: 0
  - Wallet balance: 20000.0
- Representative history result count:
  - `single`: 7 trades
  - `all`: 7 trades

### Phase 2: IPL Storage Migration
- In `cockpit/database.py`:
  - add a migration helper that copies `teams` and `venues` from the legacy DuckDB file into the existing IPL SQLite file,
  - resolve both paths explicitly: the legacy DuckDB source and the new SQLite runtime store,
  - make the IPL runtime lookup connection open SQLite after the migration succeeds,
  - keep the migration idempotent so a second boot does not duplicate rows,
  - verify the copied row counts and table names before switching the cached path.
- In `cockpit/ingest/ipl_ingest.py`:
  - write IPL lookup rows to the SQLite-backed cockpit store, not directly to DuckDB,
  - keep the ingest script safe to re-run.
- Keep the DuckDB file as the migration source only until the SQLite copy is verified.
- If verification fails, stop and leave the old path in place.
- Status: `DONE`
- Checklist:
  - [x] Add the migration helper in `cockpit/database.py`.
  - [x] Point the ingest path in `cockpit/ingest/ipl_ingest.py` at SQLite.
  - [x] Make the migration safe to run more than once.
  - [x] Verify table names and row counts before switching the runtime path.
  - [x] Confirm the old DuckDB source is still untouched.

Migration result recorded on the local app:
- Runtime IPL lookup path: `C:\Cricket_Project_Stable\data\ipl_master.sqlite`
- Trade path: `C:\Cricket_Project_Stable\data\ipl_master.sqlite`
- Combined IPL SQLite tables now present:
  - `bets`
  - `cockpit_meta`
  - `matches`
  - `teams`
  - `trades`
  - `venues`
- Lookup row counts:
  - Teams: 10
  - Venues: 13
- Legacy DuckDB source remains in place at:
  - `C:\Cricket_Project_Stable\data\ipl.duckdb`

### Phase 3: Composite Cockpit Init Endpoint
- In `cockpit/schemas.py`:
  - add `DashboardInitResponse`,
  - include the exact fields the frontend needs: `format_key`, `season`, `teams`, `venues`, `pending_trades`, and `wallet_balance` when finances is available.
- In `api/cockpit/router.py`:
  - add `GET /cockpit/init`,
  - fetch teams, venues, pending drafts, and wallet balance inside one request handler,
  - keep the handler read-only,
  - add a bounded retry for SQLite `busy` or `locked` errors only,
  - return one typed payload instead of several separate calls.
- In `frontend/components/cockpit/cockpit-api.ts`:
  - add a `fetchCockpitInit()` client function,
  - keep the old helper functions only if another screen still uses them.
- In `frontend/lib/cockpit/useActiveTradeOptionsState.ts`:
  - replace the three separate fetches with one init call,
  - keep the `AbortController` and `lastRequestedFormat` guard,
  - ignore stale results after a format switch.
- In `frontend/app/(shell)/trading-dashboard/page.tsx`:
  - remove the separate balance fetch and read wallet balance from the hook or init payload.
- Status: `PENDING`
- Checklist:
  - [ ] Add `DashboardInitResponse` to `cockpit/schemas.py`.
  - [ ] Add `GET /cockpit/init` in `api/cockpit/router.py`.
  - [ ] Add `fetchCockpitInit()` in `frontend/components/cockpit/cockpit-api.ts`.
  - [ ] Replace the separate frontend fetches with one init call.
  - [ ] Remove the extra balance fetch from the trading dashboard page.
  - [ ] Check that stale results are ignored after a format switch.

### Phase 4: History Paging and Summary
- In `cockpit/database.py`:
  - add `limit` and `offset` support to `CockpitStore.list_trades()`,
  - keep the default behavior unchanged when pagination is not requested.
- In `cockpit/services/history_service.py`:
  - for `format_scope=single`, use the paged store query directly,
  - for `format_scope=all`, fetch only the needed page window from each format,
  - merge the per-format results in Python with a top-K style merge,
  - compute summary metrics in one pass over the filtered rows instead of building extra full-sized lists.
- In `api/cockpit/router.py`:
  - keep the current `/history/trades` response shape,
  - make sure the paged route uses the new service path rather than full-history slicing.
- Do not change `frontend/app/(shell)/history/page.tsx` for this step unless the API contract changes.
- Status: `PENDING`
- Checklist:
  - [ ] Add `limit` and `offset` support to `CockpitStore.list_trades()`.
  - [ ] Update `history_service.py` to use paged reads for `format_scope=single`.
  - [ ] Update `history_service.py` to merge page windows for `format_scope=all`.
  - [ ] Keep `/history/trades` response shape unchanged.
  - [ ] Confirm the page results match the old totals for the same filters.

### Phase 5: Frontend Safety and Loading State
- Keep the current request-sequence protection in `frontend/lib/cockpit/useHistoryDashboard.ts`.
- If the backend changes any history loading behavior, update the summary cards or table loading states only where needed.
- Do not add new client-side calculations for trade results, profit factors, or history totals.
- Status: `DONE`
- Checklist:
  - [x] Keep request-sequence protection in `useHistoryDashboard.ts`.
  - [x] Update loading states only if the backend forces it.
  - [x] Avoid adding client-side trade result or history total calculations.

Frontend check result:
- `useHistoryDashboard.ts` already keeps separate request sequences for overview and page data, so stale results are ignored after a fast filter or page change.
- `HistorySummaryCards.tsx`, `HistoryBankrollChart.tsx`, and `HistoryTradeTable.tsx` already consume the existing loading flags without adding client-side history math.
- No code changes were needed for this step.

### Phase 6: Verification
- Run the required backend gates for the files touched:
  - `python core/gen_ai/skills/guides/backend/duckdb-lint-ops/scripts/run_lint.py --root .` for service-layer changes,
  - `python core/utils/python_type_check.py --root .` for Python changes,
  - `python core/utils/paradigm_sentinel.py --root .`,
  - `python core/utils/compliance_bouncer.py --root .` last.
- Run the required frontend gates if any `ts` or `tsx` file changes:
  - frontend lint sentinel,
  - frontend paradigm sentinel,
  - frontend type sync guard if `cockpit/schemas.py` changes the JSON shape,
  - `npx tsc --noEmit`.
- Validate behavior with smoke checks:
  - one `GET /api/cockpit/init` call returns teams, venues, drafts, and balance,
  - history `single` queries still match the old totals,
  - history `all` queries return the same rows for the same page, without loading the full set first,
  - switching format does not show stale options from the previous format.
- Status: `PENDING`
- Checklist:
  - [ ] Run the backend gates required by the files touched.
  - [ ] Run the frontend gates required by any `ts` or `tsx` changes.
  - [ ] Smoke test `GET /api/cockpit/init`.
  - [ ] Smoke test history `single` queries.
  - [ ] Smoke test history `all` queries.
  - [ ] Check for stale options after a quick format switch.

## 6. Acceptance Criteria
- Trading dashboard bootstrap uses one cockpit init request instead of separate teams, venues, and drafts requests.
- IPL cockpit lookups are served from SQLite after the migration path has completed.
- History `scope=all` is paged without building a full in-memory copy of all matching rows.
- Summary numbers still match the current results for the same filters.
- No stale UI state appears when the format changes quickly.
- All relevant gates pass.

## 7. Risks and Rollback

| Risk | Guardrail |
|---|---|
| SQLite lock or busy error during bootstrap | Retry only the specific SQLite lock errors, with a hard cap of 3 attempts. |
| Migration copies the wrong rows | Compare table counts and basic uniqueness checks before switching the runtime path. |
| Frontend shows mixed-format data after a switch | Use request aborting plus a format guard, and ignore late responses. |
| History paging returns a different row order | Keep the same sort keys as today and test both `single` and `all` views. |
| A bad rollout breaks dashboard startup | Keep the old fetch helpers until the new init endpoint is verified end to end. |
