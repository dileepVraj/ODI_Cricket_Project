# cockpit/services/history_service.py
# History filtering and aggregation for cockpit trade history.

from __future__ import annotations

from calendar import monthrange
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Literal

from cockpit.database import CockpitStore, get_supported_cockpit_formats, init_db
from cockpit.manifest import (
    HISTORY_PROFIT_FACTOR_CAUTIOUS_THRESHOLD,
    HISTORY_PROFIT_FACTOR_ELITE_THRESHOLD,
)
from cockpit.models import Trade
from cockpit.services._constants import (
    DEFAULT_HISTORY_STATUSES as _DEFAULT_HISTORY_STATUSES,
    HistoryFormatScope,
    ORDER_DESC,
    RELATIVE_RANGE_PATTERN as _RELATIVE_RANGE_PATTERN,
    SCOPE_SINGLE,
    STATUS_SETTLED,
)

HistoryDateRange = str
HistoryProfitFactorTier = Literal["elite", "caution", "danger"]

_SUPPORTED_FORMATS: tuple[str, ...] = get_supported_cockpit_formats()
_FORMAT_LABELS: dict[str, str] = {
    "ipl": "IPL",
    "odi": "ODI",
}


@dataclass(frozen=True, slots=True)
class HistoryQuery:
    format_scope: HistoryFormatScope = SCOPE_SINGLE
    format_key: str | None = None
    season: int | None = None
    statuses: tuple[str, ...] = _DEFAULT_HISTORY_STATUSES
    date_range: HistoryDateRange = "all"
    date_from: date | None = None
    date_to: date | None = None
    limit: int = 10
    offset: int = 0


@dataclass(frozen=True, slots=True)
class HistoryTradeRow:
    trade: Trade
    format_key: str
    format_label: str


@dataclass(frozen=True, slots=True)
class HistoryTradesPage:
    trades: list[HistoryTradeRow]
    total_count: int


@dataclass(frozen=True, slots=True)
class HistorySummary:
    format_scope: HistoryFormatScope
    format_key: str | None
    format_keys: tuple[str, ...]
    trade_count: int
    settled_trade_count: int
    total_realized_pnl: float
    total_volume_wagered: float
    positive_trades: int
    negative_trades: int
    gross_profit: float
    gross_loss: float
    profit_factor: float | None
    profit_factor_tier: HistoryProfitFactorTier
    hit_rate: float | None
    avg_win: float | None
    avg_loss: float | None
    earliest_match_date: datetime | None
    latest_match_date: datetime | None


def get_supported_history_formats() -> tuple[str, ...]:
    return _SUPPORTED_FORMATS


def _format_label(format_key: str) -> str:
    return _FORMAT_LABELS.get(format_key, format_key.upper())


def resolve_history_formats(query: HistoryQuery) -> tuple[str, ...]:
    if query.format_scope == "all":
        return _SUPPORTED_FORMATS

    if query.format_key is None or not query.format_key.strip():
        raise ValueError("format is required when format_scope is single")

    format_key = query.format_key.strip().lower()
    if format_key not in _SUPPORTED_FORMATS:
        raise ValueError(
            f"Unknown history format: {format_key!r}. Available: {list(_SUPPORTED_FORMATS)}"
        )
    return (format_key,)


def _subtract_months(base_date: date, months: int) -> date:
    month_index = base_date.month - months - 1
    year = base_date.year + month_index // 12
    month = month_index % 12 + 1
    day = min(base_date.day, monthrange(year, month)[1])
    return date(year, month, day)


def _parse_relative_date_range(date_range: str) -> tuple[int, str] | None:
    match = _RELATIVE_RANGE_PATTERN.fullmatch(date_range.strip().lower())
    if match is None:
        return None

    count = int(match.group(1))
    if count <= 0:
        return None

    return count, match.group(2)


