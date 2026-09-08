#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DEFAULT_TREE_EXCLUDES = {
    ".git",
    ".godot",
    "__pycache__",
    ".DS_Store",
}
DEFAULT_PREFIX_EXCLUDES = {
    ".prototype",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def should_exclude(relative: Path, extra: Iterable[str] = ()) -> bool:
    parts = relative.parts
    if any(part in DEFAULT_TREE_EXCLUDES for part in parts):
        return True
    posix = relative.as_posix()
    for prefix in DEFAULT_PREFIX_EXCLUDES | set(extra):
        prefix = prefix.rstrip("/")
        if posix == prefix or posix.startswith(prefix + "/"):
            return True
    return False


def deterministic_tree_hash(root: Path, extra_excludes: Iterable[str] = ()) -> tuple[str, list[dict[str, Any]]]:
    if root.is_symlink():
        raise ValueError(f"symlink artifact is unsupported: {root}")
    if not root.exists():
        raise ValueError(f"missing path: {root}")
    if root.is_file():
        digest = sha256_file(root)
        return digest, [{"path": root.name, "size": root.stat().st_size, "sha256": digest}]

    for candidate in root.rglob("*"):
        if candidate.is_symlink() and not should_exclude(candidate.relative_to(root), extra_excludes):
            raise ValueError(f"symlink in artifact is unsupported: {candidate}")
    entries: list[dict[str, Any]] = []
    aggregate = hashlib.sha256()
    for path in sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        if should_exclude(relative, extra_excludes):
            continue
        file_digest = sha256_file(path)
        size = path.stat().st_size
        rel = relative.as_posix()
        entries.append({"path": rel, "size": size, "sha256": file_digest})
        aggregate.update(rel.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(str(size).encode("ascii"))
        aggregate.update(b"\0")
        aggregate.update(file_digest.encode("ascii"))
        aggregate.update(b"\n")
    return aggregate.hexdigest(), entries
