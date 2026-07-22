"""
COSMOS-Web Ring README Figure
=============================

Builds the three-panel figure shown at the top of the README's "Getting Started"
section, which introduces the bundled COSMOS-Web Ring dataset that both starter
prompts point at.

The panels share one field of view (167 x 167 pixels at 0.06"/pixel, ~10" on a
side), so a feature seen in one panel sits at the same place in the others:

- **RGB** — the survey colour composite, annotated with an arrow marking the
  extra galaxy that sits on the southern edge of the ring. Priming the reader
  for it here means the "watch out for the extra galaxy" beat in a modelling
  session lands as a recognition rather than a surprise.
- **F277W / F444W** — the two JWST bands the multi-wavelength starter prompt
  fits, each overlaid with the circular mask that a real fit would apply.

__Contents__

- **Paths**: inputs (survey RGB, bundled `.fits`) and the output figure.
- **Registration**: the pixel mapping tying the RGB cutout to the `.fits` grid.
- **Load**: read the RGB composite and both single-band images.
- **Plot**: render the three panels, arrow annotation and mask overlay.
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from pathlib import Path
from astropy.io import fits

"""__Paths__

The RGB composite is the `6_rgb.png` cutout published for COSJ100024+015334 in
the COWLS COSMOS-Web lens survey repository; it is vendored alongside this
script so the figure can be rebuilt offline. The single-band images are the
`data.fits` files bundled with the assistant under `dataset/imaging/`.
"""

DOCS_PATH = Path(__file__).parent
REPO_PATH = DOCS_PATH.parent

RGB_PATH = DOCS_PATH / "images" / "sources" / "cosmos_web_ring_6_rgb.png"
DATASET_PATH = REPO_PATH / "dataset" / "imaging" / "cosmos_web_ring" / "wavebands"
OUTPUT_PATH = DOCS_PATH / "images" / "cosmos_web_ring_dataset.png"

BANDS = ["F277W", "F444W"]

"""__Registration__

The RGB cutout and the bundled `.fits` images are both sampled at 0.06"/pixel
but were cut out on different grids. Cross-matching the two brightest sources
(the lens itself and the bright galaxy to the north-west) fixes the offset: the
lens sits at `(y, x) = (84, 82)` in the RGB and `(104, 103)` in the `.fits`, and
the y-axis runs the opposite way because the PNG is stored top-row-first.

Applying that mapping to the RGB's 167-pixel span gives the `.fits` crop below,
so all three panels frame the same patch of sky. The crop is then flipped in y
at load time, putting the `.fits` data into the same top-row-first frame as the
RGB — after which the two annotated positions below hold in every panel.
Coordinates follow the PyAutoLens `(y, x)` ordering throughout.
"""

PIXEL_SCALE = 0.06

FITS_CROP_Y = (22, 189)
FITS_CROP_X = (21, 188)

LENS_CENTRE = (82, 82)
EXTRA_GALAXY_CENTRE = (103, 90)

"""The mask radius that a fit of this system would use. The lensed ring reaches
~1.3", so 1.8" takes in all of the lensed emission (and the extra galaxy blended
with it) while excluding the unrelated sources further out."""

MASK_RADIUS_ARCSEC = 1.8

"""__Load__

`arcsinh` scaling of the single-band data brings the faint outer ring and the
bright lens core into the same display range without saturating either. The
`[::-1]` flip puts the `.fits` row order into the RGB's top-row-first frame, so
north is up in all three panels.
"""


def load_band(band):
    data = fits.getdata(DATASET_PATH / band / "data.fits")
    data = data[FITS_CROP_Y[0] : FITS_CROP_Y[1], FITS_CROP_X[0] : FITS_CROP_X[1]]
    return np.arcsinh(data[::-1] / 0.015)


rgb = mpimg.imread(RGB_PATH)
bands = {band: load_band(band) for band in BANDS}

"""__Plot__

One row of three panels. The RGB keeps its native orientation (top-row-first),
and the single-band panels are drawn with `origin="upper"` so north is up in all
three. A 1" scale bar on the first panel sets the physical scale for the row.
"""

figure, axes = plt.subplots(1, 3, figsize=(13.5, 4.9))

axes[0].imshow(rgb, interpolation="bicubic")
axes[0].set_title("RGB Composite (COSMOS-Web)", fontsize=12, pad=8)

"""The arrow points in from open sky south-east of the ring, so it never crosses
the lensed emission it is drawing attention to."""

axes[0].annotate(
    "extra galaxy",
    xy=(EXTRA_GALAXY_CENTRE[1] + 5, EXTRA_GALAXY_CENTRE[0] + 5),
    xytext=(133, 141),
    color="white",
    fontsize=11.5,
    fontweight="bold",
    ha="center",
    arrowprops=dict(arrowstyle="-|>", color="white", lw=1.8, shrinkA=0, shrinkB=6),
)

scale_bar_pixels = 1.0 / PIXEL_SCALE
axes[0].plot(
    [12, 12 + scale_bar_pixels], [156, 156], color="white", lw=2.5, solid_capstyle="butt"
)
axes[0].text(12 + scale_bar_pixels / 2.0, 151, '1"', color="white", fontsize=10, ha="center")

for ax, band in zip(axes[1:], BANDS):

    ax.imshow(bands[band], origin="upper", cmap="magma", interpolation="bicubic")
    ax.set_title(f"JWST {band}", fontsize=12, pad=8)

    ax.add_patch(
        Circle(
            (LENS_CENTRE[1], LENS_CENTRE[0]),
            radius=MASK_RADIUS_ARCSEC / PIXEL_SCALE,
            fill=False,
            color="cyan",
            lw=1.6,
            ls="--",
        )
    )

    ax.text(
        LENS_CENTRE[1],
        LENS_CENTRE[0] - MASK_RADIUS_ARCSEC / PIXEL_SCALE - 6,
        f'{MASK_RADIUS_ARCSEC}" mask',
        color="cyan",
        fontsize=10,
        ha="center",
    )

for ax in axes:
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

figure.subplots_adjust(left=0.005, right=0.995, top=0.94, bottom=0.01, wspace=0.02)
"""110 dpi gives a ~1500 pixel wide figure — comfortably sharp at the 900 pixel
width the README displays it at, without the noise-dominated panels bloating the
committed PNG."""

figure.savefig(OUTPUT_PATH, dpi=110, facecolor="white")

print(f"Figure written to: {OUTPUT_PATH.resolve()}")