def resolve_history_date_bounds(
    query: HistoryQuery,
    *,
    now: datetime | None = None,
) -> tuple[date | None, date | None]:
    current = now or datetime.now(timezone.utc)
    today = current.date()

    range_key = query.date_range.strip().lower()

    if range_key == "all":
        if query.date_from is not None or query.date_to is not None:
            raise ValueError("date_from and date_to require date_range=custom")
        return None, None

    if range_key == "custom":
        if query.date_from is None or query.date_to is None:
            raise ValueError("Both date_from and date_to are required for custom ranges")
        if query.date_from > query.date_to:
            raise ValueError("date_from must be on or before date_to")
        return query.date_from, query.date_to

    if query.date_from is not None or query.date_to is not None:
        raise ValueError("date_from and date_to are only allowed with date_range=custom")

    relative_range = _parse_relative_date_range(range_key)
    if relative_range is not None:
        window_count, window_unit = relative_range
        if window_unit == "d":
            start = today - timedelta(days=window_count - 1)
            return start, today

        start = _subtract_months(today, window_count)
        return start, today

    if range_key == "7d":
        start = today - timedelta(days=7 - 1)
        return start, today

    if range_key == "15d":
        start = today - timedelta(days=15 - 1)
        return start, today

    if range_key == "30d":
        start = today - timedelta(days=30 - 1)
        return start, today

    if range_key == "3m":
        start = _subtract_months(today, 3)
        return start, today

    if range_key == "6m":
        start = _subtract_months(today, 6)
        return start, today

    if range_key == "12m":
        start = _subtract_months(today, 12)
        return start, today

    raise ValueError(f"Unsupported date range: {query.date_range!r}")


def _normalize_statuses(statuses: Sequence[str]) -> tuple[str, ...]:
    filtered = [status.strip().upper() for status in statuses if status and status.strip()]
    return tuple(filtered) if filtered else _DEFAULT_HISTORY_STATUSES


def _trade_in_date_window(trade: Trade, start: date | None, end: date | None) -> bool:
    if start is None and end is None:
        return True
    if trade.match_date is None:
        return False
    trade_date = trade.match_date.date()
    if start is not None and trade_date < start:
        return False
    if end is not None and trade_date > end:
        return False
    return True


def _history_sort_key(row: HistoryTradeRow) -> tuple[datetime, datetime, int]:
    primary = row.trade.match_date or row.trade.updated_at
    if primary.tzinfo is None:
        primary = primary.replace(tzinfo=timezone.utc)
    else:
        primary = primary.astimezone(timezone.utc)

    updated = row.trade.updated_at
    if updated.tzinfo is None:
        updated = updated.replace(tzinfo=timezone.utc)
    else:
        updated = updated.astimezone(timezone.utc)

    trade_id = row.trade.id or 0
    return primary, updated, trade_id


def _build_profit_factor_tier(
    profit_factor: float | None,
    gross_profit: float,
    gross_loss: float,
) -> HistoryProfitFactorTier:
    if gross_loss == 0 and gross_profit > 0:
        return "elite"
    if profit_factor is None:
        return "caution"
    if profit_factor > HISTORY_PROFIT_FACTOR_ELITE_THRESHOLD:
        return "elite"
    if profit_factor >= HISTORY_PROFIT_FACTOR_CAUTIOUS_THRESHOLD:
        return "caution"
    return "danger"


