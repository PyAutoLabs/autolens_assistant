---
title: Project state
type: state
last_touched: 2026-11-06
---

# Project state

## Science goal

Test whether simultaneous multi-band (JWST F150W + F444W) lens modelling raises the Bayesian evidence
for a dark matter subhalo on the lensed arc, compared with single-band fits (cf. Nightingale et al.
2024, arXiv:2209.10566, single-band HST).

## Data on hand

- `dataset/imaging/jwst_pl_sersic_two_band/{subhalo_m10,no_subhalo}/wavebands/{F150W,F444W}/` —
  simulated by `scripts/simulators/jwst_pl_sersic_two_band.py` (0.03"/0.06" pixels, empirical COSMOS-Web
  PSFs, 3.5" mask, matched noise between the two dataset types). Truth: PowerLaw + shear +
  `NFWMCRLudlowSph` M_200 = 1e10 Msun at (-0.10", -1.90").

## Where we are now

- Pipeline written: `scripts/subhalo_multiband/subhalo_multiband_slam.py` (SLaM + SUBHALO PIPELINE,
  factor graph per band set). Shared across bands: mass, shear, subhalo. Per band: full lens-light MGE
  (centre + ellipticity), source, and alignment (offset y/x + rotation, `--max_offset` 0.5",
  `--max_rotation` 10 deg, `--fixed_alignment`). Meant for any simulated multi-band dataset in the
  `wavebands/` layout, not only the JWST two-band one. Smoke-tested in `PYAUTO_TEST_MODE=2`; no real
  fits run yet.

## In flight

- Nothing running. Submit on the cluster from `hpc/batch_gpu/`:
  `sbatch submit_subhalo_multiband.sh jwst_pl_sersic_two_band` (6 arms + dependent `--compare` job).

## Open, carried forward

- Run the six arms ({subhalo_m10, no_subhalo} x {F150W, F444W, F150W+F444W}) on GPU, then `--compare`.

## Traps — don't repeat

- `PYAUTO_SMALL_DATASETS=1` gives NaN likelihoods for single-band F444W (16x16 at 0.6"/px cannot
  resolve the MGE's 0.006" Gaussians); smoke-test single-band arms at full resolution.
- `PYAUTO_FAST_PLOTS=1` silently skips saving figures.
- This laptop (7 GB WSL) cannot run the pixelized stages on full-resolution F150W (~43k pixels): OOM.
  Smoke tests used a 2.4" mask copy in `scripts/scratch/subhalo_multiband/small_root/` and resumes;
  real runs belong on the GPU nodes.
- The venv `activate` files (local and RAL) end the PYTHONPATH block with `:\`, which glues the next
  `export LD_LIBRARY_PATH=...` line onto it (PYTHONPATH gains a junk `export` entry). Works by accident.
- RAL worker nodes have tiny OS disks (/home and /tmp): caches/TMPDIR go to /mnt/ral/c4072114/.cache
  (done in `hpc/batch_gpu/subhalo_multiband_batch.sh`, and in the mgl repo's `mgl_batch.sh` / `submit_mgl`, commit 2792b1e).
- The env: `source ~/venvs/PyAutoJAX/bin/activate` plus the PyAuto source checkouts
  (`../PyAutoNerves`, `../PyAutoFit`, `../PyAutoArray`, `../PyAutoGalaxy`, `../PyAutoLens`) on
  `PYTHONPATH`; the project `activate.sh` finds no `.venv`.
- `af.SearchGridSearch` on a `FactorGraphModel` needs the per-cell graph rebuild in the script
  (`FactorGraphSearchGridSearch`); the workspace `simultaneous.py` grid search fits only one band.

## Journal index

- `2026-11-06-multiband-subhalo-pipeline.md` — pipeline written, sharing verified, upstream grid-search issues found.
