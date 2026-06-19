---
name: al_ingest_paper
description: Ingest a strong-lensing paper into `wiki/literature/`. Accepts a local PDF path or an arxiv URL. Reads the paper, identifies concepts and entities, creates or updates the relevant `sources/<topic>.md` stub, adds `[[wiki-link]]` cross-references on impacted concept and entity pages, and appends a dated row to `log.md`. Follows the schema in `wiki/literature/AGENTS.md`. Use when the user wants a paper added to the literature wiki so later concept pages and project-wiki entries can cite it.
---

# Ingesting a paper into the literature wiki

The literature wiki (`wiki/literature/`) is the project's persistent record of
strong-lensing scientific knowledge: **concept** pages (the *why* — mass-sheet
degeneracy, time-delay cosmography, …), **entity** pages (named surveys, lenses,
software, collaborations), and **sources** pages (one per topic, one H2 section per
paper) that everything else cites. This skill drives adding a new paper to that
record.

The binding schema lives in
[`wiki/literature/AGENTS.md`](../wiki/literature/AGENTS.md) — page types,
frontmatter, the `[[wiki-link]]` form, the per-paper section shape. Read that file
first; this skill orchestrates the ingestion but does not restate the schema.

PDFs themselves are gitignored. The in-repo convention is to keep them under
`papers/` (also gitignored), but they can live anywhere on your filesystem — give
the skill an absolute path. For arxiv-only ingestion no local PDF is needed.

## Orient

A typical ingestion produces three or four changes:

- A new H2 section in `wiki/literature/sources/<topic>.md` — the per-paper stub,
  with `File:`, `Concepts:`, and `Summary:` fields filled in.
- One or more `[[author-year-slug]]` cross-references added to existing concept or
  entity pages where this paper is now relevant.
- A new concept or entity page if the paper introduces something the wiki doesn't
  yet cover (draft as a stub; flag for upgrade later).
- A line appended to `wiki/literature/log.md` recording the date, status, and
  source.

Stub ingestion (`status: stub`) is fast — title, authors, year, one-paragraph
summary inferred from the abstract. A full read (`status: drafted`) takes longer
and produces a richer summary plus concept cross-links the abstract alone doesn't
surface. Default to stub unless the user explicitly asks for a full read or the
paper is being cited from a concept page they care about right now.

## Ask

Before doing anything, get three pieces of information from the user:

- *"Is the paper a local PDF or an arxiv URL?"* — picks the branch below.
- *"Which `sources/<topic>.md` does this paper belong to?"* If unsure, list the
  existing `wiki/literature/sources/*.md` files and ask the user to pick or
  propose a new topic. Topic slugs are kebab-case (e.g. `time-delay-cosmography`,
  `dark-matter-substructure`).
- *"Stub only, or full read?"* Default stub.

## Branch — from an arxiv URL

The flow:

1. **WebFetch the arxiv abs page** (e.g. `https://arxiv.org/abs/2401.01234`).
   The tool returns the rendered HTML; pull title, author list, year, and
   abstract.
2. **Slugify the stub key** as `<FirstAuthorSurname><Year><TitleTag>`, e.g.
   `Suyu2016Holicow`, matching the existing wiki convention.
3. **Append a per-paper H2 section** to `wiki/literature/sources/<topic>.md`
   following the schema in
   [`wiki/literature/AGENTS.md`](../wiki/literature/AGENTS.md). For stub
   ingestion the `Summary:` field is one paragraph inferred from the abstract
   and marked `(stub — verify against PDF)`. The `File:` field carries the
   arxiv URL or local path if one is available.
4. **Append one line** to `wiki/literature/log.md`:
   `YYYY-MM-DD — ingested arxiv:2401.01234 as <slug> (stub)`.

If the topic file doesn't exist yet, create it with the sources-page frontmatter
from `wiki/literature/AGENTS.md` before appending the section.

## Branch — from a local PDF

The flow:

1. **Use the Read tool with `pages="1-5"`** (or `pages="1-10"` if the abstract
   spills) to pull the front matter. For papers with intricate introductions a
   second read of `pages="6-10"` or later is fine — but stub ingestion rarely
   needs more than the front matter.
2. Title, author list, year, abstract extraction as in the arxiv branch.
3. Slug, per-paper section, log entry — same shape. The `File:` field carries
   the local path (e.g. `papers/Strong_Lens/Suyu2016Holicow.pdf` or whatever
   absolute path the user gave).
4. If the paper already has a stub on the relevant `sources/<topic>.md` (grep
   for the slug before writing), **don't duplicate** — point the user at the
   existing entry and offer to upgrade its status instead.

## Branch — full read (`status: drafted`)

When the user asks for a full read:

1. Read the rest of the PDF (or fetch additional context from the arxiv abs
   page). Ask the user how deep to go: just the key result, or
   section-by-section?
2. **Upgrade the `Summary:`** to 2–4 paragraphs covering: what the paper does,
   the key result, and what it implies for PyAutoLens-style modelling (what to
   model, what to be careful of, what assumption is being made).
3. **Identify concept cross-links.** For each concept the paper bears on:
   - If a concept page exists, append `[[author-year-slug]]` to its "Key
     results from the literature" section.
   - If it doesn't, draft a stub `wiki/literature/concepts/<slug>.md` with
     frontmatter and a one-paragraph "What it is" so the link resolves.
4. **Upgrade `status:`** from `stub` to `drafted` in the per-paper section.
5. **Log the upgrade**: `YYYY-MM-DD — upgraded <slug> stub → drafted`.

## Quality checks

A well-ingested paper:

- Has a `Summary:` an agent could quote back to a user without re-reading the
  PDF.
- Has `Concepts:` populated with at least one `[[concept-slug]]` that resolves
  to an existing or to-be-drafted concept page.
- Is cross-referenced from at least one concept or entity page (if the paper
  is genuinely about something already in the wiki).
- Has a `log.md` entry with the date and depth.

Pathological signs:

- `Summary:` reads like the abstract verbatim — paraphrase in terms a
  PyAutoLens user cares about.
- `Concepts:` is empty — either the paper is off-topic for the wiki (don't
  ingest), or you've missed an obvious link.
- Multiple stubs with the same slug — grep before writing.

## Combine

- [`al_update_wiki`](./al_update_wiki.md) — if the paper changes how
  `wiki/core/` should describe a feature, schedule a wiki refresh.
- Project-wiki entries (`wiki/project/YYYY-MM-DD-*.md`) routinely cite
  `[[author-year-slug]]` from the literature wiki — the ingestion is what
  makes those citations resolvable.

## Further reading

- **Schema** — [`wiki/literature/AGENTS.md`](../wiki/literature/AGENTS.md):
  page types, frontmatter, `[[wiki-link]]` form, and the
  concept/entity/sources structure. Read this before adding anything.
- **Existing concept pages** —
  [`wiki/literature/concepts/`](../wiki/literature/concepts/): see how
  concept pages cite per-paper sections via
  `[[sources-<topic>#author-year-slug]]`. Mirror that pattern on any new
  citation you add.
