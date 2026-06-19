---
title: Sources — deep learning for lensing
type: sources
topics: [methods]
status: drafted
---

# Sources: deep learning for lensing

## Pearson 2024 — strong-lens JWST

**Reference:** Pearson 2024 — strong-lens JWST
**Concepts:** [[deep-learning-lensing]]
**Summary:** Forecast-style paper on how modern deep-learning workflows
can exploit JWST-quality strong-lens data. The relevant message for this
wiki is not that neural networks replace classical modeling, but that the
higher resolution and source complexity of JWST data make fast learned
surrogates increasingly attractive for triage, initialization, and
population-scale inference.

## Morningstar 2019 — deep-learning source reconstruction

**Reference:** Morningstar 2019 — deep-learning source reconstruction
**Concepts:** [[deep-learning-lensing]], [[source-reconstruction]]
**Summary:** Presents recurrent inference machines for reconstructing the
unlensed source image directly from strong-lens data, coupled to a CNN
that predicts lens-mass parameters. The emphasis is automation of source
reconstruction and mass inference rather than explicit Bayesian sampling
of a hand-written physical model.

## Wagner-Carena 2021 — hierarchical BNN

**Reference:** Wagner-Carena 2021 — hierarchical BNN
**Concepts:** [[deep-learning-lensing]], [[lens-statistics]]
**Summary:** Shows how Bayesian neural networks can be embedded in a
hierarchical inference framework so that population hyperparameters can be
recovered without locking the answer to the training-set distribution. The
paper is important because it focuses on uncertainty calibration and
sample-level inference, not only point predictions for single lenses.

## Brehmer 2019 — mining DM substructure

**Reference:** Brehmer 2019 — mining DM substructure
**Concepts:** [[deep-learning-lensing]],
[[dark-matter-substructure]]
**Summary:** Uses simulation-based inference and machine learning to
extract population information about dark-matter substructure from
extended strong-lens arcs. The key contribution is not a catalog of
individual perturbers but a way to infer subhalo-population properties
from the subtle imprint of many possible perturbers on the lensed image.

## See also

- [[deep-learning-lensing]]
