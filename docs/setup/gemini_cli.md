# Gemini CLI (coding agent — free tier)

**Currently our recommended best free option.** Gemini CLI is Google's command-line coding
agent, and its free tier is generous enough for real lens modelling sessions.

**The one thing to know first: this is a command-line tool.** It runs in a terminal, not a
browser, and many users won't have used one before. The payoff for that learning curve is the
best free performance available: unlike a browser chat, a coding agent can install PyAutoLens,
read your `.fits` files, **actually run the fits it writes**, inspect the results, and iterate
— the full assistant, not just the thinking half.

## Setup

1. Install Gemini CLI and sign in with a personal Google account (that is what grants the
   free quota) — follow the official instructions at
   [github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli).
2. Clone this repository and start the agent inside it:

```bash
git clone https://github.com/PyAutoLabs/autolens_assistant.git
cd autolens_assistant
gemini
```

That's it. The repository ships `.gemini/settings.json`, which points Gemini CLI at the
assistant's canonical instructions (`AGENTS.md`) — the assistant configures itself on your
first prompt, and will install PyAutoLens for you if it isn't already installed.

## First prompts

See [First prompts to try](first_prompts.md) — the COSMOS-Web Ring data ships with the
repository, so every example works immediately.

## Limits

The free quota is capped per day ([current quotas](https://github.com/google-gemini/gemini-cli/blob/main/docs/resources/quota-and-pricing.md))
and long modelling sessions can exhaust it; paid Google AI subscriptions or usage billing
raise the limits. If you already pay for Claude or ChatGPT, [Claude Code](claude_code.md) and
[Codex CLI](codex_cli.md) are the most thoroughly tested harnesses.
