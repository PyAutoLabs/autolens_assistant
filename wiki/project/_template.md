---
date: YYYY-MM-DD
title: <one-line title — what this entry is about>
tags: [<dataset>, <profile>, <stage>, ...]
---

# <Title>

## Context

What prompted this work — the question we were trying to answer, the user's goal, or
the upstream change that forced the change here. One paragraph.

## What I did

Concrete actions taken in this session:

- Files touched (with paths, e.g. `scripts/imaging.py`, `config/priors/Sersic.yaml`).
- Commands run (e.g. `python3 scripts/imaging.py --sample=slacs --dataset=slacs0737`).
- Models composed / priors changed / pipelines added.
- Skills invoked (e.g. `al_build_imaging_model`, `al_chain_searches`).

Be specific enough that a future you / agent could redo the work from this entry alone.

## Outcome

The result. Numbers, log-likelihoods, posterior summaries, plots written. Open
questions. What we now know that we didn't at the start.

If a fit was run, name the output directory:

```
output/<sample>/<dataset>/<pipeline_stage>/<hash>/
```

If anything broke, capture the symptom and the root cause (not the fix — the fix is
in the diff).

## Next

Follow-ups, deferred items, suggested experiments. One bullet each, short.

- [ ] <thing to try next>
- [ ] <thing to verify>
