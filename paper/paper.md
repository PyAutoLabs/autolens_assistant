---
title: "PyAutoLens-Assistant: Using Natural Language and AI to Analyse Gravitational Lenses"
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
an unprecedented scale, and they include strong-lens searches which are rapidly expanding samples of galaxy-, group-, and 
cluster-scale lenses [@Collett2015]. Lensing analyses draw on optical and infrared imaging, submm and radio interferometry, strongly lensed 
point sources and transients (e.g. quasars and supernovae), and weak-lensing shear catalogues. Together, these datasets 
enable studies of cosmology, dark matter, galaxy formation, star formation, and the early Universe. 
PyAutoLens-JAX [@Nightingale2021] provides open-source software for GPU-native, autodifferentiable joint lensing 
analyses across these datasets and scales. However, combining datasets and performing inference across vastly different
lensing scales is inherently complex, time consuming and error-prone, requiring substantial effort from the scientist 
to find and adapt the PyAutoLens API and Python syntax to build their specific analysis pipelines.

PyAutoLens-Assistant allows scientists to use natural language to construct complex, bespoke scripts for 
gravitational-lens analysis. With agentic coding tools such as Claude Code or Codex, users describe the desired 
analysis and the agent collates the data, writes and executes Python scripts and brings together the results. The scientist 
can then use natural language to visualize, investigate and interpret the results. Alternatively, through web-based 
conversational AI assistants such as ChatGPT, users can ask PyAutoLens-Assistant questions and obtain fully documented 
code needed to perform lens analysis task, which they then execute themselves manually. PyAutoLens-Assistant also 
includes a Teacher Mode for users new to the software or gravitational lensing, which can explain all the core domain specific 
concepts whilest directing them to documentation and Jupyter Notebook guides to help them further build their understanding.

# Statement of need

Scientists can often inspect a dataset and know exactly which analysis they want to perform. For example, an experienced 
strong-lensing scientist might examine multi-wavelength James Webb Space Telescope (JWST) observations of the 
COSMOS-Web Ring [@Casey2023] and say:

> I want to model the F115W, F150W, F277W, and F444W JWST imaging of the COSMOS-Web Ring simultaneously, which are in 
> my local folder dataset/cosmos_web_ring. Model the lens light with a multi-Gaussian expansion and its mass with a 
> singular isothermal ellipsoid plus external shear, and reconstruct the source on an adaptive rectangular mesh. For 
> speed, run the analysis on my laptop GPU using a JAX optimizer that estimates only the maximum-likelihood solution. 
> Plot the observed image at each wavelength in the top row, its lensed source model in the middle row, and its source 
> reconstruction in the bottom row.

When the prompt above is input into PyAutoLens-Assistant using Claude Code Opus 4.8, after the user answers the 
clarifying questions asked by PyAutoLens-Assistant, the end-to-end analysis produces \autoref{fig:cosmos_web_ring}, 
successfully delivering the output requested in the prompt.

![The end-to-end COSMOS-Web Ring analysis produced by PyAutoLens-Assistant from the natural-language prompt above. 
Each column corresponds to one JWST band (F115W, F150W, F277W, F444W); the top row shows the observed image, the 
middle row the lensed source model, and the bottom row the source-plane reconstruction. 
\label{fig:cosmos_web_ring}](cosmos_web_ring.png)

The example above is a natural-language workflow: the scientist specifies the analysis in scientific terms, and the 
assistant translates it into executable code. Complex modelling concepts can therefore be expressed clearly even 
when implementing them manually in code would require substantial effort. By handling the Python syntax and PyAutoLens API, 
the assistant allows scientists to focus on what the analysis should do and why, rather than facing the implementation burden of 
how to implement it in code. PyAutoLens-Assistant includes several benchmarks that illustrate this further. One uses a 
three-paragraph prompt to reproduce the well-known detection of a dark matter subhalo in the strong lens SDSS J0946+1006 [@Vegetti2010]; 
another simulates CCD imaging and interferometric observations of a group-scale strong lens and then models both datasets jointly.

Through Teacher Mode, PyAutoLens-Assistant supports scientists new to gravitational lensing by explaining concepts in 
context and directing them to relevant documentation, tutorials, and open-source lectures. It guides undergraduates and 
early-stage PhD students through the foundations of scientific data analysis and Bayesian inference, while helping 
experienced lensing researchers new to PyAutoLens navigate its API, syntax, and workflows. This support is increasingly 
valuable as datasets grow larger and more diverse, spanning multiple observing techniques, galaxy-, group-, and 
cluster-scale systems, and both strong and weak lensing. By reducing the need to engage directly with software syntax, 
PyAutoLens-Assistant allows users to learn by performing real analyses and focusing fully on the core scientific concepts
they need to learn.

