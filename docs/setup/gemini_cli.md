# Gemini CLI (coding agent — retired for free accounts)

> **Retired for free and individual Google accounts on June 18, 2026.** Gemini CLI and the
> Gemini Code Assist IDE extensions stopped serving requests for free, Google AI Pro and
> Google AI Ultra individual tiers on that date, replaced by
> a free coding agent such as **[OpenCode](opencode_cli.md)**. If you're setting up fresh, use a paid
> **Claude Code** or **Codex** subscription — the two supported options — or that page instead.

Gemini CLI still works for **enterprise** users (Gemini Code Assist Standard/Enterprise,
Google Cloud access) and for anyone calling it with a **paid Gemini API key**. In that case
the setup is unchanged:

```bash
git clone https://github.com/PyAutoLabs/autolens_assistant.git
cd autolens_assistant
gemini
```

The repository ships `.gemini/settings.json`, which points Gemini CLI at the assistant's
canonical instructions (`AGENTS.md`); the assistant configures itself on your first prompt.

## Your first prompt

You're set up — copy and paste this to start (the COSMOS-Web Ring data ships with the
repository, so it works immediately):

```text
Find the data on the Cosmos-Web ring, give me a short script to plot it in PyAutoLens
and then given that I'm a new user give me an overview of the different ways we can
perform strong lens modeling of this system.
```

More examples: [First prompts to try](first_prompts.md). If anything misbehaves:
[Troubleshooting](troubleshooting.md).
