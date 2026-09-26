# First prompts to try

Once [Claude Code](claude_code.md), [Codex](codex_cli.md) or (experimentally)
[OpenCode](opencode_cli.md) is open inside the repository, these all work immediately — the
COSMOS-Web Ring data ships with the repository. Start with the public greeting prompt — the
assistant will ask your background first (curious reader, student or researcher) and pitch the
walkthrough accordingly. The greeting also works before you have cloned anything: paste it
into Claude Code or Codex opened in any folder and the agent clones the repository and installs
PyAutoLens itself (see "Start from any directory" in the setup pages):

<sub><b>Starting prompt for Claude Code, Codex or other AI coding agent</b></sub>

```text
I want to use the PyAutoLens Assistant: https://github.com/PyAutoLabs/autolens_assistant
First clone that repository, cd into it and follow its AGENTS.md.

I'd like to understand how gravitational lensing works using the JWST image of the COSMOS-Web Ring that ships with the assistant. Show me the picture, explain what we are looking at, and walk me through fitting a lens model so we can measure the mass inside the ring and see how well the model reproduces the observations. Pitch it at my level: ask me what my background is first. Explain what we are doing as we go, and let me ask questions or change the analysis along the way.
```

<sub><b>Example Natural Language Prompt for Claude Code, Codex or other AI coding agent</b></sub>

```text
Find the data on the COSMOS-Web ring, give me a short script to plot it in PyAutoLens,
and then, given that I'm a new user, give me an overview of the different ways we can
perform strong lens modeling of this system.
```

<sub><b>Example Natural Language Prompt for Claude Code, Codex or other AI coding agent</b></sub>

```text
Teacher mode.

I'm new to PyAutoLens and want to learn the basic workflow end-to-end. Walk me through
simulating Euclid-like imaging of a simple strong lens, plotting it, and fitting it.
```

<sub><b>Example Natural Language Prompt for Claude Code, Codex or other AI coding agent</b></sub>

```text
I have HST imaging of a galaxy-scale lens. Help me plan the model: lens light, mass, and
source. Ask me what you need to know about the data first — don't run anything yet.
```

The last one exercises two things that matter. First, you can hold a planning discussion inside
the agent without it executing anything — say so, as the prompt does. Second, on **real data**
the assistant is required to make you look at the image before it composes a fit, and to settle
two things with you: whether there are extra galaxies or artefacts in the frame, and how big the
mask should be. It will plot the data itself and show you the file; that is the rule working,
not the assistant being slow.

**No agent? Use the Colab notebook.** The same COSMOS-Web Ring analysis is also a Google Colab
notebook, [`docs/colab/cosmos_web_ring_colab.ipynb`](../colab/cosmos_web_ring_colab.ipynb)
([open in Colab](https://colab.research.google.com/github/PyAutoLabs/autolens_assistant/blob/main/docs/colab/cosmos_web_ring_colab.ipynb)): it installs PyAutoLens, loads the ring, compares two JWST colours, fits
the lens model on a free Colab GPU and compares a good fit with a poorer one, with the code in view
and a suggested question for Colab's Gemini at the end of each section. It is the recommended route
if you are learning PyAutoLens and want to see the API.

More ambitious examples — dark-matter subhalo detection, joint imaging + interferometer +
weak-lensing fits — are in the [README](../../README.md).
