"""
Read-only backfill extractor for missing matches.venue_id values.

This script never mutates the live DuckDB file. It exports a CSV patch that can
be ingested through the controlled ETL pipeline.

Usage:
  python scripts/maintenance/backfill_match_venue_ids.py
  python scripts/maintenance/backfill_match_venue_ids.py --dry-run
  python scripts/maintenance/backfill_match_venue_ids.py --output-csv scripts/maintenance/out/match_venue_backfill.csv
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List, Tuple

import duckdb
import pandas as pd

# Add project root to path for direct script execution.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.shared.venues import resolve_venue_id
from config.settings import ODI_DB_PATH


def _count_missing(con: duckdb.DuckDBPyConnection) -> int:
    return int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM matches
            WHERE venue_id IS NULL OR TRIM(CAST(venue_id AS VARCHAR)) = ''
            """
        ).fetchone()[0]
    )


def _collect_missing_rows(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return con.execute(
        """
        SELECT match_id, venue, start_date
        FROM matches
        WHERE venue_id IS NULL OR TRIM(CAST(venue_id AS VARCHAR)) = ''
          AND venue IS NOT NULL
          AND TRIM(CAST(venue AS VARCHAR)) <> ''
        """
    ).fetchdf()


def _collect_mapping_rows(venues: List[str]) -> Tuple[List[Tuple[str, str]], List[str]]:
    mapping_rows: List[Tuple[str, str]] = []
    unresolved: List[str] = []

    for venue in venues:
        resolved = resolve_venue_id(venue)
        if resolved:
            mapping_rows.append((venue, str(resolved)))
        else:
            unresolved.append(venue)

    return mapping_rows, unresolved


def backfill_match_venue_ids(
    db_path: str,
    output_csv: str,
    dry_run: bool = False,
) -> int:
    con = duckdb.connect(db_path, read_only=True)
    try:
        before_null = _count_missing(con)
        missing_rows = _collect_missing_rows(con)
        missing_venues = sorted(missing_rows["venue"].astype(str).str.strip().unique().tolist()) if not missing_rows.empty else []
        mapping_rows, unresolved = _collect_mapping_rows(missing_venues)
        mapping_lookup: Dict[str, str] = {venue: venue_id for venue, venue_id in mapping_rows}

        print(f"[INFO] DB: {db_path}")
        print(f"[INFO] Missing venue_id rows before: {before_null}")
        print(f"[INFO] Distinct missing venues: {len(missing_venues)}")
        print(f"[INFO] Resolvable venues: {len(mapping_rows)}")
        print(f"[INFO] Unresolvable venues: {len(unresolved)}")

        if missing_rows.empty or not mapping_lookup:
            print("[INFO] No resolvable rows found. Nothing to export.")
            return 0

        export_df = missing_rows[missing_rows["venue"].isin(mapping_lookup.keys())].copy()
        export_df["resolved_venue_id"] = export_df["venue"].map(mapping_lookup)
        export_df = export_df[["match_id", "venue", "resolved_venue_id", "start_date"]].drop_duplicates()

        if unresolved:
            unresolved_counts = (
                missing_rows[missing_rows["venue"].isin(unresolved)]["venue"]
                .value_counts()
                .head(20)
            )
            print("[INFO] Top unresolved venues (sample):")
            for venue, count in unresolved_counts.items():
                print(f"  - {venue} ({int(count)})")

        if dry_run:
            print("[INFO] Dry-run mode enabled. CSV export skipped.")
            print(f"[INFO] Rows that would be exported: {len(export_df)}")
            return len(export_df)

        out_dir = os.path.dirname(output_csv)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        export_df.to_csv(output_csv, index=False)

        print(f"[INFO] Exported patch rows: {len(export_df)}")
        print(f"[INFO] Patch CSV: {output_csv}")
        print("[INFO] Apply through update_data.py / refinery pipeline (no direct DB writes).")
        return len(export_df)
    finally:
        con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill matches.venue_id in DuckDB.")
    parser.add_argument(
        "--db-path",
        default=ODI_DB_PATH,
        help="Path to DuckDB file.",
    )
    parser.add_argument(
        "--output-csv",
        default="scripts/maintenance/out/match_venue_backfill.csv",
        help="Path to write backfill patch CSV.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show impact without writing CSV.",
    )
    args = parser.parse_args()
    backfill_match_venue_ids(
        db_path=args.db_path,
        output_csv=args.output_csv,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
