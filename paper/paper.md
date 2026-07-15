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
affiliations:
  - name: Institute for Computational Cosmology, Durham University, United Kingdom # Update to My Newcastle affiliation
    index: 1
date: 15 July 2026
bibliography: paper.bib
---

# Summary

Stage IV weak-lensing surveys, such as Euclid [@EuclidCollaboration2025] and the Vera C. Rubin 
Observatory [@LSSTDarkEnergyScienceCollaboration2012], are mapping the distribution of mass across the Universe on 
an unprecedented scale, while strong-lensing searches are rapidly expanding samples of galaxy-, group-, and 
cluster-scale lenses. Lensing analyses draw on optical and infrared imaging, submm and radio interferometry, strongly lensed 
point sources and transients (e.g. quasars and supernovae), and weak-lensing shear catalogues. Together, these datasets 
enable studies of cosmology, dark matter, galaxy formation, star formation, and the early Universe. 
PyAutoLens-JAX [@Nightingale2021] provides open-source software for GPU-native, autodifferentiable joint lensing 
analyses across these datasets and scales. However, combining datasets and performing inference across vast different
lensing scales is inherently complex, time consuming and error-prone, requiring substantial effort from the scientist 
to find and adapt the PyAutoLens API and Python syntax to build their specific analysis pipelines.

PyAutoLens-Assistant allows scientists to use natural language to construct complex, bespoke scripts for 
gravitational-lens analysis. With agentic coding tools such as Claude Code or Codex, users describe the desired 
analysis and the agent collates the data, writes and executes Python scripts and brings together the results. The scientist 
can then use natural language to visualize, investigate and interpret the results. Alternatively, through web-based c
onversational AI assistants such as ChatGPT, users can ask PyAutoLens-Assistant questions and obtain fully documented 
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

The example above is a natural-language workflow: the scientist specifies the analysis in scientific terms, and the 
assistant translates it into executable code. Complex modelling concepts can therefore be expressed clearly even 
when implementing them manually would require substantial effort. By handling the Python syntax and PyAutoLens API, 
the assistant allows scientists to focus on what the analysis should do and why, rather than facing the implementation burden of 
how to implement it in code. PyAutoLens-Assistant includes several benchmarks that illustrate this further. One uses a 
three-paragraph prompt to reproduce the well-known detection of a dark matter subhalo in the strong lens SDSS J0946+1006; 
another simulates CCD imaging and interferometric observations of a group-scale strong lens and then models both datasets jointly.

Through Teacher Mode, PyAutoLens-Assistant supports scientists new to gravitational lensing by explaining concepts in 
context and directing them to relevant documentation, tutorials, and open-source lectures. It guides undergraduates and 
early-stage PhD students through the foundations of scientific data analysis and Bayesian inference, while helping 
experienced lensing researchers new to PyAutoLens navigate its API, syntax, and workflows. This support is increasingly 
valuable as datasets grow larger and more diverse, spanning multiple observing techniques, galaxy-, group-, and 
cluster-scale systems, and both strong and weak lensing. By reducing the need to engage directly with software syntax, 
PyAutoLens-Assistant allows users to learn by performing real analyses and focusing fully on the core scientific concepts
they need to learn.

# How It Works

PyAutoLens-Assistant leverages the general knowledge and reasoning capabilities of the underlying foundation model, 
available whenever a user starts a new conversation with a coding agent or web-based assistant. However, it adds
two layers on top of this, both of which comprise a library of markdown files structured and formatted in a way
that can be easily and quickly read by an AI assistant or agent, providing them with the full context of PyAutoLens
before the user inputs a prompt.

The first are the wiki pages, which provide the underlying 

skills, autolens worksapce.


PyAutoLens-Assistant can be used through a browser-based conversational assistant or a local agentic coding tool. 
For systems such as ChatGPT or Claude, `llms.txt` acts as the machine-readable entry point: it asks the assistant to 
verify repository access and directs it through the canonical read order of instructions, skills, relevant wiki pages, and 
runnable workspace examples. In this mode, users can ask questions, receive scientific explanations, locate examples, 
interpret errors and figures, and generate draft end-to-end scripts, although the assistant cannot normally inspect local files or execute code.

The harness.

# State of the field

<!--
Position PyAutoLens-Assistant relative to: (i) the published PyAutoLens software
[@Nightingale2021] and its documentation/workspace; (ii) general-purpose coding
assistants used without domain grounding; and (iii) any other domain-specific
scientific AI assistants or LLM-agent frameworks in astronomy. Focus on the
combination of curated version-controlled domain knowledge, grounding against a
tested example corpus and the installed API, and inspectable, reproducible
outputs. Verify every comparison before submission.
-->



## Reference wikis

Two reference wikis provide complementary context. The core wiki organizes the PyAutoLens API, modelling concepts, datasets, 
inference methods, and operational guidance, linking these to procedural skills and relevant workspace examples. The 
literature wiki provides scientific context through pages on lensing concepts, named surveys and systems, and bibliographies of published papers. Users can also ingest papers relevant to a project, after which they become part of the assistant's persistent scientific context.



## Interaction modes and project structure

The assistant operates in two interaction modes. **Assistant mode** is intended for users who want a task completed 
efficiently, with concise explanations and support ranging from interactive coding to phased end-to-end analysis. 
**Teacher mode** prioritizes learning by explaining what each stage does and why, making assumptions explicit, and 
directing users to relevant documentation and examples. Both modes use the same scientific capabilities, reproducibility requirements, and safety checks.

For agentic work, each analysis can be stored in a separate project repository containing its data, configuration, 
scripts, results, and project journal. This separates the shared assistant knowledge base from the scientific project while preserving a complete record that can be shared with collaborators or released alongside a publication.

# Research impact statement

<!--
Give specific evidence of research enabled by PyAutoLens-Assistant: projects that
used it, external adoption, teaching use, and shareable science-project repos
released alongside publications. Keep this about software impact rather than new
scientific results.
-->

# AI usage disclosure

Generative AI tools were used to scaffold this manuscript and may be used to assist drafting. All scientific claims, citations, and prose are reviewed and verified by the authors.

# Acknowledgements

<!-- List funding, facilities, software contributors, and other support. -->

# References
