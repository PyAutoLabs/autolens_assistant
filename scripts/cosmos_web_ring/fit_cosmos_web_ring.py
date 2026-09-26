"""
Lens Model: COSMOS-Web Ring (JWST NIRCam)
=========================================

Fit the COSMOS-Web Ring, a complete Einstein ring imaged by JWST in the COSMOS-Web survey
(Mercier et al. 2024, arXiv:2309.15986) and part of the COWLS lens sample (Nightingale et al.
2025, arXiv:2503.08777). A massive galaxy at redshift z ~ 2 bends the light of a galaxy at
z ~ 5.1 into an almost perfect circle.

The script reproduces exactly what the assistant's public starting prompt asks for: prepare
the F444W imaging as the assistant recommends (extra-galaxy noise scaling, a 1.8" circular
mask, adaptive over-sampling), fit a Multi-Gaussian-Expansion (MGE) lens light, an
isothermal mass plus external shear and an MGE source with the fast JAX multi-start
gradient optimiser `MultiStartProdigy`, then write the numbers and the figures a reader needs
to judge the fit. It is the reference fit behind the `cosmos-web-ring-fit` benchmark card.

Usage (from the repository root)::

    python scripts/cosmos_web_ring/fit_cosmos_web_ring.py                       # good fit, F444W
    python scripts/cosmos_web_ring/fit_cosmos_web_ring.py --variant sersic_source
    python scripts/cosmos_web_ring/fit_cosmos_web_ring.py --band F277W          # achromatic check
    python scripts/cosmos_web_ring/fit_cosmos_web_ring.py --test-mode           # seconds, for tests

__Contents__

- **Imports:** Import the required libraries and parse the command-line options.
- **Dataset:** Load the JWST imaging of one waveband and its redshifts.
- **Extra Galaxy Noise Scaling:** Down-weight light from galaxies unrelated to the lens.
- **Masking:** Apply the 1.8" circular mask and adaptive over-sampling.
- **Model:** Compose the lens light, mass, external shear and source (and the poorer variants).
- **Search:** Configure the `MultiStartProdigy` optimiser.
- **Fit:** Run the fit on JAX and time it.
- **Einstein Mass:** Convert the Einstein radius into a mass in solar masses.
- **Summary:** Write `summary.json` with the numbers and the provenance.
- **Plots:** Save the fit subplot, the source reconstruction and the tracer figures.
"""

"""
__Imports__

`jax_wrapper` must be imported before JAX is used anywhere else: it sets the JAX environment
(64-bit precision) the likelihood relies on. The variant switches exist so the reference
"poor" fits a user could plausibly obtain are produced by the same script as the good one.
"""
from autolens import (
    jax_wrapper,
)  # noqa: F401  Sets the JAX environment before other imports

import argparse
import json
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import jax
import numpy as np
from astropy.io import fits

import autofit as af
import autolens as al
import autolens.plot as aplt
from autolens.lens.plot.tracer_plots import plane_image_from

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

VARIANTS = ("good", "sersic_source", "no_noise_scaling", "sersic_lens_light")
BANDS = ("F444W", "F277W")

parser = argparse.ArgumentParser(description="Fit the COSMOS-Web Ring JWST imaging.")
parser.add_argument("--variant", choices=VARIANTS, default="good")
parser.add_argument("--band", choices=BANDS, default="F444W")
parser.add_argument(
    "--test-mode",
    action="store_true",
    help="Tiny search (4 starts x 20 steps) for tests; the numbers are not science.",
)
parser.add_argument("--results-dir", type=Path, default=None)
parser.add_argument("--output-dir", type=Path, default=SCRIPT_DIR / "output")
args = parser.parse_args()

label = args.variant if args.band == "F444W" else f"{args.variant}_{args.band}"
if args.test_mode:
    label = f"test_mode_{label}"
results_dir = args.results_dir or SCRIPT_DIR / "results" / label
results_dir.mkdir(parents=True, exist_ok=True)

"""
__Dataset__

The ring was imaged by JWST/NIRCam in four bands (F115W, F150W, F277W, F444W); this assistant
ships all four under `dataset/imaging/cosmos_web_ring/wavebands/`. F444W and F277W share a
0.06" pixel scale. Each band folder holds the image, the per-pixel RMS noise-map, the PSF and a
mask marking extra galaxies; `info.json` gives the lens and source redshifts.

`al.Imaging.from_fits` (`PyAutoArray:autoarray/dataset/imaging/dataset.py`) normalises the PSF
to unit sum by default (`use_normalized_psf=True`). The shipped PSFs sum to about 0.97, so the
normalisation matters: without it the model would be systematically about 3% too faint. The
assertion below makes the normalisation explicit rather than assumed.
"""
dataset_path = (
    REPO_ROOT / "dataset" / "imaging" / "cosmos_web_ring" / "wavebands" / args.band
)
info = json.loads((dataset_path / "info.json").read_text())
pixel_scale = info["pixel_scale"]
redshift_lens = info["redshift_lens"]
redshift_source = info["redshift_source"]

