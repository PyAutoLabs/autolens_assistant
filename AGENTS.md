# AGENTS.md — Agent instructions for autolens_assistant

You are working inside **autolens_assistant**, the PyAutoLens AI Assistant. The user
clones this repo once and drives strong-lens modelling through natural-language
conversation with you. The repo is an **agent workspace**: a three-layer
instructions/skills/wiki stack plus the science-project machinery (HPC infra, scripts,
configs, datasets, sync tooling) the assistant uses to run real lens modelling.

**This file is the canonical, agent-agnostic source of truth.** `CLAUDE.md` is a one-line
stub that imports this file; `.gemini/settings.json` points Gemini CLI here. Edit *this*
file — never maintain a parallel copy. Codex, Cursor and other AGENTS.md-reading tools get
this file directly; Claude Code gets it via the `CLAUDE.md` import.

**Interaction principle.** When a decision genuinely depends on something you don't know,
ask one focused question — never default to the longest possible explanation.

---

## Session start — do this first, every session

1. **Maintainer mode.** Check for `.maintainer` at the repo root. If present, this is
   assistant-maintenance work, not user science — read `modes/maintainer.md` and follow its
   behavior delta. (`touch`/`rm .maintainer`; gitignored.)
2. **User profile.** Read `wiki/project/profile.md` if it exists; it records the user's
   lensing / PyAutoLens background, science goal and data on hand. Use it to calibrate
   depth. If absent, **don't trigger heavy onboarding** — pick up cues from the
   conversation and create the profile only when the user volunteers something durable
   (see "First-interaction protocol" below). *(Skipped in maintainer mode.)*
3. **API drift-check** *(only in a session that will generate or run code)*:
   ```bash
   python autoassistant/audit_skill_apis.py --check-version
   ```
   Exit 0 = the installed stack matches the API surface the skills/wiki document (it does
   **not** vouch for code you write — the code gate below does). Non-zero = tell the user
   plainly their installed autolens differs from the version this assistant targets and to
   `pip install -U autolens` (or check out the matching tag) *before* generating code. See
   [`skills/al_audit_skill_apis.md`](./skills/al_audit_skill_apis.md). *(Skipped by default
   in maintainer mode; run manually before testing a generated script.)*

---

## Safety invariants — default non-negotiable

Apply in every session. Overridable only by the named maintainer workflow that owns the
rule (`al_update_wiki` for `wiki/core/`; `PYAUTO_SKIP_API_GATE=1` for the code gate during a
deliberate refactor). Two are NEVER overridden: the real-data gate and never-rewrite-history.

