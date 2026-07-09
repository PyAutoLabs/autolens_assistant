# wiki/core/

Curated reference content for the PyAuto\* lensing stack. The core wiki documents
*what* the API contains; the skills in [`../../skills/`](../../skills/) document
*how* to use it. The two siblings — [`../literature/`](../literature/) and
[`../project/`](../project/) — hold external papers and a per-clone journal
respectively (see [`../README.md`](../README.md) for the overview).

## Organisation

- [`index.md`](./index.md) — top-level map; the entry point for an agent or human
  reader.
- [`stack/`](./stack/) — one page per source library, plus an overview of how they
  fit together.
- [`concepts/`](./concepts/) — physics + framework explanations: lensing basics,
  tracer, profiles, searches, samples, SLaM, units, etc.
- [`api/`](./api/) — task-oriented API catalogues: every search, every light profile,
  every mass profile, plotting entry points, configuration system.
- [`operations/`](./operations/) — installation, sandbox tuning, HPC.

## Page format

Every wiki page begins with YAML frontmatter:

```yaml
---
title: <Page title>
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/search/nest/nautilus/
    pinned_commit: <sha-or-tag>
last_updated: 2026-05-22
---
```

The `sources` field is what [`../../skills/al_update_wiki.md`](../../skills/al_update_wiki.md)
reads to know when a page is stale relative to upstream. After every source file
change between `pinned_commit` and current HEAD, the relevant section of the page is
rewritten and `pinned_commit` is bumped.

`pinned_commit` may be a short SHA or a tag. Use the SHA in production; tags are
fine for pages that lag releases by design.

## Source citations inside page bodies

Inside a wiki page, code references use the **project name + path relative to the
project's repo root**, identical to the skill convention:

```
See `PyAutoFit:autofit/non_linear/search/nest/nautilus/` for the implementation.
```

Resolve project names via [`../../sources.yaml`](../../sources.yaml). Never embed
absolute local paths.

## Adding a new page

1. Pick the right subdirectory (`stack/`, `concepts/`, `api/`, or `operations/`).
2. Add the YAML frontmatter, including all source paths the page depends on and a
   pinned commit.
3. Hand-write the body. The wiki is curated; auto-generated dumps belong in each
   library's own `docs/` folder.
4. Link the new page from `index.md` and from any skill that should cite it.
