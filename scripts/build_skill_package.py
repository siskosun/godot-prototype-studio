#!/usr/bin/env python3
"""Build the runtime-only skill.zip from an explicit allowlist."""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_FILES = {"SKILL.md", "VERSION"}
ALLOWED_TOP = {"agents", "assets", "references", "scripts", "templates"}
EXCLUDED_FILES = {
    "references/instruction-audit.md",
    "references/research-basis.md",
    "references/research-basis-previous.md",
}

def include(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    parts = rel.split("/")
    if rel in ALLOWED_FILES:
        return True
    if not parts or parts[0] not in ALLOWED_TOP:
        return False
    if rel in EXCLUDED_FILES:
        return False
    if "__pycache__" in parts or "node_modules" in parts:
        return False
    if path.suffix in {".pyc", ".log"}:
        return False
    if path.name.startswith("ut-") and path.suffix == ".txt":
        return False
    return True

def build(out: Path) -> None:
    files = [p for p in ROOT.rglob("*") if p.is_file() and include(p)]
    present = {p.relative_to(ROOT).as_posix() for p in files}
    required = {"SKILL.md", "VERSION", "agents/openai.yaml"}
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
