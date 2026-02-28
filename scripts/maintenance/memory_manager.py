import os
import re
import json
from collections import defaultdict

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_DIR = os.path.join(PROJECT_ROOT, "docs", "context", "history")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "docs", "context", "memory_index.json")

# Keywords to look for (Simple Ontology)
KEYWORDS = {
    "Refactor": ["refactor", "rewrite", "migration", "modularization"],
    "Bug Fix": ["bug", "fix", "error", "crash", "exception", "hotfix"],
    "Feature": ["feature", "implement", "create", "add", "expansion"],
    "Testing": ["test", "verify", "validation", "regression", "suite", "pass", "fail"],
    "UI": ["ui", "interface", "dashboard", "widget", "display", "css"],
    "Data": ["data", "schema", "column", "duckdb", "csv", "ingestion"],
    "Architecture": ["architecture", "context", "memory", "facade", "engine"]
}

def scan_history():
    """Scans history files and builds a keyword index."""
    if not os.path.exists(HISTORY_DIR):
        print(f"❌ History directory not found: {HISTORY_DIR}")
        return

    index = defaultdict(list)
    print(f"🔍 Scanning Memory Archive: {HISTORY_DIR}")

    for filename in sorted(os.listdir(HISTORY_DIR)):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(HISTORY_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line_idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Check for keywords
            lower_line = line.lower()
            for category, terms in KEYWORDS.items():
                if any(term in lower_line for term in terms):
                    # Store entry
                    entry = {
                        "date": extract_date(line) or filename.replace(".md", ""),
                        "file": f"docs/context/history/{filename}",
                        "line": line_idx + 1,
                        "preview": line[:100] + "..." if len(line) > 100 else line
                    }
                    index[category].append(entry)

    # Write Index
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    print(f"✅ Memory Index generated at: {OUTPUT_FILE}")
    print(f"📊 Categories indexed: {list(index.keys())}")

def extract_date(text):
    """Extracts date in [YYYY-MM-DD] format."""
    match = re.search(r"\[(\d{4}-\d{2}-\d{2})\]", text)
    return match.group(1) if match else None

if __name__ == "__main__":
    scan_history()
