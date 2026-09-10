"""Negative/positive utility fixtures. These are not rendered Godot or human playtests."""
from __future__ import annotations
import copy
import json
import sys
import tempfile
import subprocess
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from _common import deterministic_tree_hash, sha256_file
import _evidence
import compare_prototypes as comparison
import inspect_asset_set as assets
import inspect_engine_context as engine
import validate_quality_review as quality
import validate_release_evidence as release
import stamp_web_build

class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = self.base / 'game'
        self.project.mkdir()
        (self.project / 'project.godot').write_text('[application]\nconfig/name="fixture"\n')
        self.digest = deterministic_tree_hash(self.project)[0]

    def evidence(self, kind, name=None, digest=None):
        suffix = {'image': '.png', 'video': '.gif', 'audio': '.wav'}.get(kind, '.json')
        path = self.base / ((name or kind) + suffix)
        if kind == 'image':
            Image.new('RGBA', (4, 4), (32, 64, 128, 255)).save(path)
        elif kind == 'video':
            Image.new('RGB', (4, 4)).save(path, format='GIF')
        elif kind == 'audio':
            import wave
            with wave.open(str(path), 'wb') as w:
                w.setparams((1, 2, 8000, 1, 'NONE', 'NONE'))
                w.writeframes(b'\0\0')
        else:
            path.write_text('{"fixture": "UNIT TEST ONLY; no actual gameplay"}')
        result = {'kind': kind, 'path': path.name, 'sha256': sha256_file(path),
                  'artifactSha256': digest or self.digest}
        if kind == 'input_trace':
            result.update(entry='NORMAL_START', terminalObserved=True)
        return result

    def review(self, digest=None):
        digest = digest or self.digest
        dimensions = []
        for name in quality.DIMENSIONS:
            kinds = [sorted(alternatives)[0] for alternatives in quality.REQUIRED_KINDS[name]]
            dimensions.append({'id': name, 'criterionRefs': ['brief:quality-' + name], 'status': 'PASS',
                               'observation': 'Unit fixture, not game observation.',
                               'evidence': [self.evidence(k, digest=digest) for k in kinds]})
        return {'schemaVersion': 2, 'profile': 'NEAR_RELEASE_SLICE', 'artifactSha256': digest,
                'reviewer': {'kind': 'self', 'identity': 'unit-test fixture'}, 'dimensions': dimensions,
                'findings': [], 'humanExperience': {'status': 'UNTESTED', 'limitation': 'No human testing.'}}

    def validate(self, data):
        return quality.validate_quality(data, self.base, self.digest)

