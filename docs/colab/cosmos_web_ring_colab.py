"""
The COSMOS-Web Ring: weighing a galaxy with light bent by gravity
=================================================================

This notebook fits a lens model to one of the most striking strong gravitational lenses known:
the **COSMOS-Web Ring**, a near-perfect circle of light imaged by the James Webb Space Telescope
(JWST). By the end you will have measured how much mass sits inside the ring, seen how well
the model reproduces the picture, and compared a good model with a not-so-good one.

It is the second of two ways to start with the PyAutoLens Assistant
(https://github.com/PyAutoLabs/autolens_assistant):

- **The agent route.** Open the assistant repository in Claude Code or Codex and paste the
  starting prompt below; the AI agent shows you the ring, asks your background and walks you
  through the same analysis in conversation.
- **This notebook.** The same analysis, written out step by step with the PyAutoLens code
  visible. It is the route to take if you are learning PyAutoLens and want to see the API.

The assistant's starting prompt is:

> I want to use the PyAutoLens Assistant: https://github.com/PyAutoLabs/autolens_assistant
> I'd like to understand how gravitational lensing works using the JWST image of the
> COSMOS-Web Ring that ships with the assistant. Show me the picture, explain what we are
> looking at, and walk me through fitting a lens model so we can measure the mass inside the
> ring and see how well the model reproduces the observations. Pitch it at my level: ask me
> what my background is first. Explain what we are doing as we go, and let me ask questions or
> change the analysis along the way.

The notebook is written for a general reader first. Short **For the scientist** asides add
the technical detail. Every section ends with a question you can ask Google Colab's built-in
AI, Gemini (the sparkle button in the Colab toolbar), if you want to go deeper.

__Contents__

- **Google Colab Setup:** Install PyAutoLens and download the data (a no-op outside Colab).
- **Imports:** Load the libraries.
- **What Is A Strong Lens?:** The idea in a paragraph.
- **The Picture:** Load the JWST image and look at what it shows.
- **Four Colours, One Ring:** Why the ring looks the same in every JWST colour.
- **Preparing The Data:** Down-weight a neighbouring galaxy, mask the image, set the resolution.
- **The Model:** Describe the lens galaxy, its mass and the background galaxy in code.
- **The Fit:** Find the model that best reproduces the image.
- **The Mass Inside The Ring:** Turn the ring's size into a mass in Suns.
- **Good Versus Not-Great:** Fit a simpler model and learn to read the residuals.
- **Where Next:** The agent route, HowToLens, the COWLS sample and error bars.

__Google Colab Setup__

The cell below sets up Google Colab: it installs PyAutoLens and clones the `autolens_workspace`
repository, which ships the COSMOS-Web Ring data, then moves into it. Outside Colab (on your own
computer, with PyAutoLens installed) it only checks your environment and changes nothing.

Tip: the fits below take a few minutes on a Colab GPU and much longer on a CPU. Before running,
choose **Runtime → Change runtime type → GPU** (a T4 is fine).
"""

try:
    import google.colab
except ImportError:
    from autolens import setup_colab as _setup_colab
else:
    import importlib
    import subprocess
    import sys

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "autonerves", "--no-deps"]
    )
    _setup_colab = importlib.import_module("autonerves.setup_colab")

_setup_colab.setup(
    "autolens", raise_error_if_not_gpu=False  # Set True to insist on a Colab GPU.
)

"""
__Imports__

`jax_wrapper` must be imported first: it configures JAX, the library that makes the fit fast
(and runs it on the GPU when there is one).
"""
from autolens import jax_wrapper  # noqa: F401  Sets the JAX environment before other imports

import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import autofit as af
import autolens as al
import autolens.plot as aplt
from autolens.lens.plot.tracer_plots import plane_image_from

"""
__What Is A Strong Lens?__

Mass bends light. Einstein's general relativity says that a massive object curves the space
around it, so light passing close by is deflected, just as a glass lens deflects light.
When a massive galaxy sits almost exactly in front of a more distant one, the light of the
distant galaxy is bent around it and reaches us along several paths. We see the background
galaxy stretched into arcs, or, when the alignment is nearly perfect, into a complete circle
called an **Einstein ring**.

The size of that ring depends on how much mass the foreground galaxy holds. Measuring the
ring therefore weighs the galaxy, including its dark matter, which gives off no light at all.

**For the scientist.** The ring's angular radius is the Einstein radius, θ_E. For a
circularly symmetric lens the mass inside it is M_E = Σ_crit π θ_E², where the critical surface
density Σ_crit depends only on the angular-diameter distances to the lens and the source. Lens
modelling fits a parametric mass profile and a model of the unlensed source to every pixel of
the image, rather than measuring the ring by eye.

Ask Gemini: "How does a galaxy's mass bend light, and why does perfect alignment make a ring?"
"""

