"""GitHub composite-action adapter: pass all user inputs as data, never shell code."""
import os
import subprocess
import sys
from pathlib import Path


def run():
    action_root = Path(__file__).resolve().parents[1]
    root = Path(os.environ.get("INPUT_REPOSITORY_PATH", ".")).resolve()
    strict = os.environ.get("INPUT_FAIL_ON_MISSING", "false").lower()
    baseline = os.environ.get("INPUT_BASELINE", "")
    if strict not in {"true", "false"}:
        print("fail-on-missing must be true or false", file=sys.stderr)
        return 2
    if strict == "true" and baseline:
        print("baseline and fail-on-missing cannot be used together", file=sys.stderr)
        return 2
    args = [sys.executable, "-m", "maintainer_kit", str(root), "--portable"]
    defaults = os.environ.get("INPUT_DEFAULTS_DIRECTORY", "")
    if defaults:
        args += ["--defaults-directory", str(root / defaults)]
    if strict == "true":
        args.append("--fail-on-missing")
    if baseline:
        args += ["--baseline", str(root / baseline)]
    for ident in filter(None, (s.strip() for s in os.environ.get("INPUT_IGNORE", "").split(","))):
        args += ["--ignore", ident]
    env = dict(os.environ, PYTHONPATH=str(action_root / "src"))
    result = subprocess.run(args, env=env, capture_output=True, text=True, encoding="utf-8")
    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary and result.stdout:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(result.stdout)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(run())
