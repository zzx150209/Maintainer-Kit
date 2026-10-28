import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from maintainer_kit.cli import main, scan


class Checks(unittest.TestCase):
    def test_empty_and_nonempty_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(scan(d)["present"], 0)
            p = Path(d) / "README.md"
            p.touch()
            self.assertEqual(scan(d)["present"], 0)
            p.write_text("Hello")
            self.assertEqual(scan(d)["present"], 1)

    def test_external_symlink_not_counted(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "private"
            target.write_text("secret")
            (Path(d) / "LICENSE").symlink_to(target)
            self.assertEqual(scan(d)["present"], 0)

    def test_config_is_not_issue_template(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / ".github/ISSUE_TEMPLATE"
            folder.mkdir(parents=True)
            (folder / "config.yml").write_text("blank_issues_enabled: false")
            self.assertEqual(scan(d)["present"], 0)
            (folder / "bug.yml").write_text("name: Bug")
            self.assertEqual(scan(d)["present"], 1)

    def test_json_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([d, "--format", "json", "--fail-on-missing"]), 1)
            self.assertEqual(json.loads(output.getvalue())["schema_version"], 1)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main([str(Path(d) / "absent")]), 2)


if __name__ == "__main__":
    unittest.main()
