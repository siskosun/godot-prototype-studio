#!/usr/bin/env python3
"""Stamp a Godot Web export with a deterministic payload BUILD_ID."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _web import derive_build_id, strip_build_stamp, web_files


def stamp(root: Path) -> dict[str, str]:
    root = root.expanduser().resolve()
    files = web_files(root)
    index = files["index"]
    assert isinstance(index, Path)
    build_id = derive_build_id(root)
    html = strip_build_stamp(index.read_text(encoding="utf-8", errors="strict"))
    block = f'''\n<!-- GODOT_BUILD_ID_START -->
<div id="godot-build-id" aria-label="Build ID" style="position:fixed;right:8px;bottom:6px;z-index:2147483647;padding:2px 5px;border-radius:3px;background:rgba(0,0,0,.55);color:#fff;font:10px/1.2 monospace;pointer-events:none;opacity:.78">BUILD_ID: {build_id}</div>
<script>window.GODOT_BUILD_ID = {json.dumps(build_id)};</script>
<!-- GODOT_BUILD_ID_END -->\n'''
    if "</body>" in html.lower():
        pos = html.lower().rfind("</body>")
        html = html[:pos] + block + html[pos:]
    else:
        html += block
    index.write_text(html, encoding="utf-8")
    (root / "BUILD_ID.txt").write_text(build_id + "\n", encoding="utf-8")
    return {"buildId": build_id, "index": str(index), "buildIdFile": str(root / "BUILD_ID.txt")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export_dir")
    args = parser.parse_args()
    try:
        result = stamp(Path(args.export_dir))
        print(json.dumps({"status": "PASS", **result}, indent=2))
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