def _build_history_profit_metrics(
    settled_rows: Sequence[HistoryTradeRow],
) -> tuple[float, float, float | None, HistoryProfitFactorTier, float | None, float | None, float | None]:
    settled_count = len(settled_rows)
    positive_trades = [
        row
        for row in settled_rows
        if (row.trade.actual_profit or 0.0) > 0
    ]
    negative_trades = [
        row
        for row in settled_rows
        if (row.trade.actual_profit or 0.0) < 0
    ]
    gross_profit = round(
        sum(max(float(row.trade.actual_profit or 0.0), 0.0) for row in settled_rows),
        2,
    )
    gross_loss = round(
        sum(abs(min(float(row.trade.actual_profit or 0.0), 0.0)) for row in settled_rows),
        2,
    )

    if gross_loss > 0:
        profit_factor: float | None = round(gross_profit / gross_loss, 2)
    else:
        profit_factor = None

    hit_rate = round((len(positive_trades) / settled_count) * 100, 2) if settled_count > 0 else None
    avg_win = round(gross_profit / len(positive_trades), 2) if positive_trades else None
    avg_loss = round(gross_loss / len(negative_trades), 2) if negative_trades else None

    return (
        gross_profit,
        gross_loss,
        profit_factor,
        _build_profit_factor_tier(profit_factor, gross_profit, gross_loss),
        hit_rate,
        avg_win,
        avg_loss,
    )


def _load_trades_for_format(
    format_key: str,
    *,
    season: int | None,
    statuses: tuple[str, ...],
) -> list[Trade]:
    init_db(format_key)
    store = CockpitStore(format_key, read_only=True)
    try:
        return store.list_trades(
            season=season,
            statuses=statuses,
            order=ORDER_DESC,
        )
    finally:
        store.close()


def load_history_trade_rows(query: HistoryQuery) -> list[HistoryTradeRow]:
    statuses = _normalize_statuses(query.statuses)
    start_date, end_date = resolve_history_date_bounds(query)
    rows: list[HistoryTradeRow] = []

    for format_key in resolve_history_formats(query):
        trades = _load_trades_for_format(
            format_key,
            season=query.season,
            statuses=statuses,
        )
        for trade in trades:
            if not _trade_in_date_window(trade, start_date, end_date):
                continue
            rows.append(
                HistoryTradeRow(
                    trade=trade,
                    format_key=format_key,
                    format_label=_format_label(format_key),
                )
            )

    rows.sort(key=_history_sort_key, reverse=True)
    return rows


def list_history_trades(query: HistoryQuery) -> HistoryTradesPage:
    rows = load_history_trade_rows(query)
    return HistoryTradesPage(
        trades=rows[query.offset:query.offset + query.limit],
        total_count=len(rows),
    )


def build_history_summary(query: HistoryQuery, rows: Sequence[HistoryTradeRow]) -> HistorySummary:
    format_keys = resolve_history_formats(query)
    settled_rows = [row for row in rows if row.trade.status == STATUS_SETTLED]
    gross_profit, gross_loss, profit_factor, profit_factor_tier, hit_rate, avg_win, avg_loss = _build_history_profit_metrics(settled_rows)
    total_realized_pnl = round(
        sum(float(row.trade.actual_profit or 0.0) for row in settled_rows),
        2,
    )
    total_volume_wagered = round(
        sum(float(row.trade.total_volume_wagered or 0.0) for row in settled_rows),
        2,
    )
    match_dates = [
        row.trade.match_date
        for row in rows
        if row.trade.match_date is not None
    ]

    return HistorySummary(
        format_scope=query.format_scope,
        format_key=(
            query.format_key.strip().lower()
            if query.format_scope == SCOPE_SINGLE and query.format_key
            else None
        ),
        format_keys=format_keys,
        trade_count=len(rows),
        settled_trade_count=len(settled_rows),
        total_realized_pnl=total_realized_pnl,
        total_volume_wagered=total_volume_wagered,
        positive_trades=sum(1 for row in settled_rows if (row.trade.actual_profit or 0.0) > 0),
        negative_trades=sum(1 for row in settled_rows if (row.trade.actual_profit or 0.0) < 0),
        gross_profit=gross_profit,
        gross_loss=gross_loss,
        profit_factor=profit_factor,
        profit_factor_tier=profit_factor_tier,
        hit_rate=hit_rate,
        avg_win=avg_win,
        avg_loss=avg_loss,
        earliest_match_date=min(match_dates) if match_dates else None,
        latest_match_date=max(match_dates) if match_dates else None,
    )
