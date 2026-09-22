"""Protect the real-data selection and reject false setup-success reports."""

import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from astropy.io import fits

from autoassistant import benchmark

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "dataset/imaging/abell_1201"
CARD = benchmark.load_oneshot_card(
    ROOT / "benchmarks/prompts/oneshot/abell-1201-setup/card.md"
)
SCORER = benchmark.load_card_scorer(CARD)


def result():
    band = {
        "mask": "exact positive support of noise_map_subtracted.fits",
        "included_pixels": 31417,
        "pixel_scale_arcsec": 0.04,
        "maximum_included_radius_arcsec": 4.0,
        "psf_sum": 1.0,
        "likelihood_data": "image.fits",
        "likelihood_noise": "noise_map.fits",
        "fit_executed": False,
    }
    return {
        "stage": "setup_only",
        "model_family": "power_law_shear_point_mass",
        "preparation": {"f390w": copy.deepcopy(band), "f814w": copy.deepcopy(band)},
        "smoke": {
            "status": "coarse_inversion_smoke_passed",
            "free_parameters": 14,
            "source_mesh_shape": [12, 12],
            "figure_of_merit": 100.0,
            "seconds": 4.0,
            "posterior_search_run": False,
            "science_validated": False,
            "positions_penalty_tested": False,
        },
        "presentation_png": "scripts/scratch/abell_1201/website/abell_1201_rgb.png",
        "summary": "Setup only. The posterior and science remain unvalidated.",
    }


def context(tmp_path, payload, artifact=True):
    if artifact:
        target = tmp_path / "artifacts/abell_1201_rgb.png"
        target.parent.mkdir()
        target.write_bytes(b"\x89PNG\r\n\x1a\n")
    return SimpleNamespace(result=payload, run_dir=tmp_path, workdir=None)


def test_selected_data_match_manifest_and_approved_support():
    manifest = json.loads((DATA / "manifest.json").read_text())
    for relative, expected in manifest["files"].items():
        contents = (DATA / relative).read_bytes()
        assert len(contents) == expected["bytes"]
        assert hashlib.sha256(contents).hexdigest() == expected["sha256"]
    yy, xx = np.indices((421, 421))
    approved = (yy - 210) ** 2 + (xx - 210) ** 2 <= 100**2
    for band in ("f390w", "f814w"):
        support = fits.getdata(DATA / band / "noise_map_subtracted.fits") > 0
        assert np.array_equal(support, approved)
        assert support.sum() == 31417
        assert np.all(fits.getdata(DATA / band / "noise_map.fits")[support] > 0)


def test_valid_setup_can_be_rescored_after_workdir_deletion(tmp_path):
    payload = result()
    assert SCORER.validate_result(payload) == []
    scored = SCORER.score(context(tmp_path, payload))
    assert all(gate.passed for gate in scored.gates)
    assert all(metric.value == 1 for metric in scored.metrics)


@pytest.mark.parametrize(
    "key,value",
    [
        ("posterior_search_run", True),
        ("science_validated", True),
        ("figure_of_merit", float("nan")),
        ("figure_of_merit", float("inf")),
        ("figure_of_merit", True),
        ("status", "model_constructed"),
    ],
)
def test_false_or_incomplete_smoke_evidence_fails(tmp_path, key, value):
    payload = result()
    payload["smoke"][key] = value
    scored = SCORER.score(context(tmp_path, payload))
    assert not next(gate.passed for gate in scored.gates if gate.name == "smoke")


@pytest.mark.parametrize(
    "key,value",
    [
        ("included_pixels", 26861),
        ("maximum_included_radius_arcsec", 3.7),
        ("likelihood_noise", "noise_map_subtracted.fits"),
        ("psf_sum", 7.4),
    ],
)
def test_changed_mask_noise_or_psf_fails(tmp_path, key, value):
    payload = result()
    payload["preparation"]["f390w"][key] = value
    scored = SCORER.score(context(tmp_path, payload))
    assert not next(gate.passed for gate in scored.gates if gate.name == "preparation")


def test_missing_presentation_fails(tmp_path):
    scored = SCORER.score(context(tmp_path, result(), artifact=False))
    assert not next(gate.passed for gate in scored.gates if gate.name == "presentation")


def test_malformed_payload_does_not_crash_scorer(tmp_path):
    for payload in ({}, {"smoke": [], "preparation": "wrong"}):
        assert SCORER.validate_result(payload)
        assert not all(
            gate.passed
            for gate in SCORER.score(context(tmp_path, payload, False)).gates
        )
