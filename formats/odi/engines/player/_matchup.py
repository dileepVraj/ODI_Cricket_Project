"""formats/odi/engines/player/_matchup — PlayerEngineMatchup: player matchup analysis."""

from typing import List, Optional

import numpy as np
import pandas as pd

from core.exceptions import ConfigurationError
from core.interfaces.serialization_types import DisplayRecord

from ._base import PlayerEngineBase, _PURE_BOWLER_ROLE, _logger


class PlayerEngineMatchup(PlayerEngineBase):
    def get_matchups(
        self,
        batter: Optional[str] = None,
        bowlers: Optional[List[str]] = None,
        *,
        home_team: Optional[str] = None,
        opp_team: Optional[str] = None,
        home_xi: Optional[List[str]] = None,
        away_xi: Optional[List[str]] = None,
        context_df: pd.DataFrame,
        venue_filtered: bool = False,
    ) -> List[DisplayRecord]:
        """
        Public dispatcher for Player Matchups.
        Single-player mode: batter is provided - delegates to _matchup_single_batter.
        Bulk mode: batter is None - iterates all non-Bowler players in home_xi against away_xi,
        returning combined rows with a leading 'Batter' key per row.
        """
        if batter:
            return self._matchup_single_batter(
                batter,
                bowlers,
                home_team=home_team,
                opp_team=opp_team,
                home_xi=home_xi,
                away_xi=away_xi,
                context_df=context_df,
                venue_filtered=venue_filtered,
            )

        home_players: List[str] = list(home_xi or [])
        away_players: List[str] = list(away_xi or [])
        if not home_players or not away_players:
            return []

        eligible_home: List[str] = [
            player_name
            for player_name in home_players
            if self._get_player_role(player_name) != _PURE_BOWLER_ROLE
        ]
        eligible_away: List[str] = [
            player_name
            for player_name in away_players
            if self._get_player_role(player_name) != _PURE_BOWLER_ROLE
        ]
        if not eligible_home and not eligible_away:
            return []

        combined: List[DisplayRecord] = []
        for player_name in eligible_home:
            rows = self._matchup_single_batter(
                player_name,
                away_players,
                home_team=home_team,
                opp_team=opp_team,
                home_xi=home_xi,
                away_xi=away_xi,
                context_df=context_df,
                venue_filtered=venue_filtered,
            )
            for row in rows:
                combined.append({"Batter": player_name, **row})
        for player_name in eligible_away:
            rows = self._matchup_single_batter(
                player_name,
                home_players,
                home_team=home_team,
                opp_team=opp_team,
                home_xi=home_xi,
                away_xi=away_xi,
                context_df=context_df,
                venue_filtered=venue_filtered,
            )
            for row in rows:
                combined.append({"Batter": player_name, **row})
        return combined

    def _compute_threat_rating(
        self,
        raw_balls: pd.Series,
        raw_outs: pd.Series,
        w_avg: pd.Series,
        w_sr: pd.Series,
        threat_min_balls: int | float,
        threat_dominant_balls: int | float,
        threat_dominant_sr: int | float,
        threat_threat_sr_outs0: int | float,
        threat_threat_avg_outs1: int | float,
        threat_threat_sr_outs1: int | float,
        threat_advantage_sr: int | float,
        threat_advantage_avg: int | float,
        threat_watchful_avg: int | float,
        threat_watchful_sr: int | float,
        threat_dominated_outs: int | float,
        threat_dominated_avg: int | float,
        threat_bunny_outs: int | float,
        threat_bunny_avg: int | float,
    ) -> pd.Series:
        conditions = [
            raw_balls == 0,
            raw_balls < float(threat_min_balls),
            (raw_outs >= float(threat_bunny_outs)) & (w_avg < float(threat_bunny_avg)),
            (raw_outs >= float(threat_dominated_outs)) & (w_avg < float(threat_dominated_avg)),
            (raw_outs >= 1) & (w_avg < float(threat_watchful_avg)) & (w_sr < float(threat_watchful_sr)),
            (raw_balls >= float(threat_dominant_balls))
            & (raw_outs == 0)
            & (w_sr > float(threat_dominant_sr)),
            (
                ((raw_outs == 0) & (w_sr > float(threat_threat_sr_outs0)))
                | (
                    (raw_outs == 1)
                    & (w_avg > float(threat_threat_avg_outs1))
                    & (w_sr > float(threat_threat_sr_outs1))
                )
            ),
            (raw_outs <= 1)
            & (w_sr > float(threat_advantage_sr))
            & ((raw_outs == 0) | (w_avg > float(threat_advantage_avg))),
        ]
        choices = [
            "NEW MATCHUP",
            "LOW DATA",
            "BUNNY",
            "DOMINATED",
            "WATCHFUL",
            "DOMINANT",
            "THREAT",
            "ADVANTAGE",
        ]
        return pd.Series(
            np.select(conditions, choices, default="CONTESTED"),
            index=raw_balls.index,
        )

    def _matchup_single_batter(
        self,
        batter: str,
        bowlers: Optional[List[str]] = None,
        *,
        home_team: Optional[str] = None,
        opp_team: Optional[str] = None,
        home_xi: Optional[List[str]] = None,
        away_xi: Optional[List[str]] = None,
        context_df: pd.DataFrame,
        venue_filtered: bool = False,
    ) -> List[DisplayRecord]:
        """
        Headless logic for Batter vs Bowlers.
        """
        threat_min_balls = self._get_tactical_threshold("threat_min_balls")
        threat_dominant_balls = self._get_tactical_threshold("threat_dominant_balls")
        threat_dominant_sr = self._get_tactical_threshold("threat_dominant_sr")
        threat_threat_sr_outs0 = self._get_tactical_threshold("threat_threat_sr_outs0")
        threat_threat_avg_outs1 = self._get_tactical_threshold("threat_threat_avg_outs1")
        threat_threat_sr_outs1 = self._get_tactical_threshold("threat_threat_sr_outs1")
        threat_advantage_sr = self._get_tactical_threshold("threat_advantage_sr")
        threat_advantage_avg = self._get_tactical_threshold("threat_advantage_avg")
        threat_watchful_avg = self._get_tactical_threshold("threat_watchful_avg")
        threat_watchful_sr = self._get_tactical_threshold("threat_watchful_sr")
        threat_dominated_outs = self._get_tactical_threshold("threat_dominated_outs")
        threat_dominated_avg = self._get_tactical_threshold("threat_dominated_avg")
        threat_bunny_outs = self._get_tactical_threshold("threat_bunny_outs")
        threat_bunny_avg = self._get_tactical_threshold("threat_bunny_avg")
        recency_w_0_12 = self._get_tactical_threshold("recency_w_0_12")
        recency_w_12_24 = self._get_tactical_threshold("recency_w_12_24")
        recency_w_24_36 = self._get_tactical_threshold("recency_w_24_36")
        recency_w_36_plus = self._get_tactical_threshold("recency_w_36_plus")
        confidence_2_min = self._get_tactical_threshold("confidence_2_min")
        confidence_3_min = self._get_tactical_threshold("confidence_3_min")
        confidence_4_min = self._get_tactical_threshold("confidence_4_min")
        confidence_5_min = self._get_tactical_threshold("confidence_5_min")
        percent_scale = float(self.rules["SPORT_CONSTANTS"]["percent_scale"])

        inferred_bowlers: List[str] = list(bowlers or [])
        home_xi = home_xi or []
        away_xi = away_xi or []

        if not inferred_bowlers:
            if home_xi and away_xi:
                if batter in home_xi:
                    inferred_bowlers = away_xi
                elif batter in away_xi:
                    inferred_bowlers = home_xi
                else:
                    inferred_bowlers = away_xi
            elif away_xi:
                inferred_bowlers = away_xi
            elif home_xi:
                inferred_bowlers = home_xi

        inferred_bowlers = sorted({
            str(name).strip()
            for name in inferred_bowlers
            if str(name).strip() and str(name).strip() != batter
        })
        if not inferred_bowlers:
            return []

        base_df = context_df
        required_cols = {"striker", "bowler", "runs_off_bat", "player_dismissed"}
        missing_required = required_cols - set(base_df.columns)
        if missing_required:
            raise ConfigurationError(
                f"context_df missing required matchup columns: {missing_required}"
            )
        optional_cols = {"over_num", "wicket_type", "start_date", "innings", "wides", "match_id"}
        missing_optional = optional_cols - set(base_df.columns)
        if missing_optional:
            _logger.warning(
                "context_df missing optional matchup columns (degraded output): %s",
                missing_optional,
            )

        batter_df = base_df[
            (base_df["striker"] == batter)
            & (base_df["bowler"].isin(inferred_bowlers))
        ].copy()
        if batter_df.empty:
            return []

        batter_df["_runs_off_bat_num"] = pd.to_numeric(
            batter_df["runs_off_bat"], errors="coerce"
        ).fillna(0.0)
        batter_df["_is_out"] = (batter_df["player_dismissed"] == batter).astype(int)

        if "start_date" not in batter_df.columns:
            batter_df["_weight"] = 1.0
        else:
            reference_date = self._get_reference_date()
            days_ago = (
                reference_date - pd.to_datetime(batter_df["start_date"], errors="coerce")
            ).dt.days
            batter_df["_weight"] = np.select(
                [
                    days_ago <= 365,
                    days_ago <= 730,
                    days_ago <= 1095,
                ],
                [
                    float(recency_w_0_12),
                    float(recency_w_12_24),
                    float(recency_w_24_36),
                ],
                default=float(recency_w_36_plus),
            ).astype(float)

        batter_df["_weighted_runs"] = batter_df["_runs_off_bat_num"] * batter_df["_weight"]
        batter_df["_weighted_outs"] = batter_df["_is_out"].astype(float) * batter_df["_weight"]

        batter_df["_is_boundary"] = (batter_df["_runs_off_bat_num"] >= 4).astype(int)
        if "wides" in batter_df.columns:
            _wides_num = pd.to_numeric(batter_df["wides"], errors="coerce").fillna(0)
            batter_df["_is_wide"] = (_wides_num > 0).astype(int)
            batter_df["_is_dot"] = (
                (batter_df["_runs_off_bat_num"] == 0) & (_wides_num == 0)
            ).astype(int)
        else:
            batter_df["_is_wide"] = 0
            batter_df["_is_dot"] = (batter_df["_runs_off_bat_num"] == 0).astype(int)

        def _aggregate_matchup_window(window_df: pd.DataFrame) -> pd.DataFrame:
            if window_df.empty:
                return pd.DataFrame(
                    columns=[
                        "Bowler",
                        "Balls",
                        "Runs",
                        "Outs",
                        "Avg",
                        "SR",
                        "ThreatRating",
                        "MatchCount",
                        "BoundaryBalls",
                        "BoundaryRate",
                        "DotBalls",
                        "DotBallRate",
                    ]
                )

            grouped = window_df.groupby("bowler", sort=True, dropna=False)
            matchup_stats = grouped.agg(
                Runs=("_runs_off_bat_num", "sum"),
                Outs=("_is_out", "sum"),
                WeightedBalls=("_weight", "sum"),
                WeightedRuns=("_weighted_runs", "sum"),
                WeightedOuts=("_weighted_outs", "sum"),
                BoundaryBalls=("_is_boundary", "sum"),
                DotBalls=("_is_dot", "sum"),
                WideBalls=("_is_wide", "sum"),
            )
            matchup_stats["Balls"] = grouped.size()
            if "match_id" in window_df.columns:
                matchup_stats["MatchCount"] = grouped["match_id"].nunique()
            else:
                matchup_stats["MatchCount"] = 0
            matchup_stats["Avg"] = np.where(
                matchup_stats["Outs"] > 0,
                matchup_stats["WeightedRuns"] / matchup_stats["WeightedOuts"],
                matchup_stats["WeightedRuns"],
            )
            matchup_stats["SR"] = np.where(
                matchup_stats["WeightedBalls"] > 0,
                (matchup_stats["WeightedRuns"] / matchup_stats["WeightedBalls"]) * percent_scale,
                0.0,
            )
            matchup_stats["ThreatRating"] = self._compute_threat_rating(
                raw_balls=matchup_stats["Balls"].astype(float),
                raw_outs=matchup_stats["Outs"].astype(float),
                w_avg=matchup_stats["Avg"].astype(float),
                w_sr=matchup_stats["SR"].astype(float),
                threat_min_balls=threat_min_balls,
                threat_dominant_balls=threat_dominant_balls,
                threat_dominant_sr=threat_dominant_sr,
                threat_threat_sr_outs0=threat_threat_sr_outs0,
                threat_threat_avg_outs1=threat_threat_avg_outs1,
                threat_threat_sr_outs1=threat_threat_sr_outs1,
                threat_advantage_sr=threat_advantage_sr,
                threat_advantage_avg=threat_advantage_avg,
                threat_watchful_avg=threat_watchful_avg,
                threat_watchful_sr=threat_watchful_sr,
                threat_dominated_outs=threat_dominated_outs,
                threat_dominated_avg=threat_dominated_avg,
                threat_bunny_outs=threat_bunny_outs,
                threat_bunny_avg=threat_bunny_avg,
            )
            matchup_stats["BoundaryRate"] = np.where(
                matchup_stats["Balls"] > 0,
                matchup_stats["BoundaryBalls"] / matchup_stats["Balls"],
                0.0,
            ).round(3)
            _dot_denom = (matchup_stats["Balls"] - matchup_stats["WideBalls"]).clip(lower=0)
            matchup_stats["DotBallRate"] = np.where(
                _dot_denom > 0,
                matchup_stats["DotBalls"] / _dot_denom,
                0.0,
            ).round(3)
            matchup_stats["Runs"] = matchup_stats["Runs"].round(0)
            matchup_stats["Avg"] = matchup_stats["Avg"].round(1)
            matchup_stats["SR"] = matchup_stats["SR"].round(1)
            return matchup_stats.reset_index().rename(columns={"bowler": "Bowler"})[
                [
                    "Bowler", "Balls", "Runs", "Outs", "Avg", "SR", "ThreatRating",
                    "MatchCount", "BoundaryBalls", "BoundaryRate", "DotBalls", "DotBallRate",
                ]
            ]

        def _build_phase_stats(phase_key: str, prefix: str, overall_df: pd.DataFrame) -> pd.DataFrame:
            phase_output = overall_df[["Bowler"]].copy()
            phase_output[f"{prefix}Balls"] = 0
            phase_output[f"{prefix}Runs"] = 0
            phase_output[f"{prefix}Outs"] = 0
            phase_output[f"{prefix}Avg"] = None
            phase_output[f"{prefix}SR"] = None
            phase_output[f"{prefix}ThreatRating"] = "NEW MATCHUP"
            phase_output[f"{prefix}MatchCount"] = 0

            phase_bounds = self.rules["phases"].get(phase_key)
            if "over_num" not in batter_df.columns or phase_bounds is None:
                return phase_output

            over_num = pd.to_numeric(batter_df["over_num"], errors="coerce")
            phase_df = batter_df[over_num.between(int(phase_bounds[0]), int(phase_bounds[1]))]
            if phase_df.empty:
                return phase_output

            _phase_agg = _aggregate_matchup_window(phase_df).rename(
                columns={
                    "Balls": f"{prefix}Balls",
                    "Runs": f"{prefix}Runs",
                    "Outs": f"{prefix}Outs",
                    "Avg": f"{prefix}Avg",
                    "SR": f"{prefix}SR",
                    "ThreatRating": f"{prefix}ThreatRating",
                    "MatchCount": f"{prefix}MatchCount",
                }
            )
            _phase_keep = [
                "Bowler",
                f"{prefix}Balls", f"{prefix}Runs", f"{prefix}Outs",
                f"{prefix}Avg", f"{prefix}SR", f"{prefix}ThreatRating",
                f"{prefix}MatchCount",
            ]
            aggregated = _phase_agg[[c for c in _phase_keep if c in _phase_agg.columns]]
            phase_output = phase_output.drop(
                columns=[
                    f"{prefix}Balls",
                    f"{prefix}Runs",
                    f"{prefix}Outs",
                    f"{prefix}Avg",
                    f"{prefix}SR",
                    f"{prefix}ThreatRating",
                    f"{prefix}MatchCount",
                ]
            ).merge(aggregated, how="left", on="Bowler")
            phase_output[f"{prefix}Balls"] = phase_output[f"{prefix}Balls"].fillna(0).astype(int)
            phase_output[f"{prefix}Runs"] = phase_output[f"{prefix}Runs"].fillna(0).astype(int)
            phase_output[f"{prefix}Outs"] = phase_output[f"{prefix}Outs"].fillna(0).astype(int)
            phase_output[f"{prefix}MatchCount"] = phase_output[f"{prefix}MatchCount"].fillna(0).astype(int)
            phase_output[f"{prefix}ThreatRating"] = (
                phase_output[f"{prefix}ThreatRating"].fillna("NEW MATCHUP").astype(str)
            )
            phase_avg = pd.to_numeric(phase_output[f"{prefix}Avg"], errors="coerce").round(1)
            phase_sr = pd.to_numeric(phase_output[f"{prefix}SR"], errors="coerce").round(1)
            phase_output[f"{prefix}Avg"] = phase_avg.where(phase_output[f"{prefix}Balls"] > 0, np.nan)
            phase_output[f"{prefix}SR"] = phase_sr.where(phase_output[f"{prefix}Balls"] > 0, np.nan)
            phase_output.loc[phase_output[f"{prefix}Balls"] == 0, f"{prefix}Avg"] = None
            phase_output.loc[phase_output[f"{prefix}Balls"] == 0, f"{prefix}SR"] = None
            return phase_output

        def _build_innings_stats(innings_num: int, prefix: str, overall_df: pd.DataFrame) -> pd.DataFrame:
            inn_output = overall_df[["Bowler"]].copy()
            inn_output[f"{prefix}Balls"] = 0
            inn_output[f"{prefix}Avg"] = None
            inn_output[f"{prefix}SR"] = None
            inn_output[f"{prefix}ThreatRating"] = "NEW MATCHUP"

            if "innings" not in batter_df.columns:
                return inn_output

            innings_col = pd.to_numeric(batter_df["innings"], errors="coerce")
            inn_df = batter_df[innings_col == innings_num]
            if inn_df.empty:
                return inn_output

            aggregated = _aggregate_matchup_window(inn_df).rename(
                columns={
                    "Balls": f"{prefix}Balls",
                    "Avg": f"{prefix}Avg",
                    "SR": f"{prefix}SR",
                    "ThreatRating": f"{prefix}ThreatRating",
                }
            )
            keep_cols = [
                "Bowler",
                f"{prefix}Balls",
                f"{prefix}Avg",
                f"{prefix}SR",
                f"{prefix}ThreatRating",
            ]
            aggregated = aggregated[[c for c in keep_cols if c in aggregated.columns]]
            inn_output = inn_output.drop(
                columns=[f"{prefix}Balls", f"{prefix}Avg", f"{prefix}SR", f"{prefix}ThreatRating"]
            ).merge(aggregated, how="left", on="Bowler")
            inn_output[f"{prefix}Balls"] = inn_output[f"{prefix}Balls"].fillna(0).astype(int)
            inn_output[f"{prefix}ThreatRating"] = (
                inn_output[f"{prefix}ThreatRating"].fillna("NEW MATCHUP").astype(str)
            )
            inn_avg = pd.to_numeric(inn_output[f"{prefix}Avg"], errors="coerce").round(1)
            inn_sr = pd.to_numeric(inn_output[f"{prefix}SR"], errors="coerce").round(1)
            inn_output[f"{prefix}Avg"] = inn_avg.where(inn_output[f"{prefix}Balls"] > 0, np.nan)
            inn_output[f"{prefix}SR"] = inn_sr.where(inn_output[f"{prefix}Balls"] > 0, np.nan)
            inn_output.loc[inn_output[f"{prefix}Balls"] == 0, f"{prefix}Avg"] = None
            inn_output.loc[inn_output[f"{prefix}Balls"] == 0, f"{prefix}SR"] = None
            return inn_output

        overall = _aggregate_matchup_window(batter_df)
        overall["Style"] = overall["Bowler"].map(self.style_map).fillna("Other")
        overall["Confidence"] = np.select(
            [
                overall["Balls"] >= float(confidence_5_min),
                overall["Balls"] >= float(confidence_4_min),
                overall["Balls"] >= float(confidence_3_min),
                overall["Balls"] >= float(confidence_2_min),
            ],
            [5, 4, 3, 2],
            default=1,
        ).astype(int)

        dismissal_stats = pd.DataFrame(
            {
                "Bowler": overall["Bowler"],
                "DismissalStructural": 0,
                "DismissalCaught": 0,
                "DismissalOther": 0,
            }
        )
        if "wicket_type" in batter_df.columns:
            dismissal_df = batter_df[batter_df["_is_out"] == 1].copy()
            if not dismissal_df.empty:
                structural_mask = dismissal_df["wicket_type"].isin(["bowled", "lbw"])
                caught_mask = dismissal_df["wicket_type"].isin(["caught", "caught and bowled"])
                dismissal_df["_dismissal_structural"] = structural_mask.astype(int)
                dismissal_df["_dismissal_caught"] = caught_mask.astype(int)
                dismissal_df["_dismissal_other"] = (~(structural_mask | caught_mask)).astype(int)
                dismissal_stats = dismissal_df.groupby("bowler", sort=True, dropna=False).agg(
                    DismissalStructural=("_dismissal_structural", "sum"),
                    DismissalCaught=("_dismissal_caught", "sum"),
                    DismissalOther=("_dismissal_other", "sum"),
                ).reset_index().rename(columns={"bowler": "Bowler"})

        result = overall[
            [
                "Bowler", "Style", "Balls", "Runs", "Outs", "Avg", "SR", "ThreatRating", "Confidence",
                "MatchCount", "BoundaryBalls", "BoundaryRate", "DotBalls", "DotBallRate",
            ]
        ].copy()
        result = result.merge(dismissal_stats, how="left", on="Bowler")

        for phase_key, prefix in (
            ("powerplay", "PP_"),
            ("middle", "Mid_"),
            ("death", "Death_"),
        ):
            result = result.merge(_build_phase_stats(phase_key, prefix, overall), how="left", on="Bowler")

        result = result.merge(_build_innings_stats(1, "Inn1_", overall), how="left", on="Bowler")
        result = result.merge(_build_innings_stats(2, "Inn2_", overall), how="left", on="Bowler")

        result["Runs"] = result["Runs"].astype(int)
        result["Balls"] = result["Balls"].astype(int)
        result["Outs"] = result["Outs"].astype(int)
        result["Avg"] = pd.to_numeric(result["Avg"], errors="coerce").round(1).astype(float)
        result["SR"] = pd.to_numeric(result["SR"], errors="coerce").round(1).astype(float)
        result["ThreatRating"] = result["ThreatRating"].astype(str)
        result["Confidence"] = result["Confidence"].astype(int)
        result["MatchCount"] = result["MatchCount"].fillna(0).astype(int)
        result["BoundaryBalls"] = result["BoundaryBalls"].fillna(0).astype(int)
        result["BoundaryRate"] = pd.to_numeric(result["BoundaryRate"], errors="coerce").fillna(0.0).round(3)
        result["DotBalls"] = result["DotBalls"].fillna(0).astype(int)
        result["DotBallRate"] = pd.to_numeric(result["DotBallRate"], errors="coerce").fillna(0.0).round(3)
        result["DismissalStructural"] = result["DismissalStructural"].fillna(0).astype(int)
        result["DismissalCaught"] = result["DismissalCaught"].fillna(0).astype(int)
        result["DismissalOther"] = result["DismissalOther"].fillna(0).astype(int)
        result["PP_MatchCount"] = result["PP_MatchCount"].fillna(0).astype(int)
        result["Mid_MatchCount"] = result["Mid_MatchCount"].fillna(0).astype(int)
        result["Death_MatchCount"] = result["Death_MatchCount"].fillna(0).astype(int)
        result["Inn1_Balls"] = result["Inn1_Balls"].fillna(0).astype(int)
        result["Inn2_Balls"] = result["Inn2_Balls"].fillna(0).astype(int)
        result["VenueFiltered"] = bool(venue_filtered)

        return result[
            [
                "Bowler",
                "Style",
                "Balls",
                "Runs",
                "Outs",
                "Avg",
                "SR",
                "ThreatRating",
                "Confidence",
                "MatchCount",
                "BoundaryBalls",
                "BoundaryRate",
                "DotBalls",
                "DotBallRate",
                "DismissalStructural",
                "DismissalCaught",
                "DismissalOther",
                "PP_Balls",
                "PP_Runs",
                "PP_Outs",
                "PP_Avg",
                "PP_SR",
                "PP_ThreatRating",
                "PP_MatchCount",
                "Mid_Balls",
                "Mid_Runs",
                "Mid_Outs",
                "Mid_Avg",
                "Mid_SR",
                "Mid_ThreatRating",
                "Mid_MatchCount",
                "Death_Balls",
                "Death_Runs",
                "Death_Outs",
                "Death_Avg",
                "Death_SR",
                "Death_ThreatRating",
                "Death_MatchCount",
                "Inn1_Balls",
                "Inn1_Avg",
                "Inn1_SR",
                "Inn1_ThreatRating",
                "Inn2_Balls",
                "Inn2_Avg",
                "Inn2_SR",
                "Inn2_ThreatRating",
                "VenueFiltered",
            ]
        ].to_dict("records")
