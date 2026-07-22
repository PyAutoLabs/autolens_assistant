---
title: "`PyAutoLens-Assistant`: Using Natural Language and AI to Analyse Gravitational Lenses"
tags:
  - Python
  - astronomy
  - gravitational lensing
  - artificial intelligence
  - agentic ai
  - large language models
  - natural language interfaces
authors:
  - name: James W. Nightingale
    orcid: 0000-0002-8987-7401
    affiliation: 1
    corresponding: true
  - name: Richard G. Hayes
    affiliation: 2
affiliations:
  - name: School of Mathematics, Statistics and Physics, Newcastle University, Herschel Building, Newcastle upon Tyne, NE1 7RU, United Kingdom
    index: 1
  - name: Institute for Computational Cosmology, Durham University, South Road, Durham DH1 3LE, United Kingdom
    index: 2
date: 15 July 2026
bibliography: paper.bib
---

# Summary

Stage IV weak-lensing surveys, such as Euclid [@EuclidCollaboration2025] and the Vera C. Rubin 
Observatory [@LSSTDarkEnergyScienceCollaboration2012], are mapping the distribution of mass across the Universe on 
an unprecedented scale. They include strong-lens searches which are rapidly expanding samples of galaxy-, group-, and 
cluster-scale lenses beyond hundreds of thousands [@Collett2015]. Lensing studies draw on optical and infrared imaging [@Bolton2006; @Nightingale2025COWLS], 
submm and radio interferometry [@Hezaveh2016; @Vegetti2025; @Rizzo2020], strongly lensed point sources and 
transients (e.g. quasars and supernovae) [@Wong2019; @Grillo2018], and weak-lensing shear catalogues. Together, these datasets enable studies of cosmology, dark matter, galaxy formation, 
star formation, and the early Universe. `PyAutoLens-JAX` [@NightingaleJAX2026] provides open-source software for GPU-native, 
autodifferentiable joint lensing analyses across these datasets and scales. However, combining datasets and performing 
inference across vastly different lensing scales is inherently complex, requiring 
substantial effort from the scientist to find and adapt the `PyAutoLens` API and Python syntax to build their specific 
analysis pipelines.

`PyAutoLens-Assistant` allows scientists to use natural language to construct complex, bespoke scripts for 
gravitational-lens analysis. Through an AI chat assistant such as ChatGPT or Claude, users can 
ask `PyAutoLens-Assistant` questions and obtain fully documented code needed to perform lens analysis task, which they 
then execute themselves manually. With a command-line interface (CLI) AI coding agent such as Claude Code or Codex, users 
describe the desired analysis and the agent collates the data, writes and executes Python scripts and brings together the results. The scientist 
can therefore use natural language to visualize, investigate and interpret the results. `PyAutoLens-Assistant` also 
includes a Teacher Mode for users new to the software or gravitational lensing, which can explain the core domain specific 
concepts whilest directing them to documentation and Jupyter Notebook guides to help them further build their understanding.

# Statement of need

Scientists can often inspect a dataset and know exactly which analysis they want to perform. For example, an experienced 
strong-lensing scientist might examine multi-wavelength James Webb Space Telescope (JWST) observations of the 
COSMOS-Web Ring [@Casey2023] and say:

> I want to model the F277W and F444W JWST imaging of the COSMOS-Web Ring simultaneously, which are in 
> my local folder dataset/cosmos_web_ring. Model the lens light with a multi-Gaussian expansion, its mass with a 
> singular isothermal ellipsoid plus external shear, and model the source using a multi-Gaussian expansion. For 
> speed, run the analysis on the laptop GPU using a JAX optimizer that estimates only the maximum-likelihood solution. 
> Plot the observed image at each wavelength in the top row, its lensed source model in the middle row, and its source 
> reconstruction in the bottom row.[^web]

When the prompt above is input into `PyAutoLens-Assistant` using Claude Code Opus 4.8, after the user answers a couple of 
clarifying questions, the end-to-end analysis produces \autoref{fig:cosmos_web_ring}, 
successfully delivering the output requested in the prompt.

[^web]: To use a prompt like this in an AI chat assistant such as ChatGPT or Claude, the assistant must first 
be connected to the `autolens_assistant` repository. The `autolens_assistant` README and documentation explain clearly
how to include this in the input prompt.

![The end-to-end COSMOS-Web Ring analysis produced by `PyAutoLens-Assistant` from the natural-language prompt above. 
Each column corresponds to one JWST band (F277W and F444W); the top row shows the observed image, the 
middle row the lensed source model, and the bottom row the source-plane reconstruction. 
\label{fig:cosmos_web_ring}](cosmos_web_ring.png)

The example above is a **natural-language workflow**: the scientist specifies the analysis in scientific terms, and the 
assistant translates it into executable code. Complex modelling concepts can therefore be expressed clearly even 
when implementing them manually in code would require substantial effort. By handling the Python syntax and `PyAutoLens` API, 
the assistant allows scientists to focus on what the analysis should do and why, rather than facing the implementation burden of 
how to implement it in code. `PyAutoLens-Assistant` includes several benchmarks that illustrate this further. One uses a 
three-paragraph prompt to reproduce the well-known detection of a dark matter subhalo in the strong lens SDSS J0946+1006 [@Vegetti2010]; 
another simulates CCD imaging, interferometric and weak lensing observations of a group-scale strong lens and then 
performs joint inference of all datasets.

