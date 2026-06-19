---
name: science-project
description: Scaffold a lean, reproducible, shareable PyAutoLens science project headed toward a paper. Runs the lifecycle local → private GitHub → public paper-companion repo, with per-run reproducibility manifests, a project journal, collaborator-facing summaries, and an open-science release (CITATION.cff, license, Zenodo DOI). Use when the user wants to "start a science project", "set up a paper repo", "share this analysis with collaborators", or "prepare this project for public release". Distinct from start-new-project (which builds the heavy HPC modelling workspace).
user-invocable: true
---

# Science Project

Scaffold and run a **shareable, reproducible science project** — the repo a user takes from
first fit to published paper. It is a project-workflow skill: it drives `git`/`gh`/file
operations and produces a project repo, not a Python lensing script.

## Relationship to other skills

- **`start-new-project`** builds the *heavy HPC modelling workspace* (rsyncs the whole
  assistant: HPC submit infra, sync tooling, configs) for running large model-fits on a
  cluster. Reach for it when the bottleneck is *compute*.
- **`science-project`** (this skill) builds a *lean, shareable repo* whose job is
  reproducibility, collaboration, and publication. Reach for it when the bottleneck is
  *sharing and writing up*.

They are not mutually exclusive — a user may run fits in an HPC workspace and keep the
publishable code/figures/manifests in a science project. This skill **reuses** existing
conventions rather than reinventing them: the `project/` journal mirrors the
`wiki/project/` shape (`wiki/project/_template.md`), and the GitHub-repo creation follows the
same `gh repo create` flow as `start-new-project` Step 6.

## Orient — what stage is the user at?

1. **New project** → generate the scaffold (Branch A) and initialise git.
2. **Existing project, mid-analysis** → write/refresh a run manifest, append a journal entry,
   or draft a collaborator update.
3. **Heading public** → run the release-hardening gate before the repo goes public.

Ask **one** question only if the stage is genuinely unclear.

## Branch A — create the project

### A1. Source the scaffold

**Preferred (when an exemplar exists):** if the "Example projects" registry at the bottom of
this skill lists a suitable repo, offer to **clone and adapt** it (`git clone`, strip its
data/results, re-stamp `project.yaml`/`CITATION.cff`). Real assistant-built projects are the
best templates; this is how the scaffold improves over time.

**Default (today):** generate the standard scaffold below from scratch. The project is a
**standalone repo that lives outside `autolens_assistant`** (e.g. `~/projects/<slug>/`), so
it can become its own private and then public GitHub repository.

### A2. Scaffold tree

```
<slug>/
  README.md
  project.yaml              # minimal manifest
  .gitignore
  .gitattributes            # * text=auto eol=lf
  environment.yml           # pinned env (fill from the working venv/conda env)
  CITATION.cff
  data/
    README.md               # what the data is, where it lives, access terms
    raw/.gitkeep            # contents gitignored
    reduced/.gitkeep        # contents gitignored
    external/README.md      # how to obtain third-party data (URLs, not files)
  scripts/
    scratch/.gitkeep        # gitignored scratch
  results/
    manifests/.gitkeep      # per-run manifests — TRACKED
    figures/.gitkeep        # publication figures — TRACKED
    tables/.gitkeep         # publication tables — TRACKED
  project/                  # collaboration journal (mirrors wiki/project style)
    project_log.md
    decisions.md
    open_questions.md
    results_summary.md
    collaborator_update.md
  paper/
    figures/.gitkeep
    tables/.gitkeep
# LICENSE is added at the public-release stage (Branch C), not before.
```

### A3. File contents

`project.yaml` — keep it minimal; it records intent, not behaviour:

```yaml
schema_version: 1
project:
  slug: <slug>
  title: <one-line title>
  owner: <name / ORCID>
visibility_stage: private          # private | github_private | public
data:
  classification: restricted       # restricted | public
  publish_raw: false               # never flips to true without explicit user say-so
  dataset_ids: []
reproducibility:
  environment_file: environment.yml
  seed_policy: required
  default_seed: 42
release:
  citation_cff: true
  license: null                    # chosen at public-release time
  zenodo: planned                  # planned | on_release | <DOI>
source_boundary:
  edit_pyauto_source: false        # science work does not edit PyAuto* source
```

`.gitattributes`:

```
* text=auto eol=lf
*.fits binary
*.png binary
*.npy binary
*.pkl binary
```

`.gitignore` — exclude data, bulky output and secrets; **keep manifests, figures, tables and
the journal tracked**:

```
# Data — raw/reduced/external stay out of git (often restricted, always bulky)
data/raw/*
data/reduced/*
data/external/*
!data/**/README.md
!data/**/.gitkeep

# Bulky runtime output
output/
results/runs/
scripts/scratch/*
!scripts/scratch/.gitkeep

# Secrets / local env
.env
*.key
.venv/
__pycache__/
*.pyc

# Keep tracked: results/manifests, results/figures, results/tables, project/, paper/
```

`README.md`, `CITATION.cff`, `environment.yml`, and the five `project/*.md` files follow the
shapes in "Templates" below. Write `.gitkeep` files into the empty tracked dirs.

### A4. Initialise

```bash
cd <slug>
git init
git add -A
git commit -m "Scaffold science project <slug>"
```

(A genuinely new repo — `git init` here is correct; this is *not* the never-rewrite-history
case, which concerns repos that already have a remote.)

## The reproducibility core — per-run manifests

This is how the project stays reproducible without any logging machinery: **after each
meaningful analysis run, write one JSON manifest** to `results/manifests/<run_id>.json`.
An agent can reliably produce this once per run; do not attempt per-event transcripts.

