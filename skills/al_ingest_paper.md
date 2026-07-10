---
name: al_ingest_paper
description: Add a verified strong-lensing paper to the literature record — project-local (`wiki/project/bibliography.md`) by default when working inside a science project, or the shared literature wiki + canonical BibTeX layer when in the assistant clone or on explicit promotion. Accepts a local PDF or public paper URL, resolves or adds canonical metadata, writes a compact claim-oriented source entry, updates relevant concept/entity links, validates key consistency, and never records local PDF paths. Use when a user wants a paper added so future assistants can cite its supported claims reliably.
---

# Ingesting a paper into the literature wiki

Read [`wiki/literature/AGENTS.md`](../wiki/literature/AGENTS.md) and
[`wiki/literature/bibliography/README.md`](../wiki/literature/bibliography/README.md)
before editing. The wiki and bibliography are paired but distinct:

- `sources/*.md` says which claims a paper supports.
- `bibliography/autolens_literature.bib` holds canonical metadata and keys.
- `bibliography/bibkey_aliases.yaml` records known alternate keys.

Do not save PDFs, local PDF paths, abstracts, or long paper summaries.

## Orient

Ingestion makes a paper discoverable from scientific concepts while preserving a reliable
citation key. A normal addition changes the canonical `.bib`, one compact source section,
relevant concept/entity links, and `log.md`.

## Target — project-local or shared?

Two destinations; pick before editing anything (the hybrid rule: general concepts stay
shared, analysis-specific papers stay in the project):

- **Inside a science project** (the working repo has `project.yaml` and a thin refer-back
  `AGENTS.md`): the default target is the **project's** `wiki/project/bibliography.md` — one
  `##` section per paper, exactly the "record claim support" shape below. Reuse the
  assistant's canonical BibTeX key when the paper is already in `autolens_literature.bib`
  (read-only lookup via refer-back); otherwise use a stable author-year key, aligned with the
  project's own paper `.bib` if one exists. Do **not** edit the assistant clone's
  `bibliography/` or `sources/` from a project session — that is promotion, below. The shared
  quality gate does not run against a project page; keep it consistent by inspection.
- **In the assistant clone, or on explicit promotion** of a generally-useful paper out of a
  project: the shared `wiki/literature/` flow below — canonical `.bib`, `sources/<topic>.md`,
  concept/entity links, `log.md`, `validate-citations`. Promotion is a deliberate act, never
  the default, and is a verbatim copy of the project section into the right
  `sources/<topic>.md` plus the canonical-metadata steps.

## Ask

Establish only what is not already supplied:

- the local PDF or public URL;
- the relevant `sources/<topic>.md` page;
- whether the user needs specific claims extracted or metadata-only staging.

If the topic is unclear, show the existing source filenames and ask one focused question.

## Branch — resolve canonical metadata

1. Read the paper or its authoritative public record. A local PDF is temporary input; never
   copy or record its path.
2. Search `autolens_literature.bib` by DOI, arXiv ID, and normalized title before using a key.
3. If present, reuse its canonical key. If absent, add verified BibTeX metadata under a
   stable, unique author-year key. Do not fabricate missing fields or rename unrelated keys.
4. Add an alias only when a common or project-local alternate key is actually known.

For a downstream paper project, inspect its `.bib` separately. Match by DOI, arXiv ID, then
title/authors; use the project's existing key when present. Never assume this repository's
canonical key exists in the target project.

## Branch — record claim support

Add one H2 section to the relevant `sources/*.md` file:

```markdown
## Author Year — short tag

**Canonical BibTeX key:** `KeyYYYY`
**Reference:** DOI/arXiv/journal reference if known
**Concepts:** [[concept-1]], [[entity-1]]

**Supports:**
- Claim this paper directly supports.
- Another claim this paper directly supports.

**Use when:**
- Situation where the citation is appropriate.

**Do not use for:**
- Similar but unsupported claim.
```

Use 2–5 support bullets. Each must be directly supported by the paper. Keep prose short;
paraphrase rather than copying the abstract. If only metadata was verified, add an explicit
TODO for claim extraction instead of inferring claims.

Update concept/entity pages only where this paper materially supports existing text. Create
a new page only when the paper introduces a genuinely missing concept or named entity.

## Quality gate

Append a concise dated row to `wiki/literature/log.md`, then run:

```bash
python -m autoassistant.literature validate-citations
```

Fix missing source keys, duplicate canonical keys, and invalid alias targets. Unreferenced
BibTeX entries are informational. A successful ingestion leaves no local path in tracked
files and no unsupported claim in the source entry.

## Combine

- Use `al_update_wiki` only if the paper changes curated `wiki/core/` API documentation.
- Project notes may link the source section, but LaTeX citations must use the target
  project's resolved local BibTeX key.
