# Antigravity CLI (coding agent — free tier)

**Currently our recommended best free option.** Antigravity CLI (`agy`) is Google's
command-line coding agent — it replaced Gemini CLI for free and individual Google accounts in
June 2026. Its free tier needs no credit card and includes access to Google's current models,
which makes it the best free starting point for seeing what the assistant can do as a coding
agent. In our testing its performance is **excellent for a free option**, though below what
[Claude Code](claude_code.md) or [Codex CLI](codex_cli.md) deliver on a paid subscription.

**The one thing to know first: this is a command-line tool.** It runs in a terminal, not a
browser, and many users won't have used one before. The payoff for that learning curve is the
best free performance available: unlike a browser chat, a coding agent can install PyAutoLens,
read your `.fits` files, **actually run the fits it writes**, inspect the results, and iterate
— the full assistant, not just the thinking half.

## Setup

1. Install Antigravity CLI (a single self-verifying binary — no other software needed) and
   sign in with a personal Google account when prompted:

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

   Official instructions: [antigravity.google/docs/cli](https://antigravity.google/docs/cli/getting-started).

2. Clone this repository and start the agent inside it:

```bash
git clone https://github.com/PyAutoLabs/autolens_assistant.git
cd autolens_assistant
agy
```

That's it. Antigravity reads the assistant's canonical instructions (`AGENTS.md`) at the
repository root automatically — the assistant configures itself on your first prompt, and
will install PyAutoLens for you if it isn't already installed.

## First prompts

See [First prompts to try](first_prompts.md) — the COSMOS-Web Ring data ships with the
repository, so every example works immediately.

## Limits

The free limits are generous, but a single long modelling session can reach them: usage
refreshes in windows of roughly five hours, with a weekly ceiling on top, and Google has
adjusted the free quotas several times — run `/usage` inside the CLI to see where you stand,
and treat any numbers you read online as stale. It is enough to explore the assistant and
run real fits; heavy daily use is where a paid plan pays for itself. If you already pay for
Claude or ChatGPT, [Claude Code](claude_code.md) and [Codex CLI](codex_cli.md) are the most
thoroughly tested harnesses and the strongest performers.
