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
with Claude Code and Codex so far:

```bash
claude        # or `codex`
```

The agent reads `CLAUDE.md` (or `AGENTS.md`) on session start and already
knows the project conventions, so you don't need to preload anything. If
you don't have PyAutoLens installed yet, the assistant will guide you
through that. Then tell it about your science case or ask it a question to
get the conversation going.

## Datasets

Two real-world strong-lens datasets ship with the repo so you can start
modelling straight away:

- `dataset/imaging/cosmos_web_ring/` — JWST NIRCam imaging of a strong
  lens, with `data.fits`, `noise_map.fits`, `psf.fits`, and a mask for
  nearby galaxies. Each band (`F115W`, `F150W`, `F277W`, `F444W`) is also
  provided separately under `wavebands/` for multi-band fits.
- `dataset/imaging/slacs0946+1006/` — HST imaging of the well-known SLACS
  lens famous for its dark-matter-subhalo detection, with positions,
  extra-galaxy centres, masks, and full metadata.

Both are raw reference data — the assistant preprocesses them on demand
when you start a session.

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

> **Draft.** Tweak the modelling brief to match your exact science case
> before pasting.

```
The strong lens SLACS0946+1006 famously has a dark matter subhalo
detection that many argue is unusually concentrated. I'd like to analyse
the HST imaging of this lens provided at
dataset/imaging/slacs0946+1006/ and reproduce that detection.

Specifically, I want this analysis to perform Bayesian model comparison
to (a) confirm a subhalo is preferred over a smooth-mass baseline by
fitting a free-position, free-mass NFW perturber across the image plane
and comparing the Bayesian evidence to the no-subhalo fit, and (b) test
the "super-concentrated" claim by comparing the standard NFW subhalo
against a more concentrated mass profile (e.g. truncated NFW or a compact
pseudo-Jaffe sphere) at the recovered position.

Set the pipeline up so the smooth mass model, source reconstruction, and
subhalo sensitivity grid are all reusable across the two comparisons, and
report the Bayesian evidence for each.
```

## License

The assistant ships agent instructions and reference material derived from the public
PyAuto\* repositories. The underlying libraries are released under their own licenses
(see each repo).
