"""
Abell 1201: Approved Processed Boundary
=======================================

Load the published contaminant-cleaned imaging and retain the exact boundary
of the supplied processed files, approved by the scientist on 2026-09-22.
This preparation-only script plots the masked dataset; it does not build a
lens model, choose priors or run inference.

__Contents__

- **Imports:** Load the current PyAutoLens data and plotting APIs.
- **Dataset:** Preserve the cleaned images/noise and exact processed support.
- **Inspection:** Export the prepared dataset and checks without starting a fit.
"""

"""__Imports__

The current calls follow autolens_assistant:skills/al_prepare_imaging_data.md.
Array2D.from_fits and Imaging.from_fits share FITS orientation conventions,
so the support mask follows the image without assuming raw array orientation.
"""

from autonerves import (
    jax_wrapper,
)  # Set the numerical environment before PyAuto imports.
import argparse
import json
from pathlib import Path

import numpy as np
import autolens as al
import autolens.plot as aplt


"""__Dataset__

image.fits and noise_map.fits are the byte-verified published cleaned inputs.
Their existing contaminant down-weighting is retained. The positive support
of noise_map_subtracted.fits defines the approved processed boundary only:
that file is not substituted for the likelihood noise map. Both supplied bands
have exactly 31417 included pixels, extending to 4.0 arcsec at 0.04 arcsec/pixel.

The source of the pixel scale is the published analysis runner linked in the
sibling README. PyAutoArray:autoarray/dataset/imaging/dataset.py owns the
Imaging loader; the live loader normalises the PSF. No FITS inputs are changed.
"""


def prepare(dataset_path):
    support = al.Array2D.from_fits(
        file_path=dataset_path / "noise_map_subtracted.fits", pixel_scales=0.04
    )
    support_values = np.asarray(support.native)
    if support_values.shape != (421, 421) or not np.all(np.isfinite(support_values)):
        raise ValueError("Expected the inspected finite 421 x 421 processed support")
    mask_values = support_values <= 0
    if np.count_nonzero(~mask_values) != 31417:
        raise ValueError(
            "Processed support differs from the scientist-reviewed dataset"
        )
    dataset = al.Imaging.from_fits(
        data_path=dataset_path / "image.fits",
        noise_map_path=dataset_path / "noise_map.fits",
        psf_path=dataset_path / "psf.fits",
        pixel_scales=0.04,
    )
    if dataset.shape_native != mask_values.shape:
        raise ValueError(
            "Loaded image shape changed; disable dataset capping for inspection"
        )
    mask = al.Mask2D(mask=mask_values, pixel_scales=0.04)
    dataset = dataset.apply_mask(mask=mask)
    if not np.all(np.asarray(dataset.noise_map) > 0):
        raise ValueError("Nonpositive noise within the approved support")
    if not np.isclose(np.asarray(dataset.psf.kernel.native).sum(), 1.0):
        raise ValueError("Loaded PSF is not normalised")
    return dataset


"""__Inspection__

aplt.subplot_imaging_dataset is the current functional plot API. Its output
shows the actual arrays that a future fit would receive, independently of the
website display. Choosing a baseline, nuisance parameters and compute budget
remains a subsequent scientific step.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("__Contents__")[0])
    parser.add_argument(
        "--dataset", type=Path, default=Path("dataset/imaging/abell_1201")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("scripts/scratch/abell_1201/prepared")
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "preparation.json").write_text('{"status": "preparing"}\n')
    reports = {}
    for band in ("f390w", "f814w"):
        dataset = prepare(args.dataset / band)
        aplt.subplot_imaging_dataset(
            dataset=dataset,
            output_path=str(args.output),
            output_filename=f"dataset_{band}",
            output_format="png",
        )
        reports[band] = {
            "mask": "exact positive support of noise_map_subtracted.fits",
            "included_pixels": int(np.asarray(dataset.data).size),
            "pixel_scale_arcsec": 0.04,
            "maximum_included_radius_arcsec": 4.0,
            "psf_sum": float(np.asarray(dataset.psf.kernel.native).sum()),
            "likelihood_data": "image.fits",
            "likelihood_noise": "noise_map.fits",
            "fit_executed": False,
        }
        print((args.output / f"dataset_{band}.png").resolve())
    (args.output / "preparation.json").write_text(json.dumps(reports, indent=2) + "\n")


if __name__ == "__main__":
    main()
