# api/cockpit/router.py
# FastAPI router for the Cockpit trading module.
# Thin HTTP layer -- all business logic lives in cockpit/.
# Live trade routes now focus on bet entry and bet management.

from __future__ import annotations

from collections.abc import Generator
from dataclasses import asdict
from datetime import date as _date
from datetime import datetime as _datetime
from datetime import timezone
from typing import List, Literal, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from cockpit.calculator import (
    bet_liability,
    calculate_trade_book_state,
    BetRecord,
    odds_decimal_from_paise,
    TradeBookState,
)
from cockpit.database import BetRow, CockpitStore, init_db
from cockpit.models import Trade
from cockpit.schemas import (
    AddBetRequest,
    BetResponse,
    CreateTradeRequest,
    HistorySummaryResponse,
    HistoryTradeResponse,
    SettleTradeRequest,
    TradeRestoreRequest,
    TradeResponse,
    TradeStateResponse,
    VenuesResponse,
)
from cockpit.services.history_service import (
    HistoryDateRange,
    HistoryQuery,
    HistoryTradeRow,
    build_history_summary,
    list_history_trades as load_history_trades,
)
from cockpit.services import teams_service, venues_service

cockpit_router = APIRouter()


def _set_no_cache_headers(response: Response) -> None:
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"


def _open_store(format_key: str, *, read_only: bool) -> CockpitStore:
    try:
        init_db(format_key)
        return CockpitStore(format_key, read_only=read_only)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _get_read_db(format: str = Query(default="ipl")) -> Generator[CockpitStore, None, None]:
    """FastAPI dependency -- opens a read-only CockpitStore for query routes."""
    store = _open_store(format, read_only=True)
    try:
        yield store
    finally:
        store.close()


def _get_write_db(format: str = Query(default="ipl")) -> Generator[CockpitStore, None, None]:
    """FastAPI dependency -- opens a writable CockpitStore for mutation routes."""
    store = _open_store(format, read_only=False)
    try:
        yield store
    finally:
        store.close()


def _trade_to_response(trade: Trade) -> TradeResponse:
    """Convert a Trade object to a TradeResponse."""
    payload = asdict(trade)
    payload.pop("match_id", None)
    return TradeResponse(**payload)


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _has_pre_toss_data(body: CreateTradeRequest) -> bool:
    return (
        _normalize_optional_text(body.selected_team_before_toss) is not None
        and body.back_odds_before_toss is not None
        and body.lay_odds_before_toss is not None
    )


def _has_post_toss_data(body: CreateTradeRequest) -> bool:
    return (
        _normalize_optional_text(body.toss_winner) is not None
        and body.toss_decision in {"bat", "field"}
        and _normalize_optional_text(body.selected_team_after_toss) is not None
        and body.back_odds_after_toss is not None
        and body.lay_odds_after_toss is not None
    )


def _is_active_trade(body: CreateTradeRequest) -> bool:
    return _has_pre_toss_data(body) and _has_post_toss_data(body)


def _paisa_to_decimal(odds: int | None) -> float | None:
    if odds is None:
        return None
    return round(odds_decimal_from_paise(odds), 2)


def _apply_trade_request(trade: Trade, body: CreateTradeRequest) -> None:
    opening_odds = body.opening_odds
    if opening_odds is None:
        opening_odds = _paisa_to_decimal(body.back_odds_before_toss)
    trade.season = body.season
    trade.match_date = body.match_date
    trade.team_1 = body.team_1
    trade.team_2 = body.team_2
    trade.favourite_team = body.favourite_team
    trade.home_ground = body.home_ground
    trade.stadium = body.stadium
    trade.toss_winner = _normalize_optional_text(body.toss_winner)
    trade.toss_decision = _normalize_optional_text(body.toss_decision)
    trade.bankroll = body.bankroll
    trade.opening_odds = opening_odds
    trade.selected_team_before_toss = _normalize_optional_text(body.selected_team_before_toss)
    trade.back_odds_before_toss = body.back_odds_before_toss
    trade.lay_odds_before_toss = body.lay_odds_before_toss
    trade.selected_team_after_toss = _normalize_optional_text(body.selected_team_after_toss)
    trade.back_odds_after_toss = body.back_odds_after_toss
    trade.lay_odds_after_toss = body.lay_odds_after_toss


