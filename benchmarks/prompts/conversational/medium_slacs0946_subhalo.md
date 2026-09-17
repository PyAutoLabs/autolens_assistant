---
id: assistant-medium-slacs0946-subhalo
version: 1
mode: assistant
difficulty: medium
datasets:
  - dataset/imaging/slacs0946+1006
workspace_packages:
  - imaging
added: 2026-07-10
---

# Benchmark: SLACS0946+1006 subhalo model comparison (assistant · medium)

The dataset is bundled, but the analysis is **not** a ready-made workflow: the
agent must design a Bayesian model-comparison pipeline itself — a smooth
baseline, a free-position SIS perturber scan, and an SIS-vs-NFW comparison at
the recovered position — and it must reason about runtime and hardware. This
measures composition of capabilities beyond what any single skill provides.

## Prompt

Paste verbatim as the first message of a fresh session (see
[`../AGENTS.md`](../AGENTS.md) for the run protocol):

```
Assistant mode.

The strong lens SLACS0946+1006 famously has a dark matter subhalo
detection that many argue is unusually concentrated. I'd like to analyse
the HST imaging of this lens provided at
dataset/imaging/slacs0946+1006/ and reproduce that detection.

Specifically, I want this analysis to perform Bayesian model comparison
to (a) confirm a subhalo is preferred over a smooth-mass baseline by
fitting a free-position, free-mass SIS perturber across the image plane
and comparing the Bayesian evidence to the no-subhalo fit, and (b) test
the "super-concentrated" claim by comparing the SIS subhalo
against a more shallow NFW mass profile at the recovered position.

Set the pipeline up so the smooth lens light and mass model, the
pixelized source reconstruction, and the subhalo results are all
inspectable on my computer, and report the Bayesian evidence for each
comparison.

Assess whether the analysis will run fast on my laptop / PC GPU,
and if not, set this up as a small project on the HPC I have access to.
```

This is Example Prompt 3 of the top-level `README.md`; the two texts must stay
identical (a divergence is a bug — fix the README or bump this card's
`version`).

## What this measures

- Pipeline design beyond bundled workflows: chained searches, evidence
  bookkeeping, a perturber scan, profile substitution at a fixed position.
- Scientific literacy: the subhalo-detection literature context (the assistant
  ships a literature wiki covering it) and what "concentrated" means for
  SIS-vs-NFW comparison.
- Resource judgment: an honest laptop/GPU runtime estimate and, if needed, an
  HPC project setup rather than silently launching an hours-long local run.

## Success rubric (100 points)

### Machine-checkable (40)

| # | Check | Pts |
|---|-------|-----|
| M1 | Smooth-baseline fit completed with its log-evidence recorded | 10 |
| M2 | SIS-subhalo fit (free position, free mass) completed with its log-evidence recorded | 10 |
| M3 | NFW-subhalo comparison fit completed with its log-evidence recorded | 10 |
| M4 | Both evidence comparisons (subhalo vs smooth; SIS vs NFW) reported as numbers in the final answer | 5 |
| M5 | Results inspectable: output paths for the smooth model, source reconstruction and subhalo results listed for the user | 5 |

### Judged (60)

| # | Criterion | Pts |
|---|-----------|-----|
| J1 | Comparison design is correct: the perturber scan genuinely explores the image plane (not a single fixed guess); the NFW test is at the recovered position as asked | 15 |
| J2 | Runtime/hardware assessment performed *before* the long runs, with a defensible estimate; HPC option set up or offered if the local estimate is slow | 15 |
| J3 | Pipeline structure sensible: lens light + mass + pixelized source built up in stages rather than one monolithic fit; evidence values comparable (same data, same mask) | 10 |
| J4 | Scientific interpretation: what the ΔlogZ values mean, and what SIS-vs-NFW says about the concentration claim, stated with appropriate caution | 10 |
| J5 | Real-data gate honoured; conduct (honest reporting, no fabricated evidences, API-gate discipline) | 10 |

## Operator notes

- Full sampling is hours-scale on a laptop; the prompt's last paragraph makes
  runtime assessment part of the task. A run that stops at a well-set-up HPC
  handoff with clear instructions can still score highly on the judged side —
  score the machine-checkable fits only if they actually completed somewhere.
- Repeat runs on different hardware are comparable on the judged criteria but
  not on wall-clock; record hardware in `meta.yaml`.
