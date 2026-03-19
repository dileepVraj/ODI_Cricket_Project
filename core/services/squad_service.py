from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

from core.interfaces.player_interface import SquadMetrics

from core.interfaces.team_types import FormatRulesMap, SquadBulkMetricsResult


VALID_WICKET_TYPES = (
    "bowled",
    "caught",
    "lbw",
    "stumped",
    "caught and bowled",
    "hit wicket",
)


class SquadService:
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

    @staticmethod
    def _calculate_squad_metrics(
        base_df: pd.DataFrame,
        players: pd.Series,
        squad_batting_metrics: Optional[Dict[str, Dict[str, Union[int, float]]]] = None,
    ) -> SquadMetrics:
        if base_df.empty or players.empty:
            return SquadMetrics(0, 0, 0, 0, 0, 0, 0)

        player_index = pd.Index(players.astype(str), name="player")
        bat_df = base_df[base_df["striker"].isin(player_index)] if "striker" in base_df.columns else pd.DataFrame()
        bowl_df = base_df[base_df["bowler"].isin(player_index)] if "bowler" in base_df.columns else pd.DataFrame()

        if squad_batting_metrics and isinstance(squad_batting_metrics, dict):
            squad_bat_df = pd.DataFrame.from_dict(squad_batting_metrics, orient="index")
            squad_bat_df.index = squad_bat_df.index.astype(str)
            total_runs = int(pd.to_numeric(squad_bat_df.reindex(player_index)["runs"], errors="coerce").fillna(0).sum())
        else:
            total_runs = (
                int(pd.to_numeric(bat_df["runs_off_bat"], errors="coerce").fillna(0).sum())
                if not bat_df.empty and "runs_off_bat" in bat_df.columns
                else 0
            )

        if not bat_df.empty and "match_id" in bat_df.columns:
            bat_scores = (
                pd.to_numeric(bat_df["runs_off_bat"], errors="coerce")
                .fillna(0)
                .groupby([bat_df["striker"], bat_df["match_id"]])
                .sum()
            )
            centuries = int((bat_scores >= 100).sum())
            fifties = int(((bat_scores >= 50) & (bat_scores < 100)).sum())
        else:
            centuries = 0
            fifties = 0

        if not bowl_df.empty and "wicket_type" in bowl_df.columns:
            valid_wkts = bowl_df[bowl_df["wicket_type"].isin(VALID_WICKET_TYPES)]
            wickets = int(len(valid_wkts))
            five_wkt_hauls = (
                int((valid_wkts.groupby(["bowler", "match_id"]).size() >= 5).sum())
                if not valid_wkts.empty and "match_id" in valid_wkts.columns
                else 0
            )
        else:
            wickets = 0
            five_wkt_hauls = 0

        bat_caps = (
            bat_df[["match_id", "striker"]].rename(columns={"striker": "player"})
            if not bat_df.empty and {"match_id", "striker"}.issubset(bat_df.columns)
            else pd.DataFrame(columns=["match_id", "player"])
        )
        bowl_caps = (
            bowl_df[["match_id", "bowler"]].rename(columns={"bowler": "player"})
            if not bowl_df.empty and {"match_id", "bowler"}.issubset(bowl_df.columns)
            else pd.DataFrame(columns=["match_id", "player"])
        )
        caps = int(len(pd.concat([bat_caps, bowl_caps], ignore_index=True).drop_duplicates()))
        avg_caps = int(caps / len(player_index)) if len(player_index) > 0 else 0

        return SquadMetrics(
            caps=caps,
            runs=total_runs,
            centuries=centuries,
            fifties=fifties,
            wickets=wickets,
            five_wkt_hauls=five_wkt_hauls,
            avg_caps=avg_caps,
        )

    def _build_bulk_player_stats(
        self,
        base_df: pd.DataFrame,
        players: pd.Series,
        opposition: str,
        venue_pattern: str,
        player_roles: Optional[Dict[str, str]] = None,
        squad_batting_metrics: Optional[Dict[str, Dict[str, Union[int, float]]]] = None,
        form_window_matches: Optional[int] = None,
    ) -> List[Dict[str, Union[str, int, float, bool, List[Optional[str]], None]]]:
        if base_df.empty or players.empty:
            return self._empty_player_records(players, player_roles)

        player_index = pd.Index(players.astype(str), name="player")
        role_map = player_roles if isinstance(player_roles, dict) else {}
        default_role = self._default_player_role()

        bat_df = base_df[base_df["striker"].isin(player_index)] if "striker" in base_df.columns else pd.DataFrame()
        bowl_df = base_df[base_df["bowler"].isin(player_index)] if "bowler" in base_df.columns else pd.DataFrame()

        players_df = pd.DataFrame({"player_name": player_index.astype(str)})
        players_df["player_role"] = players_df["player_name"].map(role_map).fillna(default_role)

        innings_series = (
            bat_df.groupby("striker")["match_id"].nunique().reindex(player_index).fillna(0).astype(int)
            if not bat_df.empty and "match_id" in bat_df.columns
            else pd.Series(0, index=player_index, dtype="int64")
        )

        if squad_batting_metrics and isinstance(squad_batting_metrics, dict):
            squad_bat_df = pd.DataFrame.from_dict(squad_batting_metrics, orient="index")
            squad_bat_df.index = squad_bat_df.index.astype(str)
            runs_series = pd.to_numeric(squad_bat_df.reindex(player_index)["runs"], errors="coerce").fillna(0)
            dismissals_series = pd.to_numeric(
                squad_bat_df.reindex(player_index)["dismissals"],
                errors="coerce",
            ).fillna(0)
        else:
            runs_series = (
                pd.to_numeric(bat_df["runs_off_bat"], errors="coerce")
                .fillna(0)
                .groupby(bat_df["striker"])
                .sum()
                .reindex(player_index)
                .fillna(0)
            ) if not bat_df.empty and "runs_off_bat" in bat_df.columns else pd.Series(0, index=player_index, dtype="float64")
            if "player_dismissed" in base_df.columns:
                dismissals_series = (
                    base_df[base_df["player_dismissed"].isin(player_index)]["player_dismissed"]
                    .value_counts()
                    .reindex(player_index)
                    .fillna(0)
                )
            elif "wicket_type" in bat_df.columns:
                dismissals_series = (
                    bat_df[bat_df["wicket_type"].notna()]
                    .groupby("striker")
                    .size()
                    .reindex(player_index)
                    .fillna(0)
                )
            else:
                dismissals_series = pd.Series(0, index=player_index, dtype="float64")

        batting_avg_series = runs_series.astype(int).astype("object")
        dismissal_mask = dismissals_series > 0
        batting_avg_series.loc[dismissal_mask] = (
            (runs_series.loc[dismissal_mask] / dismissals_series.loc[dismissal_mask])
            .map(SquadService._round_one_decimal)
            .astype(float)
        )

        all_activity_frames = []
        if not bat_df.empty and {"striker", "match_id"}.issubset(bat_df.columns):
            all_activity_frames.append(
                bat_df[["striker", "match_id"] + (["start_date"] if "start_date" in bat_df.columns else [])]
                .rename(columns={"striker": "player"})
            )
        if not bowl_df.empty and {"bowler", "match_id"}.issubset(bowl_df.columns):
            all_activity_frames.append(
                bowl_df[["bowler", "match_id"] + (["start_date"] if "start_date" in bowl_df.columns else [])]
                .rename(columns={"bowler": "player"})
            )
        all_activity = (
            pd.concat(all_activity_frames, ignore_index=True).drop_duplicates(["player", "match_id"])
            if all_activity_frames
            else pd.DataFrame(columns=["player", "match_id", "start_date"])
        )
        if "start_date" not in all_activity.columns:
            all_activity["start_date"] = pd.NaT
        all_activity = all_activity.sort_values(
            ["player", "start_date", "match_id"],
            ascending=[True, False, False],
            na_position="last",
        )
        all_activity["rank"] = all_activity.groupby("player").cumcount() + 1
        threshold_window = self._get_tactical_threshold("form_window_matches", 1)
        window_size = max(1, int(form_window_matches or threshold_window))
        last_window_grid = all_activity[all_activity["rank"] <= window_size][["player", "match_id", "rank"]]

        if not bat_df.empty:
            bat_form_df = bat_df.copy()
            bat_form_df["runs_num"] = pd.to_numeric(bat_form_df["runs_off_bat"], errors="coerce").fillna(0)
            bat_form_df["is_out"] = (
                bat_form_df["wicket_type"].notna().astype(int)
                if "wicket_type" in bat_form_df.columns
                else 0
            )
            bat_match = (
                bat_form_df.groupby(["striker", "match_id"])
                .agg(runs=("runs_num", "sum"), is_out=("is_out", "max"))
                .reset_index()
                .rename(columns={"striker": "player"})
            )
            bat_join = last_window_grid.merge(bat_match, on=["player", "match_id"], how="left")
            bat_runs_text = bat_join["runs"].fillna(0).astype(int).astype(str)
            bat_join["entry"] = np.where(
                bat_join["runs"].notna(),
                np.where(bat_join["is_out"].fillna(0).astype(int).eq(1), bat_runs_text, bat_runs_text + "*"),
                None,
            )
            bat_form_series = (
                bat_join.sort_values(["player", "rank"])
                .groupby("player")["entry"]
                .agg(lambda values: [item if item is not None else None for item in values.tolist()])
                .reindex(player_index)
            )
        else:
            bat_form_series = pd.Series([[] for _ in range(len(player_index))], index=player_index, dtype="object")

        if not bowl_df.empty:
            bowl_form_df = bowl_df.copy()
            bowl_form_df["runs_num"] = pd.to_numeric(bowl_form_df["runs_off_bat"], errors="coerce").fillna(0)
            bowl_form_df["wides_num"] = (
                pd.to_numeric(bowl_form_df["wides"], errors="coerce").fillna(0)
                if "wides" in bowl_form_df.columns
                else 0
            )
            bowl_form_df["noballs_num"] = (
                pd.to_numeric(bowl_form_df["noballs"], errors="coerce").fillna(0)
                if "noballs" in bowl_form_df.columns
                else 0
            )
            bowl_form_df["is_wkt"] = (
                bowl_form_df["wicket_type"].isin(VALID_WICKET_TYPES).astype(int)
                if "wicket_type" in bowl_form_df.columns
                else 0
            )
            bowl_form_df["legal_ball"] = ((bowl_form_df["wides_num"] == 0) & (bowl_form_df["noballs_num"] == 0)).astype(int)
            bowl_form_df["total_runs"] = bowl_form_df["runs_num"] + bowl_form_df["wides_num"] + bowl_form_df["noballs_num"]

            bowl_match = (
                bowl_form_df.groupby(["bowler", "match_id"])
                .agg(
                    wkts=("is_wkt", "sum"),
                    total_runs=("total_runs", "sum"),
                    legal_balls=("legal_ball", "sum"),
                )
                .reset_index()
                .rename(columns={"bowler": "player"})
            )
            bowl_join = last_window_grid.merge(bowl_match, on=["player", "match_id"], how="left")
            legal_balls = bowl_join["legal_balls"].fillna(0).astype(int)
            overs = legal_balls // 6
            balls = legal_balls % 6
            overs_text = np.where(balls > 0, overs.astype(str) + "." + balls.astype(str), overs.astype(str))
            bowl_join["entry"] = np.where(
                bowl_join["legal_balls"].notna(),
                bowl_join["wkts"].fillna(0).astype(int).astype(str)
                + "/"
                + bowl_join["total_runs"].fillna(0).astype(int).astype(str)
                + " ("
                + overs_text
                + ")",
                None,
            )
            bowl_form_series = (
                bowl_join.sort_values(["player", "rank"])
                .groupby("player")["entry"]
                .agg(lambda values: [item if item is not None else None for item in values.tolist()])
                .reindex(player_index)
            )
        else:
            bowl_form_series = pd.Series([[] for _ in range(len(player_index))], index=player_index, dtype="object")

        if "bowling_team" in bat_df.columns:
            opp_bat_df = bat_df[bat_df["bowling_team"] == opposition]
            opp_runs_series = (
                pd.to_numeric(opp_bat_df["runs_off_bat"], errors="coerce")
                .fillna(0)
                .groupby(opp_bat_df["striker"])
                .sum()
                .reindex(player_index)
            ).fillna(0)
            if "player_dismissed" in base_df.columns and "bowling_team" in base_df.columns:
                opp_outs_series = (
                    base_df[
                        base_df["player_dismissed"].isin(player_index)
                        & base_df["bowling_team"].eq(opposition)
                    ]["player_dismissed"]
                    .value_counts()
                    .reindex(player_index)
                    .fillna(0)
                )
            elif "wicket_type" in opp_bat_df.columns:
                opp_outs_series = (
                    opp_bat_df[opp_bat_df["wicket_type"].notna()]
                    .groupby("striker")
                    .size()
                    .reindex(player_index)
                    .fillna(0)
                )
            else:
                opp_outs_series = pd.Series(0, index=player_index, dtype="float64")
            opp_avg_series = pd.Series(np.nan, index=player_index, dtype="object")
            opp_out_mask = opp_outs_series > 0
            opp_avg_series.loc[opp_out_mask] = (
                (opp_runs_series.loc[opp_out_mask] / opp_outs_series.loc[opp_out_mask])
                .map(SquadService._round_one_decimal)
                .astype(float)
            )
            no_opp_outs_with_runs_mask = (~opp_out_mask) & opp_runs_series.gt(0)
            opp_avg_series.loc[no_opp_outs_with_runs_mask] = (
                opp_runs_series.loc[no_opp_outs_with_runs_mask]
                .astype(int)
                .astype(object)
            )
        else:
            opp_avg_series = pd.Series(np.nan, index=player_index, dtype="object")

        venue_mask_all = (
            base_df["venue"].astype(str).str.contains(venue_pattern, case=False, na=False)
            if ("venue" in base_df.columns and venue_pattern)
            else pd.Series(False, index=base_df.index)
        )
        ven_bat_df = bat_df[bat_df["venue"].astype(str).str.contains(venue_pattern, case=False, na=False)] if ("venue" in bat_df.columns and venue_pattern) else pd.DataFrame()
        if not ven_bat_df.empty:
            ven_match_scores = (
                pd.to_numeric(ven_bat_df["runs_off_bat"], errors="coerce")
                .fillna(0)
                .groupby([ven_bat_df["striker"], ven_bat_df["match_id"]])
                .sum()
            )
            ven_inns_series = ven_match_scores.groupby(level=0).size().reindex(player_index)
            ven_runs_series = ven_match_scores.groupby(level=0).sum().reindex(player_index)
            ven_hs_series = ven_match_scores.groupby(level=0).max().reindex(player_index)
            ven_outs_series = (
                ven_bat_df.groupby("striker")["wicket_type"].count().reindex(player_index).fillna(0)
                if "wicket_type" in ven_bat_df.columns
                else pd.Series(0, index=player_index, dtype="float64")
            )
            ven_avg_series = pd.Series(np.nan, index=player_index, dtype="object")
            ven_out_mask = ven_outs_series > 0
            ven_avg_series.loc[ven_out_mask] = (
                (ven_runs_series.fillna(0).loc[ven_out_mask] / ven_outs_series.loc[ven_out_mask])
                .map(SquadService._round_one_decimal)
                .astype(float)
            )
            ven_no_outs_mask = (~ven_out_mask) & ven_runs_series.notna()
            ven_avg_series.loc[ven_no_outs_mask] = (
                ven_runs_series.loc[ven_no_outs_mask]
                .astype(int)
                .astype(object)
            )
        else:
            ven_inns_series = pd.Series(np.nan, index=player_index)
            ven_runs_series = pd.Series(np.nan, index=player_index)
            ven_hs_series = pd.Series(np.nan, index=player_index)
            ven_avg_series = pd.Series(np.nan, index=player_index)

        venue_activity_df = base_df[venue_mask_all] if "venue" in base_df.columns else pd.DataFrame()
        venue_activity_players = (
            pd.concat(
                [
                    venue_activity_df.loc[venue_activity_df["striker"].isin(player_index), "striker"]
                    if "striker" in venue_activity_df.columns
                    else pd.Series(dtype="string"),
                    venue_activity_df.loc[venue_activity_df["bowler"].isin(player_index), "bowler"]
                    if "bowler" in venue_activity_df.columns
                    else pd.Series(dtype="string"),
                ],
                ignore_index=True,
            )
            .dropna()
            .astype(str)
            .drop_duplicates()
        )
        ven_runs_display = pd.Series(np.nan, index=player_index, dtype="object")
        ven_runs_display.loc[ven_runs_series.dropna().index] = ven_runs_series.dropna().astype(int).astype(object)
        venue_activity_index = pd.Index(venue_activity_players, dtype="object")
        ven_runs_display.loc[venue_activity_index[~venue_activity_index.isin(ven_runs_series.dropna().index)]] = None

        if not bowl_df.empty:
            bowl_career_df = bowl_df.copy()
            bowl_career_df["runs_num"] = pd.to_numeric(bowl_career_df["runs_off_bat"], errors="coerce").fillna(0)
            bowl_career_df["wides_num"] = (
                pd.to_numeric(bowl_career_df["wides"], errors="coerce").fillna(0)
                if "wides" in bowl_career_df.columns
                else 0
            )
            bowl_career_df["noballs_num"] = (
                pd.to_numeric(bowl_career_df["noballs"], errors="coerce").fillna(0)
                if "noballs" in bowl_career_df.columns
                else 0
            )
            bowl_career_df["legal_ball"] = ((bowl_career_df["wides_num"] == 0) & (bowl_career_df["noballs_num"] == 0)).astype(int)
            bowl_career_df["total_runs"] = bowl_career_df["runs_num"] + bowl_career_df["wides_num"] + bowl_career_df["noballs_num"]

            bowl_career_group = bowl_career_df.groupby("bowler").agg(
                legal_balls=("legal_ball", "sum"),
                total_runs=("total_runs", "sum"),
            )
            bowl_econ_series = pd.Series(np.nan, index=bowl_career_group.index, dtype="float64")
            bowl_legal_mask = bowl_career_group["legal_balls"] > 0
            bowl_econ_series.loc[bowl_legal_mask] = (
                (
                    bowl_career_group.loc[bowl_legal_mask, "total_runs"]
                    / bowl_career_group.loc[bowl_legal_mask, "legal_balls"]
                )
                .mul(6)
                .map(SquadService._round_two_decimals)
                .astype(float)
            )
            bowl_econ_series = bowl_econ_series.reindex(player_index)
        else:
            bowl_econ_series = pd.Series(np.nan, index=player_index)

        ven_bowl_df = bowl_df[bowl_df["venue"].astype(str).str.contains(venue_pattern, case=False, na=False)] if ("venue" in bowl_df.columns and venue_pattern) else pd.DataFrame()
        if not ven_bowl_df.empty:
            ven_bowl_calc = ven_bowl_df.copy()
            ven_bowl_calc["runs_num"] = pd.to_numeric(ven_bowl_calc["runs_off_bat"], errors="coerce").fillna(0)
            ven_bowl_calc["wides_num"] = (
                pd.to_numeric(ven_bowl_calc["wides"], errors="coerce").fillna(0)
                if "wides" in ven_bowl_calc.columns
                else 0
            )
            ven_bowl_calc["noballs_num"] = (
                pd.to_numeric(ven_bowl_calc["noballs"], errors="coerce").fillna(0)
                if "noballs" in ven_bowl_calc.columns
                else 0
            )
            ven_bowl_calc["legal_ball"] = ((ven_bowl_calc["wides_num"] == 0) & (ven_bowl_calc["noballs_num"] == 0)).astype(int)
            ven_bowl_calc["total_runs"] = ven_bowl_calc["runs_num"] + ven_bowl_calc["wides_num"] + ven_bowl_calc["noballs_num"]
            ven_bowl_calc["is_wkt"] = (
                ven_bowl_calc["wicket_type"].isin(VALID_WICKET_TYPES).astype(int)
                if "wicket_type" in ven_bowl_calc.columns
                else 0
            )
            ven_bowl_group = ven_bowl_calc.groupby("bowler").agg(
                legal_balls=("legal_ball", "sum"),
                total_runs=("total_runs", "sum"),
                wickets=("is_wkt", "sum"),
                matches=("match_id", "nunique"),
            )
            ven_econ_series = pd.Series(np.nan, index=ven_bowl_group.index, dtype="float64")
            ven_legal_mask = ven_bowl_group["legal_balls"] > 0
            ven_econ_series.loc[ven_legal_mask] = (
                (
                    ven_bowl_group.loc[ven_legal_mask, "total_runs"]
                    / ven_bowl_group.loc[ven_legal_mask, "legal_balls"]
                )
                .mul(6)
                .map(SquadService._round_two_decimals)
                .astype(float)
            )
            ven_econ_series = ven_econ_series.reindex(player_index)
            ven_wkts_series = ven_bowl_group["wickets"].reindex(player_index)
            ven_matches_series = ven_bowl_group["matches"].reindex(player_index)
        else:
            ven_econ_series = pd.Series(np.nan, index=player_index)
            ven_wkts_series = pd.Series(np.nan, index=player_index)
            ven_matches_series = pd.Series(np.nan, index=player_index)

        output_df = players_df.copy()
        output_df["innings"] = output_df["player_name"].map(innings_series).fillna(0).astype(int)
        output_df["batting_form"] = output_df["player_name"].map(bat_form_series).apply(
            lambda value: value if isinstance(value, list) else []
        )
        output_df["batting_average"] = output_df["player_name"].map(batting_avg_series)
        output_df.loc[output_df["innings"] <= 0, "batting_average"] = None
        output_df["vs_opposition_average"] = output_df["player_name"].map(opp_avg_series)
        output_df["venue_innings"] = output_df["player_name"].map(ven_inns_series)
        output_df["venue_runs"] = output_df["player_name"].map(ven_runs_display)
        output_df["venue_average"] = output_df["player_name"].map(ven_avg_series)
        output_df["venue_high_score"] = output_df["player_name"].map(ven_hs_series)
        output_df["bowling_form"] = output_df["player_name"].map(bowl_form_series).apply(
            lambda value: value if isinstance(value, list) else []
        )
        output_df["bowling_economy"] = output_df["player_name"].map(bowl_econ_series)
        output_df["venue_economy"] = output_df["player_name"].map(ven_econ_series)
        output_df["venue_wickets"] = output_df["player_name"].map(ven_wkts_series)
        output_df["venue_matches"] = output_df["player_name"].map(ven_matches_series)

        venue_activity_flags = pd.Series(False, index=player_index, dtype="bool")
        venue_activity_flags.loc[venue_activity_index[venue_activity_index.isin(player_index)]] = True
        output_df["venue_batting_activity"] = output_df["player_name"].map(venue_activity_flags).fillna(False).astype(bool)

        output_df = output_df.where(pd.notna(output_df), None)
        return output_df.head(500).to_dict("records")

    def get_bulk_metrics(
        self,
        base_df: pd.DataFrame,
        player_ids: List[str],
        opposition: str,
        venue_pattern: str,
        player_roles: Optional[Dict[str, str]] = None,
        squad_batting_metrics: Optional[Dict[str, Dict[str, Union[int, float]]]] = None,
    ) -> SquadBulkMetricsResult:
        """
        Compute squad metrics and player stats for a full XI in a single vectorized pass.
        """
        players = self._normalize_players(player_ids)
        normalized_df = self._normalize_base_df(base_df)
        form_window_matches = self._get_tactical_threshold("form_window_matches", 1)

        squad_metrics = self._calculate_squad_metrics(
            normalized_df,
            players,
            squad_batting_metrics=squad_batting_metrics,
        )
        player_stats = self._build_bulk_player_stats(
            normalized_df,
            players,
            opposition=opposition,
            venue_pattern=venue_pattern,
            player_roles=player_roles,
            squad_batting_metrics=squad_batting_metrics,
            form_window_matches=form_window_matches,
        )
        return {
            "squad_metrics": squad_metrics,
            "player_stats": player_stats,
        }
