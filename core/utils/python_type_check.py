#!/usr/bin/env python3
"""GATE5T Python type check using ruff and mypy."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

GATE_ID = "GATE5T"
RUFF_PATTERN = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+): (?P<rule>[A-Z0-9]+) (?P<message>.+)$"
)
MYPY_PATTERN = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+)(?::(?P<col>\d+))?: error: (?P<message>.+)$"
)


def _parse_ruff(output: str) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    for raw_line in output.splitlines():
        match = RUFF_PATTERN.match(raw_line.strip())
        if not match:
            continue
        violations.append(
            {
                "file": match.group("file"),
                "line": int(match.group("line")),
                "rule": match.group("rule"),
                "message": match.group("message"),
            }
        )
    return violations


def _parse_mypy(output: str) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    for raw_line in output.splitlines():
        match = MYPY_PATTERN.match(raw_line.strip())
        if not match:
            continue
        violations.append(
            {
                "file": match.group("file"),
                "line": int(match.group("line")),
                "rule": "MYPY_ERROR",
                "message": match.group("message"),
            }
        )
    return violations


def _load_mypy_baseline(root: Path) -> int | None:
    state_path = root / "agents" / "workflow" / "state.json"
    if not state_path.exists():
        return None
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    baseline = state.get("mypy_baseline_violations")
    if isinstance(baseline, int):
        return baseline
    return None


def _emit_json(status: str, violations: list[dict[str, object]], notes: list[str]) -> int:
    output: dict[str, object] = {
        "gate": GATE_ID,
        "triggered": True,
        "status": status,
        "violations": violations,
        "violation_count": len(violations),
    }
    if notes:
        output["notes"] = notes
    print(json.dumps(output))
    return 0 if status in {"PASS", "SKIPPED"} else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="GATE5T python type check")
    parser.add_argument("--root", default=".", help="Project root path")
    parser.add_argument("--json", action="store_true", default=False, help="Emit structured JSON output")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    notes: list[str] = []
    violations: list[dict[str, object]] = []
    ruff_path = shutil.which("ruff")
    mypy_path = shutil.which("mypy")

    if not ruff_path:
        notes.append("ruff not found - skipped")
        if args.json:
            return _emit_json("SKIPPED", violations, notes)
        print(f"{GATE_ID} - SKIPPED ({'; '.join(notes)})")
        return 0

    ruff_result = subprocess.run(
        [ruff_path, "check", "."],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        cwd=root,
    )
    violations.extend(_parse_ruff(ruff_result.stdout or ""))

    if mypy_path:
        mypy_result = subprocess.run(
            [mypy_path, "core/", "--ignore-missing-imports", "--exclude", "core/gen_ai"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            cwd=root,
        )
        mypy_violations = _parse_mypy(mypy_result.stdout or "")
        baseline = _load_mypy_baseline(root)
        if baseline is None:
            notes.append("mypy_baseline_violations missing from agents/workflow/state.json")
            violations.extend(mypy_violations)
        elif len(mypy_violations) <= baseline:
            notes.append(f"mypy violations {len(mypy_violations)} <= baseline {baseline}")
        else:
            violations.extend(mypy_violations)
    else:
        notes.append("mypy not found - skipped")

    status = "PASS" if not violations else "FAIL"
    if args.json:
        return _emit_json(status, violations, notes)

    if status == "PASS":
        if notes:
            print(f"{GATE_ID} - PASS ({'; '.join(notes)})")
        else:
            print(f"{GATE_ID} - PASS")
        return 0

    print(f"{GATE_ID} - FAIL: {len(violations)} violation(s)")
    for violation in violations:
        print(
            f"  {violation['file']}:{violation['line']}: "
            f"[{violation['rule']}] {violation['message']}"
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
