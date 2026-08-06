# Setting up the Assistant on a free AI plan

This page gets the **PyAutoLens Assistant** running inside a browser chat — including on the
**free tiers** of Claude and ChatGPT. No paid subscription, no local install.

**Who should skip this page:** if you can install software locally, use a coding agent
(Claude Code, Codex) instead — it can actually *run* fits, and is strictly more capable. See
the README's [AI Coding Agent](README.md#ai-coding-agent-cli) section. This page is for
everyone else.

**Last verified: 2026-08-06** (Claude routes re-tested on a live Free account; custom GPT
built and tested the same day on paid and free accounts — currently experimental, see
Route D). Free-tier features and quotas change often. Everything
below is *observed behaviour at that date*, not a promise about what any plan includes today.
If a step doesn't match what you see, check [Troubleshooting](#troubleshooting).

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

> **Why this setup exists.** Older PyAutoLens releases are heavily represented in AI training
> data, and their API is out of date — an AI answering from memory will confidently write code
> that no longer works. Loading this repository ships the *current* API surface, generated
> from the pinned stack, so the assistant checks itself instead of guessing.

---

## Pick your route

| Your situation | Route | Setup effort |
|---|---|---|
| Claude, any plan (incl. Free) | **B — Project + knowledge pack** | ~5 min |
| ChatGPT, any plan (incl. Free) | **D — the published custom GPT** (experimental) | none — open the link |
| ChatGPT, when the GPT can't answer or you need a verified script | **C — paste the bundle** (connectors are paid-only) | ~30 s per chat |
| Any other chat (Gemini, Copilot, …) | **C — paste the bundle** | ~30 s per chat |

Route B gives the assistant the whole repository as a curated uploaded pack. Route C gives it
a ~6k-token core. All routes enforce the API-currency rule.

