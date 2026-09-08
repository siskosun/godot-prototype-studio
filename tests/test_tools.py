"""Utility regression tests. Fixtures and mocked engine calls are NOT Godot playtests."""
from __future__ import annotations
import ast
import contextlib
import copy
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import _common
import init_workspace
import run_godot_checks as runner
import validate_mission_brief as brief
import validate_decision_gate as gate
import validate_release_evidence as release


class TempCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def cli(self, module, *args):
        with mock.patch.object(sys, 'argv', [module.__file__, *map(str, args)]), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return module.main()


class WorkspaceTests(TempCase):
    def test_default_creates_only_brief_and_progress(self):
        self.assertEqual(self.cli(init_workspace, self.base), 0)
        files = {p.relative_to(self.base).as_posix() for p in self.base.rglob('*') if p.is_file()}
        self.assertEqual(files, {'.prototype/spec/mission_brief.md', '.prototype/progress.md'})

    def test_existing_brief_is_preserved(self):
        self.cli(init_workspace, self.base)
        path = self.base / '.prototype/spec/mission_brief.md'
        path.write_text('User-owned brief')
        self.cli(init_workspace, self.base)
        self.assertEqual(path.read_text(), 'User-owned brief')

    def test_starter_collision_writes_no_workflow_files(self):
        (self.base / 'project.godot').write_text('existing')
        with self.assertRaises(SystemExit) as raised:
            self.cli(init_workspace, self.base, '--with-starter')
        self.assertNotEqual(raised.exception.code, 0)
        self.assertFalse((self.base / '.prototype').exists())

    def test_starter_copy_is_complete(self):
        self.assertEqual(self.cli(init_workspace, self.base, '--with-starter'), 0)
        source = ROOT / 'assets/starter-2d'
        for file in source.rglob('*'):
            if file.is_file():
                self.assertEqual(file.read_bytes(), (self.base / file.relative_to(source)).read_bytes())

    def test_legacy_full_is_explicit(self):
        self.cli(init_workspace, self.base, '--legacy-full')
        self.assertTrue((self.base / '.prototype/spec/prototype_contract.md').exists())
        self.assertTrue((self.base / '.prototype/logs/experiments.jsonl').exists())


class GateTests(TempCase):
    def data(self):
        return json.loads((ROOT / 'templates/decision_gate.json').read_text())

    def check(self, data):
        file = self.base / 'gate.json'
        file.write_text(json.dumps(data))
        return self.cli(gate, file)

    def test_existing_open_gate_still_valid(self):
        self.assertEqual(self.check(self.data()), 0)

    def test_superseded_gate_records_delegation(self):
        data = self.data()
        data.update(status='SUPERSEDED', authorityReference='brief: delegated art direction', supersededAt='2026-09-07')
        self.assertEqual(self.check(data), 0)

    def test_supersession_without_authority_fails(self):
        data = self.data()
        data.update(status='SUPERSEDED', supersededAt='2026-09-07')
        self.assertNotEqual(self.check(data), 0)

    def test_resolved_without_human_decision_fails(self):
        data = self.data()
        data.update(status='RESOLVED', resolvedAt='2026-09-07')
        self.assertNotEqual(self.check(data), 0)


class BriefTests(unittest.TestCase):
    def valid(self):
        content = {name: 'A concrete declared requirement.' for name in brief.REQUIRED}
        content['Completion'] = 'DONE when verified. BLOCKED only by a genuine external or resource constraint.'
        return '\n'.join(f'## {name}\n{text}\n' for name, text in content.items())

    def test_valid_brief(self):
        self.assertEqual(brief.validate_text(self.valid()), [])

    def test_missing_section(self):
        self.assertTrue(brief.validate_text(self.valid().replace('## Boundaries', '## Other')))

    def test_duplicate_section(self):
        self.assertTrue(brief.validate_text(self.valid() + '\n## Outcome\nDuplicate'))

    def test_unfilled_template(self):
        self.assertTrue(brief.validate_text((ROOT / 'templates/mission_brief.md').read_text()))

    def test_inline_template_placeholder(self):
        self.assertTrue(brief.validate_text(self.valid().replace('## Delivery\nA concrete declared requirement.', '## Delivery\n- Target: [Choose target]')))

    def test_markdown_link_is_not_a_placeholder(self):
        self.assertEqual(brief.validate_text(self.valid() + '\n[Details](design.md)'), [])

    def test_missing_terminal_state(self):
        self.assertTrue(brief.validate_text(self.valid().replace('BLOCKED', 'Pending')))


