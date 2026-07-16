---
title: Euclid data releases (Q1 → DR1)
type: entity
topics: [survey, data-release]
sources:
  - Euclid Collaboration - Aussel et al. 2025 — Q1-TP001
  - Euclid Collaboration - McCracken et al. 2025 — Q1-TP002
  - Euclid Collaboration - Polenta et al. 2025 — Q1-TP003
  - Euclid Collaboration - Romelli et al. 2025 — Q1-TP004
  - Euclid Collaboration - Tucci et al. 2025 — Q1-TP005
status: drafted
---

# Euclid data releases: Q1 and DR1

## What they are

- **Q1 (Quick Release 1, 2025)** — ~63 deg² of Wide-Survey-depth data over the
  Deep Field footprints. Release overview: Aussel et al. 2025 (`Q1-TP001`);
  processing papers: VIS `Q1-TP002`, NIR `Q1-TP003`, MER multiwavelength
  catalogues `Q1-TP004`, photo-z `Q1-TP005`.
- **DR1 (Data Release 1, 2026)** — the first major public release, ~2000 deg².
  The DR1 release and processing papers (Aussel 2026, McCracken 2026, Polenta
  2026, Kümmel 2026) are in preparation at the time of writing — numbers quoted
  from drafts are preliminary.

## Strong-lensing content

- Q1: the Strong Lensing Discovery Engine yielded ~500 galaxy-galaxy candidates
  (~250 grade A) from ~63 deg² — see
  [[../sources/euclid-strong-lensing|the strong-lensing sources page]].
- DR1: the search scales to automated ML pipelines + citizen science + expert
  grading over tens of millions of galaxies, with a catalogue of >10,000
  candidates including standardised lensing-model fits (in-prep DR1 papers:
  Lines 2026 catalogue, Holloway 2026 grading, Nightingale 2026 model fits,
  Nersesian 2026 photo-zs; preliminary).
- The bundled pipeline sample `dataset/q1_walsmley/` in
  `euclid_strong_lens_modeling_pipeline` is drawn from the Q1 discovery papers.

## See also

- [[euclid-mission]], [[euclid-wide-survey]]
- [[../literature/entities/euclid-q1|euclid-q1]] (general wiki)
