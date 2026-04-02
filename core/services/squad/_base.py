from typing import Dict, List, Optional, Union

import pandas as pd

from core.interfaces.player_types import FormatRulesMap


VALID_WICKET_TYPES = (
    "bowled",
    "caught",
    "lbw",
    "stumped",
    "caught and bowled",
    "hit wicket",
)


class SquadServiceBase:
    """Vectorized squad-level and player-level aggregation service."""

    def __init__(self, format_rules: Optional[FormatRulesMap] = None) -> None:
        self.rules = dict(format_rules or {})

    def _get_tactical_threshold(self, key: str, default: int) -> int:
        thresholds = self.rules.get("tactical_thresholds", {})
        if not isinstance(thresholds, dict):
            return default
        raw_value = thresholds.get(key, default)
        try:
            return int(raw_value)
        except (TypeError, ValueError):
            return default

    def _default_player_role(self) -> str:
        raw_role = self.rules.get("default_player_role")
        if isinstance(raw_role, str) and raw_role.strip():
            return raw_role.strip()
        return "All-Rounder"

    @staticmethod
    def _normalize_players(players: List[str]) -> pd.Series:
        players_series = pd.Series(players, dtype="string").dropna().astype(str).str.strip()
        return players_series[players_series.ne("")].drop_duplicates()

    @staticmethod
    def _normalize_base_df(base_df: pd.DataFrame) -> pd.DataFrame:
        if base_df is None or base_df.empty:
            return pd.DataFrame()

        normalized = base_df.copy()
        if "match_id" in normalized.columns:
            normalized["match_id"] = normalized["match_id"].astype(str)
        if "start_date" in normalized.columns and not pd.api.types.is_datetime64_any_dtype(normalized["start_date"]):
            normalized["start_date"] = pd.to_datetime(normalized["start_date"], errors="coerce")
        return normalized

    @staticmethod
    def _round_one_decimal(value: float) -> float:
        """
        Round numeric metrics to a single decimal place with explicit policy.
        """
        return round(float(value), 1)

    @staticmethod
    def _round_two_decimals(value: float) -> float:
        """
        Round economy metrics to standard cricket precision (2 decimals).
        """
        return round(float(value), 2)

    def _empty_player_records(
        self,
        players: pd.Series,
        player_roles: Optional[Dict[str, str]],
    ) -> List[Dict[str, Union[str, int, float, bool, List[Optional[str]], None]]]:
        role_map = player_roles if isinstance(player_roles, dict) else {}
        default_role = self._default_player_role()
        if players.empty:
            return []

        empty_df = pd.DataFrame({"player_name": players.astype(str)})
        empty_df["player_role"] = empty_df["player_name"].map(role_map).fillna(default_role)
        empty_df["innings"] = 0
        empty_df["batting_form"] = [[] for _ in range(len(empty_df))]
        empty_df["batting_average"] = None
        empty_df["vs_opposition_average"] = None
        empty_df["venue_innings"] = None
        empty_df["venue_runs"] = None
        empty_df["venue_average"] = None
        empty_df["venue_high_score"] = None
        empty_df["bowling_form"] = [[] for _ in range(len(empty_df))]
        empty_df["bowling_economy"] = None
        empty_df["venue_economy"] = None
        empty_df["venue_wickets"] = None
        empty_df["venue_matches"] = None
        empty_df["venue_batting_activity"] = False
        return empty_df.head(500).to_dict("records")

