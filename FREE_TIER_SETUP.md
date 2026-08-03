# Setting up the Assistant on a free AI plan

This page gets the **PyAutoLens Assistant** running inside a browser chat — including on the
**free tiers** of Claude and ChatGPT, with no paid subscription and no local install.

If you can install software locally and want the assistant to actually *run* fits, skip this
page: a coding agent (Claude Code, Codex) is strictly more capable. See the README's
[AI Coding Agent](README.md#ai-coding-agent-cli) section. This page is for everyone else.

**Last verified: 2026-08-02.** Plan features and quotas change often, and the free tiers change
most. Everything below describes *observed behaviour at that date*, not a promise about what
any plan includes today. If a step doesn't match what you see, the troubleshooting section at
the end covers the failure modes we know about.

---

## What you get, and what you don't

In a browser chat the assistant can do most of the thinking work:

- plan a lens model with you and explain the trade-offs
- write complete, current-API PyAutoLens scripts for you to run
- explain strong-lensing concepts, and route you to the right example
- review a script, an error, or a figure you paste in

What it **cannot** do without a coding agent: run the fit, read your `.fits` files, inspect
your results folder, or iterate on a live run. When you hit that wall, the assistant will say
so and tell you what to switch to.

One rule matters more than any other, and it is why this setup exists at all: **older
PyAutoLens releases are heavily represented in AI training data, and their API is out of
date.** An AI answering from memory will confidently write code that no longer works. Loading
this repository is what stops that — it ships the current API surface, generated from the
pinned stack, so the assistant checks itself instead of guessing.

---

## Pick your route

| Your situation | Route | Setup effort |
|---|---|---|
| Claude, any plan (incl. Free) | **A — GitHub connector** | ~2 min, best results |
| Claude Free, connector not working or not wanted | **B — Project + knowledge pack** | ~5 min |
| ChatGPT Free | **C — paste the bundle** (connectors are paid-only) | ~30 s per chat |
| ChatGPT Plus/Pro, or you want a one-click share | **D — custom GPT** | maintainer builds once |
| Any other chat (Gemini, Copilot, …) | **C — paste the bundle** | ~30 s per chat |

Routes A and B give the assistant the whole repository. Route C gives it a curated ~6k-token
core plus links it can fetch if it has browsing. All of them enforce the API-currency rule.

---

## Route A — Claude with the GitHub connector

The GitHub connector is available on **all Claude plans, including Free**
([Anthropic's docs](https://support.claude.com/en/articles/10167454-use-the-github-integration)).
This is the best free setup: the assistant reads the repository directly and always sees
current content.

1. In Claude, open **Settings → Connectors** and enable **GitHub**. Authorise it and grant
   access to public repositories (this repo is public — you do not need to grant access to
   anything of your own).
2. *(Recommended)* Create a **Project** — Claude Free allows up to 5 — and put the prompt from
   step 3 in its custom instructions, so every chat in that project starts configured.
3. Start a chat with this prompt:

```text
Use the autolens_assistant repository: https://github.com/PyAutoLabs/autolens_assistant

Start by reading its front door:
https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main/llms.txt

Follow its read order (AGENTS_CHAT.md → the relevant skill → wiki) and its API rules.
First tell me whether you can actually read llms.txt — if you can't, say so plainly
and don't answer from memory.
```

**Naming `llms.txt` explicitly matters.** The connector does not reliably find it on its own,
and answers are markedly better when it is pointed there first.

The final sentence is a deliberate honesty check. If the assistant can't read the file, you
want to know immediately — not after it writes you a script from a 2023 API.

---

## Route B — Claude Project with the knowledge pack

Use this when you'd rather not connect GitHub, or the connector is misbehaving. Claude Free
Projects hold roughly 200K tokens of knowledge and — on Free — put it in **full context**
rather than retrieving fragments, so the assistant sees all of it.

1. Download the files in **[`chat_pack/`](chat_pack/)** (11 files, ~61k tokens total). Easiest
   way without git: download the repository ZIP from the green **Code** button on GitHub and
   take that folder.
2. In Claude, create a **Project**, then upload every file from `chat_pack/` into its
   **knowledge**.
3. Paste this into the project's **custom instructions**:

```text
You are the PyAutoLens Assistant. Follow 00_instructions.md in your project knowledge
exactly — especially: never write PyAutoLens from memory, check symbols against
01_api_surface.md, and use only the functional plotting API (aplt.subplot_*), never the
removed object-oriented plotters. Lead by engaging with my science goal; raise the
handoff to a local coding agent only when actually running code is the blocker.
```

Every chat in that project is now configured. You can add your own papers or data notes to the
same project knowledge.

> **Note.** Claude Projects can't be shared on Free or Pro (sharing is a Team/Enterprise
> feature), so each person does this once for themselves. It takes about five minutes.

---

## Route C — paste the bundle (works anywhere, incl. ChatGPT Free)

ChatGPT's connectors are **paid-plan only**, and free ChatGPT has a small context window. So
the free-ChatGPT route is a deliberately compact paste.

1. Open **[`llms-chat.txt`](llms-chat.txt)** and copy the whole file (~6k tokens — it is sized
   to leave room for an actual conversation).
2. Paste it as your first message in a new chat, followed by your question.

That file is self-contained: chat-mode instructions, the complete generated list of public
PyAuto\* symbols, and a routing table of raw URLs. If your chat has browsing, it can fetch any
skill or wiki page it needs from those URLs. If it doesn't, it still has the rules and the API
surface, and it is instructed to tell you when an answer would need a page it can't reach.

**Re-paste it in each new chat.** Nothing persists between conversations on a free plan unless
you put it in custom instructions or a project.

> **ChatGPT tip.** Paste the bundle, then add your question in the *same* message. A first
> message that is only context sometimes gets a "what would you like to do?" reply that wastes
> one of your limited flagship-model turns.

---

## Route D — a custom GPT (one-click for your users)

Free ChatGPT users **can use** custom GPTs; they just can't create them. So one person with a
Plus/Pro account can build a GPT once and share the link with everyone else — the only
first-class way to hand a configured assistant to free ChatGPT users.

Build recipe (maintainers — see [Maintaining](#maintaining-the-bundles) for regenerating
inputs first):

1. **Create a GPT** → *Configure*.
2. **Instructions**: paste the contents of `chat_pack/00_instructions.md`.
3. **Knowledge**: upload all files from `chat_pack/`. They are pre-split into ≤20 topic files
   with distinctive headings, because GPT knowledge is retrieved by **RAG chunking** rather
   than read whole — one topic per file is what makes retrieval land on the right chunk.
4. **Capabilities**: enable *Web Browsing* (so it can fetch skills and wiki pages beyond the
   pack). Code Interpreter is optional and does **not** give it PyAutoLens — the library is not
   installed in that sandbox, so it cannot run a fit there.
5. *(Optional)* Add an **Action** against `raw.githubusercontent.com` for always-current
   content. Publishing a GPT with an Action requires a privacy-policy URL.
6. Publish **Anyone with the link**, and record the link here.

**Status: not yet built.** This needs a paid ChatGPT account and a browser, so it is a manual
maintainer step. When it exists, its link goes here and in the README.

---

## First prompts to try

Once set up, any of these work (the COSMOS-Web Ring data ships with the repository):

```text
Find the data on the COSMOS-Web ring, give me a short script to plot it in PyAutoLens,
and then, given that I'm a new user, give me an overview of the different ways we can
perform strong lens modeling of this system.
```

```text
Teacher mode.

I'm new to PyAutoLens and want to learn the basic workflow end-to-end. Walk me through
simulating Euclid-like imaging of a simple strong lens, plotting it, and fitting it.
```

```text
I have HST imaging of a galaxy-scale lens. Help me plan the model: lens light, mass, and
source. Ask me what you need to know about the data first.
```

That last one exercises the behaviour that matters most — on **real data** the assistant is
required to make you look at the image before it composes a fit, and to settle two things with
you: whether there are extra galaxies or artefacts in the frame, and how big the mask should
be. It can't plot your data itself in chat, so it will ask you to. That is the rule working,
not the assistant being unhelpful.

---

## Troubleshooting

**"I can't access that repository" / it answers from memory anyway.**
The most common cause is a `blob/` URL. `github.com/.../blob/main/llms.txt` is an HTML page
that many chats receive as an empty JavaScript shell. Always use the
`raw.githubusercontent.com` form — every link in `llms.txt` is already in that form. If it
still fails, fall back to Route C.

**It fetched `llms.txt` but can't follow the links inside it.**
Some consumer chats only fetch URLs *you* pasted, not ones they discovered while reading. Paste
the specific URL you want it to read, or use Route C.

**It wrote `aplt.FitImagingPlotter(...)` or `aplt.MatPlot2D(...)`.**
That is the stale-API failure. Those classes were removed. Reply: *"Plotting is functional now
— re-check against `01_api_surface.md` and the plotting skill, and rewrite using
`aplt.subplot_fit_imaging(...)`."* If it keeps happening, your context was lost — re-paste the
bundle or check the project knowledge actually uploaded.

**It ran out of context / got slow and vague.**
Something large was pulled in. `wiki/literature/` and `llms-full.txt` are big enough to crowd
out the conversation on their own. Start a fresh chat and tell it to fetch single pages only.

**It stopped mid-task, or switched to a weaker model.**
Free plans have usage limits that are unpublished and vary with load — in the region of a few
dozen messages per 5 hours on Claude, and a smaller number of flagship-model turns on ChatGPT
before it falls back to a lighter model. Long modelling sessions are where a paid plan or a
local coding agent genuinely pays for itself.

**A generated script fails on an API error anyway.**
The bundle pins one specific stack version (stated at the top of `01_api_surface.md`). If your
installed PyAutoLens is newer, there may be genuine drift. Report it as an issue with the error
text — and note this is exactly the failure a coding agent's code gate catches automatically.

---

## Maintaining the bundles

`llms-chat.txt` and `chat_pack/` are **generated** — do not hand-edit them.

```bash
make chat-bundle          # regenerate both artifacts
make chat-bundle-check    # verify the committed copies are current (CI-friendly)
```

Regenerate on a machine with the PyAuto\* stack installed, so the API surface is refreshed
from a live `dir()` rather than reused from the committed copy (the script warns loudly when it
falls back).

The generator (`autoassistant/chat_bundle.py`) enforces four things, each of which fails the
build or the check:

- **Verbatim-anchor drift** — the rules `AGENTS_CHAT.md` shares with `AGENTS.md` must stay
  word-identical. Reword one in `AGENTS.md` and the check fails until both are updated.
- **Dead links** — every rewritten raw URL must resolve to a real path in the repository.
- **Staleness** — the committed artifacts must match a fresh build.
- **Budgets** — the paste tier stays under its token budget, and the pack under the 20-file
  GPT knowledge limit.

It also *warns* when a complete skill belongs to no group in `SKILL_GROUPS`, so newly written
skills don't silently fail to ship.

Chat-surface smoke tests for each route are in
[`modes/maintainer.md`](modes/maintainer.md#chat-surface-compatibility-smoke-test).
