---
name: al_audit_skill_apis
description: Verify every PyAuto* API symbol cited in skills/, wiki/core/api+stack/, and generated scripts (scripts/) resolves in the currently installed stack. Reports stale references (renamed, moved, or removed) with suggested replacements drawn from string-similarity and a cross-module search. Also owns the API version baseline (`wiki/core/api_audit_baseline.json`) that pins the workspace to an autolens version: `--write-baseline` records the installed versions + public-API-surface hash, and `--check-version` (the cheap session-start drift-check) flags when the installed stack has moved. Pairs with `al_update_wiki` (which detects prose drift via pinned source commits) — this skill closes the complementary gap that skills have no pinned commits and that wiki pages can name symbols that no longer exist. Run when a user reports an API error, after a PyAuto* upgrade, or on a manual cadence; the helper script `autoassistant/audit_skill_apis.py` does the mechanical pass and this skill drives interpretation and curates fixes.
---

# Auditing skill + wiki API references against the installed stack

Skills cite a lot of PyAuto\* symbols — class names, search algorithms, profiles, the
plot API — and the wiki cites more, in API tables and prose. Both can drift silently
when the underlying libraries rename, move, or remove things. `al_update_wiki`
catches *prose* drift (it diffs pinned source files), but it doesn't actually try to
import the symbols those pages name. And skills have no pinned commits at all.

This skill is the missing check: import the libraries, walk every cited symbol with
`getattr`, and surface the ones that don't resolve. The mechanical pass is in
`autoassistant/audit_skill_apis.py`; the skill is the curated agent task on top of it.

Like `al_update_wiki`, the philosophy is **curate, don't auto-rewrite**. The script
produces a report; the agent reads it, proposes fixes per file with the user, and edits
deliberately. A blind sed-replace over the skill tree would lose nuance — a renamed
PSF constructor might map to a different class entirely (e.g. an old `Kernel2D` helper
moving onto `Convolver`), and the script's suggestions are heuristic. The audit
answers *what's broken*; the agent + user answer *what's right*.

Before starting, confirm with the user:

- Which scope: **skills only**, **wiki only** (`wiki/core/api/` + `wiki/core/stack/`),
  or **all**.
- Whether to apply fixes in this session or just produce the report for a later pass.
- Whether the project venv is active (the libraries must be importable — see Orient
  step 1 below).

## Orient — the audit pipeline

### 1. Activate the env and confirm versions

The libraries need to be importable. The default `python` on PATH typically isn't the
one with the PyAuto\* stack — source the project's `activate.sh` first.

```bash
source activate.sh
python -c "import autoconf, autoarray, autofit, autogalaxy, autolens; \
print({m.__name__: getattr(m, '__version__', '?') for m in [autoconf, autoarray, autofit, autogalaxy, autolens]})"
```

If any of those imports fail, stop and route the user to
[`al_setup_environment.md`](./al_setup_environment.md). Don't audit against a
half-installed stack — it produces a flood of false-positive `import_failed` rows.

### 2. Run the audit script

```bash
python autoassistant/audit_skill_apis.py --scope all
```

Use `--scope skills`, `--scope wiki`, or `--scope scripts` to narrow; `--scope all`
(default) covers skills + wiki/core/api+stack + generated `scripts/` `.py` files.
The **scripts scope** is what catches stale symbols in generated pipelines and exploration
scripts — the place an old removed PyAutoLens symbol actually executes — and it skips this repo's
own committed tooling (`audit_skill_apis.py`, `refresh_api_docs.py`). The report lands at
`autoassistant/audit/skill_api_audit_<YYYY-MM-DD>.md` and is **gitignored** — only the script is
committed. Exit code is non-zero when the report contains misses; you can chain
`python autoassistant/audit_skill_apis.py && echo clean || echo drift` in shell loops.

### 3. Version baseline + drift-check

This workspace is pinned to an autolens version via `wiki/core/api_audit_baseline.json`
(per-module `__version__` + a hash of each module's public `dir()`). Two commands manage
it:

```bash
# Cheap drift-check — compares the installed stack to the committed baseline.
# No Markdown scan; safe to run at session start (AGENTS.md "Session start").
python autoassistant/audit_skill_apis.py --check-version

# Re-pin: snapshot the installed stack into the baseline after a deliberate, audited upgrade.
python autoassistant/audit_skill_apis.py --write-baseline
```

The workflow is: `--check-version` flags that the installed autolens moved → run the full
`--scope all` audit to find what broke → fix the references (per the Branch section below)
→ `--write-baseline` to re-pin once the audit is clean. **Only re-pin after fixing**, never
to silence a red drift-check on a stack you haven't audited. Because a wiki refresh
(`al_update_wiki` / `al_refresh_api_docs`) pulls from upstream source, follow either with
`--check-version` so any newly-introduced drift surfaces immediately.

The wiki documents only the **current** API — fix stale references in place and re-pin;
don't add `old → new` migration tables (they grow without bound and are themselves a drift
surface, since they name removed symbols).

