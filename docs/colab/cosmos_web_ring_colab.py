"""
The COSMOS-Web Ring: weighing a galaxy with light bent by gravity
=================================================================

This notebook is a guided tour of one of the most striking strong gravitational lenses known:
the **COSMOS-Web Ring**, a near-perfect circle of light imaged by the James Webb Space Telescope
(JWST). By the end you will have seen how a lens model reproduces the picture, compared a good
model with a not-so-good one, and measured how much mass sits inside the ring.

**No fit is run in this notebook.** Finding a lens model takes minutes on a GPU and much longer
on a CPU, so the two models shown here were fitted in advance and are loaded from the assistant
repository; the notebook evaluates them on the data, which takes seconds. To run a fit yourself,
see **Where Next** at the end.

It is the second of two ways to start with the PyAutoLens Assistant
(https://github.com/PyAutoLabs/autolens_assistant):

- **The agent route.** Open Claude Code or Codex (in any folder) and paste the starting
  prompt below; the AI agent shows you the ring, asks your background and walks you
  through the same analysis in conversation.
- **This notebook.** The same analysis, written out step by step with the PyAutoLens code
  visible. It is the route to take if you are learning PyAutoLens and want to see the API.

The assistant's starting prompt is:

> I want to use the PyAutoLens Assistant: https://github.com/PyAutoLabs/autolens_assistant
> First clone that repository, cd into it and follow its AGENTS.md.
>
> I'd like to understand how gravitational lensing works using the JWST image of the COSMOS-Web Ring that ships with the assistant. Show me the picture, explain what we are looking at, and walk me through fitting a lens model so we can measure the mass inside the ring and see how well the model reproduces the observations. Pitch it at my level: ask me what my background is first. Explain what we are doing as we go, and let me ask questions or change the analysis along the way.

The notebook is written for a general reader first. Short **For the scientist** asides add
the technical detail. Every section ends with a question you can ask Google Colab's built-in
AI, Gemini (the sparkle button in the Colab toolbar), if you want to go deeper.

<!-- Maintainers: this notebook is generated from docs/colab/cosmos_web_ring_colab.py and committed
executed; rebuild it with `make colab` from the assistant repository root. The image URLs and the
results-download URL below point at `main`; switch them to the release tag at release, as the
README's Colab badge is. -->

__Contents__

- **Google Colab Setup:** Install PyAutoLens and download the data (a no-op outside Colab).
- **Imports:** Load the libraries.
- **What Is A Strong Lens?:** How a galaxy's gravity bends light into arcs and rings.
- **The Picture:** The JWST image of the ring, and the data we will work with.
- **Four Colours, One Ring:** Why the ring looks the same in every JWST colour.
- **Preparing The Data:** Down-weight a neighbouring galaxy, mask the image, set the resolution.
- **What A Lens Model Looks Like:** The published lens model of this ring, panel by panel.
- **The Model:** The four pieces of a lens model, and the good model loaded from file.
- **Good Versus Not-Great:** Evaluate the good model and a simpler one, and read the residuals.
- **The Mass Inside The Ring:** Turn the ring's size into a mass in Suns.
- **Where Next:** Run a fit yourself, the agent route, HowToLens, COWLS and error bars.

__Google Colab Setup__

The cell below sets up Google Colab: it installs PyAutoLens and clones the `autolens_workspace`
repository, which ships the COSMOS-Web Ring data, then moves into it. Outside Colab (on your own
computer, with PyAutoLens installed) it only checks your environment and changes nothing.

Nothing in this notebook needs a GPU: every cell runs in seconds on Colab's default CPU runtime.
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

`jax_wrapper` must be imported first: it configures JAX, the numerical library PyAutoLens
uses for fast model fits. The other imports are the plotting library, NumPy, and PyAutoLens
with its plotting module.
"""
from autolens import jax_wrapper  # noqa: F401  Sets the JAX environment before other imports

import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import autolens as al
import autolens.plot as aplt

print(f"PyAutoLens version {al.__version__}")

