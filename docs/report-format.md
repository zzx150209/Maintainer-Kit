# Report format

`--format json` emits one object with `schema_version: 1`.

- `repository`: absolute scanned directory, or `.` with `--portable`.
- `present`: number of checks with `status: present`.
- `total`: number of enabled checks; skipped checks are excluded.
- `skipped`: number of disabled checks.
- `checks`: one entry for each stable check ID, in tool-defined order.
- `limitation`: human-readable scope statement.
- `regressions`: sorted newly missing check IDs; included only with `--baseline`.

Each check has `id`, `status` (`present`, `missing`, `skipped`), `evidence` (a sorted list of repository-relative paths), and `suggestion`. Evidence shows a matching nonempty file, not a validation of its contents. Internal symlinks report their resolved file path.

To create a baseline, run a normal JSON scan and save its output. A baseline must contain exactly one entry for each known check ID with valid statuses. Other report fields do not affect baseline comparison. Old version-1 reports without `skipped` counts remain accepted when their check entries are complete.

Do not overwrite the baseline automatically on every CI run: review changes deliberately. Skipping a check exempts it from the gate, so configuration changes should receive the same review as code changes.

## Shared defaults in 0.3.0

With `--defaults-directory`, the report includes `defaults_directory` (an absolute path, or `@defaults` with `--portable`). Each check also includes `source`: `repository`, `defaults`, or `null` when missing/skipped. Evidence paths are relative to the root named by `source`; they never include an absolute path. Without this option, these additive fields are omitted, preserving existing output shape. The schema version remains 1 and old baselines remain accepted.

Baseline comparison uses check status, not source or evidence path. Local-to-shared transitions remain satisfied. Removal of the last matching source causes a regression if the check previously passed. Configuration changes and defaults checkouts should be reviewed together with the baseline.
