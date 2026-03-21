#!/usr/bin/env python3
"""
Frontend Paradigm Sentinel — run_frontend_paradigm.py
Deep architectural scan for paradigm violations in frontend/ files.
Usage: python run_frontend_paradigm.py --root <project_root>
"""

import re
import sys
import argparse
from pathlib import Path


EXCLUDED_DIRS = {"node_modules", ".next", "dist", "build", ".turbo", "coverage"}


# ---------------------------------------------------------------------------
# Placement contract — maps directory names to allowed component categories
# ---------------------------------------------------------------------------

RENDERER_DIR = "renderers"
LAYOUT_DIR = "layout"
COMMON_DIR = "common"
INPUT_DIR = "inputs"

PLACEMENT_CONTRACT: dict[str, set[str]] = {
    "renderers": {"Renderer"},    # filenames must contain "Renderer"
    "layout": set(),              # no filename restriction — checked separately
    "common": set(),
    "inputs": {"Input", "Combobox", "Select", "Text"},
    "navigation": set(),
    "animations": set(),
}

# External state management libraries
EXTERNAL_STATE_LIBS = re.compile(
    r'''import.*from\s+['"](?:redux|react-redux|@reduxjs/toolkit|zustand|mobx|mobx-react|jotai|recoil|valtio)'''
)

# Domain arithmetic patterns — operations on API response fields
DOMAIN_ARITHMETIC = re.compile(
    r'\b(?:totalRuns|wickets|overs|strikeRate|economy|average)\s*[+\-*/]'
    r'|\b(?:Math\.(?:round|floor|ceil|pow|sqrt))\s*\(\s*\w*(?:run|wicket|over|rate|economy|average)',
    re.IGNORECASE
)

# Polling on execute endpoint
POLLING_EXECUTE = re.compile(
    r'''(?:setInterval|setTimeout)\s*\(.*['"]/execute/''',
    re.DOTALL
)

# Silent catch — try/catch with empty or comment-only catch body
SILENT_CATCH = re.compile(
    r'catch\s*\([^)]*\)\s*\{\s*(?://[^\n]*)?\s*\}',
    re.DOTALL
)

# Safe return types — functions returning these are display helpers, not extractors.
DISPLAY_SAFE_RETURN_TYPES = re.compile(
    r':\s*(?:'
    r'string'
    r'|boolean'
    r'|number'
    r'|void'
    r'|never'
    r'|CSSProperties'
    r'|ReactNode'
    r'|JSX\.Element'
    r'|React\.ReactNode'
    r'|React\.ReactElement'
    r'|EnrichedDataResult'
    r')(?:\s*\|?\s*undefined|\s*\|?\s*null)?\s*[{;]'
)

# Type predicates returning display-safe or lib-owned types are exempt.
DISPLAY_SAFE_TYPE_PREDICATE = re.compile(
    r'value is (?:JsonRecord|string|boolean|number)'
)

# Payload extractor pattern — function with unknown as first/sole param.
UNKNOWN_FIRST_PARAM = re.compile(
    r'function\s+\w+\s*\(\s*\w+\s*:\s*unknown'
)

# View dispatch in renderer — _view routing belongs in FunctionRenderer.tsx
VIEW_DISPATCH_PATTERN = re.compile(r"""data\[['"]_view['"]\]""")


