---
name: al_build_imaging_model
description: Compose a strong-lens model for imaging data — galaxies with light + mass profiles, prior customisation, and an `al.AnalysisImaging` ready to hand to a non-linear search. Writes a runnable Python script in ./work/. Pairs with `al_prepare_imaging_data` (which loads + masks the dataset) and `al_run_search` (which executes the fit). For visibility-plane data see `al_build_interferometer_model`.
---

# Composing an imaging lens model

The model is the PyAuto\* representation of *what kind of lens you think this is* — how
many galaxies, at what redshifts, with what light and mass parameterisations, with
which parameters free and which fixed. Building one is the step between "I have a
loaded `Imaging` dataset" and "I'm running a non-linear search".

The canonical example is `autolens_workspace:scripts/imaging/modeling.py`. This skill
generates the equivalent for the user's lens.

## Ask

- *"How many galaxies in the model — single galaxy-scale, group (2–4), cluster?"* —
  this is the only structural choice. Skill below assumes galaxy-scale; bootstrap a
  variant for groups/clusters via `_bootstrap_skill` if needed.
- *"What's the lens light parameterisation — a single Sersic, MGE (multi-Gaussian
  expansion), bulge + disk, or no lens light at all (mass-only)?"*
- *"What's the lens mass — Isothermal (SIE) + ExternalShear is the standard starting
  point; PowerLaw or NFW for total or dark-matter-only models."*
- *"What's the source — parametric Sersic, MGE, or pixelised inversion?"* — pixelised
  needs a different `Analysis` wiring; see [`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md).
- *"What are the lens and source redshifts?"* — needed for distance ratios; even a
  ballpark value works for relative-comparison runs.

## Branch — galaxy-scale, Sersic light + SIE mass + Sersic source

The minimum viable model. Save to `work/build_model.py`:

```python
# work/build_model.py
from autoconf import jax_wrapper
import autofit as af
import autolens as al

# Lens light — a Sersic for the bulge.
lens_bulge = af.Model(al.lp.Sersic)

# Lens mass — SIE + external shear.
lens_mass = af.Model(al.mp.Isothermal)
lens_shear = af.Model(al.mp.ExternalShear)

lens = af.Model(
    al.Galaxy,
    redshift=0.5,
    bulge=lens_bulge,
    mass=lens_mass,
    shear=lens_shear,
)

# Source light — a single Sersic.
source = af.Model(
    al.Galaxy,
    redshift=1.0,
    bulge=af.Model(al.lp.SersicCore),
)

# Compose into a Collection.
model = af.Collection(
    galaxies=af.Collection(lens=lens, source=source)
)

# Optional: customise priors. E.g. tighten the lens centre.
lens_mass.centre.centre_0 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)
lens_mass.centre.centre_1 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)

print(model.info)
```

Source citations:
- `PyAutoGalaxy:autogalaxy/galaxy/galaxy.py` — `Galaxy`.
- `PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic.py` — `Sersic`, `SersicCore`.
- `PyAutoGalaxy:autogalaxy/profiles/mass/total/isothermal.py` — `Isothermal`.
- `PyAutoFit:autofit/mapper/prior_model/prior_model.py` — `af.Model`.
- `PyAutoFit:autofit/mapper/prior_model/collection.py` — `af.Collection`.

Wiki:
- [`wiki/core/concepts/light_profiles.md`](../wiki/core/concepts/light_profiles.md) — what each
  light profile represents and when to pick which.
- [`wiki/core/concepts/mass_profiles.md`](../wiki/core/concepts/mass_profiles.md) — same for mass.
- [`wiki/core/concepts/galaxy_and_plane.md`](../wiki/core/concepts/galaxy_and_plane.md) — how
  galaxies, redshifts, and the `Tracer` fit together.

## Branch — linear (MGE) lens light

For complex lens galaxy morphologies, replace the single Sersic bulge with a Multi-
Gaussian Expansion of *linear* light profiles. Linear profiles have their
*intensities* solved analytically inside the fit, so the search only varies
shape parameters — far fewer dimensions, much better convergence.

```python
n_gaussians = 30
gaussian_per_basis = [
    af.Model(al.lp_linear.Gaussian) for _ in range(n_gaussians)
]
# Tie centres + ellipticities across the basis; let only sigma + intensity vary.
for g in gaussian_per_basis[1:]:
    g.centre = gaussian_per_basis[0].centre
    g.ell_comps = gaussian_per_basis[0].ell_comps

lens_bulge = af.Model(al.lp_basis.Basis, profile_list=gaussian_per_basis)
```

See `PyAutoGalaxy:autogalaxy/profiles/light_linear/` for the linear-profile classes.

## Branch — pixelised source

For sources with complex morphology (lensed arcs, multiple components), reconstruct
the source on a pixel grid rather than as a parametric Sersic. The model wiring is
different: the source `Galaxy` carries a `Pixelization`, and the `Analysis` needs a
positions likelihood penalty to keep the inversion well-posed.

See [`al_inspect_source_reconstruction`](./al_inspect_source_reconstruction.md) for
the full pattern.

## Wrap with an analysis

Once the model is built, wrap your loaded `dataset` (from `al_prepare_imaging_data`)
in an analysis object:

```python
analysis = al.AnalysisImaging(dataset=dataset)
```

Source: `PyAutoLens:autolens/imaging/model/analysis.py`.

`analysis` + `model` are the two inputs to the non-linear search. Pass them to
[`al_run_search`](./al_run_search.md).

## Combine

Natural next steps:

- [`al_configure_search`](./al_configure_search.md) — pick Nautilus (default), Dynesty,
  Emcee, or another search; tune live points / walkers.
- [`al_run_search`](./al_run_search.md) — `search.fit(model=model, analysis=analysis)`.
- [`al_chain_searches`](./al_chain_searches.md) — chain a fast Sersic source fit into
  a slower pixelised one, inheriting priors.
