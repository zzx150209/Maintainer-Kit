"""End-to-end adoption and failure cases, using isolated temporary repositories."""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from maintainer_kit.cli import main, scan, load_config


class Workflows(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, content):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main([str(self.root), *args])
        return code, out.getvalue(), err.getvalue()

    def test_portable_report_does_not_expose_local_root(self):
        code, out, _ = self.run_cli("--portable", "--format", "json")
        self.assertEqual(code, 0)
        self.assertNotIn(str(self.root), out)
        self.assertEqual(json.loads(out)["repository"], ".")

    def test_translated_readme_via_config(self):
        self.write("说明.md", "安装与使用")
        self.write(".maintainer-kit.json", json.dumps({"paths": {"readme": ["说明.md"]}, "ignore": ["conduct"]}))
        code, out, _ = self.run_cli("--format", "json")
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertEqual(report["skipped"], 1)
        self.assertEqual(report["total"], 7)
        self.assertEqual(report["checks"][0]["evidence"], ["说明.md"])

    def test_unknown_ignore_is_an_error(self):
        code, out, err = self.run_cli("--ignore", "typo")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("Unknown check IDs", err)

    def test_invalid_config_shapes(self):
        for config in ([], {"typo": []}, {"ignore": "readme"}, {"paths": []}, {"paths": {"readme": [42]}}, {"paths": {"readme": []}}):
            with self.subTest(config=config):
                self.write(".maintainer-kit.json", json.dumps(config))
                self.assertEqual(self.run_cli()[0], 2)

    def test_config_paths_cannot_escape(self):
        for candidate in ("../private", "/tmp/private"):
            self.write(".maintainer-kit.json", json.dumps({"paths": {"readme": [candidate]}}))
            self.assertEqual(self.run_cli()[0], 2)

    def test_external_config_link_is_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            p = Path(other) / "config.json"
            p.write_text('{}')
            (self.root / ".maintainer-kit.json").symlink_to(p)
            self.assertEqual(self.run_cli()[0], 2)

    def test_external_workflow_directory_not_followed(self):
        with tempfile.TemporaryDirectory() as other:
            (Path(other) / "test.yml").write_text("jobs: {}")
            (self.root / ".github").mkdir()
            (self.root / ".github/workflows").symlink_to(other, target_is_directory=True)
            self.assertEqual(scan(self.root)["present"], 0)

    def test_gitlab_ci_detected(self):
        self.write(".gitlab-ci.yml", "test: {}")
        check = next(c for c in scan(self.root)["checks"] if c["id"] == "ci")
        self.assertEqual(check["evidence"], [".gitlab-ci.yml"])

    def test_readme_evidence_has_no_duplicates(self):
        self.write(".github/PULL_REQUEST_TEMPLATE.md", "Describe the change")
        check = next(c for c in scan(self.root)["checks"] if c["id"] == "pull_request_template")
        self.assertEqual(check["evidence"], [".github/PULL_REQUEST_TEMPLATE.md"])

    def test_baseline_adoption_and_regression(self):
        readme = self.write("README.md", "Example")
        self.write("baseline.json", json.dumps(scan(self.root, portable=True)))
        code, out, _ = self.run_cli("--baseline", str(self.root / "baseline.json"), "--format", "json")
        self.assertEqual(code, 0)  # Pre-existing missing items do not block adoption.
        self.assertEqual(json.loads(out)["regressions"], [])
        readme.unlink()
        code, out, _ = self.run_cli("--baseline", str(self.root / "baseline.json"), "--format", "json")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["regressions"], ["readme"])

    def test_skipped_item_becoming_missing_is_a_regression(self):
        self.write("baseline.json", json.dumps(scan(self.root, ignored=["readme"])))
        code, out, _ = self.run_cli("--baseline", str(self.root / "baseline.json"), "--format", "json")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["regressions"], ["readme"])

    def test_malformed_baselines_are_errors(self):
        reports = [{}, {"schema_version": 1, "checks": []}, {"schema_version": 1, "checks": [{"id": [], "status": "present"}]}]
        duplicate = scan(self.root)
        duplicate["checks"].append(duplicate["checks"][0])
        reports.append(duplicate)
        for report in reports:
            with self.subTest(report=report):
                p = self.write("bad.json", json.dumps(report))
                code, out, _ = self.run_cli("--baseline", str(p))
                self.assertEqual((code, out), (2, ""))

    def test_ignore_all_has_zero_enabled_items(self):
        args = []
        for check in scan(self.root)["checks"]:
            args.extend(["--ignore", check["id"]])
        code, out, _ = self.run_cli(*args, "--fail-on-missing", "--format", "json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["total"], 0)

    def test_module_entrypoint_has_real_exit_status(self):
        result = subprocess.run([sys.executable, "-m", "maintainer_kit", str(self.root), "--fail-on-missing"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("readme", result.stdout)
        self.assertEqual(result.stderr, "")