"""
__The Picture__

The data come from the COSMOS-Web survey, the largest JWST imaging programme of its first year.
In the image below:

- **The lens galaxy** is the bright blob at the centre. It is a massive galaxy seen when the
  Universe was about 3 billion years old (redshift z ≈ 2.0).
- **The ring** is a single, much more distant galaxy (z ≈ 5.1, seen barely a billion years
  after the Big Bang) whose light has been bent into an almost complete circle.
- **An extra galaxy** just to the north-east of the ring is unrelated to the lens. We will stop
  it confusing the fit below.
- **The 1.8" circular mask** (1.8 arcseconds, a tiny patch of sky) marks the region we fit:
  it encloses the lens and the whole ring and leaves out most of the empty sky.

Each dataset has three parts: the image itself, a **noise-map** (how uncertain each pixel's
brightness is) and the **PSF** (point spread function: how the telescope blurs a point of
light). The code finds the data whether you are in Colab (inside `autolens_workspace`) or
running from the root of the assistant repository.

**For the scientist.** JWST/NIRCam imaging in four bands (F115W, F150W, F277W, F444W). F444W
and F277W have 0.06" pixels. The redshifts are z_lens = 2.0 and z_source = 5.1043, from
Mercier et al. 2024 (arXiv:2309.15986). `al.Imaging.from_fits` normalises the PSF to unit sum
on load.
"""
dataset_root = Path("dataset") / "imaging" / "cosmos_web_ring"

if not dataset_root.exists():
    raise FileNotFoundError(
        f"{dataset_root} not found: run this notebook in Colab, or from the root of the "
        "autolens_assistant or autolens_workspace repository."
    )


def band_path(band):
    """
    The folder holding one JWST band. The top-level autolens_workspace folder is F444W;
    every band, in both repositories, lives under `wavebands/<band>/`.
    """
    if band == "F444W" and (dataset_root / "data.fits").exists():
        return dataset_root  # autolens_workspace layout (Colab)
    return dataset_root / "wavebands" / band  # autolens_assistant layout


pixel_scale = 0.06
redshift_lens = 2.0
redshift_source = 5.1043


def load_band(band):
    path = band_path(band)
    return al.Imaging.from_fits(
        data_path=path / "data.fits",
        psf_path=path / "psf.fits",
        noise_map_path=path / "noise_map.fits",
        pixel_scales=pixel_scale,
    )


dataset = load_band("F444W")
aplt.subplot_imaging_dataset(dataset=dataset)

"""
Ask Gemini: "What is a redshift, and how do astronomers know the ring galaxy is at z = 5.1?"

__Four Colours, One Ring__

JWST imaged the ring in four colours of infrared light: F115W, F150W, F277W and F444W (the
number is the wavelength in hundredths of a micron, so F444W is light of about 4.4 microns).
Below are F277W and F444W side by side. The lens galaxy and the ring change in brightness from
one colour to the other, but the ring has **the same shape and size**.

That is because gravitational lensing is **achromatic**: gravity bends light of every
wavelength by exactly the same amount. Colour tells us what the galaxies are made of; the
geometry of the ring tells us about mass.

This is also something you can measure. Fitting the same model independently to each band gave
an Einstein radius of 0.803" in F444W and 0.801" in F277W (0.775" and 0.772" for the effective
radius of the critical curve), the same to 0.2%, less than a twentieth of a pixel (recorded in
`scripts/cosmos_web_ring/results/README.md` of the assistant repository).

**For the scientist.** Achromaticity is why multi-band lens modelling can share one mass model
across bands while each band gets its own lens-light and source-light model. Colour gradients
in the source do change the ring's surface brightness from band to band, which is why the
images differ in detail even though the lensing is identical.
"""
dataset_f277w = load_band("F277W")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
aplt.plot_array(array=dataset_f277w.data, title="F277W (2.8 microns)", ax=axes[0])
aplt.plot_array(array=dataset.data, title="F444W (4.4 microns)", ax=axes[1])
plt.tight_layout()
plt.show()

