#!/usr/bin/env python
"""DOD anti-pattern linter for pandas-heavy codebases."""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

ITERATION_BANNED = {"iterrows", "itertuples"}
DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
}


@dataclass
class Violation:
    path: Path
    line: int
    col: int
    code: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan for pandas Data-Oriented Design anti-patterns.")
    parser.add_argument("--root", default=".", help="Project root to scan")
    parser.add_argument("--paths", nargs="*", default=None, help="Optional specific files/directories")
    parser.add_argument("--json", action="store_true", default=False, help="Emit structured JSON output instead of prose")
    return parser.parse_args()


def _is_df_name(name: str) -> bool:
    lower = name.lower()
    return lower == "df" or lower.endswith("_df") or lower.startswith("df_")


def _contains_df_signal(node: ast.AST) -> bool:
    if isinstance(node, ast.Name):
        return _is_df_name(node.id)
    if isinstance(node, ast.Attribute):
        if node.attr in {"loc", "iloc", "index", "values", "columns", "groupby", "apply", "map"}:
            return _contains_df_signal(node.value)
        return _contains_df_signal(node.value)
    if isinstance(node, ast.Subscript):
        return _contains_df_signal(node.value)
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in {"groupby", "apply", "map", "filter", "sort_values", "iterrows", "itertuples"}:
                return _contains_df_signal(node.func.value)
            return _contains_df_signal(node.func.value)
        return any(_contains_df_signal(arg) for arg in node.args)
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return any(_contains_df_signal(elt) for elt in node.elts)
    return False


def _for_iter_is_df_loop(iter_node: ast.AST) -> bool:
    if _contains_df_signal(iter_node):
        return True

    # range(len(df_like))
    if isinstance(iter_node, ast.Call) and isinstance(iter_node.func, ast.Name):
        if iter_node.func.id in {"range", "enumerate"} and iter_node.args:
            first = iter_node.args[0]
            if isinstance(first, ast.Call) and isinstance(first.func, ast.Name) and first.func.id == "len" and first.args:
                return _contains_df_signal(first.args[0])
            return _contains_df_signal(first)
    return False


class DODVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source_lines: List[str]) -> None:
        self.path = path
        self.source_lines = source_lines
        self.violations: List[Violation] = []

    def _line_text(self, line_no: int) -> str:
        if 1 <= line_no <= len(self.source_lines):
            return self.source_lines[line_no - 1].rstrip("\n")
        return ""

    def _add(self, node: ast.AST, message: str) -> None:
        self.violations.append(
            Violation(
                path=self.path,
                line=getattr(node, "lineno", 0),
                col=getattr(node, "col_offset", 0),
                code=self._line_text(getattr(node, "lineno", 0)),
                message=message,
            )
        )

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and node.func.attr in ITERATION_BANNED:
            self._add(node, f"Forbidden pandas row iteration: .{node.func.attr}()")
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        if _for_iter_is_df_loop(node.iter):
            self._add(node, "Manual Python for-loop over DataFrame-like data; use vectorized pandas/NumPy operations")
        self.generic_visit(node)


def _iter_python_files(root: Path, explicit_paths: list[str] | None) -> Iterable[Path]:
    if explicit_paths:
        for raw in explicit_paths:
            path = (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw)
            if path.is_file() and path.suffix == ".py":
                yield path
            elif path.is_dir():
                for file in path.rglob("*.py"):
                    if not any(part in DEFAULT_EXCLUDES for part in file.parts):
                        yield file
        return

    for file in root.rglob("*.py"):
        if any(part in DEFAULT_EXCLUDES for part in file.parts):
            continue
        yield file


def lint_file(path: Path) -> List[Violation]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)
    except (SyntaxError, OSError):
        return []

    visitor = DODVisitor(path=path, source_lines=text.splitlines())
    visitor.visit(tree)
    return visitor.violations


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    violations: List[Violation] = []
    for file_path in _iter_python_files(root, args.paths):
        violations.extend(lint_file(file_path))

    if args.json:
        output = {
            "gate": "GATE2",
            "triggered": True,
            "status": "PASS" if not violations else "FAIL",
            "violations": [
                {
                    "file": str(v.path.relative_to(root)) if v.path.is_absolute() else str(v.path),
                    "line": v.line,
                    "rule": "DOD_VIOLATION",
                    "message": v.message,
                }
                for v in violations
            ],
            "violation_count": len(violations),
        }
        print(json.dumps(output))
        return 0 if not violations else 1

    if not violations:
        print("DOD lint passed: no DataFrame anti-patterns detected.")
        return 0

    print(f"DOD lint failed: {len(violations)} violation(s) detected.")
    for v in violations:
        try:
            rel = v.path.relative_to(root)
        except ValueError:
            rel = v.path
        print(f"{rel}:{v.line}:{v.col}: {v.message}")
        if v.code:
            print(f"  {v.code}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
