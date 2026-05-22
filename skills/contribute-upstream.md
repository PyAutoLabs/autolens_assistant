---
name: contribute-upstream
description: Prepare a scoped update from a fork of autolens_base_project and propose it back to the source template. Use this skill when the user says "contribute this back", "open a PR upstream", "suggest this to the base project", or "send this to PyAutoLabs/autolens_base_project". It validates the git remote layout, confirms PR scope, creates or reuses a feature branch, stages only the intended files, commits with the repo's commit conventions, pushes to the user's fork, and opens a draft PR against PyAutoLabs/autolens_base_project.
user-invocable: true
---

# Contribute Upstream

Use this skill when work done in a user's fork should be proposed back to the base template at
`PyAutoLabs/autolens_base_project`.

This is a **project-workflow** skill, not a lensing API skill. The output is a draft pull request
against the upstream template repo, not a Python script.

## Step 1 — Confirm the scope

Before touching git, confirm exactly what belongs in the PR.

- Run `git status --short` and inspect the diff for the candidate files.
- If unrelated user work is present, ask which files belong in this PR.
- Never assume the whole worktree is in scope.
- Never use `git add -A` or `git add .` for this workflow.

If the change naturally splits into more than one concern, recommend separate PRs and ask which one
to prepare first.

## Step 2 — Verify the repository and remotes

Confirm the current repository is `autolens_base_project` and inspect its remotes:

```bash
git remote -v
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name @{u}
```

You need two roles:

- **Upstream target** — the remote that points to `PyAutoLabs/autolens_base_project`.
- **Writable fork** — the user's personal fork, where branches can be pushed.

Prefer the repo convention used in this workspace:

- `origin` = `PyAutoLabs/autolens_base_project`
- `fork` = the user's writable fork

But do **not** hard-code the remote names. Detect the roles from the remote URLs so the workflow
still works if the user kept `origin` as their fork and named upstream `upstream`.

If there is no writable fork remote, stop and tell the user to add one before continuing.

## Step 3 — Check GitHub CLI/auth

This workflow assumes GitHub CLI is available:

```bash
gh --version
gh auth status
```

If `gh` is missing or unauthenticated, stop and tell the user what to fix. Do not proceed with a
half-configured publish flow.

## Step 4 — Choose the branch strategy

Inspect the current branch and its upstream tracking.

- If the user is on `main`, `master`, or a branch tracking the upstream default branch, create a
  new feature branch.
- Use a concise branch name like `codex/<description>` or `docs/<description>`.
- If the user is already on a non-default feature branch that clearly belongs to their fork, stay
  on it unless they ask to branch again.

Never push commits for this workflow directly to the upstream remote.

## Step 5 — Stage and commit safely

Stage only the agreed files, explicitly by name:

```bash
git add README.md skills/README.md skills/contribute-upstream.md
```

Before committing, announce the commit in one line, following the repo instructions:

> I'm about to commit `<files>` with message `<subject>`.

Commit conventions:

- Subject must follow the repo's conventional style: `feat:`, `fix:`, `docs:`, `chore:`.
- The body explains **why**, not just what changed.
- Include the required trailer:

```text
Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

If hooks fail, fix the underlying issue and create a new commit. Do not use `--no-verify`.

## Step 6 — Push to the fork

Push the branch to the user's writable fork remote, not upstream:

```bash
git push -u <fork-remote> <branch-name>
```

Confirm the resulting remote branch location before opening a PR.

## Step 7 — Open a draft PR into upstream

Target `PyAutoLabs/autolens_base_project` and its default branch.

Preferred order:

1. Use the GitHub app / connector if available and it can represent the cross-repo PR cleanly.
2. Otherwise use `gh pr create`.

When using CLI, prefer explicit arguments so the target is unambiguous:

```bash
gh pr create \
  --repo PyAutoLabs/autolens_base_project \
  --base main \
  --head <fork-owner>:<branch-name> \
  --draft \
  --title "<pr-title>" \
  --body-file <tmpfile>
```

Build the PR body as real Markdown prose, covering:

- what changed
- why it changed
- user or maintainer impact
- how it was validated

If the upstream default branch is not `main`, discover it first and use that value for `--base`.

## Step 8 — Report the result

Return a concise summary containing:

- the files included in the PR
- the branch name
- which remote was used for the push
- the upstream PR target
- the validation performed
- the PR URL

If the PR could not be opened, stop with the exact blocker and the next command or fix the user
needs.
