"""
COSMOS-Web Ring: Explore The Committed Models
=============================================

The fast, no-inference route through the COSMOS-Web Ring that the greeting skill
(`skills/al_greeting_cosmos_web_ring.md`) uses for curious readers and students. Instead of
running a non-linear search (minutes to hours), it loads two lens models committed under
`scripts/cosmos_web_ring/results/` and evaluates them on the F444W data with `FitImaging`,
which takes seconds. It mirrors `docs/colab/cosmos_web_ring_colab.py`, so the assistant and
the Colab notebook tell the same story with the same numbers.

- **Good model** (`results/ansofi/`): MGE lens light, power-law mass plus external shear and a
  pixelized source, fitted by a Nautilus SLaM pipeline.
- **Poor model** (`results/sersic_source/`): the same data fitted with a single Sérsic source,
  the model a user gets by asking for "a simple source".

Every number printed and written to `summary.json` is computed here from the committed models;
none is quoted from memory. Run from the repository root:

    python scripts/cosmos_web_ring/explore_committed_models.py
    python scripts/cosmos_web_ring/explore_committed_models.py --einstein-radius-offset 0.1

__Contents__

- **Arguments:** Output folder and the optional "change the model" experiment.
- **Dataset:** Load F444W and prepare it as the Colab notebook does.
- **Good Model:** Evaluate the committed pixelized-source model.
- **Poor Model:** Evaluate the committed single-Sérsic-source model.
- **Mass Inside The Ring:** Turn the Einstein radius into a mass in Suns.
- **Figures:** The fit, the source, the Einstein radius and good-versus-poor residuals.
- **Change The Model:** Optionally shift the Einstein radius or rescale the lens light.
- **Summary:** Write `summary.json`.
"""

from autonerves import (
    jax_wrapper,
)  # noqa: F401  Sets the JAX environment before other imports

import argparse
import json
from copy import deepcopy
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

import autolens as al
import autolens.plot as aplt

"""
__Arguments__

`--einstein-radius-offset` and `--lens-light-scale` reproduce the Colab notebook's "Explore The
Model" experiment: the good model's Einstein radius is shifted (arcsec) and/or its lens light
rescaled, with the source reconstruction held fixed, so the reader sees the residuals a wrong
model leaves. Both default to "no change", in which case the experiment figure is skipped.
"""
REPO_ROOT = Path(__file__).resolve().parents[2]

parser = argparse.ArgumentParser(
    description="Evaluate the committed COSMOS-Web Ring models."
)
parser.add_argument(
    "--output-dir",
    type=Path,
    default=REPO_ROOT / "scripts" / "scratch" / "cosmos_web_ring" / "models",
)
parser.add_argument("--einstein-radius-offset", type=float, default=0.0)
parser.add_argument("--lens-light-scale", type=float, default=1.0)
args = parser.parse_args()

output_dir = args.output_dir
output_dir.mkdir(parents=True, exist_ok=True)

"""
__Dataset__

F444W with the bundled extra-galaxy noise scaling and a 2.1" circular mask, the mask both
committed models were evaluated on (`scripts/cosmos_web_ring/results/README.md`), plus the 4/2/2
radial light-profile over-sampling. Same preparation as `skills/al_prepare_imaging_data.md`
and the Colab notebook's "Preparing The Data".
"""
band_path = (
    REPO_ROOT / "dataset" / "imaging" / "cosmos_web_ring" / "wavebands" / "F444W"
)
results_path = REPO_ROOT / "scripts" / "cosmos_web_ring" / "results"
info = json.loads((band_path / "info.json").read_text())
pixel_scale = info["pixel_scale"]
redshift_lens = info["redshift_lens"]
redshift_source = info["redshift_source"]
mask_radius = 2.1

