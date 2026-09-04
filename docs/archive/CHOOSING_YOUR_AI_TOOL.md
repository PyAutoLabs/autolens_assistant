<!-- Archived 2026-09-03 from CHOOSING_YOUR_AI_TOOL.md (repository root) for reinstatement when
     conversation-assistant support returns — see autolens_assistant#120 -->

# Choosing Your AI Tool

The best way to use **PyAutoLens Assistant** depends on whether you have access to a browser-based conversational 
assistant (ChatGPT, Claude, or Gemini), a CLI coding agent (Claude Code, Codex, or OpenCode), and a free or 
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

## If you have a paid OpenAI or Claude subscription

If you already have a paid OpenAI or Claude subscription, their conversational assistants and CLI coding agents all work excellently with `autolens_assistant`. OpenAI provides **ChatGPT** for browser-based conversations and **Codex** for agentic coding, while Anthropic provides **Claude Chat** and **Claude Code**, respectively. Use a conversational assistant for the quickest introduction or a CLI coding agent for the complete workflow. Links to the corresponding setup guides are provided in the table below.

---

## Conversational AI Assistants

The table below gives a run through of free and paid for conversational AI Assistant options, click each option
to get a full setup guide.

| Option | Cost           | How well it works                                                                        |
|---|----------------|------------------------------------------------------------------------------------------|
| **[Claude chat](../setup/claude_chat_paid.md)** | Paid           | Works brilliantly via repo sync or input (Project knowledge)                             |
| **[ChatGPT](../setup/chatgpt_paid_connector.md)** | Paid           | Works brilliantly via GitHub sync (different from the custom GPT)                        |
| **[Claude chat](../setup/claude_chat_free.md)** | Free           | Works, but requires project setup and goes through the free tokens quickly               |
| **[ChatGPT custom GPT](../setup/chatgpt_custom_gpt.md)** | Free           | Works, but not yet able to do all tasks (experimental)                                   |
| **[Paste the bundle](../setup/paste_bundle.md)** | Free | Reliable fallback for any AI chat |

Once set up: [first prompts to try](../setup/first_prompts.md) · something misbehaving?
[troubleshooting](../setup/troubleshooting.md).

---

## CLI Coding Agents

The table below gives a run through of free and paid for CLI coding Assistant options, click each option
to get a full setup guide.

| Option | Cost                                   | How well it works                                                                                             |
|---|----------------------------------------|---------------------------------------------------------------------------------------------------------------|
| **[Claude Code](../setup/claude_code.md)** | Paid                                   | Works brilliantly                                                                                             |
| **[Codex CLI](../setup/codex_cli.md)** | Paid                                   | Works brilliantly                                                                                             |
| **[OpenCode](../setup/opencode_cli.md)** | Free| Great free performance, but can be slow                                                                       |


