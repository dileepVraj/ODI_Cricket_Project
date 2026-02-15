"""
MASTER ORCHESTRATOR: Incremental Intelligence Pipeline
Automates the flow: JSON → CSV → Intelligence Refinery → DuckDB.
Handles format isolation (ODI, T20I, IPL, etc.) based on config.

Usage:
  python scripts/update_data.py         (Update ODI - Default)
  python scripts/update_data.py t20i    (Update T20I)
"""

import os
import sys
import argparse

# Add root to sys.path for modules
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from config.format_registry import get_format_module

def main():
    parser = argparse.ArgumentParser(description="Cricket Data Intelligence Pipeline")
    parser.add_argument('format', nargs='?', default='odi', help="Format to update (odi, t20i, ipl, etc.)")
    parser.add_argument('--skip-conversion', action='store_true', help="Skip JSON to CSV conversion")
    args = parser.parse_args()

    format_key = args.format.lower()
    
    try:
        # 1. Load Format Module & Config
        print(f"🔗 Registering Format: {format_key}...")
        fmt_module = get_format_module(format_key)
        cfg = fmt_module.FORMAT_CONFIG
        
        print(f"\n{'='*60}")
        print(f"🔥 STARTING AUTOMATED PIPELINE: {cfg['label']}")
        print(f"{'='*60}")

        # 2. Stage 1: JSON to CSV Conversion
        if not args.skip_conversion:
            try:
                from formats.odi.utils.json_converter import run_json_conversion
                run_json_conversion(cfg)
            except Exception as e:
                print(f"⚠️ Warning during Stage 1 (Conversion): {e}")

        # 3. Stage 2: Intelligence Refinery (Logic & Phases)
        try:
            from formats.odi.utils.refinery_script import rebuild_intelligence_layer
            rebuild_intelligence_layer(cfg)
        except Exception as e:
            print(f"❌ Error during Stage 2 (Refinery): {e}")
            return

        # 4. Stage 3: Database Ingestion (DuckDB)
        try:
            from formats.odi.utils.ingest_to_db import run_db_ingestion
            run_db_ingestion(cfg)
        except Exception as e:
            print(f"❌ Error during Stage 3 (DuckDB): {e}")
            return

        # 5. Stage 4: Truth Bridge Verification
        print(f"\n{'='*60}")
        print(f"🧪 STAGE 4: VERIFICATION (Truth Bridge)")
        print(f"{'='*60}")
        try:
            from formats.odi.tests.truth_bridge.run_all import run_all_verification
            # We catch SystemExit to prevent immediate script termination if we want to log summary
            try:
                run_all_verification()
            except SystemExit as e:
                if e.code != 0:
                    print(f"❌ PIPELINE HALTED: Verification Failed.")
                    sys.exit(e.code)
        except ImportError:
            print("⚠️ Verification Suite not found. Skipping.")
        except Exception as e:
            print(f"❌ Error during Stage 4 (Verification): {e}")
            return

        print(f"\n{'='*60}")
        print(f"🏆 PIPELINE SUCCESS: {cfg['label']} is now Up-to-Date.")
        print(f"{'='*60}")
        
    except KeyError:
        print(f"❌ Error: Format '{format_key}' is not registered in config/format_registry.py")
    except Exception as e:
        print(f"❌ Unhandled Pipeline Error: {e}")

if __name__ == "__main__":
    main()
