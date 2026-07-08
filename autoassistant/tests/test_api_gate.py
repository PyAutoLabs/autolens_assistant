# pyauto-api-gate: skip — this file contains intentional stale-symbol fixtures.
"""Regression tests for the pre-execution PyAuto* API gate.

These pin the two failures that motivated the gate — `al.FitImagingPlotter` and
`from autoarray.structures.arrays.kernel_2d import Kernel2D`, both run from memory via
`python3 -c "..."` against a stack where the symbols had been renamed/removed — plus the
current-correct call (`aplt.subplot_fit_imaging`) that must NOT be flagged.

Two layers are covered: the validator modes (`audit_skill_apis.py --code/--file`) and the
PreToolUse hook (`.claude/hooks/validate_pyauto_code.py`). Both shell out using
`sys.executable`, so the tests resolve symbols against the same interpreter/stack pytest
runs under (source `activate.sh` first). Each case imports autolens, so the file is slow
by design — it is a guard, not a unit-speed test.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "autoassistant" / "audit_skill_apis.py"
HOOK = ROOT / ".claude" / "hooks" / "validate_pyauto_code.py"

GOOD = "import autolens.plot as aplt; aplt.subplot_fit_imaging(fit=fit)"
GOOD_SUBMODULE = "import autofit.jax.pytrees as pytrees"
GOOD_AUTOCONF_SUBMODULE = "import autoconf.dictable"
STALE_PLOTTER = "import autolens as al; al.FitImagingPlotter(fit=fit).subplot_fit()"
STALE_KERNEL = "from autoarray.structures.arrays.kernel_2d import Kernel2D"

# Defunct *idiom* (every named symbol still resolves): the removed analysis-summing
# combine. The factor-graph form below must NOT be flagged.
IDIOM_SUM_OPERATOR = (
    "a = al.AnalysisImaging(dataset=d) + al.AnalysisInterferometer(dataset=d2)"
)
IDIOM_SUM_BUILTIN = "total = sum(analysis_list)"
GOOD_FACTOR_GRAPH = (
    "import autofit as af\n"
    "factors = [af.AnalysisFactor(prior_model=m, analysis=a) for a in analysis_list]\n"
    "fg = af.FactorGraphModel(*factors)"
)

# Keep numba/matplotlib caches writable in sandboxed/CI runs (see CLAUDE.md).
ENV = {
    **os.environ,
    "NUMBA_CACHE_DIR": "/tmp/numba_cache",
    "MPLCONFIGDIR": "/tmp/matplotlib",
    "PYAUTO_SKIP_WORKSPACE_VERSION_CHECK": "1",
}


def _run_validator(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        capture_output=True, text=True, env=ENV, timeout=180,
    )


def _run_hook(command: str, *, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    payload = json.dumps(
        {"tool_name": "Bash", "cwd": str(ROOT), "hook_event_name": "PreToolUse",
         "tool_input": {"command": command}}
    )
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload, capture_output=True, text=True,
        env={**ENV, **(env_extra or {})}, timeout=180,
    )


def _decision(proc: subprocess.CompletedProcess) -> str | None:
    """Return the hook's permissionDecision, or None for a silent allow."""
    out = proc.stdout.strip()
    if not out:
        return None
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"]


# --- validator (--code / --file) -------------------------------------------------------
def test_validator_passes_current_api():
    assert _run_validator("--code", GOOD).returncode == 0


def test_validator_passes_current_submodule_import():
    assert _run_validator("--code", GOOD_SUBMODULE).returncode == 0


def test_validator_passes_autoconf_submodule_import():
    assert _run_validator("--code", GOOD_AUTOCONF_SUBMODULE).returncode == 0


def test_validator_flags_stale_plotter():
    proc = _run_validator("--code", STALE_PLOTTER)
    assert proc.returncode == 2
    assert "FitImagingPlotter" in proc.stderr


def test_validator_flags_stale_kernel_module():
    proc = _run_validator("--code", STALE_KERNEL)
    assert proc.returncode == 2
    assert "kernel_2d" in proc.stderr


def test_validator_file_mode(tmp_path):
    script = tmp_path / "stale.py"
    script.write_text(f"import autolens as al\n{STALE_PLOTTER}\n", encoding="utf-8")
    assert _run_validator("--file", str(script)).returncode == 2
    assert _run_validator("--file", str(tmp_path / "missing.py")).returncode == 2


# --- hook ------------------------------------------------------------------------------
def test_hook_denies_stale_snippet():
    proc = _run_hook(f"{sys.executable} -c '{STALE_PLOTTER}'")
    assert _decision(proc) == "deny"
    assert "FitImagingPlotter" in proc.stdout


def test_hook_denies_stale_kernel():
    proc = _run_hook(f'{sys.executable} -c "{STALE_KERNEL}"')
    assert _decision(proc) == "deny"


def test_hook_allows_current_api():
    assert _decision(_run_hook(f"{sys.executable} -c '{GOOD}'")) is None


def test_hook_allows_non_pyauto_python():
    assert _decision(_run_hook(f"{sys.executable} -c 'import numpy as np; np.zeros(3)'")) is None


def test_hook_allows_non_python_command_without_import():
    # Pre-screen must short-circuit (no autolens import) — assert both allow and speed.
    proc = _run_hook("ls -la /tmp")
    assert _decision(proc) is None


def test_hook_allows_non_python_command_that_mentions_py_file(tmp_path):
    script = tmp_path / "mentions_stale_api.py"
    script.write_text(f"import autolens as al\n{STALE_PLOTTER}\n", encoding="utf-8")

    proc = _run_hook(f"echo {script}")

    assert _decision(proc) is None


