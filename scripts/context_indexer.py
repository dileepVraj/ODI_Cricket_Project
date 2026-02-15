import os
import ast
import json
import sys

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "docs", "context")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "project_map.json")

# Ignore specific directories and files
IGNORE_DIRS = {".git", ".venv", "__pycache__", ".gemini", "node_modules", ".vscode"}
IGNORE_FILES = {".DS_Store"}

def get_docstring(node):
    """Extracts the docstring from an AST node."""
    return ast.get_docstring(node) or ""

def parse_file(filepath):
    """Parses a Python file and extracts structure."""
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            return None

    file_data = {
        "imports": [],
        "classes": {},
        "functions": {}
    }

    for node in ast.walk(tree):
        # Imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                file_data["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                file_data["imports"].append(f"{module}.{alias.name}")

        # Classes
        elif isinstance(node, ast.ClassDef):
            methods = [
                n.name for n in node.body if isinstance(n, ast.FunctionDef)
            ]
            file_data["classes"][node.name] = {
                "methods": methods,
                "docstring": get_docstring(node),
                "lineno": node.lineno
            }

        # Top-level Functions
        elif isinstance(node, ast.FunctionDef):
            # Check if it's a top-level function (not inside a class)
            # AST generic walk doesn't track parent, so we might capture methods here if we aren't careful.
            # However, for a holographic index, capturing all defs is acceptable for now.
            # To be more precise, we'd iterate tree.body.
            pass

    # Precise top-level iteration to separate functions from methods
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
             file_data["functions"][node.name] = {
                "docstring": get_docstring(node),
                "lineno": node.lineno
            }

    return file_data

def generate_map():
    """Walks the project directory and generates the map."""
    project_map = {}

    print(f"🔍 Scanning project root: {PROJECT_ROOT}")

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file.endswith(".py") and file not in IGNORE_FILES:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, PROJECT_ROOT).replace("\\", "/")
                
                print(f"  Parsing: {rel_path}")
                data = parse_file(filepath)
                if data:
                    project_map[rel_path] = data

    # --- Governance & Context Documents ---
    # These critical docs define agent behavior and project architecture.
    # Including them in the index ensures any consumer of project_map.json
    # knows they exist and must be read before coding.
    GOVERNANCE_DOCS = [
        {"path": "docs/ai/GEMINI.md",          "role": "Agent Protocols & Governance Rules (MUST READ FIRST)"},
        {"path": "docs/ai/AI_MEMORY.md",        "role": "Living Memory — Sprint Status & Session History"},
        {"path": "docs/context/active_state.md", "role": "Current Architecture State & Anti-Patterns"},
        {"path": "docs/context/rules.json",      "role": "Automated Linting Rules (enforced by context_linter.py)"},
        {"path": "docs/guides/ENGINEERING_STANDARDS.md", "role": "Coding Constitution & Achievement Tracker"},
        {"path": "docs/guides/DEV_GUIDE.md",     "role": "Developer Onboarding & Data Pipeline"},
        {"path": "docs/guides/TECHNICAL_DOCUMENTATION.md", "role": "File-by-File Codebase Reference"},
        {"path": "docs/architecture/applicationArchitecture.md", "role": "System Architecture Diagrams"},
        {"path": "docs/plans/FRONTEND_ROADMAP.md", "role": "Frontend Phase Tracker"},
        {"path": "docs/design/UI_SPEC.md",       "role": "V5 Manifest-Driven UI Design Spec"},
        {"path": "docs/handovers/handover.md",   "role": "Project Handover Summary"},
    ]

    governance_index = []
    for doc in GOVERNANCE_DOCS:
        full_path = os.path.join(PROJECT_ROOT, doc["path"].replace("/", os.sep))
        exists = os.path.exists(full_path)
        governance_index.append({
            "path": doc["path"],
            "role": doc["role"],
            "exists": exists
        })
        status = "✅" if exists else "❌ MISSING"
        print(f"  Governance: {doc['path']} [{status}]")

    project_map["__governance__"] = {
        "description": "Critical governance & context docs. Agents MUST read docs/ai/GEMINI.md before any coding.",
        "bootstrap_order": [
            "docs/ai/AI_MEMORY.md",
            "docs/ai/GEMINI.md",
            "docs/context/active_state.md",
            "docs/guides/ENGINEERING_STANDARDS.md"
        ],
        "documents": governance_index
    }

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Write to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(project_map, f, indent=2)

    print(f"\n✅ Holographic Index generated at: {OUTPUT_FILE}")
    print(f"📊 Indexed {len(project_map) - 1} Python files + {len(governance_index)} governance docs.")

if __name__ == "__main__":
    generate_map()