def _save_trade(body: CreateTradeRequest, db: CockpitStore, trade: Trade | None = None) -> TradeResponse:
    now = _datetime.now(timezone.utc)
    current_status = trade.status if trade is not None else None
    if trade is None:
        trade = Trade(created_at=now, updated_at=now)
    _apply_trade_request(trade, body)
    if current_status == "ACTIVE" or _is_active_trade(body):
        trade.status = "ACTIVE"
    else:
        trade.status = "DRAFT"
    trade.updated_at = now
    if trade.id is None:
        trade = db.insert_trade(trade)
    else:
        trade = db.update_trade(trade)
    return _trade_to_response(trade)


def _get_trade_or_404(trade_id: int, db: CockpitStore) -> Trade:
    """Fetch a trade by ID or raise HTTP 404."""
    trade = db.get_trade(trade_id)
    if trade is None:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
    return trade


def _ensure_trade_not_settled(trade: Trade) -> None:
    if trade.status == "SETTLED":
        raise HTTPException(status_code=400, detail="Trade is settled and cannot be modified")


def _ensure_trade_is_updatable(trade: Trade) -> None:
    if trade.status not in {"DRAFT", "ACTIVE"}:
        raise HTTPException(status_code=400, detail="Trade must be DRAFT or ACTIVE to update")


def _ensure_trade_is_active(trade: Trade) -> None:
    if trade.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Trade must be ACTIVE to settle")


def _parse_status_filters(status: str | None) -> list[str] | None:
    if status is None:
        return None

    values = [value.strip().upper() for value in status.split(",")]
    filtered = [value for value in values if value]
    return filtered or None


def _history_status_filters(status: str | None) -> tuple[str, ...]:
    parsed = _parse_status_filters(status)
    if parsed is None:
        return ("SETTLED", "VOID")
    return tuple(parsed)


def _build_history_query(
    *,
    format_scope: Literal["single", "all"],
    format_key: str | None,
    season: int | None,
    status: str | None,
    date_range: HistoryDateRange,
    date_from: _date | None,
    date_to: _date | None,
) -> HistoryQuery:
    return HistoryQuery(
        format_scope=format_scope,
        format_key=format_key,
        season=season,
        statuses=_history_status_filters(status),
        date_range=date_range,
        date_from=date_from,
        date_to=date_to,
    )


def _history_trade_to_response(row: HistoryTradeRow) -> HistoryTradeResponse:
    payload = asdict(row.trade)
    payload.pop("match_id", None)
    payload["format_key"] = row.format_key
    payload["format_label"] = row.format_label
    return HistoryTradeResponse(**payload)


def _validate_bet_request(body: AddBetRequest) -> None:
    if body.bet_type not in {"BACK", "LAY"}:
        raise HTTPException(status_code=422, detail="bet_type must be BACK or LAY")
    if body.odds_paise <= 0:
        raise HTTPException(status_code=422, detail="odds_paise must be greater than 0")
    if body.stake <= 0:
        raise HTTPException(status_code=422, detail="stake must be greater than 0")


def _bet_to_response(bet: BetRow) -> BetResponse:
    return BetResponse(
        id=int(bet["id"]),
        trade_id=int(bet["trade_id"]),
        team=str(bet["team"]),
        bet_type=str(bet["bet_type"]),
        odds_paise=int(bet["odds_paise"]),
        odds_decimal=float(bet["odds_decimal"]),
        stake=float(bet["stake"]),
        liability=float(bet["liability"]),
        is_open=bool(bet["is_open"]),
        created_at=str(bet["created_at"]),
    )


