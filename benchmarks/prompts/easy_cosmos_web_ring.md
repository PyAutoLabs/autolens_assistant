---
id: assistant-easy-cosmos-web-ring
version: 1
mode: assistant
difficulty: easy
datasets:
  - dataset/imaging/cosmos_web_ring
workspace_packages:
  - imaging
added: 2026-07-10
---

# Benchmark: model the bundled JWST ring (assistant · easy)

Everything this prompt asks for is directly available in the assistant: the
dataset ships with the repo, and data preparation, model composition, pixelized
source fitting and result inspection are all covered by existing `al_*` skills.
A capable agent should complete it without inventing anything — the benchmark
measures whether it *finds and follows* the built-in workflow.

## Prompt

Paste verbatim as the first message of a fresh session (see
[`../AGENTS.md`](../AGENTS.md) for the run protocol):

```
Assistant mode.

Model the JWST imaging in dataset/imaging/cosmos_web_ring: perform data preparation steps, 
set up a sensible lens light and mass model with a pixelized source reconstruction, run 
the fit, and show me the reconstructed source and the fit residuals.
```

This is Example Prompt 2 of the top-level `README.md`; the two texts must stay
identical (a divergence is a bug — fix the README or bump this card's
`version`).

## What this measures

- Routing: does the agent use the assistant's skills and bundled dataset rather
  than writing PyAutoLens from memory?
- The real-data safety gate: inspecting the data and asking about extra
  galaxies / artefacts *before* fitting.
- A complete run: preparation → model → search → fit → the two requested
  visuals.

## Success rubric (100 points)

### Machine-checkable (40)

| # | Check | Pts |
|---|-------|-----|
| M1 | A script (or scripts) saved under `scripts/` that performs the fit | 5 |
| M2 | A completed non-linear search result exists under `output/` (not test-mode) | 10 |
| M3 | The model includes a pixelized source (mesh + regularization), verifiable in the script | 10 |
| M4 | A reconstructed-source figure was produced and its path shown to the user | 10 |
| M5 | A residual-map figure was produced and its path shown to the user | 5 |

### Judged (60)

| # | Criterion | Pts |
|---|-----------|-----|
| J1 | Real-data gate honoured: dataset plotted and inspected, one question asked about extra galaxies / foreground stars / artefacts before any fit | 15 |
| J2 | Sensible model choices for this data (lens light + total mass, e.g. Sersic/MGE light with isothermal mass; priors not obviously pathological) | 15 |
| J3 | Data preparation actually performed (mask choice justified; any needed dataset prep steps done rather than skipped) | 10 |
| J4 | Fit quality: residuals broadly noise-like, reconstruction plausibly a lensed source; agent comments on quality honestly | 10 |
| J5 | Conduct: concise assistant-mode communication, no fabricated numbers, API-gate discipline (no invented symbols) | 10 |

## Operator notes

- Expected wall-clock: roughly 15–60 minutes depending on hardware and model;
  the search is the dominant cost.
- A run that ends with the agent honestly reporting a failed or poor fit scores
  what the rubric gives it — record it; failures are data.