"""
__What Is A Strong Lens?__

![A strong gravitational lens: light from a distant source galaxy bends around a foreground lens galaxy on its way to JWST](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/strong_lens_schematic.png)

Mass bends light. Einstein's general relativity says that a massive object curves the space
around it, so light passing close by is deflected, just as a glass lens deflects light.

In the picture above, a distant **source galaxy** (right) sends out light in every direction.
Some of it passes close to a massive **lens galaxy** (centre) on its way to us, and the lens's
gravity bends it towards JWST (left). Two of those bent paths are drawn, one passing above the
lens and one below. They are just two of infinitely many: light passes the lens on every side,
and each path arrives at the telescope from a slightly different direction. So instead of one
image of the source we see it in several places, smeared out into **arcs** around the lens.
When the source sits almost exactly behind the lens, the arcs join into a complete circle, an
**Einstein ring**. In the next section you will see that the COSMOS-Web Ring is exactly that.

The picture also labels an **Extra Galaxy**, sitting near the lens but playing no part in the
lensing. Real images contain such galaxies, and this one will turn up again, marked with an
arrow, when we prepare the data.

The size of the ring depends on how much mass the foreground galaxy holds. Measuring the
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

![The COSMOS-Web Ring in JWST colour: a near-complete ring of light around a bright central galaxy](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/cosmos_web_ring_rgb.png)

This is that ring. The data come from the COSMOS-Web survey, the largest JWST imaging programme
of its first year, and the colour picture above combines several of its infrared bands:

- **The lens galaxy** is the bright blob at the centre. It is a massive galaxy seen when the
  Universe was about 3 billion years old (redshift z ≈ 2.0).
- **The ring** is a single, much more distant galaxy (z ≈ 5.1, seen barely a billion years
  after the Big Bang) whose light has been bent into an almost complete circle. Its two bright
  knots are two views of the same bright region of that galaxy.
- **The extra galaxy** from the schematic is the small blob just below and to the right of the
  ring. It is unrelated to the lens, and we will stop it confusing the model below.

A lens model is not fitted to a colour picture but to the image in one band. Each dataset has
three parts: the image itself, a **noise-map** (how uncertain each pixel's brightness is) and the
**PSF** (point spread function: how the telescope blurs a point of light). The cell below loads
the F444W band (infrared light of about 4.4 microns) and plots all three. The code finds the data
whether you are in Colab (inside `autolens_workspace`) or running from the root of the assistant
repository.

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

![The COSMOS-Web Ring in colour and in the F277W and F444W bands, with the lens galaxy, lensed source galaxy and extra galaxy marked](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/cosmos_web_ring_dataset.png)

JWST imaged the ring in four colours of infrared light: F115W, F150W, F277W and F444W (the
number is the wavelength in hundredths of a micron, so F444W is light of about 4.4 microns).
Above, the colour picture sits beside the F277W and F444W images, and the cell below plots those
two bands from the data. The lens galaxy and the ring change in brightness from one colour to
the other, but the ring has **the same shape and size**.

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

![The COSMOS-Web Ring with arrows marking the lensed source galaxy, the lens galaxy and the extra galaxy, and the circular mask](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/cosmos_web_ring_dataset.png)

Look again at the arrows in the picture: the **Lensed Source Galaxy** (the ring), the **Lens
Galaxy** (the blob in the middle) and the **Extra Galaxy**, the one the schematic labelled too.
Three steps get the image ready for a lens model.

1. **Down-weight the extra galaxy.** A file shipped with the data, `mask_extra_galaxies.fits`,
   marks the pixels covered by galaxies that have nothing to do with the lens. We give those
   pixels an enormous noise value, which tells the model "ignore these". Without this step, the
   model would bend itself out of shape trying to explain light it has no business explaining.
2. **Mask.** Only the pixels inside a 2.1" circle (2.1 arcseconds, a tiny patch of sky) are
   used. The picture shows a 1.8" circle, which already takes in the lens and the whole ring;
   we use a slightly larger 2.1" here because that is the mask the good model below was fitted
   with, so evaluating it on the same pixels reproduces its published-quality fit exactly.
3. **Over-sampling.** The lens galaxy's light rises steeply towards its centre, so near the
   centre each pixel is evaluated on a finer grid of sub-pixels, and on a coarser one further out.
   This keeps the model accurate where it matters without slowing it down everywhere.

**For the scientist.** `apply_noise_scaling` sets the noise of the flagged pixels to a large
value (and their data to zero) so they carry no weight in the χ²; it is applied before the
mask. `over_sample_size_via_radial_bins_from` uses 4×4 sub-pixels within 0.3" of the centre and
2×2 beyond. These match the SLaM pipeline that produced the good model (the `cowls_ansofi`
project, see `scripts/cosmos_web_ring/results/README.md`), which used the same 2.1" mask.
"""
mask_radius = 2.1

