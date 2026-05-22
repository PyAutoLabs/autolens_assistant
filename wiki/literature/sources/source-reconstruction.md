---
title: Sources — source reconstruction
type: sources
topics: [source-reconstruction]
status: drafted
---

# Sources: source reconstruction

## Galan 2021 — SLIT

**File:** `Strong_Lens/Galan2021SLIT.pdf`
**Concepts:** [[source-reconstruction]] (wavelet / sparse)
**Summary:** Wavelet and sparse source-plane reconstruction
(SLIT-ronomy). Alternative to Gaussian-prior pixelated grids.

## Galan 2022 — wavelet lensing

**File:** `Strong_Lens/Galan2022Wavelet.pdf`
**Concepts:** [[source-reconstruction]]
**Summary:** Follow-up to SLIT with multi-scale wavelet source
reconstruction with applications.

## Koopmans 2005 — gravitational imaging

**File:** https://arxiv.org/abs/astro-ph/0501324 (MNRAS 363, 1136)
**Concepts:** [[gravitational-imaging]], [[source-reconstruction]],
[[dark-matter-substructure]]
**Status:** drafted

**Summary (drafted):** Koopmans introduces **gravitational imaging** —
the foundational method for detecting and quantifying luminous and dark
mass substructure in galaxy-scale lenses by using highly-magnified
Einstein rings and arcs as sensitive probes of the lens potential.
Rather than parametrising the lens-galaxy mass distribution and fitting,
the method **reconstructs the lens potential non-parametrically on a
grid** alongside the source-plane intensity, treating any substructure
in the host lens as a localised perturbation to a smooth underlying
potential.

The paper's headline result is the demonstration on numerical
simulations that the algorithm recovers the smooth mass distribution of
a typical lens galaxy with sensible signal-to-noise and *additionally*
recovers compact substructure with masses as low as
M_sub ≈ 10⁻³ M_lens. The key insight is that the arc residuals after
subtracting the best-fit smooth model encode the substructure signal
directly — gravitational imaging trades parametric assumptions about
the substructure for the high information content of the Einstein-ring
pixels.

This is the **foundational citation for substructure-detection
methodology** that PyAutoLens' subhalo-scan and pixelised-potential
modes implement. Vegetti & Koopmans 2009 (below in
`sources/dark-matter-substructure.md`) extends the method to an adaptive
source grid + nested sampling for objective evidence-based detection;
Nightingale 2022 implements the production scan in PyAutoLens. Cite
Koopmans 2005 when justifying *why* gravitational imaging is the method
of choice over parametric perturber fits.

## Suyu 2006 — Bayesian regularised source inversion

**File:** https://arxiv.org/abs/astro-ph/0601493 (MNRAS 371, 983)
**Concepts:** [[source-reconstruction]], [[bayesian-inference-lensing]],
[[regularization]]
**Status:** drafted

**Summary (drafted):** Suyu, Marshall, Hobson & Blandford introduce the
**Bayesian analysis of regularised pixelised source inversions** that
PyAutoLens uses by default. Building on Warren & Dye (2003)'s linear
source-inversion method, the paper shows how to use Bayesian model
comparison to (a) determine the optimal regularisation *strength* for a
given regularisation form, and (b) objectively choose between
regularisation *forms* — zeroth-order, gradient, or curvature — based on
the marginal-likelihood evidence.

The mathematical core is the closed-form Bayesian evidence for a
Gaussian source prior under a Gaussian likelihood: marginalising over
the source-pixel intensities analytically yields the `log Z = -½χ² -
½log|LᵀC⁻¹L + λH| + ½log|λH| - ½N log(2π)` term that
[[bayesian-inference-lensing]] cites verbatim. This is the "Suyu /
Koopmans evidence" quoted across the lensing community — it reduces the
effective sampler dimensionality by analytically integrating out
hundreds to thousands of source-plane pixels, leaving only the
mass-model and regularisation hyper-parameters for the non-linear
search to explore.

The paper demonstrates the method on simulated data with the exact
lens potential, finding that the optimal regularisation form depends on
the source's intrinsic morphology (smoother sources prefer
zeroth-order, structured sources prefer curvature). In PyAutoLens, this
choice is exposed as a model option and selected per-fit by the same
evidence-based comparison the paper introduced. **This is the citation
to give whenever PyAutoLens' pixelised-source likelihood term is
invoked in a paper.**

## Ding 2016 — SHARP IX source reconstruction

**File:** `Strong_Lens/Ding2016_SHARPIXGalRecon.pdf`
**Concepts:** [[source-reconstruction]]
**Summary:** Pixelated source reconstruction in a SHARP sample
lens, possibly with stellar-population implications for the source
galaxy.

## Suyu 2009 — spiral potential correction

**File:** `Strong_Lens/Suyu2009SpiralPotentialCorr.pdf`
**Concepts:** [[gravitational-imaging]]
**Summary:** Pixelated potential corrections and detection of
spiral-like residual structure in a specific lens.

## Verbados / Vernardos 2022 — potential corrections

**File:** `Strong_Lens/Verbados2022PotentialCoorr.pdf`
**Concepts:** [[gravitational-imaging]]
**Summary:** Updated framework for pixelated potential
corrections. Filename appears to be a misspelling of Vernardos. Verify.

## Minor 2024 — pixel supersampling

**File:** `Strong_Lens/Minor2024PixelSuperSample.pdf`
**Concepts:** [[source-reconstruction]], [[gravitational-imaging]]
**Summary:** Supersampling of source-plane pixels to access
substructure below the nominal pixel scale.

## Minor 2025 — supersampling II

**File:** `Strong_Lens/Minor2025SuperSamplin.pdf`
**Concepts:** [[source-reconstruction]]
**Summary:** Continuation and application of pixel supersampling
methodology.

## See also

- [[source-reconstruction]]
- [[gravitational-imaging]]