```json
{
  "run_id": "2026-06-19_imaging_slacs0946",
  "script": "scripts/imaging.py",
  "command": "python scripts/imaging.py --dataset slacs0946 --seed 42",
  "cwd": "/abs/path/<slug>",
  "git_commit": "<sha>",
  "git_dirty": false,
  "environment_file": "environment.yml",
  "python_version": "3.11.x",
  "package_versions": {"autolens": "<v>", "autofit": "<v>", "numpy": "<v>", "jax": "<v>"},
  "seed": 42,
  "inputs":  [{"path": "data/reduced/slacs0946/data.fits", "sha256": "<hash>"}],
  "outputs": [{"path": "results/figures/fit_slacs0946.png", "sha256": "<hash>"}],
  "started": "<iso8601>",
  "finished": "<iso8601>",
  "notes": "smooth SLaM baseline; evidence logged in results_summary.md"
}
```

Record **both** the seed and the NumPy/PyAuto* versions — the random-generator bitstream is
not promised stable across versions, so a seed alone is not a reproducibility guarantee. The
matching `project/project_log.md` entry references the manifest by `run_id`.

## The project journal

`project/` is the collaboration journal, mirroring the `wiki/project/` convention:

- `project_log.md` — dated entries (Context / What I did / Outcome), newest first; each run
  links its manifest.
- `decisions.md` — durable modelling/scientific decisions and their rationale.
- `open_questions.md` — unresolved questions and what would settle them.
- `results_summary.md` — the current best models, evidences, and headline numbers.
- `collaborator_update.md` — the latest human-facing summary (regenerated on request).

## GitHub lifecycle — three stages

1. **Local private** — code, docs, manifests, figures, tables and the journal in git; raw
   data and bulky output excluded by `.gitignore`. `visibility_stage: private`.
2. **Private GitHub (collaborators)** — push to a **private** repo
   (`gh repo create <owner>/<slug> --private --source=. --push`, same flow as
   `start-new-project` Step 6). Optionally add branch protection / PRs / a light CI for
   coauthors. `visibility_stage: github_private`.
3. **Public paper-companion repo** — only after the release-hardening gate below.
   `visibility_stage: public`.

## Branch C — public-release hardening gate

Before a project goes public, confirm **every** item — this is a gate, not a checklist to
skim:

- [ ] **No raw/restricted data tracked.** `git ls-files data/` shows only READMEs/`.gitkeep`.
      Re-verify `data.publish_raw` is still `false` unless the user explicitly cleared the data.
- [ ] **LICENSE chosen and added** (e.g. MIT for code; CC-BY-4.0 for data/figures if any are
      shared). Set `release.license` in `project.yaml`.
- [ ] **CITATION.cff present and correct** (authors, title, version, ORCID).
- [ ] **Data-availability statement** in `README.md` (where the data is, access terms, what
      is and isn't shared).
- [ ] **Reproducible**: scripts + `results/manifests/` + `environment.yml` are present and the
      manifests reference the committed commit.
- [ ] **No secrets** in history (`.env`, keys).

Then tag a release and (optionally) mint a DOI:

```bash
git tag -a v1.0.0 -m "Paper release"
gh release create v1.0.0 --title "<paper> data & code" --notes-file project/results_summary.md
```

Enable the **Zenodo–GitHub integration** before tagging so the release auto-archives and
gets a DOI; record the DOI in `release.zenodo` and `CITATION.cff`.

## Templates

Concise, scientific, decision-oriented shapes for the generated files:

- **`README.md`** — title; one-paragraph science goal; data-availability statement; how to
  reproduce (env + `scripts/` + manifests); citation pointer.
- **`CITATION.cff`** — `cff-version: 1.2.0`, `title`, `authors` (with ORCID), `version`,
  `date-released`, `doi` (filled at release).
- **`environment.yml`** — pinned `python` + the key stack versions (`autolens`, `autofit`,
  `numpy`, `jax`); fill from the working environment, don't guess.
- **`project/project_log.md`** — same Context / What I did / Outcome shape as
  `wiki/project/_template.md`.
- **`project/collaborator_update.md`** — best model so far; key figures (paths); open
  concerns; recommended next run. Short and skimmable.
- **`data/external/README.md`** — third-party datasets by URL/DOI and access terms, never the
  files themselves.

## Constraints

- **Source/science boundary holds:** scaffolding a project never edits PyAuto*/PyAutoLabs
  source. If a library bug or missing feature surfaces, write a dev-handoff note in
  `project/open_questions.md` instead.
- **No logging machinery:** reproducibility is run manifests + the dated journal. Do not add
  hash-chained transcripts, event schemas, or retention/redaction engines.
- **Cross-tool:** plain files and `git`/`gh` — no Claude-only mechanism.
- **`publish_raw` is sticky:** it only becomes `true` on an explicit, specific user
  instruction; the release gate re-checks it.

## Example projects (registry)

Real science projects built with this skill — clone-and-adapt one as the scaffold source
(Branch A1) instead of generating from scratch. Add a repo here once it exists and is a good
exemplar (URL + one-line description). Empty for now:

- _none yet — generate the standard scaffold above until the first exemplar is added._

## Further reading

- `skills/start-new-project.md` — the heavy HPC modelling workspace (the compute-side sibling).
- `wiki/project/_template.md` — the journal-entry shape the `project/` log mirrors.
- CITATION.cff format: https://citation-file-format.github.io/
- Zenodo–GitHub release archiving: https://docs.github.com/repositories/archiving-a-github-repository/referencing-and-citing-content