Through Teacher Mode, `PyAutoLens-Assistant` supports scientists new to gravitational lensing by explaining concepts in 
context and directing them to relevant documentation, tutorials, and open-source lectures. It guides undergraduates and 
early-stage PhD students through the foundations of scientific data analysis and Bayesian inference, while helping 
experienced lensing researchers new to `PyAutoLens` navigate its API, syntax, and workflows. This support is increasingly 
valuable as datasets grow larger and more diverse, spanning multiple observing techniques, galaxy-, group-, and 
cluster-scale systems, and both strong and weak lensing. By reducing the need to engage directly with software syntax, 
`PyAutoLens-Assistant` allows users to learn by performing real analyses and focusing fully on the core scientific concepts
they need to learn.

# How it works

`PyAutoLens-Assistant` builds on the general knowledge and reasoning capabilities of its underlying foundation model by 
adding two version-controlled layers of PyAutoLens-specific context. Both comprise libraries of Markdown files 
structured for rapid machine reading, allowing the assistant to ground its responses in the `PyAutoLens` documentation, 
scientific literature, and established analysis workflows.

The first layer is a reference wiki comprising core and literature pages. The core wiki provides an AI-readable 
interface to the `PyAutoLens` API documentation, so that the assistant can identify and retrieve the information 
and required Python classes relevant to a user’s request. The literature wiki is derived from more than 300 strong-lensing 
papers and summarises scientific concepts, terminology, surveys, and studies of individual lens systems. This allows 
the assistant to interpret an input prompt within the wider scientific literature. Users can add papers relevant to 
their own research, giving the assistant a bespoke knowledge base tailored to their particular scientific study.

The second layer is the skills library, which provides the procedural knowledge required to perform end-to-end analyses. 
During more than a decade of `PyAutoLens` development, over 300 human-written examples have been created 
in the `autolens_workspace`, covering datasets such as CCD imaging and interferometric observations and tasks including 
simulation, data reduction, and lens modelling. These examples are extensively documented, containing 
substantially more explanatory text than code, and therefore describing both the implementation and the scientific 
reasoning behind each step. `PyAutoLens-Assistant` distils this material into concise skill files that describe how to 
perform specific tasks, which direct the assistant to the full workspace examples if more context is required.

`PyAutoLens-Assistant` does not simply match a user’s prompt to a single workspace example. The benchmark 
prompts deliberately request analyses that no individual `autolens_workspace` example performs. Instead, the assistant 
combines the relevant skills and reference material, generalizing across multiple examples to construct an end-to-end 
workflow tailored to the user’s dataset and scientific aims. This design also makes the assistant straightforward to 
maintain: as new `PyAutoLens` features and accompanying `autolens_workspace` examples are introduced, the corresponding 
skills are updated so that the assistant immediately supports the new functionality in a way that generalizes
across all other functionality.

`PyAutoLens-Assistant` can be used through an AI chat assistant such as ChatGPT or Claude. 
The `llms.txt` file defines the canonical reading order through the wikis, skills, and runnable examples, enabling 
the assistant to answer questions, explain scientific concepts, locate relevant documentation, and generate end-to-end 
modelling scripts. This mode is necessarily manual and limited: the assistant cannot normally inspect local files or 
execute code, so users must run scripts themselves and copy code, errors, figures, and other outputs between the 
conversation and their working environment. Nevertheless, conversational AI is currently the interface most familiar 
to astronomers, making this mode easy to integrate into existing workflows.

AI CLI coding agents such as Claude Code and Codex provide the complete `PyAutoLens-Assistant` workflow using the same 
curated knowledge base with substantially fewer manual steps. They can inspect `.fits` datasets directly (e.g. reading
their header information), write and execute end-to-end analysis scripts, read and then resolve Python exceptions
if code runs incorrectly. `PyAutoLens` outputs lens modeling results into directories locally which include 
structured `.json` files describing the model, sampler, results and other metadata which are specifically designed to 
be read and interpreted by the coding. Agents can also use `PyAutoLens` database and aggregator tools to combine 
large samples of analysis results into summary tables and figures. This ultimately enables users to analyse and 
interpret modelling results for thousands of lenses entirely through natural language.


# Benchmark

