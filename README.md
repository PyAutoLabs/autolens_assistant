# autolens_base_project

<p align="center">
  <img src="https://github.com/Jammy2211/PyAutoLogo/blob/main/gifs/pyautolens.gif?raw=true" alt="PyAutoLens demo" width="600">
</p>

A forkable template for **PyAutoLens** strong-lensing science projects, bundled
with an AI-agent workspace so you can do real lens modelling by conversation,
without needing to know the PyAutoLens codebase up front. Describe your data
or modelling goal, and the agent turns that into a runnable Python workflow
for your project.

This repo is opinionated in a useful way: it already knows the PyAuto\* stack,
the SLaM pipeline, the project conventions, and how to keep a per-project
journal in [`wiki/project/`](./wiki/project/). Claude Code reads
[`CLAUDE.md`](./CLAUDE.md); Codex, Copilot, and other agents read
[`AGENTS.md`](./AGENTS.md).

## Quickstart

1. Install an agent client.

```bash
# Claude Code
npm install -g @anthropic-ai/claude-code

# or Codex
npm install -g @openai/codex
```

2. Clone your fork of the template.

```bash
git clone https://github.com/<you>/autolens_base_project.git
cd autolens_base_project
```

3. Start the agent.

```bash
claude        # or `codex`
```

4. Ask for the first thing you need.

- *"Set up the Python environment."*
- *"What skills do you have?"*
- *"I have HST imaging of <lens name> - walk me through fitting it."*
- *"I'm new to lensing - can you teach me what a caustic is?"*

The agent will read the workspace instructions, pick the right skill, and
produce Python in [`work/`](./work/) rather than giving you vague API advice.
After non-trivial work it also offers to add a dated project note so later
sessions keep their context.

Quickstart docs for Claude Code: <https://docs.claude.com/claude-code/quickstart>.

## What you get

- **18 lensing skills** for data prep, model building, fitting, debugging,
  results, and visualisation — see [`skills/README.md`](./skills/README.md).
- **Grounded code generation** from pinned PyAuto\* source citations in
  [`sources.yaml`](./sources.yaml), not generic text-only advice.
- **A project memory** in [`wiki/project/`](./wiki/project/) plus curated
  reference material in [`wiki/core/`](./wiki/core/) and
  [`wiki/literature/`](./wiki/literature/).
- **Local and HPC workflows** that share the same scripts and conventions.

## Learn more below

The rest of this README covers the science background, what PyAutoLens can do,
who this workspace is for, the repo structure, and the HPC / SLaM workflow in
more detail.

---

## What is gravitational lensing?

**Gravitational lensing** is the bending of light by mass. When a distant
galaxy (the *source*) sits behind a foreground galaxy or cluster (the *lens*),
the lens's gravity warps the source's light into arcs, multiple images, or
Einstein rings. The geometry of those distortions is a precise readout of the
lens's total mass distribution — including the dark matter that dominates it —
and of the cosmological distances between observer, lens, and source.
Modelling that geometry is how we map dark matter on galaxy and cluster
scales, hunt for dark subhaloes, study the high-redshift universe through
magnified sources, and measure the Hubble constant from quasar time delays.

## What PyAutoLens can do

PyAutoLens turns a strong-lens image (or a set of interferometric visibilities)
into a probabilistic model of the lens and source. The agent uses every piece
of this; the bullets below are what it has access to whenever you ask it to
fit something.

### Modelling

- **Light profiles** for the lens and source: Sersic, exponential, de
  Vaucouleurs, cored Sersic, Multi-Gaussian Expansion, shapelets, and
  arbitrary custom profiles.
- **Mass profiles** for the lens: singular isothermal ellipsoid, NFW (with
  and without scale-radius freedom), broken / cored power laws, external
  shear, and higher-order multipole perturbations.
- **Multi-plane ray tracing** through any number of lens planes — single
  galaxies, group-scale, and cluster-scale systems.
- **Pixelised source reconstruction** via Delaunay, Voronoi, or rectangular
  meshes with constant or adaptive regularisation — the right tool for
  extended arcs.
- **Imaging and interferometer likelihoods**, including direct visibility-plane
  fits for ALMA / JVLA data.
