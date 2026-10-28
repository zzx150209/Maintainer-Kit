import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ADAPTER = Path(__file__).resolve().parents[1] / "scripts/run_action.py"


class ActionIntegration(unittest.TestCase):
    def test_report_summary_and_gate_status(self):
        with tempfile.TemporaryDirectory() as d:
            summary = Path(d) / "summary.md"
            env = dict(os.environ, INPUT_REPOSITORY_PATH=d, INPUT_FAIL_ON_MISSING="true", INPUT_BASELINE="", INPUT_IGNORE="", GITHUB_STEP_SUMMARY=str(summary))
            result = subprocess.run([sys.executable, str(ADAPTER)], cwd=d, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(summary.read_text(), result.stdout)
            self.assertIn("0 of 8", result.stdout)
            self.assertNotIn(d, result.stdout)

    def test_shell_like_input_is_not_executed(self):
        with tempfile.TemporaryDirectory() as d:
            env = dict(os.environ, INPUT_REPOSITORY_PATH=d, INPUT_FAIL_ON_MISSING="false", INPUT_BASELINE="", INPUT_IGNORE="readme; touch SHOULD_NOT_EXIST", GITHUB_STEP_SUMMARY="")
            result = subprocess.run([sys.executable, str(ADAPTER)], cwd=d, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse((Path(d) / "SHOULD_NOT_EXIST").exists())

    def test_invalid_strict_and_conflicting_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            for strict, baseline in (("yes", ""), ("true", "baseline.json")):
                env = dict(os.environ, INPUT_REPOSITORY_PATH=d, INPUT_FAIL_ON_MISSING=strict, INPUT_BASELINE=baseline, INPUT_IGNORE="", GITHUB_STEP_SUMMARY="")
                result = subprocess.run([sys.executable, str(ADAPTER)], cwd=d, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
