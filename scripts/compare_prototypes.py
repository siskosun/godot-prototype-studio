#!/usr/bin/env python3
"""Check controlled comparison records; report finite-measure dominance, not fun."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any
from _common import load_json
from _evidence import HEX, check_files, filled, finite

STATUSES = ('PENDING_EVIDENCE', 'PENDING_HUMAN_OR_EVIDENCE', 'MACHINE_DOMINATED',
            'HUMAN_SELECTED', 'AGENT_SELECTED_WITHIN_BRIEF', 'INCONCLUSIVE')

def compare(data: Any, base: Path) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(data, dict):
        data = {}
        errors.append('comparison must be an object')
    if data.get('schemaVersion') != '1.0':
        errors.append('schemaVersion must be 1.0')
    for field in ('id', 'question', 'changedDimension'):
        if not filled(data.get(field)):
            errors.append(f'missing {field}')
    baseline = data.get('baseline')
    if not isinstance(baseline, dict):
        baseline = {}
    for field in ('identity', 'scenario', 'conditions'):
        if not filled(baseline.get(field)):
            errors.append(f'baseline missing {field}')
    invariants = data.get('invariants')
    if not isinstance(invariants, list) or not invariants or not all(filled(x) for x in invariants):
        errors.append('explicit shared invariants required')
    metrics = data.get('metrics')
    if not isinstance(metrics, list):
        metrics = []
        errors.append('metrics must be a list; use empty for qualitative comparisons')
    objectives: dict[str, str] = {}
    for metric in metrics:
        if not isinstance(metric, dict):
            errors.append('metric must be an object')
            continue
        name, objective = metric.get('name'), metric.get('objective')
        if not filled(name) or name in objectives:
            errors.append('unique metric names required')
            continue
        if objective not in ('MAXIMIZE', 'MINIMIZE'):
            errors.append(f'{name}: invalid objective')
        if not filled(metric.get('unit')) or not filled(metric.get('meaning')):
            errors.append(f'{name}: unit and meaning required')
        objectives[name] = objective
    variants = data.get('variants')
    if not isinstance(variants, list) or not 2 <= len(variants) <= 4:
        errors.append('comparison needs two to four variants')
        variants = variants if isinstance(variants, list) else []
    ids, scored = set(), {}
    for i, variant in enumerate(variants):
        if not isinstance(variant, dict):
            errors.append(f'variant[{i}]: object required')
            continue
        vid = variant.get('id')
        if not filled(vid) or vid in ids:
            errors.append(f'variant[{i}]: unique id required')
            continue
        ids.add(vid)
        for field in ('change', 'isolation', 'rollback'):
            if not filled(variant.get(field)):
                errors.append(f'{vid}: missing {field}')
        run = variant.get('run')
        if not isinstance(run, dict):
            run = {}
        if not filled(run.get('identity')):
            errors.append(f'{vid}: run identity required')
        for field, expected in (('baselineIdentity', baseline.get('identity')),
                                ('scenario', baseline.get('scenario')), ('conditions', baseline.get('conditions'))):
            if not filled(run.get(field)) or run.get(field) != expected:
                errors.append(f'{vid}: incomparable {field}')
        digest = run.get('artifactSha256')
        if not isinstance(digest, str) or not HEX.fullmatch(digest):
            errors.append(f'{vid}: artifactSha256 required')
            digest = ''
        check_files(run.get('evidence'), base, digest, vid, errors)
        if not isinstance(variant.get('humanObservations'), list):
            errors.append(f'{vid}: humanObservations must be a list; leave empty without participants')
        measurements = run.get('measurements')
        if not isinstance(measurements, dict):
            errors.append(f'{vid}: measurements must be an object')
            continue
        scores = {}
        for name in objectives:
            value = measurements.get(name)
            if value is None:
                continue  # Incomplete data is not mechanically ranked.
            if not finite(value):
                errors.append(f'{vid}.{name}: finite number required (not bool or NaN)')
            else:
                scores[name] = value
        scored[vid] = scores
    selection = data.get('selection')
    if not isinstance(selection, dict):
        selection = {}
    status = selection.get('status')
    if status not in STATUSES or not filled(selection.get('rationale')):
        errors.append('selection needs supported status and rationale')
    if status in ('HUMAN_SELECTED', 'AGENT_SELECTED_WITHIN_BRIEF'):
        if selection.get('selectedVariant') not in list(ids):
            errors.append('selectedVariant must identify a compared variant')
        field = 'humanDecisionReference' if status == 'HUMAN_SELECTED' else 'authorityReference'
        if not filled(selection.get(field)):
            errors.append(f'selection requires {field}')
    dominated = []
    if not errors and objectives:
        for candidate, scores in scored.items():
            if set(scores) != set(objectives):
                continue
            for other, other_scores in scored.items():
                if candidate == other or set(other_scores) != set(objectives):
                    continue
                comparisons = [(other_scores[m] - scores[m]) * (1 if direction == 'MAXIMIZE' else -1)
                               for m, direction in objectives.items()]
                if all(x >= 0 for x in comparisons) and any(x > 0 for x in comparisons):
                    dominated.append(candidate)
                    break
    return {'valid': not errors, 'errors': errors, 'variantCount': len(variants),
            'machineDominatedVariants': dominated, 'selectionAuthority': 'BRIEF_DELEGATION_AND_RETAINED_DECISIONS',
            'scope': 'record consistency and declared measures, not statistical significance or experience quality'}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('comparison')
    args = parser.parse_args()
    try:
        path = Path(args.comparison).expanduser().absolute()
        result = compare(load_json(path), path.parent)
    except (ValueError, OSError, TypeError) as exc:
        result = {'valid': False, 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['valid'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
