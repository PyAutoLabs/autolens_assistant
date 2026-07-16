# Euclid bibliography

`euclid.bib` is the citation-metadata layer for the euclid sub-wiki. The rules are
the literature wiki's — [`../../literature/bibliography/README.md`](../../literature/bibliography/README.md)
is canonical (verify from public sources, never fabricate, no PDFs or local paths,
validate after edits) — with two Euclid-specific points:

1. **Keys follow the Euclid Collaboration's shared `euclid.bib`** (`EuclidSkyOverview`,
   `Q1-SP048`, `Q1-TP004`, `Scaramella-EP1`, …) so wiki pages and collaboration LaTeX
   agree without translation. Entries in the VERBATIM section are copied unmodified
   from that shared file; do not reformat them. Papers absent from the shared file
   (the pre-Euclid classics) sit in the VERIFIED section under author-year keys,
   resolved from public arXiv/Crossref metadata.
2. **In-prep collaboration papers get no entry.** DR1-series drafts are cited in
   wiki prose as "in prep" only; add the entry when public metadata exists.

`bibkey_aliases.yaml` maps informal author-year names and
`../../literature/bibliography/autolens_literature.bib` keys onto the canonical keys
here.
