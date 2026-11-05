"""
The COSMOS-Web Ring: weighing a galaxy with light bent by gravity
=================================================================

This notebook takes you through the **COSMOS-Web Ring**, a near-perfect circle of light
photographed by the James Webb Space Telescope (JWST). The ring is the image of a distant
galaxy, distorted by the gravity of another galaxy in front of it.

You will work through a strong lensing analysis, fit a model to the JWST data, and measure
how much mass lies inside the ring. You do not need any previous knowledge of gravitational
lensing or Python.

If you prefer to explore through conversation, you can use the PyAutoLens Assistant
(https://github.com/PyAutoLabs/autolens_assistant). Open Claude Code or Codex in any folder
and paste the starting prompt below. The assistant will show you the ring, ask about your
background and guide you through the analysis.

> I want to use the PyAutoLens Assistant: https://github.com/PyAutoLabs/autolens_assistant
> First clone that repository, cd into it and follow its AGENTS.md.
>
> I'd like to understand how gravitational lensing works using the JWST image of the COSMOS-Web Ring that ships with the assistant. Show me the picture, explain what we are looking at, and walk me through fitting a lens model so we can measure the mass inside the ring and see how well the model reproduces the observations. Pitch it at my level: ask me what my background is first. Explain what we are doing as we go, and let me ask questions or change the analysis along the way.

Each section ends with a **🤖 Ask AI:** question. If you would like to explore further,
you can ask Google Colab's built-in AI, Gemini, using the sparkle button in the toolbar.

<!-- Maintainers: this notebook is generated from docs/colab/cosmos_web_ring_colab.py and committed
executed; rebuild it with `make colab` from the assistant repository root. The image URLs and the
results-download URL below point at `main`; switch them to the release tag at release, as the
README's Colab badge is. -->

__Contents__

- **Google Colab Setup:** Install PyAutoLens and download the data (a no-op outside Colab).
- **Imports:** Load the libraries.
- **What Is A Strong Lens?:** How a galaxy's gravity bends light into arcs and rings.
- **The Picture:** The JWST image of the ring, and the data we will work with.
- **Two Colours, One Ring:** Compare the ring in two infrared bands.
- **Preparing The Data:** Remove a neighbouring galaxy's light from the analysis and choose the area to analyse.
- **What A Lens Model Looks Like:** The published lens model of this ring, panel by panel.
- **The Model:** The four pieces of a lens model, and the good model loaded from file.
- **Explore The Model:** Change the lens mass and foreground light, and see what happens.
- **The Mass Inside The Ring:** Turn the ring's size into a mass in Suns.
- **Where Next:** Run a fit yourself, the agent route, HowToLens, COWLS and error bars.

__Google Colab Setup__

Run this cell to install PyAutoLens and download the files needed for this notebook on Google Colab.
If you’re running locally or in HTML, it leaves your installation unchanged.
"""

from autolens import setup_colab

setup_colab.setup("autolens", raise_error_if_not_gpu=False)

"""
__Imports__

Run the cell below to load the Python tools we will use throughout the notebook.
"""
from autolens import jax_wrapper  # noqa: F401  Sets the JAX environment before other imports

import urllib.request
from copy import deepcopy
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import autolens as al
import autolens.plot as aplt

print(f"PyAutoLens version {al.__version__}")

"""
__What Is A Strong Lens?__

![A strong gravitational lens: light from a distant source galaxy bends around a foreground lens galaxy on its way to JWST](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/strong_lens_schematic.png)

Mass bends light. Einstein's theory of general relativity tells us that a massive object
curves the space around it. This bends the path of light passing nearby, much as a magnifying
glass bends light.

In the picture above, a distant **source galaxy** (right) sends out light in every direction.
Some of that light passes close to a **lens galaxy** (centre), whose gravity bends its path
towards JWST (left).

The picture shows two of these paths: one above the lens galaxy and one below. Light also
passes around the galaxy on all sides, reaching the telescope from different directions.
We therefore see the same source galaxy in several places, stretched into **arcs** around
the lens galaxy. When the two galaxies line up almost exactly with the telescope, these arcs
join into an **Einstein ring**. The COSMOS-Web Ring is one such ring.

The picture also labels an **Extra Galaxy** near the lens galaxy. Its light appears in the
image, and we will see it again when we prepare the data.

The size of the ring depends on how much mass the foreground galaxy contains. Measuring the
ring lets us weigh the galaxy, including its dark matter, which gives off no light.

**🤖 Ask AI:** "How does a galaxy's mass bend light, and why does perfect alignment make a ring?"
"""

