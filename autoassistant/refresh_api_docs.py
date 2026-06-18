"""Preflight helper for the `al_refresh_api_docs` maintenance skill.

This script does the mechanical part of a workspace API-refresh pass:

1. Verifies the PyAuto* stack imports cleanly.
2. Prints resolved versions for the five core packages.
3. Runs `autoassistant/audit_skill_apis.py` for the requested scope.

It does not rewrite any docs. The surrounding skill handles curation.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


MODULES = (
    ("autoconf", "autoconf"),
    ("autoarray", "autoarray"),
    ("autofit", "autofit"),
    ("autogalaxy", "autogalaxy"),
    ("autolens", "autolens"),
)


def import_versions() -> dict[str, str]:
    versions: dict[str, str] = {}

    for package_name, import_name in MODULES:
        module = __import__(import_name)
        versions[package_name] = getattr(module, "__version__", "?")

    return versions


def run_audit(scope: str) -> int:
    cmd = [sys.executable, str(ROOT / "autoassistant" / "audit_skill_apis.py"), "--scope", scope]
    print("Running:", " ".join(cmd))
    completed = subprocess.run(cmd, cwd=ROOT, check=False)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scope",
        choices=("skills", "wiki", "all"),
        default="all",
        help="Which maintenance surface to audit.",
    )
    args = parser.parse_args()

    try:
        versions = import_versions()
    except Exception as exc:  # noqa: BLE001
        print("PyAuto* import preflight failed:", repr(exc), file=sys.stderr)
        print(
            "Activate the project environment before running this helper.",
            file=sys.stderr,
        )
        return 2

    print("Resolved package versions:")
    for package_name, _ in MODULES:
        print(f"  {package_name}: {versions[package_name]}")

    audit_rc = run_audit(args.scope)

    if audit_rc == 0:
        print("Audit clean. No stale symbols found for scope:", args.scope)
    else:
        print("Audit reported drift. Read the Markdown report under autoassistant/audit/.")

    return audit_rc


if __name__ == "__main__":
    raise SystemExit(main())
