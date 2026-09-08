#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import ipaddress
import re
import socket
from pathlib import Path
from typing import Any

from _common import sha256_file

STAMP_RE = re.compile(
    r"\n?<!-- GODOT_BUILD_ID_START -->.*?<!-- GODOT_BUILD_ID_END -->\n?",
    re.DOTALL,
)
BUILD_ID_RE = re.compile(r"BUILD_ID:\s*([A-Za-z0-9._-]+)")
CANVAS_POLICY_RE = re.compile(r"[\"']?canvasResizePolicy[\"']?\s*:\s*([0-9]+)")


def strip_build_stamp(text: str) -> str:
    return STAMP_RE.sub("", text)


def web_files(root: Path) -> dict[str, list[Path] | Path]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Web export directory missing: {root}")
    index = root / "index.html"
    if not index.is_file() or index.stat().st_size == 0:
        raise ValueError("Web export requires nonempty index.html at the export root")
    groups: dict[str, list[Path] | Path] = {
        "index": index,
        "wasm": sorted(p for p in root.glob("*.wasm") if p.is_file() and p.stat().st_size > 0),
        "pck": sorted(p for p in root.glob("*.pck") if p.is_file() and p.stat().st_size > 0),
        "js": sorted(p for p in root.glob("*.js") if p.is_file() and p.stat().st_size > 0),
    }
    for key in ("wasm", "pck", "js"):
        if not groups[key]:
            raise ValueError(f"Web export requires a nonempty *.{key} file")
    return groups


def derive_build_id(root: Path) -> str:
    root = root.resolve()
    files = web_files(root)
    index = files["index"]
    assert isinstance(index, Path)
    aggregate = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel == "BUILD_ID.txt":
            continue
        if path.is_symlink():
            raise ValueError(f"symlink unsupported in Web export: {rel}")
        if path == index:
            data = strip_build_stamp(path.read_text(encoding="utf-8", errors="strict")).encode("utf-8")
            digest = hashlib.sha256(data).hexdigest()
            size = len(data)
        else:
            digest = sha256_file(path)
            size = path.stat().st_size
        aggregate.update(rel.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(str(size).encode("ascii"))
        aggregate.update(b"\0")
        aggregate.update(digest.encode("ascii"))
        aggregate.update(b"\n")
    return "WEB-" + aggregate.hexdigest()[:16].upper()


def read_build_id(root: Path) -> str | None:
    path = root / "BUILD_ID.txt"
    if not path.is_file():
        return None
    value = path.read_text(encoding="utf-8", errors="replace").strip()
    return value or None


def html_build_id(index: Path) -> str | None:
    match = BUILD_ID_RE.search(index.read_text(encoding="utf-8", errors="replace"))
    return match.group(1) if match else None


def canvas_resize_policy(index: Path) -> int | None:
    match = CANVAS_POLICY_RE.search(index.read_text(encoding="utf-8", errors="replace"))
    return int(match.group(1)) if match else None


def is_loopback_host(host: str) -> bool:
    if host.lower() in {"localhost", "localhost."} or host.lower().endswith(".localhost"):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _candidate_ipv4s() -> list[str]:
    values: list[str] = []
    try:
        for item in socket.getaddrinfo(socket.gethostname(), None, family=socket.AF_INET):
            addr = item[4][0]
            if addr not in values:
                values.append(addr)
    except OSError:
        pass
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            probe.connect(("192.0.2.1", 80))
            addr = probe.getsockname()[0]
            if addr not in values:
                values.insert(0, addr)
        finally:
            probe.close()
    except OSError:
        pass
    return values


def detect_lan_ip(preferred: str | None = None) -> str:
    if preferred:
        try:
            ip = ipaddress.ip_address(preferred)
        except ValueError as exc:
            raise ValueError(f"invalid --ip: {preferred}") from exc
        if ip.version != 4 or ip.is_loopback or ip.is_unspecified:
            raise ValueError("--ip must be a non-loopback IPv4 LAN address")
        return preferred
    ranked: list[tuple[int, str]] = []
    for value in _candidate_ipv4s():
        try:
            ip = ipaddress.ip_address(value)
        except ValueError:
            continue
        if ip.is_loopback or ip.is_unspecified or ip.is_link_local:
            continue
        score = 0 if ip.is_private else 1
        ranked.append((score, value))
    if not ranked:
        raise ValueError("could not detect a non-loopback IPv4 address; pass --ip explicitly")
    ranked.sort()
    return ranked[0][1]



def _cfg_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"')
    return value


def read_web_export_preset(project_root: Path, preset_name: str | None = None) -> dict[str, Any]:
    """Read one Web preset from export_presets.cfg without pretending to run Godot."""
    cfg = project_root.expanduser().resolve() / "export_presets.cfg"
    if not cfg.is_file():
        raise ValueError(f"export_presets.cfg missing: {cfg}")
    presets: dict[int, dict[str, Any]] = {}
    current: tuple[int, bool] | None = None
    section_re = re.compile(r"^\[preset\.(\d+)(\.options)?\]$")
    for raw in cfg.read_text(encoding="utf-8", errors="strict").splitlines():
        line = raw.strip()
        if not line or line.startswith((";", "#")):
            continue
        match = section_re.match(line)
        if match:
            index = int(match.group(1))
            current = (index, bool(match.group(2)))
            presets.setdefault(index, {"index": index, "base": {}, "options": {}})
            continue
        if line.startswith("["):
            current = None
            continue
        if current is None or "=" not in line:
            continue
        key, value = line.split("=", 1)
        bucket = "options" if current[1] else "base"
        presets[current[0]][bucket][key.strip()] = _cfg_scalar(value)
    candidates = [p for p in presets.values() if p["base"].get("platform") == "Web"]
    if preset_name is not None:
        candidates = [p for p in candidates if p["base"].get("name") == preset_name]
    if not candidates:
        target = f" named {preset_name!r}" if preset_name else ""
        raise ValueError(f"no Web export preset{target} found in {cfg}")
    if len(candidates) > 1:
        runnable = [p for p in candidates if str(p["base"].get("runnable", "false")).lower() == "true"]
        if len(runnable) == 1:
            candidates = runnable
        else:
            names = [str(p["base"].get("name", p["index"])) for p in candidates]
            raise ValueError(f"multiple Web presets found {names}; pass the intended preset name")
    return candidates[0]


def cfg_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    return None


def cfg_int(value: Any) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None

def normalize_url(url: str) -> str:
    return url.rstrip("/") + "/"


def browser_capture_record(report: Any) -> dict[str, Any] | None:
    if not isinstance(report, dict):
        return None
    capture = report.get("capture")
    return capture if isinstance(capture, dict) else None
