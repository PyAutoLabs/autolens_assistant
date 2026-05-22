---
name: al_load_results
description: Load a completed PyAutoLens fit's results from its output folder via the .json, .csv and .fits files. Use when a user wants to inspect, plot, or further analyse one (or a handful of) completed fits by pointing at the output directory. For bulk analysis of >100 fits use PyAutoFit's aggregator/database — see `wiki/core/concepts/samples_and_posteriors.md` and bootstrap a dedicated skill if needed.
---

# Loading a finished lens model fit

This skill helps a user pull a completed PyAutoLens fit back into memory and start
interpreting it. It's the entry point for *"the search finished — what did it learn
about my lens system?"*

Loading is rarely the goal in itself. The user already wants to look at *something*:
the mass model, the source reconstruction, the residuals, the posterior, or a
comparison to another fit. The skill's job is to figure out which, load only what's
needed, and route the user into the relevant wiki page.

## Orient

Loading results means taking the output folder that `search.fit(...)` wrote
(typically `output/imaging/<dataset>/modeling/<unique_hash>/`) and reconstructing the
lens model objects from disk. By default, what comes back describes the **maximum
log-likelihood** result — the single best-fitting model the search found. The full
posterior is in `files/samples.csv`, loadable as a `Samples` object.

The common file-to-object mappings:

| File | Object | What it is |
|---|---|---|
| `files/tracer.json` | `Tracer` | Max-log-likelihood lens model |
| `files/model.json` | `af.Collection` | The fitted model definition |
| `files/samples.csv` | `Samples` | Full posterior |
| `image/dataset.fits` | `Imaging` / `Interferometer` | The dataset |
| `image/fit.fits` | arrays | Model image, residuals, chi-squared map |

Loaded objects can be recombined into a fit on demand. For example
`al.FitImaging(dataset=dataset, tracer=tracer)` rebuilds the full `FitImaging` so you
can inspect linear-profile intensities, inversion outputs, log likelihood — none of
which live inside `tracer.json` alone.

## Ask

Before loading, ask what the user wants:

- *"The **mass model** — deflection field, convergence, Einstein radius?"*
- *"The **source** — its reconstruction or pixelised inversion?"*
- *"The **posterior** — errors on parameters, median values, covariances?"*
- *"**Fit quality** — residuals, chi-squared, model images?"*
- *"**Compare** to another run?"*

And the path: something like `output/imaging/<dataset>/modeling/<hash>/`. If they
point at a parent, list its contents and ask which sub-folder.

## Branch — lens / mass model (`Tracer`)

The `Tracer` is PyAutoLens's lens system representation: an ordered set of `Galaxy`
objects with their light, mass profiles and redshifts. Operationally, it knows how
to compute deflections, convergence, magnification, critical curves, and ray-trace.

```python
from autoconf.dictable import from_json
tracer = from_json(file_path=".../files/tracer.json")
```

For everything you can do with a `Tracer` — model images, ray tracing, convergence /
potential / deflection arrays, accessing `tracer.galaxies` — read
[`wiki/core/concepts/tracer.md`](../wiki/core/concepts/tracer.md). Don't mutate the loaded
tracer in place; if the user wants a modified version, build a new `al.Tracer` from
copied galaxies so the original max-log-likelihood result stays intact.

Source: `PyAutoLens:autolens/lens/tracer.py`.

## Branch — individual galaxies / profile components

Pulling one galaxy or one profile out of the tracer is common. The `tracer.galaxies`
list (or `tracer.planes` for multi-plane systems) gives them to you. Each `Galaxy`
exposes its light and mass profiles via attribute access matching the names you used
in the model.

```python
lens = tracer.galaxies[0]
einstein_radius_arcsec = lens.mass.einstein_radius  # for parametric mass
# Or compute it numerically from the convergence:
einstein_mass = tracer.einstein_mass_angular_from(grid=dataset.grid)
```

For the API surface, read [`wiki/core/concepts/galaxy_and_plane.md`](../wiki/core/concepts/galaxy_and_plane.md).

## Branch — posterior (`Samples`)

The `Samples` object holds every accepted sample from the search. Use it for
parameter errors, posterior medians, and uncertainty propagation on derived
quantities.

```python
import autofit as af
model = from_json(file_path=".../files/model.json")
samples = af.SamplesNest.from_table(filename=".../files/samples.csv", model=model)

median = samples.median_pdf()
upper = samples.values_at_upper_sigma(sigma=1.0)
lower = samples.values_at_lower_sigma(sigma=1.0)
```

For what you can do — corner plots, propagating errors to derived quantities,
covariance matrices — read [`wiki/core/concepts/samples_and_posteriors.md`](../wiki/core/concepts/samples_and_posteriors.md).

**Linear light profile intensities and inversion quantities are solved during the fit, not sampled.** To get them with uncertainties you have to recreate the fit
object (next branch).

## Branch — model-vs-data (`FitImaging`)

For residuals, chi-squared maps, normalised residuals, or per-galaxy model images,
build a fit object. Two paths:

**Static (saved FITS).** Load `image/fit.fits` as `al.Array2D.from_fits(...)`. Fast,
read-only.

**Live recreate.** Load the dataset and tracer, then build a fresh fit:

```python
fit = al.FitImaging(dataset=dataset, tracer=tracer)
aplt.FitImagingPlotter(fit=fit).subplot_fit()
```

Use the live path when you need linear intensities, inversion state, or to recompute
log likelihood on a modified input.

For plotting, [`al_plot_fit_residuals`](./al_plot_fit_residuals.md).

## Branch — pixelised source

A pixelised source reconstruction is a property of the `FitImaging`, not the
`Tracer`. You need to rebuild the fit and then inspect the inversion. See
[`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md).

## Branch — physical units

PyAutoLens reports angular units (arcseconds, dimensionless lensing quantities). For
kpc, solar masses, Einstein masses → read
[`wiki/core/concepts/cosmology_and_units.md`](../wiki/core/concepts/cosmology_and_units.md) and
use the cosmology + redshift conversions documented there.

When quoting a number, be explicit about the unit. *"Einstein radius = 1.2 arcsec"*
is fine; *"Einstein radius = 1.2"* is a bug.

## Combine

- [`al_plot_tracer`](./al_plot_tracer.md) — critical curves, caustics, magnification
  maps from the loaded tracer.
- [`al_plot_fit_residuals`](./al_plot_fit_residuals.md) — fit quality plots from a
  rebuilt FitImaging.
- [`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md) —
  pixelised inversion diagnostics.

## Sharing a fit

The whole `output/imaging/<dataset>/modeling/<hash>/` folder is portable. A
collaborator with a compatible PyAutoLens environment can load it the same way you
just did. The files that matter for them are `files/*.json`, `files/samples.csv`, the
`image/*.fits` products, and the human-readable `model.info` and `model.results`.

## Output folder reference

```
output/imaging/<dataset>/modeling/<unique_hash>/
    files/
        tracer.json
        model.json
        samples.csv
        samples_summary.json
        search.json
        cosmology.json
        covariance.csv
    image/
        dataset.fits
        fit.fits
        tracer.fits
        source_plane_images.fits
        model_galaxy_images.fits
        galaxy_images.fits
    model.info
    model.results
    search.summary
```

Sub-paths vary for interferometer / multi-wavelength fits.
