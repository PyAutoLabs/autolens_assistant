---
date: 2026-05-22
title: First skill+wiki API audit against PyAuto* 2026.5.21.1
tags: [maintenance, api-drift, plotting-refactor]
---

# First skill+wiki API audit against PyAuto\* 2026.5.21.1

## Context

A user hit a stale `al.Kernel2D.from_gaussian` reference in `skills/al_simulate_dataset.md`.
The exploration showed no machinery exists to verify any of the ~107 PyAuto\* symbols
cited across `skills/` and `wiki/core/{api,stack}/` against the installed stack —
`al_update_wiki` only checks prose drift via pinned source commits. Built
`skills/al_audit_skill_apis.md` + `work/audit_skill_apis.py` to close that gap, then
ran it against PyAuto\* `2026.5.21.1` (latest as of the run).

## What I did

- Added the audit machinery (skill + helper script + symlink + README + citation map row +
  gitignore) — see [[al_audit_skill_apis]].
- Ran `python work/audit_skill_apis.py --scope all` → 29 misses on first pass.
- Patched the verified single-symbol renames in their respective files:
  - `skills/al_simulate_dataset.md` — `al.Kernel2D.from_gaussian` → `al.Convolver.from_gaussian`
    (the original trigger; signature is identical, drop-in replacement).
  - `skills/al_run_slam_pipeline.md`, `skills/al_debug_fit_failure.md` —
    `al.PositionsLHPenalty` → `al.PositionsLH`.
  - `skills/al_run_slam_pipeline.md` — `al.Grid2DIrregular.from_json(...)` →
    `al.from_json(...)` (the classmethod moved to a free function in autoconf.dictable
    that returns whatever was serialised).
  - `skills/al_custom_profile.md` — `ag.MassProfile` → `ag.mp.MassProfile`
    (`ag.LightProfile` is still at root, only the mass base class moved).
  - `skills/al_setup_environment.md` — rewrote the version-print block to import each
    library explicitly (`autoconf.__version__`, `autoarray.__version__`, …) instead of
    going through `al.aconf` (which never existed) / `al.conf` (which is a module
    without `__version__`).
  - `wiki/core/api/analysis_objects.md` — `al.cosmo.Planck18` → `al.cosmo.Planck15`
    (Planck18 isn't exported).
  - `wiki/core/stack/autolens.md` — `al.PointFlux` → `al.ps.PointFlux`; refreshed the
    mesh and regularisation lists (`Voronoi`, `Rectangular`, `AdaptiveBrightness` are
    gone; replaced by `RectangularUniform`, `Adapt`, `AdaptSplit` and the rest of the
    new families).
  - `skills/al_audit_skill_apis.md` itself — scrubbed two prose examples (a
    hypothetical renamed Kernel2D constructor and a `aplt.MatPlot2D` mention) that the
    audit was flagging in the skill that produced it.
- Re-ran the audit → 19 misses remain, all in the "needs investigation or full
  rewrite" bucket below.

## Outcome — deferred work

The audit count fell from 29 → 19 after the simple patches. The remaining items split
into three groups, none of them safe to fix without a focused session:

### 1. Plotting API refactor (15 of the 19)

The old class-based plotting interface has been fully replaced by a flat function
namespace in `autolens.plot`. Confirmed against
`autolens_workspace/lens/start_here.py` which now uses `aplt.plot_array(...)`,
`aplt.plot_grid(...)`, `aplt.subplot_imaging_dataset(...)` directly, with no
`MatPlot2D` / `Output` / `*Plotter` classes anywhere.

Removed (or never re-exported on `autolens.plot`):
- `aplt.MatPlot2D`, `aplt.Output`, `aplt.Visuals2D`
- `aplt.FitImagingPlotter`, `aplt.FitInterferometerPlotter`, `aplt.InversionPlotter`,
  `aplt.TracerPlotter`, `aplt.MassProfilePlotter`, `aplt.ImagingPlotter`
- `aplt.plot_mapper`, `aplt.subplot_image_and_mapper`,
  `aplt.subplot_interferometer_dataset` (the first two live on `autoarray.plot`; the
  third on `autogalaxy.plot`)

Affected files:
- `skills/al_plot_tracer.md`, `skills/al_plot_fit_residuals.md`,
  `skills/al_inspect_source_reconstruction.md`, `skills/al_simulate_dataset.md`,
  `skills/al_load_results.md`, `skills/al_debug_fit_failure.md`
- `wiki/core/api/plotting.md`, `wiki/core/stack/autolens.md`
- The "Plot output and path announcement" convention in `skills/_style.md` and the
  matching block in `CLAUDE.md` (both describe the `aplt.Output(path=..., filename=...)`
  pattern that no longer exists; the new function API likely takes `output_path` /
  `filename` kwargs directly on each `plot_*` / `subplot_*` call).

This wants its own session: read `autolens/plot/__init__.py` and the workspace
examples, design the replacement convention, then rewrite each skill's plotting
recipe coherently. Probably also a new `wiki/core/api/plotting.md` rewrite.

### 2. Removed search algorithms (2 of the 19)

`af.PySwarms` and `af.UltraNest` are no longer exported from PyAutoFit. Cited in
`wiki/core/api/searches.md` and `wiki/core/stack/autofit.md`. Hand off to
[[al_update_wiki]] — these wiki pages have pinned commits and should be refreshed
from the current PyAutoFit search inventory, not patched symbol-by-symbol.

### 3. Smaller deferred items (2 of the 19)

- `al.SettingsInversion` in `skills/al_build_interferometer_model.md` — split into
  `al.Inversion` (the runtime object) and `al.Settings` (the settings container).
  Needs a small recipe rewrite, not just a symbol swap; the call sites likely changed.
- `autofit.aggregator.search.aggregator` in `skills/al_debug_fit_failure.md` — looks
  like a stale path into the aggregator module; the audit's suggestion is
  `autofit.non_linear.search`, but the right replacement depends on what the line was
  trying to demonstrate. Read the surrounding recipe before patching.

## Provenance

- Installed versions: all five PyAuto\* at `2026.5.21.1` (`PYTHONPATH` against the
  sibling editable clones at `/Users/other/autolens/{conf,array,fit,galaxy,lens}/`,
  Python 3.10 in `conda env autolens310`).
- Branch: `audit/skill-apis` (worktree under `.claude/worktrees/audit-skill-apis/`),
  to be merged back into `feat/natural-language`.
- Today's audit report: `work/audit/skill_api_audit_2026-05-22.md` (gitignored — regenerate
  with `python work/audit_skill_apis.py --scope all`).

Cross-references: [[al_audit_skill_apis]], [[al_update_wiki]], [[al_simulate_dataset]].
