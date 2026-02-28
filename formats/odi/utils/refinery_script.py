import os
from typing import Any, Dict, List

import numpy as np
import pandas as pd


def _safe_numeric(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(0, index=df.index, dtype="float64")
    return pd.to_numeric(df[col], errors="coerce").fillna(0)


def _bowler_wicket_mask(df: pd.DataFrame) -> pd.Series:
    if "wicket_type" not in df.columns:
        return pd.Series(False, index=df.index)
    return df["wicket_type"].notna() & (~df["wicket_type"].isin(["run out", "retired hurt", "retired out", "obstructing the field"]))


def _build_player_stats(df: pd.DataFrame, cfg: Dict[str, Any]) -> None:
    # Batting stats
    bat_base = df.groupby(["striker", "batting_team", "bowling_team"], dropna=False).agg(
        innings=("match_id", "nunique"),
        runs=("runs_off_bat", "sum"),
        balls=("match_id", "count"),
        dots=("runs_off_bat", lambda s: int((s == 0).sum())),
        fours=("runs_off_bat", lambda s: int((s == 4).sum())),
        sixes=("runs_off_bat", lambda s: int((s == 6).sum())),
    ).reset_index()

    if "player_dismissed" in df.columns:
        out_counts = (
            df[df["player_dismissed"].notna()]
            .groupby(["player_dismissed", "batting_team", "bowling_team"], dropna=False)
            .size()
            .reset_index(name="dismissals")
        )
        batting = pd.merge(
            bat_base,
            out_counts,
            left_on=["striker", "batting_team", "bowling_team"],
            right_on=["player_dismissed", "batting_team", "bowling_team"],
            how="left",
        )
        batting.drop(columns=["player_dismissed"], inplace=True)
        batting["dismissals"] = batting["dismissals"].fillna(0)
    else:
        batting = bat_base.copy()
        batting["dismissals"] = 0

    batting.rename(
        columns={
            "striker": "player",
            "batting_team": "team",
            "bowling_team": "opponent",
        },
        inplace=True,
    )
    batting["strike_rate"] = np.where(
        batting["balls"] > 0,
        (batting["runs"] / batting["balls"] * 100).round(2),
        0.0,
    )
    batting["average"] = np.where(
        batting["dismissals"] > 0,
        (batting["runs"] / batting["dismissals"]).round(2),
        batting["runs"],
    )
    batting["role"] = "batting"
    batting["context"] = "vs_team"

    batting_cols = [
        "player",
        "team",
        "opponent",
        "innings",
        "runs",
        "balls",
        "dismissals",
        "dots",
        "fours",
        "sixes",
        "strike_rate",
        "average",
        "role",
        "context",
    ]
    batting = batting[batting_cols]

    # Bowling stats
    bowl_source = df.copy()
    bowl_source["is_bowler_wicket"] = _bowler_wicket_mask(bowl_source).astype(int)
    bowl_source["legal_ball"] = ((bowl_source["wides"] == 0) & (bowl_source["noballs"] == 0)).astype(int)
    bowl_source["runs_conceded"] = bowl_source["runs_off_bat"] + bowl_source["extras"]

    bowling = bowl_source.groupby(["bowler", "bowling_team", "batting_team"], dropna=False).agg(
        innings=("match_id", "nunique"),
        runs=("runs_conceded", "sum"),
        balls=("match_id", "count"),
        legal_balls=("legal_ball", "sum"),
        dismissals=("is_bowler_wicket", "sum"),
        dots=("runs_off_bat", lambda s: int((s == 0).sum())),
        fours=("runs_off_bat", lambda s: int((s == 4).sum())),
        sixes=("runs_off_bat", lambda s: int((s == 6).sum())),
    ).reset_index()

    bowling.rename(
        columns={
            "bowler": "player",
            "bowling_team": "team",
            "batting_team": "opponent",
        },
        inplace=True,
    )
    bowling["economy"] = np.where(
        bowling["legal_balls"] > 0,
        (bowling["runs"] / bowling["legal_balls"] * 6).round(2),
        0.0,
    )
    bowling["strike_rate"] = np.where(
        bowling["dismissals"] > 0,
        (bowling["legal_balls"] / bowling["dismissals"]).round(2),
        0.0,
    )
    bowling["average"] = np.where(
        bowling["dismissals"] > 0,
        (bowling["runs"] / bowling["dismissals"]).round(2),
        bowling["runs"],
    )
    bowling["role"] = "bowling"
    bowling["context"] = "vs_team"

    bowling_cols = [
        "player",
        "team",
        "opponent",
        "innings",
        "runs",
        "balls",
        "legal_balls",
        "dismissals",
        "dots",
        "fours",
        "sixes",
        "economy",
        "strike_rate",
        "average",
        "role",
        "context",
    ]
    bowling = bowling[bowling_cols]

    # Backward-compatible combined view/table with clean common columns only.
    combined_cols = ["player", "team", "opponent", "innings", "runs", "balls", "dismissals", "role", "context"]
    combined = pd.concat([batting[combined_cols], bowling[combined_cols]], ignore_index=True)

    player_stats_file = cfg.get("player_stats_file", "processed_player_stats.csv")
    player_batting_stats_file = cfg.get("player_batting_stats_file", "processed_player_batting_stats.csv")
    player_bowling_stats_file = cfg.get("player_bowling_stats_file", "processed_player_bowling_stats.csv")
    metadata_file = cfg.get("metadata_file", "player_metadata.csv")

    batting.to_csv(player_batting_stats_file, index=False)
    bowling.to_csv(player_bowling_stats_file, index=False)
    combined.to_csv(player_stats_file, index=False)

    meta = combined[["player", "team"]].drop_duplicates()
    meta.to_csv(metadata_file, index=False)

    print(f"   Saved: {player_batting_stats_file}")
    print(f"   Saved: {player_bowling_stats_file}")
    print(f"   Saved: {player_stats_file}")
    print(f"   Saved: {metadata_file}")


def _build_phase_stats(df: pd.DataFrame, cfg: Dict[str, Any]) -> None:
    phases_cfg = cfg.get("phases", {})

    def get_phase(over_num: Any) -> str:
        try:
            over = int(pd.to_numeric(over_num, errors="coerce"))
        except (TypeError, ValueError):
            return "mid"
        for phase_id, phase_info in phases_cfg.items():
            if phase_info["start"] <= over <= phase_info["end"]:
                return phase_id
        return "mid"

    phase_df = df.copy()
    phase_df["phase"] = phase_df["over_num"].apply(get_phase)
    phase_df["total_runs"] = phase_df["runs_off_bat"] + phase_df["extras"]
    phase_df["is_wicket"] = phase_df["is_wicket"].astype(int)
    phase_df["legal_ball"] = ((phase_df["wides"] == 0) & (phase_df["noballs"] == 0)).astype(int)

    grouped = (
        phase_df.groupby(["match_id", "start_date", "venue", "innings", "batting_team", "phase"], dropna=False)
        .agg(phase_runs=("total_runs", "sum"), phase_wkts=("is_wicket", "sum"), phase_balls=("legal_ball", "sum"))
        .reset_index()
    )

    pivot = grouped.pivot_table(
        index=["match_id", "start_date", "venue", "innings", "batting_team"],
        columns="phase",
        values=["phase_runs", "phase_wkts", "phase_balls"],
        fill_value=0,
    ).reset_index()

    new_cols: List[str] = []
    for col in pivot.columns:
        if isinstance(col, tuple):
            metric, phase = col
            if not phase:
                new_cols.append(metric)
                continue
            suffix = "runs" if metric == "phase_runs" else "wkts" if metric == "phase_wkts" else "balls"
            new_cols.append(f"{phase}_{suffix}")
        else:
            new_cols.append(col)

    pivot.columns = new_cols
    pivot.rename(columns={"batting_team": "team"}, inplace=True)

    phase_stats_file = cfg.get("phase_stats_file", "processed_phase_stats.csv")
    pivot.to_csv(phase_stats_file, index=False)
    print(f"   Saved: {phase_stats_file}")


def rebuild_intelligence_layer(config: Dict[str, Any] = None) -> None:
    """
    Refines raw ball-by-ball data into player stats and phase stats.
    """
    if config is None:
        try:
            from formats.odi.config.settings import ODI_FORMAT_CONFIG

            config = ODI_FORMAT_CONFIG
        except ImportError:
            return

    cfg = config
    print(f"\nSTARTING INTELLIGENCE REFINERY [{cfg['label']}]...")

    master_file = cfg["data_file"]
    if not os.path.exists(master_file):
        print(f"CRITICAL ERROR: '{master_file}' not found.")
        return

    print(f"Loading Master Database ({os.path.basename(master_file)})...")
    df = pd.read_csv(master_file, low_memory=False)

    df["match_id"] = df["match_id"].astype(str)
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")

    for col in ["runs_off_bat", "extras", "wides", "noballs", "innings", "over_num", "ball_rank"]:
        df[col] = _safe_numeric(df, col)

    df["innings"] = df["innings"].astype(int)
    df["over_num"] = df["over_num"].astype(int)
    df["ball_rank"] = df["ball_rank"].astype(int)

    if "is_wicket" not in df.columns:
        if "wicket_type" in df.columns:
            df["is_wicket"] = df["wicket_type"].notna().astype(int)
        elif "player_dismissed" in df.columns:
            df["is_wicket"] = df["player_dismissed"].notna().astype(int)
        else:
            df["is_wicket"] = 0

    print("Building Player Profiles...")
    _build_player_stats(df, cfg)

    print("Building Phase Analysis...")
    _build_phase_stats(df, cfg)

    print(f"REFINERY COMPLETE for {cfg['label']}.")


if __name__ == "__main__":
    rebuild_intelligence_layer()
