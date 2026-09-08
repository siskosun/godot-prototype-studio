"""Shared local evidence checks. Identity and media signatures do not prove execution."""
from __future__ import annotations
import math
import re
from pathlib import Path
from typing import Any
from _common import sha256_file

HEX = re.compile(r'[0-9a-fA-F]{64}\Z')
KINDS = {'runtime_log', 'input_trace', 'image', 'video', 'audio', 'measurement', 'source_record', 'human_report'}
MEDIA_EXT = {
    'image': {'.png', '.jpg', '.jpeg', '.webp'},
    'video': {'.mp4', '.webm', '.mkv', '.gif'},
    'audio': {'.wav', '.ogg', '.mp3', '.flac'},
}

def filled(value: Any) -> bool:
    return (isinstance(value, str) and bool(value.strip()) and
            not value.strip().startswith(('<', 'REPLACE', 'TODO', '[Choose')))

def finite(value: Any) -> bool:
    try:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    except OverflowError:
        return False

def hash_matches(value: Any, expected: str) -> bool:
    return isinstance(value, str) and bool(HEX.fullmatch(value)) and value.lower() == expected.lower()

def local_file(value: Any, base: Path) -> Path:
    if not filled(value) or '://' in value:
        raise ValueError('local non-placeholder file path required')
    raw = Path(value).expanduser()
    path = raw if raw.is_absolute() else base / raw
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('symlink evidence is unsupported')
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f'missing or empty evidence: {path}')
    return path

def media_signature(path: Path, kind: str) -> bool:
    if kind not in MEDIA_EXT:
        return True
    suffix = path.suffix.lower()
    if suffix not in MEDIA_EXT[kind]:
        return False
    with path.open('rb') as stream:
        head = stream.read(128)
    tests = {
        '.png': head.startswith(b'\x89PNG\r\n\x1a\n'),
        '.jpg': head.startswith(b'\xff\xd8\xff'),
        '.jpeg': head.startswith(b'\xff\xd8\xff'),
        '.webp': head.startswith(b'RIFF') and head[8:12] == b'WEBP',
        '.mp4': head[4:8] == b'ftyp',
        '.webm': head.startswith(b'\x1aE\xdf\xa3'),
        '.mkv': head.startswith(b'\x1aE\xdf\xa3'),
        '.gif': head.startswith((b'GIF87a', b'GIF89a')),
        '.wav': head.startswith(b'RIFF') and head[8:12] == b'WAVE',
        '.ogg': head.startswith(b'OggS'),
        '.mp3': head.startswith(b'ID3') or (len(head) > 1 and head[0] == 255 and (head[1] & 224) == 224),
        '.flac': head.startswith(b'fLaC'),
    }
    return tests.get(suffix, False)

def check_files(records: Any, base: Path, artifact_hash: str, label: str, errors: list[str]) -> set[str]:
    kinds: set[str] = set()
    if not isinstance(records, list) or not records:
        errors.append(f'{label}: nonempty evidence list required')
        return kinds
    for i, record in enumerate(records):
        loc = f'{label}[{i}]'
        if not isinstance(record, dict):
            errors.append(f'{loc}: object required')
            continue
        kind = record.get('kind')
        if not isinstance(kind, str) or kind not in KINDS:
            errors.append(f'{loc}: invalid evidence kind')
        else:
            kinds.add(kind)
        if not hash_matches(record.get('artifactSha256'), artifact_hash):
            errors.append(f'{loc}: artifact hash mismatch')
        try:
            path = local_file(record.get('path'), base)
            if not hash_matches(record.get('sha256'), sha256_file(path)):
                errors.append(f'{loc}: evidence hash mismatch')
            if isinstance(kind, str) and not media_signature(path, kind):
                errors.append(f'{loc}: media extension/signature does not match kind')
        except (OSError, ValueError) as exc:
            errors.append(f'{loc}: {exc}')
    return kinds
