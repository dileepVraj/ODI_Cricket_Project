#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Finding:
    file: str
    line: int
    col: int
    rule: str
    message: str


def parse_findings(output: str) -> list[Finding]:
    rx = re.compile(r"^(.*):(\d+):(\d+):\s+\[([^\]]+)\]\s+(.*)$", re.M)
    findings: list[Finding] = []
    for f, ln, col, rule, msg in rx.findall(output):
        findings.append(Finding(file=f, line=int(ln), col=int(col), rule=rule, message=msg))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    cmd = [sys.executable, str(root / "core/utils/compliance_bouncer.py"), "--root", str(root)]
    proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    output = (proc.stdout or "") + (proc.stderr or "")
    findings = parse_findings(output)

    if proc.returncode != 0:
        print("HARD_FAIL")
        if findings:
            print(f"Violations: {len(findings)}")
            print("Plan:")
            for item in findings[:30]:
                print(f"- Fix {item.file}:{item.line}:{item.col} [{item.rule}] {item.message}")
        else:
            print("Violations: unresolved parse failure with non-zero bouncer exit.")
            print("Plan:")
            print("- Re-run compliance-bouncer and parse raw FAIL lines by file:line:col.")
            print("- Fix all reported violations, then rerun executive-auditor.")
        print("Task Complete status is forbidden until compliance-bouncer returns 100% PASS.")
        return 1

    print("PASS_100")
    print("Compliance clean. Completion status allowed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
