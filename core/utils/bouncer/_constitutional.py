#!/usr/bin/env python3
"""_constitutional - constitutional rule scanner extracted from compliance_bouncer."""

from __future__ import annotations

import ast
import re  # noqa: F401
from pathlib import Path
from typing import Iterable  # noqa: F401

from ._shared import (  # noqa: F401
    ANTI_GREASE_SIGNATURE_PATTERNS,
    DEPRECATED_SYMBOLS,
    RULE_CONST_GREASE,
    RULE_CONST_TYPED,
    RULE_CONST_VISUAL,
    VISUAL_SILENCE_PATTERNS,
    Violation,
    _iter_python_files,
    _is_formatter_file,
    _read_text,
    _record,
    _record_regex_match,
    _resolve_scan_paths,
    _safe_parse,
)


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

    signature_scan_files = sorted(scoped_set) if scoped_set is not None else sorted(_iter_python_files(root))
    for path in signature_scan_files:
        if path.suffix != ".py":
            continue
        tree_tt, _, _ = _safe_parse(path)
        if tree_tt is None:
            continue
        path_parts_tt = {p.lower() for p in path.parts}
        lines_tt = _read_text(path).splitlines()
        for node in ast.walk(tree_tt):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.module is None:
                continue
            module_parts = set(node.module.split("."))
            deprecated_segments = {
                "legacy", "old", "deprecated",
                "v1", "compat",
            }
            if module_parts & deprecated_segments:
                _record(
                    violations, path, lines_tt, node,
                    RULE_CONST_TYPED,
                    f"Import from deprecated module "
                    f"'{node.module}' detected.",
                )
            for alias in node.names:
                if alias.name in DEPRECATED_SYMBOLS:
                    _record(
                        violations, path, lines_tt, node,
                        RULE_CONST_TYPED,
                        f"Deprecated symbol "
                        f"'{alias.name}' imported "
                        f"from '{node.module}'.",
                    )
            if (
                "engines" in path_parts_tt
                or "calculators" in path_parts_tt
            ):
                if "engines" in module_parts:
                    _record(
                        violations, path, lines_tt, node,
                        RULE_CONST_TYPED,
                        f"Cross-engine import: "
                        f"'{node.module}'. Engines must "
                        f"import from core/interfaces/ only.",
                    )

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
