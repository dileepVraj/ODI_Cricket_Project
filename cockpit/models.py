# cockpit/models.py
# Dataclass models for cockpit match and trade records.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal, Mapping, cast


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_datetime(value: datetime | str | None) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    text = str(value)
    if text == "NaT":
        return None
    return datetime.fromisoformat(text)


def _match_date_db_value(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.isoformat()


TRADE_WRITE_COLUMNS = (
    "match_id",
    "favourite_team",
    "home_ground",
    "bankroll",
    "opening_odds",
    "bullet_05_odds",
    "bullet_05_stake",
    "bullet_1_odds",
    "bullet_1_stake",
    "bullet_2_odds",
    "bullet_2_stake",
    "bullet_3_odds",
    "bullet_3_stake",
    "total_stake",
    "target_profit",
    "profit_80pct",
    "exit_target_odds",
    "breakeven_odds",
    "pct_of_target",
    "pct_return_on_stake",
    "exit_odds",
    "fav_reached_130",
    "is_fake_favourite",
    "notes",
    "crex_url",
    "selected_team_before_toss",
    "back_odds_before_toss",
    "lay_odds_before_toss",
    "selected_team_after_toss",
    "back_odds_after_toss",
    "lay_odds_after_toss",
    "result",
    "winner",
    "actual_profit",
    "trade_sentiment",
    "fav_sub_30_loss",
    "missed_swing_team",
    "missed_swing_back_odds",
    "missed_swing_lay_odds",
    "missed_swing_bet_index",
    "missed_swing_cumulative_stake",
    "missed_swing_net_pnl",
    "trade_mistakes",
    "targeted_pnl",
    "achieved_yield_percentage",
    "total_volume_wagered",
    "status",
    "created_at",
    "updated_at",
)

MATCH_WRITE_COLUMNS = (
    "season",
    "match_date",
    "team_1",
    "team_2",
    "stadium",
    "toss_winner",
    "toss_decision",
)

TradeDbValue = int | float | str | bool | datetime | None
TradeSentiment = Literal["saved", "satisfied", "lost", "achieved"]


def _as_int(value: TradeDbValue) -> int:
    return int(cast(int | float | str | bool, value))


def _as_float(value: TradeDbValue) -> float:
    return float(cast(int | float | str | bool, value))


def _as_bool(value: TradeDbValue, *, default: bool = False) -> bool:
    if value is None:
        return default
    return bool(int(cast(int | float | str | bool, value)))


def _as_datetime(value: TradeDbValue) -> datetime | None:
    return _parse_datetime(cast(datetime | str | None, value))


def _as_optional_text(value: TradeDbValue) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _db_value(value: TradeDbValue) -> TradeDbValue:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


@dataclass(slots=True)
class Match:
    id: int | None = None
    season: int = 0
    match_date: datetime | None = None
    team_1: str = ""
    team_2: str = ""
    stadium: str = ""
    toss_winner: str | None = None
    toss_decision: str | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, TradeDbValue]) -> Match:
        return cls(
            id=_as_int(row["id"]) if row.get("id") is not None else None,
            season=_as_int(row["season"]),
            match_date=_as_datetime(row.get("match_date")),
            team_1=str(row["team_1"]),
            team_2=str(row["team_2"]),
            stadium=str(row["stadium"]),
            toss_winner=_as_optional_text(row.get("toss_winner")),
            toss_decision=_as_optional_text(row.get("toss_decision")),
        )

    def to_db_values(self) -> dict[str, TradeDbValue]:
        return {
            "season": self.season,
            "match_date": _match_date_db_value(self.match_date),
            "team_1": self.team_1,
            "team_2": self.team_2,
            "stadium": self.stadium,
            "toss_winner": self.toss_winner,
            "toss_decision": self.toss_decision,
        }


