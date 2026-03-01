#!/usr/bin/env python3
"""Phase 12 Compliance Bouncer.

AST-based governance linter enforcing:
- Zero-Literal
- Anti-Any
- I/O Air-Gap
- Presentation Purity
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import logging

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

FORBIDDEN_INFRASTRUCTURE_IMPORTS = {
    "duckdb",
    "fastapi",
    "flask",
    "django",
    "httpx",
    "requests",
    "sqlalchemy",
    "aiohttp",
}

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
)

ALLOWED_TECHNICAL_STRINGS = {
    "",
    "__main__",
}

ALLOWED_TECHNICAL_NUMBERS = {0, 1}

VISUAL_SILENCE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("emoji_u2705", re.compile("\u2705")),
    ("emoji_u2614", re.compile("\u2614")),
    ("token_included", re.compile(r"\bInclud" r"ed\b", re.IGNORECASE)),
    ("token_excluded", re.compile(r"\bExclud" r"ed\b", re.IGNORECASE)),
    ("token_last_5", re.compile(r"\bLast" r"\s+5\b", re.IGNORECASE)),
)

DEPRECATED_SYMBOLS = {
    "MatchIntelligenceData",
}

TYPED_TRUTH_IMPORT_PATTERN = re.compile(
    r"^\s*from core\.interfaces\.team_interface import MatchIntelligenceData\s*$",
    re.MULTILINE,
)

ANTI_GREASE_SIGNATURE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "dict_str_any_param",
        re.compile(
            r"(?ms)^\s*(?:async\s+)?def\s+\w+\s*\([^)]*dict\s*\[\s*str\s*,\s*Any\s*\][^)]*\)\s*(?:->\s*[^:]+)?\s*:"
        ),
    ),
    (
        "dict_str_any_return",
        re.compile(
            r"(?ms)^\s*(?:async\s+)?def\s+\w+\s*\([^)]*\)\s*->\s*[^:\n]*dict\s*\[\s*str\s*,\s*Any\s*\][^:\n]*:"
        ),
    ),
    (
        "object_param",
        re.compile(
            r"(?ms)^\s*(?:async\s+)?def\s+\w+\s*\([^)]*\bobject\b[^)]*\)\s*(?:->\s*[^:]+)?\s*:"
        ),
    ),
    (
        "object_return",
        re.compile(r"(?ms)^\s*(?:async\s+)?def\s+\w+\s*\([^)]*\)\s*->\s*[^:\n]*\bobject\b[^:\n]*:"),
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


def _scan_file(
    path: Path,
    allowed_literals: set[tuple[str, str]],
) -> list[Violation]:
    violations: list[Violation] = []
    tree, lines, parse_err = _safe_parse(path)
    if tree is None:
        line = 1
        col = 1
        src_line = lines[0].strip() if lines else ""
        violations.append(
            Violation(
                file=path,
                line=line,
                col=col,
                rule="SYNTAX_ERROR",
                message=parse_err or "Unable to parse file",
                code=src_line,
            )
        )
        return violations

    doc_nodes = _docstring_nodes(tree)
    all_nodes = _all_nodes(tree)
    is_service_layer = "services" in {p.lower() for p in path.parts}

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            key = _literal_key(node.value)
            if key is not None and id(node) not in doc_nodes and id(node) not in all_nodes:
                if not _is_literal_allowed_by_policy(node.value) and key not in allowed_literals:
                    _record(
                        violations,
                        path,
                        lines,
                        node,
                        RULE_ZERO_LITERAL,
                        f"Literal {key[1]} is not declared in manifest.py",
                    )

                if is_service_layer and isinstance(node.value, str):
                    lower = node.value.lower()
                    if any(token in lower for token in UI_TOKENS):
                        _record(
                            violations,
                            path,
                            lines,
                            node,
                            RULE_PRESENTATION,
                            f"Service-layer string looks UI-specific: {node.value!r}",
                        )

        if isinstance(node, ast.ImportFrom) and node.module == "typing":
            for alias in node.names:
                if alias.name == "Any":
                    _record(
                        violations,
                        path,
                        lines,
                        node,
                        RULE_ANTI_ANY,
                        "Importing Any from typing is forbidden",
                    )

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is None:
                _record(
                    violations,
                    path,
                    lines,
                    node,
                    RULE_MISSING_RETURN,
                    f"Function '{node.name}' is missing a return type annotation",
                )
            elif _annotation_has_any(node.returns):
                _record(
                    violations,
                    path,
                    lines,
                    node,
                    RULE_ANTI_ANY,
                    f"Function '{node.name}' return type uses Any",
                )

            all_args = [*node.args.args, *node.args.kwonlyargs]
            if node.args.vararg is not None:
                all_args.append(node.args.vararg)
            if node.args.kwarg is not None:
                all_args.append(node.args.kwarg)
            for arg in all_args:
                if _annotation_has_any(arg.annotation):
                    _record(
                        violations,
                        path,
                        lines,
                        arg,
                        RULE_ANTI_ANY,
                        f"Argument '{arg.arg}' in '{node.name}' uses Any",
                    )

            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    name = _call_name(sub)
                    if isinstance(sub.func, ast.Name) and sub.func.id == "open":
                        _record(
                            violations,
                            path,
                            lines,
                            sub,
                            RULE_IO_AIR_GAP,
                            f"Blocking I/O call detected in method '{node.name}': {name}",
                        )
                    if isinstance(sub.func, ast.Attribute):
                        if _root_name(sub.func) == "os":
                            _record(
                                violations,
                                path,
                                lines,
                                sub,
                                RULE_IO_AIR_GAP,
                                f"Blocking I/O call detected in method '{node.name}': {name}",
                            )
                        if _root_name(sub.func) == "pd" and name == "pd.read_csv":
                            _record(
                                violations,
                                path,
                                lines,
                                sub,
                                RULE_IO_AIR_GAP,
                                f"Blocking I/O call detected in method '{node.name}': {name}",
                            )

        if isinstance(node, ast.AnnAssign) and _annotation_has_any(node.annotation):
            _record(
                violations,
                path,
                lines,
                node,
                RULE_ANTI_ANY,
                "Variable annotation uses Any",
            )

    return violations


def _scan_constitutional(root: Path, scoped_paths: list[Path] | None = None) -> list[Violation]:
    violations: list[Violation] = []
    scoped_set = {path.resolve() for path in scoped_paths} if scoped_paths else None

    core_root = (root / "core").resolve()
    core_scan_files: list[Path] = []
    if core_root.exists():
        if scoped_set is None:
            for path in core_root.rglob("*.py"):
                if not _is_formatter_file(path):
                    core_scan_files.append(path.resolve())
        else:
            for path in sorted(scoped_set):
                if path.suffix != ".py":
                    continue
                if path.is_relative_to(core_root) and not _is_formatter_file(path):
                    core_scan_files.append(path)

    for path in sorted(set(core_scan_files)):
        src = _read_text(path)
        lines = src.splitlines()
        for token_name, pattern in VISUAL_SILENCE_PATTERNS:
            for match in pattern.finditer(src):
                _record_regex_match(
                    violations,
                    path,
                    lines,
                    src,
                    match,
                    RULE_CONST_VISUAL,
                    f"Visual Silence token detected ({token_name})",
                )

    team_engine_path = (root / "formats" / "odi" / "engines" / "team_engine.py").resolve()
    should_scan_team_engine = (
        team_engine_path.exists()
        and (scoped_set is None or team_engine_path in scoped_set)
    )
    if should_scan_team_engine:
        src = _read_text(team_engine_path)
        lines = src.splitlines()
        for match in TYPED_TRUTH_IMPORT_PATTERN.finditer(src):
            _record_regex_match(
                violations,
                team_engine_path,
                lines,
                src,
                match,
                RULE_CONST_TYPED,
                "Forbidden legacy import detected for MatchIntelligenceData",
            )

    signature_scan_files = sorted(scoped_set) if scoped_set is not None else sorted(_iter_python_files(root))
    for path in signature_scan_files:
        if path.suffix != ".py":
            continue
        src = _read_text(path)
        lines = src.splitlines()
        for token_name, pattern in ANTI_GREASE_SIGNATURE_PATTERNS:
            for match in pattern.finditer(src):
                _record_regex_match(
                    violations,
                    path,
                    lines,
                    src,
                    match,
                    RULE_CONST_GREASE,
                    f"Anti-Grease signature token detected ({token_name})",
                )

    return violations


def run(root: Path, raw_paths: list[str] | None = None) -> int:
    scoped_paths = _resolve_scan_paths(root, raw_paths or [])
    allowed_literals = _collect_manifest_literals(root)
    if not allowed_literals:
        logger.error("FAIL: No manifest literals discovered. Cannot run Zero-Literal rule safely.")
        return 2

    if scoped_paths:
        target_files = scoped_paths
    else:
        target_files = sorted(_iter_python_files(root))

    if (raw_paths or []) and not target_files:
        logger.error("FAIL: No Python files matched --paths scope.")
        return 2

    all_violations = _scan_constitutional(root, scoped_paths or None)
    for path in target_files:
        all_violations.extend(_scan_file(path, allowed_literals))

    if not all_violations:
        logger.info(f"PASS: 100% compliance across {len(target_files)} file(s).")
        return 0

    logger.error(f"FAIL: {len(all_violations)} violation(s) across {len(target_files)} file(s).")
    for item in sorted(all_violations, key=lambda v: (str(v.file), v.line, v.col, v.rule)):
        safe_path = str(item.file).encode("ascii", errors="backslashreplace").decode("ascii")
        safe_message = item.message.encode("ascii", errors="backslashreplace").decode("ascii")
        logger.error(f"{safe_path}:{item.line}:{item.col}: [{item.rule}] {safe_message}")
        if item.code:
            safe_code = item.code.encode("ascii", errors="backslashreplace").decode("ascii")
            logger.error(f"    {safe_code}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 12 Compliance Bouncer")
    parser.add_argument("--root", default=".", help="Project root path")
    parser.add_argument(
        "--paths",
        nargs="*",
        default=[],
        help="Optional Python files/directories to restrict scan scope",
    )
    args = parser.parse_args()
    return run(Path(args.root).resolve(), args.paths)


if __name__ == "__main__":
    raise SystemExit(main())
