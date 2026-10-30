# Reproduce the demo

This demo uses the synthetic fixtures included in this repository. They are examples, not external users. Run the README installation steps first, then run these commands from the repository root.

## Repository files only

```sh
.venv/bin/maintainer-kit examples/minimal --portable
```

```text
# Repository maintenance checklist

Found 1 of 8 enabled metadata items (0 skipped).

File presence only; content quality, security, adoption and program eligibility are not assessed.

- [x] readme
  Evidence: README.md
- [ ] license
  Choose a license you have authority to grant and add its full text.
- [ ] contributing
  Document local setup, checks and how to propose changes.
- [ ] security
  Document a private vulnerability reporting channel and supported versions.
- [ ] conduct
  Document expected conduct and an actual moderation contact.
- [ ] pull_request_template
  Add a pull request template asking for context and verification.
- [ ] issue_templates
  Add a bug report or feature request template.
- [ ] ci
  Add CI that runs the project's documented checks.
```

## Add a local shared-community checkout

```sh
.venv/bin/maintainer-kit examples/minimal --defaults-directory examples/shared-community --portable
```

```text
# Repository maintenance checklist

Found 3 of 8 enabled metadata items (0 skipped).

File presence only; content quality, security, adoption and program eligibility are not assessed.

- [x] readme
  Evidence: README.md
- [ ] license
  Choose a license you have authority to grant and add its full text.
- [x] contributing
  Evidence (defaults): CONTRIBUTING.md
- [x] security
  Evidence (defaults): SECURITY.md
- [ ] conduct
  Document expected conduct and an actual moderation contact.
- [ ] pull_request_template
  Add a pull request template asking for context and verification.
- [ ] issue_templates
  Add a bug report or feature request template.
- [ ] ci
  Add CI that runs the project's documented checks.
```

The first scan finds one of eight items. The shared checkout provides two more: contribution and security documents. The second scan therefore finds three of eight, with shared evidence labeled explicitly. No files are added to the scanned repository and no remote service is contacted.

The sample SECURITY document is a fixture, not an actual security policy. Presence checks do not validate document contents. Use real reporting instructions in a real project.

Windows: replace `.venv/bin/maintainer-kit` with `.venv\Scripts\maintainer-kit`.
