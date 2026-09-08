#!/usr/bin/env python3
"""Inspect declared image sizes/alpha/pivots and optionally make a labeled contact sheet.

Requires Pillow. This does not judge artistic quality or prove in-game integration.
"""
from __future__ import annotations
import argparse
import json
import math
import warnings
from pathlib import Path
from typing import Any
from _common import load_json
from _evidence import filled, finite

KINDS = ('sprite', 'frame', 'ui', 'background', 'other')


def _is_grayish(color: tuple[int, int, int], max_chroma: int = 18) -> bool:
    return max(color) - min(color) <= max_chroma


def _near(a: tuple[int, int, int], b: tuple[int, int, int], tolerance: int = 18) -> bool:
    return all(abs(x - y) <= tolerance for x, y in zip(a, b))


def _contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return max(abs(x - y) for x, y in zip(a, b))


def baked_checkerboard(image: Any) -> bool:
    """Detect a painted transparency-preview grid. This is not an aesthetic score."""
    rgb = image.convert('RGB')
    width, height = rgb.size
    if width < 16 or height < 16:
        return False
    pixels = rgb.load()
    for tile in (8, 16):
        hits = 0
        checks = 0
        for y in range(0, height - tile, tile):
            for x in range(0, width - tile, tile):
                a = pixels[x, y]
                b = pixels[min(x + tile, width - 1), y]
                c = pixels[x, min(y + tile, height - 1)]
                d = pixels[min(x + tile, width - 1), min(y + tile, height - 1)]
                checks += 1
                if (_is_grayish(a) and _is_grayish(b) and _is_grayish(c) and _is_grayish(d) and
                        _near(a, d) and _near(b, c) and not _near(a, b) and _contrast(a, b) >= 20):
                    hits += 1
        if checks >= 8 and hits / checks >= 0.45:
            return True
    return False

def asset_path(raw: Any, root: Path) -> Path:
    if not filled(raw) or '\\' in raw or '://' in raw or ':' in raw:
        raise ValueError('project-relative path required')
    relative = Path(raw)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('asset path escapes project')
    path = root / relative
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('symlink assets unsupported')
    path.resolve().relative_to(root.resolve())
    if not path.is_file():
        raise ValueError('asset file is missing')
    return path

