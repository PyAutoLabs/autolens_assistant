---
name: al_simulate_dataset
description: Synthesise a strong-lens imaging or interferometer dataset from a ground-truth Tracer (lens + source galaxies, redshifts, light + mass profiles). Writes data / noise / PSF FITS files plus a tracer.json to a dataset folder. Use when the user wants a controlled test dataset, a training sample for an ML pipeline, or a sanity check that a model can recover known inputs. For modelling an *existing* dataset see `al_prepare_imaging_data` instead.
---

# Simulating a strong-lens dataset

When you want to validate a modelling pipeline against a known truth — or build a
training set for neural-network classifiers — you synthesise a dataset from a
ground-truth `Tracer`. The simulator ray-traces the source through the lens galaxy's
mass, applies the PSF, adds Poisson + background noise, and writes the result to
FITS.

The canonical example is `autolens_workspace:scripts/imaging/simulator.py`. This
skill produces the equivalent for your specific model.

## Ask

- *"What kind of lens are you simulating — single galaxy-scale, group, cluster?
  Imaging or interferometer?"* — chooses the branch.
- *"What's the ground truth?"* — lens redshift, source redshift, mass profile (SIE? +
  external shear?), lens light (Sersic?), source light (Sersic? compact?).
- *"What instrument are you mimicking?"* — pixel scale, FoV, PSF FWHM, exposure
  time / background level.

## Branch — galaxy-scale imaging

```python
# work/simulate_imaging.py
from autoconf import jax_wrapper
from pathlib import Path
import autolens as al
import autolens.plot as aplt

dataset_path = Path("dataset/imaging/synthetic_galaxy_lens")
dataset_path.mkdir(parents=True, exist_ok=True)

# 1. Grid — defines the simulated image's shape and pixel scale.
grid = al.Grid2D.uniform(shape_native=(150, 150), pixel_scales=0.06)
over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=grid, sub_size_list=[8, 4, 2], radial_list=[0.3, 0.6], centre_list=[(0.0, 0.0)]
)
grid = grid.apply_over_sampling(over_sample_size=over_sample_size)

# 2. Ground-truth Tracer — lens galaxy (light + mass) + source galaxy (light).
lens = al.Galaxy(
    redshift=0.5,
    bulge=al.lp.Sersic(centre=(0.0, 0.0), ell_comps=(0.1, 0.0), intensity=4.0,
                       effective_radius=0.8, sersic_index=2.5),
    mass=al.mp.Isothermal(centre=(0.0, 0.0), ell_comps=(0.1, 0.05), einstein_radius=1.2),
    shear=al.mp.ExternalShear(gamma_1=0.05, gamma_2=0.0),
)
source = al.Galaxy(
    redshift=1.0,
    bulge=al.lp.SersicCore(centre=(0.1, 0.1), ell_comps=(0.0, 0.0), intensity=0.3,
                           effective_radius=0.1, sersic_index=1.0, radius_break=0.025),
)
tracer = al.Tracer(galaxies=[lens, source])

# 3. PSF + simulator. Match your target instrument (HST/JWST/Euclid have different
#    PSF FWHM and pixel scale).
psf = al.Convolver.from_gaussian(shape_native=(11, 11), sigma=0.05,
                                 pixel_scales=grid.pixel_scales)

simulator = al.SimulatorImaging(
    exposure_time=300.0,
    psf=psf,
    background_sky_level=0.1,
    add_poisson_noise_to_data=True,
)

dataset = simulator.via_tracer_from(tracer=tracer, grid=grid)

# 4. Persist.
dataset.output_to_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    psf_path=dataset_path / "psf.fits",
    overwrite=True,
)

# Save the ground truth so we can verify recovery later.
al.output_to_json(obj=tracer, file_path=dataset_path / "tracer.json")

# 5. Preview plot — saved to work/plots/<dataset_name>/ for inspection.
plot_dir = Path("work/plots") / dataset_path.name
plot_dir.mkdir(parents=True, exist_ok=True)
aplt.ImagingPlotter(
    dataset=dataset,
    mat_plot_2d=aplt.MatPlot2D(
        output=aplt.Output(path=str(plot_dir), filename="simulated_dataset", format="png"),
    ),
).subplot_dataset()

print(f"FITS written to: {dataset_path.resolve()}")
print(f"Preview plot saved to: {plot_dir.resolve()}")
```

Source citations:
- `PyAutoLens:autolens/imaging/simulator.py` — `SimulatorImaging.via_tracer_from`.
- `PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic.py` — Sersic profile.
- `PyAutoGalaxy:autogalaxy/profiles/mass/total/isothermal.py` — Isothermal SIE.

Read [`wiki/core/concepts/tracer.md`](../wiki/core/concepts/tracer.md) for how the `Tracer`
ray-traces source positions through the mass model, and
[`wiki/core/api/light_profile_catalog.md`](../wiki/core/api/light_profile_catalog.md) /
[`wiki/core/api/mass_profile_catalog.md`](../wiki/core/api/mass_profile_catalog.md) for the
full menu of profiles you can swap in.

## Branch — many simulated datasets (training sample)

For ML training sets, wrap the above in a loop, vary the ground-truth parameters per
iteration, and write each into its own `dataset_<i>/` subfolder. The pattern is in
`autolens_workspace:scripts/imaging/simulator_sample.py`.

## Branch — interferometer

Substitute `al.Grid2D.uniform` with a `uv_wavelengths` array of (u, v) coordinates from
your interferometer, and use `al.SimulatorInterferometer` instead of
`SimulatorImaging`. The `Tracer` build is identical. See
`PyAutoLens:autolens/interferometer/simulator.py` and
`autolens_workspace:scripts/interferometer/simulator.py`.

## Combine

After simulating:

- Fit the simulated dataset with [`al_build_imaging_model`](./al_build_imaging_model.md)
  → [`al_run_search`](./al_run_search.md). Compare the recovered posterior to the
  ground-truth `tracer.json` to verify your pipeline.
- Generate a sample of N datasets and use the database utilities in PyAutoFit to query
  aggregate behaviour — see `PyAutoFit:autofit/aggregator/`.

## Further reading

- **Student / new to lensing** — [HowToLens: Critical curves, caustics, cosmological
  coordinates](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_3_more_ray_tracing.ipynb):
  ray-tracing through to caustics and physical (kpc) coordinates — the forward physics
  the simulator runs.
- **General reference** — [RTD: Start here](https://pyautolens.readthedocs.io/en/latest/overview/overview_1_start_here.html):
  core PyAutoLens concepts in practice — grids, profiles, ray-tracing with `Tracer`.
- **Experienced PyAutoLens user** — [workspace/lens: imaging/simulators/start_here.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/imaging/simulators/start_here.py):
  canonical instrument-realistic simulation when no real data are on hand.
