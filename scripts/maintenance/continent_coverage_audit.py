"""
Audits continent/region coverage drift between naive venue_id-only filtering
and robust filtering (venue_id + raw venue + resolver fallback).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

# Add project root to path for direct script execution.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)  # noqa: E402

from core.data_access import DataAccess  # noqa: E402
from config.settings import ODI_DB_PATH  # noqa: E402
from formats.odi.engines.team_engine import TeamEngine  # noqa: E402


def _pair_mask(df: pd.DataFrame, home_team: str, away_team: str) -> pd.Series:
    return (
        ((df["team_bat_1"] == home_team) & (df["team_bat_2"] == away_team))
        | ((df["team_bat_1"] == away_team) & (df["team_bat_2"] == home_team))
    )


def _naive_region_mask(df: pd.DataFrame, prefixes: List[str]) -> pd.Series:
    if "venue_id" not in df.columns:
        return pd.Series(False, index=df.index)
    return df["venue_id"].fillna("").astype(str).str.upper().str.startswith(tuple(prefixes))


def run_continent_coverage_audit(
    db_path: str,
    *,
    years_back: int = 10,
    report_path: str = "formats/odi/reports/continent_coverage_audit.json",
    team_limit: int = 12,
) -> Dict[str, Any]:
    dal = DataAccess(db_path)
    try:
        df = dal.get_matches()
    finally:
        dal.close()

    if df is None or df.empty:
        raise RuntimeError("No matches found for continent coverage audit.")

    if "start_date" in df.columns:
        df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
        cutoff = df["start_date"].max() - pd.DateOffset(years=years_back)
        df = df[df["start_date"] >= cutoff].copy()

    teams = (
        pd.concat([df["team_bat_1"], df["team_bat_2"]], ignore_index=True)
        .dropna()
        .astype(str)
        .value_counts()
        .head(team_limit)
        .index.tolist()
    )

    engine = TeamEngine.__new__(TeamEngine)
    regions = ["Asia", "Europe", "Oceania", "Africa", "Americas"]

    mismatches: List[Dict[str, Any]] = []
    checked = 0

    for i, home_team in enumerate(teams):
        for away_team in teams[i + 1 :]:
            pair_df = df[_pair_mask(df, home_team, away_team)].copy()
            if pair_df.empty:
                continue

            for region in regions:
                prefixes = engine._get_continent_prefixes(region)
                if not prefixes:
                    continue

                robust_mask = engine._build_continent_mask(pair_df, region)
                naive_mask = _naive_region_mask(pair_df, prefixes)

                robust_ids = set(pair_df.loc[robust_mask, "match_id"].astype(str))
                naive_ids = set(pair_df.loc[naive_mask, "match_id"].astype(str))
                checked += 1

                if robust_ids != naive_ids:
                    missing_in_naive = sorted(list(robust_ids - naive_ids))
                    missing_in_robust = sorted(list(naive_ids - robust_ids))
                    mismatches.append(
                        {
                            "home_team": home_team,
                            "away_team": away_team,
                            "region": region,
                            "robust_count": len(robust_ids),
                            "naive_count": len(naive_ids),
                            "missing_in_naive": missing_in_naive,
                            "missing_in_robust": missing_in_robust,
                        }
                    )

    report = {
        "db_path": db_path,
        "years_back": years_back,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "checked_pair_region_cases": checked,
        "mismatch_cases": len(mismatches),
        "mismatches": mismatches,
    }

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit continent coverage drift across team pairs.")
    parser.add_argument("--db-path", default=ODI_DB_PATH, help="Path to ODI DuckDB.")
    parser.add_argument("--years-back", type=int, default=10, help="Lookback window for match sampling.")
    parser.add_argument("--team-limit", type=int, default=12, help="Top-N teams (by match frequency) to include in pair audit.")
    parser.add_argument(
        "--report-path",
        default="formats/odi/reports/continent_coverage_audit.json",
        help="Output JSON report path.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    report = run_continent_coverage_audit(
        db_path=args.db_path,
        years_back=args.years_back,
        report_path=args.report_path,
        team_limit=args.team_limit,
    )
    print(
        "[CONTINENT COVERAGE AUDIT] "
        f"checked={report['checked_pair_region_cases']} "
        f"mismatches={report['mismatch_cases']} "
        f"report={args.report_path}"
    )


if __name__ == "__main__":
    main()
