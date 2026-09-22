"""Posterior export cannot turn incomplete samples into a black-hole measurement."""

import importlib
import json
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def driver(monkeypatch):
    root = Path(__file__).resolve().parents[2]
    monkeypatch.syspath_prepend(str(root / "scripts/abell_1201"))
    return importlib.import_module("run_fit")


class Samples:
    paths = [("galaxies", "lens", "smbh", "einstein_radius")]
    weight_list = [1.0] * 600
    pdf_converged = True

    def median_pdf(self, as_instance):
        return [0.5]

    def values_at_sigma(self, sigma, as_instance):
        assert sigma == 1.0
        return [(0.2, 0.8)]


def test_mass_interval_transforms_endpoints_not_symmetric_errors(driver):
    af = driver.af
    model = af.Collection(
        galaxies=af.Collection(
            lens=af.Collection(
                smbh=af.Collection(
                    einstein_radius=af.UniformPrior(lower_limit=0.0, upper_limit=3.0)
                )
            )
        )
    )
    samples = af.SamplesPDF(
        model=model,
        sample_list=af.Sample.from_lists(
            model=model,
            parameter_lists=[[value] for value in np.linspace(0.2, 0.8, 600)],
            log_likelihood_list=[0.0] * 600,
            log_prior_list=[0.0] * 600,
            weight_list=[1.0 / 600] * 600,
        ),
    )
    summary = driver.posterior_summary(samples, 500)
    mass = summary["mass_solar"]
    assert mass["median"] == pytest.approx(float(driver.mass_solar(0.5)))
    assert mass["upper_68"] - mass["median"] > mass["median"] - mass["lower_68"]
    assert summary["science_validated"] is False
    assert summary["convergence_review_required"] is True


@pytest.mark.parametrize(
    "converged,weights", [(False, [1.0] * 600), (True, [1.0, 0.0])]
)
def test_incomplete_posterior_has_no_mass_estimate(driver, converged, weights):
    samples = Samples()
    samples.pdf_converged = converged
    samples.weight_list = weights
    summary = driver.posterior_summary(samples, 500)
    assert summary["status"] == "incomplete"
    assert summary["mass_solar"] is None


@pytest.mark.parametrize("value", [-1.0, np.nan, np.inf])
def test_invalid_einstein_radius_rejected(driver, value):
    with pytest.raises(ValueError):
        driver.mass_solar(value)


def test_default_command_never_starts_search(driver, monkeypatch, capsys):
    def forbidden(*args, **kwargs):
        raise AssertionError("description-only mode must not create a search")

    monkeypatch.setattr(driver.af, "Nautilus", forbidden)
    monkeypatch.setattr("sys.argv", ["run_fit.py"])
    driver.main()
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "description_only"
    assert report["posterior_search_run"] is False
