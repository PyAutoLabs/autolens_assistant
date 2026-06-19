# wiki/literature/

The literature sub-wiki holds compiled syntheses of the strong-lensing scientific
literature: concepts, named entities (surveys, lenses, software, collaborations),
and per-paper bibliography pages.

> **Authoritative schema:** [`AGENTS.md`](./AGENTS.md) describes the page types,
> frontmatter, cross-reference convention (`[[page-slug]]`), and how an assistant
> should use this wiki. Read it before adding or editing pages.

This is a **self-contained base literature wiki** that ships with the assistant. It is not
tied to any external paper repository — every page stands on its own and papers are cited by
arXiv/DOI link and/or author-year citation, never by a local file path. Users extend it with
the papers their own project needs.

## Layout

| Folder | Page type | Scope |
|---|---|---|
| `concepts/` | concept | one scientific concept per page (e.g. `mass-sheet-degeneracy.md`) |
| `entities/` | entity | one named thing per page (survey, lens, code, collaboration) |
| `sources/` | sources | bibliography of papers on one topic, one section per paper |
| `index.md` | meta | top-level navigation |
| `log.md` | meta | append-only compilation log |

## How papers are referenced

Each paper is cited by a **public reference** — an arXiv/DOI link and/or an author-year
citation — recorded on the `**Reference:**` line of its `sources/` entry. There are no PDFs
in this repo; a reader sources the paper from arXiv or the journal using that reference. See
[`AGENTS.md`](./AGENTS.md) "References" for the exact convention.

## When you, the agent, should write here

- A user asks about a specific lensing paper or result and you can find the topic
  in the wiki — quote and cite from the existing page.
- A new paper has been read and the user explicitly asks for the wiki to be
  updated. Follow the schema in `AGENTS.md`: add a section to the relevant
  `sources/<topic>.md` page, update the relevant `concepts/` and `entities/`
  pages with `[[link]]` references, and append a line to `log.md`.

Do **not** treat this folder as scratch space, and do **not** invent citations:
the schema demands that any cited result trace back to an actual paper stub.