def _bet_to_record(bet: BetRow) -> BetRecord:
    return {
        "team": str(bet["team"]),
        "bet_type": cast(Literal["BACK", "LAY"], str(bet["bet_type"])),
        "odds_decimal": float(bet["odds_decimal"]),
        "stake": float(bet["stake"]),
        "is_open": bool(bet["is_open"]),
    }


def _trade_bets_for_trade(trade: Trade, db: CockpitStore) -> list[BetRow]:
    if trade.id is None:
        raise HTTPException(status_code=500, detail="Trade id missing from database row")

    return db.list_bets(trade.id)


def _trade_book_state(trade: Trade, db: CockpitStore) -> TradeBookState:
    bets = [_bet_to_record(bet) for bet in _trade_bets_for_trade(trade, db)]
    return calculate_trade_book_state(
        team_1=trade.team_1,
        team_2=trade.team_2,
        bankroll=trade.bankroll,
        bets=bets,
    )


def _trade_total_volume_wagered(trade_id: int, db: CockpitStore) -> float:
    trade = _get_trade_or_404(trade_id, db)
    bets = _trade_bets_for_trade(trade, db)
    return round(sum(float(bet["liability"]) for bet in bets), 2)


def _apply_settlement_to_trade(trade: Trade, body: SettleTradeRequest, db: CockpitStore) -> None:
    if trade.id is None:
        raise HTTPException(status_code=500, detail="Trade id missing from database row")

    state = _trade_book_state(trade, db)
    realized_pnl = 0.0
    if body.winner == "team_1":
        realized_pnl = state["net_pnl_team_1"]
    elif body.winner == "team_2":
        realized_pnl = state["net_pnl_team_2"]

    trade.winner = body.winner
    trade.actual_profit = round(realized_pnl, 2)
    trade.trade_sentiment = body.sentiment
    trade.fav_sub_30_loss = body.fav_sub_30_loss
    trade.missed_swing_team = _normalize_optional_text(body.missed_swing_team)
    trade.missed_swing_back_odds = body.missed_swing_back_odds
    trade.missed_swing_lay_odds = body.missed_swing_lay_odds
    trade.missed_swing_bet_index = body.missed_swing_bet_index
    trade.missed_swing_cumulative_stake = (
        round(body.missed_swing_cumulative_stake, 2)
        if body.missed_swing_cumulative_stake is not None
        else None
    )
    trade.missed_swing_net_pnl = (
        round(body.missed_swing_net_pnl, 2)
        if body.missed_swing_net_pnl is not None
        else None
    )
    trade.targeted_pnl = round(body.targeted_pnl, 2)
    trade.achieved_yield_percentage = round(body.achieved_yield, 2)
    trade.trade_mistakes = (
        body.trade_mistakes.model_dump_json()
        if body.trade_mistakes is not None
        else None
    )
    trade.total_volume_wagered = _trade_total_volume_wagered(trade.id, db)
    trade.total_stake = trade.total_volume_wagered
    trade.status = "SETTLED"
    trade.updated_at = _datetime.now(timezone.utc)


def _trade_from_restore_request(body: TradeRestoreRequest) -> Trade:
    trade = Trade(**body.trade.model_dump(exclude={"id"}))
    if trade.status == "SETTLED":
        missing_fields = [
            field_name
            for field_name, value in (
                ("winner", trade.winner),
                ("actual_profit", trade.actual_profit),
                ("trade_sentiment", trade.trade_sentiment),
                ("targeted_pnl", trade.targeted_pnl),
                ("achieved_yield_percentage", trade.achieved_yield_percentage),
            )
            if value is None
        ]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Restored settled trade is missing settlement fields: "
                    + ", ".join(missing_fields)
                ),
            )
    return trade


@cockpit_router.get("/teams")
def list_teams(
    season: int = Query(default=2025),
    db: CockpitStore = Depends(_get_read_db),
) -> dict[str, object]:
    """Return team options for the cockpit match setup form."""
    return {
        "season": season,
        "teams": teams_service.get_teams(db),
    }


