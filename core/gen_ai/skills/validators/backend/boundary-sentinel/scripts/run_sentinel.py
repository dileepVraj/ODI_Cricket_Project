#!/usr/bin/env python
"""Boundary Sentinel: enforce Core-layer isolation using AST checks."""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

FORBIDDEN_IMPORT_ROOTS = {"api", "frontend"}
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


@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    col: int
    rule: str
    message: str
    code: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Boundary sentinel for core/ layer leakage checks.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--paths", nargs="*", default=None, help="Optional specific files/directories")
    parser.add_argument("--json", action="store_true", default=False, help="Emit structured JSON output instead of prose")
    return parser.parse_args()


def _line_text(lines: list[str], line_no: int) -> str:
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].rstrip("\n")
    return ""


def _iter_python_files(root: Path, explicit_paths: list[str] | None) -> Iterable[Path]:
    if explicit_paths:
        for raw in explicit_paths:
            path = (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw)
            if path.is_file() and path.suffix == ".py":
                yield path
            elif path.is_dir():
                for file in path.rglob("*.py"):
                    if any(part in DEFAULT_EXCLUDES for part in file.parts):
                        continue
                    yield file
        return

    core_dir = root / "core"
    if not core_dir.exists():
        return
    for file in core_dir.rglob("*.py"):
        if any(part in DEFAULT_EXCLUDES for part in file.parts):
            continue
        yield file


def _scan_import_block(tree: ast.Module, path: Path, lines: list[str]) -> List[Violation]:
    violations: list[Violation] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORT_ROOTS:
                    violations.append(
                        Violation(
                            path=path,
                            line=node.lineno,
                            col=node.col_offset,
                            rule="CORE_FORBIDDEN_IMPORT",
                            message=f"Forbidden cross-layer import root '{root}' in core/",
                            code=_line_text(lines, node.lineno),
                        )
                    )
        elif isinstance(node, ast.ImportFrom):
            if not node.module:
                continue
            root = node.module.split(".")[0]
            if root in FORBIDDEN_IMPORT_ROOTS:
                violations.append(
                    Violation(
                        path=path,
                        line=node.lineno,
                        col=node.col_offset,
                        rule="CORE_FORBIDDEN_IMPORT",
                        message=f"Forbidden cross-layer import root '{root}' in core/",
                        code=_line_text(lines, node.lineno),
                    )
                )
    return violations


class _ClassBodyVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, lines: list[str]) -> None:
        self.path = path
        self.lines = lines
        self.violations: list[Violation] = []

    def _add(self, node: ast.AST, rule: str, message: str) -> None:
        line_no = getattr(node, "lineno", 0)
        self.violations.append(
            Violation(
                path=self.path,
                line=line_no,
                col=getattr(node, "col_offset", 0),
                rule=rule,
                message=message,
                code=_line_text(self.lines, line_no),
            )
        )

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name) and node.value.id == "self" and node.attr == "dal":
            self._add(node, "CORE_DAL_COUPLING", "Forbidden DAL coupling in core/: self.dal usage detected")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "connect"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "duckdb"
        ):
            self._add(node, "CORE_DUCKDB_CONNECT", "Forbidden raw duckdb.connect(...) in core/")
        self.generic_visit(node)


def _scan_class_bodies(tree: ast.Module, path: Path, lines: list[str]) -> List[Violation]:
    visitor = _ClassBodyVisitor(path=path, lines=lines)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                visitor.visit(item)
    return visitor.violations


def lint_file(path: Path) -> List[Violation]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)
    except (SyntaxError, OSError):
        return []

    lines = text.splitlines()
    violations: list[Violation] = []
    violations.extend(_scan_import_block(tree, path, lines))
    violations.extend(_scan_class_bodies(tree, path, lines))

    seen: set[tuple[int, int, str]] = set()
    deduped: list[Violation] = []
    for v in violations:
        key = (v.line, v.col, v.rule)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(v)
    return deduped


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    violations: list[Violation] = []

    for file_path in _iter_python_files(root, args.paths):
        rel_parts = file_path.relative_to(root).parts if file_path.is_absolute() else file_path.parts
        if "core" not in rel_parts:
            continue
        violations.extend(lint_file(file_path))

    if args.json:
        output = {
            "gate": "GATE1",
            "status": "PASS" if not violations else "FAIL",
            "violations": [
                {
                    "file": str(v.path.relative_to(root)) if v.path.is_absolute() else str(v.path),
                    "line": v.line,
                    "rule": v.rule,
                    "message": v.message,
                }
                for v in violations
            ],
            "violation_count": len(violations),
        }
        print(json.dumps(output))
        return 0 if not violations else 1

    if not violations:
        print("Pass")
        return 0

    print(f"Fail: {len(violations)} violation(s) detected.")
    for v in violations:
        try:
            rel = v.path.relative_to(root)
        except ValueError:
            rel = v.path
        print(f"{rel}:{v.line}:{v.col}: [{v.rule}] {v.message}")
        if v.code:
            print(f"  {v.code}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
