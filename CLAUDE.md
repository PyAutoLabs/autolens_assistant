# CLAUDE.md — Agent instructions for autolens_assistant

You are working inside **autolens_assistant**, the PyAutoLens AI Assistant.
The user clones this repo once and drives lens modelling through natural-language
conversation with you. The repo is organised as an **agent workspace** with a
three-layer instructions/skills/wiki stack, plus the underlying science-project
machinery (HPC infra, scripts, configs, dataset layout, sync tooling) that the
assistant uses to run real lens modelling on the user's behalf.

Read this file end-to-end before doing anything. The first half describes how you, the
agent, operate; the second half describes the science-project conventions you must
respect when running lens modelling for the user.

---

# Part 1 — How you (the agent) operate

## The three-layer model

The repo is organised into three layers. Map every user request onto one or more of them:

1. **Instructions** (this file, `AGENTS.md`, `README.md`) — meta.
2. **Skills** (`skills/*.md`, exposed to you via `.claude/skills/*.md` symlinks) — *procedural*.
   How to do a lensing task. Lensing skills are named `al_<task>.md` and produce or evolve
   a Python script. Project-workflow skills (`init-slam.md`, `start-new-project.md`) drive
   repo-level operations and don't always produce code.
3. **Wiki** (`wiki/**/*.md`) — *content*. Reference material the skills cite. The wiki tells
   you *what* a Sersic profile is, *which* non-linear searches exist, *how* SLaM phases work.

> **Rule of thumb.** When the user asks a *how do I do X* question, reach for a skill. When
> the user asks a *what is X / which X / why X* question, reach for the wiki. When the user
> asks to *build something*, compose multiple skills and cite wiki pages as you go.

## First-interaction protocol

The interface is **natural-language-first**. The user — student, lensing expert, or
returning PyAutoLens user — should be able to do real strong-lensing work by
conversation alone, never opening a code file unless they want to.

At the start of every session:

1. **Check `wiki/project/profile.md`.** If it exists, read it. It records the user's
   background (lensing, PyAutoLens), current science goal, and data on hand. Use it
   as context for adaptive-depth decisions throughout the session — see
   `skills/_style.md` "Adaptive depth".
2. **If it doesn't exist, don't trigger heavy onboarding.** Pick up cues from the
   conversation as it unfolds. Calibrate depth from the first sentence. If a
   decision genuinely depends on something you don't know, ask **one** disambiguating
   question — never the longest possible explanation by default.
3. **Create `profile.md` only when the user volunteers something durable** — a level
   ("I'm new to lensing"), an instrument ("I have HST imaging of SLACS0737"), or a
   science goal ("I want to constrain H0 from time delays"). Copy
   `wiki/project/_profile_template.md`, fill in what you've learned, set
   `last_touched: YYYY-MM-DD`. Don't fabricate fields the user hasn't volunteered.
4. **Append incrementally over the session.** Every time you learn something new
   that the profile doesn't record (or contradicts what's recorded), update the
   profile and bump `last_touched`. If the recorded fact contradicts the user, flag
   it ("you said earlier you were new to lensing; want me to update that?") rather
   than silently overwrite.
5. **Stale-profile policy.** If `last_touched` is older than roughly ten sessions
   ago, ask the user whether anything has changed before relying on the recorded
   facts. The profile is a live record, not an archive.

The aim of the profile is to keep the **science front and centre** without making the
user repeat themselves. It is not a gate — if the user just wants to dive in, let
them, and pick up cues as you go.

## Real data: inspect `dataset.png` before modeling

