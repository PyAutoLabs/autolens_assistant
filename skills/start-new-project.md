---
name: start-new-project
description: The single bridge from the assistant to a standalone science project, and the project's full lifecycle. Use when the user says "start a new project", "create a project", "set up a science project", "set up a paper repo", "share this analysis with collaborators", "continue a collaborator's project" (they forked/cloned one), "open-source the repo that goes with my paper", or "prepare this project for public release". Creates a separate, self-contained git repo for one analysis/paper that refers back to this assistant for skills and wiki, then carries it through Create → Work → Collaborate → Publish.
user-invocable: true
---

# Start New Project

The single bridge between the assistant and a **science project**, and the skill that owns that
project's whole lifecycle. There is no second science-project skill — this is it.

## Assistant vs science project

> **`autolens_assistant` is the copilot; a science project is a separate repo.** This repo is
> the assistant you clone once — its skills, wiki, and tooling. Your actual science lives in a
> **science project**: a separate, self-contained git repo for one analysis or paper, created
> by `start-new-project`. The project holds your data, config, scripts, results, and a
> `wiki/project/` journal; for the assistant's *skills and reference wiki* it **refers back to
> this `autolens_assistant` clone** (cloning it on demand if absent), so there's one source of
> truth and no drift. Quick exploration can happen inside this clone (e.g. the bundled-dataset
> README examples); a real analysis headed for a paper gets its own project.

The project copies only what's needed to **reproduce the science** (`config/`, `activate.sh`,
`scripts/`, `dataset/`, `results/`, `hpc/`) — not the copilot's brain (`skills/`, `wiki/core/`,
`wiki/literature/`, `autoassistant/`, `modes/`), which it refers back to. This keeps the
published paper repo clean: a reviewer cloning it sees the analysis, not the whole assistant.

## Lifecycle

**Create → Work → Collaborate → Publish.** Create runs now; the later phases are invoked on
demand as the project matures. Match the user's intent to a phase and do only that phase.

---

## Phase 1 — Create

### 0. Environment discovery — run before asking setup questions

Any step that needs identity or infrastructure values (name/ORCID for `project.yaml` +
`CITATION.cff`, GitHub owner at step 6 / Collaborate, HPC alias for the `hpc/` step)
**discovers before it asks**. Precedence: the user's current instruction → project
configuration (`project.yaml`, `hpc/sync.conf`, `wiki/project/profile.md`) → detected
standard-tool state → ask one focused question.

Detect from standard tools (read-only; never store, echo, or copy credentials):

- Git identity: `git config user.name` / `git config user.email`.
- GitHub account + auth: `gh auth status`; default owner via `gh api user --jq .login`.
- SSH host aliases (candidate HPC targets): `grep -E '^Host ' ~/.ssh/config` (skip quietly
  if absent or unreadable).
- The assistant profile (`wiki/project/profile.md`) and, inside a project, its `project.yaml`.

