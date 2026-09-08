#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import deterministic_tree_hash, utc_now, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute a deterministic SHA-256. Directory mode excludes .git, .godot, __pycache__, .DS_Store, and .prototype by default.")
    parser.add_argument("path")
    parser.add_argument("--exclude", action="append", default=[], help="Additional relative path prefix to exclude.")
    parser.add_argument("--write", help="Write JSON report to this path.")
    parser.add_argument("--include-files", action="store_true", help="Include the file manifest in stdout/report.")
    args = parser.parse_args()

    target = Path(args.path).expanduser().absolute()
    try:
        digest, entries = deterministic_tree_hash(target, args.exclude)
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 2
    report = {
        "schemaVersion": 1,
        "generatedAt": utc_now(),
        "path": str(target),
        "type": "file" if target.is_file() else "directory",
        "sha256": digest,
        "fileCount": len(entries),
        "totalBytes": sum(entry["size"] for entry in entries),
        "excludedPrefixes": [".prototype", *args.exclude],
    }
    if args.include_files:
        report["files"] = entries
    if args.write:
        write_json(Path(args.write).expanduser().resolve(), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
