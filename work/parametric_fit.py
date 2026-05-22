"""
Parametric strong-lens fit of the COSMOS-Web Einstein ring (F277W band).

Stage A model:
    Lens galaxy   : Sersic light + Isothermal mass + ExternalShear
    Source galaxy : SersicCore light

The source is a single smooth Sersic — this will not capture clumpy
substructure but is fast, robust, and is the standard starting point
for nailing down the lens mass model. A pixelised-source upgrade comes
in a later stage.

Smoke-test:
    PYAUTO_TEST_MODE=1 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \\
      python work/parametric_fit.py

Production run (no PYAUTO_TEST_MODE):
    NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \\
      python work/parametric_fit.py
"""
import json
from pathlib import Path

import autofit as af
import autolens as al


DATASET_PATH = Path("dataset/imaging/cosmos_web_ring/wavebands/F277W")
EXTRA_MASK_PATH = DATASET_PATH / "mask_extra_galaxies.fits"
info = json.loads((DATASET_PATH / "info.json").read_text())
PIXEL_SCALE = info["pixel_scale"]
LENS_REDSHIFT = info["redshift_lens"]
SOURCE_REDSHIFT = info["redshift_source"]
MASK_RADIUS = 3.0  # arcsec — leaves a margin from the extended masked region near y=-3.5"


dataset = al.Imaging.from_fits(
    data_path=DATASET_PATH / "data.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    psf_path=DATASET_PATH / "psf.fits",
    pixel_scales=PIXEL_SCALE,
)

mask = al.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=MASK_RADIUS,
)
dataset = dataset.apply_mask(mask=mask)

# Apply adaptive over-sampling: fine sub-grid near the centre where light
# profiles are steep, coarse elsewhere.
over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[8, 4, 1],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)
dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

# Inflate noise on extra-galaxy pixels so the fit ignores them.
mask_extra_galaxies = al.Mask2D.from_fits(
    file_path=EXTRA_MASK_PATH,
    pixel_scales=PIXEL_SCALE,
    invert=False,
)
dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)

# Lens galaxy: Sersic light, Isothermal mass, External shear.
lens = af.Model(
    al.Galaxy,
    redshift=LENS_REDSHIFT,
    bulge=af.Model(al.lp.Sersic),
    mass=af.Model(al.mp.Isothermal),
    shear=af.Model(al.mp.ExternalShear),
)

# Source galaxy: single SersicCore profile.
source = af.Model(
    al.Galaxy,
    redshift=SOURCE_REDSHIFT,
    bulge=af.Model(al.lp.SersicCore),
)

model = af.Collection(galaxies=af.Collection(lens=lens, source=source))

print(model.info)

analysis = al.AnalysisImaging(dataset=dataset)

search = af.Nautilus(
    path_prefix="imaging/cosmos_web_ring/F277W",
    name="parametric_sie_sersic",
    n_live=100,
    number_of_cores=4,
)

result = search.fit(model=model, analysis=analysis)

print("Max log-likelihood parameters:")
print(result.max_log_likelihood_instance)

# Plot the fit (data / model / residuals) and the best-fit tracer
# (lens image, source-plane image with caustics, deflection field).
import autolens.plot as aplt

PLOT_DIR = Path("work/plots/cosmos_web_ring")
PLOT_DIR.mkdir(parents=True, exist_ok=True)

tracer = result.max_log_likelihood_tracer
fit = al.FitImaging(dataset=dataset, tracer=tracer)

aplt.subplot_fit_imaging(
    fit=fit,
    output_path=str(PLOT_DIR),
    output_format="png",
)

aplt.subplot_tracer(
    tracer=tracer,
    grid=dataset.grid,
    output_path=str(PLOT_DIR),
    output_format="png",
)

print(f"Plots saved under: {PLOT_DIR.resolve()}")
