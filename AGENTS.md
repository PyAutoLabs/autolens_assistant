# AGENTS.md — Generic agent instructions for the lenskills workspace

This file is the agent-agnostic version of [`CLAUDE.md`](./CLAUDE.md). Codex, GitHub
Copilot, and any other coding agent should read this; Claude Code should prefer
`CLAUDE.md` (same content, slightly Claude-flavoured).

## The three-layer model

Lenskills is organised into three layers:

1. **Instructions** (this file, `CLAUDE.md`, `README.md`) — meta.
2. **Skills** (`skills/*.md`) — *procedural*. How to do a lensing task. Each skill
   produces or evolves a Python script.
3. **Wiki** (`wiki/**.md`) — *content*. Reference: what a Sersic profile is, which
   non-linear searches exist, how SLaM phases work.

When the user asks *how do I do X*, reach for a skill. When the user asks *what / which /
why*, reach for the wiki. When the user asks to *build something end-to-end*, compose
skills and cite wiki pages.

## First-interaction protocol

The interface is natural-language-first. On session start:

1. **Read `wiki/project/profile.md` if it exists** — it captures the user's lensing /
   PyAutoLens background, current science goal, and data on hand. Use it to calibrate
   depth.
2. **If absent, don't trigger heavy onboarding.** Pick up cues from the conversation.
   Ask **one** disambiguating question if a decision genuinely depends on it.
3. **Create `profile.md` only when the user volunteers something durable.** Copy
   `wiki/project/_profile_template.md`, fill in what's been said, set `last_touched`.
4. **Append incrementally.** Update profile and bump `last_touched` each session. If
   the recorded fact contradicts the user, flag rather than overwrite. If
   `last_touched` is older than ~10 sessions, ask whether anything has changed.

After producing a non-trivial script via a skill, offer (default-yes) to add a
`wiki/project/YYYY-MM-DD-<slug>.md` entry covering (a) domain motivation, (b)
statistical motivation, (c) implementation choice — with `[[wiki-link]]`
cross-references into `wiki/core/` and `wiki/literature/`.

## Maintainer mode

On session start, check for `.maintainer` at the repo root. If present, the
session is template-maintenance work, not user science:

- Skip the profile.md read/create.
- Skip newcomer-mode defaults.
- Skip auto-commit (see "Commit cadence" below) — the maintainer drives commits.
- Skill activations still work, but skip the project-wiki-entry offer.

`.maintainer` is gitignored. Toggle with `touch .maintainer` / `rm .maintainer`.
See `CLAUDE.md` Part 1 for the full rules.

## Commit cadence during user work

When not in maintainer mode, commit at natural checkpoints — a script + its
`wiki/project/` entry, a paper ingestion, a wiki refresh. **Announce the commit
before running it.** Subject lines match the repo's conventional-commit style
(`feat:`, `fix:`, `docs:`, `chore:`). Body explains the *why*. Stage explicitly by
filename — never `git add -A`. Never push. Don't skip hooks. Every commit ends
with `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`. See `CLAUDE.md`
Part 1 for the full rules and the maintainer-mode exception.

## External resources

Three external resources sit alongside this repo. Per-resource indexes with
summaries and URLs live in [`wiki/core/external/`](./wiki/core/external/index.md);
the per-skill citation rows are in
[`wiki/core/external/skill_citation_map.md`](./wiki/core/external/skill_citation_map.md).

- **HowToLens** — student-aimed pedagogy. Lead with this for lensing newcomers.
- **PyAutoLens RTD** — canonical docs. Mixed audience; lead with this for
  PyAutoLens newcomers fluent in lensing.
- **`autolens_workspace`** — production-style examples. Lead with this for returning
  PyAutoLens users.

When citing a workspace script that has also been copied into this fork's `context/`
folder, cite both — the URL for the canonical version and the `context/` path for the
local copy.

## Source-of-truth resolution

The PyAuto\* libraries live in separate repos listed in [`sources.yaml`](./sources.yaml).
Any code reference must use **project name + path relative to that project's repo root**
— e.g. `PyAutoFit:autofit/non_linear/search/nest/nautilus.py`. Never embed an absolute
local path. To read source code:

- Try the installed package first (`python -c "import autofit, pathlib, inspect;
  print(pathlib.Path(inspect.getfile(autofit)).parent)"`).
- If not installed, clone the git URL from `sources.yaml` into `./sources/<project>/`
  (gitignored) and read from there.

## Answering "what can you do?"

Read `skills/README.md` — every skill has a one-line summary there. For a topical
question, grep the frontmatter `description:` of `skills/*.md` and surface matches.

Skills starting with `_` are meta-skills (authoring / maintaining the workspace); don't
surface them when the user asks a science question.

## When a skill exists for the task

1. Read the skill file end-to-end.
2. Follow its Orient → Ask → Branch → Combine arc (see `skills/_style.md`).
3. Produce Python. Save scripts to `./work/` by default — never inside `output/` or
   `sources/`.
4. Read any wiki pages the skill points at before writing code.

## When the user asks for a skill that doesn't exist

Follow the protocol in [`skills/_bootstrap_skill.md`](./skills/_bootstrap_skill.md):

1. Confirm scope with the user.
2. Read `skills/_style.md` for house style.
3. Identify the source repos needed via `sources.yaml`; clone any that aren't accessible.
4. Read the relevant source files inside the cloned repos.
5. Draft `skills/<al_new_name>.md` citing source code as `<Project>:<path>`.
6. Add a wiki page if the skill needs reference content that doesn't exist yet.
7. Update `skills/README.md` and create a `.claude/skills/<al_new_name>.md` symlink.
8. Verify by running the script the skill produces (`PYAUTO_TEST_MODE=1` for searches).

## Conventions

Standard imports for any Python this workspace produces:

```python
import autofit as af
import autolens as al
import autolens.plot as aplt
```

Generated Python scripts and Markdown notes live in `./work/` and are
**committed**. Plots go to `./work/plots/<context>/` and data dumps to
`./work/output/`; both subdirectories are gitignored. Search outputs land in
`./output/` (also gitignored). After a script saves a plot, quote the
absolute path and offer to `open <path>` (macOS). See `CLAUDE.md` Part 1
"Conventions" for the full rule.

## Sandbox environments

```bash
NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib python ./work/script.py
```

For fast smoke testing without real sampling:

```bash
PYAUTO_TEST_MODE=1 python ./work/script.py
```

## Bulk-edit safety

When editing the same region across many files, use targeted edits, not whole-file
rewrites. Whole-file rewrites based on a header skim have silently deleted ~80% of
sibling-workspace scripts in a known incident. Read first, edit narrowly.

## Never rewrite history

NEVER:

- `git init` in a directory already tracked by git
- `rm -rf .git && git init`
- Commit with subjects like "Initial commit", "Fresh start", "Reset for AI workflow" on
  a remote-tracked branch
- `git push --force` to a branch tracked as `origin/HEAD`
- `git filter-repo` / `git filter-branch` on shared branches
- `git rebase -i` rewriting commits already pushed to shared branches

The only correct clean-state sequence is:

    git fetch origin
    git reset --hard origin/main
    git clean -fd
