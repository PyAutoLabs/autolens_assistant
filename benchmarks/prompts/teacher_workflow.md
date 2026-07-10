---
id: teacher-basic-workflow
version: 1
mode: teacher
difficulty: easy
datasets: []          # fully simulated — the session generates its own data
workspace_packages:
  - imaging
added: 2026-07-10
---

# Benchmark: end-to-end workflow walkthrough (teacher)

The teacher-mode benchmark: the deliverable is **understanding**, not a fit.
The scientific content is deliberately simple (isothermal mass + Sersic
source on simulated Euclid-like imaging) so the score concentrates on
pedagogy — pacing, correctness of explanation, and whether a newcomer would
come away understanding the workflow rather than having watched commands
scroll past.

## Prompt

Paste verbatim as the first message of a fresh session (see
[`../AGENTS.md`](../AGENTS.md) for the run protocol):

```
Teacher mode.

I'm new to PyAutoLens and want to learn the basic workflow end-to-end. Can you
walk me through it on a simple simulated example: simulate Euclid-like imaging of
a simple strong lens (an isothermal mass with a Sersic source), then fit that
simulated data and recover the lens model.

Explain what each step is doing and why as we go: composing the lens and source
model, running the simulation, choosing the mask, the non-linear search, and how
to read the result. So I come away understanding the workflow, not just the
commands.
```

This is Example Prompt 1 of the top-level `README.md`; the two texts must stay
identical (a divergence is a bug — fix the README or bump this card's
`version`).

## What this measures

- Teacher-mode behaviour: explaining *why* at each step, checking in, adapting
  depth — versus dumping a complete script.
- Domain correctness at teaching depth: what an isothermal profile is, why
  masks matter, what a non-linear search does, how to read the results.
- Instrument realism: "Euclid-like" should actually inform the simulation
  (VIS-like pixel scale ~0.1", appropriate PSF and depth), not be ignored.

## Success rubric (100 points)

### Machine-checkable (30)

| # | Check | Pts |
|---|-------|-----|
| M1 | A simulation script/steps producing Euclid-like imaging of an isothermal + Sersic system exists and ran | 10 |
| M2 | A fit of the simulated data completed, with results shown | 10 |
| M3 | Recovered lens-model parameters compared against the input truths explicitly | 10 |

### Judged (70)

| # | Criterion | Pts |
|---|-----------|-----|
| J1 | Every requested step explained with its *why*: model composition, simulation, mask choice, non-linear search, reading results | 20 |
| J2 | Scientific accuracy of the explanations (no confident falsehoods about lensing or Bayesian inference; simplifications flagged as such) | 15 |
| J3 | Pedagogical pacing: steps introduced one at a time, understanding checked, user given something to do or predict — not a monologue or a code dump | 15 |
| J4 | Euclid realism: pixel scale / PSF / depth choices stated and justified as Euclid-like | 10 |
| J5 | Closure: an end-of-session recap the learner could reconstruct the workflow from | 10 |

## Operator notes

- Cheap to run (simple simulation, fast search) — a good default when adding a
  new model/harness to the comparison tables, and a good same-model/different-
  day drift probe since run cost is low.
- Judged criteria dominate by design; use the same judge (human or stated
  judge-model) across runs being compared, and record the judge in `meta.yaml`.