"""
Ask Gemini: "Why does the ring look the same in every colour, when the galaxies themselves change colour?"

__Preparing The Data__

Three steps get the image ready for fitting.

1. **Down-weight the extra galaxy.** A file shipped with the data, `mask_extra_galaxies.fits`,
   marks the pixels covered by galaxies that have nothing to do with the lens. We give those
   pixels an enormous noise value, which tells the fit "ignore these". Without this step, the
   model would bend itself out of shape trying to explain light it has no business explaining.
2. **Mask.** Only the pixels inside the 1.8" circle are fitted.
3. **Over-sampling.** The lens galaxy's light rises steeply towards its centre, so near the
   centre each pixel is evaluated on a finer grid of sub-pixels, and on a coarser one further out.
   This keeps the model accurate where it matters without slowing it down everywhere.

**For the scientist.** `apply_noise_scaling` sets the noise of the flagged pixels to a large
value so they carry no weight in the χ², and `over_sample_size_via_radial_bins_from` uses 4×4
sub-pixels within 0.3" of the centre and 2×2 beyond. These mirror the assistant's reference fit
(`scripts/cosmos_web_ring/fit_cosmos_web_ring.py`).
"""
mask_radius = 1.8


def prepare(dataset, band):
    mask_extra_galaxies = al.Mask2D.from_fits(
        file_path=band_path(band) / "mask_extra_galaxies.fits",
        pixel_scales=dataset.pixel_scales,
        invert=True,
    )
    dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)

    mask = al.Mask2D.circular(
        shape_native=dataset.shape_native,
        pixel_scales=dataset.pixel_scales,
        radius=mask_radius,
    )
    dataset = dataset.apply_mask(mask=mask)

    over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
        grid=dataset.grid,
        sub_size_list=[4, 2, 2],
        radial_list=[0.3, 0.6],
        centre_list=[(0.0, 0.0)],
    )
    return dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)


dataset = prepare(dataset, band="F444W")
n_masked_pixels = int(dataset.mask.pixels_in_mask)
aplt.subplot_imaging_dataset(dataset=dataset)

"""
Ask Gemini: "Why do astronomers mask out neighbouring galaxies before fitting a model to an image?"

__The Model__

A lens model is a description of the system in a handful of numbers. Ours has four pieces:

- **The lens galaxy's light.** The glow of the foreground galaxy, which sits on top of the ring
  and has to be modelled so it can be removed. We describe it as a sum of 20 smooth blobs of
  different sizes (a "Multi-Gaussian Expansion", MGE), which can take on almost any smooth shape.
- **The lens galaxy's mass.** An "isothermal" profile, whose density falls off with radius in
  the way that stars and dark matter together are observed to in massive galaxies. Its most
  important number is the **Einstein radius**, the size of the ring the mass produces.
- **External shear.** A gentle stretch from the galaxy's surroundings (neighbouring galaxies and
  large-scale structure).
- **The source galaxy's light.** The distant galaxy as it would look *without* lensing,
  described by another 20-blob MGE, flexible enough for a clumpy young galaxy.

The fit then asks: which values of these numbers, once the source's light is bent through the
lens and blurred by the telescope, best reproduce the image?

**Why the priors are bounded.** A "prior" is the range each number is allowed to explore. By
default the Einstein radius may be anything from 0 to 8" and each shear component anything
from -0.3 to 0.3. Left that free, the fit found a bad solution: an Einstein radius of 2.4",
larger than the mask, with the source placed where it makes no ring at all, so the whole ring
was left unexplained (reduced χ² 9.3; recorded in `scripts/cosmos_web_ring/results/README.md`). Anyone looking at
the picture already knows the ring's radius is under 1", well inside the mask, so we say so:
the Einstein radius is allowed 0.3" to 1.5", and each shear component -0.15 to 0.15.

**For the scientist.** Lens light: `al.model_util.mge_model_from` with 20 Gaussians sharing a
centre and ellipticity, intensities solved linearly. Mass: `al.mp.Isothermal` with a Gaussian
(σ = 0.1") prior on its centre. Shear: `al.mp.ExternalShear` in an `al.MassField` passed via
`fields=`. Source: a second 20-Gaussian MGE with a Gaussian (σ = 0.3") centre prior. The source
builder is a function so the same model can be refitted below with a simpler source.
"""


def model_from(source_type):
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

    if source_type == "sersic":
        source_bulge = af.Model(al.lp_linear.Sersic)
    else:
        source_bulge = al.model_util.mge_model_from(
            mask_radius=mask_radius, total_gaussians=20, centre_prior_is_uniform=False
        )

    source = af.Model(al.Galaxy, redshift=redshift_source, bulge=source_bulge)

    return af.Collection(galaxies=af.Collection(lens=lens, source=source), fields=field)


model = model_from(source_type="mge")
print(model.info)

