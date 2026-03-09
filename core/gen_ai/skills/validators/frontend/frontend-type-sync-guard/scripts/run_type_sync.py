#!/usr/bin/env python3
"""
Frontend Type Sync Guard — run_type_sync.py
Validates @schema JSDoc compliance for all interfaces in frontend/lib/*.ts files.
Usage: python run_type_sync.py --root <project_root>
"""

import re
import sys
import argparse
from pathlib import Path


INTERFACE_PATTERN = re.compile(r'^export\s+interface\s+(\w+)')
SCHEMA_TAG_PATTERN = re.compile(r'@schema\s+\w+')
EXEMPT_TAG_PATTERN = re.compile(r'@schema-exempt\b')


def check_types_file(types_path: Path) -> list[tuple[int, str, str]]:
    """
    Returns list of (line_number, interface_name, message) for each violation.
    """
    if not types_path.exists():
        return [(0, str(types_path.name), f"[MISSING] {types_path.name} not found — cannot validate")]

    try:
        lines = types_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:
        return [(0, str(types_path.name), f"[READ ERROR] {e}")]

    violations: list[tuple[int, str, str]] = []

    for i, line in enumerate(lines, 1):
        m = INTERFACE_PATTERN.match(line.strip())
        if not m:
            continue
        interface_name = m.group(1)

        # Search the preceding comment block (up to 10 lines back)
        search_start = max(0, i - 11)
        block = "\n".join(lines[search_start:i - 1])

        if not SCHEMA_TAG_PATTERN.search(block) and not EXEMPT_TAG_PATTERN.search(block):
            violations.append((
                i,
                interface_name,
                f"[RULE 2.2D-R3] Interface '{interface_name}' missing @schema JSDoc"
            ))

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Frontend Type Sync Guard")
    parser.add_argument("--root", default=".", help="Project root directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    EXCLUDED_DIRS = {"node_modules", ".next", "dist", "build", ".turbo", "coverage"}

    lib_dir = root / "frontend" / "lib"
    if not lib_dir.exists():
        print("WARN: frontend/lib/ not found — skipping type sync check")
        return 0

    lib_files = sorted([
        f for f in lib_dir.rglob("*.ts")
        if not any(part in EXCLUDED_DIRS for part in f.parts)
    ])

    if not lib_files:
        print("WARN: No .ts files found in frontend/lib/ — skipping type sync check")
        return 0

    all_violations: list[tuple[Path, int, str, str]] = []
    for lib_file in lib_files:
        for line_no, name, msg in check_types_file(lib_file):
            all_violations.append((lib_file, line_no, name, msg))

    if not all_violations:
        print("PASS: zero violations")
        return 0

    print(f"FAIL: {len(all_violations)} violation(s) found\n")
    for lib_file, line_no, name, msg in all_violations:
        rel = lib_file.relative_to(root)
        print(msg)
        print(f"  {rel}:{line_no}:1")

    return 1


if __name__ == "__main__":
    sys.exit(main())
