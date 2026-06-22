# Compilation log

Append-only record of what was done to this wiki, by whom, and when.

---

## 2026-05-22 — Initial build

**By:** Claude (Opus 4.7, PyAutoLens AI-assistant wiki bootstrap session).

**Scope of build:** strong lensing (~170 papers), substructure (11), cluster lensing (3),
dark-matter detection (2), dark-matter models (5).

**What was created**

- `CLAUDE.md` — schema, page types, naming, cross-reference conventions.
- `index.md` — top-level navigation.
- `concepts/*` — topical concept hubs synthesising the field (lens equation,
  mass models, substructure, time-delay cosmography, degeneracies, source
  reconstruction, lens finding, deep learning, cluster lensing, etc.).
- `entities/*` — SLACS, BELLS, H0liCOW, TDCOSMO, Euclid Q1, HFF, Abell 1201,
  Cosmic Horseshoe, PyAutoLens, lenstronomy, SLaM pipeline, Space Warps.
- `sources/*` — per-topic bibliography stubs. One section per paper. In
  the initial build, many per-paper summaries were inferred from
  filenames plus general field knowledge before later drafting passes
  upgraded the source pages.

**Known gaps / explicit TODOs**

- At the initial-build stage, every source stub was unread. Historical
  summary lines from that pass should still be treated as priors until the
  corresponding paper has been checked against the PDF or primary source.
- A handful of source references were ambiguous (typos, generic dates, working
  drafts like `1901.07801`, `detections_stochastic_no_zeros`,
  `MN-24-0938-MJ_Proof_hi`); these are listed under
  `sources/unclassified.md` for manual triage.
- Adjacent topics (weak lensing, ellipticals, bulge/disk decomposition,
  deep learning, statistics, IFUs, SMBHs, and the AutoLens method papers)
  contain material a PyAutoLens assistant would benefit from. These were
  deferred in this build. To extend later, follow the procedure in `AGENTS.md`.

**Provenance note**

The format follows Karpathy's LLM Wiki pattern (April 2026 gist): raw PDFs
are immutable, the wiki layer is compiled and cross-linked, and the
schema lives in `AGENTS.md` so the maintaining LLM has a stable contract.

---

## 2026-05-22 — Optimiser papers ingested

**By:** Claude (Opus 4.7), Round 6 of the `feat/natural-language` work.

**Scope:** Six canonical-paper entries added to ground PyAutoFit's
non-linear search catalogue in citable literature. Three full reads
(`drafted`), three single-paragraph stubs (`stub`):

- Skilling 2006 — Nested sampling foundation (drafted)
- Speagle 2020 — Dynesty, arXiv:1904.02180 (drafted)
- Lange 2023 — Nautilus, arXiv:2306.16923 (drafted)
- Foreman-Mackey 2013 — emcee, arXiv:1202.3665 (stub)
- Karamanis 2021 — zeus, arXiv:2105.03468 (stub)
- Hoffman 2014 — NUTS, arXiv:1111.4246 (stub)

**Files created:**

- `sources/bayesian-inference-methods.md` — per-paper bibliography.
- `concepts/nested-sampling.md` — concept page tying Skilling, Dynesty,
  Nautilus together.
- `concepts/mcmc-sampling.md` — concept page tying Emcee, Zeus, NUTS
  together.

**Cross-references added** into `wiki/core/`:

- `wiki/core/concepts/non_linear_search.md` — "Further reading" pointers
  to the two new literature concept pages.
- `wiki/core/api/searches.md` — one-line "Reference:" footers under each
  of Nautilus / DynestyStatic-Dynamic / UltraNest / Emcee / Zeus.

**Out of scope this pass:** BFGS / LBFGS / PySwarms / Drawer / NSS — no
single canonical paper to cite (classic numerical-methods textbooks or
no published reference). The JAX-native NSS has no preprint as of this
writing.

**Source of content:** arXiv abstract pages (and projecteuclid for the
Skilling 2006 journal paper). No local PDFs were used — the `**File:**`
field in each entry points at the arXiv or DOI URL.

---

## 2026-05-22 — Foundational papers ingested (Round 7)

**By:** Claude (Opus 4.7), Round 7 of the `feat/natural-language` work.

**Scope:** Eleven canonical citations added across four topics —
PyAutoLens code / methodology / SLaM, source-reconstruction physics,
substructure-detection foundation, lens surveys, and JAX tooling. Seven
full reads (`drafted`), four single-paragraph stubs (`stub`). Two
existing stubs upgraded to `drafted`.

**Drafted entries (7):**

- Nightingale & Dye 2015 (arXiv:1412.7436) — adaptive SLI; PyAutoLens
  pixelisation foundation. Added to `sources/lens-modeling-methods.md`.
- Nightingale, Dye & Massey 2018 (arXiv:1708.07377) — AutoLens code
  paper. Added to `sources/lens-modeling-methods.md`.
- Nightingale et al. 2021 (arXiv:2106.01384) — PyAutoLens JOSS software
  citation. Added to `sources/lens-modeling-methods.md`.
- Etherington et al. 2022 (arXiv:2202.09201) — SLaM "no lens left
  behind". Upgraded the existing stub in
  `sources/lens-modeling-methods.md` to drafted.
- Koopmans 2005 (arXiv:astro-ph/0501324) — gravitational-imaging
  foundation. Upgraded the existing stub in
  `sources/source-reconstruction.md` to drafted.
- Suyu et al. 2006 (arXiv:astro-ph/0601493) — Bayesian regularised
  source inversion; the "Suyu/Koopmans evidence" formula. Added to
  `sources/source-reconstruction.md`.