class QualityTests(Fixture):
    def test_complete_record_with_explicit_human_gap_passes(self):
        self.assertEqual(self.validate(self.review())['status'], 'PASS')

    def test_template_is_not_completion(self):
        data = json.loads((ROOT / 'templates/quality_review.json').read_text())
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_missing_dimension_fails(self):
        data = self.review(); data['dimensions'].pop()
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_duplicate_dimension_fails(self):
        data = self.review(); data['dimensions'].append(data['dimensions'][0])
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_unverified_dimension_fails(self):
        data = self.review(); data['dimensions'][0]['status'] = 'UNVERIFIED'
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_not_applicable_dimension_with_rationale_passes(self):
        data = self.review()
        row = next(r for r in data['dimensions'] if r['id'] == 'text_render')
        row['status'] = 'NOT_APPLICABLE'
        row['criterionRefs'] = ['brief:no-player-facing-text']
        row['observation'] = 'The delivered experience has no player-facing text.'
        row['evidence'] = []
        self.assertEqual(self.validate(data)['status'], 'PASS')

    def test_not_applicable_cannot_hide_pass_evidence(self):
        data = self.review()
        row = next(r for r in data['dimensions'] if r['id'] == 'text_render')
        row['status'] = 'NOT_APPLICABLE'
        row['observation'] = 'No player-facing text.'
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_missing_observation_fails(self):
        data = self.review(); data['dimensions'][2]['observation'] = ''
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_missing_brief_reference_fails(self):
        data = self.review(); data['dimensions'][2]['criterionRefs'] = []
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_all_visual_and_no_input_fails(self):
        data = self.review(); data['dimensions'][0]['evidence'] = [self.evidence('image')]
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_injected_state_cannot_prove_player_path(self):
        data = self.review(); data['dimensions'][0]['evidence'][0]['entry'] = 'INJECTED_STATE'
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_no_terminal_event_cannot_prove_complete_loop(self):
        data = self.review(); data['dimensions'][0]['evidence'][0]['terminalObserved'] = False
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_stale_artifact_fails(self):
        data = self.review(); data['artifactSha256'] = '0' * 64
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_stale_evidence_artifact_fails(self):
        data = self.review(); data['dimensions'][0]['evidence'][0]['artifactSha256'] = '0' * 64
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_missing_file_fails(self):
        data = self.review(); (self.base / 'image.png').unlink()
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_changed_evidence_fails(self):
        data = self.review(); (self.base / 'image.png').write_text('changed')
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_renamed_text_is_not_a_picture(self):
        data = self.review(); path = self.base / 'fake.png'; path.write_text('not an image')
        data['dimensions'][2]['evidence'] = [{'kind': 'image', 'path': path.name,
            'sha256': sha256_file(path), 'artifactSha256': self.digest}]
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_empty_evidence_fails(self):
        data = self.review(); path = self.base / 'input_trace.json'; path.write_text('')
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_remote_link_is_not_local_evidence(self):
        data = self.review(); data['dimensions'][0]['evidence'][0]['path'] = 'https://example.com/trace'
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_evidence_symlink_fails(self):
        data = self.review(); link = self.base / 'symlink.json'; link.symlink_to(self.base / 'input_trace.json')
        data['dimensions'][0]['evidence'][0]['path'] = link.name
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def finding(self, severity='MAJOR', status='OPEN'):
        return {'id': 'f1', 'dimension': 'ux', 'severity': severity, 'status': status,
                'description': 'Test fixture failure.', 'evidence': [self.evidence('input_trace')]}

    def test_major_open_fails(self):
        data = self.review(); data['findings'] = [self.finding()]
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_minor_open_remains_disclosed(self):
        data = self.review(); data['findings'] = [self.finding('MINOR')]
        self.assertEqual(self.validate(data)['status'], 'PASS')

    def test_fixed_without_retest_fails(self):
        data = self.review(); data['findings'] = [self.finding(status='FIXED')]
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_fixed_with_retest_passes(self):
        data = self.review(); f = self.finding(status='FIXED'); f['retestEvidence'] = [self.evidence('input_trace')]
        data['findings'] = [f]
        self.assertEqual(self.validate(data)['status'], 'PASS')

    def test_old_failure_trace_with_current_retest_preserved(self):
        data = self.review(); f = self.finding(status='FIXED')
        f['observedArtifactSha256'] = 'f' * 64
        f['evidence'] = [self.evidence('input_trace', 'old_failure', 'f' * 64)]
        f['retestEvidence'] = [self.evidence('input_trace', 'final_retest')]
        data['findings'] = [f]
        self.assertEqual(self.validate(data)['status'], 'PASS')

    def test_rejected_without_rationale_or_proof_fails(self):
        data = self.review(); data['findings'] = [self.finding(status='REJECTED')]
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_independence_claim_requires_provenance(self):
        data = self.review(); data['reviewer']['kind'] = 'independent'
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_agent_cannot_be_unmarked_human(self):
        data = self.review(); data['reviewer']['kind'] = 'human'
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_human_observed_requires_reports(self):
        data = self.review(); data['humanExperience'] = {'status': 'OBSERVED'}
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_human_observation_fixture_needs_separate_report(self):
        data = self.review(); data['humanExperience'] = {'status': 'OBSERVED', 'participantReports': [
            {'participantId': 'test-pseudonym', 'observation': 'Fixture only.', 'isHuman': True,
             'evidence': [self.evidence('human_report')]}]}
        self.assertEqual(self.validate(data)['status'], 'PASS')

    def test_untested_human_limit_cannot_be_hidden(self):
        data = self.review(); data['humanExperience']['limitation'] = ''
        self.assertEqual(self.validate(data)['status'], 'FAIL')

    def test_malformed_inputs_fail_without_crash(self):
        for data in (None, [], 'text', 1, {'dimensions': [None, {'id': []}]}):
            with self.subTest(data=data):
                self.assertEqual(self.validate(data)['status'], 'FAIL')

