---
title: "PyAutoLens-Assistant: Using Natural Language and AI to Analyse Gravitational Lenses"
tags:
  - Python
  - astronomy
  - gravitational lensing
  - artificial intelligence
  - large language models
  - natural language interfaces
authors:
  - name: James W. Nightingale
    orcid: 0000-0002-8987-7401
    affiliation: 1
    corresponding: true
affiliations:
  - name: Institute for Computational Cosmology, Durham University, United Kingdom
    index: 1
date: 15 July 2026
bibliography: paper.bib
---

# Summary

Stage IV weak-lensing surveys, such as Euclid [@EuclidCollaboration2025] and the Vera C. Rubin Observatory [@LSSTDarkEnergyScienceCollaboration2012], are measuring increasingly large samples of galaxies, while strong-lensing searches are discovering rapidly growing numbers of galaxy-, group-, and cluster-scale lenses. These systems are observed through optical and infrared imaging, radio interferometry, point-source measurements of lensed quasars and supernovae, and weak-lensing shear catalogues, enabling studies of cosmology, dark matter, galaxy formation, and the early Universe. Mature open-source software such as PyAutoLens [@Nightingale2021] supports simulations, lensing calculations, and strong- and weak-lensing modelling across these datasets, but constructing a bespoke analysis can still require substantial effort to locate, adapt, and combine the relevant examples using the correct Python API and syntax.

PyAutoLens-Assistant allows scientists to use natural language to describe the gravitational-lens analysis they want to perform. It provides a domain-specific interface to the documented and tested capabilities of PyAutoLens, supporting simulations, ray-tracing calculations, probabilistic modelling, data preparation, result interpretation, and visualization. Researchers can use it through a conversational AI assistant, such as ChatGPT, to ask questions and develop workflows interactively, or through agentic coding tools, such as Claude Code or Codex, which can inspect data, write and execute scripts, diagnose errors, analyse outputs, and iteratively refine an analysis. PyAutoLens-Assistant is grounded in curated, version-controlled documentation, examples, scientific reference material, and task-specific instructions, and produces explicit Python code and inspectable analysis products.

# Statement of need

Experienced PyAutoLens users often know exactly which scientific analysis they want to perform, but implementing it still requires substantial time assembling the appropriate Python workflow. An expert can quickly specify: "Perform multi-wavelength lens modelling of the F115W, F150W, F277W, and F444W JWST imaging of the COSMOS-Web Ring [@Casey2023] using a multi-Gaussian expansion lens-light model, a singular isothermal ellipsoid plus external shear mass model, and a Delaunay pixelized source reconstruction." Translating this concise scientific specification into executable code requires locating and combining several examples, loading and configuring each dataset, composing the model components with the correct API, and adapting the workflow to the system being analysed. As models incorporate more datasets, cluster-scale mass distributions, or joint strong- and weak-lensing constraints, this implementation burden increases even when the underlying scientific choices are already clear. PyAutoLens-Assistant reduces this overhead by translating natural-language specifications into explicit, executable, and reproducible PyAutoLens workflows.

New users face a complementary challenge: they may not yet know which modelling approach, software abstractions, or examples are appropriate for the task they are learning. PyAutoLens has grown from galaxy-scale imaging analyses to support point-source lenses, group- and cluster-scale systems, weak lensing, interferometry, simulations, and joint analyses, accompanied by well over one hundred worked examples across the `autolens_workspace`. Navigating this material while simultaneously learning gravitational-lensing science, Bayesian inference, and the PyAutoLens API can be overwhelming. PyAutoLens-Assistant enables users to describe their immediate goal in natural language and receive targeted explanations, example code, and pointers to the relevant documentation. Its teaching mode also explains the underlying science and numerical methods, encourages follow-up questions, and supports learning rather than simply returning code.

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

# Software design

PyAutoLens-Assistant is a version-controlled knowledge and workflow layer that enables general-purpose AI systems to use PyAutoLens reliably. Its architecture separates three components: instructions define assistant behaviour, skills describe how to perform specific tasks, and wiki pages provide the underlying technical and scientific knowledge. For a given request, the assistant selects the relevant skill, consults the associated wiki material, and adapts tested examples from the `autolens_workspace` rather than generating PyAutoLens code from memory. Generated scripts follow the established workspace structure and can be checked against the installed API, reducing the risk of outdated or invented syntax.

