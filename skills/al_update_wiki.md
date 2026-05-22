---
name: al_update_wiki
description: Refresh wiki/ pages whose pinned source commits have moved, by re-reading the relevant source files from the PyAuto* repos and rewriting stale sections. Also surfaces newly added public APIs (new classes / functions in __init__.py) so the user can decide whether they warrant new wiki pages. Use whenever the user reports an API change, after pulling fresh source repos, or on a manual refresh cadence. Do NOT run opportunistically as part of unrelated work — the diff should be reviewable.
---

# Updating the wiki from the source repos

The wiki is the content layer of the workspace — every page documents one slice of the
PyAuto\* API (light profiles, mass profiles, non-linear searches, configuration, etc.).
Each page pins the source commits it derives from, so we can detect when it's gone
stale. This skill walks every page, diffs its pinned sources against current HEAD, and
rewrites the sections that have drifted.

The update is a **curated agent task**, not an automated converter. We hand-write wiki
prose; the source diffs are inputs we read and judge against. Auto-generated docstring
dumps go in the libraries' own docs/ folders — that's not what this wiki is for.

Before starting, confirm with the user:

- Which source repos to update against — all five, or a subset?
- Whether to update against `main` of each repo, or a tagged release.
- Whether to commit changes incrementally per-page or in one batch at the end.

## Orient — what a wiki page commits to

Every wiki page starts with frontmatter that looks like this:

```yaml
---
title: Non-linear searches
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/search/nest/nautilus.py
      - autofit/non_linear/search/nest/dynesty.py
      - autofit/non_linear/search/mcmc/emcee.py
      - autofit/non_linear/search/mle/bfgs.py
      - autofit/non_linear/search/mle/pyswarms.py
    pinned_commit: <sha-or-tag>
last_updated: 2026-05-22
---
```

The two fields that matter for this skill:

- **`sources`** — every source file this page derives from. If any of these change
  between `pinned_commit` and current HEAD, the page may be stale.
- **`pinned_commit`** — the commit the page was last written against. After a successful
  update, bump this to the new HEAD.

## Ask — scope of the refresh

Ask the user once before doing work:

- *"Refresh against `main` of all five repos, or just the one whose API moved?"*
- *"Should I bump pinned commits for pages whose sources actually changed, or for every
  page touched (including those whose diffs turn out to be cosmetic)?"*

A targeted refresh ("PyAutoFit only, since they renamed `SamplesNest` to `SamplesNested`")
beats a sweep ("rebuild everything"). Sweeps are for the initial wiki seed; for ongoing
maintenance, narrow.

## Branch — the per-page update loop

For each wiki page in scope:

### 1. Resolve the source repos

Read the page's `sources` frontmatter. For each project, locate the repo:

- If installed (`python -c "import <project>, pathlib, inspect; print(pathlib.Path(inspect.getfile(<project>)).parent)"` works), read from the install location.
- Else, ensure the repo is cloned under `./sources/<project>/` (clone if not present
  using the URL from [`../sources.yaml`](../sources.yaml)).

### 2. Diff the sources

For each path listed in `sources[i].paths`:

```bash
git -C sources/<project> log --oneline <pinned_commit>..HEAD -- <path>
git -C sources/<project> diff <pinned_commit>..HEAD -- <path>
```

If both are empty, the file is unchanged. If only the log is non-empty but the diff is
whitespace/import-shuffles, treat as unchanged. If the diff has real semantic content,
the page is stale.

### 3. Read the changed file and rewrite the affected section

Open the source file at current HEAD. Identify which wiki-page sections depend on it
(usually obvious from section headings). Rewrite only those sections. Do not rewrite
unaffected prose just because the page was touched — small, reviewable diffs.

When rewriting:

- Cite source code as `<Project>:<path>` (e.g. `PyAutoFit:autofit/non_linear/search/nest/nautilus.py`).
- Update tables of classes / functions / parameters to match what's actually exported.
- Add new entries when the source has new public items in `__all__` or top-level
  imports.

### 4. Bump the pinned commit

After rewriting, set `pinned_commit` in the frontmatter to the new HEAD of the relevant
repo. Update `last_updated` to today's date.

```bash
git -C sources/PyAutoFit rev-parse HEAD
```

### 5. Surface new APIs the user might want a page for

Compare the `__all__` / top-level imports of each source package between the old pinned
commit and HEAD. For each new class / function:

- If it fits an existing wiki page, add it there.
- If it doesn't, list it to the user at the end of the run:
  > "I noticed `PyAutoFit` exported `WhiskeredSearch` (new) and `MultiNest` (deprecated).
  > The former probably wants a row in `wiki/core/api/searches.md`; want me to draft one?"

The user decides whether to extend the wiki; don't write new pages without confirmation.

## Combine — after the refresh

Once all in-scope pages are updated:

1. `git diff wiki/` — show the user the rewritten pages.
2. Run the verification scripts in any skill whose wiki page changed (e.g. if you
   rewrote `wiki/core/api/searches.md`, run `work/verify_environment.py` plus a smoke test of
   `al_run_search`).
3. Commit either incrementally (one page per commit, per the user's earlier choice) or
   in a single batch (`git commit -m "wiki: refresh against <project>@<short-sha>"`).

## When NOT to invoke this skill

- During an unrelated user task. Don't sneak a wiki refresh into a feature change.
- When you've only read part of the source. Always read the full diff of each
  `sources[i].paths` entry before deciding the page is up to date.
- When the source has been refactored but you don't yet understand the new shape. Ask
  the user for clarification before rewriting in confused terms.

## Agent procedural checklist

1. Confirm scope with the user (which repos, which pages, commit cadence).
2. For each in-scope wiki page:
   a. Read its frontmatter sources + pinned commit.
   b. Resolve source repos (install or clone via `sources.yaml`).
   c. Diff each listed source path against `pinned_commit`.
   d. If meaningful diff: read the new source, rewrite only the affected sections of the
      page.
   e. Bump `pinned_commit` and `last_updated`.
3. After the loop, compare `__all__` / top-level exports for new APIs not yet covered.
   List them to the user; don't write new pages unilaterally.
4. Show the diff. Commit on the user's chosen cadence.
