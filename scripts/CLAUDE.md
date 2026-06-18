# Scripts

This folder holds the lens modeling pipelines for this project. A fresh clone ships
**no** pipeline scripts here — they are generated per project (see below), because a
user can do a broad variety of things and there is no single "default" script. For
quick, throwaway exploration scripts, use `scripts/scratch/` (gitignored) instead.

All scripts here follow the **Generated script style** (title + `__Contents__` header,
`"""__Section__"""` narrative sections, no banner comments) — see the project root
`CLAUDE.md` "Conventions" and `skills/_style.md` "Generated script style".

## HPC interface template — `hpc/template.py`

The standard interface between the HPC batch templates and Python modeling code lives at
[`../hpc/template.py`](../hpc/template.py), paired with `hpc/batch_cpu/template` and
`hpc/batch_gpu/template`. It includes:

- **`parse_fit_args()`** — parses `--sample`, `--dataset`, `--iterations_per_quick_update`,
  `--number_of_cores`, and `--use_cpu` from the command line
- **`fit()`** — receives these parameters and sets up config, dataset loading, and
  `SettingsSearch`. The body raises `NotImplementedError` where the science-specific
  model, analysis, and search steps go
- **`__main__`** — wires `parse_fit_args()` into `fit()`

To create a pipeline for HPC array runs, copy `hpc/template.py` into this folder (e.g.
`scripts/imaging.py`) and fill in the `fit()` body with science code from
`autolens_workspace/scripts/`. The HPC interface (`parse_fit_args`, `__main__`, `use_cpu`,
`number_of_cores`) must be preserved — the batch templates run `scripts/$SCRIPT` and depend
on it.

## Adding Scripts via /init-slam

Use the `/init-slam` skill to select one or more SLaM pipelines from `autolens_workspace` and
copy them here. The skill will:

1. Show you the available SLaM pipeline options, categorized by data type and model variant
2. Copy your chosen script(s) into this folder (preserving the `hpc/template.py` HPC interface
   when the script is destined for batch runs), placing the science code inside the `fit()` body
3. Create `slam_claude.md` — a SLaM reference file that gives future AI sessions full context on
   the SLaM pipeline structure, stage ordering, and design philosophy
4. Add a banner comment at the top of each script pointing to `slam_claude.md`

## Available SLaM Pipelines (Reference)

### Imaging — Standard

| Option | Source path | Description |
|--------|-------------|-------------|
| A | `imaging/features/multi_gaussian_expansion/slam.py` | MGE lens light (2x20 Gaussians) + pixelized source. Standard choice for HST/Euclid imaging. |
| B | `imaging/features/pixelization/slam.py` | Pixelized source with standard Sersic/parametric lens light. |
| C | `imaging/features/linear_light_profiles/slam.py` | Linear light profiles for lens and/or source. Faster, less flexible than MGE. |
| D | `imaging/features/no_lens_light/slam.py` | No lens light stage (dark lens or pre-subtracted imaging). |

### Imaging — Advanced

| Option | Source path | Description |
|--------|-------------|-------------|
| E | `imaging/features/extra_galaxies/slam.py` | Adds extra galaxy light/mass components within the mask. |
| F | `imaging/features/advanced/mass_stellar_dark/slam.py` | Decomposes lens mass into stellar + dark matter (NFW). |
| G | `imaging/features/advanced/subhalo/sensitivity/slam_source_parametric.py` | DM subhalo sensitivity mapping with a parametric source. |
| H | `imaging/features/advanced/subhalo/sensitivity/slam_source_pixelized.py` | DM subhalo sensitivity mapping starting from a pixelized SLaM result. |

### Interferometer

| Option | Source path | Description |
|--------|-------------|-------------|
| I | `interferometer/features/pixelization/slam.py` | Standard pixelized source for ALMA/interferometer data. No lens light stage. |
| J | `interferometer/features/extra_galaxies/slam.py` | Interferometer pipeline with extra galaxy components. |

### Group Scale

| Option | Source path | Description |
|--------|-------------|-------------|
| K | `group/slam.py` | Group-scale lensing with multiple lens galaxies and extra perturbers. |

## slam_claude.md

When the `/init-slam` skill runs, it creates `slam_claude.md` in this folder. That file contains:

- Full SLaM design context extracted from `autolens_workspace/scripts/guides/modeling/slam_start_here.py`
- A list of the scripts active in this project with descriptions

All scripts carry a banner comment pointing to `slam_claude.md`. Future AI sessions working on
this project should read `slam_claude.md` before modifying any SLaM pipeline script.

## After Copying Scripts

Update dataset-specific values at the bottom of each script (or confirm that `info.json` provides
them via `info.get(key, default)`). See the project root `CLAUDE.md` for the full new-project
workflow checklist.
