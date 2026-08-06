# Gemini CLI (coding agent — retired for free accounts)

> **Retired for free and individual Google accounts on June 18, 2026.** Gemini CLI and the
> Gemini Code Assist IDE extensions stopped serving requests for free, Google AI Pro and
> Google AI Ultra individual tiers on that date, replaced by
> **[Antigravity CLI](antigravity_cli.md)** — which is now our recommended best free option.
> If you're setting up fresh, use that page instead.

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

## First prompts

See [First prompts to try](first_prompts.md).
