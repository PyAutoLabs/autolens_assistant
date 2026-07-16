---
title: Sources — DR1 lens-finding image-processing study (in prep)
type: sources
topics: [strong-lensing, deep-learning, data]
status: drafted
---

# Sources: DR1 image processing and lens-finding training data

## Euclid Collaboration: Fogliardi et al. 2026 — image processing & training-data ablation

**Canonical BibTeX key:** *none yet — in-prep collaboration draft; add the entry
only when public metadata exists (see `../AGENTS.md`).*
**Reference:** Euclid Collaboration: Fogliardi et al. 2026, A&A in prep — "Euclid
Data Release 1 (DR1): Enhancing deep-learning models: the impact of image
processing and training data selection for strong-lens detection"
**Concepts:** [[deep-learning-lensing]], [[lens-finding]], [[q1-dr1-releases]]

**All values below are preliminary (draft under internal review).**

**Supports:**
- Systematic ablation of the CNN lens finder deployed in the Euclid DR1 pipeline
  (Zoobot ConvNeXt-Base backbone, full-network fine-tuning): input representation
  and training-data selection matter more than architecture.
- Training on native FITS improves high-recall average precision by up to ~11%
  relative to compressed JPEG training — preserve native image content for
  survey-scale searches.
- Expert-selected hard negatives give the largest gains (~48% high-recall AP for
  VIS-only, ~22% for pseudo-RGB models); hard-negative mining from the Q1 SLDE
  rejection grades and Deep-Field artefact cutouts is critical.
- VIS-only and pseudo-RGB representations rank different lens subsets
  preferentially; score-fusion ensembles add ~3–5% AP at high recall —
  motivating ensemble approaches for future releases.
- Training data: hybrid of simulated GGSLs (cluster + field; Lenstronomy- and
  GLAMER-based sets, HST2EUCLID conversion to Euclid observing conditions) and
  real Q1/DR1 graded lenses.

**Use when:**
- Choosing image formats, negatives, or ensemble strategy for Euclid lens-finding
  ML work; motivating native-FITS pipelines.

**Do not use for:**
- Final DR1 catalogue numbers or completeness/purity — the catalogue papers
  (Lines et al. 2026, Holloway et al. 2026, in prep) own those; all figures here
  are draft-stage.
