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
import matplotlib.patheffects as path_effects
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

Panels are labelled *inside* their own frame rather than with axis titles, which
lets the row butt right up against the figure edges — no band of white space
above the images — and leaves room for the label to be set large enough to stay
readable at the width the README displays it at.
"""

"""The panels abut with no gap at all — any spacing between them shows through as
a white line, since the figure background is what sits behind the axes. The
panels are square, so the figure height is then derived rather than guessed:
three panel widths fill the figure width, and one panel width is exactly the
height. Guessing it leaves a strip of white along an edge."""

FIGURE_WIDTH = 13.5

PANEL_WIDTH = FIGURE_WIDTH / 3.0

figure, axes = plt.subplots(1, 3, figsize=(FIGURE_WIDTH, PANEL_WIDTH))

"""Amber reads clearly against both the near-black RGB sky and the magma colour
map, and stays distinct from the two annotation colours already in play (white
for the arrow and scale bar, cyan for the mask). The dark stroke keeps it legible
where a label happens to fall over a bright source."""

LABEL_COLOR = "#ffc400"
LABEL_STROKE = [path_effects.withStroke(linewidth=3.0, foreground="black")]


def panel_label(ax, text):
    ax.text(
        7,
        11,
        text,
        color=LABEL_COLOR,
        fontsize=17,
        fontweight="bold",
        ha="left",
        va="top",
        path_effects=LABEL_STROKE,
    )


axes[0].imshow(rgb, interpolation="bicubic")
panel_label(axes[0], "RGB (COSMOS-Web)")

"""The RGB panel carries the newcomer's tour of the system: which blob is the
lens, which light is the lensed source, and which galaxy is neither. The three
labels are drawn in white to read as one annotation layer, distinct from the
amber panel titles and the cyan mask.
"""

ARROW_STYLE = dict(arrowstyle="-|>", color="white", lw=1.8, shrinkA=0, shrinkB=3)


def annotate_arrow(ax, text, tip, anchor, **kwargs):
    ax.annotate(
        text,
        xy=tip,
        xytext=anchor,
        color="white",
        fontsize=13,
        fontweight="bold",
        ha="center",
        path_effects=LABEL_STROKE,
        arrowprops=ARROW_STYLE,
        **kwargs,
    )


def ring_point(angle_degrees, radius=18.0):
    """A point on the Einstein ring, by angle anticlockwise from due east. The
    sine is negated because the panel's y axis runs downwards."""
    angle = np.radians(angle_degrees)
    return (
        LENS_CENTRE[1] + radius * np.cos(angle),
        LENS_CENTRE[0] - radius * np.sin(angle),
    )


"""Two arrows onto opposite sides of the ring, sharing one label. This is the
point of the figure for a newcomer: both arcs are the *same* background galaxy,
seen twice. They target the upper-left and upper-right of the ring, keeping clear
of the south-east arc where the extra galaxy sits blended with the emission —
measuring mean flux around the annulus, that sector is the brightest, but the
excess is the interloper rather than the source."""

axes[0].annotate("", xy=ring_point(135.0), xytext=(82, 40), arrowprops=ARROW_STYLE)
annotate_arrow(
    axes[0], "Lensed Source Galaxy", tip=ring_point(45.0), anchor=(82, 34), va="top"
)

"""The lens arrow has to cross the ring to reach the galaxy inside it. It comes
in from the south-west, the faintest sector of the annulus, so it cuts the ring
where there is least emission to obscure."""

annotate_arrow(axes[0], "Lens Galaxy", tip=LENS_CENTRE[::-1], anchor=(30, 122))

"""The extra-galaxy arrow points in from open sky to the south-east, so it never
crosses the lensed emission it is drawing attention to."""

annotate_arrow(
    axes[0],
    "Extra Galaxy",
    tip=(EXTRA_GALAXY_CENTRE[1] + 5, EXTRA_GALAXY_CENTRE[0] + 5),
    anchor=(133, 141),
)

scale_bar_pixels = 1.0 / PIXEL_SCALE
axes[0].plot(
    [12, 12 + scale_bar_pixels], [158, 158], color="white", lw=2.5, solid_capstyle="butt"
)
axes[0].text(
    12 + scale_bar_pixels / 2.0, 152, '1"', color="white", fontsize=12, ha="center"
)

for ax, band in zip(axes[1:], BANDS):

    ax.imshow(bands[band], origin="upper", cmap="magma", interpolation="bicubic")
    panel_label(ax, f"JWST {band}")

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
        fontsize=13,
        fontweight="bold",
        ha="center",
        path_effects=LABEL_STROKE,
    )

for ax in axes:
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

"""With the labels moved inside the panels there is nothing left to reserve
margin for, so the axes run to the figure edge and butt against each other."""

figure.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0, wspace=0.0)
"""110 dpi gives a ~1500 pixel wide figure — comfortably sharp at the 900 pixel
width the README displays it at, without the noise-dominated panels bloating the
committed PNG."""

figure.savefig(OUTPUT_PATH, dpi=110, facecolor="white")

print(f"Figure written to: {OUTPUT_PATH.resolve()}")