## Reference wikis

Two reference wikis provide complementary context. The core wiki organizes the PyAutoLens API, modelling concepts, datasets, inference methods, and operational guidance, linking these to procedural skills and relevant workspace examples. The literature wiki provides scientific context through pages on lensing concepts, named surveys and systems, and bibliographies of published papers. Users can also ingest papers relevant to a project, after which they become part of the assistant's persistent scientific context.

## Access modes

PyAutoLens-Assistant can be used through a browser-based conversational assistant or a local agentic coding tool. For systems such as ChatGPT or Claude, `llms.txt` acts as the machine-readable entry point: it asks the assistant to verify repository access and directs it through the canonical read order of instructions, skills, relevant wiki pages, and runnable workspace examples. In this mode, users can ask questions, receive scientific explanations, locate examples, interpret errors and figures, and generate draft end-to-end scripts, although the assistant cannot normally inspect local files or execute code.

For full computational workflows, PyAutoLens-Assistant can instead be used with agentic tools such as Claude Code or Codex. These tools load the repository instructions directly and can inspect datasets, write and run scripts, generate diagnostic plots, debug failures, and iteratively refine an analysis. The resulting Python code, configuration, outputs, and modelling decisions remain explicit and inspectable.

## Interaction modes and project structure

The assistant operates in two interaction modes. **Assistant mode** is intended for users who want a task completed efficiently, with concise explanations and support ranging from interactive coding to phased end-to-end analysis. **Teacher mode** prioritizes learning by explaining what each stage does and why, making assumptions explicit, and directing users to relevant documentation and examples. Both modes use the same scientific capabilities, reproducibility requirements, and safety checks.

For agentic work, each analysis can be stored in a separate project repository containing its data, configuration, scripts, results, and project journal. This separates the shared assistant knowledge base from the scientific project while preserving a complete record that can be shared with collaborators or released alongside a publication.

# Benchmark examples

PyAutoLens-Assistant is evaluated using a suite of frozen benchmark prompts distributed with the repository. We describe three representative examples here, which span progressively more demanding scientific workflows and are run using multiple conversational and agentic AI systems. Each benchmark records the full interaction, generated code, executed analysis where applicable, scientific outputs, and a rubric-based score, enabling direct comparison between different models, tools, and interaction modes.

The first benchmark uses **Teacher mode** to simulate Euclid-like imaging of a simple strong lens, fit the simulated data, and recover the lens model. The assistant must explain the purpose of each stage, including model composition, simulation, masking, non-linear inference, and interpretation of the recovered parameters. This benchmark tests whether the assistant can provide scientifically accurate guidance while helping a new user understand an end-to-end PyAutoLens workflow.

The second benchmark uses **Assistant mode** to model JWST imaging of the COSMOS-Web Ring [@Casey2023]. The assistant must inspect the supplied dataset, perform the required data-preparation steps, construct an appropriate lens-light and mass model with a pixelized source reconstruction, run the analysis, and present the reconstructed source and fit residuals. This benchmark tests the assistant's ability to convert a concise scientific request into a complete and reproducible modelling workflow with limited user intervention.

The third benchmark requests a more autonomous analysis of the strong lens SDSSJ0946+1006. The assistant must reproduce a reported dark-matter subhalo detection [@Vegetti2010] through Bayesian model comparison, compare alternative subhalo mass profiles to test the reported high concentration of the perturber [@Minor2021], preserve all intermediate models and results for inspection, and determine whether the analysis should run locally or on high-performance computing resources. This benchmark tests long-horizon planning, scientific decision-making, project-state management, and the ability to execute a complex analysis across multiple stages.

The benchmark suite is run across different AI systems and access modes, including browser-based conversational assistants and local agentic coding tools. Results will be reported using metrics such as task completion, scientific correctness, API validity, reproducibility, degree of autonomy, number of user interventions, wall-clock time, and computational cost. Together, the benchmarks test the two principal use cases of PyAutoLens-Assistant: teaching new users how to perform gravitational-lens analyses and enabling experienced users to execute complex workflows efficiently from natural-language specifications.

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
