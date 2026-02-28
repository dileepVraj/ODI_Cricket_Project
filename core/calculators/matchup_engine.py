from typing import Dict, List, Mapping, Optional, Sequence, Union

import numpy as np
import pandas as pd


VALID_WICKET_TYPES = (
    "bowled",
    "caught",
    "lbw",
    "stumped",
    "caught and bowled",
    "hit wicket",
)


class MatchupEngine:
    """Vectorized matchup/archetype calculator with semantic outputs."""

    def __init__(self, format_rules: Optional[Mapping[str, object]] = None) -> None:
        self.rules = dict(format_rules or {})

    @staticmethod
    def _as_int_threshold(thresholds: Optional[Mapping[str, object]], key: str, default: int) -> int:
        raw_value = (thresholds or {}).get(key, default)
        try:
            return int(raw_value)
        except (TypeError, ValueError):
            return default

    def _get_tactical_threshold(self, key: str, default: int) -> int:
        thresholds = self.rules.get("tactical_thresholds", {})
        if not isinstance(thresholds, dict):
            return default
        return self._as_int_threshold(thresholds, key, default)

    def _get_engine_default(self, key: str, default: int) -> int:
        defaults = self.rules.get("engine_defaults", {})
        if not isinstance(defaults, dict):
            return default
        return self._as_int_threshold(defaults, key, default)

    @staticmethod
    def _round_one_decimal(value: float) -> float:
        """
        Round numeric metrics to a single decimal place with explicit policy.
        """
        return round(float(value), 1)

    @staticmethod
    def _default_player_role(raw_role: object) -> str:
        if isinstance(raw_role, str) and raw_role.strip():
            return raw_role.strip()
        return "All-Rounder"

    @staticmethod
    def _as_numeric_or_none(value: object) -> Optional[Union[int, float]]:
        try:
            if value is None or pd.isna(value):
                return None
        except (TypeError, ValueError):
            return None
        if isinstance(value, (int, np.integer)) and not isinstance(value, bool):
            return int(value)
        if isinstance(value, (float, np.floating)):
            return float(value)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        if numeric.is_integer():
            return int(numeric)
        return float(numeric)

    def _build_empty_matrix(
        self,
        players: pd.Series,
        styles: pd.Index,
        player_roles: Optional[Dict[str, str]],
    ) -> List[Dict[str, object]]:
        if players.empty or styles.empty:
            return []

        role_map = player_roles if isinstance(player_roles, dict) else {}
        default_role = self._default_player_role(self.rules.get("default_player_role"))
        players_df = pd.DataFrame({"player_name": players.astype(str)}).drop_duplicates()
        players_df["player_role"] = players_df["player_name"].map(role_map).fillna(default_role)
        styles_df = pd.DataFrame({"style_key": styles.astype(str)})

        scaffold = (
            players_df.assign(_join_key=1)
            .merge(styles_df.assign(_join_key=1), on="_join_key", how="inner")
            .drop(columns="_join_key")
        )

        by_player: Dict[str, Dict[str, object]] = {}
        for row in scaffold.to_dict("records"):
            player_name = str(row["player_name"])
            player_role = str(row["player_role"])
            style_key = str(row["style_key"])
            player_key = f"{player_name}::{player_role}"
            if player_key not in by_player:
                by_player[player_key] = {
                    "player_name": player_name,
                    "player_role": player_role,
                    "style_metrics": {},
                }
            style_metrics = by_player[player_key]["style_metrics"]
            if isinstance(style_metrics, dict):
                style_metrics[style_key] = {
                    "average": None,
                    "strike_rate": None,
                    "average_raw": None,
                }

        return list(by_player.values())

    def analyze_types(
        self,
        player_df: pd.DataFrame,
        style_map: Dict[str, str],
        players: Sequence[str],
        opposition_bowlers: Sequence[str],
        player_roles: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, object]]:
        """
        Build batter-vs-style tactical distribution using vectorized operations only.
        Returns row-wise records for UI table rendering.
        """
        if not isinstance(player_df, pd.DataFrame) or player_df.empty:
            return []

        if "striker" not in player_df.columns or "bowler" not in player_df.columns:
            return []

        style_lookup = style_map if isinstance(style_map, dict) else {}
        unmapped_min_balls = self._get_tactical_threshold(
            "unmapped_min_balls",
            self._get_engine_default("unmapped_min_balls_fallback", 1),
        )

        players_series = pd.Series(players, dtype="string").dropna().astype(str).str.strip()
        players_series = players_series[players_series.ne("")].drop_duplicates()
        if players_series.empty:
            return []

        opposition_series = pd.Series(opposition_bowlers, dtype="string").dropna().astype(str).str.strip()
        opposition_series = opposition_series[opposition_series.ne("")].drop_duplicates()
        if opposition_series.empty:
            return []

        source_df = player_df.copy()
        source_df["striker"] = source_df["striker"].astype("string")
        source_df["bowler"] = source_df["bowler"].astype("string")
        source_df = source_df[source_df["striker"].notna() & source_df["bowler"].notna()]
        if source_df.empty:
            return []

        bowl_counts = source_df["bowler"].value_counts(dropna=False)
        opposition_df = pd.DataFrame({"bowler": opposition_series.astype("string")})
        opposition_df["style"] = opposition_df["bowler"].map(style_lookup).fillna("Unknown")
        opposition_df = opposition_df[opposition_df["style"].ne("Part-Timer")]
        if opposition_df.empty:
            return []

        opposition_df["balls_delivered"] = (
            opposition_df["bowler"].map(bowl_counts).fillna(0).astype(int)
        )

        known_styles = (
            opposition_df.loc[opposition_df["style"].ne("Unknown"), "style"]
            .astype(str)
            .drop_duplicates()
        )
        unmapped_bowlers = opposition_df.loc[
            opposition_df["style"].eq("Unknown")
            & opposition_df["balls_delivered"].gt(unmapped_min_balls),
            "bowler",
        ]

        style_order = pd.Index(known_styles)
        if not unmapped_bowlers.empty:
            style_order = style_order.append(pd.Index(["Unmapped"]))
        if style_order.empty:
            return []

        analysis_df = source_df[source_df["striker"].isin(players_series)].copy()
        if analysis_df.empty:
            return self._build_empty_matrix(players_series, style_order, player_roles)

        mapped_styles = analysis_df["bowler"].map(style_lookup).fillna("Unknown")
        analysis_df["style_key"] = np.where(
            mapped_styles.eq("Unknown") & analysis_df["bowler"].isin(unmapped_bowlers),
            "Unmapped",
            mapped_styles,
        )
        analysis_df = analysis_df[analysis_df["style_key"].isin(style_order)]
        if analysis_df.empty:
            return self._build_empty_matrix(players_series, style_order, player_roles)

        if "runs_off_bat" not in analysis_df.columns:
            analysis_df["runs_off_bat"] = 0
        analysis_df["runs_off_bat"] = pd.to_numeric(analysis_df["runs_off_bat"], errors="coerce").fillna(0.0)

        if "match_id" not in analysis_df.columns:
            analysis_df["match_id"] = analysis_df.index.astype(str)
        if "wicket_type" not in analysis_df.columns:
            analysis_df["wicket_type"] = pd.NA
        analysis_df["is_out"] = analysis_df["wicket_type"].isin(VALID_WICKET_TYPES).astype(int)

        grouped = (
            analysis_df.groupby(["striker", "style_key"], dropna=False)
            .agg(
                runs=("runs_off_bat", "sum"),
                balls=("match_id", "count"),
                outs=("is_out", "sum"),
            )
            .reset_index()
        )

        if grouped.empty:
            return self._build_empty_matrix(players_series, style_order, player_roles)

        grouped["avg"] = grouped["runs"].astype(int).astype("object")
        out_mask = grouped["outs"] > 0
        grouped.loc[out_mask, "avg"] = (
            (grouped.loc[out_mask, "runs"] / grouped.loc[out_mask, "outs"])
            .map(self._round_one_decimal)
            .astype(float)
        )
        grouped["sr"] = np.where(
            grouped["balls"] > 0,
            (grouped["runs"] / grouped["balls"]) * 100.0,
            0.0,
        )
        grouped["sr"] = np.trunc(grouped["sr"]).astype(int)

        role_map = player_roles if isinstance(player_roles, dict) else {}
        default_role = self._default_player_role(self.rules.get("default_player_role"))
        players_df = pd.DataFrame({"player_name": players_series.astype(str)}).drop_duplicates()
        players_df["player_role"] = players_df["player_name"].map(role_map).fillna(default_role)
        styles_df = pd.DataFrame({"style_key": style_order.astype(str)})

        scaffold = (
            players_df.assign(_join_key=1)
            .merge(styles_df.assign(_join_key=1), on="_join_key", how="inner")
            .drop(columns="_join_key")
        )
        merged = scaffold.merge(
            grouped,
            left_on=["player_name", "style_key"],
            right_on=["striker", "style_key"],
            how="left",
        ).drop(columns="striker")

        by_player: Dict[str, Dict[str, object]] = {}
        for row in merged[["player_name", "player_role", "style_key", "avg", "sr"]].to_dict("records"):
            player_name = str(row["player_name"])
            player_role = str(row["player_role"])
            style_key = str(row["style_key"])
            player_key = f"{player_name}::{player_role}"

            if player_key not in by_player:
                by_player[player_key] = {
                    "player_name": player_name,
                    "player_role": player_role,
                    "style_metrics": {},
                }

            avg_raw = self._as_numeric_or_none(row.get("avg"))
            strike_rate = self._as_numeric_or_none(row.get("sr"))
            style_metrics = by_player[player_key]["style_metrics"]
            if isinstance(style_metrics, dict):
                style_metrics[style_key] = {
                    "average": avg_raw,
                    "strike_rate": int(strike_rate) if strike_rate is not None else None,
                    "average_raw": avg_raw,
                }

        return list(by_player.values())