class RunnerTests(TempCase):
    def command(self, code, timeout=3):
        return runner.run_command('fixture', [sys.executable, '-c', code], self.base, timeout)

    def test_clean_zero_exit(self):
        result = self.command("print('Godot Vulkan renderer startup fixture')")
        self.assertEqual(result['status'], 'PASS')
        self.assertTrue(Path(result['logPath']).is_file())

    def test_zero_exit_script_error_is_failure(self):
        result = self.command("print('SCRIPT ERROR: Invalid call', flush=True)")
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['exitCode'], 0)
        self.assertTrue(result['actionableErrorLines'])

    def test_renderer_banner_does_not_mask_runtime_failure(self):
        result = self.command("print('Vulkan fixture startup'); print('SCRIPT ERROR: Invalid call')")
        self.assertEqual(result['classification'], 'RUNTIME_FAILURE')

    def test_error_on_stderr_is_failure(self):
        self.assertEqual(self.command("import sys; print('ERROR: bad resource', file=sys.stderr)")['status'], 'FAIL')

    def test_normal_assertion_text_is_not_failure(self):
        self.assertEqual(self.command("print('All assertions passed')")['status'], 'PASS')

    def test_nonzero_exit(self):
        self.assertEqual(self.command('raise SystemExit(4)')['status'], 'FAIL')

    def test_timeout_is_not_pass(self):
        result = self.command('import time; time.sleep(1)', 0.03)
        self.assertEqual(result['classification'], 'TIMEOUT')
        self.assertEqual(result['status'], 'FAIL')

    def test_missing_executable_is_not_execution(self):
        result = runner.run_command('missing', [str(self.base / 'missing-command')], self.base, 1)
        self.assertFalse(result['executed'])
        self.assertEqual(result['classification'], 'EXECUTION_UNAVAILABLE')

    def project(self):
        (self.base / 'project.godot').write_text('[application]\nrun/main_scene="res://main.tscn"\n')
        (self.base / 'main.tscn').write_text('[gd_scene format=3]\n')

    def test_missing_test_returns_partial_not_success(self):
        self.project()
        with mock.patch.object(runner, 'find_godot', return_value='mock-godot'), mock.patch.object(runner, 'command_version', return_value=('MOCK', True, None)), mock.patch.object(runner, 'run_command', return_value={'name': 'mock', 'status': 'PASS'}):
            self.assertEqual(self.cli(runner, self.base, '--mode', 'all'), 3)
        report = json.loads((self.base / '.prototype/evidence/godot-checks/report.json').read_text())
        self.assertEqual(report['overall'], 'PARTIAL')

    def test_missing_engine_returns_unavailable(self):
        self.project()
        with mock.patch.object(runner, 'find_godot', return_value=None), mock.patch.object(runner, 'command_version', return_value=(None, False, 'not found')):
            self.assertEqual(self.cli(runner, self.base), 2)

    def test_bad_version_command_is_unavailable(self):
        self.project()
        with mock.patch.object(runner, 'find_godot', return_value='broken'), mock.patch.object(runner, 'command_version', return_value=(None, False, 'cannot execute')):
            self.assertEqual(self.cli(runner, self.base), 2)

    def test_missing_main_scene_is_failure(self):
        (self.base / 'project.godot').write_text('[application]\nrun/main_scene="res://missing.tscn"\n')
        _, errors = runner.preflight(self.base)
        self.assertTrue(errors)


class HashTests(TempCase):
    def test_excluded_records_do_not_change_game_hash(self):
        (self.base / 'game.gd').write_text('state = 1')
        first, _ = _common.deterministic_tree_hash(self.base)
        (self.base / '.prototype').mkdir()
        (self.base / '.prototype/evidence.json').write_text('record')
        self.assertEqual(first, _common.deterministic_tree_hash(self.base)[0])

    def test_changed_game_changes_hash(self):
        file = self.base / 'game.gd'
        file.write_text('state = 1')
        first, _ = _common.deterministic_tree_hash(self.base)
        file.write_text('state = 2')
        self.assertNotEqual(first, _common.deterministic_tree_hash(self.base)[0])

    def test_symlink_rejected(self):
        file = self.base / 'game.gd'
        file.write_text('state = 1')
        link = self.base / 'link.gd'
        try:
            link.symlink_to(file)
        except OSError:
            self.skipTest('symlink creation unavailable')
        with self.assertRaises(ValueError):
            _common.deterministic_tree_hash(self.base)
        with self.assertRaises(ValueError):
            _common.deterministic_tree_hash(link)


