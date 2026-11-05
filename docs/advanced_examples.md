# Advanced example prompts

Two longer prompts that show how far the PyAutoLens Assistant can be pushed. Paste either into Claude Code,
Codex or another AI coding agent opened inside this repository. Back to the [README](../README.md).

## Detect a dark matter subhalo in SLACS0946+1006

The strong lens SDSSJ0946+1006 is famous for a dark matter subhalo detection that appears unusually concentrated.
This prompt asks the assistant to reproduce that detection and test the "super-concentrated" claim using Bayesian
model comparison.

These lens models can take hours or days to run. The last sentence of the prompt asks the assistant to estimate the
runtime and, if your laptop is not enough, help you set the analysis up on a High Performance Computing (HPC) system
you have access to.

<sub><b>Example Natural Language Prompt for Claude Code, Codex or other AI coding agent</b></sub>

```text
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

## Combine different data types and lensing scales

PyAutoLens can model galaxy-, group- and cluster-scale lenses using CCD imaging, interferometer visibilities,
point-source positions and weak-lensing catalogues, all in JAX so fits run fast on a GPU. These can be combined in a
single joint fit. Doing that by hand means stitching several APIs into one script; with the assistant you describe
the analysis in plain English and it builds the workflow for you.

<sub><b>Example Natural Language Prompt for Claude Code, Codex or other AI coding agent</b></sub>

```text
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
