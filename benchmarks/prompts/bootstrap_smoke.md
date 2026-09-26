---
id: bootstrap-smoke
version: 1
mode: assistant
difficulty: easy
datasets:
  - dataset/imaging/cosmos_web_ring
workspace_packages:
  - imaging
added: 2026-09-26
---

# Benchmark: bootstrap smoke (assistant · easy)

A short, operator-driven card whose purpose is **to check that the public starting prompt
works from any directory** (autolens_assistant#138): an agent opened in an empty folder and
handed only the prompt must clone this repository, `cd` into it, read `AGENTS.md`, install or
verify PyAutoLens, show the F444W picture of the COSMOS-Web Ring and stop on the single
background question. It is the evidence behind the website's "Open Claude Code, Codex or
another AI coding agent and paste this" line; the protocol is in
[`docs/evaluation/agent_evaluation.md`](../../docs/evaluation/agent_evaluation.md). It cannot
run through the headless one-shot runner, which always starts inside a `git archive` of the
repository — the whole point is that the agent starts outside it.

## Prompt

One message, pasted verbatim into an agent started in an **empty directory**. It is the public
starting prompt, byte for byte:

```
I want to use the PyAutoLens Assistant: https://github.com/PyAutoLabs/autolens_assistant
I'd like to understand how gravitational lensing works using the JWST image of the COSMOS-Web Ring that ships with the assistant. Show me the picture, explain what we are looking at, and walk me through fitting a lens model so we can measure the mass inside the ring and see how well the model reproduces the observations. Pitch it at my level: ask me what my background is first. Explain what we are doing as we go, and let me ask questions or change the analysis along the way.
```

The greeting ends its first turn on the background question, so the run is one turn: the
operator does not answer it.

## What this measures

- Self-bootstrapping: the agent recognises it is not inside the checkout and follows the
  README / `llms.txt` / `AGENTS.md` step 0 instruction (clone, `cd`, read `AGENTS.md` in full)
  without being told to.
- Setup inside the task: PyAutoLens is installed or verified (`audit_skill_apis.py
  --check-version`, `al_setup_environment`) as part of answering the prompt, and the code gate
  is self-enforced because the project hooks did not load.
- The greeting itself: the F444W image plotted and explained, then exactly one question.

## Success rubric (100 points)

### Machine-checkable (50)

| # | Check | Pts |
|---|-------|-----|
| M1 | The transcript shows a `git clone` of the assistant repository into the empty directory, and the clone exists afterwards | 10 |
| M2 | The agent changed into the clone (commands run with the clone as cwd or `cd autolens_assistant`) and read `AGENTS.md` (a read/cat of the file appears in the transcript) | 10 |
| M3 | PyAutoLens was verified or installed without the operator asking (`audit_skill_apis.py --check-version`, `import autolens`, or a `pip install` / `al_setup_environment` step in the transcript) | 10 |
| M4 | The F444W dataset PNG exists under the clone (e.g. `scripts/scratch/cosmos_web_ring/dataset.png`) and its path is quoted in the final reply | 10 |
| M5 | The final reply ends on exactly one background question ("curious reader, a student, or a researcher") and no fit was started | 10 |

### Judged (50)

| # | Criterion | Pts |
|---|-----------|-----|
| J1 | Bootstrap narration: the user is told in plain lines what is being downloaded/installed and why, and that they can relaunch the agent inside the clone for the full setup; no wall of setup noise | 20 |
| J2 | Picture explanation follows the greeting skill: two plain sentences on lens and source, the extra galaxy and the 1.8" mask, the four JWST bands and achromatic lensing | 20 |
| J3 | Conduct: no fabricated numbers, no stale PyAutoLens API, generated code checked with the self-enforced code gate, nothing written outside the empty directory | 10 |

## Operator notes

- **Start the agent in an EMPTY directory** (`mkdir /tmp/bootstrap && cd /tmp/bootstrap`), never
  inside or next to an existing checkout, and in an environment you are willing to let it
  `pip install` into (a throwaway venv is ideal).
- Claude Code asks permission for `git clone` / `pip install`; approve them (headless:
  `claude -p "<prompt>" --permission-mode bypassPermissions --max-turns 60`). Codex's default
  sandbox blocks network; headless, run `codex exec --json --sandbox workspace-write -c
  sandbox_workspace_write.network_access=true "<prompt>"` (codex-cli 0.157 removed `--full-auto`),
  or approve the request interactively.
- Expected wall-clock: 3–25 minutes, dominated by the PyAutoLens install when it is absent.
- Record the model, harness, whether PyAutoLens was already importable, and the install path
  the agent took in `meta.yaml` `notes`. A run that never clones, or that tries to plot from the
  empty directory, is the key negative result: keep the record and say exactly what it did.
- Before `main` carries the bootstrap text, a pre-merge run may substitute the branch tree URL
  for the repository URL in the prompt; say so in `notes`.
