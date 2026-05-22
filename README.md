# autolens_base_project

The forkable template for PyAutoLens gravitational-lens science projects, bundled with
an AI-agent workspace (the **lenskills** instructions/skills/wiki stack) so a coding
agent can help you build models, run searches, and interpret results without
re-discovering the API every session.

Fork this repo to start a new science project, or rsync into a fresh directory (see
[`CLAUDE.md`](./CLAUDE.md) → "Creating a New Project"). The agent stack rides along
with every fork — so a Claude Code or Codex session in your fork already understands
the PyAuto\* libraries and the project conventions.

---

## Three layers (the agent workspace)

1. **Instructions** — [`CLAUDE.md`](./CLAUDE.md) (Claude Code) and
   [`AGENTS.md`](./AGENTS.md) (Codex, Copilot, generic). Explain how an agent finds
   skills, introspects them, and bootstraps new ones on demand. `CLAUDE.md` is split:
   Part 1 is how the agent operates, Part 2 is the science-project conventions below.
2. **Skills** — [`skills/`](./skills/) (also exposed at
   [`.claude/skills/`](./.claude/skills/) for Claude Code). Each skill is a procedural
   how-to for one task — `al_*.md` for lensing-API skills (`al_build_imaging_model`,
   `al_run_search`, `al_plot_fit_residuals`, …) and plain-named skills for repo
   workflows (`init-slam`, `start-new-project`).
3. **Wiki** — [`wiki/`](./wiki/) split into three sub-wikis:
   - [`wiki/core/`](./wiki/core/) — curated PyAuto\* reference (Sersic profiles,
     non-linear searches, SLaM phases, etc.). Maintained by the `al_update_wiki` skill
     against pinned source commits.
   - [`wiki/literature/`](./wiki/literature/) — broad strong-lensing scientific
     reference (concepts, entities, per-paper bibliographies). See
     [`wiki/literature/CLAUDE.md`](./wiki/literature/CLAUDE.md) for the schema.
   - [`wiki/project/`](./wiki/project/) — running journal of what *this fork* has
     done. Dated entries follow [`wiki/project/_template.md`](./wiki/project/_template.md).

### Quick start with an agent

1. Open this repo with your AI agent of choice (Claude Code, `codex`, etc.).
2. Ask **"What skills do you have?"** — the agent will list them from
   [`skills/README.md`](./skills/README.md).
3. To set up the Python environment, ask the agent to **"run `al_setup_environment`"**.
4. Walk through a lensing task by name (build a model, run a search, interpret a fit) or
   describe what you want and let the agent compose skills together.

### Asking the agent for something new

If a capability you want isn't in the skill list, just ask. The agent will follow the
bootstrap protocol in [`skills/_bootstrap_skill.md`](./skills/_bootstrap_skill.md):
confirm scope with you, clone any source repos it needs (resolved via
[`sources.yaml`](./sources.yaml)), read the relevant API, draft a new skill in the
workspace style, and link it into the wiki.

`sources.yaml` is the single source of truth for which source repos this workspace
knows about, by **git URL** rather than local path so the fork is portable across
machines. Everything else references those repos by *project name + path relative to
the repo root* (`PyAutoFit:autofit/non_linear/search/nest/nautilus.py`).

---

## Project Structure

```
autolens_base_project/
├── config/           # PyAutoLens configuration (priors, non-linear samplers, visualisation)
├── dataset/          # Imaging and interferometer data (see Dataset Layout below)
├── hpc/              # HPC batch submission scripts
│   ├── batch_cpu/    # CPU job scripts + SLURM output/error logs
│   └── batch_gpu/    # GPU job scripts + SLURM output/error logs
├── output/           # Analysis results (written automatically by PyAutoFit)
├── scripts/          # Persistent modeling pipelines — run locally or on the HPC unchanged
│   ├── imaging.py    # SLAM pipeline for imaging data
│   ├── interferometer.py  # SLAM pipeline for interferometer data
│   └── group/        # SLAM pipeline for group-scale lensing
├── simulators/       # Scripts for generating simulated datasets
├── slam_pipeline/    # SLAM pipeline stage definitions (dataset-type agnostic)
│
├── skills/           # Agent skills (procedural)
├── .claude/skills/   # Symlinks for Claude Code
└── wiki/
    ├── core/         # Curated PyAuto* reference
    ├── literature/   # Papers / derivations (project-specific)
    └── project/      # Running journal for this fork
```

(`work/` is the agent's gitignored scratch folder for one-off exploration scripts; it
appears once an agent creates it.)

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

Optional fields (used by the SLAM pipeline if present):

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

When generating a simulated dataset with `simulators/base.py`, `info.json` is written
automatically alongside the data.

For real observational data, create `info.json` manually or with a preprocessing script.

---

## Running Scripts

### Locally

Run from anywhere — paths are resolved relative to the script's location:

```bash
python3 scripts/imaging.py --sample=<sample> --dataset=<dataset>
python3 scripts/interferometer.py --sample=<sample> --dataset=<dataset>
```

The included examples:

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
| `hpc/batch_cpu/template_imaging` | Single-dataset imaging job template |
| `hpc/batch_cpu/template_interferometer` | Single-dataset interferometer job template |

```bash
cd hpc/batch_cpu
export PROJECT_PATH=/path/to/your/project
sbatch submit_imaging          # imaging
sbatch submit_interferometer   # interferometer
```

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
| push | `config/` `hpc/` `scripts/` `slam_pipeline/` `simulators/` | Normal sync — only changed files |
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

## SLAM Pipeline

`slam_pipeline/` contains the modular pipeline stages:

| Module | Stage |
|--------|-------|
| `source_lp.py` | Parametric source (light profile) |
| `source_pix.py` | Pixelised source (mesh + regularization) |
| `light_lp.py` | Lens light |
| `mass_total.py` | Total mass |
| `subhalo/detection.py` | Dark matter subhalo detection |

---

## Simulating Data

`simulators/base.py` generates a synthetic imaging dataset. Edit the dataset properties
at the top of the file (`pixel_scale`, `shape_native`, `n_batch`) then run:

```bash
# Single simulated dataset
python3 simulators/base.py

# Named subdirectory
python3 simulators/base.py my_dataset
```

The simulator writes `info.json` automatically, so analysis scripts will pick up the
correct `pixel_scale` and `n_batch` without any further configuration.

---

## License

This template ships agent instructions and reference material derived from the public
PyAuto\* repositories. The underlying libraries are released under their own licenses
(see each repo).