## Ask — narrow the scope before fixing

A complete audit may surface ten or more misses. Don't try to fix all of them in one
push. Ask the user how they want to slice the work:

- *"Fix the skill that triggered this audit first (`al_simulate_dataset`), then sweep
  the rest?"*
- *"Group fixes by library — all the PyAutoArray-related drift in one pass, all the
  PyAutoFit drift in another?"*
- *"One file per commit, or batch?"*

The audit is meant to be re-run after every fix to confirm the count shrinks — that's
how you know each edit actually resolved its target row.

## Branch — fixing one entry

For each row in the report:

### 1. Read the row in context

The report tells you `symbol`, the deepest object that resolved, the suggested
replacements, and the file + context (`code` vs `prose`). Open the cited file and
locate the actual occurrence — there may be more than one, and the surrounding
sentences matter for choosing the right replacement.

### 2. Confirm the replacement against source

Suggestions are heuristic (string-similarity + cross-module search). Don't trust them
blindly:

```bash
# Look up the suggested replacement.
python -c "import autolens as al; help(al.Convolver.from_gaussian)" | head -40
# Or read the source directly — sources.yaml has the URL per project.
```

If the suggestion looks wrong, search the installed library for what's actually there:

```bash
python -c "
import autolens as al
import inspect, pkgutil
for name in dir(al):
    obj = getattr(al, name, None)
    if obj is not None and hasattr(obj, 'from_gaussian'):
        print(name, '->', obj.from_gaussian)
"
```

Cite the new symbol's defining file using the `<Project>:<path>` form (see
`_style.md` "Source citations"), looked up via `inspect.getfile(...)`.

### 3. Edit the skill or wiki file

Replace the symbol in place. If the rename is purely cosmetic (e.g. `SamplesNest` →
`SamplesNested`), one edit is enough. If the API shape changed — different argument
order, a class split into two — the surrounding code recipe likely needs rewriting too,
not just the symbol. Read the new symbol's signature before editing.

For wiki/core/api pages: a single-symbol rename can be patched in place. A whole-section
rewrite is `al_update_wiki`'s job — hand it off rather than doing partial section
rewrites here.

### 4. Re-run the audit; expect the row to disappear

```bash
python autoassistant/audit_skill_apis.py --scope all
```

If the row is still there, the edit didn't land where you thought. If new rows
appeared, the fix introduced new drift — common when the new API has a different
shape than the old one.

## Combine — when to hand off

- **Whole-section wiki rewrites** → [`al_update_wiki.md`](./al_update_wiki.md). That
  skill diffs pinned source commits and rewrites prose accordingly; it's the right
  tool when the change is more than a symbol rename.
- **Missing libraries / import failures** → [`al_setup_environment.md`](./al_setup_environment.md).
- **New skill needed** because the new API requires a workflow the existing skills
  don't cover → [`_bootstrap_skill.md`](./_bootstrap_skill.md).

After the audit reaches zero misses, run a smoke test of any skill whose code recipe
was rewritten:

```bash
PYAUTO_TEST_MODE=1 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/<the_script_the_skill_produces>.py
```

A re-run with zero misses + a successful smoke test is the signal the audit is
complete.

## When NOT to invoke this skill

- During an unrelated user task — like `al_update_wiki`, this should not be sneaked
  into a feature commit. The audit's value is its reviewable diff.
- When the libraries aren't installed. The report will be all `import_failed` rows,
  which isn't actionable.
- When the user wants prose drift fixed (rewording, restructuring) — that's the wiki
  refresh, not this.

## Agent procedural checklist

1. Confirm scope (skills / wiki / scripts / all) and whether to apply fixes now.
2. `source activate.sh`; verify all five PyAuto\* libraries import.
3. `python autoassistant/audit_skill_apis.py --check-version` — is the installed stack still on the
   pinned baseline? If it drifted, that's likely *why* you're here.
4. `python autoassistant/audit_skill_apis.py --scope <scope>`.
5. Read the report in `autoassistant/audit/`.
6. For each miss: read the file, confirm the replacement against the installed source,
   edit, re-run the audit to verify.
7. Hand off any whole-section wiki rewrites to `al_update_wiki`.
8. Once the audit is clean against a deliberately upgraded stack, re-pin:
   `python autoassistant/audit_skill_apis.py --write-baseline` (commit the updated
   `wiki/core/api_audit_baseline.json`).
7. Smoke-test affected scripts with `PYAUTO_TEST_MODE=1`.
8. Commit per the cadence the user picked (one file per commit, or batched).
