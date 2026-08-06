# Claude chat — paid plans (repo input via Project knowledge)

Run the assistant inside claude.ai on a **paid plan** (Pro/Max/Team) by giving it the
repository as Project knowledge. **This works brilliantly:** the higher usage limits remove
the token squeeze that constrains the [Free-plan route](claude_chat_free.md), so long
modelling conversations, deep concept dives and multi-script planning sessions all run
without hitting the ceiling.

## Setup (~5 minutes, once)

The setup is the same Project + knowledge-pack recipe as the Free route — follow
[Claude chat — Free plan](claude_chat_free.md) steps 1–3. On paid plans you additionally
have room to drop your own papers, data notes and analysis logs into the same project
knowledge without crowding anything out.

> **GitHub connector.** Reading the repository live via the GitHub connector would be even
> better, but an open bug currently leaves the connector attaching repositories without
> making their content readable (see [Troubleshooting](troubleshooting.md)). When it
> recovers, this page will switch to recommending it.

## What it can and can't do

In chat the assistant does the thinking work — planning models, writing current-API scripts
for you to run, explaining concepts, reviewing errors and figures. It **cannot** run fits or
read your `.fits` files; for that, pair it with a coding agent such as
[Claude Code](claude_code.md), which shares your Claude subscription.

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
