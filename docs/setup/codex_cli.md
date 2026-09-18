# Codex (coding agent — recommended)

OpenAI's coding agent (CLI, IDE extension and cloud), and one of the two **recommended,
thoroughly exercised** harnesses for the assistant (alongside [Claude Code](claude_code.md)).
It reads the assistant's canonical instructions (`AGENTS.md`) directly, and can install
PyAutoLens, run fits end-to-end and inspect results. The tracked `.codex/hooks.json` registers
the assistant's API gate and end-at-deliverable guard. Open `/hooks` after cloning (and after
that file changes) to review and trust its exact current hash; Codex skips untrusted project
hooks. The separate Claude remote-session Python bootstrap is intentionally not registered for
Codex, so continue to use `source activate.sh` for local development setup.

**Access.** Codex is included with paid ChatGPT plans (Plus, Pro, Business, Edu and Enterprise —
the last three are the usual institutional routes) and can also be used with an OpenAI API key on
usage-based billing. Whether a Free-plan allowance exists has changed over time and could not be
re-verified against the official pricing page when this page was last revised (2026-09-10);
check [OpenAI's Codex pricing page](https://developers.openai.com/codex/pricing/) for the
current position rather than relying on this page. Sustained scientific use should be budgeted
as paid access.

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