When a detected value is used, say so in one line ("using GitHub owner `X` from `gh auth` —
correct?") so the user can override; when nothing is detected, ask. State where an accepted
value will be recorded (`project.yaml`, `profile.md`, or `hpc/sync.conf` — secrets only ever
live in `~/.ssh/config` / `gh auth`). Standard tools stay authoritative for authentication
and account selection: with multiple accounts, clusters, or SSH aliases detected, ask which
to use — never assume one global default. This is a lightweight preflight, not an onboarding
form: detect, state, confirm, move on. (A machine-local defaults file for non-secret values
is deliberately deferred until real multi-project usage shows which values recur.)

### 1. Name
> **What should this project be called?** (folder name, created at `<NEW_PROJECT>/` *outside*
> this assistant clone; short and descriptive, e.g. `slacs_subhalo`, `euclid_pilot`.)

Store as `PROJECT_NAME`.

### 2. Description
> **One or two sentences on the project's scientific goal.** Written into the project's
> `AGENTS.md` and `project.yaml`.

Store as `PROJECT_DESCRIPTION`.

### 3. Datasets
> **Datasets to include?** In a project they live under `dataset/<sample>/<dataset_name>/`
> (`<sample>` a grouping dir, e.g. `imaging/`); each needs at least `data.fits`,
> `noise_map.fits`, `info.json` (see `wiki/core/operations/dataset.md`). Point me at paths to
> copy, or skip and add later.

> **The folder is `dataset/` — never `data/`. Be pedantic about this.** It is
> `dataset/` everywhere in the PyAuto workspace convention: this assistant clone, every
> `autolens_workspace` example, `PyAutoReduce`'s scripts/docs, and the `--sample`/`--dataset`
> CLI idiom (`dataset/<sample>/<dataset_name>/`). A project that uses `data/` silently
> diverges — scripts, `hpc/sync`'s `DATA_DIRS`, and anything copied from the workspace all
> assume `dataset/`, so the mismatch surfaces later as "why did nothing sync / why can't the
> script find the dataset". Do not "improve" on the name, and do not accept `data/` from an
> existing project without flagging it. (Note `project.yaml`'s `data:` *key* is a different
> thing — a metadata block, not the folder; leave it as `data:`.)

### 4. Modeling scripts
> **Modeling scripts?** They live in `scripts/`, normally adapted from `autolens_workspace`.
> Point me at files, describe the science case so I can scan a workspace (use the Explore
> agent), or skip and use `/init-slam` later.

### 5. Scaffold the project (thin, refer-back — replaces the old whole-assistant rsync)

Create `<NEW_PROJECT>/` and populate it. **Do not `rsync` the assistant.** Copy only the
reproducible-science subset; generate the thin assistant layer; refer back for everything else.

**Copy from the assistant into the project** (the science needs these to run):
- `config/` (PyAutoConf YAML — required: pipelines `conf.instance.push(config, output)`)
- `activate.sh` (sourced locally and by HPC batch scripts)
- `scripts/` (the chosen pipeline(s), or empty + `/init-slam` later)
- datasets (Step 3) into `dataset/<sample>/...` — **`dataset/`, not `data/`** (workspace
  convention; see the pedantic note in Step 3). The project's tracked-by-README dataset tree —
  see the `.gitignore` below and the Publish gate, which audits `git ls-files dataset/`

**Generate the lean project tree:**
```
<NEW_PROJECT>/
  README.md                 # front door: reproduce + continue-this-work (template below)
  AGENTS.md                 # thin: project context + refer-back + locate rule (below)
  CLAUDE.md                 # one-line `@AGENTS.md` stub
  .gemini/settings.json     # context.fileName -> AGENTS.md
  .claude/settings.json     # PyAuto* API code-gate via refer-back (below)
  project.yaml              # minimal manifest incl. assistant_ref (below)
  config/  activate.sh  scripts/        # copied above
  dataset/  (datasets — `dataset/`, NEVER `data/`; workspace convention)
  results/{manifests,figures,tables}/.gitkeep   # manifests/figures/tables TRACKED
  paper/{figures,tables}/.gitkeep
  wiki/project/             # journal — copy _profile_template.md + _template.md + README;
                            #   generate bibliography.md (below)
  environment.yml  CITATION.cff  .gitignore  .gitattributes
```

**Never copy** `skills/`, `wiki/core/`, `wiki/literature/`, `autoassistant/`, `modes/`,
`.maintainer`, `.pytest_cache/`, `version.txt` — the project refers back for those.

**Thin `AGENTS.md`** (generate; `CLAUDE.md` = `@AGENTS.md` stub so all tools inherit it):
```markdown
# <PROJECT_NAME> — science project

<PROJECT_DESCRIPTION>

This is a science project created with autolens_assistant. The assistant is the copilot; this
repo is the science. It copies what's needed to reproduce the analysis and **refers back** to
the assistant for skills and reference wiki.

## The assistant (skills + wiki)
Resolve the assistant clone, in order: `$AUTOLENS_ASSISTANT` → sibling `../autolens_assistant`
→ else clone `https://github.com/PyAutoLabs/autolens_assistant` into `sources/autolens_assistant/`
(gitignored). Read its `AGENTS.md` and follow its constitution (safety invariants, conventions,
modes); use its `skills/` and `wiki/` as the how-to and reference.
After resolving, compare the clone's commit to `project.yaml`'s `assistant_ref.commit`; if they
differ, mention the provenance drift and offer to re-pin — never block on it and never check
out the pinned commit.

## Code gate
This project ships the assistant's PyAuto* **API code-gate** (`.claude/settings.json`): before
Bash runs generated PyAuto* code, a hook resolves the assistant (same order as above) and
validates the symbols against the installed stack, denying code written from memory. It fails
open if no assistant clone is found. Only Claude Code runs `.claude/` hooks — on any other
harness (Codex, Gemini, chat), self-enforce it: run
`python <resolved-assistant>/autoassistant/audit_skill_apis.py --code "<snippet>"` (or
`--file <script.py>`) on generated PyAuto* code before executing it; never guess symbols.

## This project
- Context / decisions / results: `wiki/project/` (dated journal + `profile.md`).
- Literature: general lensing concepts → the assistant's shared `wiki/literature/`
  (refer-back); papers specific to this analysis → `wiki/project/bibliography.md`.
  Promotion upstream is deliberate, via `al_ingest_paper` from the assistant clone.
- Toolchain provenance: `project.yaml` (`assistant_ref`) + per-run `results/manifests/`.
- Reproducibility: every meaningful run writes `results/manifests/<run_id>.json`.
```

**Project `README.md`** (generate — the front door a collaborator, referee or reader sees
first on GitHub; keep it this short, the detail lives in `AGENTS.md` and the journal):
```markdown
# <PROJECT_NAME>

<PROJECT_DESCRIPTION>

A science project built with
[autolens_assistant](https://github.com/PyAutoLabs/autolens_assistant), the PyAutoLens AI
assistant. This repo is self-contained: everything needed to reproduce the analysis is here.

## Reproduce this analysis

Set up the environment with `source activate.sh` (packages: `environment.yml`). The modeling
scripts are in `scripts/`; every meaningful run is recorded in `results/manifests/` (exact
command, seed, package versions, input/output checksums), so any result can be traced and
re-run.

## Continue this work

Fork or clone this repo and drive it with your own AI assistant: point `$AUTOLENS_ASSISTANT`
at a local `autolens_assistant` clone — or just start your agent here and let it clone the
assistant on demand (see `AGENTS.md`). You inherit the same skills, reference wiki and safety
rules this project was built with, plus the full decision journal in `wiki/project/`.

## Data availability

<!-- Filled in at Publish: where each dataset lives, and its access terms. -->

## Citation

See `CITATION.cff`.
```

**`project.yaml`** (minimal; records intent + the provenance pin):
```yaml
schema_version: 1
project: { slug: <slug>, title: <title>, owner: <name/ORCID> }
visibility_stage: private          # private | github_private | public
assistant_ref:                     # provenance, not an enforced checkout
  repo: PyAutoLabs/autolens_assistant
  commit: <assistant HEAD sha at creation>
data: { classification: restricted, publish_raw: false, dataset_ids: [] }
reproducibility: { environment_file: environment.yml, seed_policy: required, default_seed: 42 }
release: { citation_cff: true, license: null, zenodo: planned }
source_boundary: { edit_pyauto_source: false }
```

**`.claude/settings.json`** (generate — the PyAuto* API code-gate via refer-back; **on by
default and fail-open**: if no assistant clone resolves, the hook silently allows):
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'P=\"${CLAUDE_PROJECT_DIR:-.}\"; for d in \"$AUTOLENS_ASSISTANT\" \"$P/../autolens_assistant\" \"$P/sources/autolens_assistant\"; do [ -n \"$d\" ] && [ -f \"$d/.claude/hooks/validate_pyauto_code.py\" ] && exec python3 \"$d/.claude/hooks/validate_pyauto_code.py\"; done; exit 0'"
          }
        ]
      }
    ]
  }
}
```
The validator stays in the assistant — `validate_pyauto_code.py` resolves
`audit_skill_apis.py` relative to itself — so the project vendors nothing and bakes in no
absolute paths. The cross-tool caveat (hooks are Claude Code-only; other harnesses
self-enforce) is stated in the generated `AGENTS.md` "Code gate" section above.

**`wiki/project/bibliography.md`** (generate — the project-local literature home; the hybrid
rule stated once in its header):
```markdown
# Bibliography — papers specific to this analysis

Papers that belong to this project's reference list live here, one `##` section per paper in
the same shape as the assistant's `wiki/literature/sources/*.md` (canonical BibTeX key,
reference, concepts, supported claims — public arXiv/DOI references only, never local PDF
paths). General lensing concepts are NOT duplicated here: the assistant's shared
`wiki/literature/` (resolved via refer-back) stays the one source of truth. A paper that
proves generally useful can be promoted upstream by running `al_ingest_paper` from the
assistant clone — promotion is deliberate, never the default.
```

**`.gitattributes`**: `* text=auto eol=lf` (+ `*.fits *.png *.npy *.pkl binary`).

**`.gitignore`** (exclude data/output/secrets/cloned-assistant; **keep** manifests/figures/journal):
```
dataset/raw/*
dataset/reduced/*
dataset/external/*
!dataset/**/README.md
!dataset/**/.gitkeep
!dataset/**/info.json
output/
results/runs/
scripts/scratch/*
!scripts/scratch/.gitkeep
sources/                 # cloned-on-demand assistant / source repos
hpc/sync.conf
hpc/sync_jump.conf
.env
*.key
__pycache__/
*.pyc
```

**Optional HPC step — ask once:** *"Set up an HPC folder for this project?"* (Offer step 0's
detected SSH host aliases as candidate clusters instead of asking cold.)
- **Yes** → copy the assistant's `hpc/` (batch templates, `sync`, `template.py`) into the
  project and configure (job name, `--array`, `SCRIPT=`, `sample=`, `datasets=(...)`).
- **No** → create only `hpc/README.md` containing the ready-to-paste prompt:
  *"Set up the HPC folder for this project: copy the batch templates, sync script and pipeline
  template from the assistant and configure them for my cluster."*

If HPC is in play, also capture the user's HPC access **constraints** in
`wiki/project/profile.md` ("HPC access" — cluster/alias, MFA, VPN, jump host, whether
agent-driven remote execution is permitted, and the preferred automation level). Ask once,
lightly; these set the assistant's HPC posture. Connection details go in `hpc/sync.conf`,
secrets in `~/.ssh/config` — never in the profile.

**Finish Create:** `dos2unix` all `*.py`/`*.sh`/`template*`; `git init`; stage by name;
`git commit -m "Scaffold science project <slug>"`; optionally append a `Project<Name>()` alias
to `~/.bashrc` (source the venv, `cd` in).

### 6. GitHub (private) — optional now, or at Collaborate
Offer a **private** repo for backup/collaborators:
`gh repo create <owner>/<slug> --private --source=. --push` — `<owner>` from step 0's
discovery (confirm in one line), asking only if multiple accounts/orgs are plausible.
Public comes only at Publish.

---

## Phase 2 — Work

Normal modelling, using the assistant's skills resolved via refer-back. Reproducibility rests
on two things only — **no transcript/hash machinery**:

1. **Per-run manifest** → write `results/manifests/<run_id>.json` after each meaningful run:
```json
{
  "run_id": "2026-06-19_imaging_slacs0946",
  "script": "scripts/imaging.py",
  "command": "python scripts/imaging.py --dataset slacs0946 --seed 42",
  "git_commit": "<project sha>", "git_dirty": false,
  "assistant": { "repo": "PyAutoLabs/autolens_assistant", "commit": "<assistant sha>", "dirty": false },
  "environment_file": "environment.yml", "python_version": "3.11.x",
  "package_versions": { "autolens": "<v>", "autofit": "<v>", "numpy": "<v>", "jax": "<v>" },
  "seed": 42,
  "inputs":  [{ "path": "dataset/reduced/slacs0946/data.fits", "sha256": "<hash>" }],
  "outputs": [{ "path": "results/figures/fit.png", "sha256": "<hash>" }],
  "started": "<iso8601>", "finished": "<iso8601>", "notes": "smooth SLaM baseline"
}
```
   Record the seed **and** package versions **and** the `assistant` commit — the generator
   bitstream isn't promised stable across versions, and the assistant commit is the toolchain
   provenance (the entire "pin": operation uses the current clone; the manifest records what
   was actually used).

2. **Dated journal** → `wiki/project/YYYY-MM-DD-<slug>.md` (use the existing `_template.md`
   shape: Context / What I did / Outcome), each entry referencing its `run_id`. This is the
   same `wiki/project/` mechanism the assistant already uses — do not invent a parallel log.
   An accepted `assistant_ref` re-pin (from the provenance-drift check in "Locating the
   assistant from a project" below) is one line in the day's entry, not a new log.

---

## Phase 3 — Collaborate

A science project is **built to be shared** — the repo itself is the collaboration surface.
Encourage sharing as soon as a second person appears in the conversation: nothing needs to be
prepared, exported, or handed over out-of-band.

- Push to a **private** GitHub repo if not already (`gh repo create … --private`); optionally
  add branch protection / PRs / light CI for coauthors.
- **A collaborator continues the work by forking or cloning the project** and starting their
  own assistant session inside it: the thin `AGENTS.md` resolves an `autolens_assistant` clone
  via refer-back (`$AUTOLENS_ASSISTANT` → sibling → clone-on-demand), so they inherit the same
  skills, reference wiki, and safety rules the project was built with. Their first session:
  read `README.md` and the latest `wiki/project/` entries, note the provenance-drift check
  result, then continue the analysis — new runs write manifests and journal entries exactly as
  Phase 2 describes. Point an arriving collaborator at the README's "Continue this work"
  section; that is the whole onboarding.
- **Collaborator updates are built from the `wiki/project/` journal** — synthesise the latest
  best model, key figures (paths), open concerns, and recommended next run into a short,
  skimmable summary (e.g. `wiki/project/collaborator_update.md`). Don't keep a second log.

---

## Phase 4 — Publish (paper-companion hardening)

Publishing turns the project into the **open-source companion to the paper**: the data (or its
availability statement), the results, and every python script that produced them, in one
citable repo a reader can reproduce — and fork to build on (the README's "Continue this work"
section now speaks to them too).

Gate — confirm **every** item before the repo goes public (`visibility_stage: public`):

- [ ] **No raw/restricted data tracked** (`git ls-files dataset/` shows only
      READMEs/`.gitkeep`/`info.json`);
      `data.publish_raw` still `false` unless the user explicitly cleared it.
- [ ] **No full transcripts / scratch / secrets** in history (`.env`, keys, `scripts/scratch/`).
- [ ] **LICENSE** chosen and added (e.g. MIT code; CC-BY-4.0 for shared figures/data); set
      `release.license`.
- [ ] **CITATION.cff** correct (authors + ORCID, title, version).
- [ ] **Data availability** section in `README.md` filled in (scaffolded at Create; where the
      data is, access terms).
- [ ] **Reproducible**: `scripts/` + `results/manifests/` + `environment.yml` present and the
      manifests reference the committed commit.

Then release and (optionally) mint a DOI:
```bash
git tag -a v1.0.0 -m "Paper release"
gh release create v1.0.0 --title "<paper> data & code" --notes-file wiki/project/results_summary.md
```
Enable the **Zenodo–GitHub integration before tagging** so the release auto-archives → DOI;
record the DOI in `release.zenodo` and `CITATION.cff`.

**Caveats:**
- **Do not make the repo a GitHub *template* repo if you want Git LFS** — LFS is incompatible
  with template repositories.
- **GitHub release assets are < 2 GiB each** — large data goes to **Zenodo / an external
  archive**, never release assets. The repo holds code + manifests + figures, not bulk data.

---

## Locating the assistant from a project

A project is self-describing: its `AGENTS.md` and `project.yaml` record the assistant repo URL
and creation commit. When the copilot is invoked inside a project, resolve the assistant in
order — `$AUTOLENS_ASSISTANT` → `../autolens_assistant` → clone the recorded URL on demand into
the gitignored `sources/autolens_assistant/` — then read `skills/` and `wiki/` from there. This
mirrors the source-of-truth `sources/` clone-on-demand pattern in `AGENTS.md`; the project
depends on no vendored copy of the assistant.

**Provenance-drift check (non-blocking).** After resolving, compare the clone's commit
(`git -C <resolved> rev-parse HEAD`) to `project.yaml`'s `assistant_ref.commit`. If they
differ, tell the user once per session — both commits, and what the drift means (the toolchain
moved since the project was pinned; a provenance note, not a correctness problem) — and offer
to **re-pin**: update `assistant_ref.commit` to the resolved HEAD and note the re-pin in the
day's `wiki/project/` journal entry. Never hard-block on drift and never check the clone out
to the pinned commit — day-to-day operation always uses the resolved current clone, and the
per-run manifest's `assistant.commit` remains the record of what was actually used.

## Example projects (registry)

Real science projects built with this skill — clone-and-adapt one as the Create scaffold source
instead of generating from scratch, once a good exemplar exists. Add a repo here (URL + one-line
description) when it does. Empty for now:

- _none yet — generate the standard scaffold above until the first exemplar is added._

## Further reading

- `wiki/project/_template.md` — the journal-entry shape (Work / Collaborate reuse it).
- `wiki/core/operations/dataset.md` — dataset layout + `info.json`.
- `wiki/core/operations/hpc_infrastructure.md` — the `hpc/` batch templates + `sync` CLI.
- `skills/init-slam.md` — populate `scripts/` with SLaM pipelines.
- CITATION.cff: https://citation-file-format.github.io/ · Zenodo–GitHub archiving:
  https://docs.github.com/repositories/archiving-a-github-repository/referencing-and-citing-content
