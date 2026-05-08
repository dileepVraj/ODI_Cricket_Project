# PAGINATION_IMPLEMENTATION_PLAN.md

**Objective:** Add offset-based pagination to the Cockpit trade history table so the page stays fast as the trade ledger grows.

**Scope:** History trades only. Summary cards must stay unpaged and continue to reflect the full filtered result set.

**Page size:** Fixed at 10 records per page for this release.

---

## 1. BACKEND CHANGES

### A. Service Layer
**File:** `cockpit/services/history_service.py`
- Add `limit: int = 10` and `offset: int = 0` to `HistoryQuery`.
- Change `list_history_trades()` so it:
  - builds the full filtered list exactly as today
  - sorts that full list exactly as today
  - computes `total_count` before slicing
  - returns only the requested slice using `rows[offset:offset + limit]`
- Add a small result wrapper for the paged response, for example `HistoryTradesPage` with:
  - `trades: list[HistoryTradeRow]`
  - `total_count: int`
- Keep `build_history_summary()` based on the full unpaged rows list so all summary numbers stay correct.

### B. API Router
**File:** `api/cockpit/router.py`
- Update `GET /history/trades` to accept:
  - `page: int = Query(1, ge=1)`
  - `page_size: int = Query(10, ge=1)`
- Compute `offset = (page - 1) * page_size`.
- Return a paged payload instead of a bare list:
  - `trades`
  - `total_count`
  - `page`
  - `page_size`
- Keep `GET /history/summary` unchanged apart from continuing to call the service with the full row set.

### C. API Schema
**File:** `cockpit/schemas.py`
- Add a paged history response model, for example `HistoryTradesPageResponse`.
- Fields:
  - `trades: list[HistoryTradeResponse]`
  - `total_count: int`
  - `page: int`
  - `page_size: int`
- Do not change `HistoryTradeResponse` or `HistorySummaryResponse` unless the router needs a new wrapper type.

---

## 2. FRONTEND CHANGES

### A. History API Client
**File:** `frontend/lib/cockpit/history-api.ts`
- Update `HistoryTradeFilters` to include:
  - `page?: number`
  - `pageSize?: number`
- Update `buildHistoryQueryString()` to include `page` and `page_size` when present.
- Change `getHistoryTrades()` to return the new paged response type instead of a plain array.
- Leave `getHistorySummary()` unchanged so it still requests the full filtered history.

### B. Dashboard State
**File:** `frontend/lib/cockpit/useHistoryDashboard.ts`
- Add `currentPage` state and initialize it to `1`.
- Add a constant `pageSize = 10` in the hook so the value is shared in one place.
- Fetch history trades with `page` and `pageSize`.
- Keep fetching the summary with the same filters, but without pagination.
- Reset `currentPage` to `1` whenever the user changes filters or clears them.
- If the backend reports fewer rows than the current page can show, clamp to the last valid page and refetch.
- Return `currentPage`, `pageSize`, `totalTrades`, and `onPageChange` to the dashboard UI.

### C. Dashboard Component
**File:** `frontend/components/cockpit/HistoryDashboard.tsx`
- Pass the new pagination props into `HistoryTradeTable`.
- Keep pagination state in the dashboard hook, not inside the table.
- Leave the summary cards and chart driven by the full filtered dataset, not the current page.

### D. Table UI
**File:** `frontend/components/cockpit/HistoryTradeTable.tsx`
- Add props for:
  - `currentPage`
  - `pageSize`
  - `totalTrades`
  - `onPageChange`
- Replace the static footer text with:
  - `Showing X-Y of Z trades`
  - `No settled trades yet` when there are no rows
- Add `Previous` and `Next` controls using the existing Lucide icon set already used in this file.
- Disable `Previous` on page 1.
- Disable `Next` on the last page and while the table is loading.
- Keep row expansion, delete actions, and table layout unchanged.

---

## 3. BEHAVIOR RULES

- Changing any history filter must send the user back to page 1.
- Deleting a trade that makes the current page empty must not leave the UI stranded on an invalid page.
- The summary cards and chart must continue to reflect all matching trades, not just the visible page.
- The table order must stay newest first.

---

## 4. VERIFICATION

- Confirm page 1 shows rows 1-10 and the correct total count.
- Confirm page 2 shows the next set of rows and updates the footer text.
- Confirm the last page works when it has fewer than 10 rows.
- Confirm changing filters resets the page to 1.
- Confirm summary values do not change when pagination changes.

### Gates
- `GATE4` if the API response model or serializer output changes.
- `GATE5T` for every `.py` file changed.
- `GATE5P` always.
- `GATE6` always, run last.
- `GATEF1` for `.ts` / `.tsx` changes.
- `SRP-CHECK` if `frontend/components/` `.tsx` files change.
- `GATEF2` for `.ts` / `.tsx` changes.
- `GATEF3` for any `frontend/` file changes.

---

**Status:** Pending execution
