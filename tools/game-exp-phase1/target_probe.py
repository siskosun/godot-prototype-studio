#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import unicodedata
from pathlib import Path

SAFE_INT = (1 << 53) - 1
WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *{f"COM{i}" for i in range(1, 10)}, *{f"LPT{i}" for i in range(1, 10)}}
FORBIDDEN_CHARS = set('<>:"\\|?*')


class ProbeError(ValueError):
    pass


def utf16_sort_key(value: str):
    encoded = value.encode("utf-16-be")
    return tuple(int.from_bytes(encoded[i:i+2], "big") for i in range(0, len(encoded), 2))


def json_string(value: str) -> bytes:
    out = bytearray(b'"')
    for ch in value:
        cp = ord(ch)
        if ch == '"':
            out.extend(b'\\"')
        elif ch == "\\":
            out.extend(b"\\\\")
        elif ch == "\b":
            out.extend(b"\\b")
        elif ch == "\t":
            out.extend(b"\\t")
        elif ch == "\n":
            out.extend(b"\\n")
        elif ch == "\f":
            out.extend(b"\\f")
        elif ch == "\r":
            out.extend(b"\\r")
        elif cp < 0x20:
            out.extend(f"\\u{cp:04x}".encode("ascii"))
        else:
            out.extend(ch.encode("utf-8"))
    out.extend(b'"')
    return bytes(out)


def canonical_json(value) -> bytes:
    if value is None:
        return b"null"
    if value is True:
        return b"true"
    if value is False:
        return b"false"
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > SAFE_INT:
            raise ProbeError("integer outside RFC8785-safe range")
        return str(value).encode("ascii")
    if isinstance(value, float):
        raise ProbeError("float not allowed")
    if isinstance(value, str):
        return json_string(value)
    if isinstance(value, list):
        return b"[" + b",".join(canonical_json(x) for x in value) + b"]"
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            raise ProbeError("object keys must be strings")
        return b"{" + b",".join(
            json_string(k) + b":" + canonical_json(value[k])
            for k in sorted(value, key=utf16_sort_key)
        ) + b"}"
    raise ProbeError(f"unsupported type: {type(value).__name__}")


def digest(value) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def normalize_path(path: str) -> str:
    if not path or "\\" in path:
        raise ProbeError("path must be non-empty and use '/'")
    if unicodedata.normalize("NFC", path) != path:
        raise ProbeError("path must be NFC")
    if path.startswith("/") or path.endswith("/") or "//" in path:
        raise ProbeError("path must be repository-relative")
    for part in path.split("/"):
        if part in {".", ".."} or not part:
            raise ProbeError("invalid component")
        if part.endswith((" ", ".")):
            raise ProbeError("Windows-incompatible trailing character")
        if any(ch in FORBIDDEN_CHARS or ord(ch) < 32 for ch in part):
            raise ProbeError("Windows-incompatible character")
        if part.split(".", 1)[0].upper() in WINDOWS_RESERVED:
            raise ProbeError("Windows reserved name")
    return path


def check_collisions(paths):
    seen = {}
    for path in paths:
        normalize_path(path)
        key = unicodedata.normalize("NFC", path).casefold()
        if key in seen and seen[key] != path:
            raise ProbeError(f"case-fold collision: {seen[key]} vs {path}")
        seen[key] = path


def expect_fail(fn, label):
    try:
        fn()
    except Exception:
        return {"name": label, "status": "PASS"}
    return {"name": label, "status": "FAIL", "detail": "expected rejection but input was accepted"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    vector = {
        "z": "末",
        "a": ["Alpha", True, None, 42],
        "unicode": "é/游戏/Ω",
        "nested": {"β": "two", "A": "one"},
    }
    actual_digest = digest(vector)
    expected_digest = "sha256:2c0acdd98f9571bc7c3e2eadc672579b296ad74ca233aff8c11f1deff1a0d8e3"

    checks = [
        {"name": "canonical_digest", "status": "PASS" if actual_digest == expected_digest else "FAIL",
         "actual": actual_digest, "expected": expected_digest},
        {"name": "safe_int_max", "status": "PASS" if digest({"n": SAFE_INT}) else "FAIL"},
        expect_fail(lambda: digest({"n": SAFE_INT + 1}), "reject_2pow53"),
        expect_fail(lambda: normalize_path("CON/file.txt"), "reject_windows_reserved"),
        expect_fail(lambda: normalize_path("bad\\path.txt"), "reject_backslash"),
        expect_fail(lambda: normalize_path(unicodedata.normalize("NFD", "é") + "/file.txt"), "reject_nfd_path"),
        expect_fail(lambda: check_collisions(["Foo.tscn", "foo.tscn"]), "reject_casefold_collision"),
    ]

    result = {
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "sha": os.environ.get("GITHUB_SHA"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "runner_os": os.environ.get("RUNNER_OS"),
        "python": platform.python_version(),
        "unicode_version": unicodedata.unidata_version,
        "checks": checks,
        "overall": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL",
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