class AssetTests(Fixture):
    def manifest(self, size=(16, 16), alpha=0):
        image = Image.new('RGBA', size, (64, 32, 96, alpha))
        image.putpixel((1, 1), (255, 255, 255, 255)); image.save(self.project / 'a.png')
        return {'schemaVersion': 1, 'assets': [{'id': 'a', 'path': 'a.png', 'kind': 'sprite',
                 'expectedSize': list(size), 'requireTransparency': True, 'pivot': [8, 12]}]}

    def check(self, data, sheet=None):
        return assets.inspect_assets(data, self.project, sheet)

    def test_valid_image_and_contact_sheet(self):
        result = self.check(self.manifest(), self.base / 'sheet.png')
        self.assertEqual(result['status'], 'PASS')
        self.assertTrue((self.base / 'sheet.png').is_file())

    def test_existing_sheet_not_overwritten(self):
        sheet = self.base / 'sheet.png'; sheet.write_bytes(b'preserve')
        self.assertEqual(self.check(self.manifest(), sheet)['status'], 'FAIL')
        self.assertEqual(sheet.read_bytes(), b'preserve')

    def test_input_asset_not_overwritten_by_sheet(self):
        data = self.manifest(); before = (self.project / 'a.png').read_bytes()
        self.assertEqual(self.check(data, self.project / 'a.png')['status'], 'FAIL')
        self.assertEqual((self.project / 'a.png').read_bytes(), before)

    def test_dimension_mismatch(self):
        data = self.manifest(); data['assets'][0]['expectedSize'] = [17, 16]
        self.assertEqual(self.check(data)['status'], 'FAIL')

    def test_opaque_required_transparency_fails(self):
        self.assertEqual(self.check(self.manifest(alpha=255))['status'], 'FAIL')

    def test_baked_checkerboard_fails_required_transparency(self):
        # manifest() writes a baseline image; create it before the target fixture.
        data = self.manifest(size=(64, 64))
        image = Image.new('RGBA', (64, 64), (255, 255, 255, 255))
        pixels = image.load()
        for y in range(64):
            for x in range(64):
                pixels[x, y] = (255, 255, 255, 255) if ((x // 8) + (y // 8)) % 2 == 0 else (192, 192, 192, 255)
        image.save(self.project / 'a.png')
        result = self.check(data)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('checkerboard' in error for error in result['errors']))

    def test_chroma_key_is_not_default_transparency(self):
        data = self.manifest(alpha=255)
        data['assets'][0]['chromaKey'] = [0, 255, 0]
        result = self.check(data)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('fallback' in error or 'transparency' in error for error in result['errors']))

    def test_invisible_asset_fails(self):
        data = self.manifest(); Image.new('RGBA', (16, 16), (0, 0, 0, 0)).save(self.project / 'a.png')
        self.assertEqual(self.check(data)['status'], 'FAIL')

    def test_out_of_canvas_pivot_fails(self):
        data = self.manifest(); data['assets'][0]['pivot'] = [900, 2]
        self.assertEqual(self.check(data)['status'], 'FAIL')

    def test_nan_pivot_fails(self):
        data = self.manifest(); data['assets'][0]['pivot'] = [float('nan'), 2]
        self.assertEqual(self.check(data)['status'], 'FAIL')

    def test_inconsistent_frame_pivots_fail(self):
        data = self.manifest(); a = data['assets'][0]; a.update(kind='frame', group='walk')
        b = copy.deepcopy(a); b.update(id='b', pivot=[9, 12]); data['assets'].append(b)
        self.assertEqual(self.check(data)['status'], 'FAIL')

    def test_inconsistent_frame_canvas_fails(self):
        data = self.manifest(); data['assets'][0].update(kind='frame', group='walk')
        Image.new('RGBA', (32, 16), (1, 2, 3, 255)).save(self.project / 'b.png')
        data['assets'].append({'id': 'b', 'path': 'b.png', 'kind': 'frame', 'group': 'walk', 'pivot': [8, 12]})
        self.assertEqual(self.check(data)['status'], 'FAIL')

    def test_parent_escape_rejected(self):
        data = self.manifest(); data['assets'][0]['path'] = '../a.png'
        self.assertEqual(self.check(data)['status'], 'FAIL')

    def test_absolute_path_rejected(self):
        data = self.manifest(); data['assets'][0]['path'] = str(self.project / 'a.png')
        self.assertEqual(self.check(data)['status'], 'FAIL')

    def test_symlink_rejected(self):
        data = self.manifest(); (self.project / 'b.png').symlink_to(self.project / 'a.png')
        data['assets'][0]['path'] = 'b.png'
        self.assertEqual(self.check(data)['status'], 'FAIL')

    def test_corrupt_image_rejected(self):
        data = self.manifest(); (self.project / 'a.png').write_text('corrupt')
        self.assertEqual(self.check(data)['status'], 'FAIL')

    def test_duplicate_ids_fail(self):
        data = self.manifest(); data['assets'].append(data['assets'][0])
        self.assertEqual(self.check(data)['status'], 'FAIL')

    def test_dangling_contact_sheet_symlink_rejected(self):
        data = self.manifest(); sheet = self.base / 'sheet.png'
        target = self.base / 'outside.png'; sheet.symlink_to(target)
        self.assertEqual(self.check(data, sheet)['status'], 'FAIL')
        self.assertFalse(target.exists())

    def test_oversized_batch_is_bounded(self):
        data = self.manifest(); data['assets'] *= 513
        self.assertEqual(self.check(data)['status'], 'FAIL')

    def test_malformed_assets_fail(self):
        for data in (None, [], {'schemaVersion': 1, 'assets': [None, {'id': []}]}):
            with self.subTest(data=data):
                self.assertEqual(self.check(data)['status'], 'FAIL')

