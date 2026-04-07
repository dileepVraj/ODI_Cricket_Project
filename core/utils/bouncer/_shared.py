#!/usr/bin/env python3
"""Phase 12 Compliance Bouncer.

AST-based governance linter enforcing:
- ZERO_LITERAL: Hardcoded literals not
  declared in manifest registries
- ANTI_ANY: Any/object in type signatures
- MISSING_RETURN_TYPE: Missing return
  annotations
- IO_AIR_GAP: File/OS I/O in engine
  execute paths
- PRESENTATION_PURITY: UI strings in
  service layer (formatters exempt)
- DOD_VIOLATION: Scalar loops
  (.iterrows/.itertuples forbidden)
- BOUNDARY_VIOLATION: Infrastructure
  imports in Domain Core files
- CONSTITUTIONAL_VISUAL_SILENCE: Visual
  tokens in core/
- CONSTITUTIONAL_TYPED_TRUTH: Deprecated
  imports in engines and calculators
- CONSTITUTIONAL_ANTI_GREASE:
  Dict[str,Any]/object in signatures
"""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

RULE_ZERO_LITERAL = "ZERO_LITERAL"
RULE_ANTI_ANY = "ANTI_ANY"
RULE_MISSING_RETURN = "MISSING_RETURN_TYPE"
RULE_IO_AIR_GAP = "IO_AIR_GAP"
RULE_PRESENTATION = "PRESENTATION_PURITY"
RULE_DOD = "DOD_VIOLATION"
RULE_BOUNDARY = "BOUNDARY_VIOLATION"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")
RULE_CONST_VISUAL = "CONSTITUTIONAL_VISUAL_SILENCE"
RULE_CONST_TYPED = "CONSTITUTIONAL_TYPED_TRUTH"
RULE_CONST_GREASE = "CONSTITUTIONAL_ANTI_GREASE"

FORBIDDEN_INFRASTRUCTURE_IMPORTS: frozenset[str] = frozenset({
    "duckdb",
    "fastapi",
    "flask",
    "django",
    "httpx",
    "requests",
    "sqlalchemy",
    "aiohttp",
})

UI_TOKENS = (
    "placeholder",
    "dropdown",
    "button",
    "tooltip",
    "sidebar",
    "frontend",
    "emoji",
    "render",
    "table",
    "card",
    "pixel",
    "click",
    "html",
    "n/a",
    "dnb",
    "bat form",
    "bowl form",
    "not out",
    "no data",
    "unavailable",
)

ALLOWED_TECHNICAL_STRINGS = {
    "",
    "__main__",
}

ALLOWED_TECHNICAL_NUMBERS = {0, 1}

VISUAL_SILENCE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("emoji_u2705", re.compile("\\u2705")),
    ("emoji_u2614", re.compile("\\u2614")),
    ("token_included", re.compile(r"\\bInclud" r"ed\\b", re.IGNORECASE)),
    ("token_excluded", re.compile(r"\\bExclud" r"ed\\b", re.IGNORECASE)),
    ("token_last_5", re.compile(r"\\bLast" r"\\s+5\\b", re.IGNORECASE)),
)

DEPRECATED_SYMBOLS: frozenset[str] = frozenset({
    "MatchIntelligenceData",
})

ANTI_GREASE_SIGNATURE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "dict_str_any_param",
        re.compile(
            r"(?ms)^\\s*(?:async\\s+)?def\\s+\\w+\\s*\\([^)]*dict\\s*\\[\\s*str\\s*,\\s*Any\\s*\\][^)]*\\)\\s*(?:->\\s*[^:]+)?\\s*:"
        ),
    ),
    (
        "dict_str_any_return",
        re.compile(
            r"(?ms)^\\s*(?:async\\s+)?def\\s+\\w+\\s*\\([^)]*\\)\\s*->\\s*[^:\\n]*dict\\s*\\[\\s*str\\s*,\\s*Any\\s*\\][^:\\n]*:"
        ),
    ),
    (
        "object_param",
        re.compile(
            r"(?ms)^\\s*(?:async\\s+)?def\\s+\\w+\\s*\\([^)]*\\bobject\\b[^)]*\\)\\s*(?:->\\s*[^:]+)?\\s*:"
        ),
    ),
    (
        "object_return",
        re.compile(r"(?ms)^\\s*(?:async\\s+)?def\\s+\\w+\\s*\\([^)]*\\)\\s*->\\s*[^:\\n]*\\bobject\\b[^:\\n]*:"),
    ),
)


@dataclass(frozen=True)
class Violation:
    file: Path
    line: int
    col: int
    rule: str
    message: str
    code: str


def _literal_key(value: object) -> tuple[str, str] | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float, str)):
        return (type(value).__name__, repr(value))
    return None


