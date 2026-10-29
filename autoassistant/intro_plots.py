"""
Introductory Imaging Figures
===========================

Four panels for a first look at an imaging dataset. Display normalization changes
neither pixel values nor the likelihood. The notebook converter embeds the helper
body so Colab needs no assistant checkout.

__Contents__

- **Array display:** Preserve coordinates, masks and physical colorbar values.
- **Dataset display:** Image, noise, signal-to-noise and PSF in a two-by-two layout.
"""

# Notebook helper code
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import AsinhNorm, Normalize
import numpy as np


def plot_intro_array(array, ax, title, colormap="magma", stretch=0.01,
                     radius=None, unit="", linear=False, excluded_pixels=None):
    """Draw a native array with an asinh stretch; smaller stretch lifts faint light.

    ``stretch`` is the linear-width fraction of the displayed data range.
    Negative pixels are retained. Masked/non-finite pixels are grey. Limits use
    all finite, unmasked pixels within the view, without percentile clipping.
    PyAutoArray: autoarray/structures/arrays/uniform_2d.py supplies native values,
    mask and geometry.extent; no model calculation is changed here.
    """
    if not np.isfinite(stretch) or stretch <= 0:
        raise ValueError("stretch must be a finite positive number")
    if radius is not None and (not np.isfinite(radius) or radius <= 0):
        raise ValueError("radius must be a finite positive number")
    native = getattr(array, "native", array)
    values = np.asarray(getattr(native, "array", native), dtype=float)
    if values.ndim != 2:
        raise ValueError("An introductory image must be two-dimensional")
    masked = np.ma.masked_invalid(values)
    mask = getattr(array, "mask", None)
    if mask is not None:
        mask = np.asarray(getattr(mask, "array", mask), dtype=bool)
        if mask.shape == values.shape:
            masked = np.ma.masked_where(mask, masked)
    if excluded_pixels is not None:
        excluded_pixels = np.asarray(excluded_pixels, dtype=bool)
        if excluded_pixels.shape != values.shape:
            raise ValueError("excluded_pixels must have the image shape")
        masked = np.ma.masked_where(excluded_pixels, masked)
    geometry = getattr(array, "geometry", None)
    extent = getattr(geometry, "extent", None)
    if extent is None:
        extent = (-values.shape[1] / 2, values.shape[1] / 2,
                  -values.shape[0] / 2, values.shape[0] / 2)
    xmin, xmax, ymin, ymax = extent
    visible = masked
    if radius is not None:
        x = xmin + (np.arange(values.shape[1]) + 0.5) * (xmax - xmin) / values.shape[1]
        y = ymax - (np.arange(values.shape[0]) + 0.5) * (ymax - ymin) / values.shape[0]
        visible = np.ma.masked_where((abs(y[:, None]) > radius) |
                                    (abs(x[None, :]) > radius), masked)
    finite = visible.compressed()
    lo, hi = (float(finite.min()), float(finite.max())) if finite.size else (0.0, 1.0)
    if hi <= lo:
        hi = lo + max(abs(lo) * 0.01, 1e-6)
    norm = (Normalize(lo, hi) if linear else
            AsinhNorm(linear_width=stretch * (hi - lo), vmin=lo, vmax=hi))
    cmap = plt.get_cmap(colormap).with_extremes(bad="#d9dee5")
    artist = ax.imshow(masked, origin="upper", extent=extent, cmap=cmap,
                       norm=norm, interpolation="nearest", aspect="equal")
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("x (arcsec)" if geometry is not None else "x (pixel)")
    ax.set_ylabel("y (arcsec)" if geometry is not None else "y (pixel)")
    if radius is not None:
        ax.set_xlim(-radius, radius)
        ax.set_ylim(-radius, radius)
    ax.tick_params(labelsize=9)
    colorbar = ax.figure.colorbar(artist, ax=ax, fraction=0.046, pad=0.035)
    ticks = norm.inverse(np.linspace(0, 1, 5))
    colorbar.set_ticks(ticks, labels=[f"{value:.3g}" for value in ticks])
    colorbar.ax.tick_params(labelsize=8)
    if unit:
        colorbar.set_label(unit, fontsize=9)
    return artist


def plot_intro_dataset(dataset, colormap="magma", stretch=0.01, radius=None,
                       output_path=None, output_filename="dataset", excluded_pixels=None):
    """Return a four-panel figure, optionally saving PNG without displaying it.

    The image uses the chosen stretch; noise is linear, S/N is asinh, and the
    PSF uses a stronger asinh stretch to show its wings. Colorbars always show
    original values. Grey areas are masked or non-finite, not zero brightness.
    """
    fig, axes = plt.subplots(2, 2, figsize=(10, 9), layout="constrained")
    fig.set_facecolor("white")
    plot_intro_array(dataset.data, axes[0, 0], "Image", colormap, stretch, radius,
                     "Brightness (data units)", excluded_pixels=excluded_pixels)
    plot_intro_array(dataset.noise_map, axes[0, 1], "Noise map", "cividis", radius=radius,
                     unit="Uncertainty (data units)", linear=True, excluded_pixels=excluded_pixels)
    plot_intro_array(dataset.signal_to_noise_map, axes[1, 0], "Signal-to-noise map",
                     "viridis", stretch=0.1, radius=radius, unit="Signal / noise", excluded_pixels=excluded_pixels)
    if dataset.psf is not None:
        plot_intro_array(dataset.psf.kernel, axes[1, 1], "PSF", "magma", stretch=0.003,
                         unit="Kernel weight")
    else:
        axes[1, 1].set_title("PSF", loc="left")
        axes[1, 1].text(0.5, 0.5, "No PSF supplied", ha="center", va="center",
                        transform=axes[1, 1].transAxes)
        axes[1, 1].set_axis_off()
    fig.supxlabel("Grey: masked or unavailable pixels" +
                  ("; down-weighted neighbour excluded from display" if excluded_pixels is not None else ""),
                  fontsize=9)
    if output_path is not None:
        folder = Path(output_path)
        folder.mkdir(parents=True, exist_ok=True)
        fig.savefig(folder / f"{output_filename}.png", dpi=160, facecolor="white", bbox_inches="tight", pad_inches=0.15)
        plt.close(fig)
    return fig