dataset = al.Imaging.from_fits(
    data_path=dataset_path / "data.fits",
    psf_path=dataset_path / "psf.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    pixel_scales=pixel_scale,
)
psf_sum_on_disk = float(np.sum(fits.getdata(dataset_path / "psf.fits")))
psf_sum = float(np.sum(np.asarray(dataset.psf.kernel)))
assert abs(psf_sum - 1.0) < 1.0e-6, f"PSF is not normalised (sum={psf_sum})"

"""
__Extra Galaxy Noise Scaling__

Light from galaxies unrelated to the lens would otherwise be fitted by the lens or source model
and bias it. `apply_noise_scaling` (`PyAutoArray:autoarray/dataset/imaging/dataset.py`) sets the
noise of the pixels flagged in `mask_extra_galaxies.fits` to a very large value, so they carry
no weight in the likelihood. This is the preparation `skills/al_prepare_imaging_data.md`
recommends. The `no_noise_scaling` variant skips it, which is the mistake a user makes when
they load only the image, noise-map and PSF.
"""
noise_scaling_applied = args.variant != "no_noise_scaling"
if noise_scaling_applied:
    mask_extra_galaxies = al.Mask2D.from_fits(
        file_path=dataset_path / "mask_extra_galaxies.fits",
        pixel_scales=dataset.pixel_scales,
        invert=True,
    )
    dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)

"""
__Masking__

A 1.8" circular mask encloses the lens galaxy and the whole ring while excluding most empty
sky (the radius documented for this dataset in the assistant's README). Adaptive over-sampling
evaluates the light profiles on a finer sub-grid near the centre, where the lens light is
steep, and coarser further out (`PyAutoArray:autoarray/operators/over_sampling/`).
"""
mask_radius = 1.8

mask = al.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=mask_radius,
)
dataset = dataset.apply_mask(mask=mask)
n_masked_pixels = int(mask.pixels_in_mask)

over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[4, 2, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)
dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

"""
__Model__

The good model is the assistant's recommended starting point
(`autolens_workspace:scripts/imaging/start_here.py`, `skills/al_build_imaging_model.md`):

- Lens light: an MGE of 20 Gaussians with shared centre and ellipticity, whose intensities are
  solved linearly (`al.model_util.mge_model_from`, `PyAutoGalaxy:autogalaxy/analysis/model_util.py`).
- Lens mass: a singular isothermal ellipsoid (`al.mp.Isothermal`).
- External shear from the lens environment, held in an `al.MassField` passed via `fields=`.
- Source light: a second 20-Gaussian MGE, flexible enough for the clumpy z ~ 5 source.

__Priors__ The library's default Isothermal prior on `einstein_radius` is uniform over 0-8" and
the default shear priors are uniform over -0.3 to 0.3. With a 1.8" mask those defaults let the
optimiser settle in a degenerate basin: a first run of this script with them converged to
theta_E = 2.40" (larger than the mask), a shear of 0.27 and the source placed outside the caustic,
so no ring was modelled at all (reduced chi-squared 9.3; see `results/README.md`). The priors
below encode what anyone looking at the image knows before fitting: the ring (radius ~0.8") lies
well inside the mask, so `einstein_radius` is uniform over 0.3-1.5"; the environment is a modest
perturbation, so each shear component is uniform over -0.15 to 0.15. The mass centre keeps its
default Gaussian prior (mean 0, sigma 0.1") on the lens light centre at the origin, and the
source MGE centre is Gaussian (mean 0, sigma 0.3"), which `mge_model_from` sets when
`centre_prior_is_uniform=False`. Prior customisation follows `skills/al_build_imaging_model.md`.

The one compact companion galaxy inside the mask (north-east of the ring, at about y=+1.14",
x=+0.48", signal-to-noise ~30) is already covered by the bundled `mask_extra_galaxies.fits`, so
its light is down-weighted by the noise scaling above, not modelled.

The three poorer variants each change one choice a user could plausibly make:
`sersic_source` asks for "a simple source" (one linear Sérsic), `sersic_lens_light` models the
lens light with one linear Sérsic, and `no_noise_scaling` skips the extra-galaxy preparation.
"""
if args.variant == "sersic_lens_light":
    lens_bulge = af.Model(al.lp_linear.Sersic)
