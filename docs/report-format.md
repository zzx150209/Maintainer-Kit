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
