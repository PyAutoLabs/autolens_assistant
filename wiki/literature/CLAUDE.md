# PyAutoLens AI Assistant — Strong Lensing Wiki

This wiki gives a PyAutoLens AI assistant the broad scientific context of
strong gravitational lensing. It follows Karpathy's "LLM Wiki" pattern: the
PDFs in the surrounding `PyAutoPaper/` repo are the immutable `raw/` layer
(gitignored — kept locally only), and this `lensing_wiki/` folder is the
compiled, cross-linked knowledge layer the assistant reads at query time
and that lives in git for collaborators.

## Layout

```
PyAutoPaper/                  # repo root
├── lensing_wiki/             # this folder — the compiled wiki (in git)
│   ├── CLAUDE.md             # this file — schema + usage rules
│   ├── index.md              # top-level navigation
│   ├── log.md                # append-only compilation log
│   ├── concepts/             # one topic per page — the science
│   ├── entities/             # specific surveys, lenses, collaborations, software
│   └── sources/              # per-topic bibliography pages (one paper = one section)
├── Strong_Lens/              # raw/ layer — PDFs (gitignored)
├── Substructure/
├── StrongLensCluster/
├── Dark_Matter_Detection/
├── DarkMatterModels/
└── ...                       # other PDF folders (gitignored)
```

The PDFs are the ground truth. Wiki pages are syntheses. If a wiki page and a
PDF disagree, the PDF wins; the wiki page should be updated and the change
noted in `log.md`.

## Page types

| Type        | Folder       | Scope                                                 |
|-------------|--------------|-------------------------------------------------------|
| Concept     | `concepts/`  | One scientific concept (e.g. mass-sheet degeneracy)   |
| Entity      | `entities/`  | One named thing (survey, lens, code, collaboration)   |
| Sources     | `sources/`   | All paper stubs for one topic, one section per paper  |
| Index/log   | root         | Navigation and provenance                             |

## Naming

- File names are lowercase kebab-case: `mass-sheet-degeneracy.md`,
  `slacs.md`, `time-delay-cosmography.md`.
- One concept per concept page. If a page tries to cover two ideas, split it.
- Source-collection pages are named by topic: `sources/dark-matter-substructure.md`.

## Cross-references

Use `[[page-slug]]` for wiki-internal links — for example
`[[mass-sheet-degeneracy]]` or `[[slacs]]`. Slugs match the filename without
`.md`. A `[[link]]` that has no target file yet is fine — it marks a future
page to write.

External references point at the PDF on disk using a relative path from
the `PyAutoPaper/` repo root, e.g. `Strong_Lens/Suyu2016Holicow.pdf`.
The PDFs themselves are kept locally (gitignored), so collaborators
cloning the repo will see the wiki references but need to source the
PDFs separately (most are on arXiv or the journal site).

## Frontmatter

Every wiki file starts with YAML frontmatter:

```yaml
---
title: Mass-sheet degeneracy
type: concept            # concept | entity | sources | meta
topics: [degeneracies, cosmography]
sources:                 # optional — papers most relevant to this page
  - Strong_Lens/Suyu2016Holicow.pdf
  - Strong_Lens/Birrer2020TDCOSMOSIVH0.pdf
status: stub             # stub | drafted | reviewed
---
```

Sources may be `[]` for pages that synthesize general field knowledge.

## Concept page structure

```
# Title

## TL;DR
One paragraph an assistant can quote back to a user.

## What it is
The physics / definition.

## Why it matters for PyAutoLens
How this concept shows up in lens-modeling decisions a PyAutoLens user makes.

## Key results from the literature
Bullet list. Each bullet ends with `([[author-year-stub]])` so the LLM can
follow the link to the per-paper section.

## See also
- [[related-concept-1]]
- [[related-concept-2]]
```

## Entity page structure

Same idea but the headings are "What it is / Key facts / Papers / See also".
Use entity pages for: surveys (SLACS, BELLS, H0liCOW), specific lenses
(Abell 1201, the Cosmic Horseshoe), software (PyAutoLens, lenstronomy),
collaborations (TDCOSMO, Space Warps).

## Source-collection page structure

```
# Sources: <topic>

Bibliography of papers in `Papers/` covering this topic. Each paper has its
own H2 section; cross-link from concept and entity pages with
`[[sources-<topic>#author-year-slug]]`.

## Author Year — short tag

**File:** `Strong_Lens/Filename.pdf`
**Concepts:** [[concept-1]], [[concept-2]]
**Summary:** one-paragraph stub inferred from filename and field knowledge.
Mark `(stub — verify against PDF)` if not yet read.
```

## How the assistant should use this wiki

1. On a user question, first open `index.md`.
2. Follow the relevant `concepts/` or `entities/` page.
3. Cite specific results by linking the `[[sources-topic#author-year]]`
   anchor. If a claim is needed and the source stub is unread, open the
   PDF at the path in the stub's `File:` line.
4. When a PDF is read in full, upgrade the stub's `status:` from `stub` to
   `drafted`, replace the inferred summary with what the paper actually
   says, and add a line to `log.md`.
5. Never fabricate a citation. If a result is not on a wiki page, say so
   and offer to read the relevant PDF.

## Scope

In-scope folders for the current wiki build:

- `Strong_Lens/`           — primary
- `Substructure/`
- `StrongLensCluster/`
- `Dark_Matter_Detection/`
- `DarkMatterModels/`

Other folders (`WeakLensing/`, `Ellipticals/`, `Deep Learning/`, etc.)
contain papers that touch lensing tangentially but are out of scope until
explicitly added — see `log.md` for the decision.

This wiki is the **lensing** sub-wiki of `PyAutoPaper/`. Future sub-wikis
(e.g. `imaging_wiki/`, `cosmology_wiki/`) may sit alongside it at the
repo root following the same schema.
