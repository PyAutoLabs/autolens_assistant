"""
Tests for the results-inspector MCP tools: the core
(`autofit.mcp.tools`, the ``autofit[mcp]`` extra) and this repo's lens layer
(`lens_tools.py`).

The fixture runs a real (tiny) `af.LBFGS` fit of the `af.ex.Gaussian` toy so
the output directory always matches the installed PyAutoFit's on-disk format,
then plants a subplot-fit grid image and a `fit.fits` so the lens extraction
tools have real-shaped inputs without paying for a lens fit.
"""

from pathlib import Path

import numpy as np
import pytest
from astropy.io import fits
from PIL import Image

import autofit as af
import autolens as al
from autonerves import conf
from autofit.aggregator.summary.aggregate_images import subplot_filename

from autofit.mcp import tools

from autoassistant.mcp import lens_tools

ROOT = Path(__file__).resolve().parents[2]

PANEL = 40  # planted per-panel size in pixels


@pytest.fixture(scope="module")
def output_root(tmp_path_factory):
    root = tmp_path_factory.mktemp("output")
    conf.instance.push(new_path=str(ROOT / "config"), output_path=str(root))

    xvalues = np.arange(100.0)
    gaussian = af.ex.Gaussian(centre=50.0, normalization=25.0, sigma=10.0)
    data = gaussian.model_data_from(xvalues=xvalues)
    noise_map = np.full(fill_value=1.0, shape=data.shape)
    analysis = af.ex.Analysis(data=data, noise_map=noise_map)

    for name in ("fit_0", "fit_1"):
        search = af.LBFGS(name=name, path_prefix="mcp_fixture")
        search.fit(model=af.Model(af.ex.Gaussian), analysis=analysis)

    grid_x = 1 + max(position.value[0] for position in al.agg.subplot_fit)
    grid_y = 1 + max(position.value[1] for position in al.agg.subplot_fit)
    for marker in root.rglob(".completed"):
        directory = marker.parent
        (directory / "image").mkdir(exist_ok=True)
        grid_name = subplot_filename(al.agg.subplot_fit.data)
        grid_image = Image.new(
            "RGB", (grid_x * PANEL, grid_y * PANEL), color=(200, 40, 40)
        )
        grid_image.save(directory / "image" / f"{grid_name}.png")
        grid_image.save(directory / "image" / "subplot_fit.png")
        fits.HDUList(
            [fits.PrimaryHDU()]
            + [
                fits.ImageHDU(np.zeros((4, 4)), name=hdu.value)
                for hdu in al.agg.fits_fit
            ]
        ).writeto(directory / "files" / "fit.fits")

    return root


@pytest.fixture(scope="module")
def fit_directory(output_root):
    return sorted(
        marker.parent for marker in output_root.rglob(".completed")
    )[0]


# --- Mirrored core ----------------------------------------------------------


def test_list_searches(output_root):
    rows = tools.list_searches(str(output_root), sort_by="max_log_likelihood")

    assert len(rows) == 2
    assert {row["name"] for row in rows} == {"fit_0", "fit_1"}
    for row in rows:
        assert row["is_complete"] is True
        assert isinstance(row["max_log_likelihood"], float)
        assert row["log_evidence"] is None
        assert row["model_free_parameters"] == 3


def test_get_model(fit_directory):
    result = tools.get_model(str(fit_directory))

    assert "Gaussian" in result["info"]
    assert result["model"]["class_path"].endswith("Gaussian")


def test_get_result_summary(fit_directory):
    assert "Maximum Log Likelihood" in tools.get_result_summary(
        str(fit_directory)
    )


def test_get_samples_summary(fit_directory):
    summary = tools.get_samples_summary(str(fit_directory))

    assert isinstance(summary["max_log_likelihood"], float)
    assert summary["parameter_paths"] == ["centre", "normalization", "sigma"]
    assert len(summary["max_log_likelihood_parameters"]) == 3


def test_fetch_image_and_list(fit_directory):
    assert "subplot_fit.png" in tools.list_images(str(fit_directory))
    assert tools.fetch_image(str(fit_directory), name="subplot_fit").size[0] > 0


# --- Lens layer -------------------------------------------------------------


def test_list_image_names():
    names = lens_tools.list_image_names()

    assert "data" in names["subplot_fit"]
    assert "model_data" in names["fits_fit"]


def test_resolve_errors():
    with pytest.raises(KeyError, match="Unknown group"):
        lens_tools._resolve("no_such_group.data")
    with pytest.raises(KeyError, match="Unknown name"):
        lens_tools._resolve("subplot_fit.no_such_name")


def test_combine_images(output_root):
    image = lens_tools.combine_images(
        str(output_root),
        subplots=["subplot_fit.data", "subplot_fit.model_data"],
    )

    # Two panels wide, one row per fit.
    assert image.size == (2 * PANEL, 2 * PANEL)


def test_extract_fits(output_root, tmp_path):
    destination = tmp_path / "extracted.fits"

    path = lens_tools.extract_fits(
        str(output_root),
        hdus=["fits_fit.model_data"],
        destination_path=str(destination),
    )

    with fits.open(path) as hdu_list:
        # A primary HDU plus one extracted HDU per fit.
        assert len(hdu_list) == 3


def test_extract_fits_refuses_output_dir(output_root):
    with pytest.raises(ValueError, match="outside the search-output"):
        lens_tools.extract_fits(
            str(output_root),
            hdus=["fits_fit.model_data"],
            destination_path=str(output_root / "sneaky.fits"),
        )