def check_external_state(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2A-R3 — external state library imports"""
    hits = []
    for i, line in enumerate(lines, 1):
        m = EXTERNAL_STATE_LIBS.search(line)
        if m:
            hits.append((i, m.start() + 1, "[RULE 2.2A-R3] External state management library import"))
    return hits


def check_domain_arithmetic(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2A-R5 — domain logic / arithmetic on API data in component"""
    # Skip lib/ files — they are helpers not components
    if "lib" in path.parts:
        return []
    hits = []
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        m = DOMAIN_ARITHMETIC.search(line)
        if m:
            hits.append((i, m.start() + 1, "[RULE 2.2A-R5] Domain arithmetic on API data in component"))
    return hits


def check_file_size(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2A-R4 — component file exceeds 300 lines"""
    count = len(lines)
    if count > 300:
        return [(1, 1, f"[RULE 2.2A-R4] Component file exceeds 300 lines ({count} lines)")]
    return []


def check_renderer_placement(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2B-R7 — renderer not in components/renderers/

    Only flags files whose name contains 'Renderer' if they sit outside ALL
    known legitimate placement directories.  A file already inside inputs/,
    common/, navigation/, or animations/ is correctly placed — do not flag it.
    """
    _EXEMPT_DIRS = {"renderers", "inputs", "common", "navigation", "animations"}
    if "Renderer" in path.stem and path.stem != "FunctionRenderer":
        parts = {p.lower() for p in path.parts}
        if not parts & _EXEMPT_DIRS:
            return [(1, 1, f"[RULE 2.2B-R7] Renderer '{path.name}' not in components/renderers/")]
    return []


def check_polling_execute(path: Path, content: str) -> list[tuple[int, int, str]]:
    """2.2A-R14 — setInterval/setTimeout calling /execute/ endpoint"""
    hits = []
    for m in POLLING_EXECUTE.finditer(content):
        line_no = content[:m.start()].count("\n") + 1
        hits.append((line_no, 1, "[RULE 2.2A-R14] Polling /execute/ endpoint via setInterval/setTimeout"))
    return hits


def check_silent_catch_in_renderer(path: Path, content: str) -> list[tuple[int, int, str]]:
    """2.2D-R2 — silent try/catch in renderer"""
    parts = [p.lower() for p in path.parts]
    if "renderers" not in parts:
        return []
    hits = []
    for m in SILENT_CATCH.finditer(content):
        line_no = content[:m.start()].count("\n") + 1
        hits.append((line_no, 1, "[RULE 2.2D-R2] Silent try/catch in renderer component"))
    return hits


def check_payload_extractor_in_renderer(
    path: Path, lines: list[str]
) -> list[tuple[int, int, str]]:
    """
    2.2A-R6 — payload extraction function in renderer component.

    Detects functions in components/renderers/ that accept `unknown`
    as their first/sole parameter and return a domain object type.
    These functions belong in lib/, not in renderer components.

    Exempt (return display-safe types):
      string, boolean, number, void, CSSProperties, ReactNode,
      JSX.Element, and their nullable variants.
    Also exempt: type predicates for lib/ types (value is JsonRecord).
    """
    parts = [p.lower() for p in path.parts]
    if "renderers" not in parts:
        return []

    hits = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped.startswith("function"):
            continue
        if not UNKNOWN_FIRST_PARAM.search(line):
            continue
        if "):" not in line:
            continue
        if DISPLAY_SAFE_RETURN_TYPES.search(line):
            continue
        if DISPLAY_SAFE_TYPE_PREDICATE.search(line):
            continue
        hits.append((
            i, 1,
            f"[RULE 2.2A-R6] Payload extraction function in renderer — "
            f"'{stripped[:60].rstrip()}' accepts `unknown` and returns a domain type. "
            f"Move to lib/ (e.g. lib/fortress-types.ts). "
            f"Renderers must not contain data extraction or type coercion logic."
        ))
    return hits


def check_view_dispatch_in_renderer(
    path: Path, content: str
) -> list[tuple[int, int, str]]:
    """2.2A-R7 — internal _view dispatch in renderer component.

    Detects any renderer file (other than FunctionRenderer.tsx) that reads
    data["_view"] or data['_view']. This pattern means the renderer is
    performing its own view routing, which violates SRP. View dispatch
    belongs exclusively in FunctionRenderer.tsx.
    """
    parts = [p.lower() for p in path.parts]
    if "renderers" not in parts:
        return []
    if path.stem == "FunctionRenderer":
        return []
    hits = []
    for m in VIEW_DISPATCH_PATTERN.finditer(content):
        line_no = content[: m.start()].count("\n") + 1
        hits.append((
            line_no,
            1,
            "[RULE 2.2A-R7] Internal _view dispatch in renderer — "
            "reading data['_view'] in a leaf renderer violates SRP. "
            "View routing belongs in FunctionRenderer.tsx.",
        ))
    return hits


def scan_file(path: Path) -> list[tuple[int, int, str]]:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
    except Exception as e:
        return [(0, 0, f"[READ ERROR] {e}")]

    hits: list[tuple[int, int, str]] = []
    hits.extend(check_external_state(path, lines))
    hits.extend(check_domain_arithmetic(path, lines))
    hits.extend(check_file_size(path, lines))
    hits.extend(check_renderer_placement(path, lines))
    hits.extend(check_polling_execute(path, content))
    hits.extend(check_silent_catch_in_renderer(path, content))
    hits.extend(check_payload_extractor_in_renderer(path, lines))
    hits.extend(check_view_dispatch_in_renderer(path, content))
    return hits


def collect_files(root: Path) -> list[Path]:
    frontend_dir = root / "frontend"
    if not frontend_dir.exists():
        return []
    files = []
    for ext in ("*.tsx", "*.ts"):
        for f in frontend_dir.rglob(ext):
            if not any(part in EXCLUDED_DIRS for part in f.parts):
                files.append(f)
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(description="Frontend Paradigm Sentinel")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--files", nargs="*", help="Explicit file list to scan (staged files only)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.files:
        files = sorted(
            Path(f).resolve() for f in args.files
            if Path(f).suffix in {".tsx", ".ts"} and Path(f).exists()
        )
    else:
        files = collect_files(root)

    if not files:
        print("WARN: No frontend files found — verify --root is correct")
        return 0

    all_violations: dict[Path, list[tuple[int, int, str]]] = {}
    for f in files:
        hits = scan_file(f)
        if hits:
            all_violations[f] = hits

    if not all_violations:
        print("PASS: zero violations")
        return 0

    total = sum(len(v) for v in all_violations.values())
    print(f"FAIL: {total} violation(s) found\n")
    for path, hits in sorted(all_violations.items()):
        for line, col, msg in hits:
            rel = path.relative_to(root)
            print(f"{msg}")
            print(f"  {rel}:{line}:{col}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
