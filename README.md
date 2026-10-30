# Maintainer Kit

[中文说明](README.zh-CN.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

**An offline repository onboarding checklist that existing projects can adopt gradually.**

Find missing metadata, see the evidence behind every result, and fail CI only when something regresses. No API key, network requests or runtime dependencies. Scanned repository code is never executed.

Status: **0.3.0, early release**. A presence check does not establish document quality, legal compliance, security or funding eligibility. No external adoption is claimed.

## See it in 30 seconds

The same sample repository, with and without a local shared-community checkout:

```text
$ maintainer-kit examples/minimal --portable
Found 1 of 8 enabled metadata items (0 skipped).
[x] readme                 Evidence: README.md
[ ] contributing           Missing contribution guide
[ ] security               Missing security instructions

$ maintainer-kit examples/minimal --defaults-directory examples/shared-community --portable
Found 3 of 8 enabled metadata items (0 skipped).
[x] readme                 Evidence: README.md
[x] contributing           Evidence (defaults): CONTRIBUTING.md
[x] security               Evidence (defaults): SECURITY.md
```

Excerpt from real output, with other checks omitted and formatting shortened. [Run the complete demo](docs/demo.md). Both directories are synthetic fixtures, not external adoption examples.

## Add it to GitHub in one file

Copy the [complete reporting workflow](examples/workflows/maintainer-kit.yml) to `.github/workflows/maintainer-kit.yml` in your repository, commit it, then open the Actions job summary. By default missing metadata is reported without blocking your existing workflow.

For gradual enforcement, [create a baseline](docs/quickstart-actions.md) and use the [complete regression workflow](examples/workflows/maintainer-kit-baseline.yml). Both examples pin Maintainer Kit to the reviewed v0.3.0 commit.

## Try it

Python 3.10 or newer:

```sh
git clone https://github.com/zzx150209/Maintainer-Kit.git
cd Maintainer-Kit
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/maintainer-kit examples/minimal --portable
```

On Windows use `.venv\Scripts\python -m pip install .` and `.venv\Scripts\maintainer-kit`.

Without installation, from a checkout:

```sh
PYTHONPATH=src python3 -m maintainer_kit examples/minimal --portable
```

The distribution is named `maintainer-kit-local`; the command is `maintainer-kit`. It has not been published on PyPI. Install from this repository or a locally built wheel.

## Why use it?

- **Gradual adoption:** save a baseline and block newly missing items while working through existing gaps.
- **Evidence:** every result names the file that satisfied the check.
- **Different conventions:** configure translated filenames, custom CI files and optional checks.
- **Local operation:** no accounts, credentials, telemetry or repository uploads.
- **Portable reports:** omit the absolute repository path before sharing reports.

## Everyday commands

```sh
maintainer-kit /path/to/repo --portable
maintainer-kit /path/to/repo --portable --format json > baseline.json
maintainer-kit /path/to/repo --baseline baseline.json
maintainer-kit /path/to/repo --ignore conduct --ignore security
maintainer-kit /path/to/repo --fail-on-missing
```

The normal scan exits successfully even when items are missing. `--fail-on-missing` and `--baseline` are mutually exclusive. Exit codes: **0** completed/passed gate; **1** missing items or baseline regressions; **2** invalid input or scan error. A baseline compares stable check IDs; evidence path changes are not regressions while a check remains satisfied. Newly enabled checks that were skipped in the baseline count as regressions if missing.

## Shared community files (0.3.0)

If your organization keeps shared community files in a separate checkout:

```sh
maintainer-kit /path/to/repo --defaults-directory /path/to/shared-checkout --portable
```

Repository-local evidence (including custom paths) takes precedence. Missing contribution, security, conduct, pull-request and issue-template checks can use shared files. README, license and CI checks always refer to the scanned repository. Shared files may use the same built-in layout or root `PULL_REQUEST_TEMPLATE.md` / `ISSUE_TEMPLATE/` in a `.github` repository checkout. Shared configuration files are not loaded.

Reports identify the source explicitly. Portable output labels the shared root `@defaults`, hiding its absolute path. Check out shared files yourself: no downloads or GitHub API calls occur. This is an explicit local fallback, not a complete simulation of GitHub's inheritance rules. Empty local files do not satisfy a check and can fall back to shared evidence.

Use the same defaults option when creating and comparing baselines. A check switching from local to shared evidence still counts as present; losing both sources is a regression. See [report format](docs/report-format.md).

## Configuration

Create `.maintainer-kit.json` in the scanned directory:

```json
{
  "ignore": ["conduct"],
  "paths": {
    "readme": ["说明.md"],
    "ci": ["ci/pipeline.yml"]
  }
}
```

Custom paths supplement built-in paths. Paths must identify nonempty files inside the scanned directory; absolute paths, `..` and escaping symlinks are rejected. Unknown keys and check IDs are errors. Configuration is JSON data and never executes code. `--config path/to/file.json` selects a config explicitly; this path is relative to the current working directory and must remain inside the scanned directory. CLI `--ignore` adds to configured ignores.

## Checks and limits

Stable IDs: `readme`, `license`, `contributing`, `security`, `conduct`, `pull_request_template`, `issue_templates`, `ci`.

Built-in detection covers common root README/license names; root, `.github/` or `docs/` contribution/security/conduct documents; `.github/PULL_REQUEST_TEMPLATE.md` or its lowercase variant; immediate Markdown/YAML issue templates; immediate YAML GitHub workflows; and `.gitlab-ci.yml`. Issue-template `config.yml` alone does not count as a template. A zero-byte file does not count. Whitespace-only files currently do count.

Automatic fetching of GitHub organization defaults, nested templates and automatic language detection are not supported. Supply explicit custom paths when needed. Existing YAML/Markdown contents are not validated. A symlink into the repository can count; links outside it cannot. This is not a sandbox for concurrently modified or hostile filesystems.

By default reports contain the absolute local directory. Use `--portable` to replace that field with `.`. Evidence still names repository-relative files; review filenames before publishing. See [JSON format](docs/report-format.md).

## GitHub Actions

Use the complete [reporting](examples/workflows/maintainer-kit.yml) or [baseline](examples/workflows/maintainer-kit-baseline.yml) workflow. See the [step-by-step setup](docs/quickstart-actions.md) and [all inputs](docs/github-action.md).

The action sets up Python 3.12, prints a portable Markdown report and adds it to the job summary. It does not need an API key or GitHub token input. The examples grant only `contents: read`. For production, review and pin external dependencies to commit SHAs; the Maintainer Kit reference is already pinned.

## Development

```sh
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
python3 -m pip wheel --no-deps . --wheel-dir dist
```

CI covers supported Python versions on Linux and a Python 3.12 smoke suite on macOS and Windows. Check the Actions page for actual results; configured jobs alone do not establish support.

## Project direction

The near-term goal is to make onboarding gaps visible without noisy all-or-nothing checks. Next work includes nested templates and richer document validation. See [roadmap](docs/roadmap.md), [changelog](CHANGELOG.md) and [contribution guide](CONTRIBUTING.md).

MIT licensed. Built with assistance from Codex; changes remain subject to maintainer review and automated tests.
