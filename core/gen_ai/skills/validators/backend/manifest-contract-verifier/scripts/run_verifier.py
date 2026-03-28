#!/usr/bin/env python
"""Manifest contract verifier: manifest UI contract vs engine implementations."""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

BLOCKED_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules", "tests", "reports", "data"}

CONTEXT_PARAM_ALIASES: Dict[str, set[str]] = {
    "venue": {"venue", "venue_id", "stadium", "stadium_name", "stadium_id", "ground", "ground_id"},
    "team_a": {
        "team_a",
        "team_a_name",
        "home",
        "home_team",
        "home_team_name",
        "team",
        "team_name",
        "batting_team",
        "batter",
    },
    "team_b": {
        "team_b",
        "team_b_name",
        "away",
        "away_team",
        "away_team_name",
        "opp_team",
        "opposition",
        "opposition_team",
        "team_name",
        "bowling_team",
        "bowlers",
        "opposition_bowlers",
    },
    "years": {"years", "years_back", "lookback_years", "window_years", "year_window"},
    "region": {"region", "continent"},
}


@dataclass(frozen=True)
class MethodSig:
    params: set[str]
    has_var_kw: bool
    file: Path
    line: int


@dataclass(frozen=True)
class Violation:
    rule: str
    where: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify manifest -> engine contracts using AST parsing.")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--manifest", required=True, help="Manifest path, e.g. formats/odi/manifest.py")
    parser.add_argument("--json", action="store_true", default=False, help="Emit structured JSON output instead of prose")
    return parser.parse_args()


def _load_manifest_dict(manifest_path: Path) -> dict:
    text = manifest_path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(text, filename=str(manifest_path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "MANIFEST":
                    return ast.literal_eval(node.value)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "MANIFEST":
                return ast.literal_eval(node.value)
    raise ValueError("MANIFEST assignment not found in manifest file")


def _iter_engine_files(format_dir: Path) -> Iterable[Path]:
    for file in format_dir.rglob("*.py"):
        if any(part in BLOCKED_DIRS for part in file.parts):
            continue
        yield file


def _collect_class_methods(format_dir: Path) -> dict[str, dict[str, list[MethodSig]]]:
    registry: dict[str, dict[str, list[MethodSig]]] = {}
    for file in _iter_engine_files(format_dir):
        try:
            text = file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(text, filename=str(file))
        except (OSError, SyntaxError):
            continue

        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            cls_methods = registry.setdefault(node.name, {})
            for item in node.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue

                args = item.args
                names: list[str] = []
                for arg in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs):
                    if arg.arg in {"self", "cls"}:
                        continue
                    names.append(arg.arg)

                sig = MethodSig(
                    params=set(names),
                    has_var_kw=bool(args.kwarg),
                    file=file,
                    line=item.lineno,
                )
                cls_methods.setdefault(item.name, []).append(sig)
    return registry


def _flatten_manifest_functions(manifest: dict) -> list[dict]:
    rows: list[dict] = []
    for category in manifest.get("categories", []):
        cat_key = str(category.get("key", "<unknown-category>"))
        for fn in category.get("functions", []):
            rows.append(
                {
                    "category_key": cat_key,
                    "function_key": str(fn.get("key", "<unknown-function>")),
                    "engine_class": str(fn.get("engine_class", "")),
                    "engine_method": str(fn.get("engine_method", "")),
                    "required_context": list(fn.get("required_context", [])),
                }
            )
    return rows


def _ctx_aliases(ctx: str) -> set[str]:
    return CONTEXT_PARAM_ALIASES.get(ctx, {ctx})


def _missing_contexts(sig: MethodSig, required_context: list[str]) -> list[str]:
    if sig.has_var_kw:
        return []
    missing: list[str] = []
    for ctx in required_context:
        if not (_ctx_aliases(ctx) & sig.params):
            missing.append(ctx)
    return missing


def verify_contracts(manifest: dict, class_registry: dict[str, dict[str, list[MethodSig]]]) -> list[Violation]:
    violations: list[Violation] = []
    for fn in _flatten_manifest_functions(manifest):
        location = f"{fn['category_key']}/{fn['function_key']}"
        engine_class = fn["engine_class"]
        engine_method = fn["engine_method"]
        required_context = fn["required_context"]

        cls_methods = class_registry.get(engine_class)
        if cls_methods is None:
            violations.append(
                Violation(
                    rule="ENGINE_CLASS_MISSING",
                    where=location,
                    message=f"engine_class '{engine_class}' not found in format engine files",
                )
            )
            continue

        method_sigs = cls_methods.get(engine_method)
        if not method_sigs:
            available = ", ".join(sorted(cls_methods.keys())[:12])
            violations.append(
                Violation(
                    rule="ENGINE_METHOD_MISSING",
                    where=location,
                    message=(
                        f"method '{engine_method}' not found on class '{engine_class}'. "
                        f"Available methods: {available}"
                    ),
                )
            )
            continue

        candidate_miss = [_missing_contexts(sig, required_context) for sig in method_sigs]
        if any(not miss for miss in candidate_miss):
            continue

        missing_union = sorted({ctx for misses in candidate_miss for ctx in misses})
        missing_view = ", ".join(missing_union)
        violations.append(
            Violation(
                rule="REQUIRED_CONTEXT_PARAM_MISMATCH",
                where=location,
                message=(
                    f"method '{engine_class}.{engine_method}' does not expose compatible parameter aliases "
                    f"for required_context: [{missing_view}]"
                ),
            )
        )

    return violations


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    manifest_path = (root / args.manifest).resolve() if not Path(args.manifest).is_absolute() else Path(args.manifest)

    try:
        manifest = _load_manifest_dict(manifest_path)
    except (OSError, SyntaxError, ValueError) as exc:
        if args.json:
            output = {
                "gate": "GATE3",
                "status": "FAIL",
                "violations": [
                    {
                        "file": str(manifest_path.relative_to(root)) if manifest_path.is_absolute() else str(manifest_path),
                        "line": None,
                        "rule": "MANIFEST_PARSE_ERROR",
                        "message": f"cannot parse manifest: {exc}",
                    }
                ],
                "violation_count": 1,
            }
            print(json.dumps(output))
            return 1
        print(f"Fail: cannot parse manifest: {exc}")
        return 1

    format_dir = manifest_path.parent
    class_registry = _collect_class_methods(format_dir)
    violations = verify_contracts(manifest, class_registry)

    if args.json:
        output = {
            "gate": "GATE3",
            "status": "PASS" if not violations else "FAIL",
            "violations": [
                {
                    "file": None,
                    "line": None,
                    "rule": v.rule,
                    "message": f"{v.where}: {v.message}",
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
        print(f"{v.where}: [{v.rule}] {v.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
