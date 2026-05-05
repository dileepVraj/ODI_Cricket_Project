# cockpit/schemas.py
# Pydantic request and response models for the Cockpit API.
# Live trade fields (bullets, P&L, close) have been removed.
# Only match setup fields remain.

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


TradeSentiment = Literal["saved", "satisfied", "lost", "achieved"]


class TradeMistakes(BaseModel):
    """Structured mistake tags + optional free-text note."""

    tags: List[str] = Field(default_factory=list)
    note: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class CreateTradeRequest(BaseModel):
    """Body for POST /api/cockpit/trades"""

    season: int = Field(..., description="e.g. 2025")
    match_date: Optional[datetime] = None
    team_1: str = Field(..., description="e.g. 'MI'")
    team_2: str = Field(..., description="e.g. 'CSK'")
    favourite_team: str = Field(..., description="Team being traded")
    home_ground: Literal["FAV", "UG", "NEU"] = Field(..., description="Home ground advantage")
    stadium: str = Field(..., description="e.g. 'MUM'")
    toss_winner: Optional[str] = Field(default=None, description="'FAV', 'UG', or null")
    toss_decision: Optional[Literal["bat", "field"]] = Field(default=None)
    bankroll: float = Field(default=100.0)
    opening_odds: Optional[float] = None
    selected_team_before_toss: Optional[str] = None
    back_odds_before_toss: Optional[int] = None
    lay_odds_before_toss: Optional[int] = None
    selected_team_after_toss: Optional[str] = None
    back_odds_after_toss: Optional[int] = None
    lay_odds_after_toss: Optional[int] = None

    model_config = ConfigDict(extra="forbid")


class VenueInfo(BaseModel):
    """Venue option used by the cockpit match setup form."""

    model_config = ConfigDict(extra="forbid")

    id: str
    label: str


class VenuesResponse(BaseModel):
    """Returned by GET /api/cockpit/venues"""

    season: int
    venues: List[VenueInfo]

    model_config = ConfigDict(extra="forbid")


class TradeResponse(BaseModel):
    """Returned by all trade endpoints. Match setup fields only."""

    id: int
    season: int
    match_date: Optional[datetime]
    team_1: str
    team_2: str
    favourite_team: str
    home_ground: Literal["FAV", "UG", "NEU"]
    stadium: str
    status: Literal["DRAFT", "ACTIVE", "SETTLED", "VOID"]
    toss_winner: Optional[str]
    toss_decision: Optional[Literal["bat", "field"]]
    bankroll: float
    opening_odds: Optional[float]
    bullet_05_odds: Optional[float] = None
    bullet_05_stake: Optional[float] = None
    bullet_1_odds: Optional[float] = None
    bullet_1_stake: Optional[float] = None
    bullet_2_odds: Optional[float] = None
    bullet_2_stake: Optional[float] = None
    bullet_3_odds: Optional[float] = None
    bullet_3_stake: Optional[float] = None
    total_stake: Optional[float] = None
    target_profit: Optional[float] = None
    profit_80pct: Optional[float] = None
    exit_target_odds: Optional[float] = None
    breakeven_odds: Optional[float] = None
    pct_of_target: Optional[float] = None
    pct_return_on_stake: Optional[float] = None
    exit_odds: Optional[float] = None
    fav_reached_130: bool = False
    is_fake_favourite: bool = False
    notes: Optional[str] = None
    crex_url: Optional[str] = None
    selected_team_before_toss: Optional[str] = None
    back_odds_before_toss: Optional[int] = None
    lay_odds_before_toss: Optional[int] = None
    selected_team_after_toss: Optional[str] = None
    back_odds_after_toss: Optional[int] = None
    lay_odds_after_toss: Optional[int] = None
    result: Optional[str] = None
    winner: Optional[Literal["team_1", "team_2", "tie"]] = None
    actual_profit: Optional[float] = None
    trade_sentiment: Optional[TradeSentiment] = None
    fav_sub_30_loss: bool = False
    lowest_fav_odds_paise: Optional[int] = None
    post_low_bet_number: Optional[int] = None
    post_low_bet_stake: Optional[float] = None
    trade_mistakes: Optional[str] = None
    targeted_pnl: Optional[float] = None
    achieved_yield_percentage: Optional[float] = None
    total_volume_wagered: float = 0.0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class HistoryTradeResponse(TradeResponse):
    """Returned by the history endpoints with format metadata attached."""

    format_key: str
    format_label: str

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class HistorySummaryResponse(BaseModel):
    """Returned by GET /api/cockpit/history/summary."""

    format_scope: Literal["single", "all"]
    format_key: Optional[str] = None
    format_keys: List[str] = Field(default_factory=list)
    trade_count: int
    settled_trade_count: int
    total_realized_pnl: float
    total_volume_wagered: float
    positive_trades: int
    negative_trades: int
    earliest_match_date: Optional[datetime] = None
    latest_match_date: Optional[datetime] = None

    model_config = ConfigDict(extra="forbid")


class SettleTradeRequest(BaseModel):
    """Body for POST /api/cockpit/trades/{id}/settle"""

    winner: Literal["team_1", "team_2", "tie"]
    sentiment: TradeSentiment
    fav_sub_30_loss: bool = False
    lowest_fav_odds_paise: Optional[int] = None
    post_low_bet_number: Optional[int] = None
    post_low_bet_stake: Optional[float] = None
    targeted_pnl: float = Field(..., ge=0)
    achieved_yield: float
    trade_mistakes: Optional[TradeMistakes] = None

    model_config = ConfigDict(extra="forbid")


class AddBetRequest(BaseModel):
    team: str = Field(..., min_length=1)
    bet_type: Literal["BACK", "LAY"]
    odds_paise: int = Field(..., gt=0)
    stake: float = Field(..., gt=0)
    purpose: Literal["BET", "CASHOUT"] = Field(default="BET")

    model_config = ConfigDict(extra="forbid")


class BetResponse(BaseModel):
    id: int
    trade_id: int
    team: str
    bet_type: str
    odds_paise: int
    odds_decimal: float
    stake: float
    liability: float
    is_open: bool
    created_at: str

    model_config = ConfigDict(extra="forbid", from_attributes=True)


class TradeRestoreRequest(BaseModel):
    """Body for POST /api/cockpit/trades/restore."""

    trade: TradeResponse
    bets: List[BetResponse]

    model_config = ConfigDict(extra="forbid")


class TradeStateResponse(TradeResponse):
    net_pnl_team_1: float
    net_pnl_team_2: float
    total_exposure: float
    available_bankroll: float

    model_config = ConfigDict(from_attributes=True, extra="forbid")