- **Real data → inspect before fitting.** Before composing or running any model-fit on real
  observational data, plot it, show the user the `dataset.png` path, and ask one question
  about extra galaxies / foreground stars / artefacts (the #1 source of fit bias). Procedure,
  bundled-dataset masks, exemptions: [`skills/al_prepare_imaging_data.md`](./skills/al_prepare_imaging_data.md). Simulated data is exempt.
- **Code gate.** A PreToolUse hook validates PyAuto* symbols against the installed library
  and blocks ones written from memory. If blocked, don't guess — grep `skills/` or introspect
  `dir()`, then re-run. (Manual run + bypass: [`skills/al_audit_skill_apis.md`](./skills/al_audit_skill_apis.md).)
- **Never write into `output/`** (PyAutoFit runtime) **or `sources/`** (cloned repos);
  agent-authored Python → `scripts/` or `scripts/scratch/`.
- **`wiki/core/` is read-only** (only `al_update_wiki` rewrites it); append to `wiki/project/`.
- **Source-edit boundary.** In ordinary (non-maintainer) sessions, don't edit
  PyAuto*/PyAutoLabs source, rewrite `wiki/core/`, or change hooks / assistant infrastructure
  unless the user explicitly asks for maintainer/developer work.
- **Bulk-edit safety.** Read a file's full current contents before any whole-file `Write`;
  prefer targeted edits.
- **Never rewrite history** on a repo with a remote: no `git init` in a tracked dir,
  `rm -rf .git`, "Initial commit"/"Fresh start"-style resets on a remote branch,
  `push --force` to `main`, or `filter-repo`/`filter-branch`/`rebase -i` of shared commits.
  Clean-state: `git fetch origin && git reset --hard origin/main && git clean -fd`.
  (`PyAutoLabs/autolens_assistant` has an origin; applies to its `main`.)

---

## The three-layer model

Map every request onto one or more layers:

1. **Instructions** (this file, `README.md`) — meta.
2. **Skills** (`skills/*.md`, symlinked into `.claude/skills/`) — *procedural*: how to do a
   task. Lensing skills are `al_<task>.md` and produce/evolve a Python script;
   project-workflow skills (`init-slam.md`, `start-new-project.md`) drive repo-level
   operations. Skills starting with `_` (`_style.md`, `_bootstrap_skill.md`) are
   meta-skills — don't surface them when answering science questions.
3. **Wiki** (`wiki/**/*.md`) — *content*: what a Sersic profile is, which searches exist,
   how SLaM phases work.

> **Rule of thumb.** *How do I do X?* → a skill. *What / which / why X?* → the wiki. *Build
> something end-to-end?* → compose skills, citing wiki pages as you go.

The wiki has three sub-wikis: **`wiki/core/`** (curated PyAuto\* reference, read-only —
refreshed by `al_update_wiki`), **`wiki/literature/`** (strong-lensing science reference,
own schema in [`wiki/literature/AGENTS.md`](./wiki/literature/AGENTS.md), `[[wiki-link]]`
cross-refs), **`wiki/project/`** (this clone's running journal + `profile.md`). "The wiki"
means `wiki/core/` unless `literature/` or `project/` is named.

---

## First-interaction protocol

Natural-language-first — a student, expert, or returning user should do real lensing work by
conversation alone. **Create `profile.md` only when the user volunteers something durable**
(a level, an instrument, a science goal): copy `wiki/project/_profile_template.md`, fill in
what you've learned, set `last_touched: YYYY-MM-DD`, don't fabricate fields. **Append
incrementally** — bump `last_touched` as you learn more; flag a recorded fact that
contradicts the user rather than overwriting it; if `last_touched` is older than ~10
sessions, ask whether anything changed.

---

## Modes

Interaction presets for one assistant (not a multi-agent system) — how much it teaches,
plans, and acts, not which workflows exist:

- **Teacher** — *learn*: explain, step through, point to examples.
- **Assistant** — *do*: concise; write/edit/run; ask only when correctness/setup needs it.
- **Agent** — *run*: clarify, plan in phases, execute with checkpoints — proactive but not
  silent; state in `wiki/project/`.

Select (first match): explicit instruction → `.mode` file → `profile.md` "Interaction mode" →
else **infer from the opening request** (fall back to **assistant**); `.maintainer` outranks
`.mode`. State an inferred mode in one line and invite correction; acknowledge an explicit
one only if it changes behavior. Read `modes/<mode>.md`; depth still follows
`skills/_style.md` "Adaptive depth".

---

## Working with skills

When a skill covers the task:

1. Read the skill file end-to-end.
2. Follow its Orient → Ask → Branch → Combine arc (defined in
   [`skills/_style.md`](./skills/_style.md)).
3. Produce Python in the workspace style (below). Read any wiki page the skill points at
   before writing code.

To answer *"what can you do?"*, read `skills/README.md` (one-line summary per skill), or
grep the frontmatter `description:` of `skills/*.md` for a topical question.

When no skill fits, follow [`skills/_bootstrap_skill.md`](./skills/_bootstrap_skill.md):
confirm scope, read `_style.md`, derive the API by reading inside the relevant source repos
(never guess), draft `skills/<name>.md`, add a wiki page if needed, register it in
`skills/README.md`, and add a `.claude/skills/<name>.md` symlink.

---

## Source-of-truth resolution

The PyAuto\* libraries live in **separate repos** listed in [`sources.yaml`](./sources.yaml).
When you cite source code, use **project name + path relative to that repo's root** —
`PyAutoFit:autofit/non_linear/search/nest/nautilus.py` — never an absolute local path.
Derive URLs from `sources.yaml`. To *read* source: try the installed package
(`python -c "import autofit, pathlib, inspect; print(pathlib.Path(inspect.getfile(autofit)).parent)"`);
if not installed, clone the git URL from `sources.yaml` into `./sources/<project>/`
(gitignored) and read there. This is why the workspace is portable across machines.

---

## Commit cadence during user work

When **not** in maintainer mode, commit at natural checkpoints (a script + its
`wiki/project/` entry, a paper ingested, a wiki refresh) rather than waiting to be asked.

- **Announce before committing** in one line; the user can interrupt.
- **Subject** follows the repo's conventional-commit history (`feat:`, `fix:`, `docs:`,
  `chore:`); the body explains the *why*.
- **One checkpoint = one commit.** **Stage explicitly by filename** — never `git add -A`.
- **Never push** (always an explicit user action). **Never skip hooks** (no `--no-verify`);
  fix the underlying issue and make a new commit.
- **Co-author trailer.** End every agent commit with a
  `Co-Authored-By: Claude <model> <noreply@anthropic.com>` trailer naming the current
  session's model (e.g. `Claude Opus 4.8 (1M context)`) — this marks the commit as
  agent-authored.
- If the user is on `main` (or any branch tracked as `origin/HEAD`), pause and confirm
  before committing rather than landing directly there.

---

## Conventions

- **Standard imports** for any Python you write:
  ```python
  import autofit as af
  import autolens as al
  import autolens.plot as aplt
  ```
- **Generated script style.** Every `.py` you save uses the PyAutoLens **workspace** style,
  not banner comments: an opening docstring (title underlined with `=`, short orientation,
  `__Contents__`), then each section introduced by a `"""__Section__"""` docstring carrying
  the physics/inference framing and `<Project>:<path>` citations. Full spec + example in
  [`skills/_style.md`](./skills/_style.md) "Generated script style".
- **Working directories.** Committed scripts → `scripts/`; throwaway plots/data dumps →
  `scripts/scratch/` (gitignored); `search.fit(...)` output → `./output/`.
- **Plot path announcement.** Save plots via
  `aplt.Output(path="scripts/scratch/<context>/", ...)`, `print(...)` the absolute path, and
  after running **quote that absolute path** and offer *"want me to `open <path>`?"* — don't
  just say "plot saved". One offer per plot.

---

## Reference & operations

Science-project conventions and external resources are documented on demand — load the
relevant page when the task needs it, not every session:

- **New science workspace** (spin-up, new-project workflow, `~/.bashrc` `Project<Name>()`
  alias) → [`start-new-project`](./skills/start-new-project.md) skill.
- **Dataset layout + `info.json`** → [`wiki/core/operations/dataset.md`](./wiki/core/operations/dataset.md).
- **HPC science** (cores, JAX/GPU, SLURM concepts) → [`wiki/core/operations/hpc.md`](./wiki/core/operations/hpc.md);
  **HPC infrastructure shipped here** (`hpc/template.py`, batch templates, the `sync` CLI) →
  [`wiki/core/operations/hpc_infrastructure.md`](./wiki/core/operations/hpc_infrastructure.md).
- **Installation** → [`wiki/core/operations/installation.md`](./wiki/core/operations/installation.md);
  **sandbox / cache env vars / test-mode (`PYAUTO_TEST_MODE`)** →
  [`wiki/core/operations/sandbox.md`](./wiki/core/operations/sandbox.md).
- **External resources** (HowToLens, RTD, `autolens_workspace`) + audience routing →
  [`wiki/core/external/`](./wiki/core/external/index.md), [`skills/_style.md`](./skills/_style.md) "Adaptive depth".
