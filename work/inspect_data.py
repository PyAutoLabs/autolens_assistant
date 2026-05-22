"""
Inspect the F277W band of the COSMOS-Web Einstein ring dataset.

Loads the imaging arrays, the PSF, and the extra-galaxies mask, prints
basic shape / pixel-scale info, and saves a subplot of the imaging
dataset plus a separate plot of the extra-galaxies mask.

Run from the repo root:

    NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \\
      python work/inspect_data.py
"""
import json
from pathlib import Path

import autolens as al
import autolens.plot as aplt


DATASET_PATH = Path("dataset/imaging/cosmos_web_ring/wavebands/F277W")
EXTRA_MASK_PATH = DATASET_PATH / "mask_extra_galaxies.fits"
info = json.loads((DATASET_PATH / "info.json").read_text())
PIXEL_SCALE = info["pixel_scale"]

PLOT_DIR = Path("work/plots/cosmos_web_ring")
PLOT_DIR.mkdir(parents=True, exist_ok=True)


dataset = al.Imaging.from_fits(
    data_path=DATASET_PATH / "data.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    psf_path=DATASET_PATH / "psf.fits",
    pixel_scales=PIXEL_SCALE,
)

print(f"data shape       : {dataset.data.shape_native}")
print(f"pixel scale      : {dataset.pixel_scales[0]} arcsec/pixel")
field_arcsec = dataset.data.shape_native[0] * dataset.pixel_scales[0]
print(f"field of view    : {field_arcsec:.2f} arcsec on a side")
print(f"PSF kernel shape : {dataset.psf.kernel.shape_native}")

mask_extra_galaxies = al.Mask2D.from_fits(
    file_path=EXTRA_MASK_PATH,
    pixel_scales=PIXEL_SCALE,
    invert=False,
)
print(f"extra-galaxies mask shape       : {mask_extra_galaxies.shape_native}")
print(f"extra-galaxies pixels masked    : {int(mask_extra_galaxies.sum())}")

aplt.subplot_imaging_dataset(
    dataset=dataset,
    output_path=str(PLOT_DIR),
    output_filename="imaging_subplot",
    output_format="png",
)

aplt.plot_array(
    array=mask_extra_galaxies.astype("float"),
    title="Extra-galaxies mask (1 = masked)",
    output_path=str(PLOT_DIR),
    output_filename="extra_galaxies_mask",
    output_format="png",
)

print(f"Saved to: {PLOT_DIR.resolve()}")