@dataclass(slots=True)
class Trade:
    id: int | None = None
    match_id: int | None = None
    season: int = 0
    match_date: datetime | None = None
    team_1: str = ""
    team_2: str = ""
    favourite_team: str = ""
    home_ground: str = ""
    stadium: str = ""
    status: str = "DRAFT"
    toss_winner: str | None = None
    toss_decision: str | None = None
    bankroll: float = 100.0
    opening_odds: float | None = None
    bullet_05_odds: float | None = None
    bullet_05_stake: float | None = None
    bullet_1_odds: float | None = None
    bullet_1_stake: float | None = None
    bullet_2_odds: float | None = None
    bullet_2_stake: float | None = None
    bullet_3_odds: float | None = None
    bullet_3_stake: float | None = None
    total_stake: float | None = None
    target_profit: float | None = None
    profit_80pct: float | None = None
    exit_target_odds: float | None = None
    breakeven_odds: float | None = None
    pct_of_target: float | None = None
    pct_return_on_stake: float | None = None
    exit_odds: float | None = None
    fav_reached_130: bool = False
    is_fake_favourite: bool = False
    notes: str | None = None
    crex_url: str | None = None
    selected_team_before_toss: str | None = None
    back_odds_before_toss: int | None = None
    lay_odds_before_toss: int | None = None
    selected_team_after_toss: str | None = None
    back_odds_after_toss: int | None = None
    lay_odds_after_toss: int | None = None
    result: str | None = None
    winner: str | None = None
    actual_profit: float | None = None
    trade_sentiment: TradeSentiment | None = None
    fav_sub_30_loss: bool = False
    missed_swing_team: str | None = None
    missed_swing_back_odds: int | None = None
    missed_swing_lay_odds: int | None = None
    missed_swing_bet_index: int | None = None
    missed_swing_cumulative_stake: float | None = None
    missed_swing_net_pnl: float | None = None
    trade_mistakes: str | None = None
    targeted_pnl: float | None = None
    achieved_yield_percentage: float | None = None
    total_volume_wagered: float = 0.0
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def from_row(cls, row: Mapping[str, TradeDbValue]) -> Trade:
        """Build a Trade from a joined database row."""
        return cls(
            id=_as_int(row["id"]) if row.get("id") is not None else None,
            match_id=_as_int(row["match_id"]) if row.get("match_id") is not None else None,
            season=_as_int(row["season"]) if row.get("season") is not None else 0,
            match_date=_as_datetime(row.get("match_date")),
            team_1=str(row.get("team_1", "")),
            team_2=str(row.get("team_2", "")),
            favourite_team=str(row.get("favourite_team", "")),
            home_ground=str(row.get("home_ground", "")),
            stadium=str(row.get("stadium", "")),
            status=(str(row.get("status")) if row.get("status") is not None else "DRAFT"),
            toss_winner=_as_optional_text(row.get("toss_winner")),
            toss_decision=_as_optional_text(row.get("toss_decision")),
            bankroll=_as_float(row.get("bankroll", 100.0)),
            opening_odds=(
                _as_float(row["opening_odds"]) if row.get("opening_odds") is not None else None
            ),
            bullet_05_odds=(
                _as_float(row["bullet_05_odds"]) if row.get("bullet_05_odds") is not None else None
            ),
            bullet_05_stake=(
                _as_float(row["bullet_05_stake"]) if row.get("bullet_05_stake") is not None else None
            ),
            bullet_1_odds=(
                _as_float(row["bullet_1_odds"]) if row.get("bullet_1_odds") is not None else None
            ),
            bullet_1_stake=(
                _as_float(row["bullet_1_stake"]) if row.get("bullet_1_stake") is not None else None
            ),
            bullet_2_odds=(
                _as_float(row["bullet_2_odds"]) if row.get("bullet_2_odds") is not None else None
            ),
            bullet_2_stake=(
                _as_float(row["bullet_2_stake"]) if row.get("bullet_2_stake") is not None else None
            ),
            bullet_3_odds=(
                _as_float(row["bullet_3_odds"]) if row.get("bullet_3_odds") is not None else None
            ),
            bullet_3_stake=(
                _as_float(row["bullet_3_stake"]) if row.get("bullet_3_stake") is not None else None
            ),
            total_stake=(
                _as_float(row["total_stake"]) if row.get("total_stake") is not None else None
            ),
            target_profit=(
                _as_float(row["target_profit"]) if row.get("target_profit") is not None else None
            ),
            profit_80pct=(
                _as_float(row["profit_80pct"]) if row.get("profit_80pct") is not None else None
            ),
            exit_target_odds=(
                _as_float(row["exit_target_odds"])
                if row.get("exit_target_odds") is not None
                else None
            ),
            breakeven_odds=(
                _as_float(row["breakeven_odds"])
                if row.get("breakeven_odds") is not None
                else None
            ),
            pct_of_target=(
                _as_float(row["pct_of_target"]) if row.get("pct_of_target") is not None else None
            ),
            pct_return_on_stake=(
                _as_float(row["pct_return_on_stake"])
                if row.get("pct_return_on_stake") is not None
                else None
            ),
            exit_odds=(
                _as_float(row["exit_odds"]) if row.get("exit_odds") is not None else None
            ),
            fav_reached_130=_as_bool(row.get("fav_reached_130"), default=False),
            is_fake_favourite=_as_bool(row.get("is_fake_favourite"), default=False),
            notes=_as_optional_text(row.get("notes")),
            crex_url=_as_optional_text(row.get("crex_url")),
            selected_team_before_toss=_as_optional_text(row.get("selected_team_before_toss")),
            back_odds_before_toss=(
                _as_int(row["back_odds_before_toss"])
                if row.get("back_odds_before_toss") is not None
                else None
            ),
            lay_odds_before_toss=(
                _as_int(row["lay_odds_before_toss"])
                if row.get("lay_odds_before_toss") is not None
                else None
            ),
            selected_team_after_toss=_as_optional_text(row.get("selected_team_after_toss")),
            back_odds_after_toss=(
                _as_int(row["back_odds_after_toss"])
                if row.get("back_odds_after_toss") is not None
                else None
            ),
            lay_odds_after_toss=(
                _as_int(row["lay_odds_after_toss"])
                if row.get("lay_odds_after_toss") is not None
                else None
            ),
            result=_as_optional_text(row.get("result")),
            winner=_as_optional_text(row.get("winner")),
            actual_profit=(
                _as_float(row["actual_profit"]) if row.get("actual_profit") is not None else None
            ),
            trade_sentiment=cast(
                TradeSentiment | None,
                _as_optional_text(row.get("trade_sentiment")),
            ),
            fav_sub_30_loss=_as_bool(row.get("fav_sub_30_loss"), default=False),
            missed_swing_team=_as_optional_text(row.get("missed_swing_team")),
            missed_swing_back_odds=(
                _as_int(row["missed_swing_back_odds"])
                if row.get("missed_swing_back_odds") is not None
                else None
            ),
            missed_swing_lay_odds=(
                _as_int(row["missed_swing_lay_odds"])
                if row.get("missed_swing_lay_odds") is not None
                else None
            ),
            missed_swing_bet_index=(
                _as_int(row["missed_swing_bet_index"])
                if row.get("missed_swing_bet_index") is not None
                else None
            ),
            missed_swing_cumulative_stake=(
                _as_float(row["missed_swing_cumulative_stake"])
                if row.get("missed_swing_cumulative_stake") is not None
                else None
            ),
            missed_swing_net_pnl=(
                _as_float(row["missed_swing_net_pnl"])
                if row.get("missed_swing_net_pnl") is not None
                else None
            ),
            trade_mistakes=(
                str(row["trade_mistakes"])
                if row.get("trade_mistakes") is not None
                else None
            ),
            targeted_pnl=(
                _as_float(row["targeted_pnl"]) if row.get("targeted_pnl") is not None else None
            ),
            achieved_yield_percentage=(
                _as_float(row["achieved_yield_percentage"])
                if row.get("achieved_yield_percentage") is not None
                else None
            ),
            total_volume_wagered=(
                _as_float(row["total_volume_wagered"])
                if row.get("total_volume_wagered") is not None
                else 0.0
            ),
            created_at=_as_datetime(row.get("created_at")) or _utcnow(),
            updated_at=_as_datetime(row.get("updated_at")) or _utcnow(),
        )

    def to_match(self) -> Match:
        return Match(
            season=self.season,
            match_date=self.match_date,
            team_1=self.team_1,
            team_2=self.team_2,
            stadium=self.stadium,
            toss_winner=self.toss_winner,
            toss_decision=self.toss_decision,
        )

    def to_db_values(self) -> dict[str, TradeDbValue]:
        if self.match_id is None:
            raise ValueError("Trade.match_id is required before writing to the database.")
        values: dict[str, TradeDbValue] = {
            "match_id": self.match_id,
            "favourite_team": self.favourite_team,
            "home_ground": self.home_ground,
            "bankroll": self.bankroll,
            "opening_odds": self.opening_odds,
            "bullet_05_odds": self.bullet_05_odds,
            "bullet_05_stake": self.bullet_05_stake,
            "bullet_1_odds": self.bullet_1_odds,
            "bullet_1_stake": self.bullet_1_stake,
            "bullet_2_odds": self.bullet_2_odds,
            "bullet_2_stake": self.bullet_2_stake,
            "bullet_3_odds": self.bullet_3_odds,
            "bullet_3_stake": self.bullet_3_stake,
            "total_stake": self.total_stake,
            "target_profit": self.target_profit,
            "profit_80pct": self.profit_80pct,
            "exit_target_odds": self.exit_target_odds,
            "breakeven_odds": self.breakeven_odds,
            "pct_of_target": self.pct_of_target,
            "pct_return_on_stake": self.pct_return_on_stake,
            "exit_odds": self.exit_odds,
            "fav_reached_130": self.fav_reached_130,
            "is_fake_favourite": self.is_fake_favourite,
            "notes": self.notes,
            "crex_url": self.crex_url,
            "selected_team_before_toss": self.selected_team_before_toss,
            "back_odds_before_toss": self.back_odds_before_toss,
            "lay_odds_before_toss": self.lay_odds_before_toss,
            "selected_team_after_toss": self.selected_team_after_toss,
            "back_odds_after_toss": self.back_odds_after_toss,
            "lay_odds_after_toss": self.lay_odds_after_toss,
            "result": self.result,
            "winner": self.winner,
            "actual_profit": self.actual_profit,
            "trade_sentiment": self.trade_sentiment,
            "fav_sub_30_loss": self.fav_sub_30_loss,
            "missed_swing_team": self.missed_swing_team,
            "missed_swing_back_odds": self.missed_swing_back_odds,
            "missed_swing_lay_odds": self.missed_swing_lay_odds,
            "missed_swing_bet_index": self.missed_swing_bet_index,
            "missed_swing_cumulative_stake": self.missed_swing_cumulative_stake,
            "missed_swing_net_pnl": self.missed_swing_net_pnl,
            "trade_mistakes": self.trade_mistakes,
            "targeted_pnl": self.targeted_pnl,
            "achieved_yield_percentage": self.achieved_yield_percentage,
            "total_volume_wagered": self.total_volume_wagered,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        return {column: _db_value(values[column]) for column in TRADE_WRITE_COLUMNS}
