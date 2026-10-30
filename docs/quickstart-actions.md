# Set up GitHub Actions

## 1. Start with reporting

Copy [`examples/workflows/maintainer-kit.yml`](../examples/workflows/maintainer-kit.yml) into your repository as `.github/workflows/maintainer-kit.yml` and commit it. The complete file includes triggers, runner, permissions and checkout. No secrets, API key, signup or paid API service are needed by the scan.

Open **Actions → Repository onboarding report → report → Summary**. Missing metadata is listed with suggested next steps. It does not cause a failed check in this default mode. Scan/input errors still fail. Normal GitHub Actions availability and runner limits apply.

## 2. Optionally enforce a baseline

Install the CLI locally using the README instructions. From the root of **your** repository:

```sh
mkdir -p .github
maintainer-kit . --portable --format json > .github/maintainer-baseline.json
```

Review the JSON and commit it. Replace the reporting workflow with [`examples/workflows/maintainer-kit-baseline.yml`](../examples/workflows/maintainer-kit-baseline.yml), using the same `.github/workflows/maintainer-kit.yml` destination. Avoid enabling both copies unintentionally.

Existing missing items are accepted by the baseline. If a previously satisfied check becomes missing, the job fails. Fix the regression or deliberately review and update the baseline. Do not overwrite the baseline automatically on each run.

## 3. Optional shared files

The shared checkout must already exist locally in the runner workspace. Add `defaults-directory` to the action's `with` inputs, using a path relative to the scanned directory. Check out shared files yourself and use the same files/options when generating the baseline. Maintainer Kit does not fetch them.

## What the report means

It checks nonempty file presence, not content quality, license validity or vulnerabilities. An existing workflow file satisfies the CI-presence check; that does not prove your tests are useful or passing. Skipped checks are explicit exemptions, not successful checks.

The sample workflows pin Maintainer Kit to commit `b488f22f87c16bf28891184794c8cc2cc6a34fe8` (v0.3.0). Upgrade that pin after reviewing a newer release. `actions/checkout@v4` remains a moving upstream reference; use your organization's dependency-pinning policy for it.
