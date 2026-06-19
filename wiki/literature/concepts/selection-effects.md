---
title: Selection effects in strong-lens samples
type: concept
topics: [populations, systematics]
sources:
  - Sonnenfeld et al. 2023 — Selection Effects
  - Sonnenfeld et al. 2024 — Slacs Debiased
  - Sonnefendl et al. 2025 — SLACS Debiaded II
status: drafted
---

# Selection effects

## TL;DR

Lens samples are not random — they are biased toward higher σ
(stronger lenses), higher source magnification (brighter arcs), and
specific redshift/colour cuts of the parent survey. Any
[[lens-statistics|population-level inference]] must model the selection
function explicitly.

## What it is

- The **lens cross-section** σ_lens ∝ θ_E² so massive galaxies are
  overrepresented.
- Spectroscopic confirmation cuts (SLACS requirement of double-z
  spectroscopy) prefer compact, blue, lensed sources.
- Imaging surveys (HSC, DES) prefer extended bright arcs.
- Sonnenfeld 2023 / 2024 / 2025 "Debiased SLACS" series carefully
  reconstructs the SLACS selection function and re-derives scaling
  relations.

## Why it matters

- Mass-slope claims from SLACS shift after debiasing.
- Comparing samples across surveys requires a common selection-function
  framework.

## See also

- [[lens-statistics]]
- [[lens-finding]]
- [[slacs]]
- [[sources-selection-effects]]
