---
title: PyAutoFit
type: entity
topics: [software]
sources: []
status: drafted
---

# PyAutoFit

## What it is

The Bayesian-inference backend used by PyAutoLens. Provides:

- Search chaining (posterior of phase N → prior of phase N+1).
- Nested samplers: Dynesty, UltraNest, Nautilus, PolyChord.
- MCMC: emcee, Zeus.
- Hierarchical / graphical modelling for population inference.
- Database backend for managing many fits across a sample.

For [[lens-statistics|population studies]] on Euclid-scale samples, the
PyAutoFit database is the right pattern.

## See also

- [[bayesian-inference-lensing]]
- [[pyautolens]]
- [[slam-pipeline]]
