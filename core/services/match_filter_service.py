"""Vectorized match filter service for quality-controlled ODI samples."""

from __future__ import annotations

from enum import IntEnum

import pandas as pd


class MatchStatus(IntEnum):
    STATUS_OK = 1
    STATUS_NR_DROP = STATUS_OK + STATUS_OK
    STATUS_SHORT_FIRST_DROP = STATUS_NR_DROP + STATUS_OK
    STATUS_SHORT_SECOND_DROP = STATUS_SHORT_FIRST_DROP + STATUS_OK
    STATUS_DROP = STATUS_SHORT_SECOND_DROP + STATUS_OK


STATUS_COLUMN = "status"


def apply_smart_filters(df: pd.DataFrame, min_balls: int) -> pd.DataFrame:
    """Apply smart quality filters to match-level innings data.

    Rules:
    1) Drop no-result/abandoned rows.
    2) Drop short first innings unless all-out.
    3) Drop short second innings unless all-out or successful chase.
    4) Keep tied no-result scorelines in STATUS_OK.
    """
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df.copy()

    work_df = df.copy()
    min_balls_for_completed_innings = int(min_balls)

    cols = work_df.columns.tolist()
    b1_col = next((c for c in cols if "ball" in c and "inn1" in c), None)
    w1_col = next((c for c in cols if "wicket" in c and "inn1" in c), None)
    b2_col = next((c for c in cols if "ball" in c and "inn2" in c), None)
    w2_col = next((c for c in cols if "wicket" in c and "inn2" in c), None)

    t2_col = next((c for c in cols if "team" in c and "bat" in c and "2" in c), "team_bat_2")

    status_ok = int(MatchStatus.STATUS_OK)
    status_nr_drop = int(MatchStatus.STATUS_NR_DROP)
    status_short_first_drop = int(MatchStatus.STATUS_SHORT_FIRST_DROP)
    status_short_second_drop = int(MatchStatus.STATUS_SHORT_SECOND_DROP)
    status_drop = int(MatchStatus.STATUS_DROP)
    work_df[STATUS_COLUMN] = status_ok

    if "winner" in work_df.columns:
        winner_text = work_df["winner"].astype(str).str.lower().str.strip()
        is_no_result = winner_text.isin(["nan", "none", "no result", "abandoned", ""])

        if "score_inn1" in work_df.columns and "score_inn2" in work_df.columns:
            score_1 = pd.to_numeric(work_df["score_inn1"], errors="coerce")
            score_2 = pd.to_numeric(work_df["score_inn2"], errors="coerce")
            is_level_no_result = is_no_result & score_1.notna() & score_2.notna() & score_1.eq(score_2)
            work_df.loc[is_level_no_result, STATUS_COLUMN] = status_ok
            is_no_result = is_no_result & (~is_level_no_result)

        work_df.loc[is_no_result, STATUS_COLUMN] = status_nr_drop

    b1 = pd.to_numeric(work_df[b1_col], errors="coerce").fillna(0) if b1_col else pd.Series(0.0, index=work_df.index)
    w1 = pd.to_numeric(work_df[w1_col], errors="coerce").fillna(0) if w1_col else pd.Series(0.0, index=work_df.index)
    b2 = pd.to_numeric(work_df[b2_col], errors="coerce").fillna(0) if b2_col else pd.Series(0.0, index=work_df.index)
    w2 = pd.to_numeric(work_df[w2_col], errors="coerce").fillna(0) if w2_col else pd.Series(0.0, index=work_df.index)

    if b1_col and w1_col:
        is_short_1 = (b1 < min_balls_for_completed_innings) & (w1 < 10)
    else:
        is_short_1 = pd.Series(False, index=work_df.index)

    if b2_col and w2_col and "winner" in cols:
        win_names = work_df["winner"].astype(str).str.lower().str.strip()
        team2_names = work_df[t2_col].astype(str).str.lower().str.strip()
        score_1 = pd.to_numeric(work_df["score_inn1"], errors="coerce").fillna(0)
        score_2 = pd.to_numeric(work_df["score_inn2"], errors="coerce").fillna(0)
        natural_win = (win_names == team2_names) & (score_2 > score_1)
        is_short_2 = (b2 < min_balls_for_completed_innings) & (w2 < 10) & (~natural_win)
    else:
        is_short_2 = pd.Series(False, index=work_df.index)

    work_df.loc[is_short_1, STATUS_COLUMN] = status_short_first_drop
    work_df.loc[is_short_2, STATUS_COLUMN] = status_short_second_drop
    work_df.loc[is_short_1 & is_short_2, STATUS_COLUMN] = status_drop

    return work_df


class MatchFilterService:
    @staticmethod
    def _status_code_series(match_df: pd.DataFrame) -> pd.Series:
        if STATUS_COLUMN not in match_df.columns:
            return pd.Series(int(MatchStatus.STATUS_OK), index=match_df.index, dtype="Int64")
        status_code = pd.to_numeric(match_df[STATUS_COLUMN], errors="coerce")
        return status_code.fillna(int(MatchStatus.STATUS_OK)).astype("Int64")

    @staticmethod
    def get_valid_matches_mask(match_df: pd.DataFrame) -> pd.Series:
        return MatchFilterService._status_code_series(match_df).eq(int(MatchStatus.STATUS_OK))

    @staticmethod
    def get_excluded_no_result_mask(match_df: pd.DataFrame) -> pd.Series:
        return MatchFilterService._status_code_series(match_df).eq(int(MatchStatus.STATUS_NR_DROP))

    @staticmethod
    def get_excluded_short_second_mask(match_df: pd.DataFrame) -> pd.Series:
        return MatchFilterService._status_code_series(match_df).eq(int(MatchStatus.STATUS_SHORT_SECOND_DROP))