"""
Ask Gemini: "What is an isothermal mass profile, and why is it a good first guess for a massive galaxy?"

__The Fit__

Finding the best numbers is a search through a space with dozens of dimensions. We use
`MultiStartProdigy`: it starts 48 searches from different places, lets each one walk downhill
towards a better fit for up to 300 steps (using gradients, the direction in which the fit
improves fastest), and keeps the best. Running many starts at once guards against a search
getting stuck on a poor solution.

This takes a few minutes on the Colab GPU: 448 s on the laptop GPU used to record the
reference numbers (recorded in `scripts/cosmos_web_ring/results/README.md`), and much longer
on a CPU. The first part of that time is JAX compiling the model; after that, each step is fast.

**For the scientist.** `use_jax=True` evaluates the likelihood and its gradient with JAX, and
`MultiStartProdigy` batches all starts with `jax.vmap` (the GIGA-Lens approach, Gu et al. 2022,
arXiv:2202.07663; Prodigy sets its own step size, Mishchenko & Defazio 2024, arXiv:2306.06101).
It is a maximum-likelihood optimiser: it returns one best model and **no uncertainties**.
"""


def fit_model(model, name):
    search = af.MultiStartProdigy(
        path_prefix=Path("cosmos_web_ring_colab"),
        name=name,
        n_starts=48,
        batch_size=None,
        n_steps=300,
        iterations_per_quick_update=10_000,  # No mid-fit visualisation.
    )
    analysis = al.AnalysisImaging(dataset=dataset, use_jax=True)

    start = time.perf_counter()
    result = search.fit(model=model, analysis=analysis)
    print(f"Fit '{name}' took {time.perf_counter() - start:.0f} s.")
    return result


result = fit_model(model=model, name="mge_source")
print(result.info)

"""
Now look at the fit. The panels show the data, the model image, the **residuals** (data minus
model) and the **normalised residuals** (residuals divided by the noise: values within about
±3 are what noise alone produces), the χ² map, and the reconstructed source.

A good fit leaves residuals that look like noise: no ring, no blobs, no structure.

**For the scientist.** The reduced χ² printed below is χ² divided by the number of pixels in
the mask, with no correction for the model's degrees of freedom. The recorded good fit has
0.62; a value below 1 suggests the bundled noise-map is somewhat conservative.
"""
fit = result.max_log_likelihood_fit
tracer = result.max_log_likelihood_tracer

aplt.subplot_fit_imaging(fit=fit)

reduced_chi_squared = float(fit.chi_squared) / n_masked_pixels
print(f"Reduced chi-squared: {reduced_chi_squared:.2f}")

"""
And here is the payoff of lens modelling: the distant galaxy as it would look if the lens were
not there, a galaxy seen when the Universe was barely a billion years old, magnified for us by
a natural telescope.
"""
source_image = plane_image_from(
    galaxies=[tracer.galaxies[1]], grid=fit.mask.derive_grid.all_false
)
aplt.plot_array(array=source_image, title="The source galaxy, unlensed")

"""
Ask Gemini: "In a lens model fit, what do the normalised residuals tell me, and what would a bad fit look like?"

__The Mass Inside The Ring__

The Einstein radius is the ring's size in the sky. Combined with the distances to the two
galaxies (which follow from their redshifts), it gives the mass enclosed by the ring, in units
of the Sun's mass.

The reference fit found an Einstein radius of 0.803", about 6.9 kiloparsecs (some 22,000
light years) at the lens, enclosing about 4.2 × 10¹¹ solar masses: **roughly four hundred
billion Suns**, most of it stars and dark matter (recorded in
`scripts/cosmos_web_ring/results/README.md`). Your numbers below should agree closely.

**For the scientist.** M_E = Σ_crit π θ_E², with Σ_crit from the Planck15 cosmology. We quote
the isothermal `einstein_radius` parameter and the effective Einstein radius of the tangential
critical curve of the full tracer (mass plus shear), the quantity Mercier et al. 2024
(arXiv:2309.15986) quote: θ_E = 0.78 ± 0.04" (0.77" with PyAutoLens), for which the recorded
fit gives 0.775" and 3.9 × 10¹¹ solar masses. The recorded shear magnitude is 0.12.
"""
cosmology = al.cosmo.Planck15()
sigma_crit = float(
    cosmology.critical_surface_density_between_redshifts_from(
        redshift_0=redshift_lens, redshift_1=redshift_source
    )
)
kpc_per_arcsec = float(cosmology.kpc_per_arcsec_from(redshift=redshift_lens))