def inspect_assets(data: Any, root: Path, contact_sheet: Path | None = None) -> dict[str, Any]:
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise ValueError('Pillow is required for image inspection; no dependency was installed') from exc
    errors: list[str] = []
    if not isinstance(data, dict):
        data = {}
    rows = data.get('assets')
    if type(data.get('schemaVersion')) is not int or data.get('schemaVersion') != 1 or not isinstance(rows, list) or not rows:
        return {'status': 'FAIL', 'errors': ['schemaVersion 1 and nonempty assets required'], 'assets': []}
    if len(rows) > 512:
        return {'status': 'FAIL', 'errors': ['inspect at most 512 assets per batch'], 'assets': []}
    results, thumbnails, ids, groups = [], [], set(), {}
    for i, row in enumerate(rows):
        label = f'asset[{i}]'
        if not isinstance(row, dict):
            errors.append(f'{label}: object required')
            continue
        aid = row.get('id')
        if not filled(aid) or aid in ids:
            errors.append(f'{label}: unique id required')
            continue
        ids.add(aid)
        if row.get('kind') not in KINDS:
            errors.append(f'{aid}: invalid kind')
        try:
            path = asset_path(row.get('path'), root)
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                with Image.open(path) as source:
                    if source.width * source.height > 40_000_000:
                        raise ValueError('image exceeds safe inspection pixel limit')
                    image = source.convert('RGBA')
            size = list(image.size)
            expected = row.get('expectedSize')
            if expected is not None and (not isinstance(expected, list) or len(expected) != 2 or
                    not all(type(x) is int and x > 0 for x in expected) or expected != size):
                errors.append(f'{aid}: expectedSize mismatch/invalid: actual={size}')
            alpha = image.getchannel('A')
            alpha_range = alpha.getextrema()
            transparent = alpha_range[0] < 255
            if 'requireTransparency' in row and not isinstance(row['requireTransparency'], bool):
                errors.append(f'{aid}: requireTransparency must be boolean')
            if row.get('requireTransparency') is True and not transparent:
                errors.append(f'{aid}: required transparency missing')
            checkerboard = baked_checkerboard(image)
            if row.get('requireTransparency') is True and checkerboard:
                errors.append(f'{aid}: baked checkerboard/preview background is not real transparency')
            if row.get('allowChromaKeyFallback') is True:
                key = row.get('chromaKey')
                if not (isinstance(key, list) and len(key) == 3 and all(type(x) is int and 0 <= x <= 255 for x in key)):
                    errors.append(f'{aid}: chroma-key fallback requires chromaKey [r,g,b]; it is not the default')
            elif row.get('chromaKey') is not None:
                errors.append(f'{aid}: chromaKey is a fallback only; set allowChromaKeyFallback after a real-alpha failure')
            if alpha_range[1] == 0:
                errors.append(f'{aid}: entirely invisible image')
            pivot = row.get('pivot')
            if pivot is not None and (not isinstance(pivot, list) or len(pivot) != 2 or not all(finite(x) for x in pivot) or
                                      not (0 <= pivot[0] <= size[0] and 0 <= pivot[1] <= size[1])):
                errors.append(f'{aid}: pivot must be finite and within source canvas')
            group = row.get('group')
            if group is not None and not filled(group):
                errors.append(f'{aid}: group must be a nonempty string')
            if row.get('kind') == 'frame' and filled(group):
                current = (size, pivot)
                if group in groups and groups[group] != current:
                    errors.append(f'{aid}: frame group {group} canvas/pivot mismatch')
                groups.setdefault(group, current)
            results.append({'id': aid, 'path': row['path'], 'size': size, 'alphaRange': alpha_range,
                            'visibleBounds': alpha.getbbox(), 'pivot': pivot,
                            'realAlpha': transparent, 'bakedCheckerboard': checkerboard})
            if contact_sheet is not None:
                thumb = image.copy()
                thumb.thumbnail((224, 176))
                thumbnails.append((aid, path.name, size, thumb))
        except (OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            errors.append(f'{aid}: {exc}')
    if contact_sheet is not None and thumbnails:
        if contact_sheet.resolve() in {(root / str(row.get('path', ''))).resolve() for row in rows if isinstance(row, dict)}:
            errors.append('contact sheet would overwrite an input asset')
        elif contact_sheet.is_symlink() or any(p.is_symlink() for p in contact_sheet.parents):
            errors.append('contact sheet output may not follow symlinks')
        elif contact_sheet.exists():
            errors.append('contact sheet already exists; choose a fresh output path')
        else:
            cols, cell_w, cell_h = min(4, len(thumbnails)), 240, 224
            sheet = Image.new('RGB', (cols * cell_w, math.ceil(len(thumbnails) / cols) * cell_h), '#303030')
            draw = ImageDraw.Draw(sheet)
            for i, (aid, filename, size, thumb) in enumerate(thumbnails):
                x, y = (i % cols) * cell_w, (i // cols) * cell_h
                sheet.paste(thumb, (x + (cell_w - thumb.width) // 2, y + 4), thumb)
                text = f'{aid}\n{filename}\n{size[0]}x{size[1]}'
                # Portable labels; full Unicode paths remain in the JSON report.
                draw.text((x + 6, y + 182), text.encode('ascii', 'replace').decode(), fill='white')
            contact_sheet.parent.mkdir(parents=True, exist_ok=True)
            sheet.save(contact_sheet)
    return {'status': 'FAIL' if errors else 'PASS', 'errors': errors, 'assets': results,
            'inspectionScope': 'declared image properties only; no aesthetic or runtime judgment'}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--root', required=True)
    parser.add_argument('--contact-sheet')
    args = parser.parse_args()
    try:
        result = inspect_assets(load_json(Path(args.manifest)), Path(args.root).expanduser().absolute(),
                                Path(args.contact_sheet).expanduser().absolute() if args.contact_sheet else None)
    except (OSError, ValueError, TypeError) as exc:
        result = {'status': 'FAIL', 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