class ComparisonTests(Fixture):
    def data(self):
        variants = []
        for name, score in [('A', 12), ('B', 8)]:
            variants.append({'id': name, 'change': 'timing', 'isolation': 'resource override', 'rollback': 'remove override',
                'run': {'identity': name, 'artifactSha256': self.digest, 'baselineIdentity': 'base', 'scenario': 'test',
                        'conditions': 'fixture', 'evidence': [self.evidence('measurement', name)],
                        'measurements': {'mistakes': score}}, 'humanObservations': []})
        return {'schemaVersion': '1.0', 'id': 'test', 'question': 'Which avoids observable mistakes?',
            'changedDimension': 'timing', 'baseline': {'identity': 'base', 'scenario': 'test', 'conditions': 'fixture'},
            'invariants': ['same rule and scenario'], 'metrics': [{'name': 'mistakes', 'objective': 'MINIMIZE',
            'unit': 'count', 'meaning': 'test fixture count'}], 'variants': variants,
            'selection': {'status': 'AGENT_SELECTED_WITHIN_BRIEF', 'selectedVariant': 'B',
                          'rationale': 'Fewer observed mistakes in this fixture.', 'authorityReference': 'brief: delegated tuning'}}

    def check(self, data):
        return comparison.compare(data, self.base)

    def test_delegated_selection_and_dominance(self):
        result = self.check(self.data()); self.assertTrue(result['valid'])
        self.assertEqual(result['machineDominatedVariants'], ['A'])

    def test_no_metrics_means_no_automatic_ranking(self):
        data = self.data(); data['metrics'] = []
        self.assertEqual(self.check(data)['machineDominatedVariants'], [])

    def test_missing_measurement_does_not_rank(self):
        data = self.data(); data['variants'][1]['run']['measurements'] = {}
        self.assertEqual(self.check(data)['machineDominatedVariants'], [])

    def test_nonfinite_and_boolean_values_fail(self):
        for value in (float('nan'), float('inf'), True, '8', 10 ** 500):
            data = self.data(); data['variants'][0]['run']['measurements']['mistakes'] = value
            with self.subTest(value=str(value)[:30]):
                self.assertFalse(self.check(data)['valid'])

    def test_different_scenario_fails(self):
        data = self.data(); data['variants'][1]['run']['scenario'] = 'other'
        self.assertFalse(self.check(data)['valid'])

    def test_different_conditions_fail(self):
        data = self.data(); data['variants'][1]['run']['conditions'] = 'other GPU'
        self.assertFalse(self.check(data)['valid'])

    def test_missing_evidence_fails(self):
        data = self.data(); (self.base / 'A.json').unlink()
        self.assertFalse(self.check(data)['valid'])

    def test_agent_selection_requires_authority(self):
        data = self.data(); del data['selection']['authorityReference']
        self.assertFalse(self.check(data)['valid'])

    def test_human_selection_requires_human_decision(self):
        data = self.data(); data['selection']['status'] = 'HUMAN_SELECTED'
        self.assertFalse(self.check(data)['valid'])

    def test_malformed_comparison_no_crash(self):
        for data in (None, [], {'variants': [None, {'id': []}], 'baseline': []}, self.data() | {'metrics': [None]}):
            with self.subTest(data=str(data)[:40]):
                self.assertFalse(self.check(data)['valid'])

