---
name: contribute-upstream
description: Prepare a scoped update to autolens_assistant and propose it back upstream. Use this skill when the user says "contribute this back", "open a PR upstream", "suggest this to the assistant", or "send this to PyAutoLabs/autolens_assistant". It validates the git remote layout, confirms PR scope, creates or reuses a feature branch, stages only the intended files, commits with the repo's commit conventions, pushes either to the upstream repo (for collaborators) or the user's fork, and opens a draft PR against PyAutoLabs/autolens_assistant.
user-invocable: true
---

# Contribute Upstream

Use this skill when work should be proposed upstream to
`PyAutoLabs/autolens_assistant`, whether the user is working from a personal fork or from a
collaborator clone with direct branch-push access.

This is a **project-workflow** skill, not a lensing API skill. The output is a draft pull request
against the upstream assistant repo, not a Python script.

## Step 1 — Confirm the scope

Before touching git, confirm exactly what belongs in the PR.

- Run `git status --short` and inspect the diff for the candidate files.
- If unrelated user work is present, ask which files belong in this PR.
- Never assume the whole worktree is in scope.
- Never use `git add -A` or `git add .` for this workflow.

If the change naturally splits into more than one concern, recommend separate PRs and ask which one
to prepare first.

## Step 2 — Verify the repository and remotes

Confirm the current repository is `autolens_assistant` and inspect its remotes:

```bash
git remote -v
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name @{u}
```

You need to identify two possible roles:

- **Upstream target** — the remote that points to `PyAutoLabs/autolens_assistant`.
- **Writable push remote** — either the upstream repo itself (for collaborators) or the user's
  personal fork.

Prefer the repo convention used in this workspace when the user is working from a fork:

- `origin` = `PyAutoLabs/autolens_assistant`
- `fork` = the user's writable fork

But do **not** hard-code the remote names. Detect the roles from the remote URLs so the workflow
still works if the user kept `origin` as their fork and named upstream `upstream`.

If there is no writable fork remote but the user has push access to the upstream repo, branches may
be pushed directly to the upstream remote.

If there is neither a writable fork remote nor upstream push access, stop and tell the user what
remote they need to add before continuing.

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
- If the user is already on a non-default feature branch that clearly belongs to their fork or the
  upstream collaborator repo, stay on it unless they ask to branch again.

Only push commits directly to the upstream remote when the user is a collaborator and the branch is
clearly intended to live there.

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

## Step 6 — Push to the correct remote

Push the branch to the writable push remote chosen in Step 2:

```bash
git push -u <push-remote> <branch-name>
```

Confirm the resulting remote branch location before opening a PR.

## Step 7 — Open a draft PR into upstream

Target `PyAutoLabs/autolens_assistant` and its default branch.

Preferred order:

1. Use the GitHub app / connector if available.
2. Otherwise use `gh pr create`.

When using CLI from a fork, prefer explicit arguments so the target is unambiguous:

```bash
gh pr create \
  --repo PyAutoLabs/autolens_assistant \
  --base main \
  --head <fork-owner>:<branch-name> \
  --draft \
  --title "<pr-title>" \
  --body-file <tmpfile>
```

When the branch already lives on `PyAutoLabs/autolens_assistant`, `--head <branch-name>` is
sufficient.

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
- which remote was used for the push, and whether it was upstream or a fork
- the upstream PR target
- the validation performed
- the PR URL

If the PR could not be opened, stop with the exact blocker and the next command or fix the user
needs.