"""
__The Picture__

![The COSMOS-Web Ring in JWST colour, with arrows marking the lensed source galaxy, the lens galaxy and the extra galaxy](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/cosmos_web_ring_rgb_labelled.png)

This is the COSMOS-Web Ring, photographed as part of the COSMOS-Web survey, the largest JWST
imaging programme of its first year. The arrows mark:

- **The Lens Galaxy:** the bright patch at the centre. We see this massive galaxy as it was
  when the Universe was about 3 billion years old (redshift z ≈ 2.0).
- **The Lensed Source Galaxy:** the ring itself. This is a single, much more distant galaxy
  (z ≈ 5.1), seen barely a billion years after the Big Bang. Its light has been bent into an
  almost complete circle. The two bright knots in the ring are two views of the same bright
  region of that galaxy.
- **The Extra Galaxy:** the small patch just below and to the right of the ring, also shown
  in the earlier diagram. We will remove its light from the analysis when we prepare the image.

JWST takes pictures in several colours of infrared light. The colour image above combines
these, but for our analysis we use one colour at a time.

The next cell shows four views of the F444W observation:

- **Image (the data):** the measured brightness in each pixel. Look for the bright central
  lens galaxy and the ring of light around it.
- **Noise map:** the estimated uncertainty in each pixel's brightness. A larger value means
  that pixel provides a less precise measurement; this is not a separate picture of the background.
- **Signal-to-noise map:** the measured brightness divided by its uncertainty. A value of 10
  means the brightness is ten times the estimated noise level. This helps us see where the
  light is measured most clearly.
- **Point spread function (PSF):** how the telescope spreads the light from a single point
  across nearby pixels. We include this blurring when predicting what a lens model should
  look like in the image.

Each panel has its own colour scale. The image's brightness stretch lets us see the faint
ring beside the bright centre; the colours represent measured brightness, not the galaxies'
actual colours.

The plots below use the dataset's coordinate orientation; the colour composite above has
been flipped vertically for presentation, so the neighbouring galaxy appears on the opposite side.
"""
dataset_root = Path("dataset") / "imaging" / "cosmos_web_ring"  # Colab: autolens_workspace; else the assistant repo root.

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
        pixel_scales=0.03 if band in ("F115W", "F150W") else pixel_scale,
    )


dataset = load_band("F444W")
aplt.subplot_imaging_dataset_intro(dataset, stretch=0.01, radius=2.5)

"""
**🤖 Ask AI:** "What is a redshift, and how do astronomers know the ring galaxy is at z = 5.1?"

__Two Colours, One Ring__


Here we compare two infrared bands: F150W, centred near 1.5 microns, and F444W, near
4.4 microns. A band is the range of wavelengths recorded in one image.

Run the cell below to compare F150W (1.5 microns) with F444W (4.4 microns). The lens galaxy
and the ring have different brightnesses in each colour, but the ring has **the same shape
and size**. The two bands are stretched independently to show their structure, so equal colours do not imply equal flux.

This happens because gravity bends light of every wavelength by the same amount. Astronomers
call this **achromatic** lensing. The colours tell us about what the galaxies are made of,
while the ring's shape and size tell us about mass.

As a separate check, fitting a model to F277W and F444W gave an Einstein radius—a measure of
the ring's size—of 0.803" in F444W and 0.801" in F277W. These agree to 0.2%, a difference of
less than a twentieth of a pixel. A related measure, the effective radius of the critical
curve, was 0.775" and 0.772", respectively. These results are recorded in
`scripts/cosmos_web_ring/results/README.md` in the assistant repository.
"""
dataset_f150w = load_band("F150W")

display_mask = al.Mask2D.circular(
    shape_native=dataset.shape_native, pixel_scales=pixel_scale, radius=2.5
)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
display_mask_f150w = al.Mask2D.circular(
    shape_native=dataset_f150w.shape_native, pixel_scales=dataset_f150w.pixel_scales, radius=2.5
)
aplt.plot_array(dataset_f150w.apply_mask(mask=display_mask_f150w).data,
                ax=axes[0], title="F150W (1.5 microns)", stretch=0.01)
aplt.plot_array(dataset.apply_mask(mask=display_mask).data,
                ax=axes[1], title="F444W (4.4 microns)", stretch=0.01)
plt.tight_layout()
plt.show()