mask_extra_galaxies = al.Mask2D.from_fits(
    file_path=band_path("F444W") / "mask_extra_galaxies.fits",
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
dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

n_masked_pixels = int(dataset.mask.pixels_in_mask)
print(f"Pixels inside the {mask_radius}\" mask: {n_masked_pixels}")
aplt.subplot_imaging_dataset(dataset=dataset)

"""
Ask Gemini: "Why do astronomers mask out neighbouring galaxies before fitting a model to an image?"

__What A Lens Model Looks Like__

![The published PyAutoLens lens model of the COSMOS-Web Ring in F444W: observed image, lens model image, normalised residual map and source reconstruction (Mercier et al. 2024, CC BY-SA 4.0)](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/mercier2024_lens_model_f444w.png)

Before building a model, it helps to see what a good one achieves. The figure above is from the
first in-depth study of the COSMOS-Web Ring (Mercier et al. 2024), which modelled it with
PyAutoLens. Its four panels, left to right:

- **Data:** the observed F444W image, the ring around the lens galaxy.
- **Model image:** what the lens model predicts the telescope should see. Side by side, it is
  hard to tell from the data.
- **Residuals:** the data minus the model, divided by the noise (the "normalised residual
  map"). A good model leaves only noise: speckle with no ring, no blobs, no pattern, with
  values mostly between -3 and +3.
- **Source reconstruction:** the payoff. The distant galaxy as it would look if the lens were
  not there, undone from the ring. The black diamond is the **caustic**: a source sitting
  inside it is seen as four images, or a ring.

That is what a publication-quality lens model looks like, and the rest of this notebook builds
the same thing on the same data. (The paper's panels are rotated so that north is up, so they
sit at a slight angle to the images in this notebook.)

**For the scientist.** Figure 5 of the arXiv HTML version of Mercier et al. 2024, A&A 687,
A61 (https://ui.adsabs.harvard.edu/abs/2024A&A...687A..61M/abstract, arXiv:2309.15986, CC BY-SA
4.0), F444W row: independent PyAutoLens fits to each band with a pixelized source. The ring
is one of the lenses of COWLS, the COSMOS-Web Lens Survey (Nightingale et al. 2025,
arXiv:2503.08777).

Ask Gemini: "What is a caustic in gravitational lensing, and why does a source inside it make an Einstein ring?"
"""

"""
__The Model__

![The good lens model, piece by piece: the data, the ring with the lens galaxy's light removed, the model of the ring, and the reconstructed source galaxy](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/cosmos_web_ring_good_model.png)

The picture above is the good model you are about to load, taken apart. Left to right: the data;
the ring with the lens galaxy's light removed (that light is one piece of the model); the
model's prediction of the ring (the source's light bent by the lens's mass, two more pieces); and
the source galaxy itself, unlensed (the fourth piece).

A lens model is a description of the system in numbers. Ours has four pieces:

- **The lens galaxy's light.** The glow of the foreground galaxy, which sits on top of the ring
  and has to be modelled so it can be removed. It is described as a sum of 50 smooth blobs
  (Gaussians) of different sizes, a "Multi-Gaussian Expansion" (MGE) that can take on almost
  any smooth shape, including a compact bright core.
- **The lens galaxy's mass.** The simplest choice is an "isothermal" profile, whose density
  falls off with radius in the way stars and dark matter together are observed to in massive
  galaxies. The good model uses a **power law**, which lets the steepness of that fall-off vary
  as well. Its most important number is the **Einstein radius**, the size of the ring the mass
  produces.
- **External shear.** A gentle stretch from the galaxy's surroundings (neighbouring galaxies and
  large-scale structure).
- **The source galaxy's light.** The distant galaxy as it would look *without* lensing. The good
  model reconstructs it on a grid of 1,250 irregular pixels, each free to take its own
  brightness, so it can follow a clumpy young galaxy. The not-great model in the next section
  describes it with a single smooth profile instead.

Finding the numbers is the slow part (it is called "fitting" or "inference", and is explained in
Where Next). The good model was found by a five-step fitting pipeline run on a computing cluster,
and saved to a file, `tracer.json`. A **tracer** is PyAutoLens's name for a lens model with its
numbers filled in: it traces light rays from the source, through the lens, to the telescope.
The cell below loads it and prints its key numbers.

The model files live in the assistant repository; when this notebook runs inside
`autolens_workspace` (as in Colab), the cell downloads them from GitHub first.

**For the scientist.** The good model is the `mass_total[1]` result of a Source, Light and Mass
(SLaM) pipeline with Nautilus at every stage (the `cowls_ansofi` project): lens light an MGE of
2 × 20 Gaussians plus a 10-Gaussian point component, intensities solved linearly; mass
`al.mp.PowerLaw` with `al.mp.ExternalShear` in an `al.MassField`; source an `al.Pixelization` with
an `al.mesh.Delaunay` mesh (1,250 vertices from a Hilbert image mesh plus a 30-point zeroed edge
ring) under `al.reg.AdaptSplit` regularization. Provenance and the reproduction check are in
`scripts/cosmos_web_ring/results/README.md`.
"""
RESULTS_URL = (
    "https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/"
    "scripts/cosmos_web_ring/results"
)


def results_file(relative_path):
    """
    A committed model file: the local copy when running from the assistant repository,
    otherwise a copy downloaded from GitHub (once) into `cosmos_web_ring_models/`.
    """
    local = Path("scripts") / "cosmos_web_ring" / "results" / relative_path
    if local.exists():
        return local
    downloaded = Path("cosmos_web_ring_models") / relative_path
    if not downloaded.exists():
        downloaded.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(f"{RESULTS_URL}/{relative_path}", downloaded)
    return downloaded


tracer = al.from_json(file_path=results_file("ansofi/tracer.json"))

lens_galaxy, source_galaxy = tracer.galaxies
mass = lens_galaxy.mass
shear = tracer.fields[0].shear
n_gaussians = len(lens_galaxy.bulge.profile_list) + len(lens_galaxy.point.profile_list)

print(f"Lens light:     an MGE of {n_gaussians} Gaussians")
print(f"Lens mass:      {type(mass).__name__}, Einstein radius {mass.einstein_radius:.3f} arcsec, "
      f"slope {mass.slope:.2f} (2 = isothermal)")
print(f"                centre ({mass.centre[0]:.3f}, {mass.centre[1]:.3f}) arcsec")
print(f"External shear: magnitude {np.hypot(shear.gamma_1, shear.gamma_2):.3f}")
print(f"Source:         a {type(source_galaxy.pixelization.mesh).__name__} pixel grid of "
      f"{source_galaxy.pixelization.mesh.pixels} pixels")

"""
Ask Gemini: "What is a power-law mass profile, and what does its slope tell us about a galaxy?"

__Good Versus Not-Great__

![Normalised residuals of the good model (noise-like speckle) and of the not-great model with a smooth source (bright and dark patches tracing the ring and its two knots)](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/cosmos_web_ring_residuals_good_vs_bad.png)

How do you know a model is good? Look at what it leaves behind, and compare it with a worse one.
The picture above is where this section ends up: the **normalised residuals** (what is left after
subtracting the model, in units of the noise) of the good model on the left and of a simpler,
not-great model on the right, on the same colour scale. Left: speckle. Right: the ring and its
two bright knots, left behind.

**The good model.** To evaluate a model, PyAutoLens bends the source's light through the lens,
blurs it with the PSF, adds the lens galaxy's light and compares the result with every pixel
of the data. That comparison is a **fit**, and it takes a few seconds.

A pixel-grid source needs two more ingredients saved alongside the model: where its pixels sit
(they are placed more densely where the source is bright) and how strongly neighbouring pixels
are smoothed, both worked out from an earlier stage of the pipeline. The cell loads them too.

The panels show the data, the model image, the lens galaxy's light and the ring with it
subtracted, the lensed source model, the **normalised residuals** (data minus model, divided by
the noise: values within about ±3 are what noise alone produces), the χ² map and the
reconstructed source at three zooms. The second figure shows the source plane on its own: the
distant galaxy, unlensed.

**For the scientist.** The source mesh grid and the source adapt image enter through
`al.AdaptImages`; the pixelization over-sampling (4×4 where the earlier source S/N exceeds 3,
2×2 elsewhere) is the pipeline's. With these the fit reproduces the pipeline's maximum
likelihood, 3717.19, to better than 10⁻⁹ (for a pixelized source `figure_of_merit` is the
Bayesian log evidence of the linear inversion, which is what the search maximised).
"""
over_sample_size_pixelization = al.Array2D(
    values=al.Array2D.from_fits(
        file_path=results_file("ansofi/over_sample_size_pixelization.fits"),
        pixel_scales=pixel_scale,
    ).native,
    mask=dataset.mask,
)
dataset_good = dataset.apply_over_sampling(
    over_sample_size_pixelization=over_sample_size_pixelization
)

source_adapt_image = al.Array2D(
    values=al.Array2D.from_fits(
        file_path=results_file("ansofi/source_adapt_image.fits"),
        pixel_scales=pixel_scale,
    ).native,
    mask=dataset.mask,
)
source_mesh_grid = al.from_json(file_path=results_file("ansofi/source_mesh_grid.json"))

adapt_images = al.AdaptImages(
    galaxy_image_dict={source_galaxy: source_adapt_image},
    galaxy_image_plane_mesh_grid_dict={source_galaxy: source_mesh_grid},
)

fit = al.FitImaging(dataset=dataset_good, tracer=tracer, adapt_images=adapt_images)

reduced_chi_squared = float(fit.chi_squared) / n_masked_pixels
print(f"Good model: figure of merit {float(fit.figure_of_merit):.2f} (pipeline: 3717.19)")
print(f"Good model: reduced chi-squared {reduced_chi_squared:.2f}")

aplt.subplot_fit_imaging(fit=fit)
aplt.subplot_fit_imaging_of_planes(fit=fit, plane_index=1)

"""
The residuals are speckle: no ring, no knots, no pattern, just like the published figure. The
model has explained everything in the image except the noise, and the reconstructed source shows
a compact bright galaxy with fainter, clumpy structure around it, a galaxy seen when the
Universe was barely a billion years old, magnified for us by a natural telescope.

**The not-great model.** Now the same lens, with one change: the source galaxy is described by a
single smooth profile (a "Sérsic" profile) instead of a pixel grid. This is what you get by
asking for "a simple source", and it is a mistake that is easy to make, because the headline
number still looks fine. This model was fitted to the same data, with the same mask, by the
assistant's reference script (it has an isothermal mass and a 20-Gaussian lens light); the cell
loads and evaluates it in the same way.

Look at its residuals. The model ring is smooth, and the **two bright knots** of the real source,
together with structure around the ring, are left behind as bright and dark patches. The distant
galaxy is clumpy, and a smooth profile cannot describe it.

**For the scientist.** A smooth source needs no adapt images or pixelization over-sampling, so
the bad tracer is evaluated on the light-profile over-sampling alone. Its reduced χ² is
χ²/N_pixels with no degrees-of-freedom correction; the good model's is lower than 1 partly
because a 1,250-pixel source has many effective degrees of freedom and partly because the bundled
noise-map is somewhat conservative. Compare the residual maps, not only the numbers.
"""
tracer_sersic = al.from_json(file_path=results_file("sersic_source/tracer.json"))
fit_sersic = al.FitImaging(dataset=dataset, tracer=tracer_sersic)

aplt.subplot_fit_imaging(fit=fit_sersic)
aplt.subplot_fit_imaging_of_planes(fit=fit_sersic, plane_index=1)

einstein_radius = float(mass.einstein_radius)
einstein_radius_sersic = float(tracer_sersic.galaxies[0].mass.einstein_radius)
reduced_chi_squared_sersic = float(fit_sersic.chi_squared) / n_masked_pixels

print(f"Good model (pixel-grid source):    Einstein radius {einstein_radius:.3f} arcsec, "
      f"reduced chi-squared {reduced_chi_squared:.2f}")
print(f"Not-great model (Sersic source):   Einstein radius {einstein_radius_sersic:.3f} arcsec, "
      f"reduced chi-squared {reduced_chi_squared_sersic:.2f}")

"""
The two Einstein radii are close, so judged by its headline number alone the not-great model
looks fine. Its residuals say otherwise, and its reduced χ² is many times larger.

That is the lesson: a plausible-looking Einstein radius is not enough. Residuals with structure
mean the model is missing something real, and the numbers it gives may be biased.

**For the scientist.** A mismatched source model is compensated by the mass model, which is
why the Einstein radius shifts. Residuals that trace the ring point to the source (or the mass);
residuals centred on the lens point to the lens-light model. The two models also differ in mass
profile (power law versus isothermal), so the two `einstein_radius` parameters are not a
like-for-like comparison; the effective Einstein radius of the critical curve, computed for both
in the next section, is.

Ask Gemini: "Why can a model with the right Einstein radius still be a bad fit, and how do residuals reveal it?"

__The Mass Inside The Ring__

![The ring with the lens galaxy's light removed, and the good model's Einstein radius drawn on it as a white circle](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/cosmos_web_ring_einstein_radius.png)

Above is the ring with the lens galaxy's light removed, and in white the circle the good model's
mass bends light into: its **critical curve**, the ring's true size. Its radius is set by how
much mass the lens holds.

The Einstein radius is the ring's size in the sky. Combined with the distances to the two
galaxies (which follow from their redshifts), it gives the mass enclosed by the ring, in units
of the Sun's mass. The cell below works it out from the good model.

**For the scientist.** We quote the effective Einstein radius of the tangential critical curve
of the full tracer (mass plus shear), via `al.LensCalc.from_tracer`, and M_E = Σ_crit × the
enclosed angular area, with Σ_crit from the Planck15 cosmology and the bundle's redshifts
(z_lens = 2.0; the pipeline that produced the good model used 2.02, which changes the mass by
1%). Mercier et al. 2024 (arXiv:2309.15986) find θ_E = 0.78 ± 0.04" (0.77" with PyAutoLens) and
3.66–3.84 × 10¹¹ solar masses for z_source = 5.48–5.08.
"""
cosmology = al.cosmo.Planck15()
sigma_crit = float(
    cosmology.critical_surface_density_between_redshifts_from(
        redshift_0=redshift_lens, redshift_1=redshift_source
    )
)
kpc_per_arcsec = float(cosmology.kpc_per_arcsec_from(redshift=redshift_lens))

evaluation_grid = al.Grid2D.uniform(shape_native=(200, 200), pixel_scales=0.03)
lens_calc = al.LensCalc.from_tracer(tracer)
einstein_radius_effective = float(lens_calc.einstein_radius_from(grid=evaluation_grid))
einstein_mass = sigma_crit * float(lens_calc.einstein_mass_angular_from(grid=evaluation_grid))

einstein_radius_kpc = einstein_radius_effective * kpc_per_arcsec
light_years = round(einstein_radius_kpc * 3262, -3)  # 1 kpc is about 3,262 light years.

print(f"Einstein radius: {einstein_radius_effective:.3f} arcsec (Mercier et al. 2024: 0.78 +/- 0.04)")
print(f"  = {einstein_radius_kpc:.1f} kpc at the lens, about {light_years:,.0f} light years")
print(f"Mass inside the Einstein radius: {einstein_mass:.2e} solar masses")
print(f"  = about {einstein_mass / 1e11:.0f} hundred billion Suns")

einstein_radius_effective_sersic = float(
    al.LensCalc.from_tracer(tracer_sersic).einstein_radius_from(grid=evaluation_grid)
)
print(f"Not-great model, for comparison: {einstein_radius_effective_sersic:.3f} arcsec")

"""
About four hundred billion Suns sit inside the ring, most of it stars and dark matter. The
Einstein radius agrees with the published value to well within its error. The not-great model's
ring is a few per cent smaller: close, which is exactly why its residuals, not its headline
number, are what give it away.

Ask Gemini: "How can a mass measurement from a lens include dark matter that we cannot see?"

__Where Next__

![The COSMOS-Web Ring](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/cosmos_web_ring_rgb.png)

- **Run a fit yourself.** Both models here were loaded, not fitted. To find a model from
  scratch, either ask the assistant ("fit a lens model to the COSMOS-Web Ring"; see the agent
  route below), or run the assistant's reference script,
  `scripts/cosmos_web_ring/fit_cosmos_web_ring.py`: it fits an MGE lens light, an isothermal mass
  with shear and an MGE source with a fast multi-start gradient optimiser in a few minutes on a
  GPU (`--variant sersic_source --mask-radius 2.1` reproduces the not-great model above).
- **The agent route.** Open https://github.com/PyAutoLabs/autolens_assistant in Claude Code or
  Codex and paste the assistant starting prompt quoted at the top of this notebook. You can then
  change this analysis in plain language: "fit F277W as well", "try a pixelized source",
  "add a second lens galaxy".
- **HowToLens** (https://github.com/PyAutoLabs/HowToLens), the lecture series that teaches
  strong lensing and PyAutoLens from first principles.
- **COWLS**, the COSMOS-Web Lens Survey, of which this ring is one lens: Nightingale et al. 2025,
  arXiv:2503.08777.
- **The discovery paper**: Mercier et al. 2024, A&A 687, A61, arXiv:2309.15986.

**A caveat on error bars.** Evaluating a model gives one set of numbers and no error bars. The
good model was found with a nested sampler (Nautilus), which also measures uncertainties; the
reference script's fast optimiser does not, and returns one best model only. To quote an Einstein
radius with a range, such as the ±0.04" of Mercier et al., fit with a sampler, as shown in
`scripts/imaging/modeling.py` of the `autolens_workspace`.

Ask Gemini: "What is the difference between a maximum-likelihood fit and a posterior, and why do error bars need a sampler?"
"""
