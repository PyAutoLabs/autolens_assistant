# First prompts to try

Once any option from the [setup guide](../../FREE_TIER_SETUP.md) is configured, these all
work immediately — the COSMOS-Web Ring data ships with the repository:

```text
Find the data on the COSMOS-Web ring, give me a short script to plot it in PyAutoLens,
and then, given that I'm a new user, give me an overview of the different ways we can
perform strong lens modeling of this system.
```

```text
Teacher mode.

I'm new to PyAutoLens and want to learn the basic workflow end-to-end. Walk me through
simulating Euclid-like imaging of a simple strong lens, plotting it, and fitting it.
```

```text
I have HST imaging of a galaxy-scale lens. Help me plan the model: lens light, mass, and
source. Ask me what you need to know about the data first.
```

The last one exercises the behaviour that matters most. On **real data** the assistant is
required to make you look at the image before it composes a fit, and to settle two things
with you: whether there are extra galaxies or artefacts in the frame, and how big the mask
should be. In a browser chat it can't plot your data itself, so it will ask you to. That is
the rule working, not the assistant being unhelpful.

More ambitious examples — dark-matter subhalo detection, joint imaging + interferometer +
weak-lensing fits — are in the [README](../../README.md).