"""
**🤖 Ask AI:** "Why does the ring look the same in every colour, when the galaxies themselves change colour?"

__Preparing The Data__


Two steps prepare the image for our analysis.

1. **Remove the extra galaxy's light from the analysis.** A file supplied with the data marks
   the pixels covering the extra galaxy. We give these pixels very little weight, so their
   light does not influence the fit.
2. **Choose the area to analyse.** We use a circle with a radius of 2.1 arcseconds, a tiny
   angle on the sky. Blank space outside this circle marks pixels excluded from the analysis.
   We use 2.1 here to match the area used when fitting the model we will examine below.
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

# Over-sampling keeps the light calculation accurate near the galaxy's bright centre.
# You do not need to understand or change these settings to follow this notebook.
over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[4, 2, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)
dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

n_masked_pixels = int(dataset.mask.pixels_in_mask)
print(f"Pixels inside the {mask_radius}\" mask: {n_masked_pixels}")
aplt.subplot_imaging_dataset_intro(
    dataset, stretch=0.01, radius=2.5,
    excluded_pixels=~mask_extra_galaxies.array,
)

"""
Blank regions mark the area outside our mask and the down-weighted neighbouring galaxy.
The noise colourbar describes the retained pixels, rather than the artificially huge
uncertainty assigned to that neighbour.

**🤖 Ask AI:** "Why do astronomers mask out neighbouring galaxies before fitting a model to an image?"

__What A Lens Model Looks Like__

![Published PyAutoLens lens models of the COSMOS-Web Ring: F150W in the top row and F444W in the bottom row, each showing the observed image, model image, residuals and source reconstruction (Mercier et al. 2024, CC BY-SA 4.0)](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/mercier2024_lens_model_f150w_f444w.png)

