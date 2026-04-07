#!/usr/bin/env python3
"""_scan_file - per-file rule scanner extracted from compliance_bouncer."""

from __future__ import annotations

import ast
from pathlib import Path

from ._shared import (  # noqa: F401
    ALLOWED_TECHNICAL_NUMBERS,
    ALLOWED_TECHNICAL_STRINGS,
    ANTI_GREASE_SIGNATURE_PATTERNS,
    DEPRECATED_SYMBOLS,
    FORBIDDEN_INFRASTRUCTURE_IMPORTS,
    RULE_ANTI_ANY,
    RULE_BOUNDARY,
    RULE_CONST_GREASE,
    RULE_CONST_TYPED,
    RULE_CONST_VISUAL,
    RULE_DOD,
    RULE_IO_AIR_GAP,
    RULE_MISSING_RETURN,
    RULE_PRESENTATION,
    RULE_ZERO_LITERAL,
    UI_TOKENS,
    VISUAL_SILENCE_PATTERNS,
    Violation,
    _all_nodes,
    _annotation_has_any,
    _call_name,
    _collect_manifest_literals,
    _docstring_nodes,
    _is_formatter_file,
    _is_literal_allowed_by_policy,
    _iter_manifest_files,
    _iter_python_files,
    _literal_key,
    _read_text,
    _record,
    _record_regex_match,
    _resolve_scan_paths,
    _root_name,
    _safe_parse,
)


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

                if (
                    is_service_layer
                    and not _is_formatter_file(path)
                    and isinstance(node.value, str)
                ):
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

        if isinstance(node, ast.Attribute):
            if node.attr in ("iterrows", "itertuples"):
                _record(
                    violations,
                    path,
                    lines,
                    node,
                    RULE_DOD,
                    f"Scalar loop detected: "
                    f".{node.attr}() is forbidden. "
                    f"Use vectorized operations.",
                )

        if isinstance(node, ast.Import):
            for alias in node.names:
                root_mod = alias.name.split(".")[0]
                if root_mod in FORBIDDEN_INFRASTRUCTURE_IMPORTS:
                    _record(
                        violations, path, lines, node,
                        RULE_BOUNDARY,
                        f"Infrastructure import "
                        f"'{alias.name}' forbidden "
                        f"in Domain Core files.",
                    )

        if isinstance(node, ast.ImportFrom):
            if node.module is not None:
                root_mod = node.module.split(".")[0]
                if root_mod in FORBIDDEN_INFRASTRUCTURE_IMPORTS:
                    _record(
                        violations, path, lines, node,
                        RULE_BOUNDARY,
                        f"Infrastructure import from "
                        f"'{node.module}' forbidden "
                        f"in Domain Core files.",
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
