# Canonical literature bibliography

`autolens_literature.bib` is the metadata layer paired with the literature wiki. Its
BibTeX keys are canonical inside `autolens_assistant`; `sources/*.md` explains the claims
each cited paper supports. Keep abstracts, paper summaries, PDFs, and local PDF paths out of
the bibliography and keep long summaries out of the wiki.

## Adding a paper

1. Verify the paper from a public source or the paper itself. Do not invent metadata.
2. Add one complete entry to `autolens_literature.bib`. Reuse an existing key when the
   paper is already present; otherwise choose a stable author-year key and check it is unique.
3. Add or update a compact section in the relevant `sources/*.md` file using the schema in
   [`../AGENTS.md`](../AGENTS.md). Include the canonical key and only claims directly
   supported by the paper.
4. Update concept/entity links only where the paper materially supports the page.
5. Run `python -m autoassistant.literature validate-citations`.

The [`al_ingest_paper`](../../../skills/al_ingest_paper.md) skill follows this sequence for
future users. A supplied PDF may be read during ingestion, but its path is never recorded.

## Aliases and downstream projects

`bibkey_aliases.yaml` is a flat YAML mapping from a common or historical key to the
canonical key:

```yaml
Suyu16H0: Suyu2016Holicow
```

Add an alias only for a key that is actually in use; do not create aliases speculatively.
Aliases do not rewrite a paper project's bibliography.

Before patching downstream LaTeX, inspect the target project's `.bib`: a canonical key may
not exist there, or the same paper may use a local key. Match papers by trusted metadata
(prefer DOI, then arXiv ID, then title/authors), use the project's existing key when found,
and add the canonical metadata under a conflict-free local key only when necessary. Record a
reusable local/common key here as an alias to the canonical key.

## Validation

```bash
python -m autoassistant.literature validate-citations
```

Missing source keys, duplicate canonical keys, and aliases with missing targets fail.
Canonical entries not yet represented by a source entry are reported but do not fail; this
allows metadata to exist before the wiki has a claim that needs it. Use `--show-all` to print
the complete unreferenced-key list.
