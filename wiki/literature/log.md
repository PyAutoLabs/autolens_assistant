# Compilation log

Append-only record of what was done to this wiki, by whom, and when.

---

## 2026-05-22 — Initial build

**By:** Claude (Opus 4.7, PyAutoLens AI-assistant wiki bootstrap session).

**Scope of build:** Strong_Lens (~170 PDFs), Substructure (11), StrongLensCluster (3),
Dark_Matter_Detection (2), DarkMatterModels (5).

**What was created**

- `CLAUDE.md` — schema, page types, naming, cross-reference conventions.
- `index.md` — top-level navigation.
- `concepts/*` — topical concept hubs synthesising the field (lens equation,
  mass models, substructure, time-delay cosmography, degeneracies, source
  reconstruction, lens finding, deep learning, cluster lensing, etc.).
- `entities/*` — SLACS, BELLS, H0liCOW, TDCOSMO, Euclid Q1, HFF, Abell 1201,
  Cosmic Horseshoe, PyAutoLens, lenstronomy, SLaM pipeline, Space Warps.
- `sources/*` — per-topic bibliography stubs. One section per paper. All
  per-paper summaries in this initial build are inferred from filenames
  plus general field knowledge and are marked `status: stub`. They are
  **not yet verified against the PDF**.

**Known gaps / explicit TODOs**

- Every source-stub is unread. The PyAutoLens assistant should treat the
  summary lines as priors, not facts, until the corresponding PDF has been
  read and the stub upgraded to `status: drafted`.
- A handful of filenames are ambiguous (typos, generic dates, working
  drafts like `1901.07801.pdf`, `detections_stochastic_no_zeros.pdf`,
  `MN-24-0938-MJ_Proof_hi.pdf`); these are listed under
  `sources/unclassified.md` for manual triage.
- Adjacent folders (`WeakLensing/`, `Ellipticals/`, `Bulge_Disk_Decomp/`,
  `Deep Learning/`, `Stats/`, `IFUs/`, `SMBHs/`, root-level `AutoLens.pdf` &
  `autolens_paper1_resubmit_*.pdf`) contain material a PyAutoLens
  assistant would benefit from. User chose to defer ingesting these in
  this build. To extend later, follow the procedure in `CLAUDE.md`.

**Provenance note**

The format follows Karpathy's LLM Wiki pattern (April 2026 gist): raw PDFs
are immutable, the wiki layer is compiled and cross-linked, and the
schema lives in `CLAUDE.md` so the maintaining LLM has a stable contract.

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