@cockpit_router.get("/venues", response_model=VenuesResponse)
def list_venues(
    season: int = Query(default=2025),
    db: CockpitStore = Depends(_get_read_db),
) -> VenuesResponse:
    """Return venue options for the cockpit match setup form."""
    return VenuesResponse(
        season=season,
        venues=venues_service.get_venues(db),
    )


@cockpit_router.post("/trades", response_model=TradeResponse, status_code=201)
async def create_trade(
    body: CreateTradeRequest,
    request: Request,
    db: CockpitStore = Depends(_get_write_db),
) -> TradeResponse:
    """Create a new draft or active trade depending on how much of the form is filled."""
    finances = getattr(request.app.state, "finances", None)
    if finances is not None:
        requested_bankroll = body.bankroll if body.bankroll is not None else 100.0
        wallet_balance = finances.get_balances()["wallet"]
        if requested_bankroll > wallet_balance:
            raise HTTPException(status_code=400, detail="Insufficient Wallet Funds.")
    response = _save_trade(body, db)
    if finances is not None and response.status == "ACTIVE":
        stake_amount = body.bankroll if body.bankroll is not None else 100.0
        finances.record_trade_stake(stake_amount, response.id)
    return response


@cockpit_router.patch("/trades/{trade_id}", response_model=TradeResponse)
def update_trade(
    trade_id: int,
    body: CreateTradeRequest,
    db: CockpitStore = Depends(_get_write_db),
) -> TradeResponse:
    """Update an existing draft or active trade."""
    trade = _get_trade_or_404(trade_id, db)
    _ensure_trade_is_updatable(trade)
    return _save_trade(body, db, trade)


@cockpit_router.get("/trades", response_model=List[TradeResponse])
def list_trades(
    response: Response,
    season: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: CockpitStore = Depends(_get_read_db),
) -> List[TradeResponse]:
    """Return all trades, newest first. Optionally filter by season or status."""
    _set_no_cache_headers(response)
    trades = db.list_trades(
        season=season,
        statuses=_parse_status_filters(status),
        order="DESC",
    )
    return [_trade_to_response(trade) for trade in trades]


@cockpit_router.get("/history/trades", response_model=List[HistoryTradeResponse])
def list_history_trades(
    response: Response,
    format_scope: Literal["single", "all"] = Query(default="single"),
    format_key: Optional[str] = Query(default=None, alias="format"),
    season: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default="SETTLED,VOID"),
    date_range: HistoryDateRange = Query(default="all"),
    date_from: _date | None = Query(default=None),
    date_to: _date | None = Query(default=None),
) -> List[HistoryTradeResponse]:
    """Return history trades filtered by format scope, season, and match date."""
    _set_no_cache_headers(response)
    query = _build_history_query(
        format_scope=format_scope,
        format_key=format_key,
        season=season,
        status=status,
        date_range=date_range,
        date_from=date_from,
        date_to=date_to,
    )
    try:
        rows = load_history_trades(query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return [_history_trade_to_response(row) for row in rows]


@cockpit_router.get("/history/summary", response_model=HistorySummaryResponse)
def get_history_summary(
    response: Response,
    format_scope: Literal["single", "all"] = Query(default="single"),
    format_key: Optional[str] = Query(default=None, alias="format"),
    season: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default="SETTLED,VOID"),
    date_range: HistoryDateRange = Query(default="all"),
    date_from: _date | None = Query(default=None),
    date_to: _date | None = Query(default=None),
) -> HistorySummaryResponse:
    """Return a filtered summary for the history screen."""
    _set_no_cache_headers(response)
    query = _build_history_query(
        format_scope=format_scope,
        format_key=format_key,
        season=season,
        status=status,
        date_range=date_range,
        date_from=date_from,
        date_to=date_to,
    )
    try:
        rows = load_history_trades(query)
        summary = build_history_summary(query, rows)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return HistorySummaryResponse(**asdict(summary))


