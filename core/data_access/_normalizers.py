"""
DAL Normalizers - raw data cleaning functions applied after database fetch.
All functions are pure (no class state). Callers pass con explicitly where needed.
"""

import duckdb
import pandas as pd

from core.data_access._filters import is_blank_team, is_no_result_winner


def normalize_match_innings_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes innings columns to make downstream filters deterministic.
    """
    if df is None or df.empty:
        return df

    out = df.copy()
    numeric_cols = [
        "score_inn1",
        "score_inn2",
        "balls_inn1",
        "balls_inn2",
        "wickets_inn1",
        "wickets_inn2",
    ]
    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    if all(col in out.columns for col in ["winner", "balls_inn2", "wickets_inn2"]):
        no_result_mask = out["winner"].apply(is_no_result_winner)
        missing_inn2_mask = out["balls_inn2"].isna() & out["wickets_inn2"].isna()
        fill_mask = no_result_mask & missing_inn2_mask
        if bool(fill_mask.any()):
            out.loc[fill_mask, "balls_inn2"] = 0
            out.loc[fill_mask, "wickets_inn2"] = 0

    return out


def hydrate_missing_match_teams(df: pd.DataFrame, con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Backfills missing team_bat_1/team_bat_2 using team evidence from balls.
    """
    if df is None or df.empty:
        return df
    if "match_id" not in df.columns or "team_bat_1" not in df.columns or "team_bat_2" not in df.columns:
        return df

    missing_mask = df["team_bat_1"].apply(is_blank_team) | df["team_bat_2"].apply(is_blank_team)
    if not bool(missing_mask.any()):
        return df

    target_ids = df.loc[missing_mask, "match_id"].dropna().unique().tolist()
    if not target_ids:
        return df

    placeholders = ",".join(["?"] * len(target_ids))
    team_rows = con.execute(
        f"""
        SELECT match_id, LIST(DISTINCT team) AS teams
        FROM (
            SELECT match_id, batting_team AS team
            FROM balls
            WHERE match_id IN ({placeholders})
            UNION ALL
            SELECT match_id, bowling_team AS team
            FROM balls
            WHERE match_id IN ({placeholders})
        ) t
        WHERE team IS NOT NULL AND TRIM(CAST(team AS VARCHAR)) <> ''
        GROUP BY match_id
        """,
        target_ids + target_ids,
    ).df()

    def _normalize_team_list(teams_val) -> list[str]:
        if hasattr(teams_val, "tolist") and not isinstance(teams_val, (str, bytes)):
            teams_iter = teams_val.tolist()
        elif isinstance(teams_val, (list, tuple, set)):
            teams_iter = list(teams_val)
        else:
            teams_iter = [teams_val]
        teams = [str(t).strip() for t in teams_iter if not is_blank_team(t)]
        return sorted(set(teams))

    if team_rows.empty:
        return df

    team_rows = team_rows.copy()
    team_rows["teams_normalized"] = team_rows["teams"].apply(_normalize_team_list)
    team_lookup = team_rows.set_index("match_id")["teams_normalized"]

    out = df.copy()
    missing_out = out.loc[missing_mask].copy()
    missing_out["candidates"] = missing_out["match_id"].map(team_lookup)

    missing_out["team_1_current"] = missing_out["team_bat_1"].apply(
        lambda v: None if is_blank_team(v) else str(v).strip()
    )
    missing_out["team_2_current"] = missing_out["team_bat_2"].apply(
        lambda v: None if is_blank_team(v) else str(v).strip()
    )

    missing_out["team_1_filled"] = missing_out.apply(
        lambda row: row["team_1_current"]
        if row["team_1_current"] is not None
        else (row["candidates"][0] if isinstance(row["candidates"], list) and row["candidates"] else None),
        axis=1,
    )

    missing_out["team_2_filled"] = missing_out.apply(
        lambda row: row["team_2_current"]
        if row["team_2_current"] is not None
        else next(
            (
                cand
                for cand in (row["candidates"] if isinstance(row["candidates"], list) else [])
                if cand != row["team_1_filled"]
            ),
            None,
        ),
        axis=1,
    )

    filled_team_1 = missing_out["team_1_filled"].dropna()
    filled_team_2 = missing_out["team_2_filled"].dropna()
    if not filled_team_1.empty:
        out.loc[filled_team_1.index, "team_bat_1"] = filled_team_1
    if not filled_team_2.empty:
        out.loc[filled_team_2.index, "team_bat_2"] = filled_team_2

    return out
