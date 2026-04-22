# api/cockpit/router.py
# FastAPI router for the Cockpit trading module.
# Thin HTTP layer -- all business logic lives in cockpit/.

from __future__ import annotations

from collections.abc import Generator
from dataclasses import asdict
from datetime import timezone
from datetime import datetime as _datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from cockpit.calculator import compute_trade_fields
from cockpit.database import CockpitStore
from cockpit.models import Trade
from cockpit.schemas import (
    AddBulletRequest,
    CloseTradeRequest,
    CreateTradeRequest,
    UpdateOdds1OverRequest,
    TradeResponse,
    TradeSummaryResponse,
    VenuesResponse,
)
from cockpit.services import teams_service, venues_service

cockpit_router = APIRouter()


def _get_read_db(format: str = Query(default="ipl")) -> Generator[CockpitStore, None, None]:
    """FastAPI dependency -- opens a read-only CockpitStore for query routes."""
    store = CockpitStore(format, read_only=True)
    try:
        yield store
    finally:
        store.close()


def _get_write_db(format: str = Query(default="ipl")) -> Generator[CockpitStore, None, None]:
    """FastAPI dependency -- opens a writable CockpitStore for mutation routes."""
    store = CockpitStore(format, read_only=False)
    try:
        yield store
    finally:
        store.close()


def _apply_computed(trade: Trade) -> None:
    """Call the calculator and write all computed values onto the trade object."""
    computed = compute_trade_fields(
        bankroll=trade.bankroll,
        opening_odds=trade.opening_odds,
        bullet_05_odds=trade.bullet_05_odds,
        bullet_05_stake=trade.bullet_05_stake,
        bullet_1_odds=trade.bullet_1_odds,
        bullet_1_stake=trade.bullet_1_stake,
        bullet_2_odds=trade.bullet_2_odds,
        bullet_2_stake=trade.bullet_2_stake,
        bullet_3_odds=trade.bullet_3_odds,
        bullet_3_stake=trade.bullet_3_stake,
        exit_odds=trade.exit_odds,
    )
    for key, value in computed.items():
        setattr(trade, key, value)


def _trade_to_response(trade: Trade) -> TradeResponse:
    """Convert a Trade object to a TradeResponse, including alert flags."""
    data = asdict(trade)
    data["alert_above_breakeven"] = (
        trade.exit_odds is not None
        and trade.breakeven_odds is not None
        and trade.exit_odds > trade.breakeven_odds
    )
    data["alert_bullet3_active"] = (
        trade.bullet_3_stake is not None and trade.bullet_3_stake > 0
    )
    return TradeResponse(**data)


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
    trade.odds_after_1st_over = body.odds_after_1st_over


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
    _apply_computed(trade)
    if trade.id is None:
        db.insert_trade(trade)
    else:
        db.update_trade(trade)
    return _trade_to_response(trade)


def _paisa_to_decimal(odds: int | None) -> float | None:
    if odds is None:
        return None
    return round(1 + (odds / 100), 2)


def _get_trade_or_404(trade_id: int, db: CockpitStore) -> Trade:
    """Fetch a trade by ID or raise HTTP 404."""
    trade = db.get_trade(trade_id)
    if trade is None:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
    return trade


@cockpit_router.get("/teams")
def list_teams(
    season: int = Query(default=2025),
    db: CockpitStore = Depends(_get_read_db),
) -> dict[str, object]:
    """Return team options for the cockpit live trade form."""
    return {
        "season": season,
        "teams": teams_service.get_teams(db),
    }


@cockpit_router.get("/venues", response_model=VenuesResponse)
def list_venues(
    season: int = Query(default=2025),
    db: CockpitStore = Depends(_get_read_db),
) -> VenuesResponse:
    """Return venue options for the cockpit live trade form."""
    return VenuesResponse(
        season=season,
        venues=venues_service.get_venues(db),
    )


@cockpit_router.post("/trades", response_model=TradeResponse, status_code=201)
async def create_trade(
    body: CreateTradeRequest,
    db: CockpitStore = Depends(_get_write_db),
) -> TradeResponse:
    """Create a new draft or active trade depending on how much of the form is filled."""
    return _save_trade(body, db)


@cockpit_router.patch("/trades/{trade_id}", response_model=TradeResponse)
def update_trade(
    trade_id: int,
    body: CreateTradeRequest,
    db: CockpitStore = Depends(_get_write_db),
) -> TradeResponse:
    """Update an existing draft or active trade."""
    trade = _get_trade_or_404(trade_id, db)
    if trade.exit_odds is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot update a closed trade.",
        )
    return _save_trade(body, db, trade)


@cockpit_router.get("/trades", response_model=List[TradeResponse])
def list_trades(
    season: Optional[int] = Query(default=None),
    result: Optional[str] = Query(default=None),
    is_fake_favourite: Optional[bool] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: CockpitStore = Depends(_get_read_db),
) -> List[TradeResponse]:
    """Return all trades, newest first. Optionally filter by season, result, or is_fake_favourite."""
    trades = db.list_trades(
        season=season,
        result=result,
        is_fake_favourite=is_fake_favourite,
        status=status,
        order="DESC",
    )
    return [_trade_to_response(trade) for trade in trades]


@cockpit_router.get("/trades/{trade_id}", response_model=TradeResponse)
def get_trade(trade_id: int, db: CockpitStore = Depends(_get_read_db)) -> TradeResponse:
    """Return a single trade by ID."""
    trade = _get_trade_or_404(trade_id, db)
    return _trade_to_response(trade)


