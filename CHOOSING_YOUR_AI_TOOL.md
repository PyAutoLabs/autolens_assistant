# Choosing Your AI Tool — every option, free and paid

The best way to use the **PyAutoLens Assistant** depends on which AI tools you have access
to: a conversational assistant in the browser (ChatGPT, Claude, Gemini, …), a command-line
coding agent (Antigravity, Claude Code, Codex, OpenCode), a free plan or a paid one. The AI
landscape changes fast — features appear, quotas move, bugs come and go — so this page is
**updated frequently** with the current best advice, and each option below links to its own
short, step-by-step setup page.

**If something here feels out of date, please
[open a GitHub issue](https://github.com/PyAutoLabs/autolens_assistant/issues)** — a
one-line "the connector works again" or "this quota changed" is genuinely useful, because
user reports are how this page stays current.

**Last verified: 2026-08-06.** Everything below is *observed behaviour at that date*, not a
promise about what any plan includes today.

> **Why setup matters at all.** Older PyAutoLens releases are heavily represented in AI
> training data — an AI answering from memory will confidently write code that no longer
> works. Every option below loads this repository, which ships the *current* API surface, so
> the assistant checks itself instead of guessing.

---

## Currently recommended best free option: Antigravity CLI

**[Antigravity CLI](docs/setup/antigravity_cli.md)** — Google's coding agent (it replaced
Gemini CLI for free accounts in June 2026), with a free tier that needs no credit card. Note
that this is a **command-line coding agent**: it runs in a terminal, which many people won't
be familiar with. The payoff is the best free performance available — unlike a browser chat,
it can install PyAutoLens, read your `.fits` files, **actually run the fits it writes**, and
iterate on the results. Performance is excellent for a free model, though below Claude Code /
Codex on a paid subscription; the free limits are generous but can be reached relatively
quickly in a single long session.

---

## CLI Coding Agents

A coding agent is an AI you type to in a **terminal** (command line) window rather than a
browser. Because it runs directly on your computer, it goes far beyond conversation: it can
install PyAutoLens for you, inspect your `.fits` data, write Python scripts **and actually
execute them**, watch the fit run, load the results and iterate — end-to-end lens modelling
from a single prompt. If you have never used a terminal there is a small learning curve, but
this is the recommended, best-performing way to use the assistant, and each setup page below
walks you through it from a fresh install.

| Option | Cost | How well it works |
|---|---|---|
| **[Antigravity CLI](docs/setup/antigravity_cli.md)** | Free tier (paid raises limits) | **Best free performance** — excellent for free, below Claude Code / Codex on paid; generous limits, but reachable in one long session |
| **[Claude Code](docs/setup/claude_code.md)** | Paid | Works brilliantly — the primary, most thoroughly tested harness |
| **[Codex CLI](docs/setup/codex_cli.md)** | Limited free / paid | Works brilliantly — primary, thoroughly tested |
| **[OpenCode](docs/setup/opencode_cli.md)** | Free client; model access free or paid | Supported — performance depends on the model you connect |
| **[Gemini CLI](docs/setup/gemini_cli.md)** | Enterprise / paid API only | Retired for free accounts June 2026 — use Antigravity instead |

## Conversational AI Assistants

A conversational assistant is the familiar browser chat (ChatGPT, Claude, Gemini, …). Once
loaded with this repository it does the thinking half of the work well: it plans your lens
model and explains the trade-offs, writes complete current-API PyAutoLens scripts for you to
run yourself, teaches strong-lensing concepts, and reviews any script, error or figure you
paste in. What it **cannot** do is run the fit, read your `.fits` files or inspect your
results folder — when that becomes the blocker, it will say so and point you to a coding
agent.

| Option | Cost | How well it works |
|---|---|---|
| **[Claude chat](docs/setup/claude_chat_paid.md)** | Paid | Works brilliantly via repo input (Project knowledge) |
| **[ChatGPT](docs/setup/chatgpt_paid_connector.md)** | Paid | Works brilliantly via GitHub sync (different from the custom GPT) |
| **[Claude chat](docs/setup/claude_chat_free.md)** | Free | Works, but goes through the free tokens quickly |
| **[ChatGPT custom GPT](docs/setup/chatgpt_custom_gpt.md)** | Free (any plan) | Works, but not yet able to do all tasks (experimental) |
| **[Paste the bundle](docs/setup/paste_bundle.md)** | Free (any chat) | Reliable fallback anywhere — compact, so best for shorter sessions |

Once set up: [first prompts to try](docs/setup/first_prompts.md) · something misbehaving?
[troubleshooting](docs/setup/troubleshooting.md).
