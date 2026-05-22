---
title: Lens equation
type: concept
topics: [foundations]
sources: []
status: drafted
---

# Lens equation

## TL;DR

The lens equation maps a position **β** in the unlensed source plane to a
position **θ** in the image plane through a deflection field **α(θ)**
sourced by the projected mass of the lens:

```
β = θ − α(θ)
```

For a given source position β, multiple solutions θ can exist — those are
the multiple images. PyAutoLens's tracer evaluates this map by adding
deflection contributions from each [[mass-models|mass profile]] of the
lens; ray-tracing a regular image-plane grid back to the source plane
gives the unlensed source-plane coordinates each pixel "came from".

## What it is

The deflection field is the gradient of a scalar deflection potential ψ,

```
α(θ) = ∇ψ(θ)        ψ = (1/π) ∫ κ(θ′) ln|θ − θ′| d²θ′
```

where κ = Σ / Σ_crit is the convergence — the surface mass density of the
lens scaled by the critical density that depends on the angular diameter
distances D_l, D_s, D_ls. The Jacobian of β(θ) carries all the local
lensing information:

- determinant zero → **critical curves** (image plane) / **caustics**
  (source plane); magnification diverges.
- shear γ from the trace-free part → tangential / radial stretching.
- convergence κ from the trace → isotropic magnification.

Total magnification of an image is μ = 1 / det(∂β/∂θ).

## Why it matters for PyAutoLens

PyAutoLens's `Tracer` is a numerical implementation of this equation. Every
likelihood evaluation:

1. Builds the deflection α(θ) at every image-plane pixel by summing
   contributions from each `MassProfile` (see [[mass-models]]).
2. Subtracts α from θ to get source-plane positions β(θ).
3. Interpolates the source model (parametric or pixelised — see
   [[source-reconstruction]]) at those β positions to predict an image.
4. Compares to data via χ² + a [[regularization]] term for pixelised
   sources, summed into an evidence under
   [[bayesian-inference-lensing|Bayesian inference]].

When the user changes the mass model, only α changes. When they change the
source, only step 3 changes. Understanding this split is the first
mental model a PyAutoLens user needs.

## Critical curves, caustics, and image multiplicity

- **Tangential critical curve** → the Einstein ring locus where images of
  an on-axis source pile up; see [[einstein-radius]].
- **Radial critical curve** → present only when the central density slope
  is shallower than isothermal; produces radial demagnified images.
- A source inside the **tangential caustic** but outside the radial caustic
  produces a quad/cross. Inside both, five images (rare). Outside the
  tangential caustic, a double.

## See also

- [[einstein-radius]]
- [[mass-models]]
- [[mass-sheet-degeneracy]]
- [[radial-angular-degeneracy]]
- [[multipoles]]
