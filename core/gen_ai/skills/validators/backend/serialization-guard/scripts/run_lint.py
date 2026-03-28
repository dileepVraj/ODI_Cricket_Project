#!/usr/bin/env python
"""Serialization guard linter for low-latency API response paths."""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
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
    parser = argparse.ArgumentParser(description="Detect serializer memory bombs and high-latency patterns.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--paths", nargs="*", default=None, help="Optional files/directories to scan")
    parser.add_argument("--max-record-rows", type=int, default=500, help="Safety threshold for record serialization")
    parser.add_argument("--json", action="store_true", default=False, help="Emit structured JSON output instead of prose")
    return parser.parse_args()


def _line_text(lines: list[str], line_no: int) -> str:
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].rstrip("\n")
    return ""


def _iter_python_files(root: Path, explicit_paths: list[str] | None) -> Iterable[Path]:
    if explicit_paths:
        for raw in explicit_paths:
            p = (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw)
            if p.is_file() and p.suffix == ".py":
                yield p
            elif p.is_dir():
                for file in p.rglob("*.py"):
                    if any(part in EXCLUDED_DIRS for part in file.parts):
                        continue
                    yield file
        return

    for file in root.rglob("*.py"):
        if any(part in EXCLUDED_DIRS for part in file.parts):
            continue
        yield file


def _set_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "_parent", parent)


def _call_name(call: ast.Call) -> str:
    node = call.func
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    parts.reverse()
    return ".".join(parts)


def _collect_import_aliases(tree: ast.AST) -> Dict[str, str]:
    aliases: Dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.asname:
                    aliases[a.asname] = a.name
                else:
                    root = a.name.split(".")[0]
                    aliases[root] = root
        elif isinstance(node, ast.ImportFrom):
            if not node.module:
                continue
            for a in node.names:
                if a.name == "*":
                    continue
                aliases[a.asname or a.name] = f"{node.module}.{a.name}"
    return aliases


def _resolve_name(name: str, alias_map: Dict[str, str]) -> str:
    if not name:
        return name
    bits = name.split(".")
    head = bits[0]
    if head in alias_map:
        return ".".join([alias_map[head]] + bits[1:])
    return name


def _is_to_dict_records(call: ast.Call, alias_map: Dict[str, str]) -> bool:
    call_name = _resolve_name(_call_name(call), alias_map)
    if not call_name.endswith(".to_dict"):
        return False

    for arg in call.args:
        if isinstance(arg, ast.Constant) and arg.value == "records":
            return True

    for kw in call.keywords:
        if kw.arg == "orient" and isinstance(kw.value, ast.Constant) and kw.value.value == "records":
            return True
    return False


def _uses_fast_json(tree: ast.AST, alias_map: Dict[str, str]) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        call_name = _resolve_name(_call_name(node), alias_map)
        if call_name == "orjson.dumps" or call_name.endswith(".to_json"):
            return True
    return False


def _is_recursive_serializer_comp(node: ast.ListComp) -> bool:
    if not isinstance(node.elt, ast.Call):
        return False
    name = _call_name(node.elt)
    return name in {"serialize_engine_output", "serialize_output", "serialize"} or name.endswith(".serialize_engine_output")


def _ancestor_chain(node: ast.AST) -> list[ast.AST]:
    chain: list[ast.AST] = []
    cur = getattr(node, "_parent", None)
    while cur is not None:
        chain.append(cur)
        cur = getattr(cur, "_parent", None)
    return chain


def _inside_numpy_branch(node: ast.AST, alias_map: Dict[str, str]) -> bool:
    for ancestor in _ancestor_chain(node):
        if not isinstance(ancestor, ast.If):
            continue
        test = ancestor.test
        if isinstance(test, ast.Call) and _call_name(test) == "isinstance" and len(test.args) >= 2:
            type_arg = test.args[1]
            if isinstance(type_arg, ast.Attribute):
                if _resolve_name(_call_name(ast.Call(func=type_arg, args=[], keywords=[])), alias_map) in {"numpy.ndarray", "np.ndarray"}:
                    return True
            if isinstance(type_arg, ast.Tuple):
                for elt in type_arg.elts:
                    if isinstance(elt, ast.Attribute):
                        text = _resolve_name(_call_name(ast.Call(func=elt, args=[], keywords=[])), alias_map)
                        if text in {"numpy.ndarray", "np.ndarray"}:
                            return True
    return False


class SerializationVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, lines: list[str], alias_map: Dict[str, str], row_threshold: int, has_fast_json: bool) -> None:
        self.path = path
        self.lines = lines
        self.alias_map = alias_map
        self.row_threshold = row_threshold
        self.has_fast_json = has_fast_json
        self.violations: list[Violation] = []

    def _add(self, node: ast.AST, rule: str, message: str) -> None:
        line = getattr(node, "lineno", 0)
        self.violations.append(
            Violation(
                path=self.path,
                line=line,
                col=getattr(node, "col_offset", 0),
                rule=rule,
                message=message,
                code=_line_text(self.lines, line),
            )
        )

    def visit_Call(self, node: ast.Call) -> None:
        if _is_to_dict_records(node, self.alias_map):
            self._add(
                node,
                "MEMORY_BOMB_RECORDS",
                (
                    f"High Latency Risk: DataFrame .to_dict('records') without explicit <= {self.row_threshold} row gate"
                ),
            )
            if not self.has_fast_json:
                self._add(
                    node,
                    "FAST_PATH_MISSING",
                    "High Latency Risk: no orjson.dumps(...) or vectorized DataFrame.to_json(...) fast path detected",
                )
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        if _is_recursive_serializer_comp(node):
            self._add(
                node,
                "HIGH_LATENCY_RECURSIVE_COMP",
                "High Latency Risk: recursive list comprehension in serializer hot path",
            )

        if _inside_numpy_branch(node, self.alias_map):
            self._add(
                node,
                "NUMPY_ELEMENTWISE_LOOP",
                "High Latency Risk: element-wise NumPy serialization loop; use vectorized casting/to_json",
            )
        self.generic_visit(node)


def lint_file(path: Path, row_threshold: int) -> List[Violation]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)
    except (OSError, SyntaxError):
        return []

    _set_parents(tree)
    alias_map = _collect_import_aliases(tree)
    has_fast_json = _uses_fast_json(tree, alias_map)
    visitor = SerializationVisitor(
        path=path,
        lines=text.splitlines(),
        alias_map=alias_map,
        row_threshold=row_threshold,
        has_fast_json=has_fast_json,
    )
    visitor.visit(tree)

    deduped: list[Violation] = []
    seen: set[tuple[int, int, str]] = set()
    for v in visitor.violations:
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
        violations.extend(lint_file(file_path, row_threshold=args.max_record_rows))

    if args.json:
        output = {
            "gate": "GATE4",
            "triggered": True,
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
