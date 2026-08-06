# Claude Code (coding agent — paid)

The **primary, most thoroughly tested** harness for the assistant. Claude Code is Anthropic's
command-line coding agent: it reads the repository's instructions through `CLAUDE.md`, runs
the code-gate hook that blocks stale PyAutoLens API written from memory, and can install
PyAutoLens, run fits end-to-end, inspect results and drive HPC workflows.

Normally requires a paid Claude subscription or metered API usage
([costs](https://code.claude.com/docs/en/costs)).

## Setup

1. Install Claude Code — follow the official instructions at
   [code.claude.com/docs](https://code.claude.com/docs).
2. Clone this repository and start the agent inside it:

```bash
git clone https://github.com/PyAutoLabs/autolens_assistant.git
cd autolens_assistant
claude
```

The assistant configures itself on your first prompt, and will install PyAutoLens for you if
it isn't already installed.

## First prompts

See [First prompts to try](first_prompts.md) — the COSMOS-Web Ring data ships with the
repository, so every example works immediately.