@cockpit_router.get("/trades/{trade_id}", response_model=TradeResponse)
def get_trade(trade_id: int, db: CockpitStore = Depends(_get_read_db)) -> TradeResponse:
    """Return a single trade by ID."""
    trade = _get_trade_or_404(trade_id, db)
    return _trade_to_response(trade)


@cockpit_router.get("/trades/{trade_id}/state", response_model=TradeStateResponse)
def get_trade_state(trade_id: int, db: CockpitStore = Depends(_get_read_db)) -> TradeStateResponse:
    """Return the trade and its current book state."""
    trade = _get_trade_or_404(trade_id, db)
    state = _trade_book_state(trade, db)
    payload = asdict(trade)
    payload.pop("match_id", None)
    payload.update(state)
    return TradeStateResponse(**payload)


@cockpit_router.post("/trades/{trade_id}/settle", response_model=TradeResponse)
def settle_trade(
    trade_id: int,
    body: SettleTradeRequest,
    request: Request,
    db: CockpitStore = Depends(_get_write_db),
) -> TradeResponse:
    """Lock a live trade after the result is known and store journaling metrics."""
    trade = _get_trade_or_404(trade_id, db)
    _ensure_trade_is_active(trade)
    _apply_settlement_to_trade(trade, body, db)

    trade = db.update_trade(trade)
    finances = getattr(request.app.state, "finances", None)
    if finances is not None and trade.actual_profit is not None:
        finances.credit_trade_payout(trade.actual_profit, trade_id)
    return _trade_to_response(trade)


@cockpit_router.patch("/trades/{trade_id}/settlement", response_model=TradeResponse)
def re_settle_trade(
    trade_id: int,
    body: SettleTradeRequest,
    db: CockpitStore = Depends(_get_write_db),
) -> TradeResponse:
    """Correct settlement data on an already-settled trade. Does not re-credit finances."""
    trade = _get_trade_or_404(trade_id, db)
    if trade.status != "SETTLED":
        raise HTTPException(status_code=400, detail="Trade must be SETTLED to edit settlement")
    _apply_settlement_to_trade(trade, body, db)
    trade.updated_at = _datetime.now(timezone.utc)

    trade = db.update_trade(trade)
    return _trade_to_response(trade)


@cockpit_router.post("/trades/restore", response_model=TradeResponse)
def restore_trade(
    body: TradeRestoreRequest,
    db: CockpitStore = Depends(_get_write_db),
) -> TradeResponse:
    """Restore a deleted trade snapshot without replaying wallet credits."""
    trade = _trade_from_restore_request(body)
    restored_trade = db.insert_trade(trade)
    if restored_trade.id is None:
        raise HTTPException(status_code=500, detail="Trade id missing from database row")

    try:
        for bet in body.bets:
            db.insert_bet(
                trade_id=restored_trade.id,
                team=bet.team,
                bet_type=bet.bet_type,
                odds_paise=bet.odds_paise,
                odds_decimal=bet.odds_decimal,
                stake=bet.stake,
                liability=bet.liability,
                is_open=bet.is_open,
                created_at=bet.created_at,
            )
    except Exception:
        try:
            db.delete_trade(restored_trade.id)
        except Exception:
            pass
        raise

    restored_trade = db.get_trade(restored_trade.id) or restored_trade
    return _trade_to_response(restored_trade)


@cockpit_router.post("/trades/{trade_id}/void", response_model=TradeResponse)
def void_trade(
    trade_id: int,
    db: CockpitStore = Depends(_get_write_db),
) -> TradeResponse:
    """Void a live trade while keeping the bet audit trail."""
    trade = _get_trade_or_404(trade_id, db)
    _ensure_trade_is_active(trade)

    trade.status = "VOID"
    trade.winner = None
    trade.result = None
    trade.actual_profit = 0.0
    trade.trade_sentiment = None
    trade.targeted_pnl = 0.0
    trade.achieved_yield_percentage = 0.0
    trade.total_volume_wagered = 0.0
    trade.total_stake = 0.0
    trade.updated_at = _datetime.now(timezone.utc)

    trade = db.update_trade(trade)
    return _trade_to_response(trade)