# How it works

PyAutoLens-Assistant builds on the general knowledge and reasoning capabilities of its underlying foundation model by 
adding two version-controlled layers of PyAutoLens-specific context. Both comprise libraries of Markdown files 
structured for rapid machine reading, allowing the assistant to ground its responses in the PyAutoLens documentation, 
scientific literature, and established analysis workflows.

The first layer is a reference wiki comprising core and literature pages. The core wiki provides an AI-readable 
interface to the PyAutoLens API documentation, organizing key concepts, datasets, modelling methods, and software 
functionality so that the assistant can identify and retrieve the information relevant to a user’s request. The 
literature wiki is derived from more than 300 strong-lensing papers and connects scientific concepts, terminology, 
surveys, and individual lens systems to the relevant publications. This allows the assistant to interpret a request 
within its scientific context and relate it to the underlying literature. Users can also add papers relevant to their 
own research, giving the assistant a bespoke knowledge base tailored to a particular study.

The second layer is the skills library, which provides the procedural knowledge required to perform complete analyses. 
During more than a decade of PyAutoLens development, over 300 human-written examples have been created 
in autolens_workspace, covering datasets such as CCD imaging and interferometric observations and tasks including 
simulation, data reduction, and lens modelling. These examples are extensively documented, often containing 
substantially more explanatory text than code, and therefore encode both the implementation and the scientific 
reasoning behind each step. PyAutoLens-Assistant distils this material into concise skill files that describe how to 
perform specific tasks and direct the assistant to the relevant workspace examples.

Crucially, PyAutoLens-Assistant does not simply match a user’s prompt to a single existing example. The benchmark 
prompts deliberately request analyses that no individual autolens_workspace example performs. Instead, the assistant 
combines the relevant skills and reference material, generalizing across multiple examples to construct an end-to-end 
workflow tailored to the user’s dataset and scientific aims. This design also makes the assistant straightforward to 
maintain: as new PyAutoLens features and accompanying workspace examples are introduced, the corresponding skills can 
be updated so that the assistant immediately supports the new functionality.

PyAutoLens-Assistant can be accessed through either a browser-based conversational assistant or a local agentic 
coding tool. For browser-based systems such as ChatGPT or Claude, `llms.txt` provides a machine-readable entry point 
that verifies repository access and defines the canonical reading order through the instructions, skills, reference 
wikis, and runnable examples. Users can then ask questions, receive scientific explanations, interpret errors and 
figures, locate relevant examples, and generate draft end-to-end scripts. Although this mode cannot normally inspect 
local datasets or execute code, it supports the conversational AI workflow already familiar to many scientists and 
makes PyAutoLens-Assistant accessible without requiring a local coding agent.

Local agentic tools such as Claude Code and Codex provide the most complete workflow. In addition to reading the same 
instructions, skills, and reference material, they can inspect the user’s data, write and execute scripts, evaluate 
the resulting outputs, and iteratively refine an analysis through natural-language conversation. The same curated 
knowledge base therefore supports both accessible question answering in a web browser and fully agentic, end-to-end scientific analysis.

# Benchmark

The primary benchmark uses the COSMOS-Web Ring prompt presented above and evaluates whether PyAutoLens-Assistant 
can translate the same scientific request into a complete four-band JWST analysis across different models and 
interfaces. The frozen prompt is tested using Claude Code, Codex, OpenCode, and browser-based assistants such as 
ChatGPT and Claude, including models available without a paid subscription. Each run begins from a clean session, 
with the operator answering any clarifying questions minimally and without directing the assistant towards a particular implementation.

Each run is assessed using a common rubric covering the scientific validity of the lens model, correctness of the 
PyAutoLens implementation, successful construction of the requested workflow, and quality of the resulting figures and 
explanations. Complete transcripts, generated scripts, output artifacts, execution metadata, and criterion-level 
scores are recorded in the repository, making the comparison transparent and reproducible. Additional benchmarks 
test a dark-matter subhalo analysis, joint imaging and interferometric modelling of a group-scale lens, and the 
pedagogical performance of Teacher Mode.

# Science projects and open science