- **Subhalo detection** by sensitivity-mapped grid search across the image plane.
- **Forward simulators** for synthesising imaging or visibility datasets from
  ground-truth `Tracer`s (pipeline validation, training sets, sensitivity
  studies).

### Non-linear optimisation

PyAutoLens leans on [PyAutoFit](https://github.com/rhayes777/PyAutoFit) for
the inference machinery, which is what makes hard lens modelling tractable:

- **Multiple sampler back-ends** — Nautilus (nested sampling, the default for
  most lens problems), Dynesty, Emcee, Zeus, plus L-BFGS / scipy for fast
  point estimates — all driven through the same `search.fit(...)` interface.
- **Search chaining**: the posterior of an early search seeds the priors of
  the next, so you can decompose a hard problem (lens light, then mass, then
  source) into a sequence of tractable ones.
- **SLaM pipelines** (Source-Light-Mass) — an automated, model-comparison-driven
  chain from initial parametric fit through pixelised source reconstruction
  and optional subhalo detection. The [`/init-slam`](./skills/init-slam.md)
  skill copies a SLaM driver into [`scripts/`](./scripts/) tailored to your
  data type.
- **Database aggregator** — once you've run a sample of fits, query results
  across the sample with PyAutoFit's `Aggregator` API; ideal for surveys.
- **JAX acceleration** on GPU for the likelihood (`autolens[jax]` extra) —
  100× speedups for pixelised inversion.
- **Hierarchical (graphical) models** — share parameters across many lenses
  to fit population-level distributions.

For the agent: the skills in [`skills/`](./skills/) cover every step of this
flow, from data preparation through model building, sampler configuration,
search chaining, and result inspection.

## Who this is for

Pick the row that fits — the agent calibrates depth from cues in your first
message and from a light-touch profile that builds up over sessions. The full
routing matrix is in [`skills/_style.md`](./skills/_style.md) "Adaptive depth".

**If you're new to strong lensing.** The agent shifts into teacher mode. It
leads with the relevant [HowToLens](https://github.com/PyAutoLabs/HowToLens)
notebook *before* the code, frames physics → statistics → code one concept at
a time, and checks in after each beat (*"does that land, or want me to unpack
deflection angles further?"*). You leave the session understanding why, not
just how. See [`skills/_style.md`](./skills/_style.md) "Newcomer mode".

**If you know lensing but not PyAutoLens.** The agent skips the physics
lecture and maps science questions straight to API. It leads with the
[`autolens_workspace`](https://github.com/Jammy2211/autolens_workspace)
production scripts and the
[RTD overview](https://pyautolens.readthedocs.io/en/latest/overview/overview_2_new_user_guide.html),
then produces a script for your data.

**If you've used PyAutoLens before.** Quick recall — *"load `output/.../abc/`,
plot residuals, tell me if anything looks structured"*. The wiki has the API,
the skills are the command-line ergonomics, and the agent stays out of your
way.

**Contribute back to the template.** If you're a collaborator on
[`PyAutoLabs/autolens_base_project`](https://github.com/PyAutoLabs/autolens_base_project),
keep that repository as `origin`, branch from `main`, and open PRs directly
from that clone:

```bash
git remote -v
git checkout main
git pull --ff-only origin main
git checkout -b docs/<topic>
```

From an agent session you can then say:

- *"Prepare this as a PR on PyAutoLabs/autolens_base_project."*

If you do **not** have push access to the upstream repo, keep a two-remote
layout instead:

```bash
git remote rename origin fork
git remote add origin https://github.com/PyAutoLabs/autolens_base_project.git
git fetch origin
```

In that mode, `fork` is your writable remote and `origin` is the upstream
template you want to target with PRs. The `contribute-upstream` skill supports
both layouts and chooses the correct push target from the detected remotes.

---

## What you get

- **17 lensing skills** for data prep, model building, fitting, debugging,
  results, and visualisation — see [`skills/README.md`](./skills/README.md) for
  the index. Each skill is a procedural how-to with the Python recipe inline;
  the output is a runnable `.py` you keep and modify.
- **Knows how to code.** The agent reads PyAuto\* source through pinned
  citations (`<Project>:<path>`, resolved via
  [`sources.yaml`](./sources.yaml)) and produces idiomatic, working code —
  not API-hallucinated text. The python-first rule is in
  [`skills/_style.md`](./skills/_style.md).
- **Grounded in science.** Every claim points at source code or a paper.
  [`wiki/core/`](./wiki/core/) is the curated PyAuto\* reference (refreshed
  against pinned source commits); [`wiki/literature/`](./wiki/literature/) is
  the strong-lensing scientific reference (concepts, entities, papers, with
  `[[wiki-link]]` cross-refs). Add a paper with
  [`al_ingest_paper`](./skills/al_ingest_paper.md).
- **Tracks what you've done.** A per-fork journal at
  [`wiki/project/`](./wiki/project/) — dated entries cover domain motivation,
  statistical motivation, and the script produced. The agent offers
  (default-yes) to add an entry after every non-trivial piece of work. A
  light-touch [`profile.md`](./wiki/project/_profile_template.md) records your
  level, instrument, and science goal so future sessions don't make you repeat
  yourself.
- **Plots that don't disappear.** Plot-producing skills save through
  `aplt.Output(...)` into `work/plots/<context>/`. The agent quotes the
  absolute path and offers *"want me to `open <path>`?"* — see
  [`CLAUDE.md`](./CLAUDE.md) Part 1 "Conventions".
- **HPC-ready out of the box.** SLURM submit scripts for GPU and CPU,
  bidirectional [`hpc/sync`](./hpc/) for code ↔ HPC, and the same Python
  scripts run locally or on the cluster unchanged.

---

## Quick start with an agent

You'll need an agent client. Claude Code is the smoothest fit (this repo's
[`CLAUDE.md`](./CLAUDE.md) is the canonical instruction set); Codex, Copilot,
and other agents read the mirror at [`AGENTS.md`](./AGENTS.md).

**1. Install the agent.**

```bash
# Claude Code
npm install -g @anthropic-ai/claude-code

# or Codex
npm install -g @openai/codex
```

**2. Clone the project.**

If you're working from a personal fork:

```bash
git clone https://github.com/<you>/autolens_base_project.git
cd autolens_base_project
```

If you're a collaborator working directly against `PyAutoLabs`:

```bash
git clone https://github.com/PyAutoLabs/autolens_base_project.git
cd autolens_base_project
```

…or from an existing agent session, invoke the
[`start-new-project`](./skills/start-new-project.md) skill to rsync into a
fresh directory with a clean project journal.

**3. Open a session.**

```bash
claude        # or `codex`
```

The agent reads [`CLAUDE.md`](./CLAUDE.md) (or [`AGENTS.md`](./AGENTS.md)) on
session start and already knows the project conventions.

**4. Ask.** Prompts that work cold, on a fresh clone:

- *"What skills do you have?"* — lists the 17 lensing skills + the project
  workflow skills.
- *"Set up the Python environment."* — agent runs
  [`al_setup_environment`](./skills/al_setup_environment.md) (pip mode for
  read-only use, or editable-clone of all five source repos for
  source-level access).
- *"I have HST imaging of <lens name> — walk me through fitting it."* —
  agent composes data prep → model build → search → results, narrating
  physics and statistics as it goes.
- *"I'm new to lensing — can you teach me what a caustic is?"* — agent
  enters newcomer mode: leads with the HowToLens notebook, one concept at
  a time.

**5. Let the journal build.** After non-trivial work the agent offers
(default-yes) to add a `wiki/project/YYYY-MM-DD-<slug>.md` entry. Say yes —
that's how future sessions stay in context across days and weeks.

---

## The three-layer architecture

1. **Instructions.** [`CLAUDE.md`](./CLAUDE.md) (Claude Code) and
   [`AGENTS.md`](./AGENTS.md) (Codex, Copilot, generic). `CLAUDE.md` splits
   into Part 1 (how the agent operates) and Part 2 (the science-project
   conventions repeated below).
2. **Skills.** [`skills/`](./skills/), mirrored at
   [`.claude/skills/`](./.claude/skills/) for Claude Code. Lensing-API
   skills are named `al_*.md` (`al_build_imaging_model`, `al_run_search`,
   `al_plot_fit_residuals`, …); project-workflow skills have plain
   kebab-case names (`init-slam`, `start-new-project`). The writing guide
   every skill is authored against is [`skills/_style.md`](./skills/_style.md).
3. **Wiki**, split into three sub-wikis:
   - [`wiki/core/`](./wiki/core/) — curated PyAuto\* reference. Refreshed
     by [`al_update_wiki`](./skills/al_update_wiki.md) against pinned source
     commits in [`sources.yaml`](./sources.yaml).
   - [`wiki/literature/`](./wiki/literature/) — strong-lensing scientific
     reference. Schema in
     [`wiki/literature/CLAUDE.md`](./wiki/literature/CLAUDE.md); add papers
     via [`al_ingest_paper`](./skills/al_ingest_paper.md).
   - [`wiki/project/`](./wiki/project/) — per-fork journal of decisions,
     experiments, and `profile.md` (the user record). Reset on fork by the
     `start-new-project` rsync.

### Asking the agent for something new

If a capability you want isn't already a skill, just describe it. The agent
follows the bootstrap protocol in
[`skills/_bootstrap_skill.md`](./skills/_bootstrap_skill.md): confirm scope
with you, clone any source repos it needs (URLs from
[`sources.yaml`](./sources.yaml)), read the relevant API inside the cloned
source, draft a new skill in the workspace style, and link it into the wiki.

`sources.yaml` is the single source of truth for which source repos this
workspace knows about, recorded by **git URL** rather than local path so the
fork is portable across machines. Everything else cites those repos by
*project name + path relative to the repo root*
(`PyAutoFit:autofit/non_linear/search/nest/nautilus.py`).

---

## Project structure

```
autolens_base_project/
├── config/           # PyAutoLens configuration (priors, non-linear samplers, visualisation)
├── dataset/          # Imaging and interferometer data (see Dataset Layout below)
├── hpc/              # HPC batch submission scripts
│   ├── batch_cpu/    # CPU job scripts + SLURM output/error logs
│   └── batch_gpu/    # GPU job scripts + SLURM output/error logs
├── output/           # Analysis results (written automatically by PyAutoFit)
├── scripts/          # Persistent modeling pipelines — populated by `/init-slam`
│   ├── template.py   # HPC interface template that the populated scripts copy from
│   ├── imaging.py    # SLaM pipeline for imaging data (created by `/init-slam`)
│   └── interferometer.py  # SLaM pipeline for interferometer data (created by `/init-slam`)
├── skills/           # Agent skills (procedural)
├── .claude/skills/   # Symlinks for Claude Code
├── work/             # Agent working directory — see note below
└── wiki/
    ├── core/         # Curated PyAuto* reference
    ├── literature/   # Strong-lensing scientific reference (papers, concepts)
    └── project/      # Running journal for this fork
```

A fresh clone ships only the parts that don't depend on your data: `config/`,
`hpc/`, `skills/`, `wiki/`, and `scripts/template.py`. The typed
`scripts/imaging.py` / `interferometer.py` are populated by the
[`start-new-project`](./skills/start-new-project.md) and
[`init-slam`](./skills/init-slam.md) skills; `dataset/` and `output/` arrive
when you run them.

`work/` holds the Python scripts and Markdown notes the agent generates
during sessions — these are **committed** alongside the matching
`wiki/project/` entry that describes them. Plot files saved by the skills
land in `work/plots/<context>/` and data dumps (FITS / npy / pickle) in
`work/output/` — both subdirectories are gitignored, since they're
reproducible from the code that produced them.

---

## Dataset Layout

Datasets live inside `dataset/` and are organised into **samples**. A sample is a named
subdirectory that groups related datasets (e.g. all lenses from a survey). Each dataset
is then a subdirectory inside its sample.

```
dataset/
└── <sample>/
    ├── <dataset_1>/
    │   ├── data.fits
    │   ├── noise_map.fits
    │   ├── psf.fits          # imaging only
    │   ├── uv_wavelengths.fits  # interferometer only
    │   ├── positions.json
    │   └── info.json
    └── <dataset_2>/
        └── ...
```

The included example datasets use separate sample folders per data type:

```
dataset/
├── sample_imaging/
│   └── example_imaging/
│       ├── data.fits
│       ├── noise_map.fits
│       ├── psf.fits
│       ├── positions.json
│       └── info.json
└── sample_interferometer/
    └── example_interferometer/
        ├── data.fits
        ├── noise_map.fits
        ├── uv_wavelengths.fits
        ├── positions.json
        └── info.json
```

### info.json

Every dataset directory must contain an `info.json` file. This is the single source of
truth for dataset-specific properties used by analysis scripts. It removes any need to
hard-code or pass these values as arguments.

Required fields:

```json
{
    "pixel_scale": 0.05,
    "n_batch": 40
}
```

| Field         | Type  | Description                                                                 |
|---------------|-------|-----------------------------------------------------------------------------|
| `pixel_scale` | float | Arcseconds per pixel. Varies by instrument (e.g. HST ≈ 0.05, Euclid ≈ 0.1) |
| `n_batch`     | int   | Pixelization batch size. Use lower values for higher-resolution data to reduce VRAM usage (e.g. 40 for HST, 8 for AO) |

Optional fields (used by the SLaM pipeline if present):

```json
{
    "pixel_scale": 0.05,
    "n_batch": 40,
    "redshift_lens": 0.5,
    "redshift_source": 1.0
}
```

For interferometer datasets, two additional optional fields are supported:

```json
{
    "pixel_scale": 0.1,
    "n_batch": 25,
    "real_space_shape": [256, 256],
    "mask_radius": 3.5
}
```

| Field              | Type       | Description                                                                    |
|--------------------|------------|--------------------------------------------------------------------------------|
| `real_space_shape` | [int, int] | Height × width of the real-space reconstruction grid (default `[256, 256]`)    |
| `mask_radius`      | float      | Circular mask radius in arcseconds (default `3.5`)                             |

When generating a simulated dataset with
[`al_simulate_dataset`](./skills/al_simulate_dataset.md), `info.json` is written
automatically alongside the data.

For real observational data, create `info.json` manually or with a preprocessing script.
Before modelling begins, explicitly check preprocessing choices like the mask radius
and whether you need a separate exclusion mask for nearby objects, artifacts, or other
regions that should not contribute to the fit.

---

## Running Scripts

> **Prerequisite:** `scripts/imaging.py` and `scripts/interferometer.py` are
> populated by the [`/init-slam`](./skills/init-slam.md) skill — run it once
> per fork before any of the commands below.

### Locally

Run from anywhere — paths are resolved relative to the script's location:

```bash
python3 scripts/imaging.py --sample=<sample> --dataset=<dataset>
python3 scripts/interferometer.py --sample=<sample> --dataset=<dataset>
```

Against the bundled example datasets (once `/init-slam` has populated the
scripts):

```bash
python3 scripts/imaging.py --sample=sample_imaging --dataset=example_imaging
python3 scripts/interferometer.py --sample=sample_interferometer --dataset=example_interferometer
```

Both `--sample` and `--dataset` are optional. Output paths are organised as
`output/<sample>/<dataset>/<pipeline_stage>/`.

### On the HPC

The batch scripts in `hpc/batch_gpu/` and `hpc/batch_cpu/` handle all
HPC-specific concerns (SLURM directives, environment activation, paths).
The Python script itself requires no modification between local and HPC runs.

All batch scripts use a `$PROJECT_PATH` environment variable so no paths are
hard-coded in the scripts. Set it once before submitting:

```bash
export PROJECT_PATH=/path/to/your/project
```

Each dataset type has its own set of batch scripts. Imaging scripts call
`scripts/imaging.py`; interferometer scripts call `scripts/interferometer.py`.

**GPU (recommended):**

| Script | Purpose |
|--------|---------|
| `hpc/batch_gpu/submit_imaging` | Array job for imaging datasets |
| `hpc/batch_gpu/submit_interferometer` | Array job for interferometer datasets |

1. Edit the appropriate submit script:
   - Update `--mail-user` for your email
   - Set `sample=` to the sample subdirectory name
   - Populate the `datasets` array with the dataset names to run
   - Update `--array=0-N` to match the number of datasets
   - Adjust `--mem` and `--time` as needed

2. Submit from the `hpc/batch_gpu/` directory:

```bash
cd hpc/batch_gpu
export PROJECT_PATH=/path/to/your/project
sbatch submit_imaging          # imaging
sbatch submit_interferometer   # interferometer
```

**CPU:**

| Script | Purpose |
|--------|---------|
| `hpc/batch_cpu/submit_imaging` | CPU array job for imaging datasets |
| `hpc/batch_cpu/submit_interferometer` | CPU array job for interferometer datasets |

To run a single dataset, set `--array=0-0` in the submit script and put that
one entry in the `datasets=()` array.

```bash
cd hpc/batch_cpu
export PROJECT_PATH=/path/to/your/project
sbatch submit_imaging          # imaging
sbatch submit_interferometer   # interferometer
```

The generic `hpc/batch_gpu/submit`, `hpc/batch_cpu/submit`, and
`hpc/batch_cpu/template` files are kept as compatibility/reference examples
for custom cluster setups. For normal use, prefer the typed
`submit_imaging` / `submit_interferometer` scripts.

SLURM logs are written to the `output/` and `error/` subdirectories inside each batch folder.

---

## Syncing with the HPC

`hpc/sync` is a single script that handles all data movement between your local
machine and the HPC. It wraps `rsync` with sensible defaults and transfers only
what has actually changed.

### First-time setup

```bash
cp hpc/sync.conf.example hpc/sync.conf
# Edit hpc/sync.conf — set HPC_HOST, HPC_BASE, and PROJECT_NAME
```

`sync.conf` is gitignored and stays on your local machine only.
`hpc/sync_jump.conf.example` is also kept as a reference for relay / jump-host
topologies that need a second local config.

### Commands

```bash
hpc/sync push     # Upload code, config, and data to the HPC
hpc/sync pull     # Download results from the HPC
hpc/sync sync     # Push then pull (default)
hpc/sync status   # Dry run — see what would transfer without moving anything
```

### What gets transferred

| Direction | Folders | Strategy |
|-----------|---------|----------|
| push | `config/` `hpc/` `scripts/` | Normal sync — only changed files |
| push | `dataset/` | `--ignore-existing` — skips files already on HPC, avoiding re-checksumming large FITS archives |
| pull | `output/` | `--update --exclude=search_internal` — only downloads files newer than local copies, omits large sampler internals |

The `--ignore-existing` flag on dataset is the key optimisation for large projects:
once a FITS file is on the HPC, it is never re-examined on subsequent syncs.

### Connection to HPC batch scripts

`$HPC_BASE/$PROJECT_NAME` in `sync.conf` is the same path as `$PROJECT_PATH`
used inside the SLURM batch scripts, so activation paths and script calls stay
consistent across local, push, and job submission steps.

---

## Configuration

`config/` contains all PyAutoLens configuration files. The HPC jobs use the same
`config/` as local runs — there is no separate HPC config.

Key config files:

| File | Purpose |
|------|---------|
| `config/general.yaml` | Global settings |
| `config/non_linear/nest.yaml` | Nested sampling settings (Nautilus / MultiNest) |
| `config/priors/` | Prior distributions for all model components |
| `config/visualize/` | Matplotlib output settings |

---

## SLaM Pipeline

To set up a fresh `scripts/` folder against a SLaM pipeline, invoke the
[`init-slam`](./skills/init-slam.md) skill. It picks the right driver from
`autolens_workspace` (parametric or pixelised source, MGE lens light, subhalo
detection, group scale, …), copies it into `scripts/`, and writes a
`scripts/slam_claude.md` reference so future sessions inherit the SLaM
context without re-reading the workspace guides.

---

## Simulating Data

Simulation remains a first-class workflow, but the base template no longer
ships a local `simulators/` tree. Instead:

- **From an agent session**, ask for it: the agent runs
  [`al_simulate_dataset`](./skills/al_simulate_dataset.md), which synthesises
  a `Tracer` to your spec (lens redshift, mass model, source) and writes the
  FITS files plus `info.json`.
- **From workspace examples**, copy the relevant script from
  `autolens_workspace` into your project if you want a persistent simulator
  alongside your modeling pipeline.

---

## License

This template ships agent instructions and reference material derived from the public
PyAuto\* repositories. The underlying libraries are released under their own licenses
(see each repo).
