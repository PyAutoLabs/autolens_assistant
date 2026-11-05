# COSMOS-Web Ring — reference fits

Recorded outputs of [`../fit_cosmos_web_ring.py`](../fit_cosmos_web_ring.py) on the
bundled JWST/NIRCam imaging (`dataset/imaging/cosmos_web_ring/wavebands/`). They are
what "right" looks like for the assistant's COSMOS-Web Ring starting prompt and the
truth behind the `cosmos-web-ring-fit` benchmark card.

Two folders hold **models committed for evaluation without a search**, which the Colab
notebook (`docs/colab/cosmos_web_ring_colab.py`) loads and fits in seconds:
[`ansofi/`](ansofi/) (the good model, a pixelized source from a Nautilus SLaM pipeline) and
[`sersic_source/tracer.json`](sersic_source/) (the not-great model, a single Sérsic source).
Both are evaluated on the same data: F444W, extra galaxies noise-scaled, a **2.1"** circular
mask (3841 pixels) and 4/2/2 radial light-profile over-sampling. See
[The committed models](#the-committed-models) below.

**These are maximum-likelihood fits.** `MultiStartProdigy` returns one best-fit model
and no posterior: there are no error bars on any number below. For quotable
uncertainties, fit the same model with `Nautilus` (`skills/al_configure_search.md`).

## The numbers

Every row: 1.8" circular mask (2813 pixels), adaptive over-sampling, Isothermal mass
plus external shear, `MultiStartProdigy` with 48 starts × up to 300 steps, `use_jax=True`.
θ_E is the Isothermal `einstein_radius` parameter; θ_E,eff is the effective radius of the
tangential critical curve (mass plus shear), the quantity Mercier et al. 2024 quote.
Reduced χ² is χ² over the number of pixels inside the mask. Wall times are on the GPU.

| Variant | Band | θ_E (") | θ_E,eff (") | Reduced χ² | log L | Wall (s) | Kept |
|---------|------|---------|-------------|------------|-------|----------|------|
| **good** — MGE lens light + MGE source | F444W | **0.803** | **0.775** | **0.616** | 1204.4 | 448 | [`good/`](good/) |
| **poor (chosen)** — single Sérsic source | F444W | 0.755 | 0.756 | 2.879 | −1978.2 | 245 | [`sersic_source/`](sersic_source/) |
| good, achromatic check | F277W | 0.801 | 0.772 | 0.658 | 732.7 | 626 | [`good_F277W/`](good_F277W/) |
| no extra-galaxy noise scaling | F444W | 0.780 | 0.781 | 3.357 | 3668.7 † | 534 | numbers only |
| single Sérsic lens light | F444W | 0.498 | 0.513 | 40.886 | −55435.7 | 282 | numbers only |

† Not comparable: without the noise scaling the noise-map differs, so log L is on a
different scale. Compare reduced χ² instead.

**What goes wrong without priors.** The first run of the good model used the library's
default priors (Isothermal `einstein_radius` uniform over 0–8", shear components uniform
over ±0.3). It converged to θ_E = 2.40" (larger than the mask), shear 0.27 and reduced
χ² 9.34 (log L −11070.0, 363 s): the source sat outside the caustic and the whole ring
was left in the residuals. The script now bounds `einstein_radius` to 0.3–1.5" and each
shear component to ±0.15, which is what anyone looking at the image knows before fitting
(the ring's radius is ~0.8", well inside the mask). A user who copies the template
priors verbatim can see this failure; the benchmark card's text says so.

## The good fit

`good/fit_subplot.png`: the model image reproduces the data, the lens-light-subtracted
panel shows the full ring with its two bright clumps (east and north-west), and the
source-model image traces it. The source plane shows one compact source just beside a
tiny diamond caustic. The normalised residuals are within about ±6σ and mostly
noise-like; the reduced χ² below 1 suggests the bundled noise-map is somewhat
conservative.

Two coherent residual features remain. The stronger is a positive excess south of the
ring, measured from the smoothed normalised residual map at x = +0.24", y = −1.08"
(0.3" outside the Einstein radius, extending over x = 0.06–0.42", y = −1.26 to −0.72").
It appears at the same place in the F277W fit and has no counter-image on the far side
of the ring, so it is most likely light from a faint object near the lens (the small
companion seen below the ring in the COWLS colour image) rather than lensed source
structure; a fainter feature near x = −0.48", y = +0.60" sits on the ring and is source
structure a 20-Gaussian MGE cannot capture. The natural next steps are to down-weight the
southern excess by adding it to `mask_extra_galaxies.fits`, and to replace the MGE source
with a pixelized source reconstruction (`skills/al_inspect_source_reconstruction.md`).

The one compact galaxy inside the mask that is clearly not part of the lens (north-east,
x = +0.48", y = +1.14", signal-to-noise ~30) is already covered by the bundled
`mask_extra_galaxies.fits`: its light is down-weighted, not modelled.

## The poor fit, and why a user gets it

`sersic_source/` is what a user gets by asking for "a simple source": a single Sérsic
profile cannot describe a clumpy z ~ 5 galaxy. The fit still converges on a lensed ring
at almost the right size (θ_E 0.755", 6% below the good fit; θ_E,eff 0.756", 2.5%
below), so the headline number looks plausible, but `fit_subplot.png` shows the
difference at once: the model ring is smooth, and the two bright clumps are left as
~19σ residual peaks, with further structured residuals around the ring. Reduced χ² is
2.9, nearly five times the good fit's.

The other variants were not chosen. Skipping the noise scaling gives a sensible θ_E
(0.780") but its fit is dominated by one ~28σ residual on the unmasked companion, which
is a data-preparation lesson rather than a modelling one. A single-Sérsic lens light
cannot fit the lens galaxy's profile, drives θ_E to 0.50" and reduced χ² to 41: that
fit is terrible, not "poor but plausible".

## Lensing is achromatic

Lensing is achromatic: the same model fitted independently to F277W gives
θ_E = 0.801" against 0.803" in F444W (θ_E,eff 0.772" against 0.775"), the same Einstein
radius to within 0.002" (0.2%), less than a twentieth of a pixel. The ring is the same
size in every colour because gravity bends all wavelengths equally.

## The mass inside the ring

M_E = Σ_crit × π θ_E², with the critical surface density from the lens and source
redshifts (z_l = 2.0, z_s = 5.1043 from `info.json`, Planck15:
Σ_crit = 2.05 × 10¹¹ M_⊙ arcsec⁻²; 1" = 8.58 kpc at the lens). The mass inside the
effective Einstein radius is **3.9 × 10¹¹ M_⊙, about 400 billion Suns** (4.2 × 10¹¹ M_⊙
from the isothermal parameter). The Einstein radius is 6.9 kpc (isothermal parameter)
or 6.6 kpc (effective) at the lens. Mercier et al. 2024 find 3.66–3.84 × 10¹¹ M_⊙ for
z_source = 5.48–5.08 (see [`wiki/literature/entities/cosmos-web-ring.md`](../../../wiki/literature/entities/cosmos-web-ring.md)).

## The committed models

### `ansofi/` — the good model

The `mass_total[1]` result of the `cowls_ansofi` science project
(`Science/active/cowls_ansofi`, `scripts/slam.py`): a five-search Source, Light and Mass (SLaM)
pipeline, Nautilus at every stage, Numba CPU, on F444W of COSJ100024+015334 with the extra
galaxies noise-scaled before a fixed 2.1" circular mask at (0", 0") and 4/2/2 radial
light-profile over-sampling. RAL job 412621, completed 2026-10-20; log evidence 3674.0, maximum
log likelihood 3717.19. The COWLS `data.fits`, `noise_map.fits`, `psf.fits` and
`mask_extra_galaxies.fits` it fitted are md5-identical to this bundle's
`dataset/imaging/cosmos_web_ring/wavebands/F444W/`.

| File | What it is |
|------|------------|
| `tracer.json` | The maximum-likelihood `Tracer`, copied unchanged from the stage's `files/tracer.json`: lens light an MGE of 2 × 20 Gaussians plus a 10-Gaussian point component (linear intensities, re-solved in every fit); `PowerLaw` mass, θ_E = 0.768", slope 1.944, centre (0.015", 0.054"), in a `MassField` with `ExternalShear` (γ₁, γ₂) = (0.025, −0.014); source `Pixelization` with a `Delaunay` mesh (1250 vertices + 30 zeroed edge points) under `AdaptSplit` regularization. Redshifts 2.02 / 5.1043 as the project uses. |
| `source_adapt_image.fits` | The S/N-capped (at 3) source adapt image the stage used (`image/adapt_images.fits`, source extension), 209 × 209, zero outside the mask. It sets the `AdaptSplit` regularization weights. |
| `source_mesh_grid.json` | The 1280 image-plane mesh points (`image/adapt_image_plane_mesh_grids.fits`): 1250 drawn by a `Hilbert` image mesh (weight power 3.5, floor 0.01) from the adapt image, plus a 30-point circle half a pixel outside the mask. A `Grid2DIrregular`, loaded with `al.from_json`. |
| `over_sample_size_pixelization.fits` | The pixelization over-sampling (`image/dataset.fits`, `OVER_SAMPLE_SIZE_PIXELIZATION`): 4 where the `source_pix[1]` source S/N exceeds 3, 2 elsewhere. |

The adapt image and mesh grid are passed via
`al.AdaptImages(galaxy_image_dict=..., galaxy_image_plane_mesh_grid_dict=...)` keyed by the
tracer's source galaxy. **Reproduction check:** `al.FitImaging` on the bundle's F444W, prepared
as above, gives `figure_of_merit` = 3717.187053681 against the stage's maximum log likelihood
3717.187053619 (the figure of merit of a pixelized fit is the inversion's log evidence, the
quantity Nautilus maximised), with the default `al.Settings` or the stage's own settings alike.
Its normalised residuals are noise-like; reduced χ² (χ²/N_pixels) is 0.20, lower than 1 because
a 1250-pixel source has many effective degrees of freedom and the noise-map is conservative.
The effective Einstein radius of the tangential critical curve is 0.770" (6.6 kpc at z = 2.0),
enclosing 3.8 × 10¹¹ M_⊙ (Planck15, z_l = 2.0 as `info.json`; 3.9 × 10¹¹ M_⊙ with the
project's 2.02), against Mercier et al.'s θ_E = 0.78 ± 0.04".

### `sersic_source/tracer.json` — the not-great model

Re-recorded on 2026-10-20 for the notebook by running
`python scripts/cosmos_web_ring/fit_cosmos_web_ring.py --variant sersic_source --mask-radius 2.1`
once (`MultiStartProdigy`, 48 starts × up to 300 steps, JAX on the laptop CPU, 431 s) so that
the good and the not-great models are compared on identical data. `tracer.json` is
`result.max_log_likelihood_tracer` (`al.output_to_json`); `summary_mask_2.1.json` and
`fit_subplot_mask_2.1.png` are that run's summary and fit. The earlier 1.8" files in the same
folder (`summary.json`, `fit_subplot.png`, `source.png`, `tracer.png`) are the table row above.

| Mask | θ_E (") | θ_E,eff (") | Reduced χ² | log L | Pixels |
|------|---------|-------------|------------|-------|--------|
| 1.8" (table above) | 0.755 | 0.756 | 2.879 | −1978.2 | 2813 |
| **2.1" (notebook)** | **0.760** | **0.742** | **2.300** | 60.2 | 3841 |

As at 1.8", the smooth source leaves the ring's two bright knots as ~±20σ residual peaks with
structured residuals around the ring, while the Einstein radius looks plausible (3.6% below the
good model's θ_E,eff of 0.770"). The lower reduced χ² at 2.1" comes from the extra, mostly empty
sky pixels the larger mask adds.

## Provenance

- Date: 2026-09-26. Script: `scripts/cosmos_web_ring/fit_cosmos_web_ring.py` on
  branch `feature/cosmos-web-ring-greeting`; each run's `summary.json` holds the full
  settings, versions and environment.
- Library versions: autolens, autogalaxy, autoarray and autofit 2026.8.17.1; JAX 0.10.2.
- Machine: 8-core laptop, Linux under WSL2 (5.10.16.3-microsoft-standard-WSL2), with an
  NVIDIA GeForce RTX 2060 (Max-Q, 6 GB). The reference fits ran on the GPU
  (`jax.devices()` = `[cuda:0]`, `JAX_PLATFORMS=cuda`, `OMP_NUM_THREADS=8`).
- CPU timing: 8-thread CPU JAX on this machine (`jax.devices()` = `[cpu:0]`,
  `OMP_NUM_THREADS=8`) spent more than 22 min (31 min when stopped) in the first XLA
  compile of the good fit's objective and the run was abandoned; the GPU compiles the
  same objective in about 1.5 min. The CPU compile is single-threaded, so more threads do
  not help (a 4-start, 20-step test run with one thread took 1229 s). **On a CPU-only
  machine expect a long first compile**; for a quick look, use fewer starts
  (`n_starts=8`) and keep the full 48 for the reference fit.
- PSF: the shipped PSFs sum to 0.972 (F444W) and 0.968 (F277W); `al.Imaging.from_fits`
  normalises them to unit sum on load (`use_normalized_psf=True`), which the script asserts.
- Figures are downsampled to 1600 px and palette-quantised to keep this folder small;
  rerun the script for full-resolution PNGs.
