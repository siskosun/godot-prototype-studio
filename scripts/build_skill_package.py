#!/usr/bin/env python3
"""Build the runtime-only skill.zip from the repository."""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_TOP = {".git", ".github", "audit", "tests"}
EXCLUDED_FILES = {
    "CHANGELOG.md",
    "README.md",
    "README.zh-CN.md",
    "references/instruction-audit.md",
    "references/research-basis.md",
    "references/research-basis-previous.md",
}

def include(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    parts = rel.split("/")
    if parts[0] in EXCLUDED_TOP:
        return False
    if rel in EXCLUDED_FILES:
        return False
    if "__pycache__" in parts or path.suffix == ".pyc":
        return False
    return True

def build(out: Path) -> None:
    files = [p for p in ROOT.rglob("*") if p.is_file() and include(p)]
    required = {"SKILL.md", "agents/openai.yaml"}
    present = {p.relative_to(ROOT).as_posix() for p in files}
    missing = required - present
    if missing:
        raise SystemExit(f"missing required runtime files: {sorted(missing)}")
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(files):
            zf.write(path, path.relative_to(ROOT).as_posix())

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="skill.zip")
    args = parser.parse_args()
    out = Path(args.out).resolve()
    build(out)
    print(out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
