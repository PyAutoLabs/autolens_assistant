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

- **Release (workflow_call).** PyAutoHands's `release.yml` — the same run that regenerates
  the workspace/howtolens notebooks and the API baseline — invokes `wiki-currency.yml` via
  `uses:`, passing the new `stack_version` and `assistant_ref: main`. It installs that exact
  stack and runs all four checks. On drift the reusable workflow fails; PyAutoHands's
  dependent `if: failure()` job downloads the `wiki-drift-report` artifact and opens a "wiki
  drift" issue against this repo. **PyAutoHands only orchestrates and reports — it holds no
  copy of the rules.** (If releases ever move off PyAutoHands, the `repository_dispatch`/
  `workflow_call` trigger moves to whatever cuts the release; this workflow is unchanged.)
- **Assistant change (pull_request / schedule).** The same workflow runs on every PR and
  weekly against the *currently-released* stack, catching drift a wiki/skill edit introduces
  before it merges.

Ordering matters at release: PyAutoHands regenerates + commits the API baseline **before**
calling this workflow, so `--check-version` compares the new stack against an already-updated
baseline. When you change the rules, edit them here only; never copy a rule into PyAutoHands.

## Assistant-as-template: generic vs PyAutoLens-specific

This repo is the reference implementation future PyAuto domain assistants (e.g.
`autofit_assistant`, `autogalaxy_assistant`) will be modelled on. When maintaining it, keep
this boundary in mind — it is the seam a future cloning workflow will cut along. Do not
generalise anything pre-emptively; just avoid entangling the two sides.

**Generic assistant infrastructure** (clones to any domain assistant near-verbatim):
`AGENTS.md`'s skeleton (session start, safety invariants, three-layer model, mode
selection, source-of-truth resolution, commit cadence), the root `AI_POLICY.md` usage
policy, the Teacher/Assistant mode model and `modes/` machinery (the `.maintainer`
sentinel), the skills framework
(`_style.md`, `_bootstrap_skill.md`, the README index conventions), the
`core`/`literature`/`project` wiki split and its read-only/update rules, the science-project
lifecycle (`start-new-project`, `contribute-upstream`), `sources.yaml` + the source
registry pattern, the API gate (`autoassistant/audit_skill_apis.py` + wiki-currency
workflow), the profile template, the benchmark machinery (the
`benchmarks/AGENTS.md` contract + the `autoassistant/benchmark.py` harness), and
`.mcp.json` (it wires the results-inspector MCP, which *is* `autoassistant.mcp` —
generic tooling, so the wiring carries no domain either), `AGENTS_CHAT.md` (the chat-mode
counterpart of `AGENTS.md` — the same skeleton with the shell-dependent rules removed),
and the free-tier chat-bundle generator (`autoassistant/chat_bundle.py` + its
`make chat-bundle{,-check}` targets).

