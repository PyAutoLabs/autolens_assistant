# Maintainer mode

Active when `.maintainer` exists at the repo root (gitignored; `touch .maintainer` /
`rm .maintainer`). The session is **assistant-maintenance** — editing the constitution,
skills, wiki schema, hooks, or infrastructure — not user lensing science. `AGENTS.md`
"Session start" routes here when the sentinel is present.

## What changes

- Skip the `wiki/project/profile.md` read/create and the newcomer-mode defaults.
- Skip the session-start API drift-check by default (run it manually before testing any
  generated script).
- **No auto-commit.** The maintainer drives every commit; stage explicitly, announce, and
  never push.
- Don't offer to add `wiki/project/YYYY-MM-DD-*.md` entries.
- The **source-edit boundary** is lifted: you may edit `wiki/core/`, hooks, and assistant
  infrastructure (that is the point of maintenance work).

## What does NOT change

- Every safety invariant in `AGENTS.md` still applies — in particular the two hard-absolutes
  (the real-data inspection gate and never-rewrite-history), plus bulk-edit safety and the
  `output/` write-ban.
- Commits still end with the `Co-Authored-By: Claude <model> <noreply@anthropic.com>` trailer.

## Maintainer procedures

Use the existing skills, not new docs:

- Authoring or evolving a skill → [`skills/_bootstrap_skill.md`](../skills/_bootstrap_skill.md).
- Regenerating `wiki/core/` against pinned sources → `al_update_wiki`.
- API gate / version baseline → [`skills/al_audit_skill_apis.md`](../skills/al_audit_skill_apis.md).

## Release-time wiki-currency check (two triggers, one check)

The currency rules — symbol audit, idiom deny-list, provenance — live in **exactly one
place**: [`.github/workflows/wiki-currency.yml`](../.github/workflows/wiki-currency.yml) in
this repo, driving `autoassistant/audit_skill_apis.py`. The check versions with the content
it grades, so it must not be reimplemented anywhere else. Two triggers feed that one check:

- **Release (workflow_call).** PyAutoBuild's `release.yml` — the same run that regenerates
  the workspace/howtolens notebooks and the API baseline — invokes `wiki-currency.yml` via
  `uses:`, passing the new `stack_version` and `assistant_ref: main`. It installs that exact
  stack and runs all four checks. On drift the reusable workflow fails; PyAutoBuild's
  dependent `if: failure()` job downloads the `wiki-drift-report` artifact and opens a "wiki
  drift" issue against this repo. **PyAutoBuild only orchestrates and reports — it holds no
  copy of the rules.** (If releases ever move off PyAutoBuild, the `repository_dispatch`/
  `workflow_call` trigger moves to whatever cuts the release; this workflow is unchanged.)
- **Assistant change (pull_request / schedule).** The same workflow runs on every PR and
  weekly against the *currently-released* stack, catching drift a wiki/skill edit introduces
  before it merges.

Ordering matters at release: PyAutoBuild regenerates + commits the API baseline **before**
calling this workflow, so `--check-version` compares the new stack against an already-updated
baseline. When you change the rules, edit them here only; never copy a rule into PyAutoBuild.

## Chat-surface compatibility smoke test

Run these checks after documentation changes are available on the public GitHub repository. Do
not claim a surface is tested merely because its documentation says repository access is
supported.

- **ChatGPT with GitHub access:** provide the repository URL and the bootstrap prompt from
  [`llms.txt`](../llms.txt); ask it to name the exact instruction, skill-index, and wiki files
  it read before answering one installation question and one modelling question.
- **ChatGPT without GitHub access:** attach `llms.txt`, `AGENTS.md`, and one selected skill;
  confirm it states the capability boundary and requests missing local evidence rather than
  pretending to inspect files.
- **Codex web:** connect the repository, ask it to summarize the active `AGENTS.md`
  constraints, then request a read-only plan for a small modelling task. Confirm it grounds the
  plan in the relevant skill and does not make an unrequested edit or pull request.
- **Non-agentic CLI/chat:** provide the same bootstrap and either browsing access or attached
  files; confirm it produces commands for the user to run instead of claiming execution.

Record the surface, date, plan/account context, files successfully loaded, and any limitations.
Plan availability changes, so test results should describe observed behavior rather than promise
that a feature is free for every user.