def _iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        parts = {p.lower() for p in path.parts}
        if (
            "engines" in parts
            or "services" in parts
            or "calculators" in parts
        ):
            yield path


def _resolve_scan_paths(root: Path, raw_paths: list[str]) -> list[Path]:
    if not raw_paths:
        return []
    resolved: set[Path] = set()
    for raw_path in raw_paths:
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = (root / candidate).resolve()
        else:
            candidate = candidate.resolve()
        if candidate.is_file() and candidate.suffix == ".py":
            resolved.add(candidate)
        elif candidate.is_dir():
            for nested in candidate.rglob("*.py"):
                resolved.add(nested.resolve())
    return sorted(resolved)


def _is_formatter_file(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    if "formatters" in parts:
        return True
    return "formatter" in path.stem.lower()


def _iter_manifest_files(root: Path) -> list[Path]:
    manifests = sorted(root.glob("formats/*/manifest.py"))
    if manifests:
        return manifests
    return sorted(root.rglob("manifest.py"))


def _first_docstring_node(body: list[ast.stmt]) -> ast.Constant | None:
    if not body:
        return None
    first = body[0]
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
        return first.value
    return None


def _docstring_nodes(tree: ast.AST) -> set[int]:
    nodes: set[int] = set()

    if isinstance(tree, ast.Module):
        doc = _first_docstring_node(tree.body)
        if doc is not None:
            nodes.add(id(doc))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = _first_docstring_node(node.body)
            if doc is not None:
                nodes.add(id(doc))
    return nodes


def _all_nodes(tree: ast.AST) -> set[int]:
    nodes: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not (isinstance(target, ast.Name) and target.id == "__all__"):
                continue
            if not isinstance(node.value, ast.List):
                continue
            for elt in node.value.elts:
                if isinstance(elt, ast.Constant):
                    nodes.add(id(elt))
    return nodes


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _line_col_from_offset(src: str, offset: int) -> tuple[int, int]:
    line = src.count("\n", 0, offset) + 1
    last_newline = src.rfind("\n", 0, offset)
    col = offset - (last_newline + 1) + 1
    return line, col


def _code_line(lines: list[str], line: int) -> str:
    return lines[line - 1].strip() if 1 <= line <= len(lines) else ""


def _safe_parse(path: Path) -> tuple[ast.AST | None, list[str], str | None]:
    src = _read_text(path)
    lines = src.splitlines()
    try:
        return ast.parse(src, filename=str(path)), lines, None
    except SyntaxError as exc:
        return None, lines, f"SyntaxError: {exc}"


def _collect_manifest_literals(root: Path) -> set[tuple[str, str]]:
    allowed: set[tuple[str, str]] = set()
    for manifest_path in _iter_manifest_files(root):
        tree, _, parse_err = _safe_parse(manifest_path)
        if tree is None:
            if parse_err:
                logger.warning(f"[WARN] Could not parse manifest {manifest_path}: {parse_err}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                key = _literal_key(node.value)
                if key is not None:
                    allowed.add(key)
    return allowed


def _annotation_has_any(node: ast.AST | None) -> bool:
    if node is None:
        return False
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and sub.id == "Any":
            return True
        if isinstance(sub, ast.Attribute) and sub.attr == "Any":
            return True
    return False


def _call_name(call: ast.Call) -> str:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        chunks: list[str] = [func.attr]
        parent = func.value
        while isinstance(parent, ast.Attribute):
            chunks.append(parent.attr)
            parent = parent.value
        if isinstance(parent, ast.Name):
            chunks.append(parent.id)
        chunks.reverse()
        return ".".join(chunks)
    return "<unknown>"


def _root_name(node: ast.AST) -> str | None:
    current = node
    while isinstance(current, ast.Attribute):
        current = current.value
    if isinstance(current, ast.Name):
        return current.id
    return None


def _is_literal_allowed_by_policy(value: object) -> bool:
    if isinstance(value, str) and value in ALLOWED_TECHNICAL_STRINGS:
        return True
    if isinstance(value, (int, float)) and value in ALLOWED_TECHNICAL_NUMBERS:
        return True
    return False


def _record(
    output: list[Violation],
    path: Path,
    lines: list[str],
    node: ast.AST,
    rule: str,
    message: str,
) -> None:
    line = getattr(node, "lineno", 1)
    col = getattr(node, "col_offset", 0)
    src_line = _code_line(lines, line)
    output.append(Violation(path, line, col + 1, rule, message, src_line))


def _record_regex_match(
    output: list[Violation],
    path: Path,
    lines: list[str],
    src: str,
    match: re.Match[str],
    rule: str,
    message: str,
) -> None:
    line, col = _line_col_from_offset(src, match.start())
    output.append(Violation(path, line, col, rule, message, _code_line(lines, line)))
