# PyAutoLens-Assistant JOSS paper

This directory contains the PyAutoLens-Assistant paper for submission to the
[Journal of Open Source Software](https://joss.theoj.org/). It is hosted with the
software it describes, and is the sibling of the PyAutoLens-JAX paper in
`PyAutoLens/paper_jax/`.

## Files

- `paper.md` — manuscript and JOSS metadata.
- `paper.bib` — bibliography cited by the manuscript. Entries are copied verbatim
  from `../wiki/literature/bibliography/autolens_literature.bib` so the paper and
  the literature wiki cannot drift apart.
- `paper.pdf` — local build output; do not commit it.

## Drafting checklist

- Confirm the full author list, affiliations, ORCIDs, corresponding author, and
  submission date. The current block mirrors the PyAutoLens-JAX paper.
- Keep the manuscript within the current JOSS target of 750–1750 words.
- Replace every drafting comment (`State of the field`, `Research impact
  statement`, `Acknowledgements`) with specific, evidenced prose.
- Compare against other domain-specific scientific AI assistants and
  general-purpose coding assistants in “State of the field”.
- **Report real benchmark results.** The `Benchmark examples` section is written
  in the future tense because `../benchmarks/RESULTS.md` currently records no runs
  for any benchmark. Once the suite has been run, replace that prose with measured
  outcomes — do not claim results the repository cannot evidence.
- The paper describes **three representative** benchmarks; the repository ships
  **four** prompts (the fourth is `hard_group_multi.md`). This framing is
  deliberate. If the fourth is later described, update the wording in both places.
- Verify every bibliography entry resolves and is the intended paper.
- Keep the AI usage disclosure accurate as the manuscript evolves.

The current format requirements are documented in the
[JOSS paper guide](https://joss.readthedocs.io/en/latest/paper.html).

## Build the paper

From the `autolens_assistant` repository root, compile with the official JOSS
Inara image:

```bash
docker run --rm \
  --volume "$PWD/paper:/data" \
  --user "$(id -u):$(id -g)" \
  --env JOURNAL=joss \
  openjournals/inara -p -o pdf paper.md
```

The generated PDF is written to `paper/paper.pdf`.

`-p` selects the *publishing* PDF. Drop it and Inara defaults to the draft
build, which stamps a DRAFT watermark and numbers every line — useful for
reviewers citing a line, but the numbers overlap the left-hand sidebar on page
one. The layout is otherwise identical, so read the publishing build.

The `Draft JOSS PDF` GitHub Actions workflow builds both on every change under
`paper/`, as the `paper-pdf` and `paper-pdf-draft` artifacts, so no local Docker
or LaTeX install is needed.

## Submit to arXiv

`paper.md` stays the single canonical manuscript — do not maintain a second
arXiv version. JOSS's intended route is EditorialBot's
`@editorialbot generate preprint`, which needs a submission issue; before that
exists, `./make_arxiv.sh` produces the same thing from Inara's `preprint`
target and writes `arxiv/arxiv-submission.tar.gz` for upload.

The bundle is just `paper.tex` plus the figures. No `.bib` or `.bbl` is needed:
citeproc bakes the reference list into the `.tex` as a `CSLReferences`
environment, so arXiv's `pdflatex` resolves every citation in two passes.

One patch is applied on the way. Inara's `preprint.latex` template omits
pandoc's `common.latex` partial, which is where `\pandocbounded` is defined —
and since pandoc 3.5 every figure is wrapped in that macro. The generated
`.tex` therefore calls a command its own preamble never defines, and the build
dies with `Undefined control sequence` at the first `\includegraphics`. This
affects the plain `docker run ... -o preprint` invocation too, so the patch is
not optional. The JOSS PDF is unaffected, since its template does include the
partial. `make_arxiv.sh` injects the definition and then test-compiles with
`pdflatex` exactly as arXiv will, failing loudly rather than handing you a
tarball that breaks on upload. Drop the patch step if Inara fixes the template.
