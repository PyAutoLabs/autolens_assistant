---
name: al_refresh_api_docs
description: Run a full workspace-maintenance pass to bring skill recipes, wiki API pages, and other PyAuto* references back into line with the current installed stack and source repos. This is the umbrella entry point when the user wants "make the docs current again" rather than only "check whether this symbol still exists" or only "refresh this wiki page". It orchestrates `al_audit_skill_apis` (symbol-resolution drift), `al_update_wiki` (pinned-source prose drift), and any follow-up edits to `skills/*.md`. Use after a PyAuto* upgrade, after pulling fresh source repos, or on a deliberate maintenance cadence. Do not use for unrelated feature work.
---

# Refreshing the workspace against the current PyAuto* API

This skill is the maintenance umbrella for the workspace's documentation layer. The
workspace has three places API drift can show up: symbol references inside `skills/`,
curated prose inside `wiki/core/`, and the source repos themselves moving beyond the
wiki pages' pinned commits. A clean refresh pass checks all three, then fixes them in a
reviewable order.

This is deliberately broader than [`al_audit_skill_apis`](./al_audit_skill_apis.md)
and [`al_update_wiki`](./al_update_wiki.md), not a replacement for either. The audit
is still the mechanical "does this symbol resolve?" pass; the wiki update is still the
curated "did the source code change enough to rewrite this page?" pass. This skill
strings them together so the user can say "bring the workspace up to date" once.

For background on how skills, wiki pages, and source repos relate, point at
[`wiki/core/stack/overview.md`](../wiki/core/stack/overview.md) and
[`wiki/core/operations/installation.md`](../wiki/core/operations/installation.md).

## Ask

Before you start, confirm three boundaries with the user:

- Scope: **skills only**, **wiki only**, or **all maintenance surfaces**.
- Reference point: audit against the **installed environment** only, or also against
  local source checkouts under `sources/` / current repo clones.
- Cadence: produce a **report only**, or **apply fixes in this session** and commit
  incrementally.

If the user only wants one narrow slice, hand off to the narrower skill directly. Use
this umbrella skill when they want the full maintenance sweep.

## Orient — preflight the maintenance pass

Start from an environment where the PyAuto* stack imports cleanly:

```bash
source activate.sh
python -c "import autoconf, autoarray, autofit, autogalaxy, autolens; \
print({m.__name__: getattr(m, '__version__', '?') for m in [autoconf, autoarray, autofit, autogalaxy, autolens]})"
```

If those imports fail, stop and route the user to
[`al_setup_environment.md`](./al_setup_environment.md). A refresh pass against a broken
env creates noise, not signal.

The helper script below runs the same preflight and then launches the API audit:

```bash
python autoassistant/refresh_api_docs.py --scope all
```

That script is not the whole job. It gives you a repeatable starting point and a report
path; the actual edits remain curated.

## Branch — pass 1: audit symbol drift

Run the symbol-resolution pass first. This tells you where references inside skills and
the API-focused wiki no longer resolve against the installed stack.

```bash
python autoassistant/audit_skill_apis.py --scope all
```

Read the report under `autoassistant/audit/`. For each miss:

- Open the cited skill or wiki file in context.
- Confirm the suggested replacement against installed code or the relevant source repo.
- Patch the local file deliberately; don't bulk-rewrite every match to the same string.

If all misses are inside `skills/*.md`, you may be able to finish the refresh without a
wiki-source diff. If the misses touch `wiki/core/api/` or `wiki/core/stack/`, keep the
audit report open for the next pass.

See [`al_audit_skill_apis.md`](./al_audit_skill_apis.md) for the detailed fix loop.

## Branch — pass 2: refresh wiki pages whose pinned sources moved

Once the symbol audit has told you which pages are suspicious, check whether the wiki's
source pins have moved enough to warrant prose edits.

For each affected wiki page (or every page in scope, if the user asked for a full
sweep), run the pinned-commit diff loop from
[`al_update_wiki.md`](./al_update_wiki.md):

```bash
git -C sources/<project> log --oneline <pinned_commit>..HEAD -- <path>
git -C sources/<project> diff <pinned_commit>..HEAD -- <path>
```

Rewrite only the sections whose source actually changed. After the rewrite:

- bump `pinned_commit`
- bump `last_updated`
- note any newly exported APIs that may need a row or a new page

If the source diff is only cosmetic, leave the prose alone. This skill is about
accuracy, not churn.

## Branch — pass 3: refresh skill recipes and examples

The wiki refresh does not automatically fix procedure drift inside `skills/*.md`. Once
the symbol audit and wiki diff have narrowed the changed surface, sweep the affected
skills directly:

- update code snippets whose constructor names or arguments changed
- update cited source paths in `<Project>:<path>` form
- update cross-links if the underlying wiki page moved or split

When a recipe change is more than a symbol rename, write or update a concrete script in
`scripts/` and run it. For this skill, the default helper is:

```bash
PYAUTO_TEST_MODE=1 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python autoassistant/refresh_api_docs.py --scope all
```

That verifies imports, reruns the audit, and exits non-zero if symbol drift remains.
For any skill whose code recipe you materially changed, also smoke-test the user-facing
script that skill would generate.

## Combine — what "complete" looks like

A full refresh pass is complete when all five are true:

- the PyAuto* stack imports in the target environment
- `autoassistant/audit_skill_apis.py --scope <scope>` reports zero misses
- `autoassistant/audit_skill_apis.py --check-citations` reports zero missing paths
  (symbols and citation paths are independent failure axes — see
  `al_audit_skill_apis` §6)
- every touched wiki page has either an updated `pinned_commit` or an explicit decision
  that the source diff was cosmetic
- any materially changed skill recipe has been smoke-tested with `PYAUTO_TEST_MODE=1`

At that point, show the user the diff grouped by maintenance surface:

- skills
- wiki pages
- helper / verification scripts

Then commit on the cadence they chose.

## When NOT to invoke this skill

- During unrelated feature work. Keep maintenance diffs reviewable.
- When the user only wants one known-broken symbol fixed. Use
  [`al_audit_skill_apis.md`](./al_audit_skill_apis.md) directly.
- When the user already knows the exact wiki page whose pinned source moved. Use
  [`al_update_wiki.md`](./al_update_wiki.md) directly.
- When the environment cannot import the PyAuto* stack.

## Agent procedural checklist

1. Confirm scope, reference point, and whether this is report-only or fix-and-commit.
2. `source activate.sh`; verify all five PyAuto* libraries import.
3. Run `python autoassistant/refresh_api_docs.py --scope <scope>` to do preflight and launch the audit.
4. Read the audit report and fix symbol drift first.
5. For wiki pages in scope, diff each page's pinned sources against the target repo HEAD and rewrite only changed sections.
6. Sweep affected `skills/*.md` recipes and source citations.
7. Re-run `python autoassistant/audit_skill_apis.py --scope <scope>` until it reports zero misses.
8. Smoke-test any materially changed recipes with `PYAUTO_TEST_MODE=1`.
9. Show the grouped diff, then commit on the user's chosen cadence.