@cockpit_router.patch("/trades/{trade_id}/bullet", response_model=TradeResponse)
def add_bullet(
    trade_id: int,
    body: AddBulletRequest,
    db: CockpitStore = Depends(_get_write_db),
) -> TradeResponse:
    """
    Add or update a bullet entry on an open trade.
    bullet_number: 0=bullet_05, 1=bullet_1, 2=bullet_2, 3=bullet_3
    Recomputes all calculated fields after update.
    """
    trade = _get_trade_or_404(trade_id, db)

    if trade.exit_odds is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot add a bullet to a closed trade.",
        )

    bullet_map = {
        0: ("bullet_05_odds", "bullet_05_stake"),
        1: ("bullet_1_odds", "bullet_1_stake"),
        2: ("bullet_2_odds", "bullet_2_stake"),
        3: ("bullet_3_odds", "bullet_3_stake"),
    }
    if body.bullet_number not in bullet_map:
        raise HTTPException(
            status_code=400,
            detail=f"bullet_number must be 0, 1, 2, or 3. Got {body.bullet_number}.",
        )

    odds_col, stake_col = bullet_map[body.bullet_number]
    setattr(trade, odds_col, body.odds)
    setattr(trade, stake_col, body.stake)
    trade.updated_at = _datetime.now(timezone.utc)
    _apply_computed(trade)
    db.update_trade(trade)
    return _trade_to_response(trade)


@cockpit_router.patch("/trades/{trade_id}/odds-after-1over", response_model=TradeResponse)
def update_odds_after_1over(
    trade_id: int,
    body: UpdateOdds1OverRequest,
    db: CockpitStore = Depends(_get_write_db),
) -> TradeResponse:
    """Record the odds after the first over is bowled on an open trade."""
    trade = _get_trade_or_404(trade_id, db)

    if trade.exit_odds is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot update odds on a closed trade.",
        )

    trade.odds_after_1st_over = body.odds_after_1st_over
    trade.updated_at = _datetime.now(timezone.utc)
    db.update_trade(trade)
    return _trade_to_response(trade)


@cockpit_router.patch("/trades/{trade_id}/close", response_model=TradeResponse)
def close_trade(
    trade_id: int,
    body: CloseTradeRequest,
    db: CockpitStore = Depends(_get_write_db),
) -> TradeResponse:
    """
    Record the exit from a trade. Sets exit_odds and recomputes actual_profit + result.
    Use exit_odds=0.0 to record a LOST trade.
    """
    trade = _get_trade_or_404(trade_id, db)

    if trade.exit_odds is not None:
        raise HTTPException(
            status_code=400,
            detail="Trade is already closed.",
        )

    trade.exit_odds = body.exit_odds
    trade.fav_reached_130 = body.fav_reached_130
    trade.is_fake_favourite = body.is_fake_favourite
    trade.notes = body.notes
    trade.updated_at = _datetime.now(timezone.utc)
    _apply_computed(trade)
    db.update_trade(trade)
    return _trade_to_response(trade)


@cockpit_router.delete("/trades/{trade_id}")
def delete_trade(trade_id: int, db: CockpitStore = Depends(_get_write_db)) -> dict:
    """Hard-delete a trade. Paper trading -- no audit trail needed."""
    _get_trade_or_404(trade_id, db)
    db.delete_trade(trade_id)
    return {"deleted": True}


@cockpit_router.get("/summary", response_model=TradeSummaryResponse)
def get_summary(
    season: Optional[int] = Query(default=None),
    db: CockpitStore = Depends(_get_read_db),
) -> TradeSummaryResponse:
    """Return aggregate performance statistics. Optionally filter by season."""
    trades = db.list_trades(season=season, status="ACTIVE", order="ASC")
    closed = [trade for trade in trades if trade.exit_odds is not None]

    total_trades = len(trades)
    total_pnl = sum(trade.actual_profit or 0.0 for trade in closed)

    wins = [trade for trade in closed if trade.result in ("SAT", "SAV+")]
    win_rate = len(wins) / len(closed) if closed else 0.0

    pct_of_targets = [trade.pct_of_target for trade in closed if trade.pct_of_target is not None]
    avg_pct_of_target = (
        sum(pct_of_targets) / len(pct_of_targets) if pct_of_targets else None
    )

    fake_f_pnl = sum(trade.actual_profit or 0.0 for trade in closed if trade.is_fake_favourite)
    non_fake_f_pnl = sum(
        trade.actual_profit or 0.0 for trade in closed if not trade.is_fake_favourite
    )

    sat_count = sum(1 for trade in closed if trade.result == "SAT")
    savplus_count = sum(1 for trade in closed if trade.result == "SAV+")
    savminus_count = sum(1 for trade in closed if trade.result == "SAV-")
    lost_count = sum(1 for trade in closed if trade.result == "LOST")

    running = 0.0
    running_pnl: list[float] = []
    for trade in trades:
        if trade.actual_profit is not None:
            running += trade.actual_profit
            running_pnl.append(round(running, 4))

    return TradeSummaryResponse(
        total_trades=total_trades,
        total_pnl=round(total_pnl, 4),
        win_rate=round(win_rate, 4),
        avg_pct_of_target=(
            round(avg_pct_of_target, 4) if avg_pct_of_target is not None else None
        ),
        fake_f_pnl=round(fake_f_pnl, 4),
        non_fake_f_pnl=round(non_fake_f_pnl, 4),
        sat_count=sat_count,
        savplus_count=savplus_count,
        savminus_count=savminus_count,
        lost_count=lost_count,
        running_pnl=running_pnl,
    )