**PyAutoLens-specific content** (regenerated per domain, never copied blind): every
`al_*` skill body, `wiki/core/` reference pages, the entire `wiki/literature/` sub-wiki,
bundled `dataset/` examples, the README's science framing and three example prompts, the
standard-imports convention, `hpc/` templates tuned to lensing runtimes, the
benchmark prompt cards (`benchmarks/prompts/` — a new domain writes its own
easy/medium/hard assistant + teacher cards against its own bundled data), the
**euclid mode** (`skills/euclid_*.md` + the `wiki/euclid/` sub-wiki — a
survey-specific pipeline register that is lensing science throughout; a newborn
grows whatever survey modes its own domain has, if any), `paper/` (this
assistant's own JOSS paper — a newborn writes its own), the README figure
assets in `docs/` (COSMOS-Web Ring imagery + the `make_readme_figures.py`
script that renders it — a newborn regrows its own), and the bundled science
scripts in `scripts/` (`*_cosmos_web_ring.py`, tied to a named lens; only
`scripts/`'s own AGENTS/CLAUDE/README docs are generic), and the generated
`chat_pack/` knowledge bundle (concatenated `al_*` skill bodies + `wiki/core/` pages
+ a snapshot of the lensing stack's API surface — a newborn regenerates it from its
own content with `make chat-bundle`, never copies this one).

**Mixed** (structure generic, values domain-specific): `llms.txt` read-order,
`config/`, `benchmarks/README.md` (protocol generic, benchmark table domain), the
maintainer smoke tests below, and the free-tier chat surface — `docs/archive/CHOOSING_YOUR_AI_TOOL.md`
and the generated `llms-chat.txt` (the per-platform setup mechanics clone verbatim;
the worked prompts, dataset names and API rules are domain).

**Per-clone data** (never copied to a newborn — each clone accumulates its own):
`benchmarks/runs/` and the regenerated `benchmarks/RESULTS.md`. A newborn starts with
empty runs and regenerates `RESULTS.md` via `python autoassistant/benchmark.py report`.

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

Free-tier options, one per row of the options table in
[`docs/archive/CHOOSING_YOUR_AI_TOOL.md`](../docs/archive/CHOOSING_YOUR_AI_TOOL.md) (each option's setup page lives under
`docs/setup/`). Each must be tested **on a free account**, not a paid one with features
disabled:

- **Claude + GitHub connector (retired 2026-08-06 while
  [claude-code#71542](https://github.com/anthropics/claude-code/issues/71542) is open):** when
  re-testing for recovery, attach the repo via the connector and run a bootstrap prompt that
  asks "can you actually read `llms.txt`, and did you read it through the connector or by
  fetching the URL?"; the connector returns to the setup pages only if it answers truthfully
  via the connector and reaches a skill file — not just `llms.txt` — before writing code.
- **Claude Free Project upload (`docs/setup/claude_chat_free.md`):** upload `chat_pack/` to a
  Project's knowledge; ask a question whose answer lives in a skill that is *in* the pack, and
  one whose answer is in a page that is *not* (e.g. a `wiki/literature/` topic). Confirm the
  second is answered with an explicit "not in what I have" rather than from memory.
- **Pasted `llms-chat.txt` (`docs/setup/paste_bundle.md`):** paste into a fresh ChatGPT Free
  chat. Confirm the paste plus a real question fits the context window and still leaves room
  to work, and that the assistant uses `01_api_surface.md` to check a symbol it is unsure
  about.
- **Custom GPT (`docs/setup/chatgpt_custom_gpt.md`):** run the same two questions as the
  Project-upload check from a **free** ChatGPT account, to confirm knowledge retrieval works
  for a non-builder.
- **Free coding agents (`docs/setup/opencode_cli.md`):** on a
  free-tier account/model, clone the repo, launch the agent inside it, and confirm it reads
  `AGENTS.md`, runs the session-start drift check, and completes the first
  plot-the-COSMOS-Web-Ring prompt end-to-end.

In every route, include the standing regression check: ask for a plot of a fit and confirm it
emits `aplt.subplot_fit_imaging(...)` and **not** `aplt.FitImagingPlotter` / `aplt.MatPlot2D`.
Then ask it to model a *real* dataset and confirm it applies the real-data gate — asking you to
inspect the image for contaminants and to settle the mask extent — instead of silently
composing a fit.

Record the surface, date, plan/account context, files successfully loaded, and any limitations.
Plan availability changes, so test results should describe observed behavior rather than promise
that a feature is free for every user.

## Maintaining the chat bundles

`llms-chat.txt` and `chat_pack/` are **generated** — do not hand-edit them.

```bash
make chat-bundle          # regenerate both artifacts
make chat-bundle-check    # verify the committed copies are current (CI-friendly)
```

Regenerate on a machine with the PyAuto\* stack installed, so the API surface is refreshed
from a live `dir()` rather than reused from the committed copy (the script warns loudly when
it falls back). Note that source installs from library `main` report the *previous* release
in `__version__`, so a `chat-bundle-check` FAIL whose only diff is the version-stamp line is
an environment artifact, not real drift — diff the surface before regenerating.

The generator (`autoassistant/chat_bundle.py`) enforces four things, each of which fails the
build or the check:

- **Verbatim-anchor drift** — the rules `AGENTS_CHAT.md` shares with `AGENTS.md` must stay
  word-identical. Reword one in `AGENTS.md` and the check fails until both are updated.
- **Dead links** — every rewritten raw URL must resolve to a real path in the repository.
- **Staleness** — the committed artifacts must match a fresh build.
- **Budgets** — the paste tier stays under its token budget, and the pack under the 20-file
  GPT knowledge limit.

It also *warns* when a complete skill belongs to no group in `SKILL_GROUPS`, so newly
written skills don't silently fail to ship.

After a regeneration, downstream copies must be refreshed too: the custom GPT's instructions
and knowledge (build recipe in
[`docs/setup/chatgpt_custom_gpt.md`](../docs/setup/chatgpt_custom_gpt.md)), and users'
Claude Projects pick up the new pack only when they re-upload it.