@cockpit_router.post("/trades/{trade_id}/bets", response_model=BetResponse, status_code=201)
def add_bet(
    trade_id: int,
    body: AddBetRequest,
    db: CockpitStore = Depends(_get_write_db),
) -> BetResponse:
    """Add a bet to an existing trade."""
    _validate_bet_request(body)
    trade = _get_trade_or_404(trade_id, db)
    _ensure_trade_not_settled(trade)
    if body.team not in {trade.team_1, trade.team_2}:
        raise HTTPException(
            status_code=400,
            detail="Team must match one of the trade teams",
        )
    odds_decimal = odds_decimal_from_paise(body.odds_paise)
    liability = bet_liability(body.stake, odds_decimal, body.bet_type)
    if body.purpose != "CASHOUT":
        current_bets: list[BetRecord] = [_bet_to_record(bet) for bet in db.list_bets(trade.id or trade_id)]
        projected_bets = [
            *current_bets,
            cast(BetRecord, {
                "team": body.team,
                "bet_type": body.bet_type,
                "odds_decimal": odds_decimal,
                "stake": body.stake,
                "is_open": True,
            }),
        ]
        projected_state = calculate_trade_book_state(
            team_1=trade.team_1,
            team_2=trade.team_2,
            bankroll=trade.bankroll,
            bets=projected_bets,
        )
        if projected_state["available_bankroll"] < 0:
            raise HTTPException(status_code=400, detail="Insufficient bankroll")
    bet = db.insert_bet(
        trade_id=trade_id,
        team=body.team,
        bet_type=body.bet_type,
        odds_paise=body.odds_paise,
        odds_decimal=odds_decimal,
        stake=body.stake,
        liability=liability,
        is_open=True,
        created_at=_datetime.now(timezone.utc).isoformat(),
    )
    return _bet_to_response(bet)


@cockpit_router.get("/trades/{trade_id}/bets", response_model=List[BetResponse])
def list_bets(
    trade_id: int,
    response: Response,
    view: Literal["live", "history"] = Query(default="live"),
    db: CockpitStore = Depends(_get_read_db),
) -> List[BetResponse]:
    """Return all bets for a trade, oldest first."""
    _set_no_cache_headers(response)
    trade = _get_trade_or_404(trade_id, db)
    bets = _trade_bets_for_trade(trade, db)
    return [_bet_to_response(bet) for bet in bets]


@cockpit_router.patch("/trades/{trade_id}/bets/{bet_id}/close", response_model=BetResponse)
def close_bet(
    trade_id: int,
    bet_id: int,
    db: CockpitStore = Depends(_get_write_db),
) -> BetResponse:
    """Mark a bet closed and return the updated row."""
    trade = _get_trade_or_404(trade_id, db)
    _ensure_trade_not_settled(trade)
    bet = db.close_bet(trade_id, bet_id)
    if bet is None:
        raise HTTPException(
            status_code=404,
            detail=f"Bet {bet_id} not found for trade {trade_id}",
        )
    return _bet_to_response(bet)


@cockpit_router.delete("/trades/{trade_id}/bets/{bet_id}")
def delete_bet(
    trade_id: int,
    bet_id: int,
    db: CockpitStore = Depends(_get_write_db),
) -> dict[str, bool]:
    """Delete one bet from an active trade."""
    trade = _get_trade_or_404(trade_id, db)
    _ensure_trade_not_settled(trade)
    if not db.delete_bet(trade_id, bet_id):
        raise HTTPException(
            status_code=404,
            detail=f"Bet {bet_id} not found for trade {trade_id}",
        )
    return {"deleted": True}


@cockpit_router.delete("/trades/{trade_id}")
def delete_trade(trade_id: int, db: CockpitStore = Depends(_get_write_db)) -> dict[str, bool]:
    """Hard-delete a trade, its bets, and any orphaned match row."""
    _get_trade_or_404(trade_id, db)
    db.delete_trade(trade_id)
    return {"deleted": True}