class EngineTests(Fixture):
    def scene(self):
        path = self.project / 'test.tscn'
        path.write_text('''[gd_scene load_steps=3 format=3]
[ext_resource type="Script" path="res://main.gd" id="1_ab"]
[ext_resource type="PackedScene" path="res://enemy.tscn" id="2"]
[node type="Node2D" name="Main"]
script = ExtResource("1_ab")
[node name="Enemy" parent="." instance=ExtResource("2")]
[node name="InheritedChild" parent="Enemy"]
[connection signal="hit" from="Enemy" to="." method="_on_hit"]
''')
        return path

    def test_instanced_and_inherited_nodes_are_not_lost(self):
        result = engine.parse_scene(self.scene(), self.project)
        self.assertEqual(len(result['nodes']), 3)
        self.assertIsNone(result['nodes'][1]['type'])
        self.assertEqual(result['nodes'][1]['instance'], 'ExtResource("2")')

    def test_external_script_reference_is_parsed(self):
        result = engine.parse_scene(self.scene(), self.project)
        self.assertEqual(result['scriptRefs'], ['res://main.gd'])

    def test_connections_are_declared_not_runtime_proven(self):
        result = engine.parse_scene(self.scene(), self.project)
        self.assertEqual(result['signalConnections'][0]['method'], '_on_hit')
        self.assertEqual(engine.inspect(self.project)['observations'], [])

    def test_cache_and_evidence_scenes_excluded(self):
        self.scene()
        for name in ('.godot', '.prototype', '.git'):
            (self.project / name).mkdir(); (self.project / name / 'ignored.tscn').write_text('[node name="No"]')
        self.assertEqual(len(engine.inspect(self.project)['scenes']), 1)

    def test_input_whitespace_is_supported(self):
        self.assertEqual(engine.parse_input_actions('[input]\njump = {\n}\nmove_left={\n}'), ['jump', 'move_left'])

