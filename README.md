# PyAutoLens Assistant

<img src="https://github.com/Jammy2211/PyAutoLogo/blob/main/gifs/pyautolens.gif?raw=true" width="900" />

When two or more galaxies are aligned perfectly down our line-of-sight, the
background galaxy appears multiple times. This is strong gravitational lensing,
and **PyAutoLens** makes it simple to model strong gravitational lenses.

This repository is the **PyAutoLens Assistant**: an AI assistant you talk to in
natural language to do gravitational lensing science. Describe your data,
ask modelling questions, or discuss lensing theory — the assistant explains
the science as it goes and writes runnable PyAutoLens Python workflows that
stay in your repo.

## Getting Started

Clone the `autolens_assistant` repo:

```bash
git clone https://github.com/PyAutoLabs/autolens_assistant.git
cd autolens_assistant
```

Open a CLI AI agent session inside the repo. The assistant has been tested
with four CLI agents:

- **Claude Code** and **Codex** — tested most thoroughly and give the best
  results. Recommended if you have access to them.
- **Gemini CLI** and **OpenCode** — also work, and both offer free models, so
  you can use the assistant without a paid subscription. Of the two, Gemini CLI
  is preferred over OpenCode.

```bash
claude        # or `codex`, `gemini`, `opencode`
```

Each agent automatically reads the project's instructions on session start — they live in
`AGENTS.md` (Claude Code loads it via a one-line `CLAUDE.md`, and Gemini CLI via `.gemini/`),
so you don't need to preload anything. If
you don't have PyAutoLens installed yet, the assistant will guide you
through that. Then tell it about your science case or ask it a question to
get the conversation going.

## New User Example Prompt: Model JWST Imaging of a Strong Lens

A good starting point if you're new to PyAutoLens **and** less familiar with
strong lensing. It points the assistant at the bundled JWST data and asks
for a guided source-reconstruction walkthrough:

```
The folder dataset/imaging/cosmos_web_ring contains JWST imaging of a real
strong lens.

I want to work out what the source galaxy looked like before it was lensed
— how do I do this? Can you help me get started? I'm not too familiar with
how strong lens modelling works, so explain to me what you're doing as we
go.
```

## Experienced Lenser Example Prompt: Detect a Dark Matter Subhalo in SLACS0946+1006

For users already comfortable with strong lens modelling who want to see
how far the assistant can be pushed. SLACS0946+1006 has a famous subhalo
detection that is argued to be unusually concentrated; this prompt asks
the assistant to reproduce that detection and quantify the concentration
via Bayesian model comparison.

Depending on your available hardware, this analysis may take hours. The
last sentence of the prompt asks the agent to estimate the run time and,
if needed, walk you through setting the analysis up on a High Performance
Computer (HPC) you have access to.

```
The strong lens SLACS0946+1006 famously has a dark matter subhalo
detection that many argue is unusually concentrated. I'd like to analyse
the HST imaging of this lens provided at
dataset/imaging/slacs0946+1006/ and reproduce that detection.

Specifically, I want this analysis to perform Bayesian model comparison
to (a) confirm a subhalo is preferred over a smooth-mass baseline by
fitting a free-position, free-mass SIS perturber across the image plane
and comparing the Bayesian evidence to the no-subhalo fit, and (b) test
the "super-concentrated" claim by comparing the SIS subhalo
against a more shallow NFW mass profile at the recovered position.

Set the pipeline up so the smooth lens light and mass model, the
pixelized source reconstruction, and the subhalo results are all
inspectable on my computer, and report the Bayesian evidence for each
comparison.

Assess whether the analysis will run fast on my laptop / PC GPU,
and if not, set this up as a small project on the HPC I have access to.
```

## Scientific Context

The assistant doesn't just know the PyAutoLens API — it ships with a
strong-lensing **literature wiki** at `wiki/literature/` covering the
science the modelling is in service of. It has concept pages (mass-sheet
degeneracy, dark-matter substructure, time-delay cosmography, multipoles,
…), named-entity pages (SLACS, H0liCOW, TDCOSMO, Euclid Q1, Abell 1201,
…), and per-topic bibliographies summarising the relevant published
papers. When you ask a science question or start a modelling discussion,
the assistant grounds itself in this material rather than guessing from
general knowledge.

If a paper matters to your science case and isn't in the wiki yet, you
can ask the assistant to ingest it. Give it either a local PDF or an
arXiv URL and it adds a summary to the right topic bibliography, cross-
links the relevant concepts and entities, and from then on can cite the
paper in answers:

```
Ingest the following paper into the literature wiki so you can use it
when we talk about subhalo detection:

  arXiv:2401.01234

(Or, if you have the PDF locally:
  /path/to/subhalo_paper.pdf)

Once it's ingested, summarise what it adds beyond what the wiki already
covers on dark-matter substructure.
```

The more papers relevant to your science case you load in, the better
the assistant will be at framing decisions, citing prior work, and
spotting when a result has caveats.

## License

The assistant ships agent instructions and reference material derived from the public
PyAuto\* repositories. The underlying libraries are released under their own licenses
(see each repo).
