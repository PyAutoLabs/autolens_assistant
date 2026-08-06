# Codex CLI (coding agent — limited free / paid)

OpenAI's command-line coding agent, and one of the two **primary, thoroughly tested**
harnesses for the assistant (alongside [Claude Code](claude_code.md)). It reads the
assistant's canonical instructions (`AGENTS.md`) directly, and can install PyAutoLens, run
fits end-to-end and inspect results.

A [limited free plan](https://developers.openai.com/codex/pricing/) may be available; paid
ChatGPT plans or API billing provide more usage.

## Setup

1. Install Codex CLI — follow the official instructions at
   [developers.openai.com/codex](https://developers.openai.com/codex).
2. Clone this repository and start the agent inside it:

```bash
git clone https://github.com/PyAutoLabs/autolens_assistant.git
cd autolens_assistant
codex
```

The assistant configures itself on your first prompt, and will install PyAutoLens for you if
it isn't already installed.

## First prompts

See [First prompts to try](first_prompts.md) — the COSMOS-Web Ring data ships with the
repository, so every example works immediately.
