---
title: Substructure and subhaloes in strong lenses
sources:
  - project: PyAutoLens
    paths:
      - autolens/lens
      - autolens/lens/los.py
    pinned_commit: main
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/mass/dark
    pinned_commit: main
last_updated: 2026-07-09
---

# Substructure and subhaloes

Cold dark matter predicts
many low-mass subhaloes orbiting every massive lens galaxy. Strong-lens
images encode this substructure: a smooth mass model leaves coherent
residuals; an added perturber matches them. Detection (and non-detection
calibrated by sensitivity) constrains the dark-matter halo mass
function — the strongest astrophysical probe of CDM-vs-WDM-vs-fuzzy DM at
sub-galaxy scales.

## Why strong lenses probe substructure

Strong lenses are sensitive to substructure because the lensed images sit
close to critical curves, where the magnification tensor is large. A
small perturbation to the potential can therefore imprint a visible
signal even when the perturber is far too faint to detect in light.

Different observables probe different perturbation scales:

- image positions respond to relatively large perturbations
- flux ratios respond to very compact perturbations near the images
- resolved arcs and rings respond to perturbers that bend the local arc
  morphology or leave coherent residuals in a pixelized source fit

This is why high-resolution imaging and flexible source reconstructions
matter so much. The classic literature path is flux-ratio anomalies
(Mao and Schneider; Dalal and Kochanek) through to gravitational imaging
(Vegetti and Koopmans).

## Detection statistic — Bayesian model comparison

PyAutoLens treats detection as a model-comparison problem. You fit the
same dataset twice:

- a baseline model with a smooth lens potential
- a perturbed model with an extra mass component

The key statistic is the evidence difference `Delta ln Z`. The exact
threshold is science-case dependent, but the qualitative interpretation is
stable:

- small positive values mean "interesting, worth follow-up"
- large positive values mean the data genuinely prefer the perturber
- values near zero or negative mean the smooth model is sufficient

This framing automatically penalizes overly flexible perturber models, so
the evidence map is much more useful than a raw chi-squared improvement.

## Grid-search workflow

The standard workflow is a grid search over candidate perturber
locations, often with a mass or normalization axis as well. For each
cell:

1. place the perturber at that trial position
2. refit the smooth lens plus source parameters
3. record the evidence difference relative to the baseline fit

The output is an evidence map over `(y, x)` or `(y, x, mass)` space.
Peaks identify candidate perturber locations, after which a local free
fit refines the subhalo parameters. This is exactly the workflow behind
[`../../../skills/al_subhalo_detect.md`](../../../skills/al_subhalo_detect.md)
and the corresponding workspace examples.

## Sensitivity calibration

Every non-detection must be calibrated. "No subhalo found" only constrains
dark matter if you know what masses and positions the data would have
detected had they been present. That calibration is the sensitivity map:
simulate the same dataset with injected perturbers, refit, and record
where the evidence gain would have crossed your detection threshold.

Cross-reference [`sensitivity_mapping`](./sensitivity_mapping.md).

## Line-of-sight haloes vs. subhaloes

Not every perturber belongs to the main lens halo. A foreground or
background halo along the line of sight can produce a similar residual
pattern. The distinction matters physically because a line-of-sight halo
traces the cosmological halo population, not the host's subhalo
population.

PyAutoLens supports this distinction through its general multi-plane
tracing machinery. Inference-wise, the practical lesson is that the
population model should not collapse everything into "subhaloes" unless
line-of-sight contributions have been modeled or marginalized over.

### Simulating LOS halo populations

PyAutoLens ships dedicated machinery for generating realistic LOS
populations, in `PyAutoLens:autolens/lens/los.py`:

- **`LOSSampler`** draws haloes from a cosmological halo mass function
  within a light-cone geometry around the lens, converts them to
  `al.mp.NFWTruncatedSph` profiles, and distributes them over multiple
  redshift planes between the observer and the source.
- **`los_planes_from`** assembles the sampled haloes into the per-plane
  galaxy lists a multi-plane `Tracer` consumes.
- Each plane also receives an `al.mp.MassSheet` with **negative
  convergence**, compensating the mean convergence of the halo
  population so total mass is conserved (following He et al. 2022,
  MNRAS 511, 3046). Without these sheets the LOS population
  systematically over-lenses: only the *fluctuations* about the mean
  density should perturb the images, not the mean itself.

The workspace example is
`autolens_workspace:scripts/imaging/features/advanced/los_halos/simulator.py`
(with a JAX variant alongside), which also writes the halo sample list
and per-plane sheet values out as diagnostics.

## Subhalo mass parameterisations

The dark-profile catalog in
`PyAutoGalaxy:autogalaxy/profiles/mass/dark/` provides the building
blocks for perturbers. In practice, analyses usually choose among:

- NFW-like profiles when a cosmological halo interpretation is desired
- truncated variants when tidal stripping inside the host halo matters
- simpler compact approximations when the data only constrain a local
  perturbation scale

The right parameterization depends on what the data can actually resolve.
Resolved arc perturbations can support a more physical halo model; a
marginal anomaly may only justify a compact effective perturber.

## Related pages

- [`api/mass_profile_catalog.md`](../api/mass_profile_catalog.md) — NFW
  and dark-matter profile rows.
- [`concepts/sensitivity_mapping.md`](./sensitivity_mapping.md).
- [`concepts/tracer.md`](./tracer.md) — multi-plane ray tracing and
  shared lens geometry.
