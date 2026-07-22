# PyAutoLens Assistant

<img src="https://github.com/Jammy2211/PyAutoLogo/blob/main/gifs/pyautolens.gif?raw=true" width="900" />

When two or more galaxies are aligned perfectly down our line-of-sight, the
background galaxy appears multiple times. This is strong gravitational lensing,
and **PyAutoLens** makes it simple to model strong gravitational lenses.

This repository is the **PyAutoLens Assistant**: an AI assistant you talk to in
natural language to do gravitational lensing science. 

## Getting Started

There are two ways to use `autolens_assistant`, and you can start with either
depending on how you are used to using AI:

### AI Chat Assistant

Ask questions to a conversational AI assistant such as **ChatGPT** or **Claude**
in a desktop browser or web. This requires you to do two things:

- Make sure your assistant has a **GitHub connector** enabled so it can read this repository and in your initial prompt give it the URL to this repository (https://github.com/PyAutoLabs/autolens_assistant).
- Make sure your initial prompt points the assistant explicitly at the file [`llms.txt`](llms.txt), which gives it the initial instructions on how `autolens_assistant` works.

Here is a good initial prompt which you can copy and paste it ChatGPT or Claude to try it out, noting that
data for the COSMOS-Web Ring is included in this workspace as an example:

```
GitHub Use the autolens_assistant (www.github.com/PyAutoLabs/autolens_assistant with the GitHub synchronization, 
first reading its llms.txt file for initial start up.

Find the data on the Cosmos-Web ring, give me a short script to plot it in PyAutoLens and then given that I'm a 
new user give me an overview of the different ways we can perform strong lens modeling of this system.
```

The above prompt will give advise that is ideal for learning the PyAutoLens API, working out how to perform a 
calculation, and via follow up questions will allow you to ask specific questions about how to do tasks in PyAutoLens.

However, the `autolens_assistant` can easily held you with complex tasks and produce end-to-end modeling scripts.
If you copy and paste the prompt below into ChatGPT you'll get an end-to-end Python script for multi-wavelength
lens modeling of the COSMOS-Web Ring!

```
GitHub Use the autolens_assistant (www.github.com/PyAutoLabs/autolens_assistant with the GitHub synchronization, 
first reading its llms.txt file for initial start up.

I want to model the F277W and F444W JWST imaging of the COSMOS-Web Ring simultaneously, which are in 
the folder dataset/cosmos_web_ring. Model the lens light with a multi-Gaussian expansion (MGE), its mass with a singular 
isothermal ellipsoid plus external shear, and model the source also using an MGE. For speed, run the analysis on my 
laptop GPU using a JAX optimizer that estimates only the maximum-likelihood solution. Plot the observed image at 
each wavelength in the top row, its lensed source model in the middle row, and its source on the bottom row.
```

### AI Coding Agent (CLI)

`autolens_assistant` has first class support for AI coding agents, such as **Claude Code** or **Codex**. A coding agent 
is installed on your machine as a command-line (CLI) tool that run in your terminal. It can inspect your `.fits` image 
data, write and run `PyAutoLens` analysis scripts in Python, and perform end-to-end lens modeling with the results output
to your hard-disk for your inspection. If `PyAutoLens` is not installed on your computer yet, the `autolens_assistant` 
will install it for you after you input your first prompt.

To start, clone the `autolens_assistant` repo:

```bash
git clone https://github.com/PyAutoLabs/autolens_assistant.git
cd autolens_assistant
```

Next, open your AI coding agent in your terminal inside the `autolens_assistant` folder you just cloned. 

You can get started using the same COSMOS-Web ring examples above:

```
Find the data on the Cosmos-Web ring, give me a short script to plot it in PyAutoLens and then given that I'm a 
new user give me an overview of the different ways we can perform strong lens modeling of this system.
```

Or, if you want to see `autolens_assistant` perform end-to-end lens modeling:

```
I want to model the F277W and F444W JWST imaging of the COSMOS-Web Ring simultaneously, which are in 
the folder dataset/cosmos_web_ring. Model the lens light with a multi-Gaussian expansion (MGE), its mass with a singular 
isothermal ellipsoid plus external shear, and model the source also using an MGE. For speed, run the analysis on my 
laptop GPU using a JAX optimizer that estimates only the maximum-likelihood solution. Plot the observed image at 
each wavelength in the top row, its lensed source model in the middle row, and its source on the bottom row.
```

## Modes

The assistant works in two modes, depending on your lens of experience and expertise with gravitational lensing
and **PyAutoLens**:

- **Assistant Mode:** `An assistant to help you use PyAutoLens, which assumes you know the underlying lensing theory and scientific analysis.`
- **Teacher Mode:** `Teaches you the fundamentals of lensing as you use the assistant, aimed at undergraduates and early PhD students.`

You do not need to choose which mode you use, `autolens_assistant` will infer it based on your input prompts and
messages. However, if your prompt says to use a certain mode, it will.

`autolens_assistant` will also adopt its behaviour to your prompts. Want it to plan out lens modeling tasks,
ask you lots of questions before performing them and explain every step of what its doing, then tell it!
Want it to perform a task end-to-end without consulting you, then just tell it to "one-shot" the task! Just
tell `autolens_assistant` what you want from it and it will adapt.

## Example Prompt 1 (Teacher Mode): Simulate, inspect and model a strong lens

A good first session if you're new to PyAutoLens and want to learn the modelling
workflow end-to-end on data you generate yourself. Working from a simulation keeps
things simple, the data is clean, you know the true answer, and there's nothing to
inspect, so the focus stays on understanding each step.

```
Teacher mode.

I'm new to PyAutoLens and want to learn the basic workflow end-to-end. Can you
walk me through a simple example where we: 1) simulate Euclid-like imaging of
a simple strong lens; 2) sake some plots of the lens and investigate its properly and;
3) fit the data and recover the lens model.
```

## Example Prompt 2 (Assistant Mode): Detect a Dark Matter Subhalo in SLACS0946+1006

This example shows how far the assistant can be pushed in terms of scientific analysis.
The prompt aims to reproduce the famous subhalo detection in the strong lens SDSSJ0946+1006,
and show that it density profile is unusually concentrated. It uses Bayesian
model comparison to do this.

The lens modeling required for this analysis may take hours or days. The 
last sentence of the prompt asks the agent to estimate the run time and,
if needed, walk you through setting the analysis up on a High Performance
Computer (HPC) you have access to.

```
Assistant mode.

The strong lens SDSSJ0946+1006 famously has a dark matter subhalo
detection that studies show is unusually concentrated. Analyse
the HST imaging of this lens provided at
dataset/imaging/slacs0946+1006/ and reproduce the detection.

Perform Bayesian model comparison to (a) confirm a subhalo is preferred 
over a smooth-mass baseline which does not include a subhalos, and (b) test
the "super-concentrated" claim by comparing an SIS subhalo model
against a more shallow NFW mass profile at the recovered position.

For the lens light use a Multi Gaussian Expansion, for its mass use a 
Power Law plus shear and use a Delaunay mesh for the source reconstruction.

Assess whether the analysis will run fast on my laptop / PC CPU or GPU,
and if not, set this up as a small project on the HPC I have access to.
```

## Example Prompt 3 (Assistant Mode): Complex tasks combining different data and lensing scales

`PyAutoLens` has JAX support throughout, providing fast modeling via GPU acceleration and automatic differentiation. 
Galaxy-, group-, and cluster-scale lens models can be constrained using CCD imaging, interferometer visibilities, 
point-source observables, and weak-lensing catalogues fully in JAX. These are not isolated capabilities, you can 
perform joint inference combining them all. With so more customization, the challenging part was combining the different
APIs to produce a single Pythons script that could perform the modeling. With `autolens_assistant` this is no longer
a problem, you just describe the task in natural language and you get the analysus you need:

```
Assistant mode.

Simulate imaging and interferometer data of a group-scale strong lens, which is composed of
two SIE lens galaxies and a quadruply imaged Cored Sersic background source. Include a weak lensing
shear catalogue comprising 30 galaxies up to 20.0" away from the group centre.

Next, write a script which perform modeling of this dataset, simultaneously fitting the imaging data, 
interferometer data and shear catalogue. Model the foreground lens using  multi gaussian Expansions for its 
light, SIE's for each lenses mass and a multi Gaussian expansion for the background source. 

After this fit has been judged successful, do a follow up lens model that uses a pixelized source 
reconstruction.
```

### Supported Coding Agents 

CLI Coding agents like Claude and codex may require a paid subscription. The table below shows the 
coding agents `autolens_assistant` has been tested using and whether they offer a free plan. However,
pretty much any coding agent available should work with `autolens_assistant`

| Interface | Support | Access and cost | Notes |
|---|---|---|---|
| **Claude Code** | Primary; thoroughly tested | Normally a [paid Claude subscription or metered API usage](https://code.claude.com/docs/en/costs). | Loads the canonical instructions through `CLAUDE.md`. |
| **Codex CLI** | Primary; thoroughly tested | A [limited free plan](https://developers.openai.com/codex/pricing/) may be available; paid plans or API billing provide more usage. | Reads `AGENTS.md` directly and can edit and run the project locally. |
| **Gemini CLI** | Supported | Offers [limited free quotas](https://github.com/google-gemini/gemini-cli/blob/main/docs/resources/quota-and-pricing.md); subscriptions or usage billing provide higher limits. | Loads the repository instructions through `.gemini/settings.json`. |
| **OpenCode** | Supported | The client is open source; model-provider access may be free or paid. | Use it from the repository root so it can discover the project context. |

## Science Project

When you begin a specific scientific study, `autolens-assistant` can create a dedicated science project: a 
logically structured folder linked to a GitHub repository containing the datasets, configuration files, analysis scripts, 
results, plotting scripts and a full transcript with the assistant for reproducibility. Every script generated by the 
assistant is fully documented and can be converted automatically into a Jupyter notebook, with its 
explanations becoming Markdown cells and its Python becoming executable code cells. The GitHub repository then 
provides a straightforward way to share results with collaborators, so they can inspect the project’s current state,
understand how each analysis was performed, and provide suggestions or build on the project. Projects can 
also interface directly with HPC facilities through bidirectional synchronization, CPU and GPU job submission and 
monitoring. If the study leads to a paper, the completed repository can therefore serve as the paper’s open-source 
companion, enabling readers to reproduce the study end to end or fork it as the starting point for further research.

To start a science project, just add it to your input prompt:

```
Start a science project for my SDSSJ0946+1006 analysis.
```

## Benchmarks

The three example prompts above (plus the hard cross-package benchmark) are
also shipped as **frozen benchmark prompts** under [`benchmarks/`](benchmarks/),
with scoring rubrics and a small harness that records each run's conversation,
results and score. Run them against different AI agents and models — or the
same model on different days — and the committed run records in
`benchmarks/runs/` plus the regenerated tables in `benchmarks/RESULTS.md` give
you an evidence-backed comparison of how well each setup drives the assistant.
The protocol is in [`benchmarks/README.md`](benchmarks/README.md).

## Scientific Context

The assistant doesn't just know how to use PyAutoLens API — it ships with a
strong-lensing **literature wiki** at `wiki/literature/`. This provides
contexrt on other 300 strong lensing papers, broken down into concept pages
(e.g.mass-sheet degeneracy, dark-matter substructure, time-delay cosmography, 
multipoles), surveys (e.g. SLACS, H0liCOW, TDCOSMO, Euclid Q1, Abell 1201,
…), and other subject categories. This means that, for example, if your prompt
mentions ALMA and submm galaxies, the assistant's response will consider
the wider scientific literature and context.

This **base** literature wiki can and should be extended by you, with papers that are
specifically relevant to your scientific study. Doing this is simply, simply
point the assistant to the papers and it'll ingest them for you:

```
Ingest the following paper into the literature wiki so you can use it
when we talk about subhalo detection:

  arXiv:2401.01234

(Or, if you have the PDF locally: /path/to/subhalo_paper.pdf)

Once it's ingested, summarise the paper and how it complements similar
works in the literature wiki
```

The more papers relevant to your science case you load in, the better
the assistant will be at framing decisions, citing prior work, and
spotting when a result has caveats.

## How does PyAutoLens-Assistant actually work?

The `autolens-assistant` starts with the general knowledge and reasoning capabilities of its 
the underlying foundation model you call it with (e.g. ChatGPT's GPT5.6Sol model, Claude's Opus 4.8 model). 
The `autolens-assistant` supplements this with the scientific wiki above and two more sets of AI-readable markdown. 
The folder `wiki/core` provides it with a quick look-up mechanism of the PyAutoLens API documentation. The folder
`skills` pairs it with the end-to-end analysis scripts found in the [`autolens_workspace`](https://github.com/PyAutoLabs/autolens_workspace). When the `autolens-assistant` 
receives your prompt, it scans these folders to give you the best possible answer
you need. The JOSS paper located in the `paper` folder provides a more detailed description.

## Natural-language development ecosystem

In March 2026, following more than a decade of exclusively human-led software development, `PyAutoLens` transitioned
to a fully natural-language, agentic-AI development ecosystem called
[`PyAutoScientist`](https://github.com/PyAutoLabs/PyAutoScientist). The ecosystem is organised as a software organism
whose core repositories mirror the roles of human organs:
[`PyAutoBrain`](https://github.com/PyAutoLabs/PyAutoBrain) acts as the reasoning centre, classifying, planning, and
routing tasks through specialist coding agents; [`PyAutoMind`](https://github.com/PyAutoLabs/PyAutoMind) captures
intent by recording plain-English development requirements and tracking them from initial ideas to completed
implementations; and [`PyAutoMemory`](https://github.com/PyAutoLabs/PyAutoMemory) provides long-term scientific memory
through cross-linked literature wikis and verifiable citations. Humans remain firmly in the loop, defining the
scientific objectives, supervising the development process, and approving consequential decisions.

## License

This repository is released under the [MIT License](LICENSE), consistent with the wider
PyAuto\* ecosystem. The assistant ships agent instructions and reference material derived
from the public PyAuto\* repositories; the underlying libraries are released under their
own licenses (see each repo).
