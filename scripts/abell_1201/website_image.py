"""
Abell 1201: Presentation Image
==============================

Render a two-band colour composite and a monochrome alternative from the
observed F390W/F814W images. These display products are separate from inference:
no pixels are written back to FITS and no model or black-hole image is inserted.

__Contents__

- **Inputs:** Load the verified bands and record their provenance.
- **Colour:** Map two filters to RGB with a common asinh intensity stretch.
- **Export:** Save presentation images, settings, caption and alternative text.
"""

"""__Inputs__

Use image.fits in each filter directory from the published analysis dataset:
https://github.com/Jammy2211/autolens_abell_1201/tree/d412b6379934f935bfd955ee0c2d74883e88c320/dataset
These are processed observations and already contain contaminant edits. Their
central regions share the paper's 0.04 arcsec/pixel sampling. The similarly
named f390w/image_new.fits is a flipped F814W array and must not supply blue.
"""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits


def load_band(dataset, band):
    path = dataset / band / "image.fits"
    data = np.asarray(fits.getdata(path), dtype=float)
    if data.shape != (421, 421) or not np.all(np.isfinite(data)):
        raise ValueError(f"Expected finite 421 x 421 published image: {path}")
    return data, {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


"""__Colour__

F814W supplies red, F390W supplies blue, and green is a weighted mixture of
those two bands. This is an illustrative two-filter colour assignment, not
three-filter natural colour or a calibrated colour measurement. A common asinh
stretch keeps channel ratios during intensity compression; saturated pixels
are scaled together. Negative measured intensities display as black.

The crop shows the central galaxy and giant arc. It excludes most of the
edited peripheral field without reconstructing missing pixels. No rotation,
band registration, denoising, inpainting or background fit is performed.
"""


def colour(red, blue, red_scale, blue_scale, stretch):
    r = np.maximum(red, 0) / red_scale
    b = np.maximum(blue, 0) / blue_scale
    g = 0.55 * r + 0.45 * b
    rgb = np.stack((r, g, b), axis=-1)
    intensity = np.mean(rgb, axis=-1)
    gain = np.divide(
        np.arcsinh(stretch * intensity),
        intensity * np.arcsinh(stretch),
        out=np.zeros_like(intensity),
        where=intensity > 0,
    )
    rgb *= gain[..., None]
    rgb /= np.maximum(1, np.max(rgb, axis=-1))[..., None]
    return np.clip(rgb, 0, 1)


"""__Export__

Display settings and input SHA-256 hashes accompany the PNGs. Image-only
exports suit a website hero or the initial response to a science prompt; the
caption identifies the observations, colour mapping and existing processing.
The native pixel sampling is retained (no interpolation), so a web page may
choose its own display size. Outputs are previews until the scientist accepts
the data provenance, crop and attribution for publication.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("__Contents__")[0])
    parser.add_argument(
        "--dataset", type=Path, default=Path("dataset/imaging/abell_1201")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("scripts/scratch/abell_1201/website")
    )
    parser.add_argument("--red-scale", type=float, default=0.65)
    parser.add_argument("--blue-scale", type=float, default=0.08)
    parser.add_argument("--stretch", type=float, default=12.0)
    args = parser.parse_args()
    if min(args.red_scale, args.blue_scale, args.stretch) <= 0:
        parser.error("Scales and stretch must be positive")
    red, red_source = load_band(args.dataset, "f814w")
    blue, blue_source = load_band(args.dataset, "f390w")
    crop = (145, 315, 125, 300)
    y0, y1, x0, x1 = crop
    red = red[y0:y1, x0:x1]
    blue = blue[y0:y1, x0:x1]
    rgb = colour(red, blue, args.red_scale, args.blue_scale, args.stretch)
    mono = np.clip(
        np.arcsinh(args.stretch * np.maximum(blue, 0) / args.blue_scale)
        / np.arcsinh(args.stretch),
        0,
        1,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    plt.imsave(args.output / "abell_1201_rgb.png", rgb, origin="lower")
    plt.imsave(
        args.output / "abell_1201_f390w.png",
        mono,
        origin="lower",
        cmap="magma",
        vmin=0,
        vmax=1,
    )
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), facecolor="#080b12")
    for ax, array, title in zip(
        axes, (rgb, mono), ("Two-band colour", "F390W · intensity")
    ):
        ax.imshow(
            array, origin="lower", interpolation="nearest", cmap="magma", vmin=0, vmax=1
        )
        ax.set_title(title, color="#e9edf5", fontsize=13, pad=14)
        ax.set_axis_off()
    fig.subplots_adjust(left=0.025, right=0.975, bottom=0.025, top=0.9, wspace=0.035)
    fig.savefig(args.output / "comparison.png", dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    caption = (
        "Abell 1201 in processed Hubble Space Telescope observations. The arc is "
        "light from a background galaxy distorted by gravitational lensing. "
        "Colour combines F814W (red) and F390W (blue), with a mixed green channel "
        "and a nonlinear display stretch; it is not natural colour. The black hole "
        "is not directly visible. Supplied data already include contaminant edits."
    )
    metadata = {
        "status": "presentation_preview_not_fit_data",
        "sources": {"red": red_source, "blue": blue_source},
        "crop_array_slices_y0_y1_x0_x1": crop,
        "origin": "lower",
        "pixel_scale_arcsec": 0.04,
        "red_scale": args.red_scale,
        "blue_scale": args.blue_scale,
        "green_mix": {"red": 0.55, "blue": 0.45},
        "asinh_stretch": args.stretch,
        "caption": caption,
        "alt_text": "A warm-coloured central galaxy below a curved blue arc of gravitationally lensed light.",
        "credit": "HST observations; processed analysis data accompanying Nightingale et al. (2023), doi:10.1093/mnras/stad587. Final publication attribution and redistribution permission pending.",
    }
    (args.output / "display.json").write_text(json.dumps(metadata, indent=2) + "\n")
    for name in (
        "comparison.png",
        "abell_1201_rgb.png",
        "abell_1201_f390w.png",
        "display.json",
    ):
        print((args.output / name).resolve())


if __name__ == "__main__":
    main()
