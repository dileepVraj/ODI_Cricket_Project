# cockpit/models.py
# Dataclass model for the Cockpit trade record.
# Uses DuckDB-native types: BOOLEAN, TIMESTAMP, DOUBLE, INTEGER.
# No manual int/bool/str conversions needed.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping, cast


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


TRADE_WRITE_COLUMNS = (
    "season",
    "match_date",
    "team_1",
    "team_2",
    "favourite_team",
    "home_ground",
    "stadium",
    "status",
    "toss_winner",
    "toss_decision",
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
    "actual_profit",
    "pct_of_target",
    "pct_return_on_stake",
    "exit_odds",
    "result",
    "fav_reached_130",
    "is_fake_favourite",
    "notes",
    "selected_team_before_toss",
    "back_odds_before_toss",
    "lay_odds_before_toss",
    "selected_team_after_toss",
    "back_odds_after_toss",
    "lay_odds_after_toss",
    "created_at",
    "updated_at",
    "odds_after_1st_over",
)


TradeDbValue = int | float | str | bool | datetime | None


def _as_int(value: TradeDbValue) -> int:
    return int(cast(int | float | str | bool, value))


def _as_float(value: TradeDbValue) -> float:
    return float(cast(int | float | str | bool, value))


def _as_datetime(value: TradeDbValue) -> datetime | None:
    return _parse_datetime(cast(datetime | str | None, value))


def _as_optional_text(value: TradeDbValue) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


@dataclass(slots=True)
class Trade:
    id: int | None = None
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
    actual_profit: float | None = None
    pct_of_target: float | None = None
    pct_return_on_stake: float | None = None
    exit_odds: float | None = None
    result: str | None = None
    fav_reached_130: bool = False
    is_fake_favourite: bool = False
    notes: str | None = None
    selected_team_before_toss: str | None = None
    back_odds_before_toss: int | None = None
    lay_odds_before_toss: int | None = None
    selected_team_after_toss: str | None = None
    back_odds_after_toss: int | None = None
    lay_odds_after_toss: int | None = None
    odds_after_1st_over: float | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def from_row(cls, row: Mapping[str, TradeDbValue]) -> Trade:
        """Build a Trade from a DuckDB result row."""
        return cls(
            id=_as_int(row["id"]),
            season=_as_int(row["season"]),
            match_date=_as_datetime(row["match_date"]),
            team_1=str(row["team_1"]),
            team_2=str(row["team_2"]),
            favourite_team=str(row["favourite_team"]),
            home_ground=str(row["home_ground"]),
            stadium=str(row["stadium"]),
            status=(str(row["status"]) if row["status"] is not None else "DRAFT"),
            toss_winner=_as_optional_text(row["toss_winner"]),
            toss_decision=_as_optional_text(row["toss_decision"]),
            bankroll=_as_float(row["bankroll"]),
            opening_odds=(_as_float(row["opening_odds"]) if row["opening_odds"] is not None else None),
            bullet_05_odds=(_as_float(row["bullet_05_odds"]) if row["bullet_05_odds"] is not None else None),
            bullet_05_stake=(_as_float(row["bullet_05_stake"]) if row["bullet_05_stake"] is not None else None),
            bullet_1_odds=(_as_float(row["bullet_1_odds"]) if row["bullet_1_odds"] is not None else None),
            bullet_1_stake=(_as_float(row["bullet_1_stake"]) if row["bullet_1_stake"] is not None else None),
            bullet_2_odds=(_as_float(row["bullet_2_odds"]) if row["bullet_2_odds"] is not None else None),
            bullet_2_stake=(_as_float(row["bullet_2_stake"]) if row["bullet_2_stake"] is not None else None),
            bullet_3_odds=(_as_float(row["bullet_3_odds"]) if row["bullet_3_odds"] is not None else None),
            bullet_3_stake=(_as_float(row["bullet_3_stake"]) if row["bullet_3_stake"] is not None else None),
            total_stake=(_as_float(row["total_stake"]) if row["total_stake"] is not None else None),
            target_profit=(_as_float(row["target_profit"]) if row["target_profit"] is not None else None),
            profit_80pct=(_as_float(row["profit_80pct"]) if row["profit_80pct"] is not None else None),
            exit_target_odds=(_as_float(row["exit_target_odds"]) if row["exit_target_odds"] is not None else None),
            breakeven_odds=(_as_float(row["breakeven_odds"]) if row["breakeven_odds"] is not None else None),
            actual_profit=(_as_float(row["actual_profit"]) if row["actual_profit"] is not None else None),
            pct_of_target=(_as_float(row["pct_of_target"]) if row["pct_of_target"] is not None else None),
            pct_return_on_stake=(_as_float(row["pct_return_on_stake"]) if row["pct_return_on_stake"] is not None else None),
            exit_odds=(_as_float(row["exit_odds"]) if row["exit_odds"] is not None else None),
            result=(str(row["result"]) if row["result"] is not None else None),
            fav_reached_130=bool(row["fav_reached_130"]),
            is_fake_favourite=bool(row["is_fake_favourite"]),
            notes=_as_optional_text(row["notes"]),
            selected_team_before_toss=_as_optional_text(row["selected_team_before_toss"]),
            back_odds_before_toss=(
                _as_int(row["back_odds_before_toss"]) if row["back_odds_before_toss"] is not None else None
            ),
            lay_odds_before_toss=(
                _as_int(row["lay_odds_before_toss"]) if row["lay_odds_before_toss"] is not None else None
            ),
            selected_team_after_toss=_as_optional_text(row["selected_team_after_toss"]),
            back_odds_after_toss=(
                _as_int(row["back_odds_after_toss"]) if row["back_odds_after_toss"] is not None else None
            ),
            lay_odds_after_toss=(
                _as_int(row["lay_odds_after_toss"]) if row["lay_odds_after_toss"] is not None else None
            ),
            odds_after_1st_over=(_as_float(row["odds_after_1st_over"]) if row["odds_after_1st_over"] is not None else None),
            created_at=_as_datetime(row["created_at"]) or _utcnow(),
            updated_at=_as_datetime(row["updated_at"]) or _utcnow(),
        )

    def to_db_values(self) -> dict[str, TradeDbValue]:
        """Return a dict of column -> value for INSERT / UPDATE.
        Excludes `id` -- the DB sequence assigns it on insert."""
        return {col: getattr(self, col) for col in TRADE_WRITE_COLUMNS}
