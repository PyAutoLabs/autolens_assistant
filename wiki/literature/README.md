# wiki/literature/

The literature sub-wiki holds compiled syntheses of the strong-lensing scientific
literature: concepts, named entities (surveys, lenses, software, collaborations),
and per-paper bibliography pages.

> **Authoritative schema:** [`CLAUDE.md`](./CLAUDE.md) describes the page types,
> frontmatter, cross-reference convention (`[[page-slug]]`), and how an assistant
> should use this wiki. Read it before adding or editing pages.

## Layout

| Folder | Page type | Scope |
|---|---|---|
| `concepts/` | concept | one scientific concept per page (e.g. `mass-sheet-degeneracy.md`) |
| `entities/` | entity | one named thing per page (survey, lens, code, collaboration) |
| `sources/` | sources | bibliography of papers on one topic, one section per paper |
| `index.md` | meta | top-level navigation |
| `log.md` | meta | append-only compilation log |

## Where the PDFs live

The literature wiki compiles syntheses of papers whose PDFs are typically kept
**outside this repo** (in a sibling `PyAutoPaper/` checkout or wherever the user
stores them). The wiki pages reference each PDF by its relative path; collaborators
who clone this repo can read every wiki page but must obtain PDFs separately
(usually from arXiv or the journal site).

## When you, the agent, should write here

- A user asks about a specific lensing paper or result and you can find the topic
  in the wiki — quote and cite from the existing page.
- A new paper has been read and the user explicitly asks for the wiki to be
  updated. Follow the schema in `CLAUDE.md`: add a section to the relevant
  `sources/<topic>.md` page, update the relevant `concepts/` and `entities/`
  pages with `[[link]]` references, and append a line to `log.md`.

Do **not** treat this folder as scratch space, and do **not** invent citations:
the schema demands that any cited result trace back to an actual paper stub.