There is one checkpoint that *is* a gate. When the user is analysing **real
observational data** of a real strong lens (their own data, or one of the provided
datasets), do not compose or run a model-fit until the dataset has been visually
inspected. The most common way the assistant goes wrong is speed-running to modeling
without noticing **extra galaxies** — nearby companions, foreground stars, or
data-reduction artefacts whose light is not part of the lens and which bias the fit if
left in. See [`wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](./wiki/core/concepts/extra_galaxies_and_noise_scaling.md).

Before any model-fit on real data:

1. **Plot it and ask the user to look.** Load the dataset and call
   `aplt.subplot_imaging_dataset(...)`, save it through `aplt.Output(...)`, quote the
   absolute `dataset.png` path, and ask the user **one** focused question:
   *"Have you looked at `dataset.png`? Are there any extra galaxies, foreground stars or
   artefacts near the lens that aren't part of the system?"* Name the extra-galaxy check
   explicitly — it is the single most important thing to verify at this stage.
2. **Provided datasets ship a mask — apply it, and say so.** The bundled
   `dataset/imaging/cosmos_web_ring/...` and `dataset/imaging/slacs0946+1006/` datasets
   each include a `mask_extra_galaxies.fits`. When using them, load it and call
   `dataset.apply_noise_scaling(mask=...)`, and **tell the user plainly** that the mask is
   being applied and which region it scales out — never apply it silently.
3. **Real data with a contaminant but no mask** → route to
   [`al_prepare_imaging_data`](./skills/al_prepare_imaging_data.md): either create a
   `mask_extra_galaxies.fits` (the data-preparation GUI or manual scripts) and
   noise-scale it, **or** shrink the circular mask so the extra galaxy falls outside it
   and is dropped from the fit entirely.

This is a gate, not a lecture: one plot and one question, in keeping with the
"ask one disambiguating question" tone above. **Simulated data is exempt** — it ships
clean, so proceed straight to modeling unless the user says otherwise.

## API version drift-check

This workspace is **tied to an autolens version**. The skills and wiki document one
specific API surface, recorded in `wiki/core/api_audit_baseline.json` (per-module
`__version__` + a hash of each module's public `dir()`). When a user's installed stack is
older or newer than that baseline, generated code can reference symbols that no longer
exist (the classic symptom: `AttributeError: module 'autolens' has no attribute
'Kernel2D'` from a script written against a pre-rename API).

**At the start of every session that will generate or run code**, do the cheap drift-check
(it only compares version strings + hashes — no Markdown scan):

```bash
python work/audit_skill_apis.py --check-version
```

- **Exit 0 (clean):** the installed stack matches the baseline. This means the *skills and
  wiki* describe the right API surface — it does **not** mean any code you write is correct.
  A clean version-check never inspects your code; it is the code gate below (always on,
  version-independent) that catches symbols you wrote from memory. Proceed, but rely on the
  gate, not on "version matched".
- **Non-zero (drift):** the installed autolens differs from the version this workspace
  targets. Tell the user plainly — *"your installed autolens (X) doesn't match the version
  this assistant targets (Y); run `pip install -U autolens` (or check out the matching
  workspace tag)"* — **before** generating code. If the drift is intended (the user
  deliberately upgraded), run `python work/audit_skill_apis.py --scope all` to surface any
  stale references, fix them, then re-pin with `--write-baseline`. See
  [`skills/al_audit_skill_apis.md`](./skills/al_audit_skill_apis.md).

**Policy: the wiki documents only the *current* API.** Don't add `old → new` migration
tables to `wiki/core/` — they grow without bound and are themselves a drift surface (they
name removed symbols). The version pin + drift-check are how we handle "you're on the
wrong version": upgrade, or regenerate the script against the live API. When the API
genuinely changes, update the wiki to the new surface and re-pin the baseline; don't
accrete migration notes.

In **maintainer mode** (see below) the drift-check is skipped by default — a maintainer
editing skills/wiki isn't generating science code — but run it manually before testing any
generated script.

### Code gate (always on, version-independent)

The version-check only compares the installed stack to the baseline; it never looks at the
code you generate. That left a real gap: with the installed stack *matching* the baseline,
sessions still crashed on `al.FitImagingPlotter(...)` and
`from autoarray.structures.arrays.kernel_2d import Kernel2D` — symbols written from training
memory that were renamed/removed long ago. A clean version-check reported nothing.

So a `PreToolUse` hook (`.claude/hooks/validate_pyauto_code.py`, wired in
`.claude/settings.json`) now validates **every Bash command that runs Python** before it
executes: it extracts the `-c` snippet and any `.py` file arguments, resolves each
alias-rooted symbol (`al.`, `aa.`, `aplt.`, `autoarray.` …) against the *installed* library,
and **blocks** the call if any symbol does not exist — returning the stale symbol so you
re-ground against the live API. Commands with no PyAuto* symbol pay zero cost (fast allow).

You can run the same check by hand on a snippet or file:

```bash
python work/audit_skill_apis.py --code "import autolens as al; al.FitImagingPlotter"   # exit 2
python work/audit_skill_apis.py --file work/my_script.py                                # exit 0/2
```

When the gate blocks you, **do not guess a replacement** — grep `skills/` for the task
(e.g. `al_load_results.md` uses `aplt.subplot_fit_imaging(fit=fit)`) or introspect `dir()`
of the live module, then re-run. The fuzzy "closest live names" hint is a guess, not a
verified rename. Escape hatch for intentional pre-refactor/debugging work:
`PYAUTO_SKIP_API_GATE=1`. The same gate is mirrored at the `PyAutoLabs` monorepo level (its
`.claude/settings.json` invokes this very script), so it protects dev sessions too — not
just clones of this assistant.

## Maintainer mode

The First-interaction protocol above assumes the user is a **lensing scientist**
using the assistant. When the user is instead a **maintainer of the assistant
itself** (editing CLAUDE.md, evolving skills, refactoring the wiki schema), the
protocol gets in the way: profile capture is irrelevant, newcomer-mode defaults
waste tokens, and auto-commits (see "Commit cadence" below) collide with the
maintainer's own commit cadence.

**Sentinel file.** On session start, check whether `.maintainer` exists at the
repo root. If it does, the agent is in maintainer mode for this session.

```bash
# Toggle on:  touch .maintainer
# Toggle off: rm .maintainer
```

`.maintainer` is gitignored — it never leaves your machine, never propagates to
forks, never enters CI.

**What changes in maintainer mode:**

- **Skip the profile.md read / create.** A maintainer isn't a lensing user; the
  file is irrelevant.
- **Skip newcomer-mode defaults.** The maintainer is presumed fluent in PyAutoLens
  and the assistant's design. Resource routing in `_style.md` still applies if the
  maintainer asks a learn-this question, but it is not the default lens.
- **Skip auto-commit** (per "Commit cadence" below). The maintainer drives commits.
- **Skill activations still work**, but `wiki/project/YYYY-MM-DD-*.md` entries
  are not offered — `wiki/project/` is for the user's science, not for assistant
  maintenance.

**What does not change.** The bulk-edit safety rule, the never-rewrite-history
rule, source-of-truth resolution, and every other agent-safety convention apply
unchanged.

## External resources

Three external resources sit alongside this repo and inform the way you cite material:

- **HowToLens** ([github.com/PyAutoLabs/HowToLens](https://github.com/PyAutoLabs/HowToLens))
  — student-aimed pedagogy from first principles. Lead with this for lensing
  newcomers.
- **PyAutoLens RTD** ([pyautolens.readthedocs.io](https://pyautolens.readthedocs.io/en/latest/))
  — canonical PyAutoLens docs: overview series, feature tour, API. Mixed audience.
- **`autolens_workspace`** ([github.com/Jammy2211/autolens_workspace](https://github.com/Jammy2211/autolens_workspace))
  — production-style example scripts per science case. Lead with this for users
  fluent in lensing.

Per-resource indexes with summaries and URLs live in
[`wiki/core/external/`](./wiki/core/external/index.md). Per-skill citation rows live
in [`wiki/core/external/skill_citation_map.md`](./wiki/core/external/skill_citation_map.md)
and are the source of every `al_*` skill's `## Further reading` block. The
audience-routing matrix lives in `skills/_style.md` "Adaptive depth".

## Wiki layout — three sub-wikis

The wiki is split into three independently maintained sub-wikis:

- **`wiki/core/`** — curated reference for the PyAuto\* stack, derived from the source
  repos listed in `sources.yaml`. Refreshed by the `al_update_wiki` skill against pinned
  source commits. Do not edit ad-hoc; treat as read-only unless you're running the update
  skill.
- **`wiki/literature/`** — broad strong-lensing scientific reference (concepts, entities,
  per-paper bibliographies). Has its own schema in
  [`wiki/literature/CLAUDE.md`](./wiki/literature/CLAUDE.md), uses `[[wiki-link]]`
  cross-references, and is compiled from PDFs typically kept outside this repo. Extend it
  when a new paper is read; follow the schema in its CLAUDE.md.
- **`wiki/project/`** — a running journal of what *this clone* has done: decisions,
  experiments, results, blockers. Two pieces live here:
  - `profile.md` — one living record of who the user is and what they're doing
    (created on demand from `_profile_template.md`; see "First-interaction
    protocol" above).
  - Dated entries `YYYY-MM-DD-<slug>.md` following `wiki/project/_template.md`.
    When you produce a non-trivial script via a skill, **offer (default-yes) to add
    an entry** covering (a) domain motivation, (b) statistical motivation, (c)
    implementation choice. Cross-link concepts and named profiles/models into
    `wiki/core/` and `wiki/literature/` using `[[wiki-link]]` slugs (e.g.
    `[[Sersic1968]]`, `[[NavarroFrenkWhite1996]]`, `[[mass-sheet-degeneracy]]`).
    See `skills/_style.md` property #5 for the full rule.

When a skill references "the wiki", it means `wiki/core/` unless it explicitly names
`literature/` or `project/`.

## Source-of-truth resolution

The PyAuto\* libraries live in **separate repos** listed in [`sources.yaml`](./sources.yaml).
Any time you cite source code, you must:

- Use the **project name + path relative to that project's repo root**:
  `PyAutoFit:autofit/non_linear/search/nest/nautilus.py`. Never embed an absolute local path
  like `/Users/other/...`.
- For URLs, derive the link from `sources.yaml` (e.g.
  `https://github.com/rhayes777/PyAutoFit/blob/main/autofit/non_linear/search/nest/nautilus.py`).
- If you need to actually *read* source code, the source repos may or may not be cloned
  locally yet. To check:

  ```bash
  # Replace <project> with the import name (autoconf, autoarray, autofit, autogalaxy, autolens).
  python -c "import <project>, pathlib, inspect; print(pathlib.Path(inspect.getfile(<project>)).parent)"
  ```

  If the import works, read from the installed-package location. If it doesn't, clone the
  repo's git URL (from `sources.yaml`) into a temporary working directory under
  `./sources/<project>/` (this path is gitignored) and read from there.

This rule is the reason the workspace is portable. Anyone who clones this assistant onto a
new machine can resolve every reference without having seen your home directory.

## Skill introspection — how to answer "what can you do?"

Two paths:

- **Fast:** read `skills/README.md`. It lists every skill with a one-line summary. Quote
  the relevant subset back to the user.
- **Search:** for a topical question (*"can you fit interferometer data?"*), grep the
  frontmatter `description:` field of `skills/*.md` and surface matching skills.

Skills whose name begins with an underscore (`_style.md`, `_bootstrap_skill.md`) are
**meta-skills** for authoring/maintaining the workspace itself. Don't surface them when
answering science questions; do read them when extending the workspace.

## Skill invocation — how to do a task

When the user asks for something a skill already covers:

1. Read the skill file end-to-end.
2. Follow its Orient → Ask → Branch → Combine arc (defined in `skills/_style.md`).
3. Produce Python where the skill calls for it. Agent-generated exploration scripts go to
   `./work/` (gitignored). **Never write into `output/` or `sources/`**.
   Persistent project pipelines belong in `scripts/` and are maintained by the user, not
   replaced wholesale.
4. If the skill points at a wiki page for context, read that page before writing code.

## Skill bootstrap — when the user asks for something new

If the user wants a capability and no existing skill fits, follow the protocol in
[`skills/_bootstrap_skill.md`](./skills/_bootstrap_skill.md). Summary:

1. Confirm the scope with the user before writing anything.
2. Read `skills/_style.md` so the new skill matches the house style.
3. Identify which source repos are needed via `sources.yaml`. Clone any that aren't already
   accessible (locally or via `pip` install).
4. **Read inside the cloned repos** to derive the API. Never guess.
5. Draft the new skill at `skills/<name>.md`. Lensing-API skills get the `al_` prefix;
   project-workflow skills (assistant maintenance, repo-level operations) get a plain
   kebab-case name like `init-slam.md` or `start-new-project.md`. Cite source code as
   `<Project>:<path>`.
6. If the new skill needs wiki content that doesn't exist, draft a `wiki/core/` page in the
   same pass so the skill has somewhere to link.
7. Add an entry to `skills/README.md` and create a `.claude/skills/<name>.md` symlink
   pointing to `../../skills/<name>.md`.
8. Verify by writing and running the script the skill produces (with `PYAUTO_TEST_MODE=1`
   for searches; see Sandbox).

## Wiki updates

The `al_update_wiki` skill walks all `wiki/core/` pages, checks the
`sources.pinned_commit` frontmatter against the current HEAD of each source repo, and
rewrites stale sections. Use it whenever the user reports an API has changed, or when they
explicitly ask for a wiki refresh. **Do not** rewrite `wiki/core/` pages opportunistically
as part of unrelated work.

`wiki/project/` is the opposite: append-only and edited by you in the course of normal
work, using `wiki/project/_template.md` as the entry shape.

## Commit cadence during user work

When the session is **not** in maintainer mode (see above), the agent commits at
natural checkpoints rather than waiting for the user to ask. A checkpoint is one
coherent unit of work — a script produced + its `wiki/project/` entry written, a
paper ingested via `al_ingest_paper`, a wiki refresh completed via `al_update_wiki`.

The rules:

- **Announce before committing.** One short line: *"I'm about to commit `<files>`
  with message `<subject>`."* The user can interrupt.
- **Subject format** follows the repo's conventional-commit history (verify with
  `git log --oneline`): `feat:`, `fix:`, `docs:`, `chore:`. The body explains the
  *why*, not the *what*.
- **One checkpoint = one commit.** Don't bundle unrelated work. If two
  unrelated things landed in the same session, commit them separately.
- **Stage explicitly by file.** Never `git add -A` or `git add .` — the user may
  have unrelated WIP that should stay outside the commit. Add files by name.
- **Never push.** Pushing is always an explicit user action; the agent does not
  push even after committing.
- **Hooks are not skipped.** No `--no-verify`. If a pre-commit hook fails,
  diagnose and fix the underlying issue, then create a *new* commit (per the
  Never-rewrite-history rule).
- **Co-author trailer.** Every agent commit ends with
  `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>` — matches the
  convention established in commit `99bbf03`.

In **maintainer mode** the agent does **not** auto-commit. The maintainer drives
every commit; the agent stages and commits only when the maintainer asks.

If the user is on `main` (or any branch tracked as `origin/HEAD`), the agent
should pause and confirm before committing rather than assuming the user
wants commits landing directly there.

## Conventions

- **Standard imports** for any Python you write here:
  ```python
  import autofit as af
  import autolens as al
  import autolens.plot as aplt
  ```
- **Generated script style.** Every `.py` you save (to `work/` or `scripts/`) uses the
  PyAutoLens **workspace** style, not banner comments. The module opens with a single
  docstring — a title underlined with `=`, a short orientation, then a `__Contents__`
  list — and each logical section is introduced by a `"""__Section__"""` narrative
  docstring (carrying the physics/inference framing and any `<Project>:<path>` citations)
  rather than `# ---` banners or `# source:` lines. This keeps the science inline and
  makes scripts mechanically notebook-convertible. Canonical example:
  `autolens_workspace:scripts/imaging/start_here.py`; full spec and a before/after example
  in [`skills/_style.md`](./skills/_style.md) "Generated script style". Example shape:
  ```python
  """
  Lens Model: HST Imaging
  =======================

  Fit a galaxy-scale strong lens: load the data, compose an SIE + shear model, fit it.

  __Contents__

  - **Dataset:** Load imaging, apply the mask.
  - **Model:** Compose the lens and source galaxies.
  - **Fit:** Run the search and inspect the result.
  """

  """
  __Dataset__

  We load the image, noise-map and PSF via `al.Imaging.from_fits`
  (`PyAutoArray:autoarray/dataset/imaging/dataset.py`). `pixel_scales` converts pixels
  to arcseconds — set it correctly for your instrument.
  """
  dataset = al.Imaging.from_fits(...)
  ```
- **Agent working directory**: `./work/`. Python scripts and Markdown notes
  there are **committed** alongside the `wiki/project/` entry that describes
  them — they're the most reusable artefact of a session. Plots go to
  `./work/plots/<context>/` and data dumps (FITS / npy / pickle / hdf5) to
  `./work/output/`; both subdirectories are gitignored, as are any top-level
  `work/*.png|pdf|jpg|fits|npy|pkl|hdf5|h5` files.
- **Project working directory** for persistent modeling pipelines: `scripts/` — see Part 2.
- **Output of `search.fit(...)`**: goes under `./output/<dataset>/modeling/<hash>/` by
  default (per PyAutoFit's own conventions).
- **Plot output and path announcement.** Skill-generated plots are saved
  through `aplt.Output(path="work/plots/<context>/", filename=..., format="png")`
  so they persist on disk. The Python recipe `print(...)`s each plot's
  absolute path. After running the script, the agent **quotes the absolute
  path** of every saved plot and offers *"want me to `open <path>`?"* (macOS
  default). Don't just say "plot saved" — the user shouldn't have to guess
  where. One offer per plot, not nagging.

## Sandbox / restricted environments

`numba` and `matplotlib` write caches to the home directory or installed-package
`__pycache__` paths by default. In restricted environments (Codex, sandboxed CI, read-only
filesystems, `/mnt/c/...` imports under WSL) override them:

```bash
NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib python ./work/script.py
```

PyAutoFit ships a short-circuit mode that skips non-linear search sampling, for fast
end-to-end smoke testing:

```bash
PYAUTO_TEST_MODE=1 python ./work/script.py
```

Use `PYAUTO_TEST_MODE=1` whenever you're verifying a script you wrote runs end-to-end and
the user does not need a real posterior. The project's own pipeline scripts in `scripts/`
honour the older `PYAUTOFIT_TEST_MODE=1` variable — see Part 2's Test Runs section.

## Bulk-edit safety

When editing the same region across many skill or wiki files in one pass, **use `Edit`,
not `Write`**, unless you have first read the entire current contents of the target file.
A whole-file `Write` based on a header skim will silently delete every section below the
header. This rule exists because of an actual incident in the sibling `autolens_workspace`
repo where a header-only rewrite wiped ~80% of 17 scripts.

## Never rewrite history

NEVER perform these operations on any repo with a remote:

- `git init` in a directory already tracked by git
- `rm -rf .git && git init`
- Commit with subject "Initial commit", "Fresh start", "Start fresh", "Reset for AI workflow",
  or any equivalent message on a branch with a remote
- `git push --force` to `main` (or any branch tracked as `origin/HEAD`)
- `git filter-repo` / `git filter-branch` on shared branches
- `git rebase -i` rewriting commits already pushed to a shared branch

If the working tree needs a clean state, the **only** correct sequence is:

    git fetch origin
    git reset --hard origin/main
    git clean -fd

This applies to humans and every agent equally. `autolens_assistant` has an `origin`
on GitHub (`PyAutoLabs/autolens_assistant`) — these rules apply to the `main` branch
of this repo as much as to any of the PyAuto\* source repos.

---

# Part 2 — Science-project conventions

These conventions describe how the assistant manages real lens-modelling work
on the user's behalf: dataset layout, HPC submission, sync tooling, modelling
scripts. They apply whether the user is working directly inside this repo or
asking the assistant to spin off a separate science workspace (see "Spinning
up a New Science Workspace" below).

---

## Spinning up a New Science Workspace

Sometimes the user wants a separate workspace for a specific science case (a
survey, a paper, a sample) rather than running everything inside the assistant
repo itself. The new workspace lives outside this repo (e.g. `<NEW_PROJECT>/`).
Use `rsync` to copy the assistant's structure, excluding what isn't needed.

The HPC folder contains one submit script per script type (`submit_imaging`,
`submit_interferometer`) in both `batch_gpu/` and `batch_cpu/`. Use the rsync
exclusions below to copy **only** the submit scripts that match the chosen
SLaM pipeline(s) — exclude everything else.

To run a single dataset as a test, just put one entry in the `datasets=()` array
in the submit script; no separate template file is needed.

### Imaging-only project (most common)

```bash
rsync -av \
  --exclude='scripts/interferometer.py' \
  --exclude='hpc/batch_gpu/submit_interferometer' \
  --exclude='hpc/batch_cpu/submit_interferometer' \
  --exclude='dataset/' \
  --exclude='output/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  <ASSISTANT>/ \
  <NEW_PROJECT>/
```

### Interferometer-only project

```bash
rsync -av \
  --exclude='scripts/imaging.py' \
  --exclude='hpc/batch_gpu/submit_imaging' \
  --exclude='hpc/batch_cpu/submit_imaging' \
  --exclude='dataset/' \
  --exclude='output/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  <ASSISTANT>/ \
  <NEW_PROJECT>/
```

### Multiple data types

Omit the exclusions for any script types you need; keep all others.

### What to always exclude

- `dataset/` — add real datasets separately (see below)
- `output/` — never pre-populate; written by PyAutoFit at runtime
---

## Dataset Handling

### Directory layout

```
dataset/
└── <sample_name>/
    └── <dataset_name>/
        ├── data.fits
        ├── noise_map.fits
        ├── psf.fits
        ├── positions.json
        └── info.json
```

`sample_name` is the survey/batch name (e.g. `slacs`, `bells`).
`dataset_name` is the individual lens name (e.g. `slacs0737+3216`).

### Copying vs symlinking

**Copy** the dataset when the source may be deleted or reorganised (e.g. copying
from a `Results/old_project/dataset/` folder before deleting it).

**Symlink** only when the source is stable and permanent (e.g. a shared NFS mount
on the HPC, or a dedicated raw-data archive that will never move).

```bash
# Copy (preferred for real-data projects that will be archived)
cp -r /path/to/source/slacs  dataset/slacs

# Symlink (only when source is stable)
ln -s /path/to/source/slacs  dataset/slacs
```

---

## info.json Fields

Every dataset directory needs an `info.json`. The imaging script reads all values
via `info.get(key, default)` so fields can be omitted when the default is correct.

| Field | Default | Notes |
|---|---|---|
| `pixel_scale` | `0.05` | Arcsec/pixel. HST ≈ 0.05, Euclid ≈ 0.1 |
| `n_batch` | `50` | Pixelization batch size. Lower for high-res data |
| `mask_radius` | `3.5` | Circular mask radius in arcsec |
| `subhalo_grid_dimensions_arcsec` | `3.0` | Grid search half-width for subhalo pipeline |
| `redshift_lens` | `0.5` | Used by all SLAM stages |
| `redshift_source` | `1.0` | Used by all SLAM stages |

Interferometer datasets additionally support `real_space_shape` ([256,256]) and the
same `mask_radius`.

---

## HPC (`hpc/`)

The `hpc/` directory contains everything needed to submit, sync, and monitor SLURM
jobs on the HPC cluster.

### Directory Structure

```
hpc/
├── batch_gpu/                  # GPU submit scripts + SLURM log dirs
│   ├── submit_imaging          # SLURM batch script for imaging pipeline
│   ├── submit_interferometer   # SLURM batch script for interferometer pipeline
│   ├── submit                  # Generic compatibility submit script kept as a reference
│   ├── output/                 # SLURM stdout logs (*.out)
│   └── error/                  # SLURM stderr logs (*.err)
├── batch_cpu/                  # CPU submit scripts + SLURM log dirs
│   ├── submit_imaging
│   ├── submit_interferometer
│   ├── submit                  # Generic compatibility submit script kept as a reference
│   ├── template                # Single-dataset CPU template kept as a reference
│   ├── output/
│   └── error/
├── sync                        # Bidirectional sync script (local ↔ HPC)
├── sync.conf.example           # Template config for sync
├── sync_jump.conf.example      # Example config for two-hop / relay topologies
├── .gitignore                  # Ignores sync.conf, sync_jump.conf, subhalo/
└── __init__.py
```

### Submit Scripts — GPU vs CPU

Each script type (`imaging`, `interferometer`) has a submit script in both
`batch_gpu/` and `batch_cpu/`. The key differences:

| | GPU (`batch_gpu/`) | CPU (`batch_cpu/`) |
|---|---|---|
| Partition | `--partition=gpu` | `--partition=cpu` |
| GPU | `--gres=gpu:1` | none |
| CPUs | `--cpus-per-task=1` | `--cpus-per-task=4` |
| Memory | `--mem=32gb` | `--mem=64gb` |
| Wall time | `--time=08:00:00` | `-t 18:00:00` |
| JAX platform | (uses GPU by default) | Forces `JAX_PLATFORM_NAME=cpu` |
| Thread pinning | none | Sets `OPENBLAS/MKL/OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK` |
| Echo block | Includes `nvidia-smi` | No `nvidia-smi` |
| Python args | `--sample --dataset` | `--sample --dataset --use_cpu --number_of_cores=$THREADS` |

The generic `batch_gpu/submit`, `batch_cpu/submit`, and `batch_cpu/template`
files are kept as compatibility/reference examples for sites that want a
minimal or custom launcher. For normal use, prefer the typed
`submit_imaging` / `submit_interferometer` scripts.

**CPU scripts set these environment variables** to pin threads and force CPU-only JAX:

```bash
export JAX_PLATFORM_NAME=cpu
export JAX_PLATFORMS=cpu
THREADS=$SLURM_CPUS_PER_TASK
export OPENBLAS_NUM_THREADS=$THREADS
export MKL_NUM_THREADS=$THREADS
export OMP_NUM_THREADS=$THREADS
export VECLIB_MAXIMUM_THREADS=$THREADS
export NUMEXPR_NUM_THREADS=$THREADS
export NPROC=$THREADS
```

### Submit Script Structure

All submit scripts follow the same pattern:

1. **SBATCH headers** — job name, partition, resources, array range, log paths, email
2. **Environment** — `source $PROJECT_PATH/activate.sh` (must set `PROJECT_PATH` before submitting)
3. **Sample** — `sample=<sample_name>` matches subdirectory under `dataset/`
4. **Dataset list** — `datasets=(...)` array, one dataset name per line
5. **Array task selection** — `dataset="${datasets[$SLURM_ARRAY_TASK_ID]}"`
6. **Run** — GPU: `python3 $PROJECT_PATH/scripts/<type>.py --sample=$sample --dataset=$dataset`
   CPU: `python3 $PROJECT_PATH/scripts/<type>.py --sample=$sample --dataset=$dataset --use_cpu --number_of_cores=$THREADS`

### HPC Script Checklist (after copying)

For each script type present in the project (`imaging`, `interferometer`),
update these fields in both `hpc/batch_gpu/submit_<type>` and
`hpc/batch_cpu/submit_<type>`:

1. `#SBATCH -J <job_name>` — descriptive name for the SLURM queue
2. `#SBATCH --array=0-N` — set N = number of datasets minus 1
3. `sample=<sample_name>` — matches the subdirectory under `dataset/`
4. `datasets=(...)` — one dataset name per line, in the same order as the array indices

The GPU submit scripts have `nvidia-smi` in the echo block — leave it in place.

To test a single lens, temporarily set `--array=0-0` and put just that lens in
`datasets=(...)` — no separate template file is needed.

### `hpc/sync` — Bidirectional Project Sync

A single script that handles all transfer and job management between your local
machine and the HPC. Run from the project root or `hpc/` directory.

**Setup:**
```bash
cp hpc/sync.conf.example hpc/sync.conf
# Edit hpc/sync.conf with your HPC host, base path, and project name.
# sync.conf is gitignored — it stays on your local machine only.
```

**Config fields** (`sync.conf`):
- `HPC_HOST` — SSH host alias or `user@hostname`
- `HPC_BASE` — base directory on the HPC (e.g. `/path/to/hpc/scratch`)
- `PROJECT_NAME` — defaults to local folder name if unset

The remote path is `$HPC_HOST:$HPC_BASE/$PROJECT_NAME`.

**Transfer commands:**

| Command | Description |
|---|---|
| `hpc/sync push` | Upload code, config, and data to the HPC |
| `hpc/sync push --no-data` | Upload code only (skip `dataset/`) |
| `hpc/sync pull` | Download SLURM logs then results from the HPC |
| `hpc/sync logs` | Download SLURM output/error logs only (fast, use mid-run) |
| `hpc/sync sync` | Push then pull (default if no command given) |
| `hpc/sync sync --no-data` | Push code only, then pull |
| `hpc/sync push-data-init` | First-time dataset upload via tar pipe (faster for initial large uploads) |
| `hpc/sync pull-full` | Full output download via tar pipe (avoids per-file rsync overhead) |
| `hpc/sync status` | Dry run — show what would transfer without transferring |

**Job commands** (no manual SSH required):

| Command | Description |
|---|---|
| `hpc/sync submit [gpu\|cpu] <script>` | Submit a SLURM job (e.g. `submit gpu submit_imaging`) |
| `hpc/sync push-submit [gpu\|cpu] <script>` | Push code then submit in one step |
| `hpc/sync jobs` | Show queued/running jobs (`squeue`) |
| `hpc/sync sacct` | Show job history and exit codes |
| `hpc/sync cancel <job_id>` | Cancel a job by ID |
| `hpc/sync wait-and-pull [secs]` | Poll until all jobs finish, then pull (default: 60s interval) |

**Inspect commands:**

| Command | Description |
|---|---|
| `hpc/sync tail [gpu\|cpu]` | Stream live SLURM log output (Ctrl+C to stop; default: gpu) |
| `hpc/sync du` | Show remote disk usage |
| `hpc/sync check` | Verify SSH connection and remote paths |
| `hpc/sync clear-logs [gpu\|cpu]` | Delete SLURM output/error log files (local + remote) |

**What gets synced:**

- **Push (code):** `config/`, `hpc/`, `scripts/` + root files (`activate.sh`, `__init__.py`, `README.md`, `LICENSE`). Changed files are updated normally.
- **Push (data):** `dataset/` — uses `--ignore-existing` so FITS files already on the HPC are never re-transferred.
- **Pull (logs):** `hpc/batch_gpu/output/`, `hpc/batch_gpu/error/`, `hpc/batch_cpu/output/`, `hpc/batch_cpu/error/`
- **Pull (results):** `output/` — excludes `search_internal/` (large sampler state not needed locally).
- **Always excluded:** `__pycache__/`, `*.pyc`, `.git/`, `*.egg-info/`, `sync.conf`

**rsync options:** archive mode, compression (skipping FITS/gz/bz2/xz/zst), partial resume, SSH ControlMaster connection reuse.

### `.gitignore`

The `hpc/.gitignore` ignores:
- `subhalo/` — subhalo grid search output (generated at runtime)
- `sync.conf` — local HPC connection config (contains host-specific paths)
- `sync_jump.conf` — local relay / jump-host config

---

## Scripts and info.json

`scripts/imaging.py` and `scripts/interferometer.py` are **not shipped by
default** — they are populated by the [`init-slam`](./skills/init-slam.md)
skill, which copies the right SLaM driver from `autolens_workspace` into
`scripts/`. Once populated, each script reads all dataset-specific values from
`info.json` using `info.get(key, default)` (e.g. `pixel_scale`, `n_batch`,
`mask_radius`, `subhalo_grid_dimensions_arcsec`, `real_space_shape`). Never
hard-code those values in the script body.

---

## Line Endings — Always Unix (LF)

All files in this project **must use Unix line endings (LF, `\n`)**. Windows/DOS
line endings (CRLF, `\r\n`) will break shell scripts and Python files on the HPC.

**When writing or editing any file**, always produce Unix line endings. Never write
`\r\n` line endings.

After creating or copying files, verify and convert if needed:

```bash
# Check for DOS line endings
file hpc/batch_gpu/submit_imaging   # should say "ASCII text", not "CRLF"

# Convert a single file
dos2unix hpc/batch_gpu/submit_imaging

# Convert all shell scripts and Python files in the project
find . -type f \( -name "*.py" -o -name "*.sh" -o -name "submit*" -o -name "template*" \) \
  | xargs dos2unix
```

---

## Test Runs

A "test run" means running a script with `PYAUTOFIT_TEST_MODE=1`, which makes all
non-linear searches complete almost instantly with a trivial number of samples. Use
this to verify the full pipeline executes without errors before submitting to the HPC.

> **Prerequisite:** the typed scripts (`scripts/imaging.py`,
> `scripts/interferometer.py`) are populated by the
> [`init-slam`](./skills/init-slam.md) skill — run it first.

```bash
# Imaging (GPU mode — default)
PYAUTOFIT_TEST_MODE=1 python3 scripts/imaging.py --sample=<sample> --dataset=<dataset>

# Imaging (CPU mode — disables JAX, enables multicore Nautilus)
PYAUTOFIT_TEST_MODE=1 python3 scripts/imaging.py --sample=<sample> --dataset=<dataset> --use_cpu --number_of_cores=4

# Interferometer
PYAUTOFIT_TEST_MODE=1 python3 scripts/interferometer.py --sample=<sample> --dataset=<dataset>
```

`PYAUTOFIT_TEST_MODE=1` (project scripts) and `PYAUTO_TEST_MODE=1` (agent-generated
scripts in `work/`) are equivalent short-circuit modes — use whichever the script you're
running already supports.

Example datasets for each script type live at:
- Imaging: `dataset/sample_imaging/example_imaging/`
- Interferometer: `dataset/sample_interferometer/example_interferometer/`

---

## Bash Project Alias

Every new project gets a shell function in `~/.bashrc` that activates the venv and
`cd`s into the project directory. Add it immediately after creating the project,
grouped with the other `Project*` functions:

```bash
Project<ProjectName>() {
  source ~/venv/PyAuto/bin/activate
  cd <NEW_PROJECT>
}
```

Use the `PyAuto` venv unless the project requires a different one.

---

## Modeling Scripts (`scripts/`)

The `scripts/` folder holds the project's persistent modeling pipelines (one per
data type: `imaging.py`, `interferometer.py`). A fresh clone ships only
`scripts/template.py` — the typed scripts are populated by the `init-slam` skill
([`skills/init-slam.md`](./skills/init-slam.md)), which selects and copies the
appropriate SLaM pipeline script(s) from `autolens_workspace` into `scripts/`.
The skill presents categorized options, copies the chosen script(s), and
creates `scripts/slam_claude.md` with full SLaM context for future AI sessions.

For quick exploration scripts that don't belong to the pipeline, write to `work/`
instead (gitignored, agent scratch space).

**Live visualization.** When a user runs their first model-fit, offer to enable
`live_visual_update=True` on the search (e.g. `af.Nautilus(..., live_visual_update=True)`).
This opens a matplotlib window (scripts) or refreshes the Jupyter cell (notebooks)
with a 6-panel quick-update subplot every `iterations_per_quick_update` iterations,
so the user can watch the fit converge in real time. It's off by default — mention
it once when they first set up a search, don't repeat on subsequent fits.

---

## Typical New-Workspace Workflow

1. `rsync` from the assistant (with appropriate exclusions)
2. **Run the `init-slam` skill** to select and copy SLaM pipeline script(s) into `scripts/`
3. Copy or symlink the dataset into `dataset/<sample_name>/`
4. Verify every lens has an `info.json` with at least `pixel_scale` and `n_batch`
   (or confirm the defaults in the populated `scripts/imaging.py` are correct
   for the instrument)
5. Update `hpc/batch_gpu/submit_<type>` and `hpc/batch_cpu/submit_<type>` for each
   chosen script type: job name, `--array`, `sample=`, `datasets=(...)`
6. **Run `dos2unix` on all shell scripts and Python files** to ensure Unix line endings
7. **Add a `Project<Name>()` function to `~/.bashrc`** (see Bash Project Alias above)
8. Test locally on one lens before submitting the full array (requires step 2
   to have populated the typed script):
   ```bash
   python3 scripts/imaging.py --sample=<sample> --dataset=<one_lens>
   ```
