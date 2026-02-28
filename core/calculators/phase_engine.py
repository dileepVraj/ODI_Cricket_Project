"""Pure vectorized phase-analysis calculators."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from core.interfaces.team_types import (
    PhasePayload,
    ScenarioRow,
    ScenarioRows,
)

_CANONICAL_PHASE_IDS: Tuple[str, str, str] = ("pp", "mid", "dth")
_PHASE_KEY_ALIASES = {
    "pp": "pp",
    "powerplay": "pp",
    "mid": "mid",
    "middle": "mid",
    "dth": "dth",
    "death": "dth",
}


def _parse_phase_bounds(
    bounds: Union[
        Dict[str, int],
        List[int],
        Tuple[int, int],
        None,
    ]
) -> Optional[Tuple[int, int]]:
    if isinstance(bounds, dict):
        start = pd.to_numeric(bounds.get("start"), errors="coerce")
        end = pd.to_numeric(bounds.get("end"), errors="coerce")
    elif isinstance(bounds, (list, tuple)) and len(bounds) >= 2:
        start = pd.to_numeric(bounds[0], errors="coerce")
        end = pd.to_numeric(bounds[1], errors="coerce")
    else:
        return None

    if pd.isna(start) or pd.isna(end):
        return None

    start_over = int(start)
    end_over = int(end)
    if end_over < start_over:
        return None
    return start_over, end_over


def _resolve_phase_bounds(phase_config: Dict[str, List[int]]) -> Dict[str, Tuple[int, int]]:
    if not isinstance(phase_config, dict):
        return {}

    resolved: Dict[str, Tuple[int, int]] = {}
    fallback_order = list(_CANONICAL_PHASE_IDS)
    fallback_idx = 0

    for raw_key, raw_bounds in phase_config.items():
        parsed_bounds = _parse_phase_bounds(raw_bounds)
        if parsed_bounds is None:
            continue

        key_norm = str(raw_key).strip().lower()
        canonical = _PHASE_KEY_ALIASES.get(key_norm)
        if canonical is None:
            while fallback_idx < len(fallback_order) and fallback_order[fallback_idx] in resolved:
                fallback_idx += 1
            if fallback_idx >= len(fallback_order):
                continue
            canonical = fallback_order[fallback_idx]

        if canonical not in resolved:
            resolved[canonical] = parsed_bounds

    if not all(phase_id in resolved for phase_id in _CANONICAL_PHASE_IDS):
        return {}
    return resolved


def _default_payload() -> PhasePayload:
    return {
        "phase_df": pd.DataFrame(),
        "phase_bounds": {},
        "phase_overs": {"pp": 0.0, "mid": 0.0, "dth": 0.0},
    }


def _ensure_phase_metric_columns(df: pd.DataFrame) -> pd.DataFrame:
    work_df = df.copy()
    for phase_id in _CANONICAL_PHASE_IDS:
        for metric in ("runs", "wkts", "balls"):
            col = f"{phase_id}_{metric}"
            if col not in work_df.columns:
                work_df[col] = 0
            work_df[col] = pd.to_numeric(work_df[col], errors="coerce").fillna(0)

    if "total_runs" not in work_df.columns:
        work_df["total_runs"] = work_df["pp_runs"] + work_df["mid_runs"] + work_df["dth_runs"]
    else:
        work_df["total_runs"] = pd.to_numeric(work_df["total_runs"], errors="coerce").fillna(0)

    if "innings" in work_df.columns:
        work_df["innings"] = pd.to_numeric(work_df["innings"], errors="coerce")
        work_df = work_df[work_df["innings"].notna()].copy()
        if not work_df.empty:
            work_df["innings"] = work_df["innings"].astype(int)

    return work_df


def calculate_phase_breakdown(
    ball_df: pd.DataFrame,
    phase_config: Dict[str, List[int]],
) -> PhasePayload:
    """Normalize phase data into wide `pp/mid/dth` metrics using runtime phase config."""
    if ball_df is None or ball_df.empty:
        return _default_payload()

    phase_bounds = _resolve_phase_bounds(phase_config)
    if not phase_bounds:
        return _default_payload()

    phase_overs = {
        phase_id: float((phase_bounds[phase_id][1] - phase_bounds[phase_id][0]) + 1)
        for phase_id in _CANONICAL_PHASE_IDS
    }

    phase_df = ball_df.copy()
    if "match_id" in phase_df.columns:
        phase_df["match_id"] = phase_df["match_id"].astype(str).str.split(".").str[0].str.strip()

    required_phase_cols = [f"{phase_id}_runs" for phase_id in _CANONICAL_PHASE_IDS]
    has_phase_wide = all(col in phase_df.columns for col in required_phase_cols)

    if (not has_phase_wide) and {"match_id", "innings", "over_num"}.issubset(phase_df.columns):
        work = phase_df.copy()
        work["over_num"] = pd.to_numeric(work["over_num"], errors="coerce")
        work = work[work["over_num"].notna()].copy()
        if work.empty:
            return _default_payload()
        work["over_num"] = work["over_num"].astype(int)

        conditions = []
        labels: List[str] = []
        for phase_id in _CANONICAL_PHASE_IDS:
            start_over, end_over = phase_bounds[phase_id]
            conditions.append(work["over_num"].between(start_over, end_over, inclusive="both"))
            labels.append(phase_id)

        work["phase_bucket"] = np.select(conditions, labels, default="")
        work = work[work["phase_bucket"] != ""].copy()
        if work.empty:
            return _default_payload()

        runs_off_bat = (
            pd.to_numeric(work["runs_off_bat"], errors="coerce").fillna(0)
            if "runs_off_bat" in work.columns
            else pd.Series(0.0, index=work.index)
        )
        extras = (
            pd.to_numeric(work["extras"], errors="coerce").fillna(0)
            if "extras" in work.columns
            else pd.Series(0.0, index=work.index)
        )
        work["phase_runs"] = runs_off_bat + extras

        if "wicket_type" in work.columns:
            work["phase_wkts"] = work["wicket_type"].notna().astype(int)
        elif "player_dismissed" in work.columns:
            work["phase_wkts"] = work["player_dismissed"].notna().astype(int)
        else:
            work["phase_wkts"] = 0

        if "wides" in work.columns and "noballs" in work.columns:
            wides = pd.to_numeric(work["wides"], errors="coerce").fillna(0)
            noballs = pd.to_numeric(work["noballs"], errors="coerce").fillna(0)
            work["phase_balls"] = ((wides == 0) & (noballs == 0)).astype(int)
        else:
            work["phase_balls"] = 1

        team_col = "team" if "team" in work.columns else ("batting_team" if "batting_team" in work.columns else None)
        group_cols = ["match_id", "innings"]
        for optional_col in ("start_date", "venue", "venue_id"):
            if optional_col in work.columns:
                group_cols.append(optional_col)
        if team_col:
            group_cols.append(team_col)

        grouped = (
            work.groupby(group_cols + ["phase_bucket"], dropna=False, observed=False)
            .agg(
                phase_runs=("phase_runs", "sum"),
                phase_wkts=("phase_wkts", "sum"),
                phase_balls=("phase_balls", "sum"),
            )
            .reset_index()
        )

        phase_df = grouped.pivot_table(
            index=group_cols,
            columns="phase_bucket",
            values=["phase_runs", "phase_wkts", "phase_balls"],
            fill_value=0,
            observed=False,
        ).reset_index()

        suffix_map = {"phase_runs": "runs", "phase_wkts": "wkts", "phase_balls": "balls"}

        def _flatten_phase_col(
            col: Union[str, Tuple[str, str]]
        ) -> str:
            if not isinstance(col, tuple):
                return col
            metric = col[0]
            phase_id = col[1] if len(col) > 1 else ""
            if not phase_id:
                return metric
            return f"{phase_id}_{suffix_map.get(metric, metric)}"

        phase_df.columns = pd.Index(phase_df.columns).map(_flatten_phase_col)

        if "batting_team" in phase_df.columns and "team" not in phase_df.columns:
            phase_df = phase_df.rename(columns={"batting_team": "team"})

    phase_df = _ensure_phase_metric_columns(phase_df)
    return {"phase_df": phase_df, "phase_bounds": phase_bounds, "phase_overs": phase_overs}


def summarize_phase_by_innings(stats_df: pd.DataFrame) -> Dict[str, Dict[str, Dict[str, float | int]]]:
    """Return innings-wise phase summary with averages and sample counts."""
    def _empty_summary() -> Dict[str, Dict[str, Dict[str, float | int]]]:
        return {
            "1": {
                "pp": {"avg": 0.0, "n": 0, "wkts": 0.0},
                "mid": {"avg": 0.0, "n": 0, "wkts": 0.0},
                "dth": {"avg": 0.0, "n": 0, "wkts": 0.0},
                "total": {"avg": 0.0, "n": 0, "wkts": 0.0},
            },
            "2": {
                "pp": {"avg": 0.0, "n": 0, "wkts": 0.0},
                "mid": {"avg": 0.0, "n": 0, "wkts": 0.0},
                "dth": {"avg": 0.0, "n": 0, "wkts": 0.0},
                "total": {"avg": 0.0, "n": 0, "wkts": 0.0},
            },
        }

    default = _empty_summary()
    if stats_df is None or stats_df.empty or "innings" not in stats_df.columns:
        return default

    work_df = _ensure_phase_metric_columns(stats_df)
    if work_df.empty:
        return default

    agg_rules = {
        "pp_runs": ["mean", "count"],
        "pp_wkts": "mean",
        "mid_runs": ["mean", "count"],
        "mid_wkts": "mean",
        "dth_runs": ["mean", "count"],
        "dth_wkts": "mean",
        "total_runs": ["mean", "count"],
    }
    summary = work_df.groupby("innings").agg(agg_rules).round(1)

    result = _empty_summary()
    for innings in (1, 2):
        innings_key = str(innings)
        for phase_id in ("pp", "mid", "dth", "total"):
            runs_col = f"{phase_id}_runs" if phase_id != "total" else "total_runs"
            wkts_col = f"{phase_id}_wkts" if phase_id != "total" else None
            try:
                result[innings_key][phase_id] = {
                    "avg": float(summary.loc[innings, (runs_col, "mean")]),
                    "n": int(summary.loc[innings, (runs_col, "count")]),
                    "wkts": float(summary.loc[innings, (wkts_col, "mean")]) if wkts_col else 0.0,
                }
            except (KeyError, TypeError, ValueError):
                result[innings_key][phase_id] = {"avg": 0.0, "n": 0, "wkts": 0.0}

    return result


def _avg(df: pd.DataFrame, col: str) -> float:
    if col not in df.columns or df.empty:
        return 0.0
    return round(float(pd.to_numeric(df[col], errors="coerce").fillna(0).mean()), 1)


def _phase_rr(df: pd.DataFrame, runs_col: str, balls_col: str, fallback_overs: float) -> float:
    if runs_col not in df.columns or df.empty:
        return 0.0

    runs = pd.to_numeric(df[runs_col], errors="coerce").fillna(0)
    if balls_col in df.columns:
        balls = pd.to_numeric(df[balls_col], errors="coerce").fillna(0)
        valid = balls > 0
        if bool(valid.any()):
            return round(float(((runs[valid] * 6.0) / balls[valid]).mean()), 2)

    return round(float(runs.mean() / fallback_overs), 2) if fallback_overs > 0 else 0.0


def calculate_team_phase_habits(
    team_df: pd.DataFrame,
    phase_overs: Dict[str, float],
) -> Dict[str, Dict[str, float]]:
    """Calculate bat-first/chasing split and run-rates for one team."""
    work_df = _ensure_phase_metric_columns(team_df)
    if work_df.empty or "innings" not in work_df.columns:
        return {
            "bat_first": {"pp_runs": 0.0, "pp_wkts": 0.0, "mid_runs": 0.0, "mid_wkts": 0.0, "dth_runs": 0.0, "dth_wkts": 0.0},
            "chasing": {"pp_runs": 0.0, "mid_wkts": 0.0, "dth_wkts": 0.0},
            "rr": {"pp_rr": 0.0, "mid_rr": 0.0, "dth_rr": 0.0, "avg_score": 0.0},
        }

    bat_first = work_df[work_df["innings"] == 1]
    chasing = work_df[work_df["innings"] == 2]

    return {
        "bat_first": {
            "pp_runs": _avg(bat_first, "pp_runs"),
            "pp_wkts": _avg(bat_first, "pp_wkts"),
            "mid_runs": _avg(bat_first, "mid_runs"),
            "mid_wkts": _avg(bat_first, "mid_wkts"),
            "dth_runs": _avg(bat_first, "dth_runs"),
            "dth_wkts": _avg(bat_first, "dth_wkts"),
        },
        "chasing": {
            "pp_runs": _avg(chasing, "pp_runs"),
            "mid_wkts": _avg(chasing, "mid_wkts"),
            "dth_wkts": _avg(chasing, "dth_wkts"),
        },
        "rr": {
            "pp_rr": _phase_rr(work_df, "pp_runs", "pp_balls", phase_overs.get("pp", 0.0)),
            "mid_rr": _phase_rr(work_df, "mid_runs", "mid_balls", phase_overs.get("mid", 0.0)),
            "dth_rr": _phase_rr(work_df, "dth_runs", "dth_balls", phase_overs.get("dth", 0.0)),
            "avg_score": _avg(work_df, "total_runs"),
        },
    }


def _scenario_row(
    label: str,
    home_value: float | None,
    away_value: float | None,
    higher_better: bool,
) -> ScenarioRow:
    if home_value is None or away_value is None:
        return {
            "label": label,
            "home_value": home_value,
            "away_value": away_value,
            "higher_better": higher_better,
            "diff_text": "-",
            "diff_tone": "muted",
        }

    diff = round(float(home_value) - float(away_value), 1)
    if abs(diff) < 0.05:
        return {
            "label": label,
            "home_value": home_value,
            "away_value": away_value,
            "higher_better": higher_better,
            "diff_text": "0.0",
            "diff_tone": "muted",
        }

    positive_is_good = diff > 0 if higher_better else diff < 0
    sign = "UP" if positive_is_good else "DOWN"
    return {
        "label": label,
        "home_value": home_value,
        "away_value": away_value,
        "higher_better": higher_better,
        "diff_text": f"{sign} {abs(diff):.1f}",
        "diff_tone": "success" if positive_is_good else "danger",
    }


def build_phase_scenario_rows(
    home_habits: Dict[str, Dict[str, float]],
    away_habits: Dict[str, Dict[str, float]],
) -> ScenarioRows:
    """Build UI scenario rows for bat-first and chasing comparisons."""
    bat_first_rows = [
        _scenario_row("Avg PP Runs", home_habits["bat_first"].get("pp_runs"), away_habits["bat_first"].get("pp_runs"), True),
        _scenario_row("Avg PP Wkts", home_habits["bat_first"].get("pp_wkts"), away_habits["bat_first"].get("pp_wkts"), False),
        _scenario_row("Avg Mid Runs", home_habits["bat_first"].get("mid_runs"), away_habits["bat_first"].get("mid_runs"), True),
        _scenario_row("Avg Mid Wkts", home_habits["bat_first"].get("mid_wkts"), away_habits["bat_first"].get("mid_wkts"), False),
        _scenario_row("Avg Death Runs", home_habits["bat_first"].get("dth_runs"), away_habits["bat_first"].get("dth_runs"), True),
        _scenario_row("Avg Death Wkts", home_habits["bat_first"].get("dth_wkts"), away_habits["bat_first"].get("dth_wkts"), False),
    ]
    chasing_rows = [
        _scenario_row("Avg PP Score", home_habits["chasing"].get("pp_runs"), away_habits["chasing"].get("pp_runs"), True),
        _scenario_row("Avg Mid Wkts", home_habits["chasing"].get("mid_wkts"), away_habits["chasing"].get("mid_wkts"), False),
        _scenario_row("Avg Death Wkts", home_habits["chasing"].get("dth_wkts"), away_habits["chasing"].get("dth_wkts"), False),
    ]
    return {"bat_first": bat_first_rows, "chasing": chasing_rows}