class LinkedReleaseTests(Fixture):
    def make_web(self):
        web = self.base / 'web'
        web.mkdir(exist_ok=True)
        (web / 'index.html').write_text(
            '<!doctype html><html><body><canvas id="canvas"></canvas>'
            '<script>const cfg={"canvasResizePolicy":1};</script></body></html>', encoding='utf-8')
        (web / 'game.wasm').write_bytes(b'\0asmfixture')
        (web / 'game.pck').write_bytes(b'pck-fixture')
        (web / 'game.js').write_text('console.log("fixture")', encoding='utf-8')
        stamp_web_build.stamp(web)
        digest = deterministic_tree_hash(web)[0]
        build_id = (web / 'BUILD_ID.txt').read_text(encoding='utf-8').strip()
        return web, digest, build_id

    def data(self):
        web, web_digest, build_id = self.make_web()
        review = self.review(web_digest)
        path = self.base / 'quality.json'
        path.write_text(json.dumps(review))
        preflight = self.base / 'preflight.json'
        preflight.write_text(json.dumps({
            'schemaVersion': 1, 'profile': 'NEAR_RELEASE', 'status': 'PASS',
            'exportSha256': web_digest, 'buildId': build_id,
            'url': 'https://192.168.1.50:8443/', 'errors': [],
            'requirements': {'audio': True, 'glyphs': True, 'crossOriginIsolation': False, 'projectPresetChecked': True, 'canvasBudget': True, 'displayFit': True, 'customTemplateExplicitlyAllowed': False}
        }))
        evidence = self.evidence('runtime_log', digest=web_digest)
        capture = self.evidence('image', 'browser_capture', web_digest)
        checks = []
        for name in ['web_preflight', 'interaction', 'presentation', 'text_render', 'audio']:
            checks.append({'name': name, 'status': 'PASS', 'executed': True,
                           'artifactSha256': web_digest, 'evidence': [evidence]})
        return web, {'schemaVersion': 3, 'artifactSha256': web_digest, 'target': 'WEB_EXPORT',
            'testedArtifact': str(web),
            'pairedArtifacts': [{'kind': 'SOURCE_PROJECT', 'path': str(self.project), 'sha256': self.digest}],
            'requiredChecks': ['web_preflight', 'interaction', 'presentation', 'text_render', 'audio'],
            'checks': checks, 'completedLoop': True, 'errors': [],
            'environment': {'kind': 'unit fixture'}, 'limitations': [],
            'reviewer': {'kind': 'self', 'identity': 'fixture'},
            'captures': [{'path': capture['path'], 'sha256': capture['sha256']}],
            'qualityProfile': 'NEAR_RELEASE_SLICE', 'shareMode': 'LAN_SHARE', 'buildId': build_id,
            'webAudioExpected': True, 'threadSupport': False,
            'webPreflight': {'path': preflight.name, 'sha256': sha256_file(preflight)},
            'qualityReview': {'path': path.name, 'sha256': sha256_file(path)}}

    def check(self, data_tuple):
        web, data = data_tuple
        return release.validate_evidence(web, data, self.base)

    def test_linked_quality_record_passes(self):
        self.assertEqual(self.check(self.data())['status'], 'PASS')

    def test_missing_link_fails(self):
        web, data = self.data(); del data['qualityReview']
        self.assertEqual(self.check((web, data))['status'], 'FAIL')

    def test_tampered_quality_file_fails(self):
        web, data = self.data(); (self.base / 'quality.json').write_text('{}')
        self.assertEqual(self.check((web, data))['status'], 'FAIL')

    def test_rehashed_but_incomplete_quality_fails(self):
        web, data = self.data(); path = self.base / 'quality.json'; path.write_text('{}')
        data['qualityReview']['sha256'] = sha256_file(path)
        self.assertEqual(self.check((web, data))['status'], 'FAIL')

    def test_unknown_profile_fails(self):
        web, data = self.data(); data['qualityProfile'] = 'PERFECT_GAME'
        self.assertEqual(self.check((web, data))['status'], 'FAIL')

    def test_required_profile_cannot_be_omitted(self):
        web, data = self.data(); del data['qualityProfile']; del data['qualityReview']
        result = release.validate_evidence(web, data, self.base, required_profile='NEAR_RELEASE_SLICE')
        self.assertEqual(result['status'], 'FAIL')

    def test_required_profile_matches_complete_review(self):
        web, data = self.data()
        result = release.validate_evidence(web, data, self.base, required_profile='NEAR_RELEASE_SLICE')
        self.assertEqual(result['status'], 'PASS')

    def test_near_release_can_use_local_web_test(self):
        web, data = self.data(); data['shareMode'] = 'LOCAL_WEB_TEST'
        self.assertEqual(release.validate_evidence(web, data, self.base)['status'], 'PASS')

    def test_explicit_required_lan_share_still_rejects_local_mode(self):
        web, data = self.data(); data['shareMode'] = 'LOCAL_WEB_TEST'
        result = release.validate_evidence(web, data, self.base, required_share_mode='LAN_SHARE')
        self.assertEqual(result['status'], 'FAIL')

    def test_near_release_requires_paired_source_identity(self):
        web, data = self.data(); data['pairedArtifacts'] = []
        self.assertEqual(release.validate_evidence(web, data, self.base)['status'], 'FAIL')

    def test_near_release_rejects_source_identity_mixed_with_generated_web(self):
        web, data = self.data()
        generated = self.project / 'export' / 'web'
        generated.mkdir(parents=True)
        (generated / 'index.html').write_text('<canvas></canvas>')
        data['pairedArtifacts'][0]['sha256'] = deterministic_tree_hash(self.project)[0]
        result = release.validate_evidence(web, data, self.base)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('export/web' in error for error in result['errors']))


    def test_near_release_requires_audio_expectation_declaration(self):
        web, data = self.data(); del data['webAudioExpected']
        self.assertEqual(release.validate_evidence(web, data, self.base)['status'], 'FAIL')

    def test_expected_audio_must_be_enforced_by_preflight(self):
        web, data = self.data()
        path = self.base / 'preflight.json'; obj = json.loads(path.read_text()); obj['requirements']['audio'] = False
        path.write_text(json.dumps(obj)); data['webPreflight']['sha256'] = sha256_file(path)
        self.assertEqual(release.validate_evidence(web, data, self.base)['status'], 'FAIL')

    def test_expected_audio_requires_audio_hard_check(self):
        web, data = self.data()
        data['requiredChecks'].remove('audio')
        data['checks'] = [row for row in data['checks'] if row['name'] != 'audio']
        result = release.validate_evidence(web, data, self.base)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('hard gates' in error for error in result['errors']))

    def test_near_release_requires_canvas_budget_preflight(self):
        web, data = self.data()
        path = self.base / 'preflight.json'; obj = json.loads(path.read_text()); obj['requirements']['canvasBudget'] = False
        path.write_text(json.dumps(obj)); data['webPreflight']['sha256'] = sha256_file(path)
        result = release.validate_evidence(web, data, self.base)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('canvas' in error.lower() for error in result['errors']))

    def test_near_release_requires_glyph_preflight(self):
        web, data = self.data()
        path = self.base / 'preflight.json'; obj = json.loads(path.read_text()); obj['requirements']['glyphs'] = False
        path.write_text(json.dumps(obj)); data['webPreflight']['sha256'] = sha256_file(path)
        self.assertEqual(release.validate_evidence(web, data, self.base)['status'], 'FAIL')

    def test_threaded_release_requires_isolation_preflight(self):
        web, data = self.data(); data['threadSupport'] = True
        self.assertEqual(release.validate_evidence(web, data, self.base)['status'], 'FAIL')

    def test_near_release_web_fields_do_not_belong_on_native_artifact(self):
        _, data = self.data(); data['target'] = 'LOCAL_PROJECT'; data['testedArtifact'] = str(self.project)
        data['artifactSha256'] = self.digest
        self.assertEqual(release.validate_evidence(self.project, data, self.base)['status'], 'FAIL')

    def test_near_release_can_bind_native_project_without_web(self):
        review = self.review(self.digest)
        path = self.base / 'native-quality.json'
        path.write_text(json.dumps(review))
        evidence = self.evidence('runtime_log')
        capture = self.evidence('image', 'native_capture')
        data = {'schemaVersion': 3, 'artifactSha256': self.digest, 'target': 'LOCAL_PROJECT',
            'testedArtifact': str(self.project),
            'pairedArtifacts': [],
            'requiredChecks': ['interaction', 'presentation'],
            'checks': [
                {'name': 'interaction', 'status': 'PASS', 'executed': True,
                 'artifactSha256': self.digest, 'evidence': [evidence]},
                {'name': 'presentation', 'status': 'PASS', 'executed': True,
                 'artifactSha256': self.digest, 'evidence': [evidence]},
            ],
            'completedLoop': True, 'errors': [],
            'environment': {'kind': 'unit fixture'}, 'limitations': [],
            'reviewer': {'kind': 'self', 'identity': 'fixture'},
            'captures': [{'path': capture['path'], 'sha256': capture['sha256']}],
            'qualityProfile': 'NEAR_RELEASE_SLICE',
            'qualityReview': {'path': path.name, 'sha256': sha256_file(path)}}
        self.assertEqual(release.validate_evidence(self.project, data, self.base)['status'], 'PASS')

    def test_near_release_requires_display_fit_preflight(self):
        web, data = self.data()
        path = self.base / 'preflight.json'; obj = json.loads(path.read_text()); obj['requirements']['displayFit'] = False
        path.write_text(json.dumps(obj)); data['webPreflight']['sha256'] = sha256_file(path)
        result = release.validate_evidence(web, data, self.base)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('display' in error.lower() or 'clickability' in error.lower() for error in result['errors']))

    def test_custom_exclusions_cannot_hide_near_release_code(self):
        web, data = self.data()
        self.assertEqual(release.validate_evidence(web, data, self.base, ['scripts'])['status'], 'FAIL')

