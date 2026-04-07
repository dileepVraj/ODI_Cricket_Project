#!/usr/bin/env python3
"""compliance_bouncer -- shim."""
from __future__ import annotations
import argparse
import logging
import sys
from pathlib import Path
_proj = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_proj)) if str(_proj) not in sys.path else None
from core.utils.bouncer import main, run, Violation  # noqa: E402
__all__ = ["run", "main", "Violation"]
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--paths", nargs="*", default=[])
    parser.add_argument("--json", action="store_true", default=False)
    if args := parser.parse_args():
        if args.json:
            logging.disable(logging.CRITICAL)
        rc = run(Path(args.root).resolve(), args.paths)
        if args.json:
            logging.disable(logging.NOTSET)
            payload = {"gate": "GATE6", "triggered": True, "status": "PASS" if rc == 0 else "FAIL", "violations": [], "violation_count": 0 if rc == 0 else 1}
            print(__import__("json").dumps(payload))
        sys.exit(rc)