class ReleaseTests(TempCase):
    def setUp(self):
        super().setUp()
        self.project = self.base / 'tested'
        self.project.mkdir()
        (self.project / 'project.godot').write_text('[application]\nconfig/name="fixture"\n')
        (self.project / 'main.gd').write_text('extends Node\n')
        self.log = self.base / 'fixture.log'
        self.log.write_text('Unit-test fixture, NOT a real Godot run.\n')
        self.capture = self.base / 'capture-fixture.txt'
        self.capture.write_text('Unit-test capture stub, NOT a rendered frame.\n')
        digest, _ = _common.deterministic_tree_hash(self.project)
        log = {'path': str(self.log), 'sha256': _common.sha256_file(self.log)}
        self.record = {
            'schemaVersion': 3, 'artifactSha256': digest, 'target': 'LOCAL_PROJECT',
            'testedArtifact': str(self.project), 'requiredChecks': ['runtime', 'presentation'],
            'checks': [{'name': name, 'status': 'PASS', 'executed': True, 'artifactSha256': digest, 'evidence': [log]} for name in ['runtime', 'presentation']],
            'completedLoop': True, 'errors': [], 'environment': {'kind': 'unit-test fixture'},
            'reviewer': {'kind': 'self', 'identity': 'unit-test fixture'}, 'limitations': ['No actual game run'],
            'captures': [{'path': str(self.capture), 'sha256': _common.sha256_file(self.capture)}]
        }

    def validate(self, record=None, artifact=None):
        return release.validate_evidence(artifact or self.project, self.record if record is None else record, self.base)

    def test_structurally_valid_fixture(self):
        self.assertEqual(self.validate()['errors'], [])
        self.assertIn('structure', self.validate()['validationScope'])

    def test_required_failure_rejected(self):
        self.record['checks'][0]['status'] = 'FAIL'
        self.assertEqual(self.validate()['status'], 'FAIL')

    def test_required_skipped_rejected(self):
        self.record['checks'][0].update(status='SKIPPED', executed=False, reason='Unavailable')
        self.assertEqual(self.validate()['status'], 'FAIL')

    def test_pass_without_execution_rejected(self):
        self.record['checks'][0]['executed'] = False
        self.assertEqual(self.validate()['status'], 'FAIL')

    def test_missing_evidence_rejected(self):
        self.log.unlink()
        self.assertEqual(self.validate()['status'], 'FAIL')

    def test_mutated_evidence_rejected(self):
        self.log.write_text('Changed')
        self.assertEqual(self.validate()['status'], 'FAIL')

    def test_changed_artifact_rejected(self):
        (self.project / 'main.gd').write_text('changed')
        self.assertEqual(self.validate()['status'], 'FAIL')

    def test_independent_review_requires_support(self):
        self.record['reviewer']['kind'] = 'independent'
        self.assertEqual(self.validate()['status'], 'FAIL')

    def test_duplicate_check_rejected(self):
        self.record['checks'].append(copy.deepcopy(self.record['checks'][0]))
        self.assertEqual(self.validate()['status'], 'FAIL')

    def test_old_schema_rejected(self):
        self.record['schemaVersion'] = 2
        self.assertEqual(self.validate()['status'], 'FAIL')

    def test_missing_capture_rejected(self):
        self.record['captures'] = []
        self.assertEqual(self.validate()['status'], 'FAIL')

    def test_optional_skip_is_disclosed_and_allowed(self):
        self.record['checks'].append({'name': 'human', 'status': 'SKIPPED', 'executed': False, 'reason': 'Not required by brief'})
        self.assertEqual(self.validate()['errors'], [])

    def test_malformed_types_report_failure(self):
        for field, value in [('target', []), ('requiredChecks', [{}]), ('reviewer', []), ('checks', 'bad'), ('captures', None)]:
            with self.subTest(field=field):
                record = copy.deepcopy(self.record)
                record[field] = value
                self.assertEqual(self.validate(record)['status'], 'FAIL')
        self.record['checks'][0]['status'] = []
        self.assertEqual(self.validate()['status'], 'FAIL')

    def archive(self, wrapped=True):
        archive = self.base / 'game.zip'
        with zipfile.ZipFile(archive, 'w') as bundle:
            for file in self.project.rglob('*'):
                if file.is_file():
                    bundle.write(file, ('game/' if wrapped else '') + file.relative_to(self.project).as_posix())
        self.record.update(target='GODOT_PROJECT_ZIP', testedArtifact=str(archive), artifactSha256=_common.sha256_file(archive), testedTree={'path': str(self.project), 'sha256': _common.deterministic_tree_hash(self.project)[0]})
        for check in self.record['checks']:
            check['artifactSha256'] = self.record['artifactSha256']
        return archive

    def rebind_archive_hash(self, archive):
        self.record['artifactSha256'] = _common.sha256_file(archive)
        for check in self.record['checks']:
            check['artifactSha256'] = self.record['artifactSha256']

    def test_valid_zip_and_wrapped_zip(self):
        for wrapped in [True, False]:
            with self.subTest(wrapped=wrapped):
                archive = self.archive(wrapped)
                self.assertEqual(self.validate(artifact=archive)['errors'], [])

    def test_unrelated_tested_tree_rejected_even_after_rehash(self):
        archive = self.archive()
        (self.project / 'main.gd').write_text('different code')
        self.record['testedTree']['sha256'] = _common.deterministic_tree_hash(self.project)[0]
        result = self.validate(artifact=archive)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('contents differ' in error for error in result['errors']))

    def test_archive_path_traversal_rejected(self):
        archive = self.archive()
        with zipfile.ZipFile(archive, 'a') as bundle:
            bundle.writestr('../outside.txt', 'unsafe')
        self.rebind_archive_hash(archive)
        self.assertEqual(self.validate(artifact=archive)['status'], 'FAIL')

    def test_invalid_archive_rejected(self):
        archive = self.archive()
        archive.write_text('Not a ZIP')
        self.rebind_archive_hash(archive)
        self.assertEqual(self.validate(artifact=archive)['status'], 'FAIL')

    def test_archive_symlink_rejected(self):
        archive = self.archive()
        with zipfile.ZipFile(archive, 'a') as bundle:
            info = zipfile.ZipInfo('game/link')
            info.create_system = 3
            info.external_attr = 0o120777 << 16
            bundle.writestr(info, '/outside')
        self.rebind_archive_hash(archive)
        self.assertEqual(self.validate(artifact=archive)['status'], 'FAIL')

    def test_source_zip_with_generated_web_export_is_rejected(self):
        generated = self.project / 'export' / 'web'
        generated.mkdir(parents=True)
        (generated / 'index.html').write_text('<canvas></canvas>')
        (generated / 'game.wasm').write_bytes(b'\0asm')
        (generated / 'game.pck').write_bytes(b'pck')
        (generated / 'game.js').write_text('loader')
        archive = self.archive()
        result = self.validate(artifact=archive)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('export/web' in error for error in result['errors']))



