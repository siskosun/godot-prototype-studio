#!/usr/bin/env python3
"""Validate a near-release review's records, evidence identities and unresolved defects.

This does not run Godot, assess aesthetics, verify a reviewer's honesty, or certify fun.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any
from _common import deterministic_tree_hash, load_json
from _evidence import HEX, check_files, filled, hash_matches

DIMENSIONS = ('gameplay', 'ux', 'art', 'motion_audio', 'reliability', 'performance', 'platform_access', 'text_render', 'delivery_rights')
REQUIRED_KINDS = {
    'gameplay': [{'input_trace'}],
    'ux': [{'input_trace'}, {'image', 'video'}],
    'art': [{'image', 'video'}],
    'motion_audio': [{'video', 'audio'}],
    'reliability': [{'runtime_log', 'input_trace'}],
    'performance': [{'measurement'}],
    'platform_access': [{'input_trace'}, {'image', 'video'}],
    'text_render': [{'source_record'}, {'image', 'video'}],
    'delivery_rights': [{'source_record', 'runtime_log'}],
}

def validate_quality(data: Any, base: Path, artifact_hash: str) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(data, dict):
        data = {}
        errors.append('review must be an object')
    if type(data.get('schemaVersion')) is not int or data.get('schemaVersion') != 2:
        errors.append('schemaVersion must be integer 2')
    if data.get('profile') != 'NEAR_RELEASE_SLICE':
        errors.append('profile must be NEAR_RELEASE_SLICE')
    if not hash_matches(data.get('artifactSha256'), artifact_hash):
        errors.append('review artifactSha256 mismatch')
    reviewer = data.get('reviewer')
    if not isinstance(reviewer, dict):
        reviewer = {}
    if reviewer.get('kind') not in ('self', 'independent', 'human') or not filled(reviewer.get('identity')):
        errors.append('reviewer must declare identity and self/independent/human kind')
    if reviewer.get('kind') == 'human' and reviewer.get('isHuman') is not True:
        errors.append('human reviewer needs explicit isHuman=true; never relabel an agent')
    if reviewer.get('kind') == 'independent' and not filled(reviewer.get('independenceEvidence')):
        errors.append('independent reviewer needs independenceEvidence')
    rows = data.get('dimensions')
    if not isinstance(rows, list):
        rows = []
        errors.append('dimensions must be a list')
    seen: set[str] = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f'dimensions[{i}] must be an object')
            continue
        name = row.get('id')
        if not isinstance(name, str) or name not in DIMENSIONS or name in seen:
            errors.append(f'dimensions[{i}]: unknown or duplicate id')
            continue
        seen.add(name)
        refs = row.get('criterionRefs')
        if not isinstance(refs, list) or not refs or not all(filled(x) for x in refs):
            errors.append(f'{name}: link criteria/applicability in the authoritative brief')
        status = row.get('status')
        if status not in ('PASS', 'FAIL', 'UNVERIFIED', 'NOT_APPLICABLE'):
            errors.append(f'{name}: status must be PASS, FAIL, UNVERIFIED, or NOT_APPLICABLE')
            status = 'UNVERIFIED'
        if not filled(row.get('observation')):
            errors.append(f'{name}: observation or applicability rationale required')
        if status == 'PASS':
            kinds = check_files(row.get('evidence'), base, artifact_hash, name, errors)
            if name == 'gameplay':
                records = row.get('evidence') or []
                if not isinstance(records, list) or not any(isinstance(r, dict) and r.get('kind') == 'input_trace' and
                        r.get('entry') == 'NORMAL_START' and r.get('terminalObserved') is True for r in records):
                    errors.append('gameplay: normal-start player path with observed terminal/reset required')
            for alternatives in REQUIRED_KINDS[name]:
                if not kinds.intersection(alternatives):
                    errors.append(f'{name}: evidence needs one of {sorted(alternatives)}')
        elif status == 'NOT_APPLICABLE':
            evidence = row.get('evidence')
            if evidence not in (None, []):
                errors.append(f'{name}: NOT_APPLICABLE should not carry pass evidence; explain absence in observation')
        elif status == 'FAIL':
            errors.append(f'{name}: applicable quality dimension is FAIL')
            if row.get('evidence') not in (None, []):
                check_files(row.get('evidence'), base, artifact_hash, name, errors)
        else:
            errors.append(f'{name}: applicable quality dimension is UNVERIFIED')
            if row.get('evidence') not in (None, []):
                check_files(row.get('evidence'), base, artifact_hash, name, errors)
    if seen != set(DIMENSIONS):
        errors.append(f'missing quality dimensions: {sorted(set(DIMENSIONS) - seen)}')
    findings = data.get('findings')
    if not isinstance(findings, list):
        findings = []
        errors.append('findings must be a list (empty only if none found)')
    ids: set[str] = set()
    for i, finding in enumerate(findings):
        label = f'finding[{i}]'
        if not isinstance(finding, dict):
            errors.append(f'{label}: object required')
            continue
        fid = finding.get('id')
        if not filled(fid) or fid in ids:
            errors.append(f'{label}: unique id required')
        else:
            ids.add(fid)
        if finding.get('dimension') not in DIMENSIONS:
            errors.append(f'{label}: invalid dimension')
        severity, status = finding.get('severity'), finding.get('status')
        if severity not in ('BLOCKER', 'MAJOR', 'MINOR') or status not in ('OPEN', 'FIXED', 'REJECTED'):
            errors.append(f'{label}: invalid severity/status')
        if not filled(finding.get('description')):
            errors.append(f'{label}: description required')
        observed_hash = finding.get('observedArtifactSha256', artifact_hash)
        if not isinstance(observed_hash, str) or not HEX.fullmatch(observed_hash):
            errors.append(f'{label}: observedArtifactSha256 must identify the failing build')
            observed_hash = ''
        check_files(finding.get('evidence'), base, observed_hash, label, errors)
        if severity in ('BLOCKER', 'MAJOR') and status == 'OPEN':
            errors.append(f'{label}: unresolved {severity}')
        if status == 'FIXED':
            check_files(finding.get('retestEvidence'), base, artifact_hash, label + '.retest', errors)
        if status == 'REJECTED':
            if not filled(finding.get('rationale')):
                errors.append(f'{label}: rejected finding needs supported rationale')
            check_files(finding.get('resolutionEvidence'), base, artifact_hash, label + '.resolution', errors)
    human = data.get('humanExperience')
    if not isinstance(human, dict):
        human = {}
    if human.get('status') == 'UNTESTED':
        if not filled(human.get('limitation')):
            errors.append('untested human experience needs an explicit limitation')
    elif human.get('status') == 'OBSERVED':
        reports = human.get('participantReports')
        if not isinstance(reports, list) or not reports:
            errors.append('observed human experience needs actual participant reports')
        else:
            participant_ids: set[str] = set()
            for i, report in enumerate(reports):
                if not isinstance(report, dict):
                    errors.append(f'human report[{i}]: object required')
                    continue
                pid = report.get('participantId')
                if not filled(pid) or pid in participant_ids or not filled(report.get('observation')):
                    errors.append(f'human report[{i}]: unique participant ID and observation required')
                else:
                    participant_ids.add(pid)
                if report.get('isHuman') is not True:
                    errors.append(f'human report[{i}]: actual human declaration required')
                kinds = check_files(report.get('evidence'), base, artifact_hash, f'human[{i}]', errors)
                if 'human_report' not in kinds:
                    errors.append(f'human report[{i}]: human_report evidence required')
    else:
        errors.append('humanExperience.status must be UNTESTED or OBSERVED')
    return {'status': 'FAIL' if errors else 'PASS', 'errors': errors,
            'validationScope': 'status/applicability semantics, record completeness, media signatures and evidence/hash consistency only',
            'humanExperience': human.get('status', 'UNTESTED')}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review')
    parser.add_argument('--artifact', required=True)
    args = parser.parse_args()
    try:
        path = Path(args.review).expanduser().absolute()
        digest, _ = deterministic_tree_hash(Path(args.artifact).expanduser().absolute())
        result = validate_quality(load_json(path), path.parent, digest)
    except (OSError, ValueError, TypeError) as exc:
        result = {'status': 'FAIL', 'errors': [str(exc)]}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
