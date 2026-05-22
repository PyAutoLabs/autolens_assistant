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
