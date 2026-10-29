"""Exercise the introductory plot on native-array coordinates and synthetic data."""
from types import SimpleNamespace

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

from autoassistant.intro_plots import plot_intro_array, plot_intro_dataset


class Array:
    def __init__(self, values, mask=None):
        self.native = SimpleNamespace(array=np.asarray(values, dtype=float))
        self.mask = mask
        self.geometry = SimpleNamespace(extent=(-2, 2, -2, 2))


def test_four_panels_exclusions_and_display_controls(tmp_path):
    values = np.arange(16, dtype=float).reshape(4, 4) - 2
    mask = np.zeros((4, 4), dtype=bool)
    mask[0, 0] = True
    excluded = np.zeros_like(mask)
    excluded[1, 1] = True
    noise = np.ones((4, 4))
    noise[1, 1] = 1e8
    dataset = SimpleNamespace(data=Array(values, mask), noise_map=Array(noise, mask),
                              signal_to_noise_map=Array(values / noise, mask),
                              psf=SimpleNamespace(kernel=Array(np.eye(4))))
    before = dataset.data.native.array.copy()
    fig = plot_intro_dataset(dataset, colormap="cividis", stretch=0.1,
                             excluded_pixels=excluded, output_path=tmp_path)
    panels = [ax for ax in fig.axes if ax.images]
    assert [ax.get_title(loc="left") for ax in panels] == [
        "Image", "Noise map", "Signal-to-noise map", "PSF"]
    image = panels[0].images[0]
    assert image.get_cmap().name == "cividis"
    assert image.get_array().mask[0, 0] and image.get_array().mask[1, 1]
    assert image.norm.vmin < 0  # Negative measurements remain in the display.
    assert panels[1].images[0].norm.vmax < 2  # Excluded high noise cannot swamp the scale.
    np.testing.assert_array_equal(dataset.data.native.array, before)
    assert (tmp_path / "dataset.png").is_file()
    assert image.origin == "upper"
    assert image.get_extent() == [-2, 2, -2, 2]


@pytest.mark.parametrize("values", [np.zeros((3, 3)), np.full((3, 3), np.nan)])
def test_empty_or_constant_data_has_finite_scale(values):
    fig, ax = plt.subplots()
    artist = plot_intro_array(Array(values), ax, "Image")
    assert np.isfinite([artist.norm.vmin, artist.norm.vmax]).all()
    assert artist.norm.vmax > artist.norm.vmin
    plt.close(fig)


def test_contrast_changes_display_not_values():
    data = Array([[0, 1], [2, 100]])
    fig, axes = plt.subplots(1, 2)
    a = plot_intro_array(data, axes[0], "A", stretch=0.01)
    b = plot_intro_array(data, axes[1], "B", stretch=0.1)
    assert a.norm(1) > b.norm(1)
    np.testing.assert_array_equal(a.get_array(), b.get_array())
    plt.close(fig)


def test_invalid_stretch_fails_clearly():
    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match="stretch"):
        plot_intro_array(Array(np.ones((2, 2))), ax, "Image", stretch=0)
    plt.close(fig)