When a user begins a specific scientific study, PyAutoLens-Assistant can create a dedicated science project: a 
logically structured folder linked to a GitHub repository containing the datasets, configuration, analysis scripts, 
results, plotting scripts and a full transcript with the assistant for reproducibility. Every script generated by the assistant provides 
a fully documented, end-to-end analysis and can be converted automatically into a Jupyter notebook, with its 
explanations becoming Markdown cells and its Python becoming executable code cells. The GitHub repository then 
provides a straightforward way to share results with collaborators, so they can inspect the project’s current state,
understand how each analysis was performed, and provide suggestions or build on the project. Projects can 
also interface directly with HPC facilities through bidirectional synchronization, CPU and GPU job submission and 
monitoring. If the study leads to a paper, the completed repository can therefore serve as the paper’s open-source 
companion, enabling readers to reproduce the study end to end or fork it as the starting point for further research.

# Natural-language development ecosystem

In March 2026, following more than a decade of exclusively human-led software development, PyAutoLens transitioned 
to a fully natural-language, agentic-AI development ecosystem documented in 
[PyAutoScientist](https://github.com/PyAutoLabs/PyAutoScientist). This ecosystem currently comprises seven 
repositories, each named after a human organ and responsible for a distinct part of the development workflow. For 
example, [PyAutoBrain](https://github.com/PyAutoLabs/PyAutoBrain) classifies, plans, and routes tasks through 
specialist coding agents; [PyAutoMind](https://github.com/PyAutoLabs/PyAutoMind) records plain-English development 
requirements and tracks them from initial ideas to completed implementations; and 
[PyAutoMemory](https://github.com/PyAutoLabs/PyAutoMemory) maintains long-term scientific knowledge through 
cross-linked literature wikis and verifiable citations. Throughout, humans continue to direct the scientific goals 
and approve consequential decisions.

This transition has retained a strong emphasis on documentation written for human readers. 
[HowToLens](https://github.com/PyAutoLabs/HowToLens) teaches gravitational lensing and Bayesian modelling from first 
principles, while [autolens_workspace](https://github.com/PyAutoLabs/autolens_workspace) provides extensively 
documented, research-grade examples applying those concepts. These paired resources also directly support Teacher 
Mode, grounding its explanations in the same tutorials and examples through which scientists can learn PyAutoLens 
independently.

# Model Context Protocol

Consider a PyAutoLens analysis containing models for over 10,000 strong lenses, as anticipated for Euclid Data 
Release 1. Rather than downloading the results, installing PyAutoLens, and learning its output structure, a 
collaborator could interrogate the entire catalogue through natural language—for example, asking ChatGPT or 
Claude to “show lenses with Einstein radii above $1.5^{\prime\prime}$” or “compare the magnification distributions 
of two samples.” PyAutoLens-Assistant ships with its own Model Context Protocol (MCP) tools for this purpose. MCP 
is an open standard that connects AI assistants to external tools and data; the read-only tools provided by 
PyAutoLens-Assistant search, filter, and aggregate completed models before returning relevant parameters, summaries, 
and figures directly within the conversation. CLI agents can use the same interface while retaining access to the 
more flexible human-facing analysis tools documented in the wiki. MCP therefore transforms a large collection of 
modelling outputs into an accessible, interactive scientific resource that collaborators can explore safely without 
running the underlying analyses themselves.


# Similar software

A mature ecosystem of open-source packages supports strong-lens modelling. `lenstronomy` 
[@Birrer2018a] is a widely used, multi-purpose package for galaxy-scale lens modelling, while 
`Herculens` [@Galan2022Herculens] provides differentiable, GPU-capable modelling built on `JAX`, 
analogous to the autodifferentiable engine underlying PyAutoLens-JAX. Cluster-scale analyses are 
commonly performed with `Lenstool` [@Jullo2007], and other established tools such as `GLEE` [@SuyuHalkola2010].
These packages provide the numerical and statistical machinery for lens modelling, but the 
scientist must still write and adapt code directly against each package's API in order to build 
a bespoke analysis. None currently offer a natural-language or AI-agent 
interface of the kind PyAutoLens-Assistant introduces.

# AI usage disclosure

Generative AI tools were used to scaffold this manuscript and may be used to assist drafting. All scientific claims, citations, and prose are reviewed and verified by the authors.

# Acknowledgements

JWN is supported by an STFC/UKRI Ernest Rutherford Fellowship, Project Reference: ST/X003086/1. 
RGH is supported by STFC Opportunities grant ST/T002565/1.

PyAutoLens-Assistant builds on the open-source scientific Python ecosystem, in particular 
`NumPy` [@Numpy2011], `Astropy` [@astropy:2013], and `JAX` [@jax2018github].

# References