class CliTests(Fixture):
    def run_cli(self, script, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts' / script), *map(str, args)],
                              cwd=self.base, text=True, capture_output=True, timeout=10)

    def test_quality_cli_accepts_complete_fixture(self):
        path = self.base / 'review.json'; path.write_text(json.dumps(self.review()))
        result = self.run_cli('validate_quality_review.py', path, '--artifact', self.project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'PASS')

    def test_quality_cli_rejects_non_json_file(self):
        path = self.base / 'review.json'; path.write_text('broken')
        self.assertNotEqual(self.run_cli('validate_quality_review.py', path, '--artifact', self.project).returncode, 0)

    def test_engine_cli_preserves_previous_runtime_record(self):
        previous = self.project / '.prototype/spec/engine_context.json'; previous.parent.mkdir(parents=True)
        previous.write_text('{"observations": ["previous runtime evidence"]}')
        before = previous.read_bytes()
        result = self.run_cli('inspect_engine_context.py', self.project, '--write')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(previous.read_bytes(), before)
        self.assertTrue((previous.parent / 'engine_static_context.json').is_file())

    def test_asset_cli_rejects_unfilled_template(self):
        result = self.run_cli('inspect_asset_set.py', ROOT / 'templates/asset_set.json', '--root', self.project)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['status'], 'FAIL')

    def test_release_cli_required_profile_is_enforced(self):
        path = self.base / 'release.json'; path.write_text('{}')
        result = self.run_cli('validate_release_evidence.py', self.project, '--evidence', path,
                              '--required-profile', 'NEAR_RELEASE_SLICE')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('qualityProfile', result.stdout)

if __name__ == '__main__':
    unittest.main()
