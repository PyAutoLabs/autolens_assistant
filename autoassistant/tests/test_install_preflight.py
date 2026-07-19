"""Regression tests for the PyAuto* installation preflight."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "autoassistant" / "audit_skill_apis.py"
ENV = {
    **os.environ,
    "NUMBA_CACHE_DIR": "/tmp/numba_cache",
    "MPLCONFIGDIR": "/tmp/matplotlib",
    "PYAUTO_SKIP_WORKSPACE_VERSION_CHECK": "1",
}


def _run(*args: str, isolated: bool = False, env: dict[str, str] | None = None):
    command = [sys.executable]
    if isolated:
        command.append("-S")
    command.extend([str(VALIDATOR), *(args or ("--check-install",))])
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env or ENV,
        timeout=180,
    )


def test_install_preflight_reports_ready_environment():
    process = _run()

    assert process.returncode == 0
    assert "[install] READY" in process.stdout
    assert f"python: {sys.executable}" in process.stdout
    assert "autolens:" in process.stdout
    assert "install type:" in process.stdout


def test_install_preflight_distinguishes_absent_stack():
    process = _run(isolated=True, env={**ENV, "PYTHONPATH": ""})

    assert process.returncode == 2
    assert "[install] NOT INSTALLED" in process.stderr
    assert "missing from this interpreter" in process.stderr
    assert "al_setup_environment.md" in process.stderr


def test_install_preflight_distinguishes_broken_import(tmp_path):
    for package in ("autonerves", "autoarray", "autofit", "autogalaxy", "autolens"):
        package_path = tmp_path / package
        package_path.mkdir()
        body = (
            "raise RuntimeError('broken dependency')\n"
            if package == "autolens"
            else "__version__ = 'test'\n"
        )
        (package_path / "__init__.py").write_text(body, encoding="utf-8")

    process = _run(isolated=True, env={**ENV, "PYTHONPATH": str(tmp_path)})

    assert process.returncode == 3
    assert "[install] IMPORT FAILED" in process.stderr
    assert "autolens import failed: RuntimeError: broken dependency" in process.stderr
    assert "missing from this interpreter" not in process.stderr


def test_version_check_routes_absent_stack_to_install_preflight():
    process = _run("--check-version", isolated=True, env={**ENV, "PYTHONPATH": ""})

    assert process.returncode == 2
    assert "[install] NOT INSTALLED" in process.stderr
    assert "API DRIFT" not in process.stderr