else:
    lens_bulge = al.model_util.mge_model_from(
        mask_radius=mask_radius,
        total_gaussians=20,
        centre_prior_is_uniform=True,
        sigma_min=dataset.pixel_scales[0] / 10.0,
    )

mass = af.Model(al.mp.Isothermal)
mass.einstein_radius = af.UniformPrior(lower_limit=0.3, upper_limit=1.5)
mass.centre.centre_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
mass.centre.centre_1 = af.GaussianPrior(mean=0.0, sigma=0.1)

shear = af.Model(al.mp.ExternalShear)
shear.gamma_1 = af.UniformPrior(lower_limit=-0.15, upper_limit=0.15)
shear.gamma_2 = af.UniformPrior(lower_limit=-0.15, upper_limit=0.15)

lens = af.Model(al.Galaxy, redshift=redshift_lens, bulge=lens_bulge, mass=mass)
field = af.Model(al.MassField, redshift=redshift_lens, shear=shear)

if args.variant == "sersic_source":
    source_bulge = af.Model(al.lp_linear.Sersic)
else:
    source_bulge = al.model_util.mge_model_from(
        mask_radius=mask_radius, total_gaussians=20, centre_prior_is_uniform=False
    )

source = af.Model(al.Galaxy, redshift=redshift_source, bulge=source_bulge)

model = af.Collection(galaxies=af.Collection(lens=lens, source=source), fields=field)
print(model.info)

"""
__Search__

`MultiStartProdigy` (`PyAutoFit:autofit/non_linear/search/mle/multi_start_gradient/search.py`)
launches `n_starts` gradient descents from broad starting points, all batched on JAX with
`jax.vmap`, and returns the best. Many starts guard against the local maxima of lens-model
parameter spaces (the GIGA-Lens approach, Gu et al. 2022, arXiv:2202.07663); Prodigy
(Mishchenko & Defazio 2024, arXiv:2306.06101) sets its own step size. It is a maximum a
posteriori optimiser: the fit gives one best model and no uncertainties
(`skills/al_configure_search.md`).
"""
n_starts, n_steps = (4, 20) if args.test_mode else (48, 300)

af.conf.instance.output_path = str(args.output_dir)

search = af.MultiStartProdigy(
    path_prefix=Path("cosmos_web_ring"),
    name="test_mode" if args.test_mode else "fit",
    unique_tag=label,
    n_starts=n_starts,
    batch_size=None,
    n_steps=n_steps,
    iterations_per_quick_update=10_000,  # No mid-fit visualisation: this is a timed run.
)

analysis = al.AnalysisImaging(dataset=dataset, use_jax=True)

"""
__Fit__

The first likelihood evaluation compiles the likelihood and its gradient with JAX, so the wall
time below includes compilation. On an RTX 2060 GPU the good fit takes about 7.5 minutes, most
of it compilation. On a CPU-only machine expect a much longer first compile (more than 20
minutes on the 8-core laptop the reference fits were made on, see `results/README.md`); for a
quick look, lower `n_starts` to 8.
"""
start = time.perf_counter()
result = search.fit(model=model, analysis=analysis)
wall_seconds = time.perf_counter() - start

print(result.info)

fit = result.max_log_likelihood_fit
tracer = result.max_log_likelihood_tracer
instance = result.instance

"""
__Einstein Mass__

The mass inside the Einstein radius follows from geometry alone: M_E = Sigma_crit x pi x
theta_E^2, where the critical surface density Sigma_crit depends only on the lens and source
redshifts through angular-diameter distances. `critical_surface_density_between_redshifts_from`
(`PyAutoGalaxy:autogalaxy/cosmology/model.py`, Planck15 cosmology) returns Sigma_crit in solar
masses per square arcsecond. We quote two versions:

- from the isothermal `einstein_radius` parameter (the number most papers quote), and
- from the effective Einstein radius of the tangential critical curve of the full tracer
  (mass plus shear), via `al.LensCalc.from_tracer(tracer).einstein_mass_angular_from`
  (`PyAutoGalaxy:autogalaxy/operate/lens_calc.py`).
"""
cosmology = al.cosmo.Planck15()
sigma_crit = float(
    cosmology.critical_surface_density_between_redshifts_from(
        redshift_0=redshift_lens, redshift_1=redshift_source
    )
)
kpc_per_arcsec = float(cosmology.kpc_per_arcsec_from(redshift=redshift_lens))

