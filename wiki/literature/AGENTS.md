# PyAutoLens AI Assistant — Strong Lensing Literature Wiki

This sub-wiki (`autolens_assistant/wiki/literature/`) gives the assistant the broad
scientific context of strong gravitational lensing. It follows Karpathy's "LLM Wiki"
pattern: a compiled, cross-linked knowledge layer the assistant reads at query time.

It ships as a **self-contained base literature wiki** paired with a canonical BibTeX
bibliography. It is not tied to a PDF library: pages use public references and canonical
keys, never local file paths. Users extend it through
[`skills/al_ingest_paper.md`](../../skills/al_ingest_paper.md).

## References and citation metadata

The two layers have separate roles:

- `sources/*.md` records compact, claim-oriented guidance about what a paper supports.
- `bibliography/autolens_literature.bib` records canonical citation metadata and keys.
- `bibliography/bibkey_aliases.yaml` maps known alternate keys to canonical keys.

Use an arXiv ID, DOI, journal reference, or author/year/title when verified. Never record a
local PDF path or fabricate metadata. A canonical key is local to this repository: before
patching a paper's LaTeX, resolve it against that project's `.bib` and use its existing local
key where available. Detailed rules are in [`bibliography/README.md`](./bibliography/README.md).

## Layout

```
wiki/literature/             # the compiled wiki (in git)
├── AGENTS.md                # this file — schema + usage rules (canonical)
├── CLAUDE.md                # one-line import stub of AGENTS.md
├── index.md                 # top-level navigation
├── log.md                   # append-only compilation log
├── concepts/                # one topic per page — the science
├── entities/                # specific surveys, lenses, collaborations, software
├── sources/                 # per-topic claim support (one paper = one section)
└── bibliography/            # canonical BibTeX, aliases, and citation instructions
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

External references use verified public metadata, never a local path.

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

## Source-entry structure

```
# Sources: <topic>

Bibliography of papers covering this topic. Each paper has its own H2 section;
cross-link from concept and entity pages with `[[sources-<topic>#author-year-slug]]`.

## Author Year — short tag

**Canonical BibTeX key:** `KeyYYYY`
**Reference:** arXiv:1607.00017  (or a DOI/journal URL, and/or "Author Year — title")
**Concepts:** [[concept-1]], [[concept-2]]

**Supports:**
- Claim this paper directly supports.
- Another claim this paper directly supports.

**Use when:**
- Situation where the citation is appropriate.

**Do not use for:**
- Similar but unsupported claim.
```

Keep entries short: normally 2–5 support bullets and no long prose. Do not copy abstracts or
turn source pages into paper summaries. If a claim has not been verified, add a TODO rather
than guessing.

## How the assistant should use this wiki

1. On a user question, first open `index.md`.
2. Follow the relevant `concepts/` or `entities/` page.
3. Follow the source entry for claim scope and its canonical key for metadata.
4. Resolve that key against any downstream project's `.bib` before changing LaTeX.
5. If support or metadata is unclear, read the public paper and add a TODO rather than guess.

## Extending the wiki

This base wiki is a starting point, not a fixed corpus. When a user's project needs a paper
that is not here, use [`skills/al_ingest_paper.md`](../../skills/al_ingest_paper.md). Add the
verified BibTeX metadata, a compact source entry, relevant cross-links, and a log row; then
run `python -m autoassistant.literature validate-citations`.
