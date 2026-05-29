---
title: Samples and posteriors
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/samples/
      - autofit/non_linear/result.py
      - autofit/aggregator/
    pinned_commit: main
last_updated: 2026-05-22
---

# Samples and posteriors

After a non-linear search completes, the posterior on the model parameters is
captured in a `Samples` object. PyAutoFit exposes it as `result.samples` from a
live fit, or via `af.SamplesNest.from_table(...)` when loading from disk.

Source: `PyAutoFit:autofit/non_linear/samples/`.

## What a Samples object holds

- Every accepted sample's parameter values.
- Every sample's log-likelihood and log-evidence (for nested-sampler outputs).
- The model definition (so values can be unflattened into named structure).
- Sampler-specific metadata (acceptance fractions, evidence, etc.).

The flavour of `Samples` depends on the search:

- **`SamplesNest`** — nested-sampler output (Nautilus, Dynesty, UltraNest).
- **`SamplesMCMC`** — Emcee, Zeus.
- **`SamplesMLE`** — BFGS, PySwarms, Drawer.

All share the same accessor API.

## Loading from a finished fit

```python
from autoconf.dictable import from_json
import autofit as af

model = from_json(file_path=".../files/model.json")
samples = af.SamplesNest.from_table(
    filename=".../files/samples.csv",
    model=model,
)
```

For the live fit (in the same process that ran `search.fit`):

```python
samples = result.samples
```

## Common queries

```python
# Single best-fitting parameter instance.
best = samples.max_log_likelihood()

# Posterior median.
median = samples.median_pdf()

# Sigma-level bounds.
upper = samples.values_at_upper_sigma(sigma=1.0)
lower = samples.values_at_lower_sigma(sigma=1.0)

# Errors at a sigma level.
errors_up = samples.errors_at_upper_sigma(sigma=1.0)
errors_low = samples.errors_at_lower_sigma(sigma=1.0)

# Random draw from the posterior.
draw = samples.draw_randomly_via_pdf()
```

`max_log_likelihood`, `median_pdf`, and draws return **instances** — i.e. the model
with parameters filled in, traversable via attribute access:

```python
best.galaxies.lens.mass.einstein_radius   # 1.234
```

`values_at_*` and `errors_at_*` return dictionaries keyed by the same attribute path
but flattened.

## Derived quantities with uncertainties

The posterior covers the *sampled* parameters. For derived quantities — Einstein
mass, mass-to-light ratio, half-light radius after deconvolution, etc. — recompute
the quantity for every sample and aggregate.

```python
import numpy as np

einstein_masses = []
for params in samples.parameter_lists:
    instance = model.instance_from_vector(vector=params)
    tracer = al.Tracer(galaxies=instance.galaxies)
    einstein_masses.append(tracer.einstein_mass_angular_from(grid=grid))

print(f"E.M. = {np.median(einstein_masses):.3e} ± {np.std(einstein_masses):.3e}")
```

For physical-unit conversions, [`cosmology_and_units`](./cosmology_and_units.md).

## Linear / inversion quantities

Linear light profile intensities, pixelised source amplitudes, and other inversion
solutions are *not* in `samples.csv`. They're solved during the fit and depend on
the dataset.

To get a linear intensity with an uncertainty, recreate the `FitImaging` for many
posterior draws and read `fit.linear_light_profile_intensity_dict` (or equivalent)
per draw. See `PyAutoLens:autolens/imaging/fit_imaging.py`.

## Bulk analysis — the aggregator

For hundreds of fits, don't load each `samples.csv` into memory at once. Use the
aggregator:

```python
import autofit as af

agg = af.Aggregator(af.db.open_database("sqlite://"))
agg.add_directory("output/imaging/my_sample/")

for samples in agg.values("samples"):
    print(samples.median_pdf().galaxies.lens.mass.einstein_radius)
```

The aggregator yields one fit at a time, so memory is bounded. For really large
samples (>1000 fits) PyAutoFit also provides a SQLAlchemy database backend; see
`PyAutoFit:autofit/database/`.

## See also

- [`non_linear_search`](./non_linear_search.md) — what generates `samples`.
- [`../../../skills/al_load_results.md`](../../../skills/al_load_results.md) — loading a
  saved fit.
- [`cosmology_and_units`](./cosmology_and_units.md) — propagating to physical units.
