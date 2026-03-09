#!/usr/bin/env python3
"""
Frontend Lint Sentinel — run_frontend_lint.py
Scans all .tsx and .ts files under frontend/ for 12 rule violations.
Usage: python run_frontend_lint.py --root <project_root>
"""

import re
import sys
import argparse
from pathlib import Path


EXCLUDED_DIRS = {"node_modules", ".next", "dist", "build", ".turbo", "coverage"}


# ---------------------------------------------------------------------------
# Check definitions
# ---------------------------------------------------------------------------

def check_raw_fetch(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2A-R1 — raw fetch() outside lib/api.ts"""
    if path.name == "api.ts" and "lib" in path.parts:
        return []
    hits = []
    for i, line in enumerate(lines, 1):
        # skip comments
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        for m in re.finditer(r'\bfetch\s*\(', line):
            hits.append((i, m.start() + 1, "[RULE 2.2A-R1] Raw fetch() outside lib/api.ts"))
    return hits


def check_any_unknown(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2A-R6 — : any in type annotations (: unknown is exempt — idiomatic defensive typing)"""
    hits = []
    pattern = re.compile(r':\s*any\b')
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        for m in pattern.finditer(line):
            hits.append((i, m.start() + 1, "[RULE 2.2A-R6] ': any' in type annotation"))
    return hits


def check_hardcoded_format_strings(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2A-R13 — hardcoded format strings as raw literals"""
    # Skip types.ts and api.ts where these may legitimately appear as type literals
    if path.name in ("types.ts", "api.ts"):
        return []
    hits = []
    pattern = re.compile(r'["\'](?:odi|t20i|the_hundred)["\']')
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        for m in pattern.finditer(line):
            hits.append((i, m.start() + 1, "[RULE 2.2A-R13] Hardcoded format string literal"))
    return hits


def check_raw_hex_colors(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2B-R1 — raw hex colours outside globals.css"""
    if path.name == "globals.css":
        return []
    hits = []
    pattern = re.compile(r'#[0-9a-fA-F]{3,8}\b')
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        for m in pattern.finditer(line):
            hits.append((i, m.start() + 1, "[RULE 2.2B-R1] Raw hex colour outside globals.css"))
    return hits


def check_non_lucide_icons(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2B-R4 — non-lucide-react icon imports"""
    hits = []
    pattern = re.compile(r'''import\s.*from\s+['"](@heroicons|react-icons|@phosphor-icons|phosphor-react)''')
    for i, line in enumerate(lines, 1):
        for m in pattern.finditer(line):
            hits.append((i, m.start() + 1, "[RULE 2.2B-R4] Non-lucide-react icon library import"))
    return hits


def check_inline_font_family(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2B-R5 — inline font-family declarations in component files (CSS files exempt)"""
    if path.suffix == ".css":
        return []
    hits = []
    pattern = re.compile(r'font-family\s*:')
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        for m in pattern.finditer(line):
            hits.append((i, m.start() + 1, "[RULE 2.2B-R5] Inline font-family declaration"))
    return hits


def check_component_keyframes(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2B-R6 — @keyframes in component files"""
    if path.suffix == ".css":
        return []
    hits = []
    pattern = re.compile(r'@keyframes\b')
    for i, line in enumerate(lines, 1):
        for m in pattern.finditer(line):
            hits.append((i, m.start() + 1, "[RULE 2.2B-R6] @keyframes in component file"))
    return hits


def check_eager_renderer_imports(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2C-R1 — non-React.lazy imports in FunctionRenderer.tsx"""
    if path.name != "FunctionRenderer.tsx":
        return []
    hits = []
    # Detect static component imports that are NOT React.lazy
    import_pattern = re.compile(r'''^import\s+\w.*from\s+['"]''')
    lazy_pattern = re.compile(r'React\.lazy|lazy\(')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if import_pattern.match(stripped) and not lazy_pattern.search(stripped):
            # Allow react itself and type-only imports
            if "from 'react'" in line or 'from "react"' in line:
                continue
            if "import type" in line:
                continue
            hits.append((i, 1, "[RULE 2.2C-R1] Eager (non-React.lazy) renderer import in FunctionRenderer.tsx"))
    return hits


def check_schema_jsdoc(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2D-R3 — interfaces in lib/types.ts missing @schema JSDoc"""
    if path.name != "types.ts":
        return []
    hits = []
    interface_pattern = re.compile(r'^export\s+interface\s+(\w+)')
    for i, line in enumerate(lines, 1):
        m = interface_pattern.match(line.strip())
        if m:
            # Look back up to 5 lines for @schema
            start = max(0, i - 6)
            block = "\n".join(lines[start:i - 1])
            if "@schema" not in block:
                hits.append((i, 1, f"[RULE 2.2D-R3] Interface '{m.group(1)}' missing @schema JSDoc"))
    return hits


def check_aria_label_buttons(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2E-R1 — icon-only buttons without aria-label"""
    hits = []
    # Simple heuristic: <button> on a line without aria-label, followed by icon-like content
    # Full AST check not possible with regex; flag <button> elements with no aria-label on the same tag
    button_open = re.compile(r'<button(?![^>]*aria-label)[^>]*>')
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        for m in button_open.finditer(line):
            hits.append((i, m.start() + 1, "[RULE 2.2E-R1] <button> element without aria-label"))
    return hits


def check_onclick_non_interactive(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2E-R2 â€” onClick on non-interactive elements without role=button + tabIndex"""
    hits = []
    div_span_onclick = re.compile(r'<(div|span)\b[^>]*\bonClick\b[^>]*>')
    has_role_button = re.compile(r'role\s*=\s*["\']button["\']')
    has_tabindex = re.compile(r'tabIndex\s*=')
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        for m in div_span_onclick.finditer(line):
            tag_content = m.group(0)
            if not has_role_button.search(tag_content) or not has_tabindex.search(tag_content):
                hits.append((
                    i,
                    m.start() + 1,
                    '[RULE 2.2E-R2] onClick on <div>/<span> without role="button" and tabIndex',
                ))
    return hits


def check_live_region_announcements(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2E-R3 â€” error/result containers missing aria-live or role=alert"""
    hits = []
    error_container = re.compile(
        r'<div\b[^>]*className\s*=\s*["\'][^"\']*(?<![a-zA-Z-])(?:error|alert|danger)(?![a-zA-Z-])[^"\']*["\'][^>]*>'
    )
    result_container = re.compile(
        r'<div\b[^>]*className\s*=\s*["\'][^"\']*(?<![a-zA-Z-])(?:result|output|response)(?![a-zA-Z-])[^"\']*["\'][^>]*>'
    )
    has_aria_live = re.compile(r'aria-live\s*=')
    has_role_alert = re.compile(r'role\s*=\s*["\']alert["\']')
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        for pattern in (error_container, result_container):
            for m in pattern.finditer(line):
                tag_content = m.group(0)
                if not has_aria_live.search(tag_content) and not has_role_alert.search(tag_content):
                    hits.append((
                        i,
                        m.start() + 1,
                        '[RULE 2.2E-R3] Error/result container missing aria-live or role="alert"',
                    ))
    return hits


def check_non_vitest_imports(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2F-R1 — non-Vitest test framework imports"""
    hits = []
    pattern = re.compile(r'''import.*from\s+['"](?:jest|mocha|enzyme|jasmine)''')
    for i, line in enumerate(lines, 1):
        for m in pattern.finditer(line):
            hits.append((i, m.start() + 1, "[RULE 2.2F-R1] Non-Vitest test framework import"))
    return hits


def check_polling_execute(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2A-R14 — setInterval/setTimeout calling /execute/ endpoint"""
    hits = []
    # Match setInterval or setTimeout on same line as /execute/
    pattern = re.compile(r'\b(setInterval|setTimeout)\b')
    execute_pattern = re.compile(r'/execute/')
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if pattern.search(line) and execute_pattern.search(line):
            hits.append((i, 1, "[RULE 2.2A-R14] setInterval/setTimeout calling /execute/ endpoint"))
    return hits


# ---------------------------------------------------------------------------
# All checks — order matters (matches table in SKILL.md)
# ---------------------------------------------------------------------------
def check_inline_object_array_props(path: Path, lines: list[str]) -> list[tuple[int, int, str]]:
    """2.2C-R3 - inline object/array literals passed as props"""
    hits = []
    object_prop = re.compile(r'\b(?!value\b)\w+\s*=\s*\{\{(?!.*(?:width|height|top|left|right|bottom|transform))')
    array_prop = re.compile(r'\b\w+\s*=\s*\{\[')
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        for m in object_prop.finditer(line):
            hits.append((
                i,
                m.start() + 1,
                "[RULE 2.2C-R3] Inline object literal passed as prop - extract to constant or useMemo",
            ))
        for m in array_prop.finditer(line):
            hits.append((
                i,
                m.start() + 1,
                "[RULE 2.2C-R3] Inline array literal passed as prop - extract to constant or useMemo",
            ))
    return hits


CHECKS = [
    check_raw_fetch,
    check_any_unknown,
    check_hardcoded_format_strings,
    check_raw_hex_colors,
    check_non_lucide_icons,
    check_inline_font_family,
    check_component_keyframes,
    check_eager_renderer_imports,
    check_schema_jsdoc,
    check_aria_label_buttons,
    check_onclick_non_interactive,
    check_live_region_announcements,
    check_non_vitest_imports,
    check_polling_execute,
    check_inline_object_array_props,
]


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def scan_file(path: Path) -> list[tuple[int, int, str]]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:
        return [(0, 0, f"[READ ERROR] {e}")]
    hits: list[tuple[int, int, str]] = []
    for check in CHECKS:
        hits.extend(check(path, lines))
    return hits


def collect_files(root: Path) -> list[Path]:
    frontend_dir = root / "frontend"
    if not frontend_dir.exists():
        return []
    files = []
    for ext in ("*.tsx", "*.ts", "*.css"):  # lint has .css, paradigm doesn't — keep as-is
        for f in frontend_dir.rglob(ext):
            if not any(part in EXCLUDED_DIRS for part in f.parts):
                files.append(f)
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(description="Frontend Lint Sentinel")
    parser.add_argument("--root", default=".", help="Project root directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
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
