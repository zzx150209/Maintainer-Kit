"""Inspect local repository metadata without network access or code execution."""
import argparse
import json
import sys
from pathlib import Path

RULES = (
    ("readme", ("README.md", "README.rst", "README.txt", "README"), "Add a README explaining purpose, installation and one runnable example."),
    ("license", ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"), "Choose a license you have authority to grant and add its full text."),
    ("contributing", ("CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md"), "Document local setup, checks and how to propose changes."),
    ("security", ("SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md"), "Document a private vulnerability reporting channel and supported versions."),
    ("conduct", ("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md", "docs/CODE_OF_CONDUCT.md"), "Document expected conduct and an actual moderation contact."),
    ("pull_request_template", (".github/PULL_REQUEST_TEMPLATE.md", ".github/pull_request_template.md"), "Add a pull request template asking for context and verification."),
)
DIRECTORY_RULES = (
    ("issue_templates", ".github/ISSUE_TEMPLATE", "Add a bug report or feature request template."),
    ("ci", ".github/workflows", "Add CI that runs the project's documented checks."),
)
CHECK_IDS = frozenset(rule[0] for rule in RULES + DIRECTORY_RULES)
DEFAULT_CHECK_IDS = frozenset({"contributing", "security", "conduct", "pull_request_template", "issue_templates"})
LIMITATION = "File presence only; content quality, security, adoption and program eligibility are not assessed."


def contained_file(root, path):
    """Do not follow metadata symlinks outside the repository."""
    try:
        return path.resolve().is_relative_to(root) and path.is_file() and path.stat().st_size > 0
    except (OSError, RuntimeError):
        return False


def evidence_path(root, path):
    resolved = path.resolve()
    # Preserve actual spelling on case-insensitive filesystems.
    for actual in resolved.parent.iterdir():
        if actual.name.casefold() == resolved.name.casefold() and actual.samefile(resolved):
            return actual.relative_to(root).as_posix()
    return resolved.relative_to(root).as_posix()


def validate_ids(values, label):
    if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
        raise ValueError(f"{label} must be a list of check IDs")
    unknown = set(values) - CHECK_IDS
    if unknown:
        raise ValueError(f"Unknown check IDs in {label}: {', '.join(sorted(unknown))}")
    return set(values)


def load_config(root, filename=None):
    """JSON only: configuration never imports or runs repository code."""
    path = Path(filename) if filename else root / ".maintainer-kit.json"
    if not filename and not path.exists():
        return set(), {}
    if not contained_file(root, path):
        raise ValueError("Configuration must be a nonempty file inside the scanned directory")
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) - {"ignore", "paths"}:
        raise ValueError("Configuration must be an object with only 'ignore' and 'paths' keys")
    ignored = validate_ids(config.get("ignore", []), "ignore")
    paths = config.get("paths", {})
    if not isinstance(paths, dict):
        raise ValueError("paths must be an object mapping check IDs to filename lists")
    validate_ids(list(paths), "paths")
    for ident, candidates in paths.items():
        if not isinstance(candidates, list) or not candidates or any(not isinstance(p, str) or not p for p in candidates):
            raise ValueError(f"paths.{ident} must be a nonempty list of filenames")
        for candidate in candidates:
            p = Path(candidate)
            if p.is_absolute() or ".." in p.parts or not (root / p).resolve().is_relative_to(root):
                raise ValueError(f"paths.{ident} must stay inside the scanned directory")
    return ignored, paths


