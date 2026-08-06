# Choosing Your AI Tool

The best way to use **PyAutoLens Assistant** depends on whether you have access to a browser-based conversational 
assistant (ChatGPT, Claude, or Gemini), a CLI coding agent (Antigravity, Claude Code, Codex, or OpenCode), and a free or 
paid plan. This guide helps you choose the best option for your needs and set it up.

---

## Keeping this guide current

**Last updated: 6 August 2026.**

The AI landscape changes rapidly: features appear, usage limits change, and temporary issues are common. This guide 
is updated regularly to reflect the best available options.

If anything appears outdated, please **[open a GitHub issue](https://github.com/PyAutoLabs/autolens_assistant/issues)**. 
Even a one-line report such as “the connector works again” or “the free quota has changed” is genuinely useful in 
keeping this guidance current.

---

## Recommended free option: Antigravity CLI

**[Antigravity CLI](docs/setup/antigravity_cli.md)** is Google’s coding agent, which replaced Gemini CLI for free 
accounts in June 2026. Its free tier does not require a credit card.

Antigravity is a **CLI coding agent**, meaning that it runs in a terminal rather than a browser. Although this 
may initially be unfamiliar, it provides the most capable free workflow: it can install `PyAutoLens`, inspect `.fits` 
files, write and execute lens-modelling scripts, diagnose errors, and iterate on the results. Its performance is 
excellent for a free tool, although generally below Claude Code or Codex with a paid subscription. The free limits 
are generous, but a long analysis session may reach them.

---

## If you have a paid OpenAI or Claude subscription

If you already have a paid OpenAI or Claude subscription, their conversational assistants and CLI coding agents all work excellently with `autolens_assistant`. OpenAI provides **ChatGPT** for browser-based conversations and **Codex** for agentic coding, while Anthropic provides **Claude Chat** and **Claude Code**, respectively. Use a conversational assistant for the quickest introduction or a CLI coding agent for the complete workflow. Links to the corresponding setup guides are provided in the table below.

---

## Conversational AI Assistants

The table below gives a run through of free and paid for conversational AI Assistant options, click each option
to get a full setup guide.

| Option | Cost           | How well it works                                                                        |
|---|----------------|------------------------------------------------------------------------------------------|
| **[Claude chat](docs/setup/claude_chat_paid.md)** | Paid           | Works brilliantly via repo sync or input (Project knowledge)                             |
| **[ChatGPT](docs/setup/chatgpt_paid_connector.md)** | Paid           | Works brilliantly via GitHub sync (different from the custom GPT)                        |
| **[Claude chat](docs/setup/claude_chat_free.md)** | Free           | Works, but requires project setup and goes through the free tokens quickly               |
| **[ChatGPT custom GPT](docs/setup/chatgpt_custom_gpt.md)** | Free           | Works, but not yet able to do all tasks (experimental)                                   |
| **[Paste the bundle](docs/setup/paste_bundle.md)** | Free | Reliable fallback for any AI chat |

Once set up: [first prompts to try](docs/setup/first_prompts.md) · something misbehaving?
[troubleshooting](docs/setup/troubleshooting.md).

---

## CLI Coding Agents

The table below gives a run through of free and paid for CLI coding Assistant options, click each option
to get a full setup guide.

| Option | Cost                                   | How well it works                                                                                              |
|---|----------------------------------------|----------------------------------------------------------------------------------------------------------------|
| **[Antigravity CLI](docs/setup/antigravity_cli.md)** | Free                                   | **Best free performance** setup easy with generous limits, less capable at complex tasks than paid for options |
| **[Claude Code](docs/setup/claude_code.md)** | Paid                                   | Works brilliantly                                                                                              |
| **[Codex CLI](docs/setup/codex_cli.md)** | Paid                                   | Works brilliantly                                                                                              |
| **[OpenCode](docs/setup/opencode_cli.md)** | Free| Great free performance, but can be slow                                                                        |


