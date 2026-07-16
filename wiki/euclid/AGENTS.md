# PyAutoLens AI Assistant — Euclid Wiki

This sub-wiki (`autolens_assistant/wiki/euclid/`) gives the assistant the Euclid-specific
scientific context for **euclid mode** — modeling Euclid strong lenses through
`euclid_strong_lens_modeling_pipeline` (see the `skills/euclid_*.md` family). It covers
the Euclid strong-lensing literature *and* the mission/instrument/data papers the general
strong-lensing wiki deliberately does not: VIS/NISP, the Wide Survey, the EXT ground
data, per-tile PSFs, zero-point corrections, and photometric redshifts.

## Schema

The schema, page types, naming, cross-reference and citation rules are **identical to
the literature sub-wiki** — [`../literature/AGENTS.md`](../literature/AGENTS.md) is
canonical; do not restate it here. Layout:

```
wiki/euclid/
├── AGENTS.md        # this file — scope + the rules below
├── CLAUDE.md        # one-line import stub
├── index.md         # top-level navigation
├── log.md           # append-only compilation log
├── concepts/        # Euclid data concepts (PSF, ZPCs, photo-z, …)
├── entities/        # mission, instruments, surveys, data releases
├── sources/         # per-topic claim support (one paper = one section)
└── bibliography/    # euclid.bib + aliases (see bibliography/README.md)
```

`[[wiki-link]]` slugs resolve within this sub-wiki first, then against
`../literature/` — link general lensing concepts (e.g. `[[lens-finding]]`,
`[[selection-effects]]`) rather than duplicating their pages here.

## Euclid-specific rules

- **Bibliography keys are the Euclid Collaboration's own** (`EuclidSkyOverview`,
  `Q1-SP048`, `Q1-TP004`, …), copied verbatim from the collaboration's shared
  `euclid.bib` so pages and downstream paper LaTeX agree. Mappings to
  `../literature/bibliography/autolens_literature.bib` keys and to informal
  author-year names live in `bibliography/bibkey_aliases.yaml`.
- **In-prep DR1 material stays summarised, never committed.** Several DR1 papers
  (Aussel 2026, Lines 2026, Holloway 2026, Nightingale 2026, Nersesian 2026,
  Vincken 2026a, Fogliardi 2026, Kümmel 2026, McCracken 2026, Polenta 2026) are
  collaboration-internal drafts at the time of writing: numbers from them are
  **preliminary**, pages must say so, no draft PDFs are committed to this public
  repo, and no bibliography entry is written until public metadata exists
  (never fabricate — `../literature/bibliography/README.md`).
- This repo is public: no collaboration-internal documents, no local file paths,
  no PyAutoMemory references.