def scan(directory, *, ignored=(), extra_paths=None, portable=False, defaults_directory=None):
    root = Path(directory).resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    defaults_root = None
    fallback = {}
    if defaults_directory is not None:
        defaults_root = Path(defaults_directory).resolve()
        if not defaults_root.is_dir():
            raise ValueError(f"Not a defaults directory: {defaults_root}")
        shared_paths = {"pull_request_template": ["PULL_REQUEST_TEMPLATE.md", "pull_request_template.md"]}
        issue_folder = defaults_root / "ISSUE_TEMPLATE"
        if issue_folder.resolve().is_relative_to(defaults_root):
            shared_paths["issue_templates"] = [p.relative_to(defaults_root).as_posix() for p in issue_folder.glob("*")
                if p.suffix.lower() in {".md", ".yml", ".yaml"} and p.name.lower() not in {"config.yml", "config.yaml"}]
        fallback = {c["id"]: c for c in scan(defaults_root, extra_paths=shared_paths)["checks"]}
    ignored = validate_ids(list(ignored), "ignore")
    extra_paths = extra_paths or {}
    checks = []
    for ident, candidates, advice in RULES + DIRECTORY_RULES:
        evidence = set()
        if ident not in ignored:
            if ident in {"issue_templates", "ci"}:
                folder = candidates
                base = root / folder
                # Avoid walking an external directory even when all its files are excluded.
                if base.resolve().is_relative_to(root):
                    for p in base.glob("*"):
                        extensions = {".yml", ".yaml"} | ({".md"} if ident == "issue_templates" else set())
                        if p.suffix.lower() in extensions and p.name.lower() not in {"config.yml", "config.yaml"} and contained_file(root, p):
                            evidence.add(evidence_path(root, p))
                candidates = (".gitlab-ci.yml",) if ident == "ci" else ()
            for candidate in tuple(candidates) + tuple(extra_paths.get(ident, ())):
                path = root / candidate
                if contained_file(root, path):
                    evidence.add(evidence_path(root, path))
        status = "skipped" if ident in ignored else "present" if evidence else "missing"
        check = dict(id=ident, status=status, evidence=sorted(evidence), suggestion=advice)
        if defaults_root is not None:
            check["source"] = "repository" if evidence else None
            if status == "missing" and ident in DEFAULT_CHECK_IDS and fallback[ident]["status"] == "present":
                check.update(status="present", evidence=fallback[ident]["evidence"], source="defaults")
        checks.append(check)
    report = dict(schema_version=1, repository="." if portable else str(root),
                present=sum(c["status"] == "present" for c in checks),
                total=sum(c["status"] != "skipped" for c in checks),
                skipped=sum(c["status"] == "skipped" for c in checks), checks=checks, limitation=LIMITATION)
    if defaults_root is not None:
        report["defaults_directory"] = "@defaults" if portable else str(defaults_root)
    return report


def load_baseline(filename):
    report = json.loads(Path(filename).read_text(encoding="utf-8"))
    if not isinstance(report, dict) or report.get("schema_version") != 1 or not isinstance(report.get("checks"), list):
        raise ValueError("Baseline must be a schema_version 1 JSON report")
    checks = report["checks"]
    if any(not isinstance(c, dict) or not isinstance(c.get("id"), str) or c.get("id") not in CHECK_IDS or not isinstance(c.get("status"), str) or c.get("status") not in {"present", "missing", "skipped"} for c in checks):
        raise ValueError("Baseline contains an invalid check")
    ids = [c["id"] for c in checks]
    if set(ids) != CHECK_IDS or len(ids) != len(CHECK_IDS):
        raise ValueError("Baseline must include each check ID exactly once")
    return {c["id"] for c in checks if c["status"] == "missing"}


def markdown(report):
    lines = ["# Repository maintenance checklist", "", f"Found {report['present']} of {report['total']} enabled metadata items ({report['skipped']} skipped).", "", report["limitation"], ""]
    if "regressions" in report:
        lines += ["New missing items: " + (", ".join(report["regressions"]) or "none"), ""]
    for check in report["checks"]:
        mark = "x" if check["status"] == "present" else "-" if check["status"] == "skipped" else " "
        lines.append(f"- [{mark}] {check['id']}")
        detail = "Skipped by configuration" if check["status"] == "skipped" else ("Evidence (defaults): " if check.get("source") == "defaults" else "Evidence: ") + ", ".join(check["evidence"]) if check["evidence"] else check["suggestion"]
        lines.append("  " + detail)
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", default=".")
    parser.add_argument("--version", action="version", version="maintainer-kit 0.3.0")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--defaults-directory", help="Local checkout of shared community files; never downloaded automatically")
    parser.add_argument("--config", help="Explicit JSON config path; must be inside the scanned directory")
    parser.add_argument("--ignore", action="append", default=[], metavar="CHECK_ID", help="Skip a check (repeatable)")
    parser.add_argument("--portable", action="store_true", help="Replace the local repository path with '.' in reports")
    gate = parser.add_mutually_exclusive_group()
    gate.add_argument("--fail-on-missing", action="store_true", help="Exit 1 if any enabled metadata item is missing")
    gate.add_argument("--baseline", help="Exit 1 only for missing items not already missing in a saved JSON report")
    args = parser.parse_args(argv)
    try:
        root = Path(args.directory).resolve()
        if not root.is_dir():
            raise ValueError(f"Not a directory: {root}")
        ignored, paths = load_config(root, args.config)
        ignored |= validate_ids(args.ignore, "--ignore")
        report = scan(root, ignored=ignored, extra_paths=paths, portable=args.portable, defaults_directory=args.defaults_directory)
        missing = {c["id"] for c in report["checks"] if c["status"] == "missing"}
        if args.baseline:
            report["regressions"] = sorted(missing - load_baseline(args.baseline))
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"maintainer-kit: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.format == "json" else markdown(report), end="\n" if args.format == "json" else "")
    return int(bool(report.get("regressions")) if args.baseline else args.fail_on_missing and bool(missing))


if __name__ == "__main__":
    sys.exit(main())
