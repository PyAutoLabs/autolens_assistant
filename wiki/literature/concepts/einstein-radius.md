---
title: Einstein radius
type: concept
topics: [foundations]
sources: []
status: drafted
---

# Einstein radius

## TL;DR

The Einstein radius θ_E is the angular radius of the ring an axisymmetric
lens produces when source, lens, and observer are exactly aligned. It is
also the radius inside which the mean convergence equals one — i.e. it is
a **direct measurement of the projected mass inside θ_E**:

```
θ_E² = (4 G M(<θ_E) / c²) · (D_ls / (D_l D_s))
```

For galaxy-scale lenses θ_E is typically ~0.5–2″. The Einstein **mass**
M_E = M(<θ_E) is one of the cleanest mass measurements available in
astrophysics — almost independent of the assumed [[mass-models|mass
profile]].

## What it is

For a singular isothermal sphere with velocity dispersion σ:

```
θ_E,SIS = 4π (σ/c)² (D_ls/D_s)
```

For an extended source not exactly behind the lens, "Einstein ring" is
loose shorthand for the tangential critical curve. The radius at which
the average convergence is 1 is sometimes called the "effective Einstein
radius" — that is what an observer recovers from image positions almost
independently of the slope.

## Why it matters for PyAutoLens

- It is the natural unit for almost every mass-model parameter. PyAutoLens
  parametrises `EllIsothermal` and `EllPowerLaw` profiles with
  `einstein_radius` rather than a normalisation, because θ_E is what the
  data constrain directly.
- It anchors prior choices. A user fitting a galaxy lens with arcs at
  ~1″ should expect θ_E ≈ 1″ within a factor of ~2; priors should
  reflect that.
- It also anchors the [[radial-angular-degeneracy|radial-vs-angular]]
  decomposition: data tightly fix the mass at θ_E and weakly fix its
  radial slope.

## Subtleties

- The Einstein radius is **not** the half-light radius and need not be
  near it. For SLACS-type lenses θ_E is often close to the effective
  radius R_eff; for cluster lenses it is far inside R_eff.
- The recovered θ_E is subject to the [[mass-sheet-degeneracy]] — a
  uniform sheet rescales it.

## See also

- [[lens-equation]]
- [[mass-models]]
- [[mass-sheet-degeneracy]]
- [[radial-angular-degeneracy]]
- [[slacs]]
