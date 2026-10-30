"""Shared defaults are explicit, offline and scoped to community metadata."""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from maintainer_kit.cli import main, markdown, scan


class Defaults(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repository'
        self.shared = Path(self.tmp.name) / 'shared'
        self.root.mkdir()
        self.shared.mkdir()

    def write(self, root, path, text='Example document'):
        p = root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
        return p

    def check_for(self, report, ident):
        return next(c for c in report['checks'] if c['id'] == ident)

    def test_opt_in_only(self):
        self.write(self.shared, 'CONTRIBUTING.md')
        self.assertEqual(scan(self.root)['present'], 0)
        report = scan(self.root, defaults_directory=self.shared)
        self.assertEqual(report['present'], 1)
        self.assertEqual(self.check_for(report, 'contributing')['source'], 'defaults')
        self.assertIn('Evidence (defaults): CONTRIBUTING.md', markdown(report))

    def test_local_evidence_precedes_defaults(self):
        self.write(self.shared, 'CONTRIBUTING.md')
        self.write(self.root, 'docs/CONTRIBUTING.md')
        c = self.check_for(scan(self.root, defaults_directory=self.shared), 'contributing')
        self.assertEqual((c['source'], c['evidence']), ('repository', ['docs/CONTRIBUTING.md']))

    def test_custom_local_evidence_precedes_defaults(self):
        self.write(self.shared, 'CONTRIBUTING.md')
        self.write(self.root, '参与贡献.md')
        c = self.check_for(scan(self.root, extra_paths={'contributing': ['参与贡献.md']}, defaults_directory=self.shared), 'contributing')
        self.assertEqual(c['source'], 'repository')

    def test_readme_license_and_ci_are_not_inherited(self):
        for filename in ('README.md', 'LICENSE', '.gitlab-ci.yml'):
            self.write(self.shared, filename)
        self.assertEqual(scan(self.root, defaults_directory=self.shared)['present'], 0)

    def test_ignored_checks_stay_skipped(self):
        self.write(self.shared, 'SECURITY.md')
        c = self.check_for(scan(self.root, ignored=['security'], defaults_directory=self.shared), 'security')
        self.assertEqual((c['status'], c['source']), ('skipped', None))

    def test_portable_hides_both_roots(self):
        self.write(self.shared, 'SECURITY.md')
        text = json.dumps(scan(self.root, defaults_directory=self.shared, portable=True))
        self.assertNotIn(str(Path(self.tmp.name)), text)
        self.assertIn('@defaults', text)

    def test_external_symlinks_excluded(self):
        outside = self.write(Path(self.tmp.name), 'outside.md')
        (self.shared / 'SECURITY.md').symlink_to(outside)
        self.assertEqual(scan(self.root, defaults_directory=self.shared)['present'], 0)

    def test_shared_configuration_is_not_executed_or_applied(self):
        self.write(self.shared, '.maintainer-kit.json', '{"ignore": ["security"]}')
        c = self.check_for(scan(self.root, defaults_directory=self.shared), 'security')
        self.assertEqual(c['status'], 'missing')

    def test_missing_directory_reports_error(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = main([str(self.root), '--defaults-directory', str(self.shared / 'absent')])
        self.assertEqual(code, 2)

    def test_same_root_is_allowed_without_recursion(self):
        self.write(self.root, 'SECURITY.md')
        c = self.check_for(scan(self.root, defaults_directory=self.root), 'security')
        self.assertEqual(c['source'], 'repository')

    def test_removal_of_shared_file_is_baseline_regression(self):
        doc = self.write(self.shared, 'SECURITY.md')
        baseline = self.write(self.root, 'baseline.json', json.dumps(scan(self.root, defaults_directory=self.shared)))
        doc.unlink()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main([str(self.root), '--defaults-directory', str(self.shared), '--baseline', str(baseline), '--format', 'json'])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out.getvalue())['regressions'], ['security'])

    def test_action_passes_explicit_defaults(self):
        self.write(self.shared, 'SECURITY.md')
        script = Path(__file__).resolve().parents[1] / 'scripts/run_action.py'
        env = dict(os.environ, INPUT_REPOSITORY_PATH=str(self.root), INPUT_DEFAULTS_DIRECTORY=str(self.shared), INPUT_FAIL_ON_MISSING='false', INPUT_BASELINE='', INPUT_IGNORE='', GITHUB_STEP_SUMMARY='')
        result = subprocess.run([sys.executable, str(script)], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Evidence (defaults): SECURITY.md', result.stdout)

    def test_shared_root_template_layout(self):
        self.write(self.shared, 'PULL_REQUEST_TEMPLATE.md')
        self.write(self.shared, 'ISSUE_TEMPLATE/bug.yml')
        report = scan(self.root, defaults_directory=self.shared)
        self.assertEqual(self.check_for(report, 'pull_request_template')['source'], 'defaults')
        self.assertEqual(self.check_for(report, 'issue_templates')['evidence'], ['ISSUE_TEMPLATE/bug.yml'])

    def test_external_root_template_directory_excluded(self):
        outside = Path(self.tmp.name) / 'external'
        outside.mkdir()
        self.write(outside, 'bug.yml')
        (self.shared / 'ISSUE_TEMPLATE').symlink_to(outside, target_is_directory=True)
        self.assertEqual(scan(self.root, defaults_directory=self.shared)['present'], 0)
