import fnmatch
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RULES_FILE = PROJECT_ROOT / "docs" / "context" / "rules.json"


def load_rules() -> list[dict[str, Any]]:
    if not RULES_FILE.exists():
        print(f"[ERROR] Rules file not found: {RULES_FILE}")
        return []
    with RULES_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_file(filepath: Path, rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return []  # Skip binary/non-utf8 files
    except OSError as exc:
        violations.append(
            {
                "file": str(filepath),
                "line": 0,
                "rule": "FILE_READ_ERROR",
                "message": f"Could not read file: {exc}",
                "severity": "CRITICAL",
            }
        )
        return violations

    rel_path = filepath.relative_to(PROJECT_ROOT).as_posix()

    for rule in rules:
        include_patterns = rule.get("include", [])
        if include_patterns and not any(fnmatch.fnmatch(rel_path, pattern) for pattern in include_patterns):
            continue

        exclude_patterns = rule.get("exclude", [])
        if exclude_patterns and any(fnmatch.fnmatch(rel_path, pattern) for pattern in exclude_patterns):
            continue

        pattern_text = rule.get("pattern")
        if not pattern_text:
            continue

        try:
            pattern = re.compile(pattern_text)
        except re.error as exc:
            violations.append(
                {
                    "file": rel_path,
                    "line": 0,
                    "rule": rule.get("id", "INVALID_RULE"),
                    "message": f"Invalid regex pattern '{pattern_text}': {exc}",
                    "severity": "CRITICAL",
                }
            )
            continue

        for i, line in enumerate(lines, start=1):
            if pattern.search(line):
                violations.append(
                    {
                        "file": rel_path,
                        "line": i,
                        "rule": rule.get("id", "UNKNOWN_RULE"),
                        "message": rule.get("message", "Rule violation"),
                        "severity": rule.get("severity", "WARNING"),
                    }
                )

    return violations


def check_governance_docs() -> list[dict[str, Any]]:
    required_docs = [
        {"path": "docs/ai/GEMINI.md", "purpose": "Agent Protocols & Governance Rules"},
        {"path": "docs/ai/AI_MEMORY.md", "purpose": "Living Memory index"},
        {"path": "docs/context/active_state.md", "purpose": "Current architecture state"},
        {"path": "docs/context/rules.json", "purpose": "Automated linting rules"},
    ]

    violations: list[dict[str, Any]] = []
    for doc in required_docs:
        full_path = PROJECT_ROOT / doc["path"]
        if not full_path.exists():
            violations.append(
                {
                    "file": doc["path"],
                    "line": 0,
                    "rule": "GOVERNANCE_DOC_MISSING",
                    "message": (
                        f"Critical governance doc missing: {doc['path']} "
                        f"({doc['purpose']})."
                    ),
                    "severity": "CRITICAL",
                }
            )
    return violations


def _iter_python_files(root: Path) -> list[Path]:
    blocked_dirs = {"node_modules", ".git", ".venv", "__pycache__"}
    py_files: list[Path] = []
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in blocked_dirs]
        for file_name in files:
            if file_name.endswith(".py"):
                py_files.append(Path(current_root) / file_name)
    return py_files


def _write_report(lines: list[str]) -> Path | None:
    payload = "\n".join(lines)
    candidates = [
        PROJECT_ROOT / "linter_report.txt",
        Path.cwd() / "linter_report.txt",
        Path.home() / "cricket_linter_report.txt",
    ]

    for candidate in candidates:
        try:
            candidate.write_text(payload, encoding="utf-8")
            return candidate
        except OSError:
            continue

    return None


def run_linter() -> None:
    print(f"[INFO] Running context linter on: {PROJECT_ROOT}")

    rules = load_rules()
    print(f"[INFO] Loaded {len(rules)} rule(s).")

    all_violations: list[dict[str, Any]] = []

    print("[INFO] Phase 1: Governance checks...")
    all_violations.extend(check_governance_docs())

    print("[INFO] Phase 2: Code checks...")
    for py_file in _iter_python_files(PROJECT_ROOT):
        all_violations.extend(check_file(py_file, rules))

    report_lines: list[str] = []
    if all_violations:
        report_lines.append(f"[FAIL] Found {len(all_violations)} violation(s).")
        report_lines.append("")
        for v in all_violations:
            report_lines.append(f"[{v['severity']}] [{v['rule']}] {v['file']}:{v['line']}")
            report_lines.append(f"  {v['message']}")
        report_path = _write_report(report_lines)
        if report_path is not None:
            print(f"[FAIL] Found {len(all_violations)} violation(s). Report: {report_path}")
        else:
            print(f"[FAIL] Found {len(all_violations)} violation(s). No writable report path available.")
        sys.exit(1)

    report_lines.append("[OK] No violations found. Codebase is clean.")
    report_path = _write_report(report_lines)
    if report_path is not None:
        print(f"[OK] No violations found. Report: {report_path}")
    else:
        print("[OK] No violations found. No writable report path available.")
    sys.exit(0)


if __name__ == "__main__":
    run_linter()
