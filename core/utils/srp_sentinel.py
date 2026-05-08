#!/usr/bin/env python3
"""GATE_SRP — Multi-signal SRP sentinel.

Signals
-------
A  method count > 12                          +1
B  file lines > 300                           +1
C  LCOM4 > 1  (disconnected self.X groups)    +2
E  file imports 3+ domain layers              +1
F  inheritance depth > 2                      +1
H  any method calls into 2+ domain layers     +2   ← call-site domain analysis
I  any method has disconnected variable       +1   ← variable cluster analysis
   clusters (independent sub-computations)

Score >= 5 → SRP_FLAG (blocking)
Score >= 3 → SRP_WARNING (advisory)

Removed signals
---------------
D  verb clusters — name-based, unreliable, removed
G  false cohesion — depended on D, removed
J  LLM semantic check — removed (requires paid API key)
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Optional

# ── Domain map ────────────────────────────────────────────────────────────────

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

# ── Thresholds ────────────────────────────────────────────────────────────────

METHOD_COUNT_THRESHOLD: int = 12
LINE_COUNT_THRESHOLD: int = 300
LCOM4_THRESHOLD: int = 1
IMPORT_DOMAIN_THRESHOLD: int = 3
INHERITANCE_DEPTH_THRESHOLD: int = 2
CALL_DOMAIN_THRESHOLD: int = 2   # domains a single function may call before flagging
VAR_CLUSTER_THRESHOLD: int = 1   # disconnected variable groups inside a function

SRP_WARNING_THRESHOLD: int = 3
SRP_FLAG_THRESHOLD: int = 5


# ── Allowlist ─────────────────────────────────────────────────────────────────

def _load_allowlist(root: Path) -> set[str]:
    """Load allowlisted file paths from agents/audits/SRP_VIOLATIONS.md."""
    allowlist_path = root / "agents" / "audits" / "SRP_VIOLATIONS.md"
    if not allowlist_path.exists():
        return set()
    import re
    allowlist: set[str] = set()
    pattern = re.compile(r"\|\s*`([^`]+)`\s*\|")
    for line in allowlist_path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line.strip())
        if match:
            allowlist.add(match.group(1))
    return allowlist


# ── Signal C: LCOM4 ───────────────────────────────────────────────────────────

def _compute_lcom4(class_node: ast.ClassDef) -> int:
    """
    LCOM4 = number of connected components in the method cohesion graph.
    Two methods are connected if they share >= 1 self.X attribute access.
    Methods with no self.X accesses are isolated nodes.
    Returns 1 if the class has <= 1 method (always cohesive by definition).
    """
    methods = [
        node for node in class_node.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if len(methods) <= 1:
        return 1

    dunder_attrs: frozenset[str] = frozenset({
        "__class__", "__dict__", "__slots__", "__weakref__",
        "__doc__", "__module__", "__qualname__",
    })

    def _get_self_attrs(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
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

    method_attrs = [_get_self_attrs(m) for m in methods]
    parent = {i: i for i in range(len(methods))}

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a: int, b: int) -> None:
        parent[find(a)] = find(b)

    for i in range(len(methods)):
        for j in range(i + 1, len(methods)):
            if method_attrs[i] & method_attrs[j]:
                union(i, j)

    return len({find(i) for i in range(len(methods))})


# ── Signal E: import domain count ────────────────────────────────────────────

def _count_import_domains(tree: ast.Module) -> int:
    """Count how many distinct project domain layers this file imports from."""
    domains: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            modules = [node.module] if node.module else []
        else:
            continue

        for mod in modules:
            if any(mod.startswith(pfx) for pfx in EXCLUDED_MODULE_PREFIXES):
                continue
            best_domain: Optional[str] = None
            best_len = 0
            for key, domain in PROJECT_DOMAIN_MAP.items():
                if mod.startswith(key) and len(key) > best_len:
                    best_domain = domain
                    best_len = len(key)
            if best_domain:
                domains.add(best_domain)

    return len(domains)


# ── Signal H: call-site domain analysis ──────────────────────────────────────

def _build_import_map(tree: ast.Module) -> dict[str, str]:
    """
    Build a map of every locally-bound name → full module path.

    Handles:
      import X              → X → X
      import X.Y as Z       → Z → X.Y
      from X import Y       → Y → X.Y
      from X import Y as Z  → Z → X.Y
    """
    import_map: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".")[0]
                import_map[local] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                local = alias.asname or alias.name
                full = f"{module}.{alias.name}" if module else alias.name
                import_map[local] = full
    return import_map


def _resolve_domain(name: str, import_map: dict[str, str]) -> Optional[str]:
    """Resolve an imported name to a project domain, or None if not a project import."""
    module = import_map.get(name)
    if not module:
        return None
    if any(module.startswith(pfx) for pfx in EXCLUDED_MODULE_PREFIXES):
        return None
    best: Optional[str] = None
    best_len = 0
    for key, domain in PROJECT_DOMAIN_MAP.items():
        if module.startswith(key) and len(key) > best_len:
            best = domain
            best_len = len(key)
    return best


def _get_call_domains(
    func_node: ast.FunctionDef | ast.AsyncFunctionDef,
    import_map: dict[str, str],
) -> set[str]:
    """
    Find all project domain layers that this function actually calls into.

    Only counts calls to names that resolve to a known project import.
    Examples caught:
      get_player(id)              → data domain (if get_player is from core.data_access)
      calculator.compute(x)       → calculation domain (if calculator is from core.calculators)
    """
    domains: set[str] = set()
    for node in ast.walk(func_node):
        if not isinstance(node, ast.Call):
            continue
        # Direct call: foo()
        if isinstance(node.func, ast.Name):
            d = _resolve_domain(node.func.id, import_map)
            if d:
                domains.add(d)
        # Attribute call: obj.method() — resolve the object
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                d = _resolve_domain(node.func.value.id, import_map)
                if d:
                    domains.add(d)
    return domains


# ── Signal I: variable cluster analysis ──────────────────────────────────────

def _get_var_clusters(
    func_node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> int:
    """
    Count disconnected variable clusters inside a function body.

    Two variables are in the same cluster if they appear together in the same
    statement.  If a function has 2+ disconnected clusters, it has independent
    sub-computations with no shared data flow — it can be cleanly split, proving
    it is doing more than one job.

    Returns 1 for functions with <= 2 local variables (too sparse to judge).
    """
    param_names: set[str] = {arg.arg for arg in func_node.args.args}
    param_names.discard("self")
    param_names.discard("cls")

    # Collect all locally-assigned variable names
    local_vars: set[str] = set()
    for node in ast.walk(func_node):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id not in param_names:
                local_vars.add(node.id)

    if len(local_vars) <= 2:
        return 1

    parent: dict[str, str] = {v: v for v in local_vars}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        parent[find(a)] = find(b)

    for stmt in func_node.body:
        vars_in_stmt = [
            node.id
            for node in ast.walk(stmt)
            if isinstance(node, ast.Name) and node.id in local_vars
        ]
        for i in range(len(vars_in_stmt) - 1):
            union(vars_in_stmt[i], vars_in_stmt[i + 1])

    return len({find(v) for v in local_vars})


# ── File scanning ─────────────────────────────────────────────────────────────

def _scan_file(
    path: Path,
    root: Path,
) -> list[dict[str, object]]:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        print(f"WARNING: skipping {path} (SyntaxError: {exc})", file=sys.stderr)
        return []

    line_count = len(source.splitlines())
    import_map = _build_import_map(tree)
    import_domain_count = _count_import_domains(tree)

    # File-level signals (shared across all classes in file)
    signal_b = 1 if line_count > LINE_COUNT_THRESHOLD else 0
    signal_e = 1 if import_domain_count >= IMPORT_DOMAIN_THRESHOLD else 0

    try:
        rel_path = path.relative_to(root).as_posix()
    except ValueError:
        rel_path = path.as_posix()

    violations: list[dict[str, object]] = []
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    scored_classes = [
        c for c in classes
        if any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in c.body)
        or len(c.bases) > INHERITANCE_DEPTH_THRESHOLD
    ]

    if scored_classes:
        for class_node in scored_classes:
            methods = [
                n for n in class_node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            method_count = len(methods)
            lcom4 = _compute_lcom4(class_node)

            # A: too many methods
            signal_a = 1 if method_count > METHOD_COUNT_THRESHOLD else 0
            # C: LCOM4 — disconnected self.X groups
            signal_c = 2 if lcom4 > LCOM4_THRESHOLD else 0
            # F: inheritance depth
            parent_count = len(class_node.bases)
            signal_f = 1 if parent_count > INHERITANCE_DEPTH_THRESHOLD else 0

            # H: any method calls into 2+ domain layers
            multi_domain_methods: list[str] = []
            for method in methods:
                domains = _get_call_domains(method, import_map)
                if len(domains) >= CALL_DOMAIN_THRESHOLD:
                    multi_domain_methods.append(
                        f"{method.name}({', '.join(sorted(domains))})"
                    )
            signal_h = 2 if multi_domain_methods else 0

            # I: any method has disconnected variable clusters
            multi_cluster_methods: list[str] = []
            for method in methods:
                clusters = _get_var_clusters(method)
                if clusters > VAR_CLUSTER_THRESHOLD:
                    multi_cluster_methods.append(f"{method.name}(clusters={clusters})")
            signal_i = 1 if multi_cluster_methods else 0

            score = signal_a + signal_b + signal_c + signal_e + signal_f + signal_h + signal_i

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
            if signal_e:
                parts.append(f"import_domains={import_domain_count}(E+1)")
            if signal_f:
                parts.append(f"parent_count={parent_count}(F+1)")
            if signal_h:
                parts.append(f"multi_domain_methods={multi_domain_methods}(H+2)")
            if signal_i:
                parts.append(f"multi_cluster_methods={multi_cluster_methods}(I+1)")

            lcom4_detail = f" {lcom4} disjoint method groups." if lcom4 > 1 else ""
            message = (
                f"{class_node.name}: score={score} [{', '.join(parts)}]."
                f"{lcom4_detail}"
            )

            violations.append({
                "file": rel_path,
                "line": class_node.lineno,
                "rule": rule,
                "message": message,
            })

    else:
        # No classes — check top-level functions
        top_fns = [
            n for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        fn_count = len(top_fns)

        signal_a = 1 if fn_count > METHOD_COUNT_THRESHOLD else 0

        multi_domain_fns: list[str] = []
        for fn in top_fns:
            domains = _get_call_domains(fn, import_map)
            if len(domains) >= CALL_DOMAIN_THRESHOLD:
                multi_domain_fns.append(f"{fn.name}({', '.join(sorted(domains))})")
        signal_h = 2 if multi_domain_fns else 0

        multi_cluster_fns: list[str] = []
        for fn in top_fns:
            clusters = _get_var_clusters(fn)
            if clusters > VAR_CLUSTER_THRESHOLD:
                multi_cluster_fns.append(f"{fn.name}(clusters={clusters})")
        signal_i = 1 if multi_cluster_fns else 0

        score = signal_a + signal_b + signal_e + signal_h + signal_i

        if score >= SRP_FLAG_THRESHOLD:
            rule = "SRP_FLAG"
        elif score >= SRP_WARNING_THRESHOLD:
            rule = "SRP_WARNING"
        else:
            return violations

        module_parts: list[str] = []
        if signal_a:
            module_parts.append(f"fn_count={fn_count}(A+1)")
        if signal_b:
            module_parts.append(f"lines={line_count}(B+1)")
        if signal_e:
            module_parts.append(f"import_domains={import_domain_count}(E+1)")
        if signal_h:
            module_parts.append(f"multi_domain_fns={multi_domain_fns}(H+2)")
        if signal_i:
            module_parts.append(f"multi_cluster_fns={multi_cluster_fns}(I+1)")

        message = (
            f"module: score={score} [{', '.join(module_parts)}]. "
            "Free-function module with mixed responsibilities."
        )
        violations.append({
            "file": rel_path,
            "line": 1,
            "rule": rule,
            "message": message,
        })

    return violations


# ── File collection ───────────────────────────────────────────────────────────

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


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="GATE_SRP multi-signal SRP sentinel")
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

    allowlist = _load_allowlist(root_path)
    blocking_violations = [v for v in violations if v["file"] not in allowlist]
    advisory_violations = [v for v in violations if v["file"] in allowlist]
    status = "FAIL" if blocking_violations else "PASS"

    if args.json:
        print(
            json.dumps({
                "gate": "GATE_SRP",
                "triggered": True,
                "status": status,
                "blocking_violations": blocking_violations,
                "advisory_violations": advisory_violations,
                "violations": blocking_violations,
                "violation_count": len(blocking_violations),
            })
        )
    else:
        print("GATE_SRP - srp-sentinel (multi-signal)")
        print(f"  Scanned: {len(files)} files")
        print(f"  Blocking findings: {len(blocking_violations)}")
        print(f"  Advisory findings: {len(advisory_violations)}")
        for v in blocking_violations:
            print(f"  [BLOCKING][{v['rule']}] {v['file']}:{v['line']} — {v['message']}")
        for v in advisory_violations:
            print(f"  [ADVISORY][{v['rule']}] {v['file']}:{v['line']} — {v['message']}")
        print(
            f"GATE_SRP - {status} "
            f"({len(blocking_violations)} blocking, {len(advisory_violations)} advisory)"
        )
    return 1 if blocking_violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
