"""Full-suite truth-bridge baseline refresher for Operation Lego Block.

This script performs four tasks:
1) Seeds all ODI truth-bridge suites using current engine logic.
2) Injects mandatory metadata into every generated ground_truth.json.
3) Validates Universal Core calculators against FINAL_ODI_MASTER.csv.
4) Cleans root-level temporary truth_bridge/debug files.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

# Ensure repository root is importable when executing as a script.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))  # noqa: E402

from core.calculators.performance import calculate_team_metrics  # noqa: E402
from core.calculators.phase_engine import calculate_phase_breakdown  # noqa: E402
from core.services.match_filter_service import apply_smart_filters  # noqa: E402
from formats.odi.manifest import FORMAT_RULES  # noqa: E402


REFACTOR_DATE = "2026-02-23"
ARCHITECT_NOTE = (
    "Migration to Universal Core Calculators. "
    "Averages now utilize competitive_chase_threshold=200 and corrected "
    "smart_filter_service logic."
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _truth_bridge_root(repo_root: Path) -> Path:
    return repo_root / "formats" / "odi" / "tests" / "truth_bridge"


def _find_test_runners(repo_root: Path) -> List[Path]:
    base = _truth_bridge_root(repo_root)
    return sorted(base.glob("*/test_runner.py"))


def _run_seed_refresh(repo_root: Path) -> Dict[str, Any]:
    runners = _find_test_runners(repo_root)
    env = os.environ.copy()
    env["SEED_MODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        str(repo_root)
        if not existing_pythonpath
        else str(repo_root) + os.pathsep + existing_pythonpath
    )

    results: List[Dict[str, Any]] = []
    success = 0

    for runner in runners:
        proc = subprocess.run(
            [sys.executable, str(runner)],
            cwd=str(repo_root),
            env=env,
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
        )
        ok = proc.returncode == 0
        if ok:
            success += 1
        results.append(
            {
                "runner": str(runner.relative_to(repo_root)),
                "return_code": proc.returncode,
                "status": "ok" if ok else "failed",
                "stderr_tail": proc.stderr[-1000:] if proc.stderr else "",
            }
        )

    return {
        "runners_total": len(runners),
        "runners_ok": success,
        "runners_failed": len(runners) - success,
        "runner_results": results,
    }


def _find_ground_truth_files(repo_root: Path) -> List[Path]:
    return sorted(_truth_bridge_root(repo_root).glob("*/ground_truth.json"))


def _inject_metadata_headers(repo_root: Path) -> Dict[str, Any]:
    tagged = 0
    errors: List[Dict[str, str]] = []

    for gt_file in _find_ground_truth_files(repo_root):
        try:
            with gt_file.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            if not isinstance(payload, dict):
                errors.append(
                    {
                        "file": str(gt_file.relative_to(repo_root)),
                        "error": "ground_truth root is not a JSON object",
                    }
                )
                continue

            metadata_header = {
                "refactor_date": REFACTOR_DATE,
                "architect_note": ARCHITECT_NOTE,
            }
            payload = {"_metadata": metadata_header, **{k: v for k, v in payload.items() if k != "_metadata"}}

            with gt_file.open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=True, default=str)
            tagged += 1
        except (OSError, ValueError, TypeError) as exc:
            errors.append({"file": str(gt_file.relative_to(repo_root)), "error": str(exc)})

    return {
        "ground_truth_files_tagged": tagged,
        "ground_truth_files_total": len(_find_ground_truth_files(repo_root)),
        "errors": errors,
    }


def _build_match_summary_from_balls(ball_df: pd.DataFrame) -> pd.DataFrame:
    """Build match-level summary from ball-level master data (vectorized)."""
    work = ball_df.copy()
    work["match_id"] = work["match_id"].astype(str).str.split(".").str[0].str.strip()
    work["innings"] = pd.to_numeric(work["innings"], errors="coerce")
    work = work[work["innings"].isin([1, 2])].copy()
    work["innings"] = work["innings"].astype(int)

    runs_off_bat = pd.to_numeric(work.get("runs_off_bat"), errors="coerce").fillna(0)
    extras = pd.to_numeric(work.get("extras"), errors="coerce").fillna(0)
    work["total_runs"] = runs_off_bat + extras

    wides = pd.to_numeric(work.get("wides"), errors="coerce").fillna(0)
    noballs = pd.to_numeric(work.get("noballs"), errors="coerce").fillna(0)
    work["is_legal_ball"] = ((wides == 0) & (noballs == 0)).astype(int)

    if "wicket_type" in work.columns:
        work["is_wicket"] = work["wicket_type"].notna().astype(int)
    elif "player_dismissed" in work.columns:
        work["is_wicket"] = work["player_dismissed"].notna().astype(int)
    else:
        work["is_wicket"] = 0

    innings_agg = (
        work.groupby(["match_id", "innings"], dropna=False, observed=False)
        .agg(
            batting_team=("batting_team", "first"),
            score=("total_runs", "sum"),
            balls=("is_legal_ball", "sum"),
            wickets=("is_wicket", "sum"),
        )
        .reset_index()
    )

    wide = innings_agg.pivot_table(
        index="match_id",
        columns="innings",
        values=["batting_team", "score", "balls", "wickets"],
        aggfunc="first",
        observed=False,
    ).reset_index()

    flattened: List[str] = []
    for col in wide.columns:
        if isinstance(col, tuple):
            base, inn = col
            if inn == "":
                flattened.append(str(base))
            else:
                flattened.append(f"{base}_inn{int(inn)}")
        else:
            flattened.append(str(col))
    wide.columns = flattened

    match_meta = (
        work.groupby("match_id", dropna=False, observed=False)
        .agg(
            start_date=("start_date", "first"),
            venue=("venue", "first"),
            winner=("winner", "first"),
        )
        .reset_index()
    )

    summary = match_meta.merge(wide, on="match_id", how="left")
    summary = summary.rename(
        columns={
            "batting_team_inn1": "team_bat_1",
            "batting_team_inn2": "team_bat_2",
            "score_inn1": "score_inn1",
            "score_inn2": "score_inn2",
            "balls_inn1": "balls_inn1",
            "balls_inn2": "balls_inn2",
            "wickets_inn1": "wickets_inn1",
            "wickets_inn2": "wickets_inn2",
        }
    )

    for col in ["score_inn1", "score_inn2", "balls_inn1", "balls_inn2", "wickets_inn1", "wickets_inn2"]:
        if col in summary.columns:
            summary[col] = pd.to_numeric(summary[col], errors="coerce")

    summary["start_date"] = pd.to_datetime(summary["start_date"], errors="coerce")
    return summary


def _run_universal_core_validation(repo_root: Path) -> Dict[str, Any]:
    csv_path = repo_root / "formats" / "odi" / "data" / "FINAL_ODI_MASTER.csv"
    ball_df = pd.read_csv(csv_path)

    min_balls = int(FORMAT_RULES.get("min_balls_for_completed_innings", 270))
    phase_config = FORMAT_RULES.get("phases", {})
    competitive_threshold = int(FORMAT_RULES.get("competitive_chase_threshold", 200))

    match_df = _build_match_summary_from_balls(ball_df)
    filtered_df = apply_smart_filters(match_df, min_balls=min_balls)

    included_mask = filtered_df["status"].astype(str).str.contains("Included", na=False)
    dropped_mask = ~included_mask

    total_matches = int(filtered_df["match_id"].nunique())
    included_matches = int(filtered_df.loc[included_mask, "match_id"].nunique())
    dropped_matches = int(filtered_df.loc[dropped_mask, "match_id"].nunique())

    phase_payload = calculate_phase_breakdown(ball_df, phase_config)
    phase_df = phase_payload.get("phase_df", pd.DataFrame())

    team_name = "India"
    if "team_bat_1" in filtered_df.columns and filtered_df["team_bat_1"].notna().any():
        top_team = filtered_df["team_bat_1"].astype(str).value_counts()
        if not top_team.empty:
            team_name = str(top_team.index[0])

    team_metrics = calculate_team_metrics(
        df=filtered_df,
        team_name=team_name,
        competitive_threshold=competitive_threshold,
    )

    total_drift = {
        "total_matches": total_matches,
        "included_matches": included_matches,
        "dropped_matches": dropped_matches,
        "dropped_pct": round((dropped_matches / total_matches) * 100, 2) if total_matches > 0 else 0.0,
    }

    return {
        "source_csv": str(csv_path.relative_to(repo_root)),
        "loaded_modules": [
            "core/calculators/performance.py",
            "core/calculators/phase_engine.py",
            "core/services/match_filter_service.py",
        ],
        "thresholds": {
            "min_balls_for_completed_innings": min_balls,
            "competitive_chase_threshold": competitive_threshold,
            "phases": phase_config,
        },
        "ball_level_rows": int(len(ball_df)),
        "match_level_rows": int(len(match_df)),
        "phase_breakdown_rows": int(len(phase_df)),
        "sample_team_for_metrics": team_name,
        "sample_team_metrics": team_metrics,
        "total_drift": total_drift,
    }


def _cleanup_root_temp_files(repo_root: Path) -> Dict[str, Any]:
    deleted: List[str] = []
    failures: List[Dict[str, str]] = []

    candidates = list(repo_root.glob("truth_bridge.py"))
    candidates.extend(repo_root.glob("debug*.py"))
    candidates.extend(repo_root.glob("*_debug.py"))
    candidates.extend(repo_root.glob("debug*.json"))
    candidates.extend(repo_root.glob("*_debug.json"))
    candidates.extend(repo_root.glob("debug*.txt"))
    candidates.extend(repo_root.glob("*_debug.txt"))

    unique_candidates = sorted({p for p in candidates if p.is_file()})

    for file_path in unique_candidates:
        try:
            file_path.unlink()
            deleted.append(str(file_path.relative_to(repo_root)))
        except OSError as exc:
            failures.append({"file": str(file_path.relative_to(repo_root)), "error": str(exc)})

    return {"deleted_files": deleted, "failures": failures}


def _write_report(repo_root: Path, report: Dict[str, Any]) -> Path:
    out_dir = repo_root / "tests" / "truth_bridge"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "refresh_report.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    return out_path


def main() -> int:
    repo_root = _repo_root()

    metadata_preseed = _inject_metadata_headers(repo_root)
    seed_result = _run_seed_refresh(repo_root)
    metadata_result = _inject_metadata_headers(repo_root)
    validation_result = _run_universal_core_validation(repo_root)
    cleanup_result = _cleanup_root_temp_files(repo_root)

    report = {
        "refactor_date": REFACTOR_DATE,
        "architect_note": ARCHITECT_NOTE,
        "metadata_preseed_sanitize": metadata_preseed,
        "seed_refresh": seed_result,
        "metadata_tagging": metadata_result,
        "validation": validation_result,
        "cleanup": cleanup_result,
    }

    report_path = _write_report(repo_root, report)
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    print(f"Report written to: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
