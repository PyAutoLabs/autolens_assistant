---
id: abell-1201-setup
version: 1
kind: oneshot
prompt_sha256: a75d08eaa4285e413f297c4335f3263138336d010350db0e5e3ad12a0082a020
budget:
  compute_seconds: 300
  run_seconds: 900
datasets:
  - dataset/imaging/abell_1201
workspace_packages:
  - imaging
added: 2026-09-22
---

# Abell 1201: presentation and setup smoke

This is the inexpensive setup check for the point-mass benchmark, not a
posterior-fitting benchmark or reproduction of the SMBH discovery. The
scientist approved the cleaned data, exact processed boundary, mass-model
family and smoke-only execution on 2026-09-22.

## Prompt

```text
Show me a colour image of Abell 1201, then prepare and smoke-test the F390W power-law galaxy mass + external shear + central point-mass model using dataset/imaging/abell_1201. Read scripts/abell_1201/README.md first. The scientist has inspected these real data and approved the existing contaminant removal and exact processed 4 arcsec boundary; do not ask again or replace that boundary. Use the supplied image.fits/noise_map.fits likelihood pair, retain lens/source nuisance parameters, and keep the presentation image separate from inference. Run the supplied presentation, dataset-preparation and coarse model smoke scripts. Do not launch a posterior search, infer a black-hole mass, or claim scientific validation. Write result.json with exactly these keys: stage ("setup_only"), model_family ("power_law_shear_point_mass"), preparation (the preparation.json object), smoke (the setup.json object), presentation_png (the repository-relative path of the generated RGB PNG), summary (at most three sentences explaining what was checked and what still needs a full run).
```

## What this measures

The assistant finds the supplied data and current setup scripts, renders a
separate presentation image, preserves the approved preparation, constructs
the model and evaluates one coarse inversion. It reports its limitations
without fabricating a mass measurement. Positions-penalty acceptance and
scientific resolution are not validated by this coarse inversion.

## Score

The harness enforces valid JSON/schema and compute/wall-clock budgets.
Card gates require the setup-only stage, the approved model family, both
bands with 31417 included pixels at 0.04 arcsec/pixel and radius 4 arcsec,
normalised PSFs, original cleaned image/noise pair, a finite smoke inversion
with 14 free parameters, explicit no-posterior/no-validation flags and an
existing PNG presentation artifact. Passing these gates gives three binary
metrics: preparation, smoke, and presentation. No mass value is scored.

The 300-second interpreter / 900-second wall budgets are provisional generous
setup caps, informed by the local script smoke (seconds, not a full headless
agent run). A headless qualification run is still pending. Change/version the
card if measured qualification requires another budget or prompt.
