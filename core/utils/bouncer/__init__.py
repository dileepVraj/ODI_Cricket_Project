#!/usr/bin/env python3
"""core.utils.bouncer - compliance scanner package.

Public API: run(), main()
"""

from __future__ import annotations

import argparse  # noqa: F401
import json  # noqa: F401
import logging
from pathlib import Path

from ._shared import (  # noqa: F401
    Violation,
    _collect_manifest_literals,
    _iter_python_files,
    _resolve_scan_paths,
)
from ._scan_file import _scan_file
from ._constitutional import _scan_constitutional

logger = logging.getLogger(__name__)


def run(root: Path, raw_paths: list[str] | None = None) -> int:
    scoped_paths = _resolve_scan_paths(root, raw_paths or [])
    allowed_literals = _collect_manifest_literals(root)
    if not allowed_literals:
        logger.error("FAIL: No manifest literals discovered. Cannot run Zero-Literal rule safely.")
        return 2

    if scoped_paths:
        target_files = scoped_paths
    else:
        target_files = sorted(_iter_python_files(root))

    if (raw_paths or []) and not target_files:
        logger.error("FAIL: No Python files matched --paths scope.")
        return 2

    all_violations = _scan_constitutional(root, scoped_paths or None)
    for path in target_files:
        all_violations.extend(_scan_file(path, allowed_literals))

    if not all_violations:
        logger.info(f"PASS: 100% compliance across {len(target_files)} file(s).")
        return 0

    logger.error(f"FAIL: {len(all_violations)} violation(s) across {len(target_files)} file(s).")
    for item in sorted(all_violations, key=lambda v: (str(v.file), v.line, v.col, v.rule)):
        safe_path = str(item.file).encode("ascii", errors="backslashreplace").decode("ascii")
        safe_message = item.message.encode("ascii", errors="backslashreplace").decode("ascii")
        logger.error(f"{safe_path}:{item.line}:{item.col}: [{item.rule}] {safe_message}")
        if item.code:
            safe_code = item.code.encode("ascii", errors="backslashreplace").decode("ascii")
            logger.error(f"    {safe_code}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 12 Compliance Bouncer")
    parser.add_argument("--root", default=".", help="Project root path")
    parser.add_argument(
        "--paths",
        nargs="*",
        default=[],
        help="Optional Python files/directories to restrict scan scope",
    )
    args = parser.parse_args()
    return run(Path(args.root).resolve(), args.paths)


if __name__ == "__main__":
    raise SystemExit(main())