def test_hook_allows_grep_of_pyauto_file(tmp_path):
    script = tmp_path / "grep_target.py"
    script.write_text(
        "import autofit.jax.pytrees as pytrees\n"
        f"import autolens as al\n{STALE_PLOTTER}\n",
        encoding="utf-8",
    )

    proc = _run_hook(f"grep -n autofit.jax {script}")

    assert _decision(proc) is None


def test_hook_allows_non_python_count_option_with_pyauto_pattern(tmp_path):
    script = tmp_path / "grep_count_target.py"
    script.write_text("aa.AbstractPreloads\n", encoding="utf-8")

    proc = _run_hook(f"grep -c aa.AbstractPreloads {script}")

    assert _decision(proc) is None


def test_hook_escape_hatch():
    proc = _run_hook(f"{sys.executable} -c '{STALE_PLOTTER}'", env_extra={"PYAUTO_SKIP_API_GATE": "1"})
    assert _decision(proc) is None


def test_hook_escape_hatch_command_prefix():
    # The documented per-command form: the env var is a prefix on the command itself,
    # so it never reaches the hook's own environment — the hook must detect it in the
    # command text.
    proc = _run_hook(f"PYAUTO_SKIP_API_GATE=1 {sys.executable} -c '{STALE_PLOTTER}'")
    assert _decision(proc) is None


def test_hook_validates_py_file_argument(tmp_path):
    good = tmp_path / "good.py"
    good.write_text(f"import autolens.plot as aplt\n{GOOD}\n", encoding="utf-8")
    assert _decision(_run_hook(f"{sys.executable} {good}")) is None

    bad = tmp_path / "bad.py"
    bad.write_text(f"import autolens as al\n{STALE_PLOTTER}\n", encoding="utf-8")
    assert _decision(_run_hook(f"{sys.executable} {bad}")) == "deny"


# --- idiom deny-list (validator --code / --lint-idioms) --------------------------------
def test_validator_flags_summing_operator_idiom():
    proc = _run_validator("--code", IDIOM_SUM_OPERATOR)
    assert proc.returncode == 2
    assert "analysis-summing-operator" in proc.stderr
    assert "AnalysisFactor" in proc.stderr  # the replacement is surfaced


def test_validator_flags_sum_builtin_idiom():
    proc = _run_validator("--code", IDIOM_SUM_BUILTIN)
    assert proc.returncode == 2
    assert "analysis-summing-sum-builtin" in proc.stderr


def test_validator_passes_factor_graph_api():
    # Every symbol resolves AND no idiom — the current combine pattern must be clean.
    assert _run_validator("--code", GOOD_FACTOR_GRAPH).returncode == 0


def test_hook_denies_summing_idiom():
    proc = _run_hook(f'{sys.executable} -c "{IDIOM_SUM_OPERATOR}"')
    assert _decision(proc) == "deny"
    assert "analysis-summing-operator" in proc.stdout


def test_lint_idioms_flags_planted_doc(tmp_path):
    # Acceptance: the audit over the docs flags a planted summing idiom. Build a minimal
    # tree (sources.yaml marks the root) with one wiki page carrying the dead idiom.
    (tmp_path / "sources.yaml").write_text("projects: []\n", encoding="utf-8")
    page = tmp_path / "wiki" / "core" / "concepts" / "planted.md"
    page.parent.mkdir(parents=True)
    page.write_text(
        "# Planted\n\n```python\nanalysis = analysis_g + analysis_r\n```\n",
        encoding="utf-8",
    )
    proc = _run_validator("--lint-idioms", "--root", str(tmp_path))
    assert proc.returncode == 1
    assert "planted.md" in proc.stderr
    assert "analysis-summing-operator" in proc.stderr


def test_lint_idioms_clean_tree(tmp_path):
    (tmp_path / "sources.yaml").write_text("projects: []\n", encoding="utf-8")
    page = tmp_path / "wiki" / "core" / "concepts" / "clean.md"
    page.parent.mkdir(parents=True)
    page.write_text(
        "# Clean\n\n```python\nfg = af.FactorGraphModel(*analysis_factor_list)\n```\n",
        encoding="utf-8",
    )
    assert _run_validator("--lint-idioms", "--root", str(tmp_path)).returncode == 0


# --- broken-stack handling (import failure is an env problem, not symbol drift) --------
def _load_validator_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("audit_skill_apis_under_test", VALIDATOR)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses resolve fields via sys.modules
    spec.loader.exec_module(mod)
    return mod


def test_validate_source_reports_broken_stack_once_not_stale():
    mod = _load_validator_module()
    wall = "WorkspaceVersionMismatchError('pinned != installed" + " x" * 200 + "')"
    mod._module_cache["autolens"] = None
    mod._import_errors["autolens"] = wall

    n_stale, lines, import_failed = mod.validate_source("al.Tracer; al.Galaxy; al.FitImaging")

    assert n_stale == 0 and lines == []  # broken stack is never "stale symbols"
    assert list(import_failed) == ["autolens"]  # reported once, not per symbol
    assert len(import_failed["autolens"]) <= 201  # truncated, not the full wall


def test_render_installation_check_groups_identical_errors():
    mod = _load_validator_module()
    check = mod.InstallationCheck(
        status="import_failed", python="py", prefix="env",
        versions={}, locations={}, missing=[],
        errors={name: "Boom: identical wall" for name in ("autofit", "autogalaxy", "autolens")},
        install_kind="unknown", cache_defaults={},
    )

    text = mod.render_installation_check(check)

    assert text.count("Boom: identical wall") == 1
    assert "autofit, autogalaxy, autolens import failed" in text


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
