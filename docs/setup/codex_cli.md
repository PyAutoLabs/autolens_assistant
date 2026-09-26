# Codex (coding agent — recommended)

OpenAI's coding agent (CLI, IDE extension and cloud). It reads the shared
`AGENTS.md` instructions, and this repository exposes its canonical `skills/*.md`
through generated, project-level `.codex/skills/` adapters. Discovery was checked
with an installed Codex CLI; adapter validation and fixture guard tests cover the
setup, while scientific fits still need to be exercised in the user's environment.
See the [harness smoke record](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/docs/agent_harness_smoke.md)
for the measured scope.

The tracked `.codex/hooks.json` registers the API and end-at-deliverable guards.
Review and trust its current hash in `/hooks` after cloning and after changes;
Codex skips project hooks until that hash is trusted. The separate Claude
remote-session Python bootstrap is not registered for Codex, so use
`source activate.sh` for local development setup.

**Access.** Check [OpenAI's Codex pricing page](https://developers.openai.com/codex/pricing/)
for current plans and API billing.

## Setup

1. Install Codex — follow the official instructions at
   [developers.openai.com/codex](https://developers.openai.com/codex).
2. Clone this repository and start the agent inside it:

```bash
git clone https://github.com/PyAutoLabs/autolens_assistant.git
cd autolens_assistant
codex
```

The assistant configures itself on your first prompt, and will install PyAutoLens for you if
it isn't already installed.

## Start from any directory

Cloning first is optional. You can open Codex in any folder — even an empty one — and paste
the [starting prompt](../../README.md#starting-prompt). Because the prompt names this
repository, the agent will clone it, `cd` into it, read `AGENTS.md`, install PyAutoLens if it
is missing, and then show you the COSMOS-Web Ring and ask your background.

Codex's default sandbox blocks network access, so the clone and the install need it: approve
the network request when Codex asks, start it with `codex --full-auto`, or clone the
repository yourself and relaunch `codex` inside it. Codex reads `AGENTS.md` and registers the
project hooks only at launch, so in a session started elsewhere the agent reads the file
explicitly and checks its PyAutoLens code against the installed library by hand; relaunching
inside `autolens_assistant/` gives you the full setup.

## Your first prompt

You're set up — copy and paste this to start (the COSMOS-Web Ring data ships with the
repository, so it works immediately):

<sub><b>Example Natural Language Prompt for Claude Code, Codex or other AI coding agent</b></sub>

```text
Find the data on the Cosmos-Web ring, give me a short script to plot it in PyAutoLens
and then given that I'm a new user give me an overview of the different ways we can
perform strong lens modeling of this system.
```

You do not have to let it run anything: start with `Teacher mode.` to learn, or ask it to plan
an analysis and discuss the choices before any fit is submitted.

More examples: [First prompts to try](first_prompts.md). If anything misbehaves:
[Troubleshooting](troubleshooting.md).
