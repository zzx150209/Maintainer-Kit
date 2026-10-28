# Maintainer Kit

[中文说明](README.zh-CN.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

**An offline repository onboarding checklist that existing projects can adopt gradually.**

Find missing metadata, see the evidence behind every result, and fail CI only when something regresses. No API key, network requests or runtime dependencies. Scanned repository code is never executed.

Status: **0.2.0, early release**. A presence check does not establish document quality, legal compliance, security or funding eligibility. No external adoption is claimed.

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

GitHub organization defaults, nested templates and automatic language detection are not supported. Supply explicit custom paths when needed. Existing YAML/Markdown contents are not validated. A symlink into the repository can count; links outside it cannot. This is not a sandbox for concurrently modified or hostile filesystems.

By default reports contain the absolute local directory. Use `--portable` to replace that field with `.`. Evidence still names repository-relative files; review filenames before publishing. See [JSON format](docs/report-format.md).

## GitHub Actions

After checking out your repository:

```yaml
- uses: actions/checkout@v4
- uses: zzx150209/Maintainer-Kit@main
  with:
    fail-on-missing: 'true'
```

For gradual adoption, commit a portable JSON baseline first:

```yaml
- uses: zzx150209/Maintainer-Kit@main
  with:
    baseline: .github/maintainer-baseline.json
```

For production, pin external actions to a reviewed commit SHA. This composite action sets up Python 3.12, prints a portable Markdown report, and adds it to the job summary. It has no need for a GitHub token and does not comment on issues or change repository files. [Inputs and integration details](docs/github-action.md).

## Development

```sh
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
python3 -m pip wheel --no-deps . --wheel-dir dist
```

CI covers supported Python versions on Linux and a Python 3.12 smoke suite on macOS and Windows. Check the Actions page for actual results; configured jobs alone do not establish support.

## Project direction

The near-term goal is to make onboarding gaps visible without noisy all-or-nothing checks. Next work includes organization-level defaults, nested templates and richer document validation. See [roadmap](docs/roadmap.md), [changelog](CHANGELOG.md) and [contribution guide](CONTRIBUTING.md).

MIT licensed. Built with assistance from Codex; changes remain subject to maintainer review and automated tests.
