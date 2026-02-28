import os
import json
import argparse
import datetime

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOCUS_FILE = os.path.join(PROJECT_ROOT, "docs", "context", "focus.json")

def load_focus():
    """Loads focus state or returns empty default."""
    if os.path.exists(FOCUS_FILE):
        try:
            with open(FOCUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"task": None, "files": [], "start_time": None}

def save_focus(state):
    """Saves focus state to JSON."""
    os.makedirs(os.path.dirname(FOCUS_FILE), exist_ok=True)
    with open(FOCUS_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    print(f"✅ Focus updated: {FOCUS_FILE}")

def start_task(task_name):
    """Resets focus and starts a new task."""
    state = {
        "task": task_name,
        "files": [],
        "start_time": datetime.datetime.now().isoformat()
    }
    save_focus(state)
    print(f"🚀 Started task: '{task_name}'")

def add_file(filepath):
    """Adds a file to the active context."""
    state = load_focus()
    if not state.get("task"):
        print("❌ No active task. Use 'start <task>' first.")
        return

    # Normalize path
    rel_path = filepath
    if os.path.isabs(filepath):
        try:
            rel_path = os.path.relpath(filepath, PROJECT_ROOT)
        except ValueError:
            pass # Keep as is if on different drive

    if rel_path not in state["files"]:
        state["files"].append(rel_path)
        save_focus(state)
        print(f"📂 Added file: {rel_path}")
    else:
        print(f"ℹ️ File already in focus: {rel_path}")

def clear_focus():
    """Clears the active context."""
    if os.path.exists(FOCUS_FILE):
        os.remove(FOCUS_FILE)
        print("🧹 Focus cleared.")
    else:
        print("ℹ️ No active focus to clear.")

def show_status():
    """Prints current focus status."""
    state = load_focus()
    if not state.get("task"):
        print("ℹ️ No active task.")
        return

    print(f"🎯 Current Task: {state['task']}")
    print(f"🕒 Started: {state['start_time']}")
    print(f"📂 Active Files: ({len(state['files'])})")
    for f in state["files"]:
        print(f"  - {f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage AI Working Context")
    subparsers = parser.add_subparsers(dest="command")

    # Start
    start_parser = subparsers.add_parser("start", help="Start a new task")
    start_parser.add_argument("name", help="Task name/description")

    # Add
    add_parser = subparsers.add_parser("add", help="Add file to context")
    add_parser.add_argument("file", help="File path")

    # Clear
    subparsers.add_parser("clear", help="Clear context")

    # Status
    subparsers.add_parser("status", help="Show current context")

    args = parser.parse_args()

    if args.command == "start":
        start_task(args.name)
    elif args.command == "add":
        add_file(args.file)
    elif args.command == "clear":
        clear_focus()
    elif args.command == "status":
        show_status()
    else:
        parser.print_help()
