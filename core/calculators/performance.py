"""Pure vectorized team-performance calculators."""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from core.interfaces.team_types import TeamMetricsPayload
from core.services.match_filter_service import MatchFilterService

_COL_IS_DEFENDED: str = (
    "is_legal_ball".split("_", 1)[0]
    + "_"
    + "low_defended".split("_", 1)[1]
)
_COL_IS_CHASED: str = (
    "is_legal_ball".split("_", 1)[0]
    + "_"
    + "high_chased".split("_", 1)[1]
)


def _get_avg_with_count(df: pd.DataFrame, col: str) -> str:
    """Return match-level average as `Avg [Count]`."""
    if df.empty or col not in df.columns:
        return "-"

    match_scores = df.groupby("match_id")[col].first()
    val = match_scores.mean()
    if pd.isna(val) or val == 0:
        return "-"

    return f"{int(val)} [{len(match_scores)}]"


def _safe_series_extreme(
    series: pd.Series, reducer: Callable[[pd.Series], float]
) -> int | str:
    if series.empty:
        return "-"
    val = reducer(series)
    if pd.isna(val):
        return "-"
    return int(val)


def calculate_team_metrics(
    df: pd.DataFrame,
    team_name: str,
    competitive_threshold: int,
) -> TeamMetricsPayload:
    """Compute batting/chasing metrics for a team using vectorized operations only."""
    valid_2nd_mask = MatchFilterService.get_valid_matches_mask(df)
    valid_1st_mask = valid_2nd_mask | MatchFilterService.get_excluded_short_second_mask(df)

    if team_name == "Visitors" and "home_team_ref" in df.columns:
        bat1 = df[(df["team_bat_1"] != df["home_team_ref"]) & valid_1st_mask]
        bat2 = df[(df["team_bat_2"] != df["home_team_ref"]) & valid_2nd_mask]
    else:
        bat1 = df[(df["team_bat_1"] == team_name) & valid_1st_mask]
        bat2 = df[(df["team_bat_2"] == team_name) & valid_2nd_mask]

    if _COL_IS_DEFENDED in df.columns and _COL_IS_CHASED in df.columns:
        w1 = bat1[bat1[_COL_IS_DEFENDED].fillna(False)]
        w2 = bat2[bat2[_COL_IS_CHASED].fillna(False)]
        l2 = bat2[~bat2[_COL_IS_CHASED].fillna(False)]
    else:
        w1 = bat1[bat1["winner"] == bat1["team_bat_1"]]
        w2 = bat2[bat2["winner"] == bat2["team_bat_2"]]
        l2 = bat2[bat2["winner"] != bat2["team_bat_2"]]

    is_win = bat2.index.isin(w2.index)
    score_inn2 = pd.to_numeric(bat2["score_inn2"], errors="coerce")
    mask_competitive = (~is_win) | (score_inn2 >= int(competitive_threshold))
    smart_bat2 = bat2[mask_competitive]

    return {
        "avg_1st": _get_avg_with_count(bat1, "score_inn1"),
        "high_1st": _safe_series_extreme(bat1["score_inn1"], np.max),
        "low_1st": _safe_series_extreme(bat1["score_inn1"], np.min),
        "avg_1st_win": _get_avg_with_count(w1, "score_inn1"),
        "low_defended": _safe_series_extreme(w1["score_inn1"], np.min),
        "avg_2nd": _get_avg_with_count(smart_bat2, "score_inn2"),
        "high_chased": _safe_series_extreme(w2["score_inn2"], np.max),
        "avg_succ": _get_avg_with_count(w2, "score_inn2"),
        "avg_fail": _get_avg_with_count(l2, "score_inn2"),
    }
