#!/usr/bin/env python
"""Read-only DuckDB query helper for quant workflows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import duckdb
import pandas as pd


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run read-only SQL against a DuckDB file.")
    parser.add_argument(
        "--db",
        default="formats/odi/data/odi.duckdb",
        help="Path to DuckDB file (default: formats/odi/data/odi.duckdb)",
    )
    parser.add_argument("--sql", help="SQL text to execute")
    parser.add_argument("--sql-file", help="Path to a .sql file")
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format",
    )
    return parser.parse_args()


def _load_sql(args: argparse.Namespace) -> str:
    sql_text = (args.sql or "").strip()
    sql_file = (args.sql_file or "").strip()

    if bool(sql_text) == bool(sql_file):
        raise ValueError("Provide exactly one of --sql or --sql-file.")

    if sql_text:
        return sql_text

    path = Path(sql_file)
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text(encoding="utf-8")


def _print_df(df: pd.DataFrame, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(df.to_dict(orient="records"), ensure_ascii=False, default=str, indent=2))
        return
    if output_format == "csv":
        print(df.to_csv(index=False), end="")
        return

    if df.empty:
        print("(0 rows)")
    else:
        print(df.to_string(index=False))


def main() -> int:
    try:
        args = _parse_args()
        sql = _load_sql(args)

        db_path = Path(args.db)
        if not db_path.exists():
            raise FileNotFoundError(f"DuckDB file not found: {db_path}")

        # Critical safety guarantee: read-only connection.
        con = duckdb.connect(str(db_path), read_only=True)
        try:
            df = con.execute(sql).df()
        finally:
            con.close()

        _print_df(df, args.format)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
