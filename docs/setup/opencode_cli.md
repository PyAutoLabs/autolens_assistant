# OpenCode (coding agent — open-source client)

[OpenCode](https://github.com/sst/opencode) is an **open-source** command-line coding agent.
The client itself is free; you connect it to a model provider of your choice, which may be
free or paid depending on the provider. Like the other coding agents, it can install
PyAutoLens, run fits end-to-end and inspect results — performance depends on the model you
connect it to.

## Setup

1. Install OpenCode and configure a model provider — follow the official instructions at
   [github.com/sst/opencode](https://github.com/sst/opencode).
2. Clone this repository and start the agent inside it (running from the repository root is
   what lets it discover the assistant's instructions in `AGENTS.md`):

```bash
git clone https://github.com/PyAutoLabs/autolens_assistant.git
cd autolens_assistant
opencode
```

The assistant configures itself on your first prompt, and will install PyAutoLens for you if
it isn't already installed.

## First prompts

See [First prompts to try](first_prompts.md) — the COSMOS-Web Ring data ships with the
repository, so every example works immediately.
