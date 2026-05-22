---
name: start-new-project
description: Spin up a new PyAutoLens science workspace from the assistant. Use this skill when the user says "start a new project", "create a project", "set up a new project", or "new science workspace". Walks through project name, description, datasets, and modeling scripts, then scaffolds the project directory and optional GitHub repo.
user-invocable: true
---

# Start New Project

Interactive setup for a new PyAutoLens science workspace, scaffolded from the
`autolens_assistant` repo. Guides the user through naming, describing, and
populating a project step by step.

## Intro — Explain the spin-off

Before asking any questions, explain the following to the user:

> This repository (`autolens_assistant`) is the **PyAutoLens AI Assistant** —
> the directory structure, HPC submission scripts, sync tools, skills, wiki,
> and pipeline scaffolding that lets you do lens modelling by conversation.
>
> When you want a separate workspace dedicated to a specific science case (a
> survey, a paper, a sample), this skill copies the assistant's structure into
> a fresh directory (`<NEW_PROJECT>/`) and **resets the project journal** so
> the new workspace gets a clean slate. You then populate it with your
> datasets and modeling scripts; the assistant's skills and wiki come along
> for the ride.
>
> **Modeling scripts** are normally adapted from the **workspace
> repository** of the software you're using. For example, if you're using PyAutoLens, the
> `autolens_workspace` repository contains template scripts for different modeling pipelines
> and tutorials that you can copy and customize for your science case.
> Other workspaces include `autofit_workspace`, `autogalaxy_workspace`, etc.
>
> I'll walk you through five steps to set everything up. Most steps are optional — you can
> always add things later.

Then proceed to Step 1.

## Step 1 — Project name

Ask the user:

> **What should this project be called?**
>
> This will be the folder name, created at `<NEW_PROJECT>/`.
> Use a short, descriptive name (e.g. `slacs_subhalo`, `euclid_pilot`, `bells_mge`).

Store the answer as `PROJECT_NAME`. Confirm the full path will be
`<NEW_PROJECT>/`.

## Step 2 — Project description

Ask the user:

> **Give a short description of this project's scientific goals.**
>
> This will be written into the project's `CLAUDE.md` so that future AI sessions understand
> the purpose and scope of the project. A sentence or two is fine — e.g. "Subhalo detection
> in SLACS lenses using pixelized source reconstruction" or "MGE modeling of Euclid strong
> lens candidates for the initial catalog."

Store the answer as `PROJECT_DESCRIPTION`.

## Step 3 — Datasets

Ask the user:

> **Do you have datasets to include in this project?**
>
> Datasets live under `dataset/<sample_name>/<dataset_name>/`, where `sample_name` is the
> survey or batch (e.g. `slacs`, `bells`) and `dataset_name` is the individual lens (e.g.
> `slacs0737+3216`). Each dataset directory should contain at minimum `data.fits`,
> `noise_map.fits`, and an `info.json` with fields like `pixel_scale`, `redshift_lens`, etc.
>
> You can either:
> - **Point me to dataset paths** and I'll copy them into the project
> - **Skip for now** and add datasets later
>
> If pointing to paths, give me the source directory and tell me the sample name to file them
> under.

If the user provides paths, validate they exist and note the sample/dataset structure. If they
skip, move on.

## Step 4 — Modeling scripts

Ask the user:

> **Do you have modeling scripts for this project?**
>
> Modeling scripts define the analysis pipeline (e.g. SLaM stages for source, light, mass,
> subhalo detection). They live in `scripts/` in the project.
>
> These are normally **adapted from the workspace** of the software you're using. For example,
> `autolens_workspace/scripts/` contains template pipelines for imaging, interferometer, and
> group-scale lensing, organized by feature (pixelization, MGE, subhalo, etc.).
>
> You can either:
> - **Point me to specific script paths** and I'll copy them in
> - **Describe your science case** and I'll scan the workspace to suggest relevant templates
> - **Skip for now** — you can add scripts later or use the `/init-slam` skill
>
> If you want me to scan a workspace, tell me which workspace to look in (e.g.
> `autolens_workspace`) and describe what kind of modeling you need.

If the user asks for a workspace scan, use the Explore agent to search the workspace's
`scripts/` directory for relevant pipelines based on the user's science description. Present
the findings and let the user pick which scripts to copy.

If the user points to specific files, copy them to `scripts/` in the project.

If they skip, move on.

## Step 5 — Execute

Once all questions are answered, perform these actions:

### 5a — rsync from the assistant

Copy the assistant's structure into the new project directory. Always exclude
`dataset/`, `output/`, `__pycache__/`, and `*.pyc`:

