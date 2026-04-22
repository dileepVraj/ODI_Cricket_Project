# cockpit/schemas.py
# Pydantic request and response models for the Cockpit API.

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


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
    odds_after_1st_over: Optional[float] = None

    model_config = ConfigDict(extra="forbid")


class AddBulletRequest(BaseModel):
    """Body for PATCH /api/cockpit/trades/{id}/bullet"""

    bullet_number: int = Field(
        ...,
        description="Which bullet: 0 for bullet_05, 1 for bullet_1, 2 for bullet_2, 3 for bullet_3",
    )
    odds: float = Field(..., description="Decimal odds for this bullet entry")
    stake: float = Field(..., description="Units staked on this bullet")

    model_config = ConfigDict(extra="forbid")


class UpdateOdds1OverRequest(BaseModel):
    """Body for PATCH /api/cockpit/trades/{id}/odds-after-1over"""

    odds_after_1st_over: float = Field(..., description="Decimal odds after the first over")

    model_config = ConfigDict(extra="forbid")


class CloseTradeRequest(BaseModel):
    """Body for PATCH /api/cockpit/trades/{id}/close"""

    exit_odds: float = Field(
        ...,
        description="Decimal odds at exit. Use 0.0 to record a LOST trade.",
    )
    fav_reached_130: bool = Field(
        default=False,
        description="Did the favourite's odds reach 1.30 before reversing?",
    )
    is_fake_favourite: bool = Field(
        default=False,
        description="Was this a fake favourite (not genuine market leader)?",
    )
    notes: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class VenueInfo(BaseModel):
    """Venue option used by the cockpit live trade form."""

    model_config = ConfigDict(extra="forbid")

    id: str
    label: str


class VenuesResponse(BaseModel):
    """Returned by GET /api/cockpit/venues"""

    season: int
    venues: List[VenueInfo]

    model_config = ConfigDict(extra="forbid")


class TradeResponse(BaseModel):
    """Returned by all trade endpoints. Includes every field including computed ones."""

    id: int
    season: int
    match_date: Optional[datetime]
    team_1: str
    team_2: str
    favourite_team: str
    home_ground: Literal["FAV", "UG", "NEU"]
    stadium: str
    status: Literal["DRAFT", "ACTIVE"]
    toss_winner: Optional[str]
    toss_decision: Optional[Literal["bat", "field"]]
    bankroll: float
    opening_odds: Optional[float]
    bullet_05_odds: Optional[float]
    bullet_05_stake: Optional[float]
    bullet_1_odds: Optional[float]
    bullet_1_stake: Optional[float]
    bullet_2_odds: Optional[float]
    bullet_2_stake: Optional[float]
    bullet_3_odds: Optional[float]
    bullet_3_stake: Optional[float]
    total_stake: Optional[float]
    target_profit: Optional[float]
    profit_80pct: Optional[float]
    exit_target_odds: Optional[float]
    breakeven_odds: Optional[float]
    actual_profit: Optional[float]
    pct_of_target: Optional[float]
    pct_return_on_stake: Optional[float]
    exit_odds: Optional[float]
    result: Literal["OPEN", "LOST", "SAT", "SAV+", "SAV-"] | None
    fav_reached_130: bool
    is_fake_favourite: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    selected_team_before_toss: Optional[str] = None
    back_odds_before_toss: Optional[int] = None
    lay_odds_before_toss: Optional[int] = None
    selected_team_after_toss: Optional[str] = None
    back_odds_after_toss: Optional[int] = None
    lay_odds_after_toss: Optional[int] = None
    odds_after_1st_over: Optional[float] = None
    alert_above_breakeven: bool = Field(
        description="True if exit_odds > breakeven_odds (exited at a loss despite backing out)"
    )
    alert_bullet3_active: bool = Field(
        description="True if the emergency bullet (bullet 3) has been used"
    )

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class TradeSummaryResponse(BaseModel):
    """Returned by GET /api/cockpit/summary"""

    total_trades: int
    total_pnl: float
    win_rate: float
    avg_pct_of_target: Optional[float]
    fake_f_pnl: float
    non_fake_f_pnl: float
    sat_count: int
    savplus_count: int
    savminus_count: int
    lost_count: int
    running_pnl: List[float]

    model_config = ConfigDict(extra="forbid")
