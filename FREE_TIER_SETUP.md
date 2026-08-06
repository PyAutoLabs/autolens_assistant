# Using the Assistant — every AI option, free and paid

The best way to use the **PyAutoLens Assistant** depends on which AI tools you have access
to: a conversational assistant in the browser (ChatGPT, Claude, Gemini, …), a command-line
coding agent (Gemini CLI, Claude Code, Codex, OpenCode), a free plan or a paid one. The AI
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

## Currently recommended best free option: Gemini CLI

**[Gemini CLI](docs/setup/gemini_cli.md)** — Google's coding agent, with a generous free
tier. Note that this is a **command-line coding agent**: it runs in a terminal, which many
people won't be familiar with. The payoff is the best free performance available — unlike a
browser chat, it can install PyAutoLens, read your `.fits` files, **actually run the fits it
writes**, and iterate on the results.

---

## All options

| Option | Type | Cost | How well it works |
|---|---|---|---|
| **[Gemini CLI](docs/setup/gemini_cli.md)** | Coding agent (CLI) | Free tier (paid raises limits) | **Best free performance** — runs fits end-to-end; requires the command line |
| **[Claude Code](docs/setup/claude_code.md)** | Coding agent (CLI) | Paid | Works brilliantly — the primary, most thoroughly tested harness |
| **[Codex CLI](docs/setup/codex_cli.md)** | Coding agent (CLI) | Limited free / paid | Works brilliantly — primary, thoroughly tested |
| **[OpenCode](docs/setup/opencode_cli.md)** | Coding agent (CLI) | Free client; model access free or paid | Supported — performance depends on the model you connect |
| **[Claude chat — paid](docs/setup/claude_chat_paid.md)** | Conversational AI | Paid | Works brilliantly via repo input (Project knowledge) |
| **[ChatGPT — paid](docs/setup/chatgpt_paid_connector.md)** | Conversational AI | Paid | Works brilliantly via GitHub sync (different from the custom GPT) |
| **[Claude chat — free](docs/setup/claude_chat_free.md)** | Conversational AI | Free | Works, but goes through the free tokens quickly |
| **[ChatGPT custom GPT](docs/setup/chatgpt_custom_gpt.md)** | Conversational AI | Free (any plan) | Works, but not yet able to do all tasks (experimental) |
| **[Paste the bundle](docs/setup/paste_bundle.md)** | Conversational AI | Free (any chat) | Reliable fallback anywhere — compact, so best for shorter sessions |

**The one distinction that matters most:** a *conversational AI* does the thinking work —
planning models, writing scripts for you to run, explaining concepts, reviewing errors — but
cannot run fits or read your `.fits` files. A *coding agent* does all of that **and**
executes the analysis end-to-end. If you can use a terminal, a coding agent is strictly more
capable.

Once set up: [first prompts to try](docs/setup/first_prompts.md) · something misbehaving?
[troubleshooting](docs/setup/troubleshooting.md).
