"""
data_snapshot.py — Snapshot and diff the data/ directory.

Usage:
  python core/utils/data_snapshot.py snap        # Save a new snapshot
  python core/utils/data_snapshot.py diff        # Diff latest two snapshots
  python core/utils/data_snapshot.py list        # List all saved snapshots
  python core/utils/data_snapshot.py diff <f1> <f2>  # Diff two specific snapshot files
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SNAPSHOT_DIR = Path(__file__).resolve().parents[2] / ".snapshots"
SNAPSHOT_DIR.mkdir(exist_ok=True)


def hash_file(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def collect_snapshot(directory: Path) -> dict[str, dict[str, str | int]]:
    result: dict[str, dict[str, str | int]] = {}
    for root, _, files in os.walk(directory):
        for name in sorted(files):
            fp = Path(root) / name
            rel = str(fp.relative_to(directory))
            stat = fp.stat()
            result[rel] = {
                "sha256": hash_file(fp),
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
    return result


def save_snapshot() -> Path:
    snap = collect_snapshot(DATA_DIR)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = SNAPSHOT_DIR / f"data_snap_{ts}.json"
    out.write_text(json.dumps(snap, indent=2))
    print(f"Snapshot saved: {out}")
    print(f"  Files captured: {len(snap)}")
    for rel, info in snap.items():
        print(f"  {rel}  ({info['size_bytes']:,} bytes)  {info['modified']}")
    return out


def load_snapshot(path: Path) -> dict[str, dict[str, str | int]]:
    return json.loads(path.read_text())


def diff_snapshots(
    old: dict[str, dict[str, str | int]],
    new: dict[str, dict[str, str | int]],
    label_old: str,
    label_new: str,
) -> None:
    old_keys = set(old)
    new_keys = set(new)

    added = sorted(new_keys - old_keys)
    deleted = sorted(old_keys - new_keys)
    common = sorted(old_keys & new_keys)
    modified = [k for k in common if old[k]["sha256"] != new[k]["sha256"]]
    unchanged = [k for k in common if old[k]["sha256"] == new[k]["sha256"]]

    print(f"\nDiff: {label_old}  →  {label_new}")
    print("=" * 60)

    if not added and not deleted and not modified:
        print("No changes detected. All files identical.")
        return

    if added:
        print(f"\nADDED ({len(added)}):")
        for f in added:
            print(f"  + {f}  ({new[f]['size_bytes']:,} bytes)")

    if deleted:
        print(f"\nDELETED ({len(deleted)}):")
        for f in deleted:
            print(f"  - {f}")

    if modified:
        print(f"\nMODIFIED ({len(modified)}):")
        for f in modified:
            old_size = old[f]["size_bytes"]
            new_size = new[f]["size_bytes"]
            delta = new_size - old_size
            sign = "+" if delta >= 0 else ""
            print(f"  ~ {f}")
            print(f"      size: {old_size:,} → {new_size:,} bytes  ({sign}{delta:,})")
            print(f"      modified: {old[f]['modified']} → {new[f]['modified']}")

    if unchanged:
        print(f"\nUNCHANGED: {len(unchanged)} file(s)")


def list_snapshots() -> None:
    snaps = sorted(SNAPSHOT_DIR.glob("data_snap_*.json"))
    if not snaps:
        print("No snapshots found. Run: python core/utils/data_snapshot.py snap")
        return
    print(f"Snapshots in {SNAPSHOT_DIR}:")
    for s in snaps:
        data = json.loads(s.read_text())
        print(f"  {s.name}  ({len(data)} files)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Snapshot and diff the data/ directory.")
    parser.add_argument("command", choices=["snap", "diff", "list"], help="Command to run")
    parser.add_argument("files", nargs="*", help="Optional: two snapshot filenames for diff")
    args = parser.parse_args()

    if args.command == "snap":
        save_snapshot()

    elif args.command == "list":
        list_snapshots()

    elif args.command == "diff":
        snaps = sorted(SNAPSHOT_DIR.glob("data_snap_*.json"))
        if args.files:
            if len(args.files) != 2:
                print("ERROR: provide exactly two snapshot filenames for explicit diff.")
                sys.exit(1)
            f1 = SNAPSHOT_DIR / args.files[0]
            f2 = SNAPSHOT_DIR / args.files[1]
            for f in (f1, f2):
                if not f.exists():
                    print(f"ERROR: snapshot not found: {f}")
                    sys.exit(1)
            diff_snapshots(load_snapshot(f1), load_snapshot(f2), f1.name, f2.name)
        else:
            if len(snaps) < 2:
                print("Need at least 2 snapshots to diff. Run 'snap' first.")
                sys.exit(1)
            old, new = snaps[-2], snaps[-1]
            diff_snapshots(load_snapshot(old), load_snapshot(new), old.name, new.name)


if __name__ == "__main__":
    main()
