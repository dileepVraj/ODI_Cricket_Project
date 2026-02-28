"""Pure vectorized batting math utilities."""

from __future__ import annotations

import pandas as pd


def calculate_batting_metrics(balls_df: pd.DataFrame, player_name: str) -> dict[str, float | int]:
    """Calculate core batting metrics for one player from raw ball-by-ball data.

    Expected raw columns:
    - ``striker``
    - ``runs_off_bat``
    Optional columns:
    - ``player_dismissed`` (preferred for dismissals)
    - ``wicket_type`` (fallback for dismissals)
    """
    if not isinstance(player_name, str) or not player_name.strip():
        raise ValueError("player_name must be a non-empty string.")

    required_columns = {"striker", "runs_off_bat"}
    missing_columns = required_columns.difference(balls_df.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"balls_df is missing required column(s): {missing_text}")

    striker_mask = balls_df["striker"].eq(player_name)
    player_runs = pd.to_numeric(
        balls_df.loc[striker_mask, "runs_off_bat"],
        errors="coerce",
    ).fillna(0)

    runs = int(player_runs.sum())
    balls_faced = int(striker_mask.sum())
    fours = int(player_runs.eq(4).sum())
    sixes = int(player_runs.eq(6).sum())

    if "player_dismissed" in balls_df.columns:
        dismissals = int(balls_df["player_dismissed"].eq(player_name).sum())
    elif "wicket_type" in balls_df.columns:
        dismissals = int(balls_df.loc[striker_mask, "wicket_type"].notna().sum())
    else:
        dismissals = 0

    strike_rate = round((runs / balls_faced) * 100, 1) if balls_faced > 0 else 0.0
    average = round(runs / dismissals, 1) if dismissals > 0 else float(runs)

    return {
        "runs": runs,
        "balls_faced": balls_faced,
        "strike_rate": strike_rate,
        "dismissals": dismissals,
        "average": average,
        "fours": fours,
        "sixes": sixes,
    }


def calculate_squad_batting_metrics(
    balls_df: pd.DataFrame,
    squad_players: list[str],
) -> dict[str, dict[str, float | int]]:
    """Calculate batting metrics for an entire squad in one vectorized pass."""
    if not squad_players:
        return {}

    required_columns = {"striker", "runs_off_bat"}
    missing_columns = required_columns.difference(balls_df.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"balls_df is missing required column(s): {missing_text}")

    players_ordered = list(dict.fromkeys([p for p in squad_players if isinstance(p, str) and p.strip()]))
    if not players_ordered:
        return {}

    squad_balls = balls_df.loc[balls_df["striker"].isin(players_ordered), ["striker", "runs_off_bat"]].copy()
    squad_balls["runs_off_bat"] = pd.to_numeric(squad_balls["runs_off_bat"], errors="coerce").fillna(0)

    grouped = squad_balls.groupby("striker", sort=False)
    squad_stats = grouped.agg(
        runs=("runs_off_bat", "sum"),
        balls_faced=("runs_off_bat", "size"),
        fours=("runs_off_bat", lambda s: s.eq(4).sum()),
        sixes=("runs_off_bat", lambda s: s.eq(6).sum()),
    )

    if "player_dismissed" in balls_df.columns:
        dismissals = (
            balls_df.loc[balls_df["player_dismissed"].isin(players_ordered), "player_dismissed"]
            .value_counts(dropna=False)
            .rename("dismissals")
        )
    elif "wicket_type" in balls_df.columns:
        dismissal_df = balls_df.loc[balls_df["striker"].isin(players_ordered), ["striker", "wicket_type"]]
        dismissals = dismissal_df.loc[dismissal_df["wicket_type"].notna(), "striker"].value_counts().rename("dismissals")
    else:
        dismissals = pd.Series(dtype="int64", name="dismissals")

    squad_stats = squad_stats.join(dismissals, how="left").reindex(players_ordered)
    squad_stats[["runs", "balls_faced", "fours", "sixes", "dismissals"]] = (
        squad_stats[["runs", "balls_faced", "fours", "sixes", "dismissals"]].fillna(0)
    )

    squad_stats["strike_rate"] = (
        ((squad_stats["runs"] / squad_stats["balls_faced"]).where(squad_stats["balls_faced"] > 0, 0.0) * 100).round(1)
    )
    squad_stats["average"] = (squad_stats["runs"] / squad_stats["dismissals"]).round(1)
    squad_stats["average"] = squad_stats["average"].where(
        squad_stats["dismissals"] > 0,
        squad_stats["runs"].astype(float),
    )
    squad_stats["boundaries"] = squad_stats["fours"] + squad_stats["sixes"]

    int_columns = ["runs", "balls_faced", "dismissals", "fours", "sixes", "boundaries"]
    squad_stats[int_columns] = squad_stats[int_columns].astype(int)

    return squad_stats[
        ["runs", "balls_faced", "strike_rate", "dismissals", "average", "fours", "sixes", "boundaries"]
    ].to_dict(orient="index")