Before fitting a model, it helps to see what a good fit looks like. The figure above comes
from the first in-depth study of the COSMOS-Web Ring (Mercier et al. 2024, published in
Astronomy & Astrophysics: https://ui.adsabs.harvard.edu/abs/2024A&A...687A..61M/abstract),
which used PyAutoLens. The top row shows F150W and the bottom row shows F444W.
Each row has four panels, from left to right:

- **Data:** the JWST image, showing the ring around the lens galaxy.
- **Model image:** the image predicted by the model. It looks very similar to the observations.
- **Residuals:** the differences between the observations and the model, measured relative
  to the noise in the image. A good fit leaves small differences consistent with noise rather than recognisable
  shapes or patterns, with values mostly between -3 and +3.
- **Source reconstruction:** what the distant galaxy would look like without the lens
  bending its light. The black diamond marks a boundary called a **caustic**. A source inside
  this boundary produces four images, which can join into a ring.

In the following sections, we will examine a model fitted to the same F444W data. The paper's
images are rotated so that north is up, so they appear at a slightly different angle from the
images in this notebook.

**🤖 Ask AI:** "What is a caustic in gravitational lensing, and why does a source inside it make an Einstein ring?"
"""

"""
__The Model__

![The good lens model, piece by piece: the data, the ring with the lens galaxy's light removed, the model of the ring, and the reconstructed source galaxy](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/cosmos_web_ring_good_model.png)

The picture above shows the model we will explore. From left to right, you can see the
observed image, the ring with the foreground galaxy's light removed, the model's version of
the ring, and the reconstructed distant galaxy.

To reproduce the image, we need to describe four things:

- **The lens galaxy's light.** The foreground galaxy's glow overlaps the ring. We describe
  that glow using 50 smooth ellipses of different sizes, which together follow the galaxy's
  brightness.
- **The lens galaxy's mass.** This determines how strongly the galaxy bends light. Our model
  allows the mass to become less concentrated further from the centre. It also allows us to
  adjust how quickly that concentration changes. An important measurement is the
  **Einstein radius**, which describes the size of the ring.
- **The influence of nearby matter.** Neighbouring galaxies and other surrounding matter
  gently stretch the image. We include this effect, called **external shear**.
- **The source galaxy's light.** We reconstruct the distant galaxy using a grid of 1,250
  small, irregular pixels. Each can have a different brightness, allowing us to describe
  the galaxy's bright clumps. Later, we will change the lens mass and foreground light to
  see how they affect the image.

Finding a model that matches the observations is called **lens modelling**. This can take
hours of computing time, so here we will explore an existing model fitted to the COSMOS-Web
Ring. It uses the same F444W data shown in the paper's figure above and is saved in a file
called `tracer.json`.

PyAutoLens calls this saved description a **tracer** because it calculates the paths light
takes through the lens system. Run the cell below to load it and display its main
measurements. In Colab, the cell first downloads the model files from GitHub.

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
**🤖 Ask AI:** "What is a power-law mass profile, and what does its slope tell us about a galaxy?"

__Explore The Model__

![The good model: the observations, the ring with the foreground light removed, the predicted ring and the reconstructed source](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/cosmos_web_ring_good_model.png)

To judge how well a model matches the image, look at the differences it leaves behind.
These differences are called **residuals**. We measure them relative to the noise in the
image, so values mostly between -3 and +3 are consistent with noise. Look for any remaining
shapes or patterns that might reveal something the model has missed.

PyAutoLens calculates how the lens bends the distant galaxy's light, adds the foreground
galaxy's light and accounts for the telescope's blurring. It then compares this predicted
image with the observations. Checking an existing model this way takes only a few seconds.

Run the cell below to see the comparison. Among the panels are the observed image, the model
image and the residuals.

The final panels show a **reconstruction** of the distant galaxy. By undoing the bending and
stretching of its light—a process called **delensing**—we can see what it would look like if
its light had not been bent by the foreground galaxy's gravity; that is, what the source
galaxy *truly* looks like.
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
print(f"Good model: fit score {float(fit.figure_of_merit):.2f} (3717.19 when it was fitted)")
print(f"Good model: reduced chi-squared {reduced_chi_squared:.2f}")

aplt.subplot_fit_imaging(fit=fit)
aplt.subplot_fit_imaging_of_planes(fit=fit, plane_index=1)

"""
The good model leaves small differences consistent with noise, with no obvious ring or
bright knots remaining. Its reconstruction reveals a compact, bright galaxy surrounded by
fainter clumps, seen when the Universe was barely a billion years old.

**Try changing the model.** The next cell starts with the Einstein radius increased by
0.1 arcseconds. This changes how strongly the lens bends light, so the predicted ring no
longer matches the observations. The source reconstruction stays fixed throughout this
experiment: we do not fit a new source to compensate for the change.

You can change two numbers at the top of the cell, then run it again:

- **`einstein_radius_offset`:** how much to add to the good model's Einstein radius, in
  arcseconds. Try `0.05` or `-0.05`, or set it to `0.0` to restore the original mass model.
- **`lens_light_scale`:** how bright to make the foreground galaxy's light. `1.0` keeps its
  original brightness. Try `1.2` to subtract too much light, or `0.8` to subtract too little.

Change one number at a time. The plots compare the original model with your changed version,
including the ring after subtracting the foreground light and the residuals on the same
colour scale. Set the numbers to `0.0` and `1.0` to recover the original model.
"""
einstein_radius_offset = 0.1  # Arcseconds added to the original Einstein radius.
lens_light_scale = 1.0  # 1.0 = original brightness; 1.2 = 20% brighter.


def changed_model_image(einstein_radius_offset, lens_light_scale):
    # Keep the source pixels and their brightnesses fixed: no new fit is performed.
    changed_tracer = deepcopy(tracer)
    changed_mass = changed_tracer.galaxies[0].mass
    changed_mass.einstein_radius = float(mass.einstein_radius) + einstein_radius_offset
    if not np.isfinite(changed_mass.einstein_radius) or changed_mass.einstein_radius <= 0:
        raise ValueError("Choose an offset that leaves the Einstein radius above zero.")
    if not np.isfinite(lens_light_scale) or lens_light_scale < 0:
        raise ValueError("Choose a finite, non-negative lens light scale.")

    mapper = fit.inversion.cls_list_from(cls=al.Mapper)[0]
    source_brightness = fit.inversion.reconstruction_dict[mapper]
    traced_grid = changed_tracer.traced_grid_2d_list_from(grid=fit.grids.pixelization)[-1]
    mesh = source_galaxy.pixelization.mesh
    traced_grid = mesh.relocated_grid_from(
        border_relocator=(dataset_good.grids.border_relocator
                          if fit.settings.use_border_relocator else None),
        source_plane_data_grid=traced_grid,
    )
    # Reuse the original source mesh, even when the light paths change.
    interpolator = type(mapper.interpolator)(
        mesh=mesh,
        mesh_grid=mapper.interpolator.mesh_grid,
        data_grid=traced_grid,
    )
    changed_mapper = al.Mapper(interpolator=interpolator, settings=fit.settings)
    blurred_mapping = dataset_good.psf.convolved_mapping_matrix_from(
        mapping_matrix=changed_mapper.mapping_matrix, mask=dataset_good.mask,
    )
    source_image = blurred_mapping @ source_brightness
    lens_image = np.asarray(fit.galaxy_model_image_dict[lens_galaxy])
    return al.Array2D(values=source_image + lens_light_scale * lens_image, mask=dataset.mask)


changed_image = changed_model_image(einstein_radius_offset, lens_light_scale)
changed_residuals = (dataset.data - changed_image) / dataset.noise_map
lens_image = fit.galaxy_model_image_dict[lens_galaxy]
model_max = float(np.max(fit.model_data))
subtracted_original = dataset.data - lens_image
subtracted_changed = dataset.data - lens_light_scale * lens_image
light_min = float(min(np.min(subtracted_original), np.min(subtracted_changed)))
light_max = float(max(np.max(subtracted_original), np.max(subtracted_changed)))

fig, axes = plt.subplots(2, 3, figsize=(15, 9))
for row, (label, model_image, light_scale, residuals) in enumerate([
    ("Original", fit.model_data, 1.0, fit.normalized_residual_map),
    ("Changed", changed_image, lens_light_scale, changed_residuals),
]):
    aplt.plot_array(array=model_image, title=f"{label}: model image",
                    use_log10=True, vmin=model_max / 1000, vmax=model_max, ax=axes[row, 0])
    aplt.plot_array(array=dataset.data - light_scale * lens_image,
                    title=f"{label}: light subtracted",
                    vmin=light_min, vmax=light_max, ax=axes[row, 1])
    aplt.plot_array(array=residuals, title=f"{label}: residuals", cb_unit=r"$\sigma$",
                    vmin=-5.0, vmax=5.0, ax=axes[row, 2])
plt.tight_layout()
plt.show()

print(f"Original Einstein radius: {float(mass.einstein_radius):.3f} arcsec")
print(f"Changed Einstein radius: {float(mass.einstein_radius) + einstein_radius_offset:.3f} arcsec")
print(f"Foreground light brightness: {lens_light_scale:.0%} of the original")

"""
Changing the mass moves the predicted ring; changing the foreground light leaves too much
or too little light near the centre. Both can leave patterns in the residuals. These patterns
help us identify where a model needs improvement.

The mass measurement in the next section uses the original good model, unaffected by your
experiments here.

**🤖 Ask AI:** "How do the residuals change when the lens mass is wrong, compared with when the foreground galaxy's light is too bright?"

__The Mass Inside The Ring__

![The ring with the lens galaxy's light removed, and the good model's Einstein radius drawn on it as a white circle](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/cosmos_web_ring_einstein_radius.png)

The picture above shows the ring with the foreground galaxy's light removed. The white line
marks the ring's size according to the original good model.

We describe this size using the **Einstein radius**. Together with the distances to the two
galaxies, it lets us calculate how much mass lies inside the ring. Those distances come from
the galaxies' redshifts.

Run the cell below to calculate the mass, expressed as a number of Suns. This uses the
original model, regardless of any changes you tried in the previous section.
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

"""
The ring encloses about **400 billion times the mass of the Sun**, mostly in stars and dark
matter. Our measurement of the Einstein radius also agrees with the value reported in the
discovery paper.

**🤖 Ask AI:** "How can a mass measurement from a lens include dark matter that we cannot see?"

__Where Next__

![The COSMOS-Web Ring](https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/docs/images/cosmos_web_ring_rgb.png)

You have explored a lens model, changed its ingredients and measured the mass inside the ring.
Here are some ways to continue:

- **Try lens modelling yourself.** Ask the PyAutoLens Assistant to "fit a lens model to the
  COSMOS-Web Ring". If you prefer to run Python directly, the reference script
  `scripts/cosmos_web_ring/fit_cosmos_web_ring.py` fits a simpler model in a few minutes on a GPU.
- **Explore through conversation.** Open Claude Code or Codex and paste the starting prompt from
  the top of this notebook. You can ask questions or suggest changes in plain language, such as
  "fit F150W as well" or "include the extra galaxy in the lens model".
- **Learn the foundations.** HowToLens (https://github.com/PyAutoLabs/HowToLens) introduces
  gravitational lensing and PyAutoLens step by step.
- **Explore more lenses.** COWLS, the COSMOS-Web Lens Survey (Nightingale et al. 2025,
  arXiv:2503.08777), studies this ring alongside other gravitational lenses.
- **Read the discovery study.** Mercier et al. 2024, Astronomy & Astrophysics 687, A61
  (https://ui.adsabs.harvard.edu/abs/2024A&A...687A..61M/abstract) presents the published
  analysis illustrated earlier in this notebook.

**How certain is the measurement?** This notebook calculates a mass from one saved model. To
estimate its uncertainty, we need to explore other models that could also explain the
observations.

The analysis that produced our model did this, but the fast reference script returns only one
best model. To calculate uncertainty ranges, such as the ±0.04 arcseconds quoted by Mercier et
al., follow the example in `scripts/imaging/modeling.py` in `autolens_workspace`.

**🤖 Ask AI:** "How do astronomers estimate the uncertainty in a lens model's mass measurement?"
"""
