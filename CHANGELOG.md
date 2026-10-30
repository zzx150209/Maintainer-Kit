# Changelog

## 0.3.0

- Add explicit offline shared community-file defaults via `--defaults-directory` and the Action input of the same name.
- Prefer repository-local metadata and label shared evidence with its source.
- Support root community templates in local organization `.github` checkouts.
- Keep README, license and CI evidence scoped to the scanned repository.
- Preserve version-1 baseline compatibility and document source-transition behavior.
- Add tests covering fallback precedence, ignored checks, missing directories, symlink boundaries, portable paths and baseline regressions.

## 0.2.0

- Add JSON configuration for optional checks and custom metadata paths.
- Add baseline regression gates for gradual adoption.
- Add portable output that omits the absolute repository root.
- Recognize GitLab CI metadata and support `python -m maintainer_kit`.
- Add a reusable composite GitHub Action, Chinese documentation and runnable examples.
- Validate malformed baselines, unknown checks and configuration path escapes.
- Expand temporary-repository integration coverage.

## 0.1.0 (local prototype)

- Initial offline file-presence checks, JSON/Markdown output and optional strict gate.
