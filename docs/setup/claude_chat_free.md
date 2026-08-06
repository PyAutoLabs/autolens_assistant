# Claude chat — Free plan (Project + knowledge pack)

Run the assistant inside claude.ai on the **Free plan**: a curated pack of this repository is
uploaded straight into a Project's knowledge. On Free, project knowledge is put in **full
context** (~200K tokens) rather than retrieved in fragments, so the assistant sees all of it
from the first message.

**How well it works:** well — the assistant plans models, writes current-API scripts and
teaches concepts faithfully — **but it goes through the free token allowance quickly**. Free
usage limits are unpublished and vary with load (in the region of a few dozen messages per 5
hours), and every message carries the pack. Fine for planning sessions and short questions;
long modelling conversations will hit the ceiling — that is where a
[paid plan](claude_chat_paid.md) or a [coding agent](antigravity_cli.md) pays for itself.

## Setup (~5 minutes, once)

1. Download the files in [`chat_pack/`](../../chat_pack/) (11 files, ~61k tokens total).
   Easiest way without git: download the repository ZIP from the green **Code** button on
   GitHub and take that folder.
2. In Claude, create a **Project** (Free allows up to 5), then upload every file from
   `chat_pack/` into its **knowledge**.
3. Paste this into the project's **custom instructions**:

```text
You are the PyAutoLens Assistant. Follow 00_instructions.md in your project knowledge
exactly — especially: never write PyAutoLens from memory, check symbols against
01_api_surface.md, and use only the functional plotting API (aplt.subplot_*), never the
removed object-oriented plotters. Lead by engaging with my science goal; raise the
handoff to a local coding agent only when actually running code is the blocker.
```

Every chat in that project is now configured. You can add your own papers or data notes to
the same project knowledge.

> **Notes.** Claude Projects can't be shared on Free or Pro (sharing is a Team/Enterprise
> feature), so each person does this once for themselves. Don't bother with the GitHub
> connector for now — an open bug leaves it attaching repositories without making their
> content readable (see [Troubleshooting](troubleshooting.md)).

## What it can and can't do

In chat the assistant does the thinking work — planning models, writing scripts for you to
run, explaining concepts, reviewing errors and figures you paste in. It **cannot** run fits,
read your `.fits` files or inspect your results folder; when that is the blocker it will say
so and point you to a coding agent.

## First prompts

See [First prompts to try](first_prompts.md). If anything misbehaves:
[Troubleshooting](troubleshooting.md).
