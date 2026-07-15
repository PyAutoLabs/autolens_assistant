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
  openjournals/inara
```

The generated PDF is written to `paper/paper.pdf`.