```bash
rsync -av \
  --exclude='dataset/' \
  --exclude='output/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='skills/' \
  --exclude='wiki/project/profile.md' \
  --exclude='wiki/project/[0-9]*-*.md' \
  <ASSISTANT>/ \
  <NEW_PROJECT>/
```

The two `wiki/project/` exclusions **reset the project journal in the new workspace**:
they drop any prior `profile.md` and any dated `YYYY-MM-DD-<slug>.md` entries,
while keeping `README.md` and `_profile_template.md`. The new project gets a clean
slate to record its own decisions and user profile.

### 5b — Copy datasets

If the user provided dataset paths, copy them into
`<NEW_PROJECT>/dataset/<sample_name>/`. Verify each dataset
directory has at least `data.fits` and `info.json`.

### 5c — Copy modeling scripts

If the user provided or selected scripts, copy them into
`<NEW_PROJECT>/scripts/`.

### 5d — Update CLAUDE.md

Open `<NEW_PROJECT>/CLAUDE.md`. Add a project-specific section
at the very top, before the existing assistant instructions:

```markdown
# <PROJECT_NAME>

<PROJECT_DESCRIPTION>

---

```

### 5e — Run dos2unix

Convert all shell scripts and Python files to Unix line endings:

```bash
find <NEW_PROJECT>/ \
  -type f \( -name "*.py" -o -name "*.sh" -o -name "submit*" \) \
  | xargs dos2unix
```

### 5f — Add bash alias

Append a `Project<Name>()` function to `~/.bashrc`:

```bash
Project<ProjectName>() {
  source ~/venv/PyAuto/bin/activate
  cd <NEW_PROJECT>
}
```

Use PascalCase for the function name (e.g. `SlacsSubhalo` for project `slacs_subhalo`).

## Step 6 — GitHub repository

Ask the user:

> **Do you want to create a GitHub repository for this project?**
>
> A GitHub repo lets you manage the project remotely — edit scripts, push changes, and
> trigger HPC jobs from your phone or any device. Only **code** goes in the repo (scripts,
> config, HPC submit files). Large data files (`dataset/`, `output/`) stay excluded
> via `.gitignore` — data is already on the HPC from `hpc/sync push` and doesn't need to
> live in GitHub.
>
> Options:
> - **Private repo** — visible only to you (recommended for unpublished science)
> - **Public repo** — open to everyone
> - **Skip** — no GitHub repo for now

If the user wants a repo:

### 6a — Create .gitignore

Write a `.gitignore` at the project root with these entries:

```
# Data — too large for GitHub; lives on HPC via hpc/sync
dataset/
output/

# HPC local config (host-specific paths, never committed)
hpc/sync.conf
hpc/sync_jump.conf

# SLURM logs (pulled from HPC, not version-controlled)
hpc/batch_gpu/output/
hpc/batch_gpu/error/
hpc/batch_cpu/output/
hpc/batch_cpu/error/

# Python
__pycache__/
*.pyc
*.egg-info/

# OS
.DS_Store
Thumbs.db
```

### 6b — Initialize git and create the repo

```bash
cd <NEW_PROJECT>
git init
git add -A
git commit -m "Initial science workspace from autolens_assistant"
```

Then determine the user's GitHub username:

```bash
gh api user --jq .login
```

Store the result as `GH_USER`. Create the repo:

```bash
# Private (default):
gh repo create <GH_USER>/<PROJECT_NAME> --private --source=. --push

# Public:
gh repo create <GH_USER>/<PROJECT_NAME> --public --source=. --push
```

Use `--private` or `--public` based on the user's choice.

### 6c — Confirm

Report:
- Repo URL: `https://github.com/<GH_USER>/<PROJECT_NAME>`
- What's tracked: scripts, config, HPC submit files, skills, wiki
- What's excluded: dataset/, output/, SLURM logs, sync configs
- Remind them: data stays on the HPC. To work from your phone, edit code via GitHub,
  then SSH to the HPC to pull and submit jobs.

## Step 7 — Final summary

Report a summary:
- Project path: `<NEW_PROJECT>/`
- What was copied: datasets, scripts (or "none" for each)
- Bash alias added
- GitHub repo (if created): URL and visibility
- Remind the user of next steps:
  - Verify `info.json` in each dataset if datasets were copied
  - Update HPC submit scripts (`hpc/batch_gpu/submit_*`, `hpc/batch_cpu/submit_*`) with job
    name, `--array` range, `sample=`, and `datasets=(...)`
  - Run a test: `PYAUTOFIT_TEST_MODE=1 python3 scripts/<type>.py --sample=<sample> --dataset=<dataset>`
  - Use `/init-slam` if they skipped modeling scripts and want to set up SLaM pipelines later
  - If GitHub repo was created: push changes with `git add -A && git commit -m "..." && git push`
    after making edits
