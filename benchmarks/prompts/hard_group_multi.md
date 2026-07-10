---
id: assistant-hard-group-multi
version: 1
mode: assistant
difficulty: hard
datasets: []          # fully simulated — the agent creates both datasets
workspace_packages:
  - group
  - multi
  - imaging
  - interferometer
added: 2026-07-10
---

# Benchmark: group-scale joint imaging + interferometer (assistant · hard)

Not based on any README example, and deliberately not achievable from a single
workspace package: the agent must combine **group**-scale lens composition
(two lens galaxies), **multi**-dataset joint analysis, and both the
**imaging** and **interferometer** pipelines — simulation and modeling — then
chain a pixelized-source follow-up. This measures cross-package synthesis, the
hardest thing for an agent working from per-package examples.

## Prompt

Paste verbatim as the first message of a fresh session (see
[`../AGENTS.md`](../AGENTS.md) for the run protocol):

```
Assistant mode.

First, I want to simulate imaging and interferometer data of a group-scale strong lens, which is composed of
two SIE lens galaxies and a quadruply imaged Cored Sersic background source. 

Then, I want to perform modeling of this dataset, simultaneously fitting the imaging and interferometer data.
I want the foreground lens model to use multi gaussian Expansions for the lens light, SIE's for each lens
and a multi Gaussian expansion for the background source. 

After this fit has been judged successful, do a follow up lens model that uses a pixelized source reconstruction,
but retains the MGE lens light and SIE source.

Present me with results confirming the fit was a success. 
```

The prompt is frozen verbatim — including its rough edges (e.g. the final
"SIE source" plainly means the SIE mass profiles are retained while the source
switches to pixelized). Interpreting user intent sensibly, or asking one
focused question, is part of what is being measured; do not clean the wording.

## What this measures

- Cross-package composition: group (multi-galaxy lens) × multi (joint
  datasets) × imaging × interferometer, for both simulation and modeling.
- Simulation judgment: choosing sensible instrument configurations (a
  resolution/uv-plane setup that actually resolves a quad) and verifying the
  source is genuinely quadruply imaged.
- Joint-fit wiring: one lens model shared across an imaging and an
  interferometer analysis, fitted simultaneously.
- Staged modeling: judging the MGE fit successful before the pixelized-source
  follow-up, and demonstrating success against known truths.

## Success rubric (100 points)

### Machine-checkable (45)

| # | Check | Pts |
|---|-------|-----|
| M1 | Simulated imaging dataset created: two SIE lenses + Cored Sersic source, with the quad morphology visible/verified | 10 |
| M2 | Simulated interferometer dataset of the same system created | 10 |
| M3 | Joint fit completed fitting imaging + interferometer **simultaneously** (one search over a shared model, not two independent fits) with MGE lens light, one SIE per lens, MGE source | 15 |
| M4 | Follow-up pixelized-source fit completed retaining MGE lens light and the SIE mass profiles | 5 |
| M5 | A results summary presented: truth-vs-recovered comparison and/or residual figures with paths shown | 5 |

### Judged (55)

| # | Criterion | Pts |
|---|-----------|-----|
| J1 | Simulation quality: group-scale geometry plausible; instrument configs sensible; the quad verified rather than assumed | 15 |
| J2 | Joint-analysis wiring correct: shared parametrisation across datasets, dataset-specific nuisance handled sensibly; simultaneous fit demonstrated (not sequential) | 15 |
| J3 | Success judged honestly between stages: explicit criteria (residuals, recovered parameters vs truth) before proceeding to the pixelized follow-up | 10 |
| J4 | The "SIE source" ambiguity handled sensibly (correct interpretation or one focused question — not silent nonsense, not an interrogation) | 5 |
| J5 | Conduct: staged plan communicated, honest evidence of success/failure, API-gate discipline, no fabricated results | 10 |

## Operator notes

- The heaviest benchmark: two simulations plus a joint search plus a pixelized
  follow-up. Expect multiple hours of wall-clock on a laptop; interferometer
  transforms benefit strongly from a GPU. Partial completions are still
  recorded — score what completed.
- Because everything is simulated, the run is fully self-contained and
  hardware-reproducible: truths are known, so recovered-parameter accuracy is
  objective evidence.