instance = result.instance
einstein_radius = float(instance.galaxies.lens.mass.einstein_radius)
einstein_mass = sigma_crit * np.pi * einstein_radius**2
shear = instance.fields.shear

print(f"Einstein radius: {einstein_radius:.3f} arcsec")
print(f"  = {einstein_radius * kpc_per_arcsec:.1f} kpc at the lens")
print(f"Mass inside the Einstein radius: {einstein_mass:.2e} solar masses")
print(f"  = about {einstein_mass / 1e11:.0f} hundred billion Suns")
print(f"Shear magnitude: {float(np.hypot(shear.gamma_1, shear.gamma_2)):.2f}")

evaluation_grid = al.Grid2D.uniform(shape_native=(200, 200), pixel_scales=0.03)
lens_calc = al.LensCalc.from_tracer(tracer)
try:
    einstein_radius_effective = float(lens_calc.einstein_radius_from(grid=evaluation_grid))
    einstein_mass_effective = sigma_crit * float(
        lens_calc.einstein_mass_angular_from(grid=evaluation_grid)
    )
    print(f"Effective Einstein radius (critical curve): {einstein_radius_effective:.3f} arcsec")
    print(f"Mass inside it: {einstein_mass_effective:.2e} solar masses")
except Exception as exc:  # A poorly converged fit may have no tangential critical curve.
    print(f"Effective Einstein radius unavailable: {exc}")

"""
Ask Gemini: "How can a mass measurement from a lens include dark matter that we cannot see?"

__Good Versus Not-Great__

How do you know a fit is good? Compare it with a worse one. Here we refit with one change: the
source galaxy is described by a single smooth profile (a "Sérsic" profile) instead of 20
blobs. This is what you get by asking for "a simple source", and it is a mistake that is easy
to make, because the headline number still looks fine.

The recorded fit with a single Sérsic source found an Einstein radius of 0.755", close to the
good fit's 0.803", but a reduced χ² of 2.88 against 0.62 (recorded in
`scripts/cosmos_web_ring/results/README.md`). Look at its residuals below: the model ring is
smooth, and the **two bright knots** of the real source, together with structure around the
ring, are left behind. The distant galaxy is clumpy, and a smooth profile cannot describe it.

That is the lesson: a plausible-looking Einstein radius is not enough. Residuals with structure
mean the model is missing something real, and the numbers it gives may be biased.

**For the scientist.** A mismatched source model is compensated by the mass model, which is
why the Einstein radius moves by about 6% here. Residuals that trace the ring point to the
source (or the mass); residuals centred on the lens point to the lens-light model.
"""
model_sersic = model_from(source_type="sersic")
result_sersic = fit_model(model=model_sersic, name="sersic_source")

fit_sersic = result_sersic.max_log_likelihood_fit
aplt.subplot_fit_imaging(fit=fit_sersic)

einstein_radius_sersic = float(result_sersic.instance.galaxies.lens.mass.einstein_radius)
print(f"Single Sersic source: Einstein radius {einstein_radius_sersic:.3f} arcsec, "
      f"reduced chi-squared {float(fit_sersic.chi_squared) / n_masked_pixels:.2f}")
print(f"MGE source:           Einstein radius {einstein_radius:.3f} arcsec, "
      f"reduced chi-squared {reduced_chi_squared:.2f}")

"""
Ask Gemini: "Why can a model with the right Einstein radius still be a bad fit, and how do residuals reveal it?"

__Where Next__

- **The agent route.** Open https://github.com/PyAutoLabs/autolens_assistant in Claude Code or
  Codex and paste the assistant starting prompt quoted at the top of this notebook. You can then
  change this analysis in plain language: "fit F277W as well", "try a pixelized source",
  "add a second lens galaxy".
- **HowToLens** (https://github.com/PyAutoLabs/HowToLens), the lecture series that teaches
  strong lensing and PyAutoLens from first principles.
- **COWLS**, the COSMOS-Web Lens Survey, of which this ring is one lens: Nightingale et al. 2025,
  arXiv:2503.08777.
- **The discovery paper**: Mercier et al. 2024, arXiv:2309.15986.

**A caveat.** Both fits here are maximum-likelihood fits: each gives one best model and no
error bars. To measure uncertainties, fit the same model with a nested sampler (Nautilus), as
shown in `scripts/imaging/modeling.py` of the `autolens_workspace`; the Einstein radius then
comes with a range, such as the ±0.04" of Mercier et al.

Ask Gemini: "What is the difference between a maximum-likelihood fit and a posterior, and why do error bars need a sampler?"
"""