class PackageTests(unittest.TestCase):
    def test_scripts_parse(self):
        for file in SCRIPTS.glob('*.py'):
            with self.subTest(file=file.name):
                ast.parse(file.read_text(), filename=str(file))

    def test_json_templates_parse(self):
        for file in (ROOT / 'templates').glob('*.json'):
            with self.subTest(file=file.name):
                self.assertIsInstance(json.loads(file.read_text()), dict)

    def test_local_markdown_links_resolve(self):
        for file in ROOT.rglob('*.md'):
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', file.read_text()):
                link = link.split('#', 1)[0]
                if not link or '://' in link or link.startswith('mailto:'):
                    continue
                with self.subTest(file=str(file.relative_to(ROOT)), link=link):
                    self.assertTrue((file.parent / link).exists())

    def test_root_is_compact_router(self):
        text = (ROOT / 'SKILL.md').read_text()
        self.assertTrue(text.startswith('---\nname: godot-prototype-studio\n'))
        self.assertLess(len(text.split()), 1200)
        description = re.search(r'^description: (.+)$', text, re.MULTILINE).group(1)
        self.assertLess(len(description.split()), 45)
        self.assertIn('**DONE**', text)
        self.assertIn('**BLOCKED**', text)


if __name__ == '__main__':
    unittest.main()
