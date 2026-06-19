# PyAutoLens AI Assistant — Strong Lensing Literature Wiki

This sub-wiki (`autolens_assistant/wiki/literature/`) gives the assistant the broad
scientific context of strong gravitational lensing. It follows Karpathy's "LLM Wiki"
pattern: a compiled, cross-linked knowledge layer the assistant reads at query time.

It ships as a **self-contained base literature wiki** — a starting body of strong-lensing
science that every clone of the assistant gets out of the box. It is **not** tied to any
external paper repository or personal PDF library: every page stands on its own, and papers
are referenced by arXiv/DOI link and/or citation, never by a local file path. Users are
expected to **extend** it with the papers and context their own project needs (see
[`skills/al_ingest_paper.md`](../../skills/al_ingest_paper.md)).

## References — how papers are cited

Papers are identified by a **public reference**, not a file on disk:

- An **arXiv** link/ID (`arXiv:2011.10627`) or a **DOI**/journal URL when one is known, and/or
- a **citation** — author(s), year, and a short descriptive tag (e.g.
  `Minor et al. 2021 — J0946 subhalo overconcentration`).

Never record a local PDF path, and **never fabricate** an arXiv ID or DOI: if no public
identifier is known for a paper, cite it by author/year/title only. A reader who wants the
PDF sources it from arXiv or the journal using the reference.

## Layout

```
wiki/literature/             # the compiled wiki (in git)
├── AGENTS.md                # this file — schema + usage rules (canonical)
├── CLAUDE.md                # one-line import stub of AGENTS.md
├── index.md                 # top-level navigation
├── log.md                   # append-only compilation log
├── concepts/                # one topic per page — the science
├── entities/                # specific surveys, lenses, collaborations, software
└── sources/                 # per-topic bibliography pages (one paper = one section)
```

Wiki pages are syntheses. If a page and the paper it cites disagree, the paper wins; update
the page and note the change in `log.md`.

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

External references point at a paper by its arXiv/DOI link and/or citation (see "References"
above), never a local path.

## Frontmatter

Every wiki file starts with YAML frontmatter:

```yaml
---
title: Mass-sheet degeneracy
type: concept            # concept | entity | sources | meta
topics: [degeneracies, cosmography]
sources:                 # optional — papers most relevant to this page,
  - arXiv:1607.00017     # by arXiv ID, DOI, or "Author Year — tag" citation
  - Suyu et al. 2010 — H0 from B1608+656
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

Bibliography of papers covering this topic. Each paper has its own H2 section;
cross-link from concept and entity pages with `[[sources-<topic>#author-year-slug]]`.

## Author Year — short tag

**Reference:** arXiv:1607.00017  (or a DOI/journal URL, and/or "Author Year — title")
**Concepts:** [[concept-1]], [[concept-2]]
**Summary:** one-paragraph stub. Mark `(stub — verify against the paper)` if not yet read.
```

## How the assistant should use this wiki

1. On a user question, first open `index.md`.
2. Follow the relevant `concepts/` or `entities/` page.
3. Cite specific results by linking the `[[sources-topic#author-year]]`
   anchor. If a claim is needed and the source stub is unread, fetch the paper
   from the arXiv/DOI in the stub's `Reference:` line.
4. When a paper is read in full, upgrade the stub's `status:` from `stub` to
   `drafted`, replace the inferred summary with what the paper actually
   says, and add a line to `log.md`.
5. Never fabricate a citation or identifier. If a result is not on a wiki page, say so
   and offer to read the relevant paper.

## Extending the wiki

This base wiki is a starting point, not a fixed corpus. When a user's project needs a paper
that isn't here yet, add it via [`skills/al_ingest_paper.md`](../../skills/al_ingest_paper.md):
create or update the relevant `sources/<topic>.md` section, cross-link the impacted
`concepts/` and `entities/` pages with `[[wiki-link]]`s, and append a row to `log.md`. Over
time the wiki grows into the project's own literature record.