- Vegetti & Koopmans 2009 (arXiv:0805.0201) — adaptive grids + nested
  sampling for objective substructure detection. Added to
  `sources/dark-matter-substructure.md`.

**Stub entries (4):**

- Bolton et al. 2006 (arXiv:astro-ph/0511453) — SLACS-I founding paper.
- Brownstein et al. 2012 (arXiv:1112.3683) — BELLS-I founding paper.
- Suyu et al. 2017 (arXiv:1607.00017) — H0LiCOW-I program overview.
  All three added to the new file `sources/lens-surveys.md`.
- Cabezas et al. 2024 (arXiv:2402.10797) — BlackJAX library. Added to
  `sources/bayesian-inference-methods.md`.

**Also added (1 new file):**

- `sources/lens-surveys.md` — flat bibliography page for the
  survey-defining papers (SLACS-I, BELLS-I, H0LiCOW-I).

**Entity-page cross-refs:**

- `entities/pyautolens.md` — added "Key papers" section with the four
  PyAutoLens citations.
- `entities/slam-pipeline.md` — added "Canonical citation" pointing at
  Etherington 2022.
- `entities/slacs.md`, `entities/bells-gallery.md`, `entities/h0licow.md`
  — added "Founding citation" pointing at the survey paper.

**Bonus find:** the arXiv-listing search turned up the Etherington
"external shear is not shear" paper (arXiv:2301.05244), the J0946
ultramassive-black-hole paper (arXiv:2303.15514), and the Cao 2022
subhalo-scan paper (arXiv:2209.10566) — all under Etherington's
authorship and all worth a future ingestion pass into the relevant
existing source files.

---

## 2026-05-22 — Round 8: dark-matter-substructure depth pass

**By:** Claude (Opus 4.7), driven by user audit "look at the wiki — are
there any stubs/drafted still?". File-level status across the wiki is
uniformly `drafted`, but a sweep of `sources/*.md` surfaced ~120
per-paper entries whose summaries were 1-2-line filename-inferred stubs.
This round addresses the `dark-matter-substructure.md` hub.

**Scope:** Sixteen distinct papers in
`sources/dark-matter-substructure.md` upgraded from one-liner summaries
to 3-5-sentence arXiv-sourced summaries with arXiv ID, journal
reference, and author list. Done by fetching the arXiv abstract for each
and synthesising the lensing-relevant takeaway.

**Papers expanded (arXiv IDs):**

- Vegetti, Despali, Lovell, Enzi 2018 — 1801.01505
- Nightingale et al. 2024 (subm 2022) — 2209.10566
- Despali & Vegetti 2017 (baryons) — 1608.06938
- Despali et al. 2018 (LOS) — 1710.05029
- Despali et al. 2022 (Sensitivity I) — 2111.08718
- Despali et al. 2024 (Sensitivity II) — 2407.12910
- He et al. 2018 (GCs, subm 2017) — 1707.01849
- Loudas et al. 2022 (millilensing) — 2209.13393
- Li et al. 2016 (CDM vs WDM) — 1512.06507
- Li et al. 2017 (projection effects) — 1612.06227
- Diaz Rivero & Dvorkin 2019 (CNN) — 1910.00015
- Ritondale et al. 2019 (BELLS subhaloes, subm 2018) — 1811.03627
- Ritondale et al. 2019 (BELLS Lyα morphology) — 1811.03628
- Sawala et al. 2016 (the chosen few) — 1406.6362
- Benitez-Llambay & Frenk 2020 — 2004.06124
- Minor et al. 2021 (J0946 overconcentration) — 2011.10627

**Duplicates resolved:**

- "Despali 2021 — sensitivity" and "Despali 2022 — sensitivity" were
  the same paper (arXiv:2111.08718, submission year vs publication
  year). Merged into one entry.
- "Minor 2020 — DM concentration of J0946" and "Minor 2021 — DM
  concentration" were the same paper (arXiv:2011.10627). Merged into
  one entry.

**Out of scope this pass:** The other ~14 source hubs with thin entries
(`dark-matter-physics.md`, `multipoles.md`, `lens-finding.md`,
`flux-ratios.md`, `bulge-halo.md`, etc.) — to be addressed in
follow-up rounds. The two flagged `Verify` notes in
`degeneracies-systematics.md` and `multipoles.md`, and the
`unclassified.md` MNRAS-proof files, are also untouched.

**Source of content:** arXiv abstract pages plus the MNRAS / A&A
landing pages cited there. No local PDFs were used.

---

## 2026-06-19 — Decoupled from PyAutoPaper

**By:** Claude (maintainer session).

The literature wiki is now **self-contained** and no longer depends on any external paper
repository. Every per-paper `**File:**` line that pointed at a PyAutoPaper PDF path (e.g.
`Strong_Lens/Xxx.pdf`) was replaced with a public `**Reference:**` — an arXiv/DOI identifier
where the entry already recorded one, otherwise an author-year-title citation derived from the
entry heading or the source filename. Frontmatter `sources:` PDF paths across `concepts/` and
`entities/` were converted the same way. **No identifiers were invented:** papers without a
known arXiv/DOI are cited by author/year/title only. The schema (`AGENTS.md`) now documents
this reference convention, and the README frames the wiki as a base literature set users
extend with their own papers via `al_ingest_paper`.

---

## 2026-06-22 — Added canonical citation metadata

**By:** Codex (maintainer session).

Added the paired canonical BibTeX and alias layer, citation validation tooling, and compact
claim-support schema. Normalised the supplied bibliography without local file paths or
abstracts, and repaired the clearly matched Euclid Q1 and lens-finding source entries.
