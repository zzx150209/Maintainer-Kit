# Security policy

## Supported versions

Only the latest 0.3.x revision is maintained at this early stage. Fixes are delivered in the repository; there is no support SLA.

## Reporting

Use GitHub's private vulnerability reporting feature if the **Report a vulnerability** button is available under this repository's Security tab:

https://github.com/zzx150209/Maintainer-Kit/security/advisories

If private reporting is unavailable, contact the maintainer through the public GitHub profile https://github.com/zzx150209 to request a private channel. Do not put exploit details, secrets or private repository contents into public issues. No private email address or response time is promised.

Include the affected revision, Python/OS versions, minimal reproduction and impact after a private channel is established.

## Boundaries

Scanning is read-only and offline. JSON configuration does not execute code. Metadata symlinks outside the scanned directory are excluded; custom path escapes are rejected. Reports can disclose directory and file names. `--portable` hides the absolute root, not evidence filenames. This tool does not audit vulnerabilities, validate document contents or defend against concurrent malicious filesystem changes.
