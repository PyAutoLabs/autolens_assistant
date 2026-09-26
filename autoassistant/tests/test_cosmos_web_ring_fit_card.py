"""Tests for the `cosmos-web-ring-fit` one-shot card and its reference-fit script.

The card scores an agent's `result.json` against the recorded reference fits
(`benchmarks/truth/cosmos-web-ring-fit/truth.json`, built from
`scripts/cosmos_web_ring/results/`). These tests pin the mapping: the good
reference numbers score 100, the poor reference numbers score partially, and a
run that skipped the preparation the prompt asks for fails a gate.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from autoassistant import benchmark

REPO_ROOT = Path(__file__).resolve().parents[2]
CARD_ID = "cosmos-web-ring-fit"
TRUTH = json.loads(
    (REPO_ROOT / "benchmarks" / "truth" / CARD_ID / "truth.json").read_text()
)


def _card():
    return benchmark.load_oneshot_cards(REPO_ROOT)[CARD_ID]


def _scorer():
    return benchmark.load_card_scorer(_card())


FIGURE = "scripts/scratch/cosmos_web_ring/fit_subplot.png"


def _workdir(tmp_path):
    """A stand-in session checkout holding the one figure the result lists."""
    workdir = tmp_path / "workdir"
    (workdir / FIGURE).parent.mkdir(parents=True, exist_ok=True)
    (workdir / FIGURE).write_bytes(b"\x89PNG\r\n\x1a\n")
    return workdir


def _ctx(tmp_path, result, workdir=None, compute_seconds=300.0):
    run_dir = tmp_path / "run"
    run_dir.mkdir(exist_ok=True)
    return benchmark.RunContext(
        run_dir=run_dir,
        workdir=workdir,
        result=result,
        truth_dir=benchmark.benchmarks_dir(REPO_ROOT) / "truth",
        card=_card(),
        meta={
            "model": "m",
            "harness": "h",
            "date": "2026-09-26",
            "run": {"compute_seconds": compute_seconds},
        },
        transcript=benchmark.Transcript(final_text="done."),
        root=REPO_ROOT,
    )


def _result(**overrides):
    result = {
        "einstein_radius": TRUTH["einstein_radius"],
        "reduced_chi_squared": TRUTH["reduced_chi_squared_good"],
        "n_masked_pixels": TRUTH["n_masked_pixels"],
        "noise_scaling_applied": True,
        "mask_radius": 1.8,
        "search": "MultiStartProdigy",
        "figures": [FIGURE],
        "summary": "The MGE model reproduces the ring. Residuals are near the noise.",
    }
    result.update(overrides)
    return result


def _computed(tmp_path, result, workdir="default", compute_seconds=300.0):
    if workdir == "default":
        workdir = _workdir(tmp_path)
    card_score = _scorer().score(
        _ctx(tmp_path, result, workdir=workdir, compute_seconds=compute_seconds)
    )
    gates = {g.name: g.passed for g in card_score.gates}
    metrics = {m.name: m.value for m in card_score.metrics}
    return gates, metrics, benchmark.computed_score(card_score.gates, card_score.metrics)


def test_card_is_frozen_and_listed_in_the_lock():
    card = _card()
    assert card.meta["prompt_sha256"] == benchmark.prompt_sha256(card.prompt)
    assert benchmark.freeze_findings(REPO_ROOT) == []
    assert card.meta["datasets"] == ["dataset/imaging/cosmos_web_ring"]


def test_truth_is_consistent_with_the_reference_fits():
    results = REPO_ROOT / "scripts" / "cosmos_web_ring" / "results"
    good = json.loads((results / "good" / "summary.json").read_text())
    assert TRUTH["einstein_radius"] == pytest.approx(good["einstein_radius"], abs=1e-4)
    assert TRUTH["reduced_chi_squared_good"] == pytest.approx(good["reduced_chi_squared"], abs=1e-4)
    assert TRUTH["n_masked_pixels"] == good["n_masked_pixels"]
    assert TRUTH["mask_radius"] == 1.8
    assert TRUTH["einstein_radius_tol"] >= 0.03
    assert TRUTH["reduced_chi_squared_poor"] > TRUTH["reduced_chi_squared_good"]


def test_good_reference_numbers_score_100(tmp_path):
    result = _result()
    assert _scorer().validate_result(result) == []
    gates, metrics, score = _computed(tmp_path, result)
    assert all(gates.values())
    assert metrics == {
        "einstein_radius_within_tol": 1.0,
        "fit_quality": 1.0,
        "figures_exist": 1.0,
        "summary_length": 1.0,
    }
    assert score == 100.0


def test_poor_reference_numbers_score_partially(tmp_path):
    result = _result(
        einstein_radius=TRUTH["einstein_radius"] + 3.0 * TRUTH["einstein_radius_tol"],
        reduced_chi_squared=TRUTH["reduced_chi_squared_poor"],
    )
    gates, metrics, score = _computed(tmp_path, result)
    assert all(gates.values())
    assert metrics["fit_quality"] == 0.5
    assert metrics["einstein_radius_within_tol"] == pytest.approx(0.0, abs=1e-9)
    assert 0.0 < score < 100.0

    # Twice the tolerance off is half-credit on the Einstein radius.
    halfway = _result(einstein_radius=TRUTH["einstein_radius"] - 2.0 * TRUTH["einstein_radius_tol"])
    assert _computed(tmp_path, halfway)[1]["einstein_radius_within_tol"] == pytest.approx(0.5)

    # Worse than the poor reference fit earns nothing for fit quality.
    worse = _result(reduced_chi_squared=2.0 * TRUTH["reduced_chi_squared_poor"])
    assert _computed(tmp_path, worse)[1]["fit_quality"] == 0.0


def test_copying_the_reference_results_earns_nothing(tmp_path):
    """The reference fit ships in the checkout: its figures do not count, and a
    session that never ran a fit fails the `fit_was_run` gate."""
    reference = _result(figures=["scripts/cosmos_web_ring/results/good/fit_subplot.png"])
    gates, metrics, _score = _computed(tmp_path, reference, workdir=REPO_ROOT)
    assert metrics["figures_exist"] == 0.0

    gates, _metrics, score = _computed(tmp_path, _result(), compute_seconds=2.0)
    assert gates["fit_was_run"] is False
    assert score == 0.0


def test_skipping_the_preparation_fails_a_gate(tmp_path):
    for result, gate in (
        (_result(noise_scaling_applied=False), "noise_scaling_applied"),
        (_result(mask_radius=3.0), "mask_radius"),
    ):
        gates, _metrics, score = _computed(tmp_path, result)
        assert gates[gate] is False
        assert score == 0.0


def test_schema_rejects_wrong_types():
    scorer = _scorer()
    assert scorer.validate_result({}) == [
        "'einstein_radius' must be a finite number",
        "'reduced_chi_squared' must be a finite number",
        "'mask_radius' must be a finite number",
        "'n_masked_pixels' must be an integer",
        "'noise_scaling_applied' must be a boolean",
        "'search' must be a non-empty string",
        "'figures' must be a non-empty list",
        "'summary' must be a non-empty string",
    ]
    assert scorer.validate_result(_result(noise_scaling_applied="yes")) == [
        "'noise_scaling_applied' must be a boolean"
    ]


def test_copes_with_no_result(tmp_path):
    card_score = _scorer().score(_ctx(tmp_path, None))
    assert [m.value for m in card_score.metrics] == [0.0, 0.0, 0.0, 0.0]
    assert not all(g.passed for g in card_score.gates)


def test_rescore_without_workdir_is_byte_stable(tmp_path):
    """`score-oneshot` runs after the workdir is gone; the sidecar keeps figures_exist."""
    result = _result(figures=[FIGURE, "scripts/scratch/cosmos_web_ring/missing.png"])
    workdir = _workdir(tmp_path)

    def readings(workdir):
        card_score = _scorer().score(_ctx(tmp_path, result, workdir=workdir))
        return [(m.name, m.value, m.detail) for m in card_score.metrics]

    first = readings(workdir)
    assert dict((n, v) for n, v, _ in first)["figures_exist"] == 0.5
    assert readings(None) == first
    assert all(str(tmp_path) not in detail for _n, _v, detail in first)


@pytest.mark.skipif(
    not os.environ.get("AUTOASSISTANT_RUN_FIT_SMOKE"),
    reason="runs a JAX lens fit (minutes); set AUTOASSISTANT_RUN_FIT_SMOKE=1",
)
def test_fit_script_test_mode_smoke(tmp_path):
    script = REPO_ROOT / "scripts" / "cosmos_web_ring" / "fit_cosmos_web_ring.py"
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--test-mode",
            "--results-dir",
            str(tmp_path / "results"),
            "--output-dir",
            str(tmp_path / "output"),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    summary = json.loads((tmp_path / "results" / "summary.json").read_text())
    assert summary["test_mode"] is True
    assert summary["n_masked_pixels"] == TRUTH["n_masked_pixels"]
    assert summary["mask_radius"] == 1.8
    assert summary["noise_scaling_applied"] is True
    for name in ("fit_subplot.png", "source.png", "tracer.png"):
        assert (tmp_path / "results" / name).is_file()
