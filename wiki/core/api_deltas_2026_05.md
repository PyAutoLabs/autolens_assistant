---
title: API deltas — PyAuto* `2026.5.21` release
sources:
  - project: PyAutoArray
    pinned_commit: 2026.5.21.1
  - project: PyAutoGalaxy
    pinned_commit: 2026.5.21.1
  - project: PyAutoLens
    pinned_commit: 2026.5.21.1
---

# API deltas — `2026.5.21` release

This page lists every public-API change between the previous workspace baseline
and the `2026.5.21` release of the PyAuto\* stack. Every skill in this repo has
been audited against the released wheels; if a script you copy from an older
version of a skill stops working, this is the first place to look.

The list was derived by running the audit harness at
`work/edge_case_tests/` (see the PR introducing this page). Any entry below
that still doesn't reproduce on the released wheels should be treated as a
release-only artefact and reported upstream.

## Plotting (the biggest one)

`autolens.plot` is now a **flat module of free functions**, not a tree of
plotter classes. Direct class references and instance methods have all been
removed:

| Removed (pre-2026)                                                | Use instead                                              |
| ----------------------------------------------------------------- | -------------------------------------------------------- |
| `aplt.MatPlot2D(output=aplt.Output(path=..., filename=..., format=...))` | Pass `output_path=...`, `output_filename=...`, `output_format=...` directly to the new functions |
| `aplt.Output(...)`                                                | Replaced by per-function `output_*` kwargs              |
| `aplt.GalaxyPlotter`                                              | `aplt.subplot_galaxy_images`, `aplt.subplot_galaxies`, `aplt.subplot_galaxy_light_profiles`, `aplt.subplot_galaxy_mass_profiles` |
| `aplt.TracerPlotter`                                              | `aplt.subplot_tracer`, `aplt.subplot_galaxies_images`, `aplt.subplot_lensed_images` |
| `aplt.FitImagingPlotter`                                          | `aplt.subplot_fit_imaging`, `aplt.subplot_fit_imaging_log10`, `aplt.subplot_fit_imaging_of_planes`, `aplt.subplot_fit_imaging_tracer` |
| `aplt.ImagingPlotter`                                             | `aplt.subplot_imaging_dataset`                          |
| `aplt.MassProfilePlotter` / `aplt.LightProfilePlotter`            | Build the array via `profile.convergence_2d_from(...)` (or `.image_2d_from(...)`) then call `aplt.plot_array(...)` |
| `aplt.Visuals2D` (critical curves / caustics / positions overlay) | Several `subplot_*` functions take `positions=`, `image_plane_lines=`, `source_plane_lines=`, `tangential_critical_curves=`, `radial_critical_curves=` directly as kwargs. Tracer-level critical-curve / caustic *helpers* on `Tracer` are gone — derive them from the magnification map. |

The full inventory is `aplt.plot_array`, `aplt.plot_grid`, `aplt.output_figure`,
`aplt.fits_array`, `aplt.fits_imaging`, `aplt.fits_interferometer`, and a
collection of `subplot_*` helpers (see `dir(autolens.plot)` for the live list).

## FITS I/O

`Array2D.output_to_fits(...)` and `Imaging.output_to_fits(...)` are removed.
Use the new top-level helpers:

```python
import autolens.plot as aplt
aplt.fits_array(array=arr, file_path="…/data.fits", overwrite=True)
aplt.fits_imaging(dataset=imaging,
                  data_path="…/data.fits",
                  noise_map_path="…/noise.fits",
                  psf_path="…/psf.fits",
                  overwrite=True)
```

Reading (`Array2D.from_fits`, `Imaging.from_fits`, `Mask2D.from_fits`) is
unchanged.

## PSF / Convolver

`al.Kernel2D` → **`al.Convolver`**. The constructor / classmethods are
otherwise identical:

```python
psf = al.Convolver.from_gaussian(shape_native=(11, 11), sigma=0.1,
                                 pixel_scales=0.05, normalize=True)
psf = al.Convolver.from_fits(file_path="…/psf.fits", pixel_scales=0.05)
```

`SimulatorImaging(psf=…)` now expects a `Convolver`, not an `Array2D`.

## Pixelisation / mesh