dataset = al.Imaging.from_fits(
    data_path=band_path / "data.fits",
    psf_path=band_path / "psf.fits",
    noise_map_path=band_path / "noise_map.fits",
    pixel_scales=pixel_scale,
)
mask_extra_galaxies = al.Mask2D.from_fits(
    file_path=band_path / "mask_extra_galaxies.fits",
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

"""
__Good Model__

The pixelized source needs its saved over-sampling, adapt image and image-plane mesh grid to be
evaluated exactly as it was fitted (`PyAutoLens:autolens/imaging/fit_imaging.py`).
"""


def masked_array_from(file_name):
    return al.Array2D(
        values=al.Array2D.from_fits(
            file_path=results_path / "ansofi" / file_name, pixel_scales=pixel_scale
        ).native,
        mask=mask,
    )


tracer = al.from_json(file_path=results_path / "ansofi" / "tracer.json")
lens_galaxy, source_galaxy = tracer.galaxies
mass = lens_galaxy.mass
shear = tracer.fields[0].shear

adapt_images = al.AdaptImages(
    galaxy_image_dict={source_galaxy: masked_array_from("source_adapt_image.fits")},
    galaxy_image_plane_mesh_grid_dict={
        source_galaxy: al.from_json(
            file_path=results_path / "ansofi" / "source_mesh_grid.json"
        )
    },
)
dataset_good = dataset.apply_over_sampling(
    over_sample_size_pixelization=masked_array_from(
        "over_sample_size_pixelization.fits"
    )
)
fit = al.FitImaging(dataset=dataset_good, tracer=tracer, adapt_images=adapt_images)
reduced_chi_squared_good = float(fit.chi_squared) / n_masked_pixels

"""
__Poor Model__

A single linear Sérsic source cannot describe a clumpy z ~ 5 galaxy: the ring comes out about
the right size, but the bright knots are left in the residuals.
"""
tracer_poor = al.from_json(file_path=results_path / "sersic_source" / "tracer.json")
fit_poor = al.FitImaging(dataset=dataset, tracer=tracer_poor)
reduced_chi_squared_poor = float(fit_poor.chi_squared) / n_masked_pixels

"""
__Mass Inside The Ring__

M_E = Sigma_crit x (area inside the tangential critical curve), with Sigma_crit from the two
redshifts in a Planck15 cosmology (`PyAutoGalaxy:autogalaxy/cosmology/model.py`) and the
effective Einstein radius from `al.LensCalc` (`PyAutoGalaxy:autogalaxy/operate/lens_calc.py`).
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
einstein_mass = sigma_crit * float(
    lens_calc.einstein_mass_angular_from(grid=evaluation_grid)
)
critical_curves = lens_calc.tangential_critical_curve_list_from(grid=evaluation_grid)
einstein_radius_kpc = einstein_radius_effective * kpc_per_arcsec

"""
__Figures__

- `fit_good.png` / `fit_poor.png` — data, model, residuals and source for each model.
- `source_good.png` — the good model plane by plane: the ring with the lens light removed, the
  model ring and the reconstructed (delensed) source galaxy.
- `einstein_radius.png` — the lens-light-subtracted ring with the tangential critical curve.
- `good_vs_poor.png` — model images and normalised residuals of both models, on shared scales.
"""
aplt.subplot_fit_imaging(fit=fit, output_path=str(output_dir), output_format="png")
(output_dir / "fit.png").replace(output_dir / "fit_good.png")
aplt.subplot_fit_imaging(fit=fit_poor, output_path=str(output_dir), output_format="png")
(output_dir / "fit.png").replace(output_dir / "fit_poor.png")
aplt.subplot_fit_imaging_of_planes(
    fit=fit, plane_index=1, output_path=str(output_dir), output_format="png"
)
(output_dir / "fit_of_plane_1.png").replace(output_dir / "source_good.png")

figure, ax = plt.subplots(1, 1, figsize=(6, 5))
aplt.plot_array(
    array=fit.subtracted_images_of_planes_list[1],
    title=f'Einstein radius {einstein_radius_effective:.2f}"',
    lines=[curve.array for curve in critical_curves],
    line_colors=["white"] * len(critical_curves),
    ax=ax,
)
plt.tight_layout()
figure.savefig(output_dir / "einstein_radius.png", dpi=150, facecolor="white")
plt.close(figure)

model_max = float(np.max(fit.model_data))
figure, axes = plt.subplots(2, 2, figsize=(12, 10))
for row, (label, a_fit, chi2) in enumerate(
    [
        ("Good", fit, reduced_chi_squared_good),
        ("Poor", fit_poor, reduced_chi_squared_poor),
    ]
):
    aplt.plot_array(
        array=a_fit.model_data,
        title=f"{label} model",
        use_log10=True,
        vmin=model_max / 1000,
        vmax=model_max,
        ax=axes[row, 0],
    )
    aplt.plot_array(
        array=a_fit.normalized_residual_map,
        title=f"{label}: residuals, reduced $\\chi^2$ {chi2:.2f}",
        cb_unit=r"$\sigma$",
        vmin=-5.0,
        vmax=5.0,
        ax=axes[row, 1],
    )
plt.tight_layout()
figure.savefig(output_dir / "good_vs_poor.png", dpi=150, facecolor="white")
plt.close(figure)

"""
__Change The Model__

The Colab notebook's experiment, unchanged: the source pixels and their brightnesses are held
fixed (no new fit), the light is re-traced through the changed mass, blurred by the PSF and
added to the rescaled lens light.
"""
changed = args.einstein_radius_offset != 0.0 or args.lens_light_scale != 1.0
if changed:
    if not np.isfinite(args.lens_light_scale) or args.lens_light_scale < 0:
        raise ValueError("Choose a finite, non-negative lens light scale.")
    changed_tracer = deepcopy(tracer)
    changed_mass = changed_tracer.galaxies[0].mass
    changed_mass.einstein_radius = (
        float(mass.einstein_radius) + args.einstein_radius_offset
    )
    if (
        not np.isfinite(changed_mass.einstein_radius)
        or changed_mass.einstein_radius <= 0
    ):
        raise ValueError("Choose an offset that leaves the Einstein radius above zero.")

    mapper = fit.inversion.cls_list_from(cls=al.Mapper)[0]
    source_brightness = fit.inversion.reconstruction_dict[mapper]
    traced_grid = changed_tracer.traced_grid_2d_list_from(grid=fit.grids.pixelization)[
        -1
    ]
    mesh = source_galaxy.pixelization.mesh
    traced_grid = mesh.relocated_grid_from(
        border_relocator=(
            dataset_good.grids.border_relocator
            if fit.settings.use_border_relocator
            else None
        ),
        source_plane_data_grid=traced_grid,
    )
    interpolator = type(mapper.interpolator)(
        mesh=mesh, mesh_grid=mapper.interpolator.mesh_grid, data_grid=traced_grid
    )
    changed_mapper = al.Mapper(interpolator=interpolator, settings=fit.settings)
    blurred_mapping = dataset_good.psf.convolved_mapping_matrix_from(
        mapping_matrix=changed_mapper.mapping_matrix, mask=dataset_good.mask
    )
    lens_image = fit.galaxy_model_image_dict[lens_galaxy]
    changed_image = al.Array2D(
        values=blurred_mapping @ source_brightness
        + args.lens_light_scale * np.asarray(lens_image),
        mask=dataset.mask,
    )
    changed_residuals = (dataset.data - changed_image) / dataset.noise_map

    subtracted_original = dataset.data - lens_image
    subtracted_changed = dataset.data - args.lens_light_scale * lens_image
    light_min = float(min(np.min(subtracted_original), np.min(subtracted_changed)))
    light_max = float(max(np.max(subtracted_original), np.max(subtracted_changed)))

    figure, axes = plt.subplots(2, 3, figsize=(15, 9))
    for row, (label, model_image, light_scale, residuals) in enumerate(
        [
            ("Original", fit.model_data, 1.0, fit.normalized_residual_map),
            ("Changed", changed_image, args.lens_light_scale, changed_residuals),
        ]
    ):
        aplt.plot_array(
            array=model_image,
            title=f"{label}: model image",
            use_log10=True,
            vmin=model_max / 1000,
            vmax=model_max,
            ax=axes[row, 0],
        )
        aplt.plot_array(
            array=dataset.data - light_scale * lens_image,
            title=f"{label}: light subtracted",
            vmin=light_min,
            vmax=light_max,
            ax=axes[row, 1],
        )
        aplt.plot_array(
            array=residuals,
            title=f"{label}: residuals",
            cb_unit=r"$\sigma$",
            vmin=-5.0,
            vmax=5.0,
            ax=axes[row, 2],
        )
    plt.tight_layout()
    figure.savefig(output_dir / "changed_model.png", dpi=150, facecolor="white")
    plt.close(figure)

"""
__Summary__

The reduced chi-squared is chi-squared over the number of pixels inside the mask, the
definition `scripts/cosmos_web_ring/results/README.md` uses.
"""
summary = {
    "mask_radius": mask_radius,
    "n_masked_pixels": n_masked_pixels,
    "good_model": {
        "source": f"{type(source_galaxy.pixelization.mesh).__name__} pixelization, "
        f"{source_galaxy.pixelization.mesh.pixels} pixels",
        "mass": type(mass).__name__,
        "einstein_radius_parameter": float(mass.einstein_radius),
        "slope": float(mass.slope),
        "shear_magnitude": float(np.hypot(shear.gamma_1, shear.gamma_2)),
        "reduced_chi_squared": reduced_chi_squared_good,
    },
    "poor_model": {
        "source": "single linear Sersic",
        "einstein_radius_parameter": float(
            tracer_poor.galaxies[0].mass.einstein_radius
        ),
        "reduced_chi_squared": reduced_chi_squared_poor,
    },
    "einstein_radius_effective_arcsec": einstein_radius_effective,
    "einstein_radius_kpc": einstein_radius_kpc,
    "einstein_radius_light_years": einstein_radius_kpc * 3261.56,
    "einstein_mass_solar_masses": einstein_mass,
    "cosmology": "Planck15",
    "changed_model": (
        {
            "einstein_radius_offset": args.einstein_radius_offset,
            "lens_light_scale": args.lens_light_scale,
            "reduced_chi_squared": float(np.sum(np.asarray(changed_residuals) ** 2))
            / n_masked_pixels,
        }
        if changed
        else None
    ),
}
(output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
print(f"Figures and summary written to: {output_dir.resolve()}")