We benchmark `PyAutoLens-Assistant` using ChatGPT (GPT-5.6 Sol and **GPT-5.5**), Claude (Opus 4.8 and **Sonnet 5.0**), 
Claude Code (Opus 4.8), Codex (GPT-5.6 Sol), and OpenCode (**[model]**), with bold models available without a paid 
subscription at the time of writing. The primary benchmark uses the COSMOS-Web Ring prompt above, with success 
determined by whether the generated script constructs the requested model and recovers the expected lens configuration. 
All tested models pass, suggesting this task is accessible even to less capable models. Further benchmarks reproduce 
the dark-matter subhalo detection in SDSS J0946+1006 [@Vegetti2010], assess Teacher Mode, and simulate and jointly 
model CCD imaging, interferometric and weak lensing observations of a group-scale lens. The final benchmark intentionally combines 
simulation, multiple data types, a multi-galaxy mass model, and joint inference, which are documented over many different 
`autolens_workspace` examples. Thus it shows how the assistant can generalize across the wikis and skills to do complex
tasks which are not documented individually.

# Science projects and open science

When a user begins a specific scientific study, `PyAutoLens-Assistant` can create a dedicated science project: a 
logically structured folder linked to a GitHub repository containing the datasets, configuration files, analysis scripts, 
results, plotting scripts and a full transcript with the assistant for reproducibility. Every script generated by the 
assistant is fully documented and can be converted automatically into a Jupyter notebook, with its 
explanations becoming Markdown cells and its Python becoming executable code cells. The GitHub repository then 
provides a straightforward way to share results with collaborators, so they can inspect the project’s current state,
understand how each analysis was performed, and provide suggestions or build on the project. Projects can 
also interface directly with HPC facilities through bidirectional synchronization, CPU and GPU job submission and 
monitoring. If the study leads to a paper, the completed repository can therefore serve as the paper’s open-source 
companion, enabling readers to reproduce the study end to end or fork it as the starting point for further research.

# Model Context Protocol

Model Context Protocol (MCP) provides a standard way for an AI assistant to access external data and software, 
rather than relying only on information copied into a conversation. `PyAutoLens-Assistant` ships with read-only MCP 
tools that allow an AI chat assistant or AI coding agent to search, filter and retrieve completed lens-modelling results 
through natural language. For example, a Euclid lensing analysis may contain models for over 10,000 strong lenses. 
Using MCP, a scientist can point `PyAutoLens-Assistant` to a result hosting server and ask the AI agent 
to “show lenses with Einstein radii above $1.5^{\prime\prime}$” or “compare the magnification distributions of two samples,”. 
They would then receive the relevant parameters and figures without directly interfacing with the `PyAutoLens` API at all. 
MCP therefore turns a large collection of modelling outputs into an accessible, interactive scientific resource 
that scientists can explore thruogh solely via natural language.

# Natural-language development ecosystem

In March 2026, following more than a decade of exclusively human-led software development, `PyAutoLens` transitioned
to a fully natural-language, agentic-AI development ecosystem called
[`PyAutoScientist`](https://github.com/PyAutoLabs/PyAutoScientist). The ecosystem is organised as a software organism
whose core repositories mirror the roles of human organs:
[`PyAutoBrain`](https://github.com/PyAutoLabs/PyAutoBrain) acts as the reasoning centre, classifying, planning, and
routing tasks through specialist coding agents; [`PyAutoMind`](https://github.com/PyAutoLabs/PyAutoMind) captures
intent by recording plain-English development requirements and tracking them from initial ideas to completed
implementations; and [`PyAutoMemory`](https://github.com/PyAutoLabs/PyAutoMemory) provides long-term scientific memory
through cross-linked literature wikis and verifiable citations. Humans can therefore conduct software development
entirely through natural language.

# Similar software

A mature ecosystem of open-source packages supports strong-lens modelling. `lenstronomy` 
[@Birrer2018a] is a widely used, multi-purpose package for galaxy-scale lens modelling, while 
`Herculens` [@Galan2022Herculens] provides differentiable, GPU-capable modelling built on `JAX`, 
analogous to the autodifferentiable engine underlying `PyAutoLens-JAX`. Cluster-scale analyses are 
commonly performed with `Lenstool` [@Jullo2007], and other established tools such as `GLEE` [@SuyuHalkola2010].
These packages provide the numerical and statistical machinery for lens modelling, but the 
scientist must still write and adapt code directly against each package's API in order to build 
a bespoke analysis. None currently offer a natural-language or AI-agent 
interface of the kind `PyAutoLens-Assistant` introduces.

# AI usage disclosure

Generative AI tools were used to scaffold this manuscript and assist drafting. All scientific claims, 
citations, and prose are reviewed and verified by the authors.

# Acknowledgements

JWN is supported by an STFC/UKRI Ernest Rutherford Fellowship, Project Reference: ST/X003086/1. 
RGH is supported by STFC Opportunities grant ST/T002565/1.

`PyAutoLens-Assistant` builds on the open-source scientific Python ecosystem, in particular 
`NumPy` [@Numpy2011], `SciPy` [@scipy], `Astropy` [@astropy:2013], `matplotlib` [@matplotlib], `Numba` [@numba] 
and `JAX` [@jax2018github], together with the non-linear search libraries `dynesty` [@dynesty], `emcee` [@emcee] 
and `nautilus` [@nautilus]. The full set of packages the underlying `PyAutoLens` software builds on is catalogued 
in its [citation file](https://github.com/PyAutoLabs/PyAutoLens/blob/main/files/citations.bib).

# References
