---
title: Euclid photometric redshifts
type: concept
topics: [data, photo-z]
sources:
  - Euclid Collaboration - Desprez et al. 2020 — Desprez-EP10
  - Euclid Collaboration - Tucci et al. 2025 — Q1-TP005
status: drafted
---

# Photometric redshifts in Euclid

## The concept

Euclid measures redshifts for billions of galaxies photometrically, from I_E +
Y_E/J_E/H_E + [[ext-surveys]] colours. The methodology was stress-tested
pre-launch in the photo-z challenge (Desprez et al. 2020, `Desprez-EP10`) and runs
in production as the PHZ processing function (Tucci et al. 2025, `Q1-TP005`),
downstream of the [[zero-point-corrections]] computed by [[ou-phz]].

## Why it matters for lens modeling

Catalogue photo-zs for strong lenses are computed on **blended** photometry — lens
and source light mixed — and are therefore biased for exactly the objects the
pipeline cares about. The modeling pipeline's answer is deblended, model-based
photometry: Sersic fits per band with the mass model fixed
(`euclid_strong_lens_modeling_pipeline:scripts/sersic_lens_model.py`) yield
separate lens and source SEDs, from which photo-zs are estimated *after* modeling.
This is why the pipeline treats redshifts as placeholders during the fit (a
single-plane lens model is redshift-independent in dimensionless units) and why
its latent aperture-flux outputs feed SED fitting rather than consuming catalogue
photo-zs.

## See also

- [[zero-point-corrections]], [[ou-phz]], [[psf-homogenisation]]
