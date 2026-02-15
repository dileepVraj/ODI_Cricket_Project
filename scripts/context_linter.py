import os
import re
import json
import glob
import sys
import io

# Force UTF-8 output for Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_FILE = os.path.join(PROJECT_ROOT, "docs", "context", "rules.json")

def load_rules():
    if not os.path.exists(RULES_FILE):
        print(f"❌ Rules file not found: {RULES_FILE}")
        return []
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def check_file(filepath, rules):
    violations = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        return [] # Skip binary files

    rel_path = os.path.relpath(filepath, PROJECT_ROOT).replace("\\", "/")

    for rule in rules:
        # Check inclusions
        if not any(glob.fnmatch.fnmatch(rel_path, p) for p in rule["include"]):
            continue
        # Check exclusions
        if "exclude" in rule and any(glob.fnmatch.fnmatch(rel_path, p) for p in rule["exclude"]):
            continue

        pattern = re.compile(rule["pattern"])
        
        for i, line in enumerate(lines):
            if pattern.search(line):
                violations.append({
                    "file": rel_path,
                    "line": i + 1,
                    "rule": rule["id"],
                    "message": rule["message"],
                    "severity": rule["severity"]
                })
    return violations


def check_governance_docs():
    """
    Verify that critical governance & context documents exist.
    These files are the 'source of truth' for AI agent behavior.
    Missing files = broken context pipeline = agent amnesia.
    """
    REQUIRED_DOCS = [
        {"path": "docs/ai/GEMINI.md",           "purpose": "Agent Protocols & Governance Rules"},
        {"path": "docs/ai/AI_MEMORY.md",         "purpose": "Living Memory — Sprint Status & Session History"},
        {"path": "docs/context/active_state.md",  "purpose": "Current Architecture State & Anti-Patterns"},
        {"path": "docs/context/rules.json",       "purpose": "Automated Linting Rules"},
    ]

    violations = []
    for doc in REQUIRED_DOCS:
        full_path = os.path.join(PROJECT_ROOT, doc["path"].replace("/", os.sep))
        if not os.path.exists(full_path):
            violations.append({
                "file": doc["path"],
                "line": 0,
                "rule": "GOVERNANCE_DOC_MISSING",
                "message": f"🚨 CRITICAL: Governance doc missing: {doc['path']} ({doc['purpose']}). This file is required for agent context pipeline.",
                "severity": "CRITICAL"
            })
    return violations


def run_linter():
    print(f"🔍 Running Neuro-Symbolic Linter on: {PROJECT_ROOT}")
    rules = load_rules()
    print(f"📜 Loaded {len(rules)} rules.")

    all_violations = []

    # Phase 1: Check governance doc integrity
    print("📋 Phase 1: Checking governance docs...")
    gov_violations = check_governance_docs()
    all_violations.extend(gov_violations)
    if gov_violations:
        print(f"  ❌ {len(gov_violations)} governance docs missing!")
    else:
        print("  ✅ All governance docs present.")

    # Phase 2: Walk project and check pattern rules
    print("🔎 Phase 2: Checking code rules...")
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if "node_modules" in dirs: dirs.remove("node_modules")
        if ".git" in dirs: dirs.remove(".git")
        if ".venv" in dirs: dirs.remove(".venv")
        if "__pycache__" in dirs: dirs.remove("__pycache__")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                all_violations.extend(check_file(filepath, rules))

    # Report to file to avoid console encoding issues
    report_file = os.path.join(PROJECT_ROOT, "linter_report.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        if all_violations:
            f.write(f"❌ Found {len(all_violations)} violations:\n\n")
            for v in all_violations:
                icon = "🔴" if v["severity"] == "CRITICAL" else "🟠"
                f.write(f"{icon} [{v['rule']}] {v['file']}:{v['line']}\n")
                f.write(f"   {v['message']}\n")
            print(f"❌ Found {len(all_violations)} violations. See linter_report.txt")
            sys.exit(1)
        else:
            f.write("✅ No violations found. Codebase is clean!")
            print("✅ No violations found.")
            sys.exit(0)

if __name__ == "__main__":
    run_linter()