The `image_mesh=` kwarg on `Pixelization` is removed. Image-plane mesh
selection is now done by choosing the right `mesh` class:

| Pre-2026                                                                  | 2026.5+                                       |
| ------------------------------------------------------------------------- | --------------------------------------------- |
| `Pixelization(mesh=al.mesh.Rectangular(shape=(N, N)), …)`                  | `Pixelization(mesh=al.mesh.RectangularUniform(shape=(N, N)), …)` |
| `Pixelization(image_mesh=al.image_mesh.Overlay(shape=(N, N)), mesh=al.mesh.Delaunay(), …)` | `Pixelization(mesh=al.mesh.Delaunay(pixels=N*N), …)` |
| `Pixelization(image_mesh=al.image_mesh.Overlay(shape=(N, N)), mesh=al.mesh.Voronoi(), …)`  | `Pixelization(mesh=al.mesh.KNNBarycentric(pixels=N*N), …)` |

The new adaptive families are `Rectangular{AdaptDensity,AdaptImage,RotatedAdaptImage,SplineAdaptDensity,SplineAdaptImage}`,
`Delaunay`, and `KNNBarycentric`.

> ⚠️ **Known regression in `2026.5.21.1`.** `Delaunay` and `KNNBarycentric`
> crash inside `FitImaging` with
> `AttributeError: 'NoneType' object has no attribute 'array'`. Use
> `RectangularUniform` until the upstream fix lands. Tracking issue:
> <https://github.com/Jammy2211/PyAutoArray/issues/332>.

## Tracer surface

These methods on `Tracer` are **removed in 2026.5.21.1**:

* `Tracer.magnification_2d_from(...)`
* `Tracer.tangential_critical_curve_list_from(...)`
* `Tracer.radial_critical_curve_list_from(...)`
* `Tracer.tangential_caustic_list_from(...)`
* `Tracer.critical_curves_from(...)`, `Tracer.caustics_from(...)`

If you need magnification, build it manually from the deflection field's
Jacobian, or compute it galaxy-wise. Critical curves / caustics are not
currently surfaced through the public API.

## Cosmology

`al.cosmo.FlatLambdaCDMWrap` → `al.cosmo.FlatLambdaCDM`.
`al.cosmo.Planck15()` remains the default cosmology (verified empirically:
the same `Tracer` evaluated with the default vs an explicit `Planck15()`
produces bit-identical images).

## Array2D ergonomic note

`Array2D` does *not* expose `.extent` directly. Use
`array.geometry.extent` (or `array.mask.geometry.extent`) instead.

## Removed entirely

| Symbol                          | Notes                          |
| ------------------------------- | ------------------------------ |
| `aplt.MatPlot2D`                | Function-style API only        |
| `aplt.Output`                   | Function-style API only        |
| `aplt.GalaxyPlotter`            | Function-style API only        |
| `aplt.TracerPlotter`            | Function-style API only        |
| `aplt.FitImagingPlotter`        | Function-style API only        |
| `aplt.ImagingPlotter`           | Function-style API only        |
| `aplt.MassProfilePlotter`       | Function-style API only        |
| `aplt.LightProfilePlotter`      | Function-style API only        |
| `aplt.Visuals2D`                | Overlays moved to per-function kwargs |
| `al.Kernel2D`                   | Renamed to `al.Convolver`      |
| `al.mesh.Rectangular`           | Renamed to `al.mesh.RectangularUniform` |
| `al.mesh.Voronoi`               | Replaced by `al.mesh.KNNBarycentric` |
| `Pixelization(image_mesh=…)`    | Removed (see Pixelisation table) |
| `Tracer.magnification_2d_from`  | Gone                           |
| `Tracer.critical_curves_from`   | Gone                           |
| `Tracer.caustics_from`          | Gone                           |
| `Array2D.output_to_fits`        | Use `aplt.fits_array(…)`       |
| `Imaging.output_to_fits`        | Use `aplt.fits_imaging(…)`     |
| `al.cosmo.FlatLambdaCDMWrap`    | Renamed to `FlatLambdaCDM`     |

## How this page is kept current

`al_update_wiki` walks every page in `wiki/core/` and re-derives content
from the pinned commits in the frontmatter above. If you bump the libraries,
re-run that skill and refresh this page.