> **Where is Route A?** There used to be a connector route: Claude's GitHub connector reading
> this repository live. It is retired from this page while an open bug
> ([claude-code#71542](https://github.com/anthropics/claude-code/issues/71542)) leaves the
> connector attaching repositories without making their content readable — and Claude's
> web-fetch fallback only retrieves URLs *you* paste, so that path degrades into pasting a
> raw URL for every page the assistant needs (verified on a live Free account, 2026-08-06).
> If the connector recovers, the route comes back; nothing else on this page depends on it.

---

## Route B — Claude Project with the knowledge pack

This is the Claude route: no connector, and nothing to fetch mid-conversation. A
curated pack of the repository is uploaded straight into a Project's knowledge. On Free,
project knowledge is put in **full context** (~200K tokens) rather than retrieved in
fragments, so the assistant sees all of it from the first message.

1. Download the files in **[`chat_pack/`](chat_pack/)** (11 files, ~61k tokens total).
   Easiest way without git: download the repository ZIP from the green **Code** button on
   GitHub and take that folder.
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

Every chat in that project is now configured. You can add your own papers or data notes to
the same project knowledge.

> **Note.** Claude Projects can't be shared on Free or Pro (sharing is a Team/Enterprise
> feature), so each person does this once for themselves. It takes about five minutes.

---

## Route C — paste the bundle (works anywhere, incl. ChatGPT Free)

ChatGPT's connectors are **paid-plan only**, and free ChatGPT has a small context window. So
the free-ChatGPT route is a deliberately compact paste.

1. Open **[`llms-chat.txt`](llms-chat.txt)** and copy the whole file (~6k tokens — sized to
   leave room for an actual conversation).
2. Paste it as your first message in a new chat, followed by your question.

That file is self-contained: chat-mode instructions, the complete generated list of public
PyAuto\* symbols, and a routing table of raw URLs. If your chat has browsing, it can fetch
any skill or wiki page from those URLs; if not, it still has the rules and the API surface,
and it is instructed to tell you when an answer would need a page it can't reach.

Two things to know:

- **Re-paste it in each new chat.** Nothing persists between conversations on a free plan
  unless you put it in custom instructions or a project.
- **ChatGPT tip:** paste the bundle and add your question in the *same* message. A first
  message that is only context sometimes gets a "what would you like to do?" reply that
  wastes one of your limited flagship-model turns.

---

## Route D — the custom GPT (one-click, experimental)

**The GPT is live:**
**[PyAutoLens AI Assistant](https://chatgpt.com/g/g-6a74c33c58c48191b8cd353e7b46f18b-pyautolens-ai-assistant)**
(built 2026-08-06 against the 2026.8.4.1 `chat_pack/`). Open the link and start chatting —
no setup.

> **Experimental (as of 2026-08-06).** In testing, the GPT's uploaded knowledge was not
> reliably retrievable in published chats (a known custom-GPT platform issue), and on free
> accounts browsing could not fetch raw GitHub pages either. The GPT is honest about this —
> it will *decline* to write code it can't verify rather than fabricate a stale API, which
> is the designed behaviour. It remains good for planning, concepts, and reviewing your
> scripts and errors. **If it says it can't retrieve its documentation, or you need a
> verified full script, use Route C** — the paste puts everything in-context and is immune
> to both problems.

Free ChatGPT users **can use** custom GPTs; they just can't create them. So one person with a
Plus/Pro account builds a GPT once and shares the link — the only first-class way to hand a
configured assistant to free ChatGPT users.

Build recipe (maintainers, for rebuilding after a `chat_pack/` regeneration — see
[Maintaining](#maintaining-the-bundles) for regenerating inputs first):

1. **Create a GPT** → *Configure*.
2. **Instructions**: paste the contents of `chat_pack/00_instructions.md`.
3. **Knowledge**: upload all files from `chat_pack/`. They are pre-split into ≤20 topic files
   with distinctive headings, because GPT knowledge is retrieved by **RAG chunking** rather
   than read whole — one topic per file is what makes retrieval land on the right chunk.
4. **Capabilities**: enable *Web Browsing* (so it can fetch skills and wiki pages beyond the
   pack). Code Interpreter is optional and does **not** give it PyAutoLens — the library is
   not installed in that sandbox, so it cannot run a fit there.
5. *(Optional)* Add an **Action** against `raw.githubusercontent.com` for always-current
   content. Publishing a GPT with an Action requires a privacy-policy URL.
6. Publish **Anyone with the link**, and record the link here.

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

The last one exercises the behaviour that matters most. On **real data** the assistant is
required to make you look at the image before it composes a fit, and to settle two things
with you: whether there are extra galaxies or artefacts in the frame, and how big the mask
should be. It can't plot your data itself in chat, so it will ask you to. That is the rule
working, not the assistant being unhelpful.

---

## Troubleshooting

**You tried the GitHub connector anyway, and connecting the repo just inserts a
`github.com/.../tree/main` link into the message.**
This is the connector bug that retired Route A
([claude-code#71542](https://github.com/anthropics/claude-code/issues/71542)), which we
reproduced on our own Free-account test (2026-08-06). Some accounts have recovered by
connecting the repo inside a **brand-new Project**, or by disconnecting the connector fully
(also revoke Claude under GitHub → Settings → Applications) and reconnecting — but don't
sink time into it: Route B needs no connector at all and works today.

**"I can't access that repository" / it answers from memory anyway.**
The most common cause is a `blob/` URL — `github.com/.../blob/main/llms.txt` is an HTML page
that many chats receive as an empty JavaScript shell. Always use the
`raw.githubusercontent.com` form; every link in `llms.txt` already is. If it still fails,
fall back to Route C.

**It fetched `llms.txt` but can't follow the links inside it — it keeps asking you to paste
URLs.**
On claude.ai (and some other chats) the fetch tool only retrieves URLs *you* pasted or
literal search hits — links the assistant discovers inside a page it fetched stay blocked.
Pasting the raw URL it asks for works instantly, but costs a message each time. If you're
doing this more than once or twice, switch to Route B: with the pack in project knowledge,
nothing needs fetching.

**It wrote `aplt.FitImagingPlotter(...)` or `aplt.MatPlot2D(...)`.**
That is the stale-API failure — those classes were removed. Reply: *"Plotting is functional
now — re-check against `01_api_surface.md` and the plotting skill, and rewrite using
`aplt.subplot_fit_imaging(...)`."* If it keeps happening, your context was lost — re-paste
the bundle or check the project knowledge actually uploaded.

**It ran out of context / got slow and vague.**
Something large was pulled in — `wiki/literature/` and `llms-full.txt` are big enough to
crowd out the conversation on their own. Start a fresh chat and tell it to fetch single
pages only.

**It stopped mid-task, or switched to a weaker model.**
Free plans have usage limits that are unpublished and vary with load — in the region of a
few dozen messages per 5 hours on Claude, and a smaller number of flagship-model turns on
ChatGPT before it falls back to a lighter model. Long modelling sessions are where a paid
plan or a local coding agent genuinely pays for itself.

**A generated script fails on an API error anyway.**
The bundle pins one specific stack version (stated at the top of `01_api_surface.md`). If
your installed PyAutoLens is newer, there may be genuine drift. Report it as an issue with
the error text — and note this is exactly the failure a coding agent's code gate catches
automatically.

---

## Maintaining the bundles

`llms-chat.txt` and `chat_pack/` are **generated** — do not hand-edit them.

```bash
make chat-bundle          # regenerate both artifacts
make chat-bundle-check    # verify the committed copies are current (CI-friendly)
```

Regenerate on a machine with the PyAuto\* stack installed, so the API surface is refreshed
from a live `dir()` rather than reused from the committed copy (the script warns loudly when
it falls back).

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

Chat-surface smoke tests for each route are in
[`modes/maintainer.md`](modes/maintainer.md#chat-surface-compatibility-smoke-test).
