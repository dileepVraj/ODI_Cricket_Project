"""
ODI ETL reconciliation checks.

Validates post-ingestion DuckDB integrity contracts and optionally reconciles
against source ball-by-ball CSV.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import duckdb
import pandas as pd


def _count_csv_rows(csv_path: str) -> int:
    with open(csv_path, "r", encoding="utf-8") as f:
        # subtract header row
        return max(sum(1 for _ in f) - 1, 0)


def _emit_report(report: Dict[str, Any], output_path: Optional[str]) -> None:
    if not output_path:
        return
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def _check(name: str, ok: bool, severity: str, actual: Any = None, expected: Any = None, details: str = "") -> Dict[str, Any]:
    return {
        "name": name,
        "status": "pass" if ok else "fail",
        "severity": severity,
        "actual": actual,
        "expected": expected,
        "details": details,
    }


def run_reconciliation_checks(
    db_path: str,
    *,
    source_balls_csv: Optional[str] = None,
    max_unresolved_venue_ratio: float = 0.05,
    output_path: Optional[str] = None,
    fail_on_error: bool = True,
) -> Dict[str, Any]:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"DuckDB path not found: {db_path}")

    checks: List[Dict[str, Any]] = []
    started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    con = duckdb.connect(db_path, read_only=True)
    try:
        tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
        has_matches = "matches" in tables
        has_balls = "balls" in tables

        checks.append(_check("table_exists_matches", has_matches, "hard", actual=has_matches, expected=True))
        checks.append(_check("table_exists_balls", has_balls, "hard", actual=has_balls, expected=True))

        if has_matches and has_balls:
            balls_count = int(con.execute("SELECT COUNT(*) FROM balls").fetchone()[0])
            matches_count = int(con.execute("SELECT COUNT(*) FROM matches").fetchone()[0])
            checks.append(_check("balls_non_empty", balls_count > 0, "hard", actual=balls_count, expected="> 0"))
            checks.append(_check("matches_non_empty", matches_count > 0, "hard", actual=matches_count, expected="> 0"))

            distinct_balls = int(con.execute("SELECT COUNT(DISTINCT match_id) FROM balls").fetchone()[0])
            distinct_matches = int(con.execute("SELECT COUNT(DISTINCT match_id) FROM matches").fetchone()[0])
            checks.append(
                _check(
                    "match_id_distinct_parity",
                    distinct_balls == distinct_matches,
                    "hard",
                    actual={"balls": distinct_balls, "matches": distinct_matches},
                    expected="equal",
                )
            )

            orphan_matches = int(
                con.execute(
                    """
                    SELECT COUNT(*)
                    FROM matches m
                    LEFT JOIN balls b ON b.match_id = m.match_id
                    WHERE b.match_id IS NULL
                    """
                ).fetchone()[0]
            )
            checks.append(_check("matches_without_balls", orphan_matches == 0, "hard", actual=orphan_matches, expected=0))

            orphan_balls = int(
                con.execute(
                    """
                    SELECT COUNT(*)
                    FROM (
                        SELECT DISTINCT b.match_id
                        FROM balls b
                        LEFT JOIN matches m ON m.match_id = b.match_id
                        WHERE m.match_id IS NULL
                    ) q
                    """
                ).fetchone()[0]
            )
            checks.append(_check("balls_without_matches", orphan_balls == 0, "hard", actual=orphan_balls, expected=0))

            balls_cols = {row[1] for row in con.execute("PRAGMA table_info('balls')").fetchall()}
            has_identity_cols = {"over_num", "ball_rank"}.issubset(balls_cols)
            checks.append(
                _check(
                    "balls_identity_columns_present",
                    has_identity_cols,
                    "hard",
                    actual=sorted(list(balls_cols & {"over_num", "ball_rank"})),
                    expected=["over_num", "ball_rank"],
                )
            )

            if has_identity_cols:
                duplicate_delivery_keys = int(
                    con.execute(
                        """
                        SELECT COUNT(*)
                        FROM (
                            SELECT match_id, innings, over_num, ball_rank, COUNT(*) AS c
                            FROM balls
                            GROUP BY match_id, innings, over_num, ball_rank
                            HAVING COUNT(*) > 1
                        ) d
                        """
                    ).fetchone()[0]
                )
                checks.append(
                    _check(
                        "duplicate_delivery_identity",
                        duplicate_delivery_keys == 0,
                        "hard",
                        actual=duplicate_delivery_keys,
                        expected=0,
                    )
                )

            unresolved_venue_rows = int(
                con.execute(
                    """
                    SELECT COUNT(*)
                    FROM matches
                    WHERE venue_id IS NULL OR TRIM(CAST(venue_id AS VARCHAR)) = ''
                    """
                ).fetchone()[0]
            )
            unresolved_ratio = (float(unresolved_venue_rows) / float(matches_count)) if matches_count else 1.0
            checks.append(
                _check(
                    "unresolved_venue_ratio",
                    unresolved_ratio <= float(max_unresolved_venue_ratio),
                    "hard",
                    actual=round(unresolved_ratio, 6),
                    expected=f"<= {max_unresolved_venue_ratio:.6f}",
                    details=f"rows={unresolved_venue_rows}/{matches_count}",
                )
            )

            suspicious_missing_inn2 = int(
                con.execute(
                    """
                    SELECT COUNT(*)
                    FROM matches
                    WHERE (balls_inn2 IS NULL OR wickets_inn2 IS NULL)
                      AND lower(trim(coalesce(winner, ''))) NOT IN ('', 'none', 'nan', 'no result', 'abandoned')
                    """
                ).fetchone()[0]
            )
            checks.append(
                _check(
                    "declared_result_missing_innings2",
                    suspicious_missing_inn2 == 0,
                    "hard",
                    actual=suspicious_missing_inn2,
                    expected=0,
                )
            )

            if source_balls_csv and os.path.exists(source_balls_csv):
                source_rows = _count_csv_rows(source_balls_csv)
                checks.append(
                    _check(
                        "source_csv_vs_db_ball_rows",
                        source_rows == balls_count,
                        "hard",
                        actual={"source": source_rows, "db": balls_count},
                        expected="equal",
                    )
                )

                try:
                    source_match_ids = int(pd.read_csv(source_balls_csv, usecols=["match_id"])["match_id"].nunique())
                    checks.append(
                        _check(
                            "source_csv_vs_db_match_ids",
                            source_match_ids == distinct_balls,
                            "hard",
                            actual={"source": source_match_ids, "db": distinct_balls},
                            expected="equal",
                        )
                    )
                except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as exc:
                    checks.append(
                        _check(
                            "source_csv_match_id_scan",
                            False,
                            "soft",
                            actual=str(exc),
                            expected="source match_id column readable",
                        )
                    )

        hard_failures = [c for c in checks if c["severity"] == "hard" and c["status"] == "fail"]
        soft_failures = [c for c in checks if c["severity"] == "soft" and c["status"] == "fail"]

        report = {
            "db_path": db_path,
            "source_balls_csv": source_balls_csv,
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "max_unresolved_venue_ratio": max_unresolved_venue_ratio,
            "checks": checks,
            "summary": {
                "total_checks": len(checks),
                "hard_failures": len(hard_failures),
                "soft_failures": len(soft_failures),
                "status": "pass" if len(hard_failures) == 0 else "fail",
            },
        }

        _emit_report(report, output_path)

        if fail_on_error and hard_failures:
            failed_names = ", ".join(c["name"] for c in hard_failures)
            raise RuntimeError(f"Reconciliation failed: {failed_names}")

        return report
    finally:
        con.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ODI ETL reconciliation checks against DuckDB.")
    parser.add_argument("--db-path", default="formats/odi/data/odi.duckdb", help="Path to DuckDB file.")
    parser.add_argument("--source-balls-csv", default="formats/odi/data/FINAL_ODI_MASTER.csv", help="Source ball-by-ball CSV path.")
    parser.add_argument("--max-unresolved-venue-ratio", type=float, default=0.05, help="Hard-fail threshold for unresolved venue_id ratio.")
    parser.add_argument("--report-path", default="formats/odi/reports/reconciliation_audit.json", help="Optional JSON report output path.")
    parser.add_argument("--no-fail", action="store_true", help="Do not raise non-zero on hard failures.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    report = run_reconciliation_checks(
        db_path=args.db_path,
        source_balls_csv=args.source_balls_csv,
        max_unresolved_venue_ratio=args.max_unresolved_venue_ratio,
        output_path=args.report_path,
        fail_on_error=not args.no_fail,
    )
    print(
        "[RECONCILIATION] "
        f"status={report['summary']['status']} "
        f"checks={report['summary']['total_checks']} "
        f"hard_failures={report['summary']['hard_failures']} "
        f"soft_failures={report['summary']['soft_failures']}"
    )


if __name__ == "__main__":
    main()
