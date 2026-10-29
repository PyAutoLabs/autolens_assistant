"""
COSMOS-Web Ring Colab Figures
=============================

Builds the introductory dataset and band-comparison figures, plus the two model figures the Colab notebook (`docs/colab/cosmos_web_ring_colab.py`) shows
*before* the code that computes them, so a reader sees the result of a section the moment they
open it: the good lens model's pieces ("The Model") and its Einstein radius
("The Mass Inside The Ring"). The model figures come from evaluating the committed model under
`scripts/cosmos_web_ring/results/` exactly as the notebook does, so the pictures and the
notebook's executed output agree. Run from the repository root (`make colab` runs it first)::

    python docs/colab/make_colab_figures.py

__Contents__

- **Imports:** Import the required libraries.
- **Dataset:** Load F444W and prepare it as the notebook does (noise scaling, 2.1" mask, over-sampling).
- **Model:** Evaluate the good (cowls_ansofi) tracer.
- **Figures:** Save the good model's plane subplot and Einstein radius.
"""

"""
__Imports__

`jax_wrapper` first, as in every PyAutoLens script; matplotlib is switched to the non-interactive
`Agg` backend because this script only writes files.
"""
from autolens import jax_wrapper  # noqa: F401  Sets the JAX environment before other imports

import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from PIL import Image

import autolens as al
import autolens.plot as aplt

REPO_PATH = Path(__file__).resolve().parents[2]
BAND_PATH = REPO_PATH / "dataset" / "imaging" / "cosmos_web_ring" / "wavebands" / "F444W"
RESULTS_PATH = REPO_PATH / "scripts" / "cosmos_web_ring" / "results"
IMAGES_PATH = REPO_PATH / "docs" / "images"

PIXEL_SCALE = 0.06
MASK_RADIUS = 2.1

"""
__Dataset__

The preparation of the notebook's "Preparing The Data" section: extra galaxies noise-scaled
before masking, a 2.1" circular mask (the good model's evaluation mask), and 4/2/2 radial
light-profile over-sampling about the centre.
"""
dataset = al.Imaging.from_fits(
    data_path=BAND_PATH / "data.fits",
    psf_path=BAND_PATH / "psf.fits",
    noise_map_path=BAND_PATH / "noise_map.fits",
    pixel_scales=PIXEL_SCALE,
)
aplt.subplot_imaging_dataset_intro(dataset, radius=2.5, output_path=IMAGES_PATH,
                   output_filename="cosmos_web_ring_intro", output_format="png")
comparison, comparison_axes = plt.subplots(1, 2, figsize=(11, 5), layout="constrained")
display_mask = al.Mask2D.circular(shape_native=dataset.shape_native,
                                  pixel_scales=PIXEL_SCALE, radius=2.5)
f150w = al.Array2D.from_fits(file_path=BAND_PATH.parent / "F150W" / "data.fits",
                           pixel_scales=0.03)
f150w = f150w.apply_mask(mask=al.Mask2D.circular(
    shape_native=f150w.shape_native, pixel_scales=f150w.pixel_scales, radius=2.5
))
aplt.plot_array(f150w, ax=comparison_axes[0], title="F150W (1.5 microns)", stretch=0.01)
aplt.plot_array(dataset.apply_mask(mask=display_mask).data, ax=comparison_axes[1],
                title="F444W (4.4 microns)", stretch=0.01)
comparison.savefig(IMAGES_PATH / "cosmos_web_ring_bands.png", dpi=150)
plt.close(comparison)

mask_extra_galaxies = al.Mask2D.from_fits(
    file_path=BAND_PATH / "mask_extra_galaxies.fits",
    pixel_scales=PIXEL_SCALE,
    invert=True,
)
dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)
mask = al.Mask2D.circular(
    shape_native=dataset.shape_native, pixel_scales=PIXEL_SCALE, radius=MASK_RADIUS
)
dataset = dataset.apply_mask(mask=mask)
aplt.subplot_imaging_dataset_intro(dataset, radius=2.5, output_path=IMAGES_PATH,
                   output_filename="cosmos_web_ring_prepared",
                   excluded_pixels=~mask_extra_galaxies.array, output_format="png")
over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[4, 2, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)
dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

"""
__Model__

The good model needs its pixelization over-sampling, source adapt image and source mesh grid
(see `scripts/cosmos_web_ring/results/README.md`).
"""


def masked_array_from(file_name):
    return al.Array2D(
        values=al.Array2D.from_fits(
            file_path=RESULTS_PATH / "ansofi" / file_name, pixel_scales=PIXEL_SCALE
        ).native,
        mask=mask,
    )


tracer = al.from_json(file_path=RESULTS_PATH / "ansofi" / "tracer.json")
source_galaxy = tracer.galaxies[1]
adapt_images = al.AdaptImages(
    galaxy_image_dict={source_galaxy: masked_array_from("source_adapt_image.fits")},
    galaxy_image_plane_mesh_grid_dict={
        source_galaxy: al.from_json(
            file_path=RESULTS_PATH / "ansofi" / "source_mesh_grid.json"
        )
    },
)
dataset_good = dataset.apply_over_sampling(
    over_sample_size_pixelization=masked_array_from("over_sample_size_pixelization.fits")
)
fit = al.FitImaging(dataset=dataset_good, tracer=tracer, adapt_images=adapt_images)

print(f"Good model figure of merit: {float(fit.figure_of_merit):.2f}")

"""
__Figures__

Both PNGs are Lanczos-resampled to 1600 pixels wide and palette-quantised, the convention of
`scripts/cosmos_web_ring/results/`, so they stay small in the repository and sharp at notebook
width. The editable model experiment is saved as executed output in the notebook.
"""


def save_small(source, destination, width=1600):
    image = Image.open(source).convert("RGB")
    height = round(image.height * width / image.width)
    image = image.resize((width, height), resample=Image.LANCZOS).quantize(256)
    image.save(destination, optimize=True)
    print(f"Figure written to: {destination}")


with tempfile.TemporaryDirectory() as tmp:
    aplt.subplot_fit_imaging_of_planes(
        fit=fit, plane_index=1, output_path=tmp, output_format="png"
    )
    save_small(
        Path(tmp) / "fit_of_plane_1.png", IMAGES_PATH / "cosmos_web_ring_good_model.png"
    )

    """
    The ring with the lens galaxy's light subtracted, and the good model's tangential critical
    curve on top: the curve the ring traces, whose effective radius is the Einstein radius the
    notebook turns into a mass.
    """
    evaluation_grid = al.Grid2D.uniform(shape_native=(200, 200), pixel_scales=0.03)
    lens_calc = al.LensCalc.from_tracer(tracer)
    critical_curves = lens_calc.tangential_critical_curve_list_from(grid=evaluation_grid)
    einstein_radius = float(lens_calc.einstein_radius_from(grid=evaluation_grid))
    figure, ax = plt.subplots(1, 1, figsize=(6, 5))
    aplt.plot_array(
        array=fit.subtracted_images_of_planes_list[1],
        title=f'Einstein radius {einstein_radius:.2f}"',
        lines=[curve.array for curve in critical_curves],
        line_colors=["white"] * len(critical_curves),
        ax=ax,
    )
    plt.tight_layout()
    einstein_path = Path(tmp) / "einstein.png"
    figure.savefig(einstein_path, dpi=150, facecolor="white")
    plt.close(figure)
    save_small(
        einstein_path, IMAGES_PATH / "cosmos_web_ring_einstein_radius.png", width=900
    )

