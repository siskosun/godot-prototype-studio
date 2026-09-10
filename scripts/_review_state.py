"""Local record helpers. File identity is not evidence of execution or truth."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from _common import sha256_file

SHA256 = re.compile(r"^[0-9a-f]{64}$")
MAX_RECORD_BYTES = 2 * 1024 * 1024


def project_root(path: Path) -> Path:
    raw = path.expanduser().absolute()
    if raw.is_symlink() or any(p.is_symlink() for p in raw.parents):
        raise ValueError("symlink project root is unsupported")
    if not raw.is_dir():
        raise ValueError("project directory does not exist")
    return raw.resolve()


def local_path(root: Path, value: Any) -> Path:
    if (not isinstance(value, str) or not value or value != value.strip()
            or any(ord(c) < 32 for c in value) or "\\" in value or ":" in value
            or value.startswith("/") or any(p in {"", ".", ".."} for p in value.split("/"))):
        raise ValueError("canonical project-relative path required")
    path = root / value
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError("symlink record/dependency is unsupported")
    path.resolve().relative_to(root.resolve())
    return path


def read_record(path: Path) -> dict[str, Any]:
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError("symlink record is unsupported")
    if path.stat().st_size > MAX_RECORD_BYTES:
        raise ValueError("record exceeds 2 MiB safety limit")
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON value: {value}")
    def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    data = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant,
                      object_pairs_hook=unique_pairs)
    if not isinstance(data, dict) or type(data.get("schemaVersion")) is not int or data["schemaVersion"] != 1:
        raise ValueError("record must be an object with integer schemaVersion 1")
    return data


def fingerprint(root: Path, relative: str) -> dict[str, str]:
    path = local_path(root, relative)
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"nonempty file required: {relative}")
    return {"path": relative, "sha256": sha256_file(path)}


def check_reference(root: Path, record: Any) -> str | None:
    if not isinstance(record, dict) or not isinstance(record.get("sha256"), str) or not SHA256.fullmatch(record["sha256"]):
        raise ValueError("file reference needs path and lowercase SHA-256")
    path = local_path(root, record.get("path"))
    if not path.is_file():
        return f"missing file: {record['path']}"
    if path.stat().st_size == 0:
        return f"empty file: {record['path']}"
    if sha256_file(path) != record["sha256"]:
        return f"changed file: {record['path']}"
    return None
