#!/usr/bin/env python3
"""GATE5P paradigm sentinel that aggregates GATE1 and GATE6."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE1_SCRIPT = ROOT / "utils/boundary_sentinel.py"
GATE6_SCRIPT = ROOT / "utils/compliance_bouncer.py"
GATE_SRP_SCRIPT = ROOT / "utils/srp_sentinel.py"


def _parse_gate_output(stdout: str, stderr: str, gate_name: str) -> dict[str, object]:
    try:
        return json.loads(stdout.strip())
    except json.JSONDecodeError:
        message = stdout.strip() or stderr.strip() or "Gate emitted invalid JSON."
        return {
            "gate": gate_name,
            "triggered": True,
            "status": "FAIL",
            "violations": [
                {
                    "file": None,
                    "line": None,
                    "rule": "PARSE_ERROR",
                    "message": message[:500],
                }
            ],
            "violation_count": 1,
        }


def run_gate(script: Path, extra_args: list[str], gate_name: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(script), "--json", *extra_args],
        capture_output=True,
        text=True,
        check=False,
    )
    return _parse_gate_output(result.stdout, result.stderr, gate_name)


def _gate_args(root: str, paths: list[str], default_paths: list[str] | None = None) -> list[str]:
    args: list[str] = ["--root", root]
    effective_paths = paths or (default_paths or [])
    if effective_paths:
        args.extend(["--paths", *effective_paths])
    return args


def main() -> int:
    parser = argparse.ArgumentParser(description="GATE5P paradigm sentinel")
    parser.add_argument("--root", default=".", help="Project root path")
    parser.add_argument("--json", action="store_true", default=False, help="Emit structured JSON output")
    parser.add_argument("--paths", nargs="*", default=[], help="Optional Python files/directories to restrict scope")
    args = parser.parse_args()

    gate1 = run_gate(GATE1_SCRIPT, _gate_args(args.root, args.paths, ["core/"]), "GATE1")
    gate6 = run_gate(GATE6_SCRIPT, _gate_args(args.root, args.paths), "GATE6")
    gate_srp = run_gate(GATE_SRP_SCRIPT, _gate_args(args.root, args.paths), "GATE_SRP")
    srp_findings = list(gate_srp.get("violations", []))
    all_violations = list(gate1.get("violations", [])) + list(gate6.get("violations", []))
    status = "PASS" if not all_violations else "FAIL"

    if args.json:
        print(
            json.dumps(
                {
                    "gate": "GATE5P",
                    "triggered": True,
                    "status": status,
                    "violations": all_violations,
                    "violation_count": len(all_violations),
                    "srp_advisory": srp_findings,
                }
            )
        )
        return 0 if status == "PASS" else 1

    print("GATE5P - paradigm-sentinel")
    print(f"  GATE1 (boundary): {gate1.get('status', 'FAIL')}")
    print(f"  GATE6 (bouncer): {gate6.get('status', 'FAIL')}")
    print(f"  GATE_SRP (advisory): {len(srp_findings)} finding(s)")
    print(f"GATE5P - {status}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
