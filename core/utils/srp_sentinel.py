#!/usr/bin/env python3
"""GATE_SRP advisory SRP sentinel."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

VERB_GROUPS: dict[str, list[str]] = {
    "fetch": ["fetch_", "get_", "load_", "retrieve_", "read_"],
    "calculate": ["calculate_", "calc_", "compute_", "score_", "measure_"],
    "build": ["build_", "create_", "make_", "generate_", "gen_", "construct_"],
    "format": ["format_", "render_", "display_", "stringify_", "to_"],
    "validate": ["validate_", "check_", "verify_", "is_", "has_"],
    "save": ["save_", "write_", "store_", "persist_", "export_"],
    "update": ["update_", "set_", "refresh_", "reset_"],
    "parse": ["parse_", "extract_", "transform_", "convert_", "decode_"],
    "compare": ["compare_", "analyze_", "analyse_", "rank_", "sort_"],
}

PROJECT_DOMAIN_MAP: dict[str, str] = {
    "core.data_access": "data",
    "core.calculators": "calculation",
    "core.services": "service",
    "core.match_pack": "presentation",
    "core.player_engine": "engine",
    "core.team_engine": "engine",
    "formats.odi.engines": "engine",
    "formats.odi": "format",
    "api.": "api",
    "config.": "config",
}

EXCLUDED_MODULE_PREFIXES: tuple[str, ...] = (
    "core.interfaces",
    "core.exceptions",
    "core.utils",
    "typing",
    "collections",
    "dataclasses",
    "enum",
    "abc",
    "logging",
    "re",
    "os",
    "sys",
    "io",
    "pathlib",
    "datetime",
    "json",
    "math",
    "copy",
    "functools",
    "itertools",
    "pandas",
    "numpy",
    "duckdb",
)

DEFAULT_SCAN_PATHS: list[str] = ["core/", "api/", "formats/"]

METHOD_COUNT_THRESHOLD: int = 20
LINE_COUNT_THRESHOLD: int = 400
LCOM4_THRESHOLD: int = 1
VERB_CLUSTER_THRESHOLD: int = 3
IMPORT_DOMAIN_THRESHOLD: int = 3

SRP_WARNING_THRESHOLD: int = 3
SRP_FLAG_THRESHOLD: int = 5


def _compute_lcom4(class_node: ast.ClassDef) -> int:
    """
    Returns the LCOM4 score for a class.
    LCOM4 = number of connected components in the method cohesion graph.
    Two methods are connected if they share >= 1 self.X attribute access.
    Methods with no self.X accesses are isolated nodes (1 component each).
    Returns 1 if class has <= 1 methods (always cohesive by definition).
    """

    methods = [
        node
        for node in class_node.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    if len(methods) <= 1:
        return 1

    dunder_attrs: frozenset[str] = frozenset(
        {
            "__class__",
            "__dict__",
            "__slots__",
            "__weakref__",
            "__doc__",
            "__module__",
            "__qualname__",
        }
    )

    def _get_self_attrs(
        func_node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> set[str]:
        attrs: set[str] = set()
        for node in ast.walk(func_node):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id == "self"
                and node.attr not in dunder_attrs
            ):
                attrs.add(node.attr)
        return attrs

    method_attrs: list[set[str]] = [_get_self_attrs(method) for method in methods]
    parent: dict[int, int] = {i: i for i in range(len(methods))}

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        parent[find(left)] = find(right)

    for left in range(len(methods)):
        for right in range(left + 1, len(methods)):
            if method_attrs[left] & method_attrs[right]:
                union(left, right)

    return len({find(index) for index in range(len(methods))})


def _count_verb_clusters(method_names: list[str]) -> int:
    active: set[str] = set()
    for name in method_names:
        lower = name.lower()
        for group, prefixes in VERB_GROUPS.items():
            if any(lower.startswith(prefix) for prefix in prefixes):
                active.add(group)
                break
    return len(active)


def _count_import_domains(tree: ast.Module) -> int:
    domains: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            modules = [node.module] if node.module else []
        else:
            continue

        for mod in modules:
            if any(mod.startswith(prefix) for prefix in EXCLUDED_MODULE_PREFIXES):
                continue

            matched_domain: str | None = None
            matched_len = 0
            for key, domain in PROJECT_DOMAIN_MAP.items():
                if mod.startswith(key) and len(key) > matched_len:
                    matched_domain = domain
                    matched_len = len(key)

            if matched_domain:
                domains.add(matched_domain)

    return len(domains)


def _scan_file(path: Path, root: Path) -> list[dict[str, object]]:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        print(f"WARNING: skipping {path} (SyntaxError: {exc})", file=sys.stderr)
        return []

    line_count = len(source.splitlines())
    import_domain_count = _count_import_domains(tree)

    signal_b = 1 if line_count > LINE_COUNT_THRESHOLD else 0
    signal_e = 1 if import_domain_count >= IMPORT_DOMAIN_THRESHOLD else 0

    try:
        rel_path = path.relative_to(root).as_posix()
    except ValueError:
        rel_path = path.as_posix()

    violations: list[dict[str, object]] = []
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    scored_classes = [
        class_node
        for class_node in classes
        if any(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            for node in class_node.body
        )
    ]

    if scored_classes:
        for class_node in scored_classes:
            methods = [
                node
                for node in class_node.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            method_count = len(methods)
            method_names = [method.name for method in methods]
            lcom4 = _compute_lcom4(class_node)
            verb_clusters = _count_verb_clusters(method_names)

            signal_a = 1 if method_count > METHOD_COUNT_THRESHOLD else 0
            signal_c = 2 if lcom4 > LCOM4_THRESHOLD else 0
            signal_d = 1 if verb_clusters >= VERB_CLUSTER_THRESHOLD else 0

            score = signal_a + signal_b + signal_c + signal_d + signal_e

            if score >= SRP_FLAG_THRESHOLD:
                rule = "SRP_FLAG"
            elif score >= SRP_WARNING_THRESHOLD:
                rule = "SRP_WARNING"
            else:
                continue

            parts: list[str] = []
            if signal_a:
                parts.append(f"method_count={method_count}(A+1)")
            if signal_b:
                parts.append(f"lines={line_count}(B+1)")
            if signal_c:
                parts.append(f"lcom4={lcom4}(C+2)")
            if signal_d:
                parts.append(f"verb_clusters={verb_clusters}(D+1)")
            if signal_e:
                parts.append(f"import_domains={import_domain_count}(E+1)")

            lcom4_detail = f" {lcom4} disjoint method groups." if lcom4 > 1 else ""
            message = (
                f"{class_node.name}: score={score} [{', '.join(parts)}]."
                f"{lcom4_detail}"
            )

            violations.append(
                {
                    "file": rel_path,
                    "line": class_node.lineno,
                    "rule": rule,
                    "message": message,
                }
            )
    else:
        top_fns = [
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        fn_count = len(top_fns)
        fn_names = [func.name for func in top_fns]
        verb_clusters = _count_verb_clusters(fn_names)

        signal_a = 1 if fn_count > METHOD_COUNT_THRESHOLD else 0
        signal_d = 1 if verb_clusters >= VERB_CLUSTER_THRESHOLD else 0
        score = signal_a + signal_b + signal_d + signal_e

        if score >= SRP_FLAG_THRESHOLD:
            rule = "SRP_FLAG"
        elif score >= SRP_WARNING_THRESHOLD:
            rule = "SRP_WARNING"
        else:
            return violations

        if score >= SRP_WARNING_THRESHOLD:
            parts: list[str] = []
            if signal_a:
                parts.append(f"fn_count={fn_count}(A+1)")
            if signal_b:
                parts.append(f"lines={line_count}(B+1)")
            if signal_d:
                parts.append(f"verb_clusters={verb_clusters}(D+1)")
            if signal_e:
                parts.append(f"import_domains={import_domain_count}(E+1)")

            message = (
                f"module: score={score} [{', '.join(parts)}]. "
                "Free-function module with mixed responsibilities."
            )
            violations.append(
                {
                    "file": rel_path,
                    "line": 1,
                    "rule": rule,
                    "message": message,
                }
            )

    return violations


def _collect_py_files(scan_paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    result: list[Path] = []
    for scan_path in scan_paths:
        if not scan_path.exists():
            continue
        if scan_path.is_file() and scan_path.suffix == ".py":
            if scan_path not in seen:
                seen.add(scan_path)
                result.append(scan_path)
        elif scan_path.is_dir():
            for path in sorted(scan_path.rglob("*.py")):
                if "__pycache__" in path.parts:
                    continue
                if path not in seen:
                    seen.add(path)
                    result.append(path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="GATE_SRP advisory SRP sentinel")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", default=False)
    parser.add_argument("--paths", nargs="*", default=[])
    args = parser.parse_args()

    root_path = Path(args.root).resolve()
    if args.paths:
        scan_paths = [root_path / path for path in args.paths]
    else:
        scan_paths = [root_path / path for path in DEFAULT_SCAN_PATHS]

    files = _collect_py_files(scan_paths)
    violations: list[dict[str, object]] = []
    for file_path in files:
        violations.extend(_scan_file(file_path, root_path))

    if args.json:
        print(
            json.dumps(
                {
                    "gate": "GATE_SRP",
                    "triggered": True,
                    "status": "PASS",
                    "advisory": True,
                    "violations": violations,
                    "violation_count": len(violations),
                }
            )
        )
    else:
        print("GATE_SRP - srp-sentinel (advisory)")
        print(f"  Scanned: {len(files)} files")
        print(f"  Findings: {len(violations)}")
        for violation in violations:
            print(
                f"  [{violation['rule']}] {violation['file']}:{violation['line']} — "
                f"{violation['message']}"
            )
        print("GATE_SRP - PASS (advisory)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
