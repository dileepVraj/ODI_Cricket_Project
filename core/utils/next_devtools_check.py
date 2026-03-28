#!/usr/bin/env python3
"""GATEF4 next-devtools check placeholder."""

from __future__ import annotations

import argparse
import json

NOTE = "next-devtools MCP not available - manual check required"


def main() -> int:
    parser = argparse.ArgumentParser(description="GATEF4 next-devtools check")
    parser.add_argument("--root", default=".", help="Project root path")
    parser.add_argument("--json", action="store_true", default=False, help="Emit structured JSON output")
    args = parser.parse_args()

    if args.json:
        print(
            json.dumps(
                {
                    "gate": "GATEF4",
                    "triggered": True,
                    "status": "SKIPPED",
                    "violations": [],
                    "violation_count": 0,
                    "note": NOTE,
                }
            )
        )
    else:
        print(f"GATEF4 - SKIPPED ({NOTE})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