mass_instance = instance.galaxies.lens.mass
einstein_radius = float(mass_instance.einstein_radius)
einstein_mass = sigma_crit * np.pi * einstein_radius**2

evaluation_grid = al.Grid2D.uniform(shape_native=(200, 200), pixel_scales=0.03)
lens_calc = al.LensCalc.from_tracer(tracer)
try:
    einstein_radius_effective = float(
        lens_calc.einstein_radius_from(grid=evaluation_grid)
    )
    einstein_mass_effective = sigma_crit * float(
        lens_calc.einstein_mass_angular_from(grid=evaluation_grid)
    )
except Exception as exc:  # A test-mode fit may have no tangential critical curve.
    print(f"Effective Einstein radius unavailable: {exc}")
    einstein_radius_effective = None
    einstein_mass_effective = None

shear = instance.fields.shear

"""
__Summary__

`summary.json` records every number the results README and the benchmark truth quote, with
the provenance needed to reproduce them. The reduced chi-squared is the chi-squared over the
number of pixels inside the mask (no correction for the degrees of freedom of the model), the
definition the benchmark card uses.
"""
chi_squared = float(fit.chi_squared)


def _version(module_name):
    module = __import__(module_name)
    return getattr(module, "__version__", "unknown")


summary = {
    "variant": args.variant,
    "band": args.band,
    "test_mode": args.test_mode,
    "einstein_radius": einstein_radius,
    "einstein_radius_effective": einstein_radius_effective,
    "ell_comps": [float(v) for v in mass_instance.ell_comps],
    "centre": [float(v) for v in mass_instance.centre],
    "shear_gamma_1": float(shear.gamma_1),
    "shear_gamma_2": float(shear.gamma_2),
    "shear_magnitude": float(np.hypot(shear.gamma_1, shear.gamma_2)),
    "log_likelihood": float(fit.log_likelihood),
    "chi_squared": chi_squared,
    "n_masked_pixels": n_masked_pixels,
    "reduced_chi_squared": chi_squared / n_masked_pixels,
    "einstein_mass_solar_masses": einstein_mass,
    "einstein_mass_effective_solar_masses": einstein_mass_effective,
    "einstein_radius_kpc": einstein_radius * kpc_per_arcsec,
    "critical_surface_density_solar_mass_per_arcsec2": sigma_crit,
    "cosmology": "Planck15",
    "redshift_lens": redshift_lens,
    "redshift_source": redshift_source,
    "mask_radius": mask_radius,
    "noise_scaling_applied": noise_scaling_applied,
    "psf_sum_on_disk": psf_sum_on_disk,
    "wall_seconds": wall_seconds,
    "search": {
        "class": type(search).__name__,
        "n_starts": n_starts,
        "n_steps": n_steps,
        "batch_size": None,
        "use_jax": True,
    },
    "versions": {
        name: _version(name)
        for name in ("autolens", "autogalaxy", "autoarray", "autofit", "jax")
    },
    "jax_devices": [str(device) for device in jax.devices()],
    "thread_env": {
        name: os.environ.get(name)
        for name in (
            "JAX_PLATFORMS",
            "OMP_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "MKL_NUM_THREADS",
            "XLA_FLAGS",
        )
    },
    "cpu_count": os.cpu_count(),
    "machine": platform.platform(),
    "processor": platform.processor() or platform.machine(),
    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
}
(results_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

"""
__Plots__

Three figures, written with the function-style plot API (`skills/al_plot_fit_residuals.md`):

- `fit_subplot.png` — data, model, residuals, normalised residuals, chi-squared and source.
- `source.png` — the source galaxy's reconstructed light in its own (unlensed) plane.
- `tracer.png` — the lensed image, convergence, magnification and critical curves.
"""
aplt.subplot_fit_imaging(fit=fit, output_path=str(results_dir), output_format="png")
(results_dir / "fit.png").replace(results_dir / "fit_subplot.png")

source_image = plane_image_from(
    galaxies=[tracer.galaxies[1]], grid=fit.mask.derive_grid.all_false
)
aplt.plot_array(
    array=source_image,
    title="Source plane (unlensed)",
    output_path=str(results_dir),
    output_filename="source",
    output_format="png",
)
aplt.subplot_tracer(
    tracer=tracer,
    grid=dataset.grids.lp,
    output_path=str(results_dir),
    output_format="png",
)

print(json.dumps(summary, indent=2))
print(f"Results written to: {results_dir}")
