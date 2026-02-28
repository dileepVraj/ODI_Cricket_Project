#!/usr/bin/env python
"""AST linter for async event-state safety in service/scraper modules."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

BLOCKED_DIRS = {
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

REQUESTS_BLOCKING = {"get", "post", "put", "patch", "delete", "request", "head", "options"}
IO_LIKE_SUFFIXES = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "request",
    "connect",
    "open",
    "read",
    "write",
    "recv",
    "send",
    "sleep",
    "fetch",
}
IO_LIKE_ROOTS = {"requests", "httpx", "aiohttp", "aiofiles", "asyncio", "duckdb"}


@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    col: int
    rule: str
    message: str
    code: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint files for event-loop blocking and async state discipline.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--paths", nargs="*", default=None, help="Optional files/directories to scan")
    return parser.parse_args()


def _line_text(lines: list[str], line: int) -> str:
    if 1 <= line <= len(lines):
        return lines[line - 1].rstrip("\n")
    return ""


def _iter_python_files(root: Path, explicit_paths: list[str] | None) -> Iterable[Path]:
    if explicit_paths:
        for raw in explicit_paths:
            path = (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw)
            if path.is_file() and path.suffix == ".py":
                yield path
            elif path.is_dir():
                for file in path.rglob("*.py"):
                    if any(part in BLOCKED_DIRS for part in file.parts):
                        continue
                    yield file
        return

    for file in root.rglob("*.py"):
        if any(part in BLOCKED_DIRS for part in file.parts):
            continue
        yield file


def _set_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "_parent", parent)


def _is_awaited(node: ast.AST) -> bool:
    return isinstance(getattr(node, "_parent", None), ast.Await)


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


def _is_state_class(name: str) -> bool:
    return name.lower().endswith("state") or name.lower().startswith("state")


def _inherits_basemodel(class_node: ast.ClassDef, alias_map: Dict[str, str]) -> bool:
    for base in class_node.bases:
        if isinstance(base, ast.Name):
            resolved = alias_map.get(base.id, base.id)
            if resolved in {"BaseModel", "pydantic.BaseModel"}:
                return True
        if isinstance(base, ast.Attribute) and base.attr == "BaseModel":
            root = base.value.id if isinstance(base.value, ast.Name) else ""
            resolved_root = alias_map.get(root, root)
            if resolved_root in {"pydantic", "pydantic.BaseModel"}:
                return True
    return False


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
                local = a.asname or a.name
                aliases[local] = f"{node.module}.{a.name}"
    return aliases


def _resolve_call_name(call_name: str, alias_map: Dict[str, str]) -> str:
    if not call_name:
        return call_name
    parts = call_name.split(".")
    head = parts[0]
    resolved_head = alias_map.get(head)
    if resolved_head:
        return ".".join([resolved_head] + parts[1:])
    return call_name


def _is_await_asyncio_sleep(call: ast.Call, alias_map: Dict[str, str]) -> bool:
    resolved = _resolve_call_name(_call_name(call), alias_map)
    return resolved == "asyncio.sleep"


def _contains_await_asyncio_sleep(node: ast.AST, alias_map: Dict[str, str]) -> bool:
    for child in ast.walk(node):
        if not isinstance(child, ast.Await):
            continue
        value = child.value
        if isinstance(value, ast.Call) and _is_await_asyncio_sleep(value, alias_map):
            return True
    return False


def _is_blocking_call(call_name: str) -> tuple[str, str] | None:
    if call_name == "time.sleep":
        return "BLOCKING_TIME_SLEEP", "Blocking call detected: time.sleep(...)"
    if call_name.startswith("requests."):
        method = call_name.split(".")[-1]
        if method in REQUESTS_BLOCKING:
            return "BLOCKING_REQUESTS_CALL", f"Blocking HTTP call detected: {call_name}(...)"
    if call_name == "duckdb.connect":
        return "BLOCKING_DUCKDB_CONNECT", "Blocking DB connection detected: duckdb.connect(...)"
    return None


def _is_io_like_call(call_name: str) -> bool:
    if not call_name:
        return False
    bits = call_name.split(".")
    if len(bits) == 1:
        return bits[0] in {"open"}
    root = bits[0]
    leaf = bits[-1]
    return root in IO_LIKE_ROOTS and leaf in IO_LIKE_SUFFIXES


class EventStateVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source_lines: list[str], alias_map: Dict[str, str]) -> None:
        self.path = path
        self.lines = source_lines
        self.alias_map = alias_map
        self.violations: list[Violation] = []
        self._fn_stack: list[ast.AST] = []

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

    def _current_fn(self) -> ast.AST | None:
        return self._fn_stack[-1] if self._fn_stack else None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if _is_state_class(node.name) and not _inherits_basemodel(node, self.alias_map):
            self._add(
                node,
                "STATE_MODEL_NOT_BASEMODEL",
                f"State class '{node.name}' must inherit pydantic.BaseModel",
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._fn_stack.append(node)
        self.generic_visit(node)
        self._fn_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._fn_stack.append(node)
        self.generic_visit(node)
        self._fn_stack.pop()

    def visit_While(self, node: ast.While) -> None:
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            if not _contains_await_asyncio_sleep(node, self.alias_map):
                self._add(
                    node,
                    "EVENT_LOOP_STARVATION_RISK",
                    "while True loop missing await asyncio.sleep(...), may starve event loop",
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = _resolve_call_name(_call_name(node), self.alias_map)
        current_fn = self._current_fn()
        is_async_fn = isinstance(current_fn, ast.AsyncFunctionDef)
        is_sync_fn = isinstance(current_fn, ast.FunctionDef)

        blocking = _is_blocking_call(call_name)
        if blocking is not None:
            rule, message = blocking
            self._add(node, rule, message)

        if _is_io_like_call(call_name):
            if is_sync_fn:
                fn_name = getattr(current_fn, "name", "<module>")
                self._add(
                    node,
                    "IO_IN_SYNC_FUNCTION",
                    f"Function '{fn_name}' performs I/O but is not async",
                )
            if is_async_fn and not _is_awaited(node):
                self._add(
                    node,
                    "MISSING_AWAIT_ON_IO",
                    f"I/O call '{call_name}(...)' in async function must be awaited",
                )

        self.generic_visit(node)


def lint_file(path: Path) -> List[Violation]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)
    except (SyntaxError, OSError):
        return []

    _set_parents(tree)
    alias_map = _collect_import_aliases(tree)
    visitor = EventStateVisitor(path=path, source_lines=text.splitlines(), alias_map=alias_map)
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
        violations.extend(lint_file(file_path))

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
