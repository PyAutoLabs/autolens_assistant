"""The HPC pipeline template's command-line contract (likelihood lifecycle R6 phase C).

`hpc/template.py` takes `--setup <auto|cpu|gpu|setup_id>` and `--number_of_cores <auto|int>`,
both defaulting to `auto`, with `--use_cpu` kept as a deprecated alias for `--setup cpu`. This
is the same contract as the Euclid pipeline's `util.parse_fit_args`; the batch templates
depend on it.
"""
import importlib.util
import os
from pathlib import Path

import pytest

TEMPLATE = Path(__file__).resolve().parents[2] / "hpc" / "template.py"


@pytest.fixture(scope="module")
def template():
    spec = importlib.util.spec_from_file_location("hpc_template", TEMPLATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _parse(template, monkeypatch, *argv):
    monkeypatch.setattr("sys.argv", ["template.py", "--dataset=lens", *argv])
    return template.parse_fit_args()


def test_defaults_are_auto(template, monkeypatch):
    assert _parse(template, monkeypatch) == (None, "lens", 5000, "auto", "auto")


def test_setup_and_cores_are_parsed(template, monkeypatch):
    parsed = _parse(
        template, monkeypatch, "--setup=numba_cpu_sparse_fp64", "--number_of_cores=8"
    )
    assert parsed[3:] == (8, "numba_cpu_sparse_fp64")


def test_use_cpu_is_a_deprecated_alias_for_setup_cpu(template, monkeypatch, capsys):
    assert _parse(template, monkeypatch, "--use_cpu")[4] == "cpu"
    assert "--use_cpu is deprecated; use --setup cpu" in capsys.readouterr().err


@pytest.mark.parametrize(
    "argv",
    [("--setup=bogus",), ("--number_of_cores=0",), ("--use_cpu", "--setup=gpu")],
)
def test_invalid_values_are_usage_errors(template, monkeypatch, argv):
    with pytest.raises(SystemExit) as error:
        _parse(template, monkeypatch, *argv)
    assert error.value.code == 2


def test_device_intent_goes_through_pyauto_setup(template, monkeypatch):
    monkeypatch.delenv("PYAUTO_SETUP", raising=False)
    monkeypatch.setenv("JAX_PLATFORMS", "cpu")
    assert template.analysis_setup_from("cpu") == "auto"
    assert os.environ["PYAUTO_SETUP"] == "cpu"
    assert template.analysis_setup_from("auto") == "auto"
    assert template.analysis_setup_from("jax_gpu_dense_fp64") == "jax_gpu_dense_fp64"
