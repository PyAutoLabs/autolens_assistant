"""
Abell 1201: Inspect Supplied Imaging
===================================

Inventory the supplied FITS files and compare the two observed bands with their
lens-light-subtracted variants before choosing inputs for inference. This script
does not fit a model, alter the data, or approve a mask. Axes use pixel offsets
because the supplied headers do not establish an angular scale or sky orientation.

__Contents__

- **Imports:** Load FITS, numerical and plotting utilities.
- **Inventory:** Record checksums, dimensions, header metadata and suspect values.
- **Inspection:** Compare images, central structure and noise treatment.
- **Command:** Save a machine-readable inventory and dataset inspection figure.
"""

"""__Imports__

Astropy reads the original FITS arrays without a PyAutoLens loader normalising
the PSF or transforming coordinates. Matplotlib displays array rows increasing
upwards; no north/east orientation is inferred from the stripped headers.
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
from astropy.visualization import AsinhStretch, ImageNormalize


"""__Inventory__

The published data and analysis are described at
https://github.com/Jammy2211/autolens_abell_1201. Local file names alone do not
prove their provenance. Byte checksums let the scientist compare this inventory
with a pinned reference before selecting an authoritative variant. Zero noise
must not enter a likelihood as a valid uncertainty; PSF sums are reported without
modifying the input kernels.
"""


def inventory(dataset):
    records = []
    for path in sorted(dataset.glob("*/*.fits")):
        data, header = fits.getdata(path, header=True)
        finite = np.isfinite(data)
        values = data[finite]
        records.append(
            {
                "path": str(path.relative_to(dataset)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "shape": list(data.shape),
                "dtype": str(data.dtype),
                "nonfinite_pixels": int(np.count_nonzero(~finite)),
                "zero_pixels": int(np.count_nonzero(data == 0)),
                "negative_pixels": int(np.count_nonzero(data < 0)),
                "minimum": float(values.min()) if values.size else None,
                "maximum": float(values.max()) if values.size else None,
                "sum": float(values.sum()) if values.size else None,
                "metadata": {
                    key: header[key]
                    for key in (
                        "BUNIT", "EXPTIME", "FILTER", "PIXSCALE", "CDELT1",
                        "CDELT2", "CD1_1", "CD2_2", "TELESCOP", "INSTRUME",
                    )
                    if key in header
                },
            }
        )
    if not records:
        raise ValueError(f"No FITS files found under {dataset}")
    return records


"""__Inspection__

Each band has its own explicitly recorded intensity stretch. Image and
subtracted-image panels within a band share the same stretch; the centre zoom
uses the original image. The final panel flags zero subtracted noise and very
large base noise (greater than 100 times its median), which may encode prior
exclusions. This threshold is diagnostic, not a proposed scientific mask.

The real-data inspection gate is defined in
autolens_assistant:skills/al_prepare_imaging_data.md. No mask is applied here.
"""


def inspection(dataset, output):
    fig, axes = plt.subplots(2, 4, figsize=(17, 9), constrained_layout=True)
    settings = {}
    for row, band in enumerate(("f390w", "f814w")):
        folder = dataset / band
        data = fits.getdata(folder / "image.fits")
        subtracted = fits.getdata(folder / "data_mge_subtracted.fits")
        noise = fits.getdata(folder / "noise_map.fits")
        subtracted_noise = fits.getdata(folder / "noise_map_subtracted.fits")
        if any(a.shape != data.shape for a in (subtracted, noise, subtracted_noise)):
            raise ValueError(f"Inconsistent image/noise shapes for {band}")
        vmin, vmax = np.nanpercentile(data, (5, 99.7))
        norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=AsinhStretch(0.05))
        settings[band] = {
            "vmin": float(vmin), "vmax": float(vmax), "asinh_a": 0.05,
            "cmap": "magma", "origin": "lower", "axes": "pixel offsets",
        }
        ny, nx = data.shape
        extent = (-nx / 2, nx / 2, -ny / 2, ny / 2)
        for col, (array, title) in enumerate(
            ((data, "image.fits"), (subtracted, "data_mge_subtracted.fits"),
             (data, "Original image: centre zoom"))
        ):
            ax = axes[row, col]
            ax.imshow(array, origin="lower", extent=extent, cmap="magma", norm=norm)
            ax.set_title(f"{band.upper()} — {title}", fontsize=10)
            if col == 2:
                ax.set_xlim(-65, 65)
                ax.set_ylim(-65, 65)
            ax.set_xlabel("Column offset (pixels)")
            ax.set_ylabel("Row offset (pixels)")
        flags = np.zeros(data.shape, dtype=int)
        large = noise > 100 * np.median(noise[np.isfinite(noise) & (noise > 0)])
        flags[large] = 1
        flags[subtracted_noise <= 0] = 2
        ax = axes[row, 3]
        im = ax.imshow(flags, origin="lower", extent=extent, cmap="viridis", vmin=0, vmax=2)
        ax.set_title("Noise flags (no mask applied)", fontsize=10)
        ax.set_xlabel("Column offset (pixels)")
        ax.set_ylabel("Row offset (pixels)")
        bar = fig.colorbar(im, ax=ax, ticks=(0, 1, 2), shrink=0.75)
        bar.ax.set_yticklabels(("Other", "Large base noise", "Nonpositive subtracted noise"))
    fig.suptitle("Abell 1201 — input inspection; angular scale and mask unconfirmed")
    path = output / "dataset.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path, settings


"""__Command__

Run from the assistant root, supplying the directory containing f390w/ and
f814w/. Outputs go to scripts/scratch/ by default. inventory.json preserves
input checksums and display settings; dataset.png is the human review surface.
The original FITS files are only read.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("__Contents__")[0])
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("scripts/scratch/abell_1201"))
    args = parser.parse_args()
    records = inventory(args.dataset)
    args.output.mkdir(parents=True, exist_ok=True)
    path, settings = inspection(args.dataset, args.output)
    report = {
        "status": "inspection_only_not_approved_for_fitting",
        "dataset_root": str(args.dataset.resolve()),
        "pixel_scale_arcsec": None,
        "units": None,
        "files": records,
        "display": settings,
    }
    (args.output / "inventory.json").write_text(json.dumps(report, indent=2) + "\n")
    print(path.resolve())
    print((args.output / "inventory.json").resolve())


if __name__ == "__main__":
    main()
