from typing import Dict, Optional, Union

import pandas as pd

from core.interfaces.player_interface import SquadMetrics
from core.services.squad._base import SquadServiceBase, VALID_WICKET_TYPES


class SquadMetricsCalculator(SquadServiceBase):
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

