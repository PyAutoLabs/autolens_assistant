# Setting up Codex

Codex is OpenAI's AI coding agent, available in your terminal, inside editors and in the cloud. Inside this
repository it can install PyAutoLens, plot your data, run lens models and look at the results. It reads the same
instructions as Claude Code, and the assistant's skills are set up for it automatically.

## What it costs

Codex is included with ChatGPT plans, and can also be paid for through API billing. See
[OpenAI's Codex pricing page](https://developers.openai.com/codex/pricing/) for the current options.

## Install and start

1. Install Codex by following the instructions at [developers.openai.com/codex](https://developers.openai.com/codex).
2. Download this repository and start Codex inside it:

```bash
git clone https://github.com/PyAutoLabs/autolens_assistant.git
cd autolens_assistant
codex
```

3. Type `/hooks` and choose to trust this repository's hooks. These are safety checks, for example one that stops the
   assistant writing out-of-date PyAutoLens code. Codex ignores them until you trust them, and asks again whenever
   they change.
4. Paste in the [starting prompt](../../README.md#starting-prompt) from the README. The assistant installs PyAutoLens
   for you if it is missing.

## Starting from another folder

You can also open Codex in any folder and paste in the starting prompt, and it will download this repository itself.
Codex blocks internet access by default, so approve the request when it asks, or start it with internet access
switched on:

```bash
codex --sandbox workspace-write -c sandbox_workspace_write.network_access=true
```

Codex only loads the repository's instructions and safety checks when it is started inside the folder, so once the
download has finished, quit and restart `codex` inside `autolens_assistant/` for the full setup.

## How well it is tested

Codex's setup and safety checks are tested automatically, but full lens-model fits have mostly been run in Claude Code,
so you may be the first to try some analyses in Codex. The
[harness smoke record](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/docs/agent_harness_smoke.md) has the
details. If you are developing the assistant itself, run `source activate.sh` to set up your environment.

## Next steps

You do not have to let it run anything: start with `Teacher mode.` to learn, or ask it to plan an analysis and
discuss the choices before any fit is run. More prompts are in [First prompts to try](first_prompts.md), and if
something goes wrong see [Troubleshooting](troubleshooting.md).
