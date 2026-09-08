#!/usr/bin/env python3
"""Inventory Godot text declarations; not a full parser, inheritance resolver or live bridge."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from _common import should_exclude, utc_now, write_json

ATTR = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)=("(?:\\.|[^"\\])*"|ExtResource\("[^"\n]*"\)|[^\s\]]+)')

def attributes(text: str) -> dict[str, str]:
    result = {}
    for key, raw in ATTR.findall(text):
        try:
            result[key] = json.loads(raw) if raw.startswith('"') else raw
        except json.JSONDecodeError:
            result[key] = raw
    return result

def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()

def parse_input_actions(text: str) -> list[str]:
    section = re.search(r'\[input\]\s*(.*?)(?=\n\[|\Z)', text, re.DOTALL)
    return sorted(re.findall(r'^([A-Za-z0-9_./-]+)\s*=\s*\{', section.group(1), re.MULTILINE)) if section else []

def parse_scene(path: Path, root: Path) -> dict:
    text = path.read_text(encoding='utf-8', errors='replace')
    nodes, external, connections = [], [], []
    for tag, body in re.findall(r'^\[(node|ext_resource|connection)\s+([^\n]*)\]\s*$', text, re.MULTILINE):
        attrs = attributes(body)
        if tag == 'node':
            nodes.append({'name': attrs.get('name', ''), 'type': attrs.get('type'),
                          'parent': attrs.get('parent', ''), 'instance': attrs.get('instance'),
                          'typeResolution': 'DECLARED' if 'type' in attrs else 'UNRESOLVED_INHERITED_OR_INSTANCE'})
        elif tag == 'ext_resource':
            external.append(attrs)
        else:
            connections.append(attrs)
    return {'path': rel(root, path), 'nodes': nodes, 'externalResources': external,
            'resourceRefs': sorted(set(re.findall(r'(?:res|uid)://[^"\s)]+', text))),
            'scriptRefs': sorted({r['path'] for r in external if 'path' in r and
                                  (r.get('type') == 'Script' or r['path'].endswith(('.gd', '.cs')))}),
            'signalConnections': connections}

def parse_script(path: Path, root: Path) -> dict:
    text = path.read_text(encoding='utf-8', errors='replace')
    extends = re.search(r'^\s*extends\s+(.+)$', text, re.MULTILINE)
    return {'path': rel(root, path), 'extends': extends.group(1).strip() if extends else '',
            'signals': sorted(set(re.findall(r'^\s*signal\s+([A-Za-z_][A-Za-z0-9_]*)', text, re.MULTILINE)))}

def inspect(root: Path) -> dict:
    project = root / 'project.godot'
    if not project.is_file() or project.is_symlink():
        raise ValueError('a real project.godot file is required')
    paths, skipped = [], []
    for p in sorted(root.rglob('*')):
        if should_exclude(p.relative_to(root)):
            continue
        if p.is_symlink() or any(parent.is_symlink() for parent in p.parents):
            skipped.append(rel(root, p))
            continue
        if p.is_file() and p.suffix in ('.tscn', '.gd', '.tres'):
            if p.stat().st_size > 8 * 1024 * 1024:
                skipped.append(rel(root, p))
            else:
                paths.append(p)
    text = project.read_text(encoding='utf-8', errors='replace')
    main_scene = re.search(r'run/main_scene\s*=\s*"([^"\n]+)"', text)
    return {'schemaVersion': '1.0', 'generatedAt': utc_now(), 'projectRoot': str(root),
            'sources': [{'kind': 'STATIC_PROJECT', 'exercised': True, 'confidence': 'DECLARED'}],
            'project': {'mainScene': main_scene.group(1) if main_scene else '', 'inputActions': parse_input_actions(text)},
            'scenes': [parse_scene(p, root) for p in paths if p.suffix == '.tscn'],
            'scripts': [parse_script(p, root) for p in paths if p.suffix == '.gd'],
            'resources': [rel(root, p) for p in paths if p.suffix == '.tres'], 'observations': [],
            'skippedPaths': skipped, 'limitations': ['Static text declarations only; engine load and inheritance unverified.']}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project_root')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--output')
    args = parser.parse_args()
    try:
        root = Path(args.project_root).expanduser().absolute()
        result = inspect(root)
        if args.write or args.output:
            output = Path(args.output).expanduser().absolute() if args.output else root / '.prototype/spec/engine_static_context.json'
            if output.suffix.lower() != '.json' or output == root / 'project.godot':
                raise ValueError('output must be a JSON record, not a project source file')
            write_json(output, result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({'status': 'FAIL', 'errors': [str(exc)]}))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
