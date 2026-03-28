#!/usr/bin/env python3
"""GATE1 wrapper that delegates to the boundary sentinel script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REAL_SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "gen_ai/skills/validators/backend/boundary-sentinel/scripts/run_sentinel.py"
)


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(REAL_SCRIPT), *sys.argv[1:]],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
