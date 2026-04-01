"""
MASTER ORCHESTRATOR: Incremental Intelligence Pipeline
Automates the flow: JSON -> CSV -> Intelligence Refinery -> DuckDB -> Reconciliation -> Truth Bridge.

Usage:
  python scripts/maintenance/update_data.py
  python scripts/maintenance/update_data.py odi --skip-conversion
  python scripts/maintenance/update_data.py odi --allow-partial-conversion
"""

import argparse
import os
import sys

# Add project root to sys.path for module imports.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)  # noqa: E402

from config.format_registry import get_format_module  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Cricket Data Intelligence Pipeline")
    parser.add_argument("format", nargs="?", default="odi", help="Format to update (odi, t20i, ipl, etc.)")
    parser.add_argument("--skip-conversion", action="store_true", help="Skip JSON to CSV conversion stage.")
    parser.add_argument(
        "--allow-partial-conversion",
        action="store_true",
        help="Allow partial conversion output when some JSON files fail.",
    )
    parser.add_argument(
        "--skip-reconciliation",
        action="store_true",
        help="Skip post-ingestion reconciliation checks.",
    )
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Skip Truth Bridge verification stage.",
    )
    parser.add_argument(
        "--reconciliation-report",
        default=None,
        help="Optional output path for reconciliation report JSON.",
    )
    args = parser.parse_args()

    format_key = args.format.lower()

    try:
        print(f"Registering format: {format_key}...")
        fmt_module = get_format_module(format_key)
        cfg = fmt_module.FORMAT_CONFIG

        print(f"\n{'=' * 60}")
        print(f"STARTING AUTOMATED PIPELINE: {cfg['label']}")
        print(f"{'=' * 60}")

        # Stage 1: JSON conversion
        if not args.skip_conversion:
            print(f"\n{'=' * 60}")
            print("STAGE 1: JSON CONVERSION")
            print(f"{'=' * 60}")
            from formats.odi.utils.json_converter import run_json_conversion

            run_json_conversion(
                cfg,
                strict=True,
                allow_partial=args.allow_partial_conversion,
                audit_path=cfg.get("conversion_audit_file"),
            )

        # Stage 2: Intelligence refinery
        print(f"\n{'=' * 60}")
        print("STAGE 2: INTELLIGENCE REFINERY")
        print(f"{'=' * 60}")
        from formats.odi.utils.refinery_script import rebuild_intelligence_layer

        rebuild_intelligence_layer(cfg)

        # Stage 3: DuckDB ingestion
        print(f"\n{'=' * 60}")
        print("STAGE 3: DUCKDB INGESTION")
        print(f"{'=' * 60}")
        from formats.odi.utils.ingest_to_db import run_db_ingestion

        run_db_ingestion(cfg)

        # Stage 4: Reconciliation checks
        if not args.skip_reconciliation:
            print(f"\n{'=' * 60}")
            print("STAGE 4: RECONCILIATION CHECKS")
            print(f"{'=' * 60}")
            from scripts.maintenance.etl_reconciliation_report import run_reconciliation_checks

            report_path = args.reconciliation_report or cfg.get("reconciliation_audit_file")
            run_reconciliation_checks(
                db_path=cfg["db_file"],
                source_balls_csv=cfg.get("data_file"),
                max_unresolved_venue_ratio=float(cfg.get("max_unresolved_venue_ratio", 0.25)),
                output_path=report_path,
                fail_on_error=True,
            )

        # Stage 5: Truth Bridge verification
        if not args.skip_verification:
            print(f"\n{'=' * 60}")
            print("STAGE 5: VERIFICATION (Truth Bridge)")
            print(f"{'=' * 60}")
            from formats.odi.tests.truth_bridge.run_all import run_all_verification

            try:
                run_all_verification()
            except SystemExit as exc:
                if exc.code != 0:
                    print("PIPELINE HALTED: Verification failed.")
                    raise

        print(f"\n{'=' * 60}")
        print(f"PIPELINE SUCCESS: {cfg['label']} is up to date.")
        print(f"{'=' * 60}")

    except KeyError:
        print(f"Error: Format '{format_key}' is not registered in config/format_registry.py")
        sys.exit(1)
    except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError, ImportError) as exc:
        print(f"Pipeline failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
