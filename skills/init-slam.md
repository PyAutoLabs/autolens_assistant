---
name: init-slam
description: Initialize SLaM (Source, Light and Mass) modeling scripts for a new PyAutoLens project. Use this skill when starting a new strong-lens modeling project, when the scripts/ folder is empty and needs pipeline scripts, when a user says "set up scripts", "add a pipeline", "copy the slam script", or "initialize this project". Shows categorized options from autolens_workspace, copies chosen script(s) to scripts/, creates slam_claude.md with full SLaM context, and adds reference banners to each copied script.
---

# SLaM Script Initializer

Sets up lens modeling scripts for a new PyAutoLens project. Selects from available SLaM pipelines
in `autolens_workspace`, copies them to `scripts/`, and creates `slam_claude.md` so that future
AI sessions have full SLaM context without needing to read the workspace guides.

## Step 1 — Locate the project

The project root has a `scripts/` folder (empty in a fresh template). Confirm it exists. If the
user hasn't specified a project path, use the current working directory.

Check whether `scripts/` already contains scripts — if so, note which are present and ask whether
to add more or replace.

Also verify that `../autolens_workspace/` exists relative to the project root. If not, ask the
user for the correct path to `autolens_workspace`.

## Step 2 — Present pipeline options

Show the user these options grouped by category. Ask them to pick one or more (e.g., "A" or "A, I").

**Imaging — Standard** (most projects start here)

| # | Filename in scripts/ | Description |
|---|----------------------|-------------|
| A | `imaging.py` | MGE lens light (2x20 Gaussians) + pixelized source — standard choice for HST/Euclid |
| B | `imaging.py` | Pixelized source + parametric Sersic lens light |
| C | `imaging.py` | Linear light profiles for lens and/or source — faster, less flexible |
| D | `imaging.py` | No lens light stage — for dark lenses or pre-subtracted data |

**Imaging — Advanced** (add on top of a standard script)

| # | Filename in scripts/ | Description |
|---|----------------------|-------------|
| E | `imaging_extra_galaxies.py` | Extra galaxy light/mass within the mask |
| F | `imaging_stellar_dark.py` | Stellar + dark matter (NFW) mass decomposition |
| G | `imaging_subhalo_sensitivity_lp.py` | DM subhalo sensitivity mapping, parametric source |
| H | `imaging_subhalo_sensitivity_pix.py` | DM subhalo sensitivity mapping, pixelized source |

**Interferometer**

| # | Filename in scripts/ | Description |
|---|----------------------|-------------|
| I | `interferometer.py` | Standard pixelized source for ALMA/interferometer data (no lens light stage) |
| J | `interferometer_extra_galaxies.py` | Interferometer pipeline with extra galaxy components |

**Group Scale**

| # | Filename in scripts/ | Description |
|---|----------------------|-------------|
| K | `group.py` | Group-scale lensing — multiple lens galaxies and extra perturbers |

## Step 3 — Copy scripts

For each chosen option, copy the source file from `autolens_workspace/scripts/` to `scripts/`
using the destination filename from the table above.

If the script is destined for HPC array runs, preserve the command-line interface from
`hpc/template.py` (`parse_fit_args`, `__main__`, `--sample`, `--dataset`, `--use_cpu`,
`--number_of_cores`) — the `hpc/batch_cpu/template` and `hpc/batch_gpu/template` submit
scripts run `scripts/$SCRIPT` and depend on it.

Source paths (relative to `autolens_workspace/scripts/`):

```
A: imaging/features/multi_gaussian_expansion/slam.py
B: imaging/features/pixelization/slam.py
C: imaging/features/linear_light_profiles/slam.py
D: imaging/features/no_lens_light/slam.py
E: imaging/features/extra_galaxies/slam.py
F: imaging/features/advanced/mass_stellar_dark/slam.py
G: imaging/features/advanced/subhalo/sensitivity/slam_source_parametric.py
H: imaging/features/advanced/subhalo/sensitivity/slam_source_pixelized.py
I: interferometer/features/pixelization/slam.py
J: interferometer/features/extra_galaxies/slam.py
K: group/slam.py
```

If a destination file already exists, ask before overwriting.

After copying, add this banner comment at the very top of each script, before the existing docstring:

```python
# SLaM CONTEXT: See slam_claude.md in this directory for full documentation of the SLaM
# (Source, Light and Mass) pipeline — design philosophy, stage ordering, and key conventions.
#
# Source template: autolens_workspace/scripts/<relative-path>
```

Replace `<relative-path>` with the actual source path for that script.

## Step 4 — Create slam_claude.md

Read `autolens_workspace/scripts/guides/modeling/slam_start_here.py`. Extract all top-level
module docstrings (the `"""..."""` blocks that appear outside function bodies — these are the
explanatory sections between the function definitions, including the module docstring, pipeline
stage descriptions, and dataset setup comments).

Write `scripts/slam_claude.md` with this structure:

```markdown
# SLaM (Source, Light and Mass) — Project Reference

> Generated from `autolens_workspace/scripts/guides/modeling/slam_start_here.py`.
> That file contains a complete runnable example with the same pipeline structure as the
> scripts in this directory. Read it for concrete implementation details.

[paste extracted documentation prose here, preserving section headings and formatting]

---

## Scripts in This Project

[one line per copied script, format: `- filename.py` — one-sentence description]
```

If `slam_claude.md` already exists (a previous run added some scripts), only update the
"Scripts in This Project" section to append the new entries — do not overwrite the rest.

## Step 5 — Confirm and advise

Report:
- Which scripts were copied and their destination filenames
- That `slam_claude.md` was created/updated
- Remind the user to update dataset-specific values at the bottom of each script, or ensure
  `info.json` provides them (see the `start-new-project` skill for the full checklist)
- Remind them to run `dos2unix` on the copied scripts if working on Windows/WSL
