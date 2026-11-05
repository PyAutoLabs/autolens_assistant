# Setting up Claude Code

Claude Code is Anthropic's AI coding agent, and it is the agent the PyAutoLens Assistant has been tested with most.
It runs in your terminal, as a desktop app or inside an editor such as VS Code. Inside this repository it can install
PyAutoLens, plot your data, run lens models and look at the results.

## What it costs

Claude Code is a paid product. You can use it through a Claude subscription (Pro or Max), a Team or Enterprise seat
from your institution, pay-as-you-go billing through the Claude Console, or a cloud provider your institution already
uses (Amazon Bedrock, Google Cloud or Microsoft Foundry). Lens modeling is heavy use, so check Anthropic's
[cost page](https://code.claude.com/docs/en/costs) to see which option suits you.

## Install and start

1. Install Claude Code by following the instructions at [code.claude.com/docs](https://code.claude.com/docs).
2. Open Claude Code in any folder and paste in the [starting prompt](../../README.md#starting-prompt) from the README.

The prompt tells Claude Code to download this repository and follow its instructions, so it will install PyAutoLens
for you and then show you the COSMOS-Web Ring. It will ask your permission before downloading and installing things;
say yes.

## Getting the full setup

The repository includes some safety checks, for example one that stops the assistant writing out-of-date PyAutoLens
code. Claude Code only switches these on when it is started from inside the repository folder. Once the repository is
downloaded, quit and restart Claude Code there:

```bash
cd autolens_assistant
claude
```

If you prefer, you can do this from the start by downloading the repository yourself:

```bash
git clone https://github.com/PyAutoLabs/autolens_assistant.git
cd autolens_assistant
claude
```

The desktop app and editor extensions work the same way once you open them on the `autolens_assistant` folder.

## Next steps

You do not have to let it run anything: start with `Teacher mode.` to learn, or ask it to plan an analysis and
discuss the choices before any fit is run. More prompts are in [First prompts to try](first_prompts.md), and if
something goes wrong see [Troubleshooting](troubleshooting.md).
