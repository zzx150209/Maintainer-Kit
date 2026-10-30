# GitHub Action

The root `action.yml` defines a composite action. Use it after checkout. It uses Python 3.12 via `actions/setup-python`, runs the source included in the action, and requires no package installation or API credentials.

Inputs:

- `repository-path`: directory to inspect, default `.` relative to the job working directory.
- `fail-on-missing`: `true` or `false`, default `false`.
- `defaults-directory`: optional local shared checkout, relative to `repository-path` unless absolute. The action never downloads it.
- `baseline`: optional saved JSON report path, relative to `repository-path` unless absolute.
- `ignore`: comma-separated stable check IDs, default empty.

`baseline` and `fail-on-missing: 'true'` are mutually exclusive. Invalid inputs fail with exit 2. A gate failure exits 1. Markdown output is written to stdout and to the GitHub step summary, including on a gate failure; input errors go to stderr.

The action does not clone repositories, write reports into the checkout, post comments or use a GitHub token. Use minimal workflow permissions (`contents: read`) and review configuration/baseline changes. Pin the action and its dependencies to reviewed commit SHAs for production workflows.